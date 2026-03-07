"""
消息通知服务
支持: 企业微信机器人 / 飞书机器人
特性: 失败自动重试、丰富的卡片模板、飞书签名校验
"""

import asyncio
import base64
import hashlib
import hmac
import logging
import time
from typing import Optional

import httpx

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# 告警颜色映射
SEVERITY_COLORS = {
    "info": "blue",
    "warning": "orange",
    "critical": "red",
}

SEVERITY_EMOJI = {
    "info": "ℹ️",
    "warning": "⚠️",
    "critical": "🚨",
}


class NotificationService:
    """消息推送服务（带重试机制）"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 3, 5]  # 重试间隔（秒）

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)

    async def close(self):
        await self.client.aclose()

    # ================================================================
    # 企业微信
    # ================================================================

    async def send_wecom(self, content: str, msg_type: str = "markdown") -> bool:
        """发送企业微信机器人消息（带重试）"""
        url = settings.WECOM_WEBHOOK_URL
        if not url:
            logger.warning("[Notify] 企业微信Webhook未配置")
            return False

        payload = {
            "msgtype": msg_type,
            msg_type: {"content": content},
        }

        return await self._post_with_retry(
            url, payload, platform="企业微信",
            success_check=lambda data: data.get("errcode") == 0,
        )

    # ================================================================
    # 飞书 — 多种卡片模板
    # ================================================================

    async def send_feishu(self, title: str, content: str, severity: str = "info") -> bool:
        """发送飞书富文本卡片消息（带重试）"""
        url = settings.FEISHU_WEBHOOK_URL
        if not url:
            logger.warning("[Notify] 飞书Webhook未配置")
            return False

        color = SEVERITY_COLORS.get(severity, "blue")
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🦀 {title}"},
                    "template": color,
                },
                "elements": [
                    {"tag": "markdown", "content": content},
                ],
            },
        }

        return await self._post_with_retry(
            url, payload, platform="飞书", is_feishu=True,
            success_check=lambda data: data.get("code") == 0 or data.get("StatusCode") == 0,
        )

    async def send_feishu_price_alert(
        self,
        brand: str,
        product_name: str,
        old_price: float,
        new_price: float,
        change_pct: float,
        platform: str,
        url: str = "",
    ) -> bool:
        """飞书 — 价格变动卡片"""
        direction = "📈 上涨" if change_pct > 0 else "📉 下降"
        severity = "critical" if abs(change_pct) > 30 else "warning"
        color = SEVERITY_COLORS.get(severity, "orange")

        content = (
            f"**{brand}** 在 **{platform}** 价格{direction}\n\n"
            f"商品: {product_name}\n"
            f"原价: ¥{old_price:.2f}\n"
            f"现价: **¥{new_price:.2f}**\n"
            f"变动: **{'+' if change_pct > 0 else ''}{change_pct:.1f}%**"
        )

        elements = [{"tag": "markdown", "content": content}]

        if url:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "查看商品"},
                        "type": "primary",
                        "url": url,
                    }
                ],
            })

        webhook_url = settings.FEISHU_WEBHOOK_URL
        if not webhook_url:
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🦀 价格变动 - {brand}"},
                    "template": color,
                },
                "elements": elements,
            },
        }

        return await self._post_with_retry(
            webhook_url, payload, platform="飞书", is_feishu=True,
            success_check=lambda data: data.get("code") == 0 or data.get("StatusCode") == 0,
        )

    async def send_feishu_sentiment_alert(
        self,
        brand: str,
        platform: str,
        sentiment_score: float,
        mention_count: int,
        hot_topics: list[str],
        analysis: str = "",
    ) -> bool:
        """飞书 — 舆情预警卡片"""
        score_desc = "差评较多" if sentiment_score < 0.3 else "有负面趋势" if sentiment_score < 0.5 else "正常"
        severity = "critical" if sentiment_score < 0.3 else "warning" if sentiment_score < 0.5 else "info"
        color = SEVERITY_COLORS.get(severity, "blue")

        topics_text = "、".join(hot_topics[:5]) if hot_topics else "暂无"
        content = (
            f"**{brand}** 在 **{platform}** 舆情预警\n\n"
            f"情感评分: **{sentiment_score:.2f}** ({score_desc})\n"
            f"提及量: **{mention_count}**\n"
            f"热门话题: {topics_text}"
        )
        if analysis:
            content += f"\n\n> {analysis}"

        webhook_url = settings.FEISHU_WEBHOOK_URL
        if not webhook_url:
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🦀 舆情预警 - {brand}"},
                    "template": color,
                },
                "elements": [{"tag": "markdown", "content": content}],
            },
        }

        return await self._post_with_retry(
            webhook_url, payload, platform="飞书", is_feishu=True,
            success_check=lambda data: data.get("code") == 0 or data.get("StatusCode") == 0,
        )

    async def send_feishu_new_product_alert(
        self,
        brand: str,
        platform: str,
        new_products: list[dict],
    ) -> bool:
        """飞书 — 新品上市卡片"""
        product_lines = []
        for p in new_products[:5]:
            name = p.get("name", "未知")
            price = p.get("price")
            line = f"- **{name}**"
            if price:
                line += f"  ¥{price}"
            product_lines.append(line)

        content = (
            f"**{brand}** 在 **{platform}** 发现新品\n\n"
            + "\n".join(product_lines)
        )
        if len(new_products) > 5:
            content += f"\n- ...共 {len(new_products)} 个新品"

        webhook_url = settings.FEISHU_WEBHOOK_URL
        if not webhook_url:
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🦀 新品监测 - {brand}"},
                    "template": "green",
                },
                "elements": [{"tag": "markdown", "content": content}],
            },
        }

        return await self._post_with_retry(
            webhook_url, payload, platform="飞书", is_feishu=True,
            success_check=lambda data: data.get("code") == 0 or data.get("StatusCode") == 0,
        )

    async def send_feishu_daily_summary(
        self,
        tasks_executed: int,
        alerts_count: int,
        brands_monitored: list[str],
        highlights: list[str],
    ) -> bool:
        """飞书 — 每日监测摘要卡片"""
        brands_text = "、".join(brands_monitored[:10]) if brands_monitored else "暂无"
        highlights_text = "\n".join(f"- {h}" for h in highlights[:10]) if highlights else "- 今日无重要变化"

        content = (
            f"**今日监测摘要**\n\n"
            f"执行任务: **{tasks_executed}** 个\n"
            f"触发告警: **{alerts_count}** 个\n"
            f"监测品牌: {brands_text}\n\n"
            f"**重点变化:**\n{highlights_text}"
        )

        webhook_url = settings.FEISHU_WEBHOOK_URL
        if not webhook_url:
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": "🦀 每日监测报告"},
                    "template": "blue",
                },
                "elements": [{"tag": "markdown", "content": content}],
            },
        }

        return await self._post_with_retry(
            webhook_url, payload, platform="飞书", is_feishu=True,
            success_check=lambda data: data.get("code") == 0 or data.get("StatusCode") == 0,
        )

    # ================================================================
    # 统一入口
    # ================================================================

    async def send_alert(
        self, title: str, content: str, severity: str = "info",
        alert_data: Optional[dict] = None,
    ) -> dict:
        """
        统一告警入口 — 同时发送到所有已配置的平台
        alert_data: 可选，用于生成更丰富的飞书卡片
        """
        emoji = SEVERITY_EMOJI.get(severity, "📢")
        full_title = f"{emoji} {title}"
        full_content = f"**{full_title}**\n\n{content}"

        results = {}

        # 企业微信
        if settings.WECOM_WEBHOOK_URL:
            results["wecom"] = await self.send_wecom(full_content)

        # 飞书
        if settings.FEISHU_WEBHOOK_URL:
            results["feishu"] = await self.send_feishu(full_title, content, severity)

        if not results:
            logger.warning("[Notify] 未配置任何通知平台，告警被忽略")

        return results

    # ================================================================
    # 飞书签名
    # ================================================================

    @staticmethod
    def _gen_feishu_sign(secret: str) -> tuple[str, str]:
        """生成飞书 Webhook 签名 (timestamp + sign)"""
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return timestamp, sign

    def _attach_feishu_sign(self, payload: dict) -> dict:
        """如果配置了飞书签名密钥，自动附加 timestamp + sign"""
        secret = settings.FEISHU_WEBHOOK_SECRET
        if secret:
            timestamp, sign = self._gen_feishu_sign(secret)
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        return payload

    # ================================================================
    # 内部：带重试的 POST
    # ================================================================

    async def _post_with_retry(
        self,
        url: str,
        payload: dict,
        platform: str,
        success_check=None,
        is_feishu: bool = False,
    ) -> bool:
        """带指数退避重试的 POST 请求"""
        for attempt in range(self.MAX_RETRIES):
            try:
                # 飞书每次重试都要重新生成签名（timestamp 必须新鲜）
                send_payload = dict(payload)
                if is_feishu:
                    send_payload = self._attach_feishu_sign(send_payload)

                resp = await self.client.post(url, json=send_payload)
                data = resp.json()

                if success_check and success_check(data):
                    logger.info(f"[Notify] {platform}发送成功")
                    return True
                elif not success_check and resp.status_code == 200:
                    logger.info(f"[Notify] {platform}发送成功(HTTP 200)")
                    return True
                else:
                    logger.warning(
                        f"[Notify] {platform}发送失败(尝试 {attempt+1}/{self.MAX_RETRIES}): {data}"
                    )

            except httpx.TimeoutException:
                logger.warning(
                    f"[Notify] {platform}超时(尝试 {attempt+1}/{self.MAX_RETRIES})"
                )
            except Exception as e:
                logger.error(
                    f"[Notify] {platform}异常(尝试 {attempt+1}/{self.MAX_RETRIES}): {e}"
                )

            # 等待后重试
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[attempt]
                logger.info(f"[Notify] {delay}秒后重试...")
                await asyncio.sleep(delay)

        logger.error(f"[Notify] {platform}发送失败，已达最大重试次数({self.MAX_RETRIES})")
        return False
