"""
CrabRes Growth Daemon — 永远在线的增长引擎

学习自 Claude Code KAIROS：
- 心跳机制：每 30 分钟 tick 一次
- 用户不在时自主执行低风险任务
- 用户在时展示发现、等待确认
- 午夜边界：生成今日增长日报
- Growth Dream：空闲时整理记忆

和 KAIROS 的区别：
- KAIROS 监控代码变化，我们监控市场变化
- KAIROS 的 tick 间隔 5 分钟（代码变化快），我们 30 分钟（市场变化慢）
- 我们有 Growth Dream（夜间记忆蒸馏）
"""

import asyncio
import logging
from datetime import datetime, time as dtime
from typing import Optional

logger = logging.getLogger(__name__)


class GrowthDaemon:
    """
    后台增长引擎
    
    主动性分级：
    L0: 被动响应（用户问才答）
    L1: 提醒（到点提醒执行任务）
    L2: 主动发现（发现机会/威胁主动通知）——MVP 目标
    L3: 自主执行（低风险操作自动做）
    """

    TICK_INTERVAL = 1800  # 30 分钟

    def __init__(self, memory, tools, notification_service):
        self.memory = memory
        self.tools = tools
        self.notifier = notification_service
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """启动 daemon"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🦀 Growth Daemon started")

    async def stop(self):
        """停止 daemon"""
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("🦀 Growth Daemon stopped")

    async def _run_loop(self):
        """主循环"""
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Daemon tick error: {e}")

            # 检查是否到午夜边界
            now = datetime.now()
            if now.hour == 0 and now.minute < 5:
                await self._midnight_boundary()

            await asyncio.sleep(self.TICK_INTERVAL)

    async def _tick(self):
        """
        每 30 分钟执行一次
        
        学 KAIROS 的设计：每次 tick 决定是静默还是行动
        """
        logger.debug("Growth Daemon tick")

        discoveries = []

        # 1. 扫描竞品变化
        competitor_changes = await self._scan_competitors()
        if competitor_changes:
            discoveries.extend(competitor_changes)

        # 2. 检查内容日历到期任务
        due_tasks = await self._check_content_calendar()
        if due_tasks:
            discoveries.extend(due_tasks)

        # 3. 搜索新的相关讨论（Reddit/X/HN）
        # 只在有明确的产品信息时才搜索
        product = await self.memory.load("product")
        if product:
            new_discussions = await self._scan_social_mentions(product)
            if new_discussions:
                discoveries.extend(new_discussions)

        # 如果有发现，通知用户
        if discoveries:
            await self._notify_user(discoveries)

    async def _scan_competitors(self) -> list[dict]:
        """扫描竞品变化"""
        # TODO: 实现竞品网站定期抓取对比
        return []

    async def _check_content_calendar(self) -> list[dict]:
        """检查内容日历"""
        # TODO: 检查今天是否有待发布的内容
        return []

    async def _scan_social_mentions(self, product: dict) -> list[dict]:
        """搜索社媒上的相关讨论"""
        # TODO: 搜索 Reddit/X 上有人在讨论相关话题
        return []

    async def _notify_user(self, discoveries: list[dict]):
        """通知用户发现"""
        # TODO: 通过配置的渠道（邮件/飞书/Slack）通知
        for d in discoveries:
            logger.info(f"Discovery: {d}")

    async def _midnight_boundary(self):
        """午夜边界处理"""
        logger.info("Midnight boundary: generating daily growth report")
        # TODO: 生成今日增长日报
        # TODO: 准备明天的任务清单
        # TODO: 触发 Growth Dream（如果满足条件）

    async def growth_dream(self):
        """
        Growth Dream — 记忆蒸馏
        
        学 Claude Code AutoDream：
        触发条件：24 小时未整理 + 5 次以上会话
        
        四阶段：
        1. Orient: 扫描记忆目录
        2. Gather: 从最近会话提取关键信息
        3. Consolidate: 整合、消除矛盾、更新时间
        4. Prune: 修剪冗余记忆
        """
        logger.info("Starting Growth Dream...")
        # TODO: 实现四阶段记忆蒸馏
        logger.info("Growth Dream completed")
