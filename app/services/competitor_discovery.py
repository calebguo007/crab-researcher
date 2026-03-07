"""
竞品管理服务
- 用户手动添加/更新/删除竞品（核心流程）
- LLM 自动发现竞品候选（可选辅助功能）
"""

import json
import logging
import random
from datetime import datetime
from typing import Optional
from urllib.parse import quote

import httpx
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.task import UserProduct, CompetitorDiscovery, CompetitorProduct
from app.services.llm_service import LLMService
from app.services.cost_controller import TaskTier

settings = get_settings()
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class CompetitorDiscoveryService:
    """竞品管理服务（手动添加 + LLM辅助发现）"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService(db)

    # ========== 手动 CRUD（核心功能）==========

    async def add_competitor(self, user_product_id: int, data: dict) -> CompetitorProduct:
        """用户手动添加竞品"""
        competitor = CompetitorProduct(
            user_product_id=user_product_id,
            brand=data["brand"],
            product_name=data["product_name"],
            platform=data.get("platform"),
            price=data.get("price"),
            promo_price=data.get("promo_price"),
            specs=data.get("specs", {}),
            features=data.get("features", []),
            product_url=data.get("product_url"),
        )
        self.db.add(competitor)
        await self.db.flush()
        await self.db.refresh(competitor)
        logger.info(f"[Competitor] 手动添加竞品: {competitor.brand} - {competitor.product_name}")
        return competitor

    async def update_competitor(self, competitor_id: int, data: dict) -> CompetitorProduct:
        """更新竞品信息"""
        result = await self.db.execute(
            select(CompetitorProduct).where(CompetitorProduct.id == competitor_id)
        )
        competitor = result.scalar_one_or_none()
        if not competitor:
            raise ValueError(f"竞品 {competitor_id} 不存在")

        for key, value in data.items():
            if value is not None and hasattr(competitor, key):
                setattr(competitor, key, value)

        await self.db.flush()
        await self.db.refresh(competitor)
        logger.info(f"[Competitor] 更新竞品: {competitor.brand} - {competitor.product_name}")
        return competitor

    async def delete_competitor(self, competitor_id: int):
        """删除竞品"""
        result = await self.db.execute(
            select(CompetitorProduct).where(CompetitorProduct.id == competitor_id)
        )
        competitor = result.scalar_one_or_none()
        if not competitor:
            raise ValueError(f"竞品 {competitor_id} 不存在")

        brand_name = competitor.brand
        await self.db.delete(competitor)
        await self.db.flush()
        logger.info(f"[Competitor] 删除竞品: {brand_name}")

    async def get_competitor(self, competitor_id: int) -> Optional[CompetitorProduct]:
        """获取单个竞品"""
        result = await self.db.execute(
            select(CompetitorProduct).where(CompetitorProduct.id == competitor_id)
        )
        return result.scalar_one_or_none()

    async def list_competitors(self, user_product_id: int) -> list[CompetitorProduct]:
        """获取产品下所有竞品"""
        result = await self.db.execute(
            select(CompetitorProduct)
            .where(CompetitorProduct.user_product_id == user_product_id)
            .order_by(CompetitorProduct.created_at.desc())
        )
        return list(result.scalars().all())

    # ========== LLM 自动发现（可选辅助功能）==========

    async def discover(self, user_product: UserProduct, user_id: int) -> list[CompetitorDiscovery]:
        """
        基于用户产品信息自动发现竞品
        1. 构建搜索关键词
        2. 调用 LLM 分析行业竞品格局
        3. 生成竞品候选列表
        """
        logger.info(f"[Discovery] 开始竞品发现: product={user_product.product_name}, "
                     f"category={user_product.category}")

        # 构建 LLM prompt
        keywords = user_product.keywords or [user_product.category]
        price_range = user_product.price_range or {}
        price_info = ""
        if price_range.get("min") or price_range.get("max"):
            price_info = f"，目标价格带: {price_range.get('min', '不限')} - {price_range.get('max', '不限')} 元"

        prompt = f"""你是一个专业的市场调研分析师。请根据以下信息，分析该产品的竞争格局，列出主要竞品。

## 用户产品信息
- 产品名称: {user_product.product_name}
- 所属行业: {user_product.industry}
- 细分品类: {user_product.category}
- 搜索关键词: {', '.join(keywords)}
- 监测平台: {', '.join(user_product.platforms or ['jd', 'tmall'])}{price_info}

## 任务要求
请从以下维度分析，列出该品类下 **5-8 个主要竞品品牌及其代表产品**：

