"""
CrabRes 策略模拟器 — "如果我做 X，会怎样？"

让 13 位专家基于实时数据模拟不同策略的结果。
"""

import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from app.agent.engine.llm_adapter import AgentLLM, TaskTier
from app.agent.memory import GrowthMemory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/simulate", tags=["Strategy Simulator"])


class SimulationRequest(BaseModel):
    hypothesis: str  # "如果我下周在 Product Hunt 发布..."
    timeframe: str = "2 weeks"  # 模拟时间范围


@router.post("")
async def simulate_strategy(
    req: SimulationRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    策略模拟：让专家们预测如果执行某策略会怎样
    
    返回乐观/中性/悲观三种预测 + 综合建议
    """
    uid = current_user.get("user_id", 0)
    memory = GrowthMemory(base_dir=f".crabres/memory/{uid}")

    product = await memory.load("product") or {}
    strategy = await memory.load("growth_plan", category="strategy") or {}
    patterns = await memory.load("growth_patterns", category="strategy") or {}

    product_desc = product.get("raw_description", product.get("name", "Unknown product"))
    current_plan = strategy.get("content", "No plan yet")[:500]
    learned_patterns = patterns.get("patterns", "No patterns yet")[:300]

    llm = AgentLLM(budget_limit_usd=0.05)

    prompt = f"""You are a team of growth experts running a simulation.

PRODUCT: {product_desc}
CURRENT PLAN: {current_plan}
LEARNED PATTERNS: {learned_patterns}

HYPOTHESIS: "{req.hypothesis}"
TIMEFRAME: {req.timeframe}

Simulate three scenarios:

## 🟢 Optimistic (30% probability)
What happens if everything goes right? Specific numbers.

## 🟡 Realistic (50% probability)  
What's the most likely outcome? Specific numbers.

## 🔴 Pessimistic (20% probability)
What if things go wrong? What are the risks?

## 📊 Verdict
Should they do it? YES/NO/MAYBE with specific conditions.
What's the expected value?
What should they prepare before executing?

Be specific with numbers. Use the product context and learned patterns."""

    try:
        response = await llm.generate(
            system_prompt="You are 13 growth experts jointly simulating a strategy outcome. Be specific with numbers and timelines.",
            messages=[{"role": "user", "content": prompt}],
            tier=TaskTier.THINKING,
            max_tokens=2048,
        )

        return {
            "hypothesis": req.hypothesis,
            "timeframe": req.timeframe,
            "simulation": response.content,
            "cost_usd": llm.total_cost,
        }
    except Exception as e:
        return {
            "hypothesis": req.hypothesis,
            "error": str(e),
        }
