#!/usr/bin/env python3
"""
CrabRes Growth Loop — 终端交互闭环

用法：python3 growth_loop.py

三步闭环：
1. 今日行动 — 记录你做了什么
2. 今日结果 — 记录结果（手动填）
3. 明日策略 — AI 基于数据生成下一步

这是 Demo 阶段的核心测试工具。
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.memory.growth_log import GrowthLog, judge_result, CHANNEL_BENCHMARKS

# 默认用户目录
USER_DIR = ".crabres/memory/1"
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "blue": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "orange": "\033[38;5;208m",
    "purple": "\033[35m",
}
C = COLORS


def cprint(color: str, text: str):
    print(f"{C.get(color, '')}{text}{C['reset']}")


def header():
    cprint("orange", """
╔══════════════════════════════════════════╗
║   🦀 CrabRes Growth Loop                ║
║   今日行动 → 今日结果 → 明日策略         ║
╚══════════════════════════════════════════╝
""")


def show_menu():
    print(f"""
{C['bold']}Commands:{C['reset']}
  {C['blue']}1{C['reset']}  📝 Log today's action (记录今日行动)
  {C['blue']}2{C['reset']}  📊 Log result (记录结果)
  {C['blue']}3{C['reset']}  🎯 Generate tomorrow's strategy (生成明日策略)
  {C['blue']}4{C['reset']}  📋 View today's log (查看今日日志)
  {C['blue']}5{C['reset']}  📈 View growth state (查看增长状态)
  {C['blue']}6{C['reset']}  📜 View all history (查看全部历史)
  {C['blue']}q{C['reset']}  Exit
