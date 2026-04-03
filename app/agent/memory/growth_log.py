"""
CrabRes Growth Log — 增长闭环的核心数据层

三个日志：
1. Action Log — 今天做了什么
2. Result Log — 结果是什么（手动填或自动追踪）
3. Strategy Log — 明天该做什么（AI 基于 1+2 生成）

判断"好"和"增长"的标准：
- 不是模糊的"效果不错"，是可量化的 benchmark
- 每个渠道有自己的"好"的定义

State 系统：
- 当前策略（正在执行的 playbook）
- 历史表现（action→result 的统计分析）
- 渠道权重（基于真实数据的动态排序）
"""

import json
import time
import uuid
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


# ===== 判断"好"的标准 =====

CHANNEL_BENCHMARKS = {
    "reddit": {
        "post": {
            "good_upvotes": 20,        # >20 upvotes = good
            "great_upvotes": 100,       # >100 = great
            "good_comments": 5,         # >5 comments = good
            "good_click_rate": 0.02,    # >2% CTR = good
        },
        "reply": {
            "good_upvotes": 5,
            "great_upvotes": 20,
        },
    },
    "x": {
        "post": {
            "good_likes": 10,
            "great_likes": 50,
            "good_replies": 3,
            "great_replies": 15,
            "good_impressions": 500,
            "great_impressions": 5000,
        },
        "thread": {
            "good_likes": 30,
            "great_likes": 200,
        },
    },
    "xiaohongshu": {
        "post": {
            "good_likes": 50,           # 小红书互动基数高
            "great_likes": 500,
            "good_collects": 20,        # 收藏比点赞更有价值
            "great_collects": 200,
            "good_comments": 10,
            "great_comments": 100,
        },
    },
    "linkedin": {
        "post": {
            "good_reactions": 20,
            "great_reactions": 100,
            "good_comments": 5,
        },
    },
    "email": {
        "outreach": {
            "good_reply_rate": 0.15,    # >15% reply rate = good
            "great_reply_rate": 0.30,
        },
    },
}


def judge_result(platform: str, action_type: str, metrics: dict) -> dict:
    """
    判断一个 action 的结果是"好"还是"差"。
    
    返回：
    {
        "verdict": "great" | "good" | "mediocre" | "poor",
        "score": 0-100,
        "reason": "为什么这么判断",
        "signals": ["具体的好/坏信号"]
    }
    """
    benchmarks = CHANNEL_BENCHMARKS.get(platform, {}).get(action_type, {})
    if not benchmarks:
        # 没有基准数据，用通用逻辑
        total_engagement = sum(v for v in metrics.values() if isinstance(v, (int, float)))
        if total_engagement > 100:
            return {"verdict": "great", "score": 90, "reason": "High total engagement", "signals": [f"Total engagement: {total_engagement}"]}
        elif total_engagement > 20:
            return {"verdict": "good", "score": 65, "reason": "Moderate engagement", "signals": [f"Total engagement: {total_engagement}"]}
        elif total_engagement > 5:
            return {"verdict": "mediocre", "score": 35, "reason": "Low engagement", "signals": [f"Total engagement: {total_engagement}"]}
        else:
            return {"verdict": "poor", "score": 10, "reason": "Minimal engagement", "signals": [f"Total engagement: {total_engagement}"]}

    signals = []
    score_points = []

    for metric_key, value in metrics.items():
        great_key = f"great_{metric_key}"
        good_key = f"good_{metric_key}"

        if great_key in benchmarks and value >= benchmarks[great_key]:
            signals.append(f"{metric_key}={value} (great, benchmark={benchmarks[great_key]})")
            score_points.append(90)
        elif good_key in benchmarks and value >= benchmarks[good_key]:
            signals.append(f"{metric_key}={value} (good, benchmark={benchmarks[good_key]})")
            score_points.append(65)
        elif good_key in benchmarks:
            pct = value / benchmarks[good_key] if benchmarks[good_key] > 0 else 0
            signals.append(f"{metric_key}={value} (below good={benchmarks[good_key]}, {pct:.0%})")
            score_points.append(max(10, int(pct * 65)))

    if not score_points:
        return {"verdict": "mediocre", "score": 30, "reason": "No matching benchmarks", "signals": signals}

    avg_score = sum(score_points) // len(score_points)
    verdict = "great" if avg_score >= 80 else "good" if avg_score >= 55 else "mediocre" if avg_score >= 30 else "poor"

    return {"verdict": verdict, "score": avg_score, "reason": f"Avg score {avg_score} across {len(score_points)} metrics", "signals": signals}


