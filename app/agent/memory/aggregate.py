"""
CrabRes Growth Intelligence — 跨用户匿名化学习

这是壁垒的核心：
100 个用户 × 3 个月 × 每天 5 次实验 = 45,000 条坑位数据。
新模型可以复制我们的架构，但复制不了我们的数据。

当前：从本地文件聚合（单用户）。
未来：迁移到 PostgreSQL 后，跨用户聚合。
"""

import json
import logging
from pathlib import Path
from typing import Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class GrowthIntelligence:
    """
    从所有用户的实验数据中提取通用增长规律。
    
    这是"Google 搜不到、AI 猜不出"的私域数据。
    """

    def __init__(self, base_dir: str = ".crabres/memory"):
        self.base_dir = Path(base_dir)

    async def aggregate_channel_stats(self) -> dict:
        """
        聚合所有用户的渠道效果数据。
        
        输出示例：
        {
            "reddit": {"total_actions": 45, "avg_engagement": 23.5, "top_subreddit": "r/SaaS"},
            "x": {"total_actions": 30, "avg_engagement": 15.2, "best_time": "Tue 9am"},
            "xiaohongshu": {"total_actions": 12, "avg_engagement": 890, "top_keyword": "AI工具"},
        }
        """
        channel_data = defaultdict(lambda: {"actions": 0, "total_engagement": 0, "results": []})

        # 扫描所有用户的实验数据
        for user_dir in self.base_dir.iterdir():
            if not user_dir.is_dir():
                continue
            results_path = user_dir / "execution" / "results.json"
            actions_path = user_dir / "execution" / "actions.json"

            if not results_path.exists() or not actions_path.exists():
                continue

            try:
                results = json.loads(results_path.read_text())
                actions = json.loads(actions_path.read_text())

                # 建立 action_id → action 映射
                action_map = {a.get("id"): a for a in actions}

                for result in results:
                    action_id = result.get("action_id", "")
                    action = action_map.get(action_id, {})
                    platform = action.get("platform", "unknown")
                    metrics = result.get("metrics", {})

                    engagement = sum(metrics.values())
                    channel_data[platform]["actions"] += 1
                    channel_data[platform]["total_engagement"] += engagement
                    channel_data[platform]["results"].append({
                        "engagement": engagement,
                        "action_type": action.get("action_type", ""),
                        "metrics": metrics,
                    })
            except Exception as e:
                logger.debug(f"Failed to read experiment data from {user_dir}: {e}")

        # 计算聚合统计
        stats = {}
        for platform, data in channel_data.items():
            count = data["actions"]
            if count == 0:
                continue
            stats[platform] = {
                "total_actions": count,
                "avg_engagement": round(data["total_engagement"] / count, 1),
                "total_engagement": data["total_engagement"],
            }

        return stats

    async def get_channel_benchmarks(self, platform: str) -> dict:
        """获取特定渠道的基准数据"""
        stats = await self.aggregate_channel_stats()
        return stats.get(platform, {})

    async def get_intelligence_prompt(self) -> str:
        """生成可注入 Coordinator prompt 的智能数据摘要"""
        stats = await self.aggregate_channel_stats()
        if not stats:
            return ""

        lines = ["## GROWTH INTELLIGENCE (from real user experiments across CrabRes)"]
        for platform, data in sorted(stats.items(), key=lambda x: x[1]["total_actions"], reverse=True):
            lines.append(
                f"- {platform}: {data['total_actions']} experiments tracked, "
                f"avg engagement {data['avg_engagement']}"
            )

        lines.append("\nThese are REAL data points from CrabRes users, not estimates. Use them to calibrate expectations.")
        return "\n".join(lines)

    async def extract_learnings_across_users(self) -> list[str]:
        """
        跨用户提取增长规律。
        
        这是壁垒：
        "带数字的 Reddit 标题转化率是纯文字的 3x" 
        — 这不是 LLM 猜的，是从 45 次实验中总结的。
        """
        learnings = []

        # 扫描所有用户的 learnings
        for user_dir in self.base_dir.iterdir():
            if not user_dir.is_dir():
                continue
            learnings_path = user_dir / "execution" / "learnings.json"
            if learnings_path.exists():
                try:
                    data = json.loads(learnings_path.read_text())
                    for item in data:
                        learning = item.get("learning", "")
                        if learning:
                            learnings.append(learning)
                except Exception:
                    pass

        return learnings