""")


async def log_action(gl: GrowthLog):
    cprint("bold", "\n── 记录今日行动 ──\n")

    platforms = ["reddit", "x", "xiaohongshu", "linkedin", "email", "other"]
    print("Platform:", " / ".join(f"{i+1}.{p}" for i, p in enumerate(platforms)))
    p_idx = input("Choose (1-6): ").strip()
    platform = platforms[int(p_idx) - 1] if p_idx.isdigit() and 1 <= int(p_idx) <= 6 else "other"

    action_types = ["post", "reply", "dm", "email", "thread", "outreach", "other"]
    print("Action type:", " / ".join(f"{i+1}.{a}" for i, a in enumerate(action_types)))
    a_idx = input("Choose (1-7): ").strip()
    action_type = action_types[int(a_idx) - 1] if a_idx.isdigit() and 1 <= int(a_idx) <= 7 else "other"

    description = input("What did you do? (一句话描述): ").strip()
    target = input("Target (e.g., r/SaaS, @user): ").strip()
    url = input("URL (if published, or leave empty): ").strip()
    time_str = input("Time spent (minutes): ").strip()
    time_min = int(time_str) if time_str.isdigit() else 0

    entry = await gl.log_action(
        platform=platform, action_type=action_type,
        description=description, url=url, target=target,
        time_spent_min=time_min,
    )
    cprint("green", f"\n✅ Action logged: {entry.id}")
    cprint("dim", f"   {platform}/{action_type} → {description}")


async def log_result(gl: GrowthLog):
    cprint("bold", "\n── 记录结果 ──\n")

    # 显示今日未记录结果的 actions
    today = datetime.now().strftime("%Y-%m-%d")
    actions = await gl.get_actions(today)
    results = await gl.get_results(today)
    logged_ids = {r.get("action_id") for r in results}

    pending = [a for a in actions if a.get("id") not in logged_ids]

    if not pending:
        # 也显示往日的
        all_actions = await gl.get_actions()
        all_results = await gl.get_results()
        all_logged = {r.get("action_id") for r in all_results}
        pending = [a for a in all_actions if a.get("id") not in all_logged]

    if not pending:
        cprint("yellow", "No pending actions to log results for. Log an action first.")
        return

    print("Pending actions:")
    for i, a in enumerate(pending):
        print(f"  {C['blue']}{i+1}{C['reset']}. [{a.get('platform')}/{a.get('action_type')}] {a.get('description', '')[:60]}")

    idx = input("\nChoose action (number): ").strip()
    if not idx.isdigit() or int(idx) < 1 or int(idx) > len(pending):
        cprint("red", "Invalid choice")
        return

    action = pending[int(idx) - 1]
    action_id = action.get("id", "")
    platform = action.get("platform", "")

    print(f"\nLogging result for: {action.get('description', '')}")

    # 根据平台提示输入 metrics
    metrics = {}
    if platform == "reddit":
        v = input("Upvotes: ").strip()
        if v.isdigit(): metrics["upvotes"] = int(v)
        v = input("Comments: ").strip()
        if v.isdigit(): metrics["comments"] = int(v)
    elif platform == "x":
        v = input("Likes: ").strip()
        if v.isdigit(): metrics["likes"] = int(v)
        v = input("Replies: ").strip()
        if v.isdigit(): metrics["replies"] = int(v)
        v = input("Impressions: ").strip()
        if v.isdigit(): metrics["impressions"] = int(v)
    elif platform == "xiaohongshu":
        v = input("点赞: ").strip()
        if v.isdigit(): metrics["likes"] = int(v)
        v = input("收藏: ").strip()
        if v.isdigit(): metrics["collects"] = int(v)
        v = input("评论: ").strip()
        if v.isdigit(): metrics["comments"] = int(v)
    elif platform == "email":
        v = input("Replies received: ").strip()
        if v.isdigit(): metrics["replies"] = int(v)
        v = input("Total sent: ").strip()
        if v.isdigit(): metrics["sent"] = int(v)
    else:
        v = input("Total engagement (any number): ").strip()
        if v.isdigit(): metrics["engagement"] = int(v)

    notes = input("Notes (optional): ").strip()

    entry = await gl.log_result(action_id=action_id, metrics=metrics, notes=notes)

    # 显示判定
    verdict_colors = {"great": "green", "good": "blue", "mediocre": "yellow", "poor": "red"}
    verdict_emoji = {"great": "🔥", "good": "✅", "mediocre": "😐", "poor": "❌"}
    v = entry.verdict
    cprint(verdict_colors.get(v, "dim"),
           f"\n{verdict_emoji.get(v, '?')} Result: {v.upper()} (score: {entry.score}/100)")
    cprint("dim", f"   {entry.notes}")


async def generate_strategy(gl: GrowthLog):
    cprint("bold", "\n── 生成明日策略 ──\n")

    state = await gl.compute_state()
    today_actions = await gl.get_today_actions()
    today_results = await gl.get_results(datetime.now().strftime("%Y-%m-%d"))

    # 基于数据生成策略（当前用规则引擎，未来接 LLM）
    tomorrow_actions = []
    reasoning_parts = []

    if state.total_actions == 0:
        tomorrow_actions = [
            "📱 Post 1 value-first content on your primary channel",
            "💬 Reply to 5 relevant discussions where your users hang out",
            "🔍 Research 3 competitor recent posts for inspiration",
        ]
        reasoning_parts.append("No history yet. Starting with basics: create→engage→research.")
    else:
        # 基于渠道权重分配
        if state.best_channel:
            tomorrow_actions.append(f"📱 Double down on {state.best_channel} — your best performing channel (weight: {state.channel_weights.get(state.best_channel, 0):.0%})")
            reasoning_parts.append(f"Best channel is {state.best_channel}")

        if state.worst_channel and state.worst_channel != state.best_channel:
            worst_weight = state.channel_weights.get(state.worst_channel, 0)
            if worst_weight < 0.2:
                tomorrow_actions.append(f"❌ Consider dropping {state.worst_channel} — underperforming (weight: {worst_weight:.0%})")
                reasoning_parts.append(f"Worst channel {state.worst_channel} below 20% weight")
            else:
                tomorrow_actions.append(f"🔄 Try a different approach on {state.worst_channel}")

        # 分析今日结果
        great_count = sum(1 for r in today_results if r.get("verdict") == "great")
        poor_count = sum(1 for r in today_results if r.get("verdict") == "poor")

        if great_count > 0:
            tomorrow_actions.append(f"🔥 Replicate today's {great_count} successful action(s) — same format, same timing")
            reasoning_parts.append(f"{great_count} great results today")

        if poor_count > 0:
            tomorrow_actions.append(f"⚠️ Analyze why {poor_count} action(s) underperformed — change angle or timing")
            reasoning_parts.append(f"{poor_count} poor results need attention")

        # 如果连胜中
        if state.streak_days >= 3:
            tomorrow_actions.append(f"🔥 {state.streak_days}-day streak! Keep momentum. Don't skip tomorrow.")

        # 默认添加
        if len(tomorrow_actions) < 3:
            tomorrow_actions.append("💬 Reply to 5 relevant discussions (build authority)")
        if len(tomorrow_actions) < 3:
            tomorrow_actions.append("🔍 Check competitor latest posts for new angles")

    reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Starting fresh"

    entry = await gl.log_strategy(
        actions=tomorrow_actions,
        reasoning=reasoning,
        based_on=[f"state.avg_score={state.avg_score}", f"state.streak={state.streak_days}"],
    )

    cprint("purple", "🎯 Tomorrow's Strategy:\n")
    for i, a in enumerate(tomorrow_actions):
        print(f"  {i+1}. {a}")
    print()
    cprint("dim", f"Reasoning: {reasoning}")
    cprint("dim", f"Based on: {state.total_actions} actions, {state.total_results} results, avg score {state.avg_score}")


async def view_today(gl: GrowthLog):
    cprint("bold", "\n── 今日日志 ──\n")
    today = datetime.now().strftime("%Y-%m-%d")

    actions = await gl.get_actions(today)
    results = await gl.get_results(today)
    result_map = {r.get("action_id"): r for r in results}

    if not actions:
        cprint("dim", "No actions logged today. Start with command 1.")
        return

    for a in actions:
        aid = a.get("id", "")
        r = result_map.get(aid)
        status = ""
        if r:
            v = r.get("verdict", "")
            emoji = {"great": "🔥", "good": "✅", "mediocre": "😐", "poor": "❌"}.get(v, "?")
            status = f" → {emoji} {v} (score: {r.get('score', 0)})"
        else:
            status = f" → {C['yellow']}⏳ awaiting result{C['reset']}"

        platform = a.get("platform", "?")
        desc = a.get("description", "")[:60]
        print(f"  [{C['blue']}{platform}{C['reset']}] {desc}{status}")

    # 策略
    strategy = await gl.get_latest_strategy()
    if strategy and strategy.get("date") == today:
        cprint("purple", "\n🎯 Today's Strategy:")
        for s in strategy.get("actions", []):
            print(f"  • {s}")


async def view_state(gl: GrowthLog):
    cprint("bold", "\n── 增长状态 ──\n")
    state = await gl.compute_state()

    print(f"  Total actions:  {C['bold']}{state.total_actions}{C['reset']}")
    print(f"  Results tracked: {state.total_results}")
    print(f"  Average score:  {C['bold']}{state.avg_score}/100{C['reset']}")
    print(f"  Streak:         {C['orange']}{state.streak_days} days{C['reset']}")

    if state.channel_weights:
        print(f"\n  Channel performance:")
        for ch, w in sorted(state.channel_weights.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(w * 20) + "░" * (20 - int(w * 20))
            marker = " 🏆" if ch == state.best_channel else ""
            print(f"    {ch:15s} {bar} {w:.0%}{marker}")

    if state.best_channel:
        cprint("green", f"\n  Best: {state.best_channel}")
    if state.worst_channel and state.worst_channel != state.best_channel:
        cprint("red", f"  Worst: {state.worst_channel}")


async def view_history(gl: GrowthLog):
    cprint("bold", "\n── 全部历史 ──\n")
    actions = await gl.get_actions()
    results = await gl.get_results()
    result_map = {r.get("action_id"): r for r in results}

    if not actions:
        cprint("dim", "No history yet.")
        return

    current_date = ""
    for a in sorted(actions, key=lambda x: x.get("date", "")):
        d = a.get("date", "")
        if d != current_date:
            current_date = d
            print(f"\n  {C['bold']}── {d} ──{C['reset']}")

        r = result_map.get(a.get("id"))
        v_str = ""
        if r:
            v = r.get("verdict", "")
            emoji = {"great": "🔥", "good": "✅", "mediocre": "😐", "poor": "❌"}.get(v, "?")
            v_str = f" → {emoji} {r.get('score', 0)}/100"
        else:
            v_str = f" → ⏳"

        print(f"    [{a.get('platform','?'):12s}] {a.get('description','')[:50]}{v_str}")


async def main():
    header()
    gl = GrowthLog(base_dir=USER_DIR)

    while True:
        show_menu()
        cmd = input(f"{C['orange']}crabres>{C['reset']} ").strip().lower()

        if cmd in ("q", "quit", "exit"):
            cprint("dim", "Bye! Keep growing 🦀")
            break
        elif cmd == "1":
            await log_action(gl)
        elif cmd == "2":
            await log_result(gl)
        elif cmd == "3":
            await generate_strategy(gl)
        elif cmd == "4":
            await view_today(gl)
        elif cmd == "5":
            await view_state(gl)
        elif cmd == "6":
            await view_history(gl)
        else:
            cprint("yellow", "Unknown command. Try 1-6 or q.")


if __name__ == "__main__":
    asyncio.run(main())