# ===== 数据模型 =====

@dataclass
class ActionEntry:
    """今日行动"""
    id: str = field(default_factory=lambda: f"act-{uuid.uuid4().hex[:8]}")
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    platform: str = ""         # reddit / x / xiaohongshu / email / other
    action_type: str = ""      # post / reply / dm / email / thread / outreach
    description: str = ""      # 做了什么（一句话）
    content_preview: str = ""  # 实际内容摘要
    url: str = ""              # 发布后的链接
    target: str = ""           # 目标（如 r/SaaS、@某博主）
    time_spent_min: int = 0    # 花了多少分钟

@dataclass
class ResultEntry:
    """今日结果"""
    id: str = field(default_factory=lambda: f"res-{uuid.uuid4().hex[:8]}")
    action_id: str = ""        # 对应哪个 action
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    metrics: dict = field(default_factory=dict)  # {"likes": 10, "replies": 2, ...}
    verdict: str = ""          # great / good / mediocre / poor
    score: int = 0             # 0-100
    notes: str = ""            # 手动备注
    auto_tracked: bool = False # 是自动追踪的还是手动填的

@dataclass
class StrategyEntry:
    """明日策略"""
    id: str = field(default_factory=lambda: f"str-{uuid.uuid4().hex[:8]}")
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    actions: list = field(default_factory=list)  # 明天要做的事
    reasoning: str = ""        # 为什么这样安排
    based_on: list = field(default_factory=list)  # 基于哪些历史数据

@dataclass
class GrowthState:
    """增长状态快照"""
    current_strategy: str = ""           # 当前正在执行的策略概述
    active_playbook: str = ""            # 当前活跃的 playbook ID
    channel_weights: dict = field(default_factory=dict)  # {"reddit": 0.4, "x": 0.35, "xiaohongshu": 0.25}
    total_actions: int = 0
    total_results: int = 0
    avg_score: float = 0.0
    best_channel: str = ""
    worst_channel: str = ""
    streak_days: int = 0
    last_action_date: str = ""


