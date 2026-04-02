"""
CrabRes Creature API — 生物体真实数据驱动

属性 = 真实增长指标
情绪 = 基于增长状态自动变化
"""

import time
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.agent.memory import GrowthMemory

router = APIRouter(prefix="/creature", tags=["Creature"])


@router.get("/state")
async def get_creature_state(current_user: dict = Depends(get_current_user)):
    """获取生物体的真实状态（数据驱动）"""
    uid = current_user.get("user_id", 0)
    memory = GrowthMemory(base_dir=f".crabres/memory/{uid}")

    # 加载数据
    product = await memory.load("product") or {}
    execution = await memory.load("execution_stats", category="execution") or {}
    trust = await memory.load("trust_level", category="feedback") or {}
    plan = await memory.load("growth_plan", category="strategy") or {}

    # 计算真实属性
    total_users = execution.get("total_users", 0)
    growth_rate = execution.get("growth_rate", 0)
    streak = execution.get("streak_days", 0)
    sessions = trust.get("total_sessions", 0)
    first_use = trust.get("first_use_at", time.time())
    days_active = max(1, (time.time() - first_use) / 86400)

    # 属性计算（0-100）
    growth_score = min(100, growth_rate * 4)  # 25% 增长 = 100 分
    reach_score = min(100, total_users)       # 100 用户 = 100 分
    consistency_score = min(100, streak * 7)  # 14 天连胜 = 98 分
    insight_score = min(100, sessions * 5)    # 20 次会话 = 100 分
    momentum_score = min(100, int((growth_rate * 2 + streak * 3 + (1 if plan else 0) * 20)))

    # 情绪自动判断
    if growth_rate > 20:
        mood = "excited"
    elif growth_rate > 5:
        mood = "happy"
    elif streak > 7:
        mood = "working"
    elif days_active > 3 and sessions < 2:
        mood = "sad"  # 注册了但很少用
    elif total_users == 0 and days_active > 7:
        mood = "worried"  # 一周了还没用户
    elif days_active < 1:
        mood = "waving"  # 新用户
    else:
        mood = "idle"

    # 等级（基于总用户数）
    if total_users >= 10000:
        level = 50 + min(50, total_users // 1000)
    elif total_users >= 1000:
        level = 30 + (total_users - 1000) // 500
    elif total_users >= 100:
        level = 15 + (total_users - 100) // 60
    elif total_users >= 10:
        level = 5 + total_users // 10
    else:
        level = max(1, sessions)

    # 大小
    if total_users >= 10000:
        size = "grand"
    elif total_users >= 1000:
        size = "large"
    elif total_users >= 100:
        size = "medium"
    elif total_users >= 10:
        size = "small"
    else:
        size = "tiny"

    return {
        "mood": mood,
        "level": min(100, level),
        "size": size,
        "attributes": {
            "growth": growth_score,
            "reach": reach_score,
            "consistency": consistency_score,
            "insight": insight_score,
            "momentum": momentum_score,
        },
        "raw_data": {
            "total_users": total_users,
            "growth_rate": growth_rate,
            "streak_days": streak,
            "sessions": sessions,
            "days_active": round(days_active, 1),
        },
        "xp": sessions * 10 + streak * 5 + total_users,
        "xp_to_next": (level + 1) * 50,
    }
