"""
CrabRes Proactive Notifier — Agent 主动通知用户

缺失能力 #5：Daemon 发现东西后无法推送到前端

解决方案：
1. SSE 推送到前端（已有 /api/webhooks/events/stream）
2. 邮件通知（如果配置了 SMTP）
3. Telegram 推送（如果配置了 Bot Token）
4. 内存队列（前端轮询 /api/notifications）

通知触发条件：
- 竞品网站发生变化
- RSS 发现相关新内容
- Action 结果被追踪到
- 目标进度有风险
- 每日反思完成
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

NOTIFICATION_DIR = Path(".crabres/notifications")
NOTIFICATION_DIR.mkdir(parents=True, exist_ok=True)


class NotificationType:
    COMPETITOR_CHANGE = "competitor_change"
    RSS_DISCOVERY = "rss_discovery"
    ACTION_RESULT = "action_result"
    GOAL_AT_RISK = "goal_at_risk"
    DAILY_REFLECTION = "daily_reflection"
    APPROVAL_NEEDED = "approval_needed"
    SKILL_LEARNED = "skill_learned"
    SYSTEM = "system"


class Notification:
    def __init__(self, ntype: str, title: str, body: str, 
                 priority: str = "normal", data: dict = None):
        self.id = f"notif_{int(time.time()*1000)}"
        self.type = ntype
        self.title = title
        self.body = body
        self.priority = priority  # low / normal / high / urgent
        self.data = data or {}
        self.created_at = time.time()
        self.read = False
        self.delivered_via = []  # ["sse", "telegram", "email"]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "body": self.body,
            "priority": self.priority,
            "data": self.data,
            "created_at": self.created_at,
            "read": self.read,
            "delivered_via": self.delivered_via,
        }


class ProactiveNotifier:
    """
    主动通知系统 — Agent 的"嘴"

    支持多种通知渠道，按优先级尝试：
    1. SSE → 前端实时推送
    2. Telegram → 移动端推送
    3. 内存队列 → 前端轮询
    """

    def __init__(self):
        self._queue: list[Notification] = []
        self._sse_subscribers: list = []  # SSE 连接列表
        self._load_queue()

    async def notify(self, ntype: str, title: str, body: str,
                     priority: str = "normal", data: dict = None):
        """发送通知"""
        notif = Notification(ntype, title, body, priority, data)
        self._queue.append(notif)

        # 1. 尝试 SSE 推送
        if self._sse_subscribers:
            await self._push_sse(notif)
            notif.delivered_via.append("sse")

        # 2. 尝试 Telegram 推送
        if priority in ("high", "urgent"):
            try:
                await self._push_telegram(notif)
                notif.delivered_via.append("telegram")
            except Exception as e:
                logger.debug(f"Telegram push failed: {e}")

        # 3. 始终保存到队列（前端轮询兜底）
        self._save_queue()

        logger.info(f"📢 Notification: [{priority}] {title} (via {notif.delivered_via or ['queue']})")

    async def send_discovery(self, discovery: dict):
        """将 Daemon 发现转化为通知"""
        dtype = discovery.get("type", "unknown")

        if dtype == "competitor_change":
            await self.notify(
                NotificationType.COMPETITOR_CHANGE,
                f"🔍 Competitor changed: {discovery.get('url', '')}",
                json.dumps(discovery.get("changes", {}), ensure_ascii=False, default=str)[:300],
                priority="high",
                data=discovery,
            )
        elif dtype == "rss_new_item":
            await self.notify(
                NotificationType.RSS_DISCOVERY,
                f"📰 {discovery.get('source', 'RSS')}: {discovery.get('title', '')}",
                discovery.get("description", "")[:200],
                priority="normal",
                data=discovery,
            )
        elif dtype == "action_result_tracked":
            await self.notify(
                NotificationType.ACTION_RESULT,
                f"📊 Action result: {discovery.get('platform', '')}",
                json.dumps(discovery.get("result", {}), ensure_ascii=False, default=str)[:200],
                priority="normal",
                data=discovery,
            )
        elif dtype == "skill_extraction_candidate":
            await self.notify(
                NotificationType.SKILL_LEARNED,
                f"🧠 New skill candidate from {discovery.get('platform', '')}",
                discovery.get("description", "")[:200],
                priority="low",
                data=discovery,
            )

    def get_unread(self, limit: int = 20) -> list[dict]:
        """获取未读通知"""
        unread = [n for n in self._queue if not n.read]
        return [n.to_dict() for n in unread[-limit:]]

    def get_all(self, limit: int = 50) -> list[dict]:
        """获取所有通知"""
        return [n.to_dict() for n in self._queue[-limit:]]

    def mark_read(self, notification_id: str):
        """标记已读"""
        for n in self._queue:
            if n.id == notification_id:
                n.read = True
                self._save_queue()
                return True
        return False

    def mark_all_read(self):
        """全部已读"""
        for n in self._queue:
            n.read = True
        self._save_queue()

    def add_sse_subscriber(self, subscriber):
        """添加 SSE 订阅者"""
        self._sse_subscribers.append(subscriber)

    def remove_sse_subscriber(self, subscriber):
        """移除 SSE 订阅者"""
        if subscriber in self._sse_subscribers:
            self._sse_subscribers.remove(subscriber)

    async def _push_sse(self, notif: Notification):
        """通过 SSE 推送"""
        data = json.dumps(notif.to_dict(), ensure_ascii=False, default=str)
        dead = []
        for sub in self._sse_subscribers:
            try:
                await sub.put(f"event: notification\ndata: {data}\n\n")
            except Exception:
                dead.append(sub)
        for d in dead:
            self._sse_subscribers.remove(d)

    async def _push_telegram(self, notif: Notification):
        """通过 Telegram 推送"""
        import os
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            return

        import httpx
        text = f"*{notif.title}*\n\n{notif.body}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                timeout=10,
            )

    def _save_queue(self):
        data = [n.to_dict() for n in self._queue[-200:]]  # 最多保留200条
        (NOTIFICATION_DIR / "queue.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str)
        )

    def _load_queue(self):
        path = NOTIFICATION_DIR / "queue.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            for d in data:
                n = Notification(d["type"], d["title"], d["body"], d.get("priority", "normal"), d.get("data"))
                n.id = d["id"]
                n.created_at = d["created_at"]
                n.read = d.get("read", False)
                n.delivered_via = d.get("delivered_via", [])
                self._queue.append(n)
        except Exception:
            pass
