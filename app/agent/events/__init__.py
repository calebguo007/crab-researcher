"""
CrabRes Event Bus — Agent 的神经系统

解决的核心问题：
- Agent 之前是纯被动的（用户不说话就不动）
- 现在 Agent 能接收外部事件并主动反应

架构：
  外部世界 → Webhook → EventBus → Daemon/Notifier → 用户
  Daemon tick → EventBus → 前端 SSE → 实时展示

支持两种模式：
1. Redis Pub/Sub（生产环境，多实例共享）
2. 内存队列（开发环境，零依赖）
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)


class EventBus:
    """
    事件总线 — 连接 Agent 内部组件和外部世界

    事件类型：
    - daemon.discovery: Daemon 发现了新信息
    - daemon.tick: Daemon 完成一次扫描
    - webhook.github: GitHub 事件（star, issue, PR）
    - webhook.telegram: Telegram 新消息
    - webhook.stripe: 支付事件
    - agent.response: Agent 完成一次回复
    - agent.tool_call: Agent 调用了工具
    - skill.learned: 新 Skill 被学习
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._redis_url = redis_url
        self._redis = None
        self._local_subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._event_log: list[dict] = []
        self._max_log_size = 100

    async def connect(self):
        """连接 Redis（如果配置了）"""
        if not self._redis_url or self._redis_url == "redis://localhost:6379":
            logger.info("📡 EventBus: using in-memory mode (no Redis)")
            return

        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(self._redis_url)
            await self._redis.ping()
            logger.info("📡 EventBus: connected to Redis")
        except ImportError:
            logger.info("📡 EventBus: redis package not installed, using in-memory mode")
        except Exception as e:
            logger.warning(f"📡 EventBus: Redis connection failed ({e}), using in-memory mode")
            self._redis = None

    async def publish(self, event_type: str, data: dict):
        """发布事件"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
            "id": f"{event_type}_{int(time.time()*1000)}",
        }

        # 记录到事件日志
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]

        # Redis 模式
        if self._redis:
            try:
                await self._redis.publish("crabres:events", json.dumps(event, default=str))
            except Exception as e:
                logger.error(f"📡 EventBus Redis publish failed: {e}")

        # 内存模式：直接推送到所有订阅者
        for queue in self._local_subscribers.get(event_type, []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                    queue.put_nowait(event)
                except Exception:
                    pass

        # 通配符订阅者
        for queue in self._local_subscribers.get("*", []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                    queue.put_nowait(event)
                except Exception:
                    pass

        logger.debug(f"📡 Event: {event_type}")

    async def subscribe(self, event_type: str = "*") -> AsyncGenerator[dict, None]:
        """订阅事件流（SSE 友好）"""
        queue: asyncio.Queue = asyncio.Queue(maxsize=50)
        self._local_subscribers[event_type].append(queue)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._local_subscribers[event_type].remove(queue)

    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 20) -> list[dict]:
        """获取最近的事件"""
        events = self._event_log
        if event_type:
            events = [e for e in events if e["type"].startswith(event_type)]
        return events[-limit:]

    async def close(self):
        if self._redis:
            await self._redis.close()


# 全局单例
_event_bus: Optional[EventBus] = None


async def get_event_bus() -> EventBus:
    """获取全局 EventBus 实例"""
    global _event_bus
    if _event_bus is None:
        from app.core.config import get_settings
        settings = get_settings()
        _event_bus = EventBus(redis_url=settings.REDIS_URL)
        await _event_bus.connect()
    return _event_bus