1. **品牌名称** - 该品类内的主要竞争品牌
2. **代表产品** - 每个品牌最具竞争力的 1 个产品
3. **估算价格** - 该产品的大致价格区间
4. **估算月销量** - 基于你对该品类的了解估算
5. **竞争理由** - 为什么它是竞品（品类相同/价格带重叠/目标客群重叠等）
6. **竞争相关度** - 0到1之间的分数，1表示最直接的竞品

## 输出格式
请严格按照以下 JSON 格式输出，不要输出任何其他内容：
```json
[
  {{
    "brand": "品牌名",
    "product_name": "产品名称",
    "platform": "jd",
    "estimated_price": 999,
    "estimated_monthly_sales": 5000,
    "discovery_reason": "同品类直接竞品，价格带重叠，京东月销Top3",
    "relevance_score": 0.95
  }}
]
```

注意:
- platform 只能是: jd, tmall, pdd, taobao 之一
- relevance_score 在 0-1 之间
- 不要包含用户自己的产品"{user_product.product_name}"
- 基于你对中国电商市场的了解，给出真实存在的品牌和产品"""

        # 调用 LLM
        try:
            result = await self.llm.chat(
                user_id=user_id,
                tier=TaskTier.TIER_3_ANALYSIS,
                messages=[
                    {"role": "system", "content": "你是专业的市场竞品分析师，精通中国各行业的竞争格局。请直接输出 JSON，不要任何额外说明。"},
                    {"role": "user", "content": prompt},
                ],
                task_type="competitor_discovery",
                temperature=0.3,
            )
        except Exception as e:
            logger.error(f"[Discovery] LLM 调用失败: {e}")
            raise RuntimeError(f"LLM 调用失败: {e}")

        # 解析 LLM 返回
        content = result["content"]
        competitors_data = self._parse_llm_response(content)

        if not competitors_data:
            logger.warning("[Discovery] LLM 返回无法解析为竞品列表")
            return []

        # 存入数据库
        discoveries = []
        for comp in competitors_data:
            discovery = CompetitorDiscovery(
                user_product_id=user_product.id,
                brand=comp.get("brand", "未知"),
                product_name=comp.get("product_name", "未知产品"),
                platform=comp.get("platform", "jd"),
                price=comp.get("estimated_price"),
                monthly_sales=comp.get("estimated_monthly_sales"),
                discovery_reason=comp.get("discovery_reason", ""),
                relevance_score=min(1.0, max(0.0, comp.get("relevance_score", 0.5))),
                status="pending",
            )
            self.db.add(discovery)
            discoveries.append(discovery)

        await self.db.flush()

        logger.info(f"[Discovery] 发现 {len(discoveries)} 个竞品候选")
        return discoveries

    def _parse_llm_response(self, content: str) -> list[dict]:
        """解析 LLM 返回的 JSON"""
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块中提取
        import re
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找到 [ 开头 ] 结尾的内容
        bracket_match = re.search(r'\[[\s\S]*\]', content)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.error(f"[Discovery] 无法解析 LLM 返回: {content[:200]}")
        return []

    async def confirm_candidate(self, discovery_id: int) -> CompetitorProduct:
        """确认一个竞品候选，转入持续监测"""
        result = await self.db.execute(
            select(CompetitorDiscovery).where(CompetitorDiscovery.id == discovery_id)
        )
        discovery = result.scalar_one_or_none()
        if not discovery:
            raise ValueError(f"竞品候选 {discovery_id} 不存在")

        discovery.status = "confirmed"

        # 创建 CompetitorProduct 记录
        competitor = CompetitorProduct(
            user_product_id=discovery.user_product_id,
            discovery_id=discovery.id,
            brand=discovery.brand,
            product_name=discovery.product_name,
            platform=discovery.platform,
            price=discovery.price,
            product_url=discovery.product_url,
        )
        self.db.add(competitor)
        await self.db.flush()

        logger.info(f"[Discovery] 确认竞品: {discovery.brand} - {discovery.product_name}")
        return competitor

    async def reject_candidate(self, discovery_id: int):
        """排除一个竞品候选"""
        result = await self.db.execute(
            select(CompetitorDiscovery).where(CompetitorDiscovery.id == discovery_id)
        )
        discovery = result.scalar_one_or_none()
        if not discovery:
            raise ValueError(f"竞品候选 {discovery_id} 不存在")

        discovery.status = "rejected"
        await self.db.flush()
        logger.info(f"[Discovery] 排除竞品: {discovery.brand} - {discovery.product_name}")

    async def get_candidates(self, user_product_id: int, status: Optional[str] = None) -> list[CompetitorDiscovery]:
        """获取竞品候选列表"""
        query = select(CompetitorDiscovery).where(
            CompetitorDiscovery.user_product_id == user_product_id
        )
        if status:
            query = query.where(CompetitorDiscovery.status == status)
        query = query.order_by(CompetitorDiscovery.relevance_score.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())


