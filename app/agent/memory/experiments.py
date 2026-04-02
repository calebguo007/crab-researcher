"""
CrabRes Growth Experiments — action→result 闭环追踪

这是让 CrabRes 从"玩具"变成"增长操作系统"的核心数据层。

每个增长行动（发帖、DM、邮件）都被记录为一个 GrowthAction。
每个行动的效果被追踪为 GrowthResult。
一批行动组成一个 GrowthExperiment，可以被总结为可复用的增长规律。
"""

import json
import time
import uuid
import logging
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class GrowthAction:
    """一次增长行动的记录"""
    id: str = field(default_factory=lambda: f"act-{uuid.uuid4().hex[:8]}")
    experiment_id: str = ""
    platform: str = ""          # reddit / x / linkedin / email / hackernews
    action_type: str = ""       # post / reply / dm / email / comment
    content_preview: str = ""   # 发布内容的前 200 字
    url: str = ""               # 发布后的链接
    posted_at: float = 0.0
    status: str = "pending"     # pending / posted / tracked / failed
    metadata: dict = field(default_factory=dict)


@dataclass
class GrowthResult:
    """一次行动的效果追踪"""
    action_id: str = ""
    tracked_at: float = field(default_factory=time.time)
    metrics: dict = field(default_factory=dict)
    # metrics 示例: {"likes": 10, "replies": 2, "upvotes": 50, "clicks": 5}
    conversion: dict = field(default_factory=dict)
    # conversion 示例: {"signups": 2, "revenue_usd": 0}
    raw_data: dict = field(default_factory=dict)


@dataclass
class GrowthExperiment:
    """一批增长实验"""
    id: str = field(default_factory=lambda: f"exp-{uuid.uuid4().hex[:8]}")
    goal: str = ""              # "Get 50 signups from Reddit this week"
    hypothesis: str = ""        # "数字标题帖比叙事帖转化率高"
    platform: str = ""          # 主要平台
    actions: list[str] = field(default_factory=list)  # action IDs
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    status: str = "active"      # active / completed / abandoned
    conclusion: str = ""        # Agent 总结
    learnings: list[str] = field(default_factory=list)  # 提取的规律


