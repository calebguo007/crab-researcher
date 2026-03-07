"""
成本控制器 - 智能模型选择 & 预算管理
核心策略:
  Tier 1: 数据抓取 → 零LLM调用
  Tier 2: 简单处理 → GPT-4o-mini / DeepSeek (极低成本)
  Tier 3: 智能分析 → GPT-4o (中等成本)
  Tier 4: 深度推理 → o1-mini (可控成本)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.task import TokenUsageLog, User

settings = get_settings()


class TaskTier(str, Enum):
    """任务分级"""
    TIER_1_SCRAPE = "scrape"       # 纯爬虫，无LLM
    TIER_2_SIMPLE = "simple"       # 格式化/关键词提取
    TIER_3_ANALYSIS = "analysis"   # 周报/对比分析
    TIER_4_DEEP = "deep"           # Persona模拟/策略建议


@dataclass
class ModelConfig:
    """模型配置"""
    name: str                          # 模型标识
    provider: str                      # openai / anthropic / deepseek
    input_price_per_1m: float          # 每百万输入token价格(USD)
    output_price_per_1m: float         # 每百万输出token价格(USD)
    max_tokens: int = 4096
    usd_to_cny: float = 7.2           # 汇率

    @property
    def input_cost_cny_per_token(self) -> float:
        return (self.input_price_per_1m / 1_000_000) * self.usd_to_cny

    @property
    def output_cost_cny_per_token(self) -> float:
        return (self.output_price_per_1m / 1_000_000) * self.usd_to_cny


# 可用模型池
MODELS = {
    "moonshot-v1-8k": ModelConfig(
        name="moonshot-v1-8k", provider="moonshot",
        input_price_per_1m=12.0, output_price_per_1m=12.0,
        usd_to_cny=1.0,  # Moonshot 直接人民币计价
    ),
    "moonshot-v1-32k": ModelConfig(
        name="moonshot-v1-32k", provider="moonshot",
        input_price_per_1m=24.0, output_price_per_1m=24.0,
        usd_to_cny=1.0,
    ),
    "moonshot-v1-128k": ModelConfig(
        name="moonshot-v1-128k", provider="moonshot",
        input_price_per_1m=60.0, output_price_per_1m=60.0,
        usd_to_cny=1.0,
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini", provider="openai",
        input_price_per_1m=0.15, output_price_per_1m=0.6,
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o", provider="openai",
        input_price_per_1m=2.5, output_price_per_1m=10.0,
    ),
    "o1-mini": ModelConfig(
        name="o1-mini", provider="openai",
        input_price_per_1m=3.0, output_price_per_1m=12.0,
    ),
    "deepseek-chat": ModelConfig(
        name="deepseek-chat", provider="deepseek",
        input_price_per_1m=0.14, output_price_per_1m=0.28,
    ),
    "claude-3-5-sonnet": ModelConfig(
        name="claude-3-5-sonnet-20241022", provider="anthropic",
        input_price_per_1m=3.0, output_price_per_1m=15.0,
    ),
}

# 每个 Tier 的默认模型和降级模型（Demo 阶段优先使用 Moonshot）
TIER_MODEL_MAP: dict[TaskTier, list[str]] = {
    TaskTier.TIER_1_SCRAPE: [],  # 不需要LLM
    TaskTier.TIER_2_SIMPLE: ["moonshot-v1-8k", "deepseek-chat", "gpt-4o-mini"],
    TaskTier.TIER_3_ANALYSIS: ["moonshot-v1-32k", "moonshot-v1-8k", "gpt-4o-mini"],
    TaskTier.TIER_4_DEEP: ["moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k"],
}


class CostController:
    """成本控制器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_monthly_usage(self, user_id: int) -> float:
        """获取用户本月已用费用"""
        from datetime import datetime
        now = datetime.utcnow()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        result = await self.db.execute(
            select(func.coalesce(func.sum(TokenUsageLog.cost_cny), 0.0)).where(
                TokenUsageLog.user_id == user_id,
                TokenUsageLog.created_at >= first_day,
            )
        )
        return float(result.scalar())

    async def get_budget(self, user_id: int) -> float:
        """获取用户月度预算"""
        result = await self.db.execute(
            select(User.monthly_budget).where(User.id == user_id)
        )
        budget = result.scalar()
        return budget or settings.MONTHLY_BUDGET_PER_USER

    async def check_budget(self, user_id: int) -> dict:
        """检查预算使用状况"""
        used = await self.get_monthly_usage(user_id)
        budget = await self.get_budget(user_id)
        ratio = used / budget if budget > 0 else 1.0

        return {
            "used": round(used, 2),
            "budget": round(budget, 2),
            "ratio": round(ratio, 4),
            "remaining": round(budget - used, 2),
            "is_over_budget": ratio >= 1.0,
            "is_warning": ratio >= settings.TOKEN_USAGE_ALERT_THRESHOLD,
        }

    async def select_model(self, user_id: int, tier: TaskTier) -> Optional[ModelConfig]:
        """
        智能模型选择:
        1. 根据任务 tier 获取候选模型列表
        2. 检查预算状况
        3. 如果接近预算上限，自动降级到便宜模型
        """
        if tier == TaskTier.TIER_1_SCRAPE:
            return None  # 不需要LLM

        candidates = TIER_MODEL_MAP[tier]
        if not candidates:
            return None

        budget_info = await self.check_budget(user_id)

        # 超预算 → 只允许最便宜的模型
        if budget_info["is_over_budget"]:
            return MODELS.get(candidates[-1])  # 列表最后一个是最便宜的

        # 接近预算 → 降级
        if budget_info["is_warning"]:
            return MODELS.get(candidates[min(1, len(candidates) - 1)])

        # 正常 → 使用默认(最优)模型
        return MODELS.get(candidates[0])

    async def log_usage(
        self, user_id: int, model: str,
        prompt_tokens: int, completion_tokens: int,
        task_type: str,
    ) -> float:
        """记录Token使用并计算费用"""
        model_config = MODELS.get(model)
        if not model_config:
            return 0.0

        cost = (
            prompt_tokens * model_config.input_cost_cny_per_token
            + completion_tokens * model_config.output_cost_cny_per_token
        )

        log = TokenUsageLog(
            user_id=user_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_cny=round(cost, 6),
            task_type=task_type,
        )
        self.db.add(log)

        # 更新用户月度已用额度
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.monthly_token_used = round((user.monthly_token_used or 0) + cost, 6)

        return round(cost, 6)

    @staticmethod
    def estimate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """预估费用(不写库)"""
        m = MODELS.get(model_name)
        if not m:
            return 0.0
        return round(
            prompt_tokens * m.input_cost_cny_per_token
            + completion_tokens * m.output_cost_cny_per_token,
            6,
        )
