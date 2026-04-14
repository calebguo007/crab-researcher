"""
CrabRes Goal Tracker — 目标追踪 + 自我调整

缺失能力 #2：Agent 没有目标感——不知道自己在追求什么，不会自我调整

一个真正的 Agent 应该：
1. 和用户一起设定明确的增长目标（如"30天内获得100个注册用户"）
2. 每次 tick 时检查进度
3. 进度落后时自动调整策略
4. 进度超预期时加大投入

目标结构：
- OKR 模式：Objective → Key Results → Tasks
- 每个 Key Result 有量化指标和截止日期
- 进度自动从 GrowthLog + ExperimentTracker 同步
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class KeyResult:
    """可量化的关键结果"""
    id: str = ""
    description: str = ""          # "获得100个注册用户"
    metric_name: str = ""          # "signups"
    target_value: float = 0.0      # 100
    current_value: float = 0.0     # 当前进度
    unit: str = ""                 # "users", "$", "posts"
    deadline: str = ""             # "2026-05-15"
    status: str = "active"         # active / completed / at_risk / failed
    auto_track_source: str = ""    # 自动追踪数据源（如 "growth_log.x.likes"）

    @property
    def progress_pct(self) -> float:
        if self.target_value == 0:
            return 0
        return min(100, round(self.current_value / self.target_value * 100, 1))

    @property
    def is_at_risk(self) -> bool:
        """基于时间进度判断是否有风险"""
        if not self.deadline:
            return False
        from datetime import datetime
        try:
            deadline_dt = datetime.strptime(self.deadline, "%Y-%m-%d")
            now = datetime.now()
            total_days = (deadline_dt - now).days
            if total_days <= 0:
                return self.progress_pct < 100
            # 如果时间过了一半但进度不到40%，标记为at_risk
            return self.progress_pct < 40 and total_days < 15
        except Exception:
            return False


@dataclass
class GrowthGoal:
    """增长目标（OKR）"""
    id: str = ""
    objective: str = ""            # "成为独立开发者增长工具的首选"
    key_results: list = field(default_factory=list)  # KeyResult列表
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "active"         # active / completed / paused
    strategy_adjustments: list = field(default_factory=list)  # 策略调整记录

    @property
    def overall_progress(self) -> float:
        if not self.key_results:
            return 0
        krs = [KeyResult(**kr) if isinstance(kr, dict) else kr for kr in self.key_results]
        return round(sum(kr.progress_pct for kr in krs) / len(krs), 1)


class GoalTracker:
    """
    目标追踪器 — Agent 的"方向感"

    用法：
        tracker = GoalTracker(memory)

        # 设定目标
        goal = await tracker.set_goal(
            objective="30天内获得100个注册用户",
            key_results=[
                {"description": "Reddit 发帖获得 50 upvotes", "metric_name": "reddit_upvotes", "target_value": 50, "deadline": "2026-05-01"},
                {"description": "产品注册用户达到 100", "metric_name": "signups", "target_value": 100, "deadline": "2026-05-15"},
            ]
        )

        # Daemon tick 时检查进度
        status = await tracker.check_progress()
        # → {"overall": 35%, "at_risk": ["signups"], "adjustments": ["增加Reddit发帖频率"]}
    """

    def __init__(self, memory=None):
        self.memory = memory
        self._goal_path = Path(".crabres/goals")
        self._goal_path.mkdir(parents=True, exist_ok=True)

    async def set_goal(self, objective: str, key_results: list[dict]) -> GrowthGoal:
        """设定新的增长目标"""
        goal_id = f"goal_{int(time.time())}"
        krs = []
        for i, kr in enumerate(key_results):
            krs.append(KeyResult(
                id=f"{goal_id}_kr{i}",
                description=kr.get("description", ""),
                metric_name=kr.get("metric_name", ""),
                target_value=kr.get("target_value", 0),
                unit=kr.get("unit", ""),
                deadline=kr.get("deadline", ""),
            ))

        goal = GrowthGoal(
            id=goal_id,
            objective=objective,
            key_results=[asdict(kr) for kr in krs],
        )

        self._save_goal(goal)
        logger.info(f"Goal set: {objective} ({len(krs)} key results)")
        return goal

    async def check_progress(self) -> dict:
        """
        检查目标进度 — Daemon tick 时调用

        自动从 GrowthLog 和 ExperimentTracker 同步数据
        """
        goal = self._load_active_goal()
        if not goal:
            return {"has_goal": False}

        # 同步进度数据
        await self._sync_progress(goal)

        # 检查风险
        at_risk = []
        completed = []
        for kr_data in goal.get("key_results", []):
            kr = KeyResult(**kr_data)
            if kr.is_at_risk:
                at_risk.append(kr.description)
                kr_data["status"] = "at_risk"
            elif kr.progress_pct >= 100:
                completed.append(kr.description)
                kr_data["status"] = "completed"

        # 计算总进度
        krs = [KeyResult(**kr) for kr in goal.get("key_results", [])]
        overall = round(sum(kr.progress_pct for kr in krs) / max(len(krs), 1), 1)

        # 如果有风险项，生成调整建议
        adjustments = []
        if at_risk:
            adjustments.append(f"⚠️ {len(at_risk)} key results at risk: {', '.join(at_risk)}")
            adjustments.append("Consider: increasing posting frequency, trying new channels, or adjusting targets")

        result = {
            "has_goal": True,
            "objective": goal.get("objective", ""),
            "overall_progress": overall,
            "key_results": [
                {
                    "description": kr.description,
                    "progress": kr.progress_pct,
                    "current": kr.current_value,
                    "target": kr.target_value,
                    "status": kr_data.get("status", "active"),
                }
                for kr, kr_data in zip(krs, goal.get("key_results", []))
            ],
            "at_risk": at_risk,
            "completed": completed,
            "adjustments": adjustments,
        }

        # 保存更新后的目标
        self._save_goal_data(goal)

        return result

    async def _sync_progress(self, goal: dict):
        """从真实数据源同步进度"""
        if not self.memory:
            return

        try:
            from app.agent.memory.growth_log import GrowthLog
            growth_log = GrowthLog(base_dir=str(self.memory.base_dir))
            state = await growth_log.compute_state()

            for kr_data in goal.get("key_results", []):
                metric = kr_data.get("metric_name", "")
                # 自动匹配指标
                if "action" in metric or "post" in metric:
                    kr_data["current_value"] = state.total_actions
                elif "score" in metric:
                    kr_data["current_value"] = state.avg_score
                elif "streak" in metric:
                    kr_data["current_value"] = state.streak_days
        except Exception as e:
            logger.warning(f"Progress sync failed: {e}")

    def get_goal_prompt(self) -> str:
        """生成可注入 Coordinator prompt 的目标状态"""
        goal = self._load_active_goal()
        if not goal:
            return ""

        krs = [KeyResult(**kr) for kr in goal.get("key_results", [])]
        overall = round(sum(kr.progress_pct for kr in krs) / max(len(krs), 1), 1)

        lines = [
            f"## ACTIVE GROWTH GOAL: {goal.get('objective', '')}",
            f"Overall progress: {overall}%",
            "",
        ]
        for kr in krs:
            status_icon = "✅" if kr.progress_pct >= 100 else "⚠️" if kr.is_at_risk else "🔵"
            lines.append(f"- {status_icon} {kr.description}: {kr.current_value}/{kr.target_value} ({kr.progress_pct}%)")

        if any(kr.is_at_risk for kr in krs):
            lines.append("\n⚠️ Some goals are at risk! Prioritize actions that directly impact these metrics.")

        return "\n".join(lines)

    def _save_goal(self, goal: GrowthGoal):
        data = asdict(goal)
        self._save_goal_data(data)

    def _save_goal_data(self, data: dict):
        path = self._goal_path / "active_goal.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def _load_active_goal(self) -> Optional[dict]:
        path = self._goal_path / "active_goal.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except Exception:
            return None
