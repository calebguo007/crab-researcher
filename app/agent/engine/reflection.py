"""
CrabRes Reflection Engine — Agent 的反思能力

缺失能力 #1：Agent 不会回顾自己做过的事并改进

这是区分"工具"和"Agent"的核心能力：
- 工具：你问它答，答完就忘
- Agent：它会回顾自己的输出质量，发现模式，主动改进

反思触发时机：
1. 每次 Daemon midnight tick（每日反思）
2. 用户给出负面反馈时（即时反思）
3. Action result 追踪到差结果时（执行反思）
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

REFLECTION_DIR = Path(".crabres/reflections")
REFLECTION_DIR.mkdir(parents=True, exist_ok=True)


class ReflectionEngine:
    """
    Agent 反思引擎

    三种反思模式：
    1. daily_reflection: 回顾今天所有对话，提取改进点
    2. execution_reflection: 回顾 action 结果，提取成功/失败模式
    3. feedback_reflection: 用户纠正时立即反思并记录
    """

    def __init__(self, memory=None, llm=None):
        self.memory = memory
        self.llm = llm

    async def daily_reflection(self) -> dict:
        """
        每日反思 — Daemon midnight 时触发

        回顾今天的所有对话和行动，提取：
        1. 我今天做得好的（保持）
        2. 我今天做得差的（改进）
        3. 我发现的新模式（学习）
        4. 明天应该做什么（计划）
        """
        if not self.memory or not self.llm:
            return {"error": "memory or llm not available"}

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # 收集今天的日志
        journal_path = self.memory.base_dir / "journal" / f"{today}.jsonl"
        journal_entries = []
        if journal_path.exists():
            for line in journal_path.read_text().splitlines():
                try:
                    journal_entries.append(json.loads(line))
                except Exception:
                    pass

        if not journal_entries:
            return {"date": today, "entries": 0, "reflection": "No activity today."}

        # 收集今天的 action 结果
        from app.agent.memory.growth_log import GrowthLog
        growth_log = GrowthLog(base_dir=str(self.memory.base_dir))
        today_actions = await growth_log.get_actions(today)
        today_results = await growth_log.get_results(today)

        # 收集已有的反思历史（避免重复）
        past_reflections = self._load_recent_reflections(3)

        from app.agent.engine.llm_adapter import TaskTier
        prompt = f"""You are CrabRes's self-reflection engine. Review today's activity and extract learnings.

## Today's Journal ({len(journal_entries)} entries)
{json.dumps(journal_entries[:20], ensure_ascii=False, default=str)[:3000]}

## Today's Growth Actions ({len(today_actions)} actions)
{json.dumps(today_actions[:10], ensure_ascii=False, default=str)[:1500]}

## Today's Results ({len(today_results)} tracked)
{json.dumps(today_results[:10], ensure_ascii=False, default=str)[:1500]}

## Past Reflections (don't repeat these)
{json.dumps(past_reflections[:3], ensure_ascii=False, default=str)[:1000]}

## Output Format (JSON only)
{{
  "date": "{today}",
  "what_went_well": ["specific thing 1", "specific thing 2"],
  "what_went_wrong": ["specific thing 1", "specific thing 2"],
  "patterns_discovered": ["pattern 1", "pattern 2"],
  "tomorrow_priorities": ["priority 1", "priority 2", "priority 3"],
  "self_improvement": ["how to improve response quality", "what to do differently"],
  "confidence_score": 0.0  // 0-1, how confident am I in today's advice quality
}}"""

        response = await self.llm.generate(
            system_prompt="You are a precise self-evaluation engine. Output ONLY valid JSON.",
            messages=[{"role": "user", "content": prompt}],
            tier=TaskTier.THINKING,
            max_tokens=1000,
        )

        try:
            raw = response.content
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            reflection = json.loads(raw.strip())
        except Exception:
            reflection = {
                "date": today,
                "raw": response.content[:500],
                "parse_error": True,
            }

        # 保存反思
        self._save_reflection(today, reflection)

        # 将改进点写入记忆（供下次对话使用）
        if reflection.get("self_improvement"):
            improvements = reflection["self_improvement"]
            await self.memory.save("self_improvements", {
                "improvements": improvements,
                "from_date": today,
                "updated_at": time.time(),
            }, category="feedback")

        logger.info(f"Daily reflection completed: {today}, confidence={reflection.get('confidence_score', 'N/A')}")
        return reflection

    async def execution_reflection(self, action_id: str, result: dict, platform: str) -> dict:
        """
        执行反思 — 当 action result 被追踪到时触发

        分析为什么这个 action 成功/失败，提取可复用模式
        """
        if not self.llm:
            return {}

        from app.agent.memory.growth_log import judge_result
        judgment = judge_result(platform, "post", result.get("metrics", {}))

        if judgment["verdict"] in ("great", "good"):
            # 成功 → 提取成功模式
            analysis_type = "success_pattern"
        else:
            # 失败 → 分析原因
            analysis_type = "failure_analysis"

        return {
            "action_id": action_id,
            "type": analysis_type,
            "verdict": judgment["verdict"],
            "score": judgment["score"],
            "signals": judgment["signals"],
            "timestamp": time.time(),
        }

    async def feedback_reflection(self, user_message: str, context: str = "") -> dict:
        """
        即时反思 — 用户给出负面反馈时触发

        检测负面反馈信号：
        - "不对"、"wrong"、"这不是我要的"
        - "太泛了"、"too generic"
        - "你没有理解"、"you misunderstood"
        """
        negative_signals = [
            "不对", "错了", "wrong", "不是我要的", "太泛", "too generic",
            "没有理解", "misunderstood", "没用", "useless", "不好",
            "重新", "redo", "再来", "try again", "不满意",
        ]

        is_negative = any(s in user_message.lower() for s in negative_signals)
        if not is_negative:
            return {"triggered": False}

        correction = {
            "triggered": True,
            "user_feedback": user_message[:200],
            "context": context[:200],
            "timestamp": time.time(),
            "type": "user_correction",
        }

        # 保存到反馈记忆
        if self.memory:
            corrections = await self.memory.load("corrections", category="feedback") or []
            if not isinstance(corrections, list):
                corrections = []
            corrections.append(correction)
            corrections = corrections[-50:]  # 只保留最近 50 条
            await self.memory.save("corrections", corrections, category="feedback")

        logger.info(f"Feedback reflection: user correction recorded")
        return correction

    def _save_reflection(self, date: str, reflection: dict):
        path = REFLECTION_DIR / f"{date}.json"
        with open(path, "w") as f:
            json.dump(reflection, f, indent=2, ensure_ascii=False, default=str)

    def _load_recent_reflections(self, days: int = 7) -> list[dict]:
        reflections = []
        for path in sorted(REFLECTION_DIR.glob("*.json"), reverse=True)[:days]:
            try:
                reflections.append(json.loads(path.read_text()))
            except Exception:
                pass
        return reflections

    def get_improvement_prompt(self) -> str:
        """生成可注入到 Coordinator prompt 的自我改进指令"""
        reflections = self._load_recent_reflections(3)
        if not reflections:
            return ""

        lines = ["## SELF-IMPROVEMENT NOTES (from recent reflections)"]
        for r in reflections:
            if r.get("self_improvement"):
                for imp in r["self_improvement"]:
                    lines.append(f"- {imp}")
            if r.get("what_went_wrong"):
                for w in r["what_went_wrong"]:
                    lines.append(f"- AVOID: {w}")
        lines.append("\nApply these improvements in this conversation.")
        return "\n".join(lines)
