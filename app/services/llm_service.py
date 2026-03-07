"""
LLM 调用服务 - 统一封装多模型调用
支持: OpenAI / Anthropic / DeepSeek
自动集成成本控制器
"""

import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.cost_controller import CostController, ModelConfig, TaskTier, MODELS

settings = get_settings()
logger = logging.getLogger(__name__)


class LLMService:
    """LLM 统一调用层"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cost_controller = CostController(db)

        # OpenAI 客户端 (同时兼容 DeepSeek / Moonshot 的 OpenAI 兼容接口)
        self._openai_client = None
        self._deepseek_client = None
        self._moonshot_client = None

    @property
    def openai_client(self) -> AsyncOpenAI:
        if self._openai_client is None:
            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    @property
    def deepseek_client(self) -> AsyncOpenAI:
        if self._deepseek_client is None:
            self._deepseek_client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )
        return self._deepseek_client

    @property
    def moonshot_client(self) -> AsyncOpenAI:
        if self._moonshot_client is None:
            self._moonshot_client = AsyncOpenAI(
                api_key=settings.MOONSHOT_API_KEY,
                base_url="https://api.moonshot.cn/v1",
            )
        return self._moonshot_client

    def _get_client(self, model_config: ModelConfig) -> AsyncOpenAI:
        """根据 provider 选择客户端"""
        if model_config.provider == "deepseek":
            return self.deepseek_client
        if model_config.provider == "moonshot":
            return self.moonshot_client
        return self.openai_client

    async def chat(
        self,
        user_id: int,
        tier: TaskTier,
        messages: list[dict],
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        force_model: Optional[str] = None,
    ) -> dict:
        """
        统一聊天接口

        Args:
            user_id: 用户ID
            tier: 任务分级(影响模型选择)
            messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
            task_type: 任务类型标签(用于费用追踪)
            temperature: 温度
            max_tokens: 最大生成tokens
            force_model: 强制指定模型(跳过自动选择)

        Returns:
            {"content": str, "model": str, "cost": float, "tokens": {...}}
        """
        # 选择模型
        if force_model and force_model in MODELS:
            model_config = MODELS[force_model]
        else:
            model_config = await self.cost_controller.select_model(user_id, tier)

        if model_config is None:
            raise ValueError("无可用模型(可能是Tier1任务不需要LLM)")

        logger.info(f"[LLM] user={user_id} tier={tier.value} model={model_config.name}")

        client = self._get_client(model_config)

        try:
            response = await client.chat.completions.create(
                model=model_config.name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or model_config.max_tokens,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage

            # 记录费用
            cost = await self.cost_controller.log_usage(
                user_id=user_id,
                model=model_config.name,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                task_type=task_type,
            )

            return {
                "content": content,
                "model": model_config.name,
                "cost_cny": cost,
                "tokens": {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"[LLM] 调用失败: {e}, 尝试降级...")
            return await self._fallback(
                user_id, tier, messages, task_type, temperature, max_tokens, model_config.name
            )

    async def _fallback(
        self,
        user_id: int,
        tier: TaskTier,
        messages: list[dict],
        task_type: str,
        temperature: float,
        max_tokens: Optional[int],
        failed_model: str,
    ) -> dict:
        """降级策略: 当前模型失败时，自动切换到更便宜的备选模型"""
        from app.services.cost_controller import TIER_MODEL_MAP

        candidates = TIER_MODEL_MAP.get(tier, [])
        fallback_models = [m for m in candidates if m != failed_model]

        for model_name in fallback_models:
            try:
                logger.info(f"[LLM] 降级到 {model_name}")
                mc = MODELS[model_name]
                client = self._get_client(mc)

                response = await client.chat.completions.create(
                    model=mc.name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens or mc.max_tokens,
                )

                content = response.choices[0].message.content or ""
                usage = response.usage

                cost = await self.cost_controller.log_usage(
                    user_id=user_id,
                    model=mc.name,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    task_type=task_type,
                )

                return {
                    "content": content,
                    "model": mc.name,
                    "cost_cny": cost,
                    "tokens": {
                        "prompt": usage.prompt_tokens,
                        "completion": usage.completion_tokens,
                        "total": usage.total_tokens,
                    },
                    "fallback": True,
                }
            except Exception as e:
                logger.error(f"[LLM] 降级模型 {model_name} 也失败: {e}")
                continue

        raise RuntimeError("所有模型均调用失败，请检查API Key配置")

    async def generate_embedding(self, text: str) -> list[float]:
        """生成文本向量(使用 OpenAI text-embedding-3-small)"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
