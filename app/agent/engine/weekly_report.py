"""
CrabRes Weekly Report — 自动生成增长周报

缺失能力 #6：没有定期汇总能力

每周日 midnight 自动生成，包含：
1. 本周行动总结（做了什么）
2. 效果数据（结果如何）
3. 关键发现（竞品变化、市场动态）
4. 下周建议（基于数据的策略调整）
5. 目标进度（OKR 进展）
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class WeeklyReportGenerator:
    """
    周报生成器 — Agent 的"汇报能力"
    """

    def __init__(self, memory=None, llm=None):
        self.memory = memory
        self.llm = llm

    async def generate(self) -> dict:
        """生成本周周报"""
        if not self.memory or not self.llm:
            return {"error": "memory or llm not available"}

        now = datetime.now()
        week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        week_end = now.strftime("%Y-%m-%d")

        # 收集本周数据
        data = await self._collect_week_data(week_start, week_end)

        if data["total_entries"] == 0:
            return {
                "week": f"{week_start} ~ {week_end}",
                "summary": "No activity this week.",
                "generated_at": time.time(),
            }

        from app.agent.engine.llm_adapter import TaskTier
        prompt = f"""Generate a weekly growth report based on this data.

## Week: {week_start} ~ {week_end}

## Actions This Week ({data['action_count']} total)
{json.dumps(data['actions'][:15], ensure_ascii=False, default=str)[:2000]}

## Results Tracked ({data['result_count']} total)
{json.dumps(data['results'][:10], ensure_ascii=False, default=str)[:1500]}

## Daemon Discoveries ({data['discovery_count']} total)
{json.dumps(data['discoveries'][:10], ensure_ascii=False, default=str)[:1000]}

## Reflections
{json.dumps(data['reflections'][:3], ensure_ascii=False, default=str)[:1000]}

## Output Format (JSON)
{{
  "week": "{week_start} ~ {week_end}",
  "executive_summary": "2-3 sentence overview",
  "actions_summary": {{
    "total": N,
    "by_platform": {{"reddit": N, "x": N}},
    "highlights": ["best action 1", "best action 2"]
  }},
  "results_summary": {{
    "total_engagement": N,
    "best_performing": "description",
    "worst_performing": "description",
    "avg_score": N
  }},
  "key_discoveries": ["discovery 1", "discovery 2"],
  "next_week_priorities": ["priority 1", "priority 2", "priority 3"],
  "hard_truth": "one uncomfortable insight"
}}"""

        response = await self.llm.generate(
            system_prompt="You are a growth analytics engine. Generate concise, data-driven weekly reports. Output ONLY valid JSON.",
            messages=[{"role": "user", "content": prompt}],
            tier=TaskTier.THINKING,
            max_tokens=1500,
        )

        try:
            raw = response.content
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            report = json.loads(raw.strip())
        except Exception:
            report = {"week": f"{week_start} ~ {week_end}", "raw": response.content[:1000]}

        report["generated_at"] = time.time()

        # 保存报告
        report_dir = Path(".crabres/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / f"weekly_{week_start}.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=str)
        )

        # 也保存到记忆
        if self.memory:
            await self.memory.save(f"weekly_report_{week_start}", report, category="execution")

        logger.info(f"Weekly report generated: {week_start}")
        return report

    async def _collect_week_data(self, start: str, end: str) -> dict:
        """收集本周所有数据"""
        # 日志
        journal_entries = []
        journal_dir = self.memory.base_dir / "journal"
        if journal_dir.exists():
            for path in journal_dir.glob("*.jsonl"):
                date = path.stem
                if start <= date <= end:
                    for line in path.read_text().splitlines():
                        try:
                            journal_entries.append(json.loads(line))
                        except Exception:
                            pass

        # Growth Log
        from app.agent.memory.growth_log import GrowthLog
        growth_log = GrowthLog(base_dir=str(self.memory.base_dir))
        all_actions = []
        all_results = []
        try:
            # 获取本周所有日期的数据
            current = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            while current <= end_dt:
                date_str = current.strftime("%Y-%m-%d")
                actions = await growth_log.get_actions(date_str)
                results = await growth_log.get_results(date_str)
                all_actions.extend(actions)
                all_results.extend(results)
                current += timedelta(days=1)
        except Exception:
            pass

        # Daemon 发现
        discoveries = []
        for entry in journal_entries:
            if entry.get("type") == "daemon_discovery":
                discoveries.append(entry.get("discovery", {}))

        # 反思
        reflections = []
        reflection_dir = Path(".crabres/reflections")
        if reflection_dir.exists():
            for path in reflection_dir.glob("*.json"):
                date = path.stem
                if start <= date <= end:
                    try:
                        reflections.append(json.loads(path.read_text()))
                    except Exception:
                        pass

        return {
            "total_entries": len(journal_entries),
            "action_count": len(all_actions),
            "result_count": len(all_results),
            "discovery_count": len(discoveries),
            "actions": all_actions,
            "results": all_results,
            "discoveries": discoveries,
            "reflections": reflections,
        }

    async def get_recent_reports(self, limit: int = 4) -> list[dict]:
        """获取最近的周报"""
        report_dir = Path(".crabres/reports")
        if not report_dir.exists():
            return []
        reports = []
        for path in sorted(report_dir.glob("weekly_*.json"), reverse=True)[:limit]:
            try:
                reports.append(json.loads(path.read_text()))
            except Exception:
                pass
        return reports
