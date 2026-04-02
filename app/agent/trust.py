"""
CrabRes Trust Levels — 随使用时间逐步升级自主权

Level 1 (Day 1-7):    每个策略建议需确认，每篇文案需审核
Level 2 (Day 8-21):   研究自动进行，文案生成但需审核，竞品自动追踪
Level 3 (Day 22-60):  自动生成下周内容，自动更新计划，发现机会自动准备方案
Level 4 (Manual opt-in): 自动在平台回复，自动提交目录，用户只需周审核
"""

import time
import logging
from app.agent.memory import GrowthMemory

logger = logging.getLogger(__name__)


class TrustLevel:
    CAUTIOUS = 1      # 每步确认
    BUILDING = 2      # 研究自动，输出需审核
    TRUSTED = 3       # 大部分自动，重要的需确认
    AUTOPILOT = 4     # 自动驾驶（用户手动开启）


class TrustManager:
    """管理用户的信任等级"""

    def __init__(self, memory: GrowthMemory):
        self.memory = memory

    async def get_level(self) -> int:
        """获取当前信任等级"""
        trust_data = await self.memory.load("trust_level", category="feedback") or {}

        # 检查是否手动开启了 autopilot
        if trust_data.get("autopilot_enabled"):
            return TrustLevel.AUTOPILOT

        # 基于使用天数和交互次数自动计算
        first_use = trust_data.get("first_use_at", time.time())
        days_active = (time.time() - first_use) / 86400
        total_confirmations = trust_data.get("total_confirmations", 0)
        total_sessions = trust_data.get("total_sessions", 0)

        if days_active >= 22 and total_confirmations >= 20:
            return TrustLevel.TRUSTED
        elif days_active >= 8 and total_confirmations >= 5:
            return TrustLevel.BUILDING
        else:
            return TrustLevel.CAUTIOUS

    async def record_session(self):
        """记录一次会话"""
        trust_data = await self.memory.load("trust_level", category="feedback") or {}
        if "first_use_at" not in trust_data:
            trust_data["first_use_at"] = time.time()
        trust_data["total_sessions"] = trust_data.get("total_sessions", 0) + 1
        trust_data["last_session_at"] = time.time()
        await self.memory.save("trust_level", trust_data, category="feedback")

    async def record_confirmation(self):
        """记录用户确认了一个建议"""
        trust_data = await self.memory.load("trust_level", category="feedback") or {}
        trust_data["total_confirmations"] = trust_data.get("total_confirmations", 0) + 1
        await self.memory.save("trust_level", trust_data, category="feedback")

    async def enable_autopilot(self, enabled: bool = True):
        """手动开启/关闭自动驾驶"""
        trust_data = await self.memory.load("trust_level", category="feedback") or {}
        trust_data["autopilot_enabled"] = enabled
        await self.memory.save("trust_level", trust_data, category="feedback")

    async def get_permissions(self) -> dict:
        """获取当前等级的权限"""
        level = await self.get_level()
        return {
            "level": level,
            "level_name": {1: "Cautious", 2: "Building Trust", 3: "Trusted", 4: "Autopilot"}[level],
            "auto_research": level >= 2,           # 自动执行研究
            "auto_generate_content": level >= 2,   # 自动生成内容（但需审核）
            "auto_monitor_competitors": level >= 2, # 自动监控竞品
            "auto_update_plan": level >= 3,        # 自动更新增长计划
            "auto_prepare_actions": level >= 3,    # 自动准备行动方案
            "auto_post": level >= 4,               # 自动发帖（需手动开启）
            "auto_reply": level >= 4,              # 自动回复（需手动开启）
            "auto_submit": level >= 4,             # 自动提交目录
        }