class GrowthLog:
    """
    增长日志系统
    
    数据存储在 .crabres/memory/{user_id}/growth_log/ 下
    """

    def __init__(self, base_dir: str = ".crabres/memory"):
        self.base_dir = Path(base_dir)
        self.log_dir = self.base_dir / "growth_log"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.log_dir / f"{name}.json"

    def _load(self, name: str) -> list:
        p = self._path(name)
        if not p.exists():
            return []
        try:
            return json.loads(p.read_text())
        except Exception:
            return []

    def _save(self, name: str, data: list):
        self._path(name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    # ===== Action Log =====

    async def log_action(self, platform: str, action_type: str, description: str,
                         content_preview: str = "", url: str = "", target: str = "",
                         time_spent_min: int = 0) -> ActionEntry:
        entry = ActionEntry(
            platform=platform, action_type=action_type,
            description=description, content_preview=content_preview,
            url=url, target=target, time_spent_min=time_spent_min,
        )
        actions = self._load("actions")
        actions.append(asdict(entry))
        self._save("actions", actions)
        logger.info(f"Action logged: {platform}/{action_type} — {description[:50]}")
        return entry

    async def get_actions(self, date: str = None) -> list[dict]:
        actions = self._load("actions")
        if date:
            actions = [a for a in actions if a.get("date") == date]
        return actions

    async def get_today_actions(self) -> list[dict]:
        return await self.get_actions(datetime.now().strftime("%Y-%m-%d"))

    # ===== Result Log =====

    async def log_result(self, action_id: str, metrics: dict, notes: str = "",
                         auto_tracked: bool = False) -> ResultEntry:
        # 找到对应的 action 获取 platform 和 action_type
        actions = self._load("actions")
        action = next((a for a in actions if a.get("id") == action_id), {})
        platform = action.get("platform", "")
        action_type = action.get("action_type", "")

        # 自动判断好坏
        judgment = judge_result(platform, action_type, metrics)

        entry = ResultEntry(
            action_id=action_id,
            metrics=metrics,
            verdict=judgment["verdict"],
            score=judgment["score"],
            notes=notes or judgment["reason"],
            auto_tracked=auto_tracked,
        )
        results = self._load("results")
        results.append(asdict(entry))
        self._save("results", results)
        logger.info(f"Result logged for {action_id}: {judgment['verdict']} (score={judgment['score']})")
        return entry

    async def get_results(self, date: str = None) -> list[dict]:
        results = self._load("results")
        if date:
            results = [r for r in results if r.get("date") == date]
        return results

    # ===== Strategy Log =====

    async def log_strategy(self, actions: list, reasoning: str, based_on: list = None) -> StrategyEntry:
        entry = StrategyEntry(actions=actions, reasoning=reasoning, based_on=based_on or [])
        strategies = self._load("strategies")
        strategies.append(asdict(entry))
        self._save("strategies", strategies)
        return entry

    async def get_latest_strategy(self) -> Optional[dict]:
        strategies = self._load("strategies")
        return strategies[-1] if strategies else None

    # ===== Growth State =====

    async def compute_state(self) -> GrowthState:
        """基于所有历史数据计算当前增长状态"""
        actions = self._load("actions")
        results = self._load("results")

        # 渠道统计
        channel_scores = {}  # platform → [scores]
        for r in results:
            # 找对应 action 的 platform
            action = next((a for a in actions if a.get("id") == r.get("action_id")), {})
            platform = action.get("platform", "unknown")
            channel_scores.setdefault(platform, []).append(r.get("score", 0))

        # 计算渠道权重（基于平均分数）
        channel_weights = {}
        channel_avgs = {}
        total_avg = 0
        for platform, scores in channel_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            channel_avgs[platform] = avg
            total_avg += avg

        if total_avg > 0:
            for platform, avg in channel_avgs.items():
                channel_weights[platform] = round(avg / total_avg, 2)

        # 连胜天数
        dates_with_actions = sorted(set(a.get("date", "") for a in actions))
        streak = 0
        today = datetime.now().strftime("%Y-%m-%d")
        check_date = today
        for i in range(len(dates_with_actions) - 1, -1, -1):
            if dates_with_actions[i] == check_date:
                streak += 1
                # 计算前一天
                from datetime import timedelta
                d = datetime.strptime(check_date, "%Y-%m-%d") - timedelta(days=1)
                check_date = d.strftime("%Y-%m-%d")
            else:
                break

        # 总体统计
        all_scores = [r.get("score", 0) for r in results]
        best = max(channel_avgs, key=channel_avgs.get) if channel_avgs else ""
        worst = min(channel_avgs, key=channel_avgs.get) if channel_avgs else ""

        return GrowthState(
            channel_weights=channel_weights,
            total_actions=len(actions),
            total_results=len(results),
            avg_score=round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
            best_channel=best,
            worst_channel=worst,
            streak_days=streak,
            last_action_date=dates_with_actions[-1] if dates_with_actions else "",
        )

    async def get_state_prompt(self) -> str:
        """生成可注入 Coordinator prompt 的状态文本"""
        state = await self.compute_state()
        if state.total_actions == 0:
            return ""

        lines = [
            "## GROWTH STATE (from real execution data)",
            f"- Total actions: {state.total_actions} | Results tracked: {state.total_results}",
            f"- Average score: {state.avg_score}/100",
            f"- Streak: {state.streak_days} consecutive days",
        ]

        if state.channel_weights:
            lines.append("- Channel weights (based on real performance):")
            for ch, w in sorted(state.channel_weights.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  - {ch}: {w:.0%}")

        if state.best_channel:
            lines.append(f"- Best performing channel: {state.best_channel}")
        if state.worst_channel and state.worst_channel != state.best_channel:
            lines.append(f"- Worst performing channel: {state.worst_channel} (consider reducing investment)")

        lines.append("\nAdjust strategy based on these REAL performance signals, not assumptions.")
        return "\n".join(lines)