class ExperimentTracker:
    """
    增长实验追踪器
    
    数据持久化在 .crabres/memory/{user_id}/execution/ 下
    """

    def __init__(self, base_dir: str = ".crabres/memory"):
        self.base_dir = Path(base_dir)
        self._ensure_dirs()

    def _ensure_dirs(self):
        (self.base_dir / "execution").mkdir(parents=True, exist_ok=True)

    def _experiments_path(self) -> Path:
        return self.base_dir / "execution" / "experiments.json"

    def _actions_path(self) -> Path:
        return self.base_dir / "execution" / "actions.json"

    def _results_path(self) -> Path:
        return self.base_dir / "execution" / "results.json"

    def _learnings_path(self) -> Path:
        return self.base_dir / "execution" / "learnings.json"

    def _load_json(self, path: Path) -> list:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    def _save_json(self, path: Path, data: list):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    # ===== Experiments =====

    async def create_experiment(self, goal: str, hypothesis: str = "", platform: str = "") -> GrowthExperiment:
        exp = GrowthExperiment(goal=goal, hypothesis=hypothesis, platform=platform)
        experiments = self._load_json(self._experiments_path())
        experiments.append(asdict(exp))
        self._save_json(self._experiments_path(), experiments)
        logger.info(f"Created experiment {exp.id}: {goal}")
        return exp

    async def get_experiments(self, status: str = None) -> list[dict]:
        experiments = self._load_json(self._experiments_path())
        if status:
            experiments = [e for e in experiments if e.get("status") == status]
        return experiments

    async def get_experiment(self, experiment_id: str) -> Optional[dict]:
        for e in self._load_json(self._experiments_path()):
            if e.get("id") == experiment_id:
                return e
        return None

    async def complete_experiment(self, experiment_id: str, conclusion: str, learnings: list[str]):
        experiments = self._load_json(self._experiments_path())
        for e in experiments:
            if e.get("id") == experiment_id:
                e["status"] = "completed"
                e["ended_at"] = time.time()
                e["conclusion"] = conclusion
                e["learnings"] = learnings
                break
        self._save_json(self._experiments_path(), experiments)

        # 同时保存 learnings 到独立文件（供 Coordinator 加载）
        all_learnings = self._load_json(self._learnings_path())
        for l in learnings:
            all_learnings.append({
                "experiment_id": experiment_id,
                "learning": l,
                "created_at": time.time(),
            })
        # 只保留最近 50 条规律
        all_learnings = all_learnings[-50:]
        self._save_json(self._learnings_path(), all_learnings)
        logger.info(f"Completed experiment {experiment_id}: +{len(learnings)} learnings")

    # ===== Actions =====

    async def record_action(
        self,
        platform: str,
        action_type: str,
        url: str = "",
        content_preview: str = "",
        experiment_id: str = "",
        metadata: dict = None,
    ) -> GrowthAction:
        action = GrowthAction(
            experiment_id=experiment_id,
            platform=platform,
            action_type=action_type,
            url=url,
            content_preview=content_preview[:200],
            posted_at=time.time(),
            status="posted" if url else "pending",
            metadata=metadata or {},
        )
        actions = self._load_json(self._actions_path())
        actions.append(asdict(action))
        self._save_json(self._actions_path(), actions)

        # 把 action ID 加到 experiment
        if experiment_id:
            experiments = self._load_json(self._experiments_path())
            for e in experiments:
                if e.get("id") == experiment_id:
                    e.setdefault("actions", []).append(action.id)
                    break
            self._save_json(self._experiments_path(), experiments)

        logger.info(f"Recorded action {action.id}: {platform}/{action_type} → {url[:50] if url else 'no url'}")
        return action

    async def get_actions(self, experiment_id: str = None, status: str = None) -> list[dict]:
        actions = self._load_json(self._actions_path())
        if experiment_id:
            actions = [a for a in actions if a.get("experiment_id") == experiment_id]
        if status:
            actions = [a for a in actions if a.get("status") == status]
        return actions

    async def get_trackable_actions(self) -> list[dict]:
        """获取所有需要追踪效果的 action（有 URL、status=posted、还没 tracked）"""
        actions = self._load_json(self._actions_path())
        return [
            a for a in actions
            if a.get("url") and a.get("status") == "posted"
        ]

    async def update_action_status(self, action_id: str, status: str):
        actions = self._load_json(self._actions_path())
        for a in actions:
            if a.get("id") == action_id:
                a["status"] = status
                break
        self._save_json(self._actions_path(), actions)

    # ===== Results =====

    async def record_result(self, action_id: str, metrics: dict, conversion: dict = None, raw_data: dict = None):
        result = GrowthResult(
            action_id=action_id,
            metrics=metrics,
            conversion=conversion or {},
            raw_data=raw_data or {},
        )
        results = self._load_json(self._results_path())
        results.append(asdict(result))
        self._save_json(self._results_path(), results)

        # 标记 action 为已追踪
        await self.update_action_status(action_id, "tracked")
        logger.info(f"Recorded result for {action_id}: {metrics}")

    async def get_results(self, action_id: str = None) -> list[dict]:
        results = self._load_json(self._results_path())
        if action_id:
            results = [r for r in results if r.get("action_id") == action_id]
        return results

    # ===== Learnings =====

    async def get_learnings(self, limit: int = 20) -> list[dict]:
        """获取最近的增长规律（供 Coordinator prompt 注入）"""
        learnings = self._load_json(self._learnings_path())
        return learnings[-limit:]

    async def get_learnings_text(self) -> str:
        """格式化为可注入 prompt 的文本"""
        learnings = await self.get_learnings(20)
        if not learnings:
            return ""
        lines = ["## LEARNED GROWTH PATTERNS (from real execution data)"]
        for l in learnings:
            lines.append(f"- {l.get('learning', '')}")
        lines.append("\nUse these patterns when planning the next experiment. Prioritize what worked. Kill what didn't.")
        return "\n".join(lines)

    # ===== Summary =====

    async def get_summary(self) -> dict:
        """获取实验追踪总览"""
        experiments = self._load_json(self._experiments_path())
        actions = self._load_json(self._actions_path())
        results = self._load_json(self._results_path())
        learnings = self._load_json(self._learnings_path())

        total_actions = len(actions)
        tracked = len([a for a in actions if a.get("status") == "tracked"])
        total_likes = sum(r.get("metrics", {}).get("likes", 0) + r.get("metrics", {}).get("upvotes", 0) for r in results)
        total_clicks = sum(r.get("metrics", {}).get("clicks", 0) for r in results)

        return {
            "experiments": len(experiments),
            "active_experiments": len([e for e in experiments if e.get("status") == "active"]),
            "total_actions": total_actions,
            "tracked_actions": tracked,
            "total_engagement": total_likes,
            "total_clicks": total_clicks,
            "learnings_count": len(learnings),
        }
