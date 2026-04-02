"""
CrabRes Demo API — 免登录的快速市场扫描

Landing 页面用这个端点替代假的 setTimeout Demo。
用户输入产品描述，立刻看到真实的竞品名字 + 数据点。
不需要登录，但有速率限制（防滥用）。
"""

import asyncio
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.agent.tools.research import WebSearchTool, SocialSearchTool
from app.agent.engine.llm_adapter import AgentLLM, TaskTier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo", tags=["Demo"])

# 简易速率限制：每个 IP 每分钟最多 3 次
_rate_limit: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX = 3


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    if ip not in _rate_limit:
        _rate_limit[ip] = []
    _rate_limit[ip] = [t for t in _rate_limit[ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_limit[ip]) >= _RATE_LIMIT_MAX:
        return False
    _rate_limit[ip].append(now)
    return True


class QuickScanRequest(BaseModel):
    product_description: str = Field(..., min_length=3, max_length=500)


class QuickScanResult(BaseModel):
    product: str
    competitors: list[dict]
    social_mentions: list[dict]
    key_insight: str
    uncomfortable_truth: str


@router.post("/quick-scan", response_model=QuickScanResult)
async def quick_scan(req: QuickScanRequest, request: Request):
    """
    免登录的快速市场扫描。Landing 页面用这个。
    
    做两件事：
    1. web_search 找竞品
    2. social_search 找用户讨论
    
    然后用最便宜的 LLM 生成一句洞察 + 一句刺痛真话。
    总成本 < $0.001，耗时 < 15 秒。
    """
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")

    product = req.product_description.strip()

    # 并行执行搜索
    web_tool = WebSearchTool()
    social_tool = SocialSearchTool()

    try:
        web_result, social_result = await asyncio.gather(
            asyncio.wait_for(
                web_tool.execute(query=f"{product} competitors pricing alternatives 2026", num_results=5),
                timeout=15.0,
            ),
            asyncio.wait_for(
                social_tool.execute(query=product, platforms=["reddit", "hackernews"]),
                timeout=15.0,
            ),
            return_exceptions=True,
        )
    except Exception as e:
        logger.error(f"Demo scan failed: {e}")
        web_result = {"results": [], "answer": ""}
        social_result = {"results": []}

    # 安全提取
    if isinstance(web_result, Exception):
        web_result = {"results": [], "answer": ""}
    if isinstance(social_result, Exception):
        social_result = {"results": []}

    competitors = []
    for r in (web_result.get("results") or [])[:4]:
        competitors.append({
            "name": r.get("title", "")[:80],
            "url": r.get("url", ""),
            "snippet": r.get("content", "")[:150],
        })

    social_mentions = []
    for r in (social_result.get("results") or [])[:3]:
        social_mentions.append({
            "title": r.get("title", "")[:80],
            "platform": r.get("platform", ""),
            "url": r.get("url", ""),
        })

    # 用最便宜的 LLM 生成洞察
    key_insight = ""
    uncomfortable_truth = ""

    try:
        llm = AgentLLM(budget_limit_usd=0.01)
        search_context = web_result.get("answer", "")
        comp_names = ", ".join(c["name"][:40] for c in competitors[:3]) or "no competitors found"
        social_topics = "; ".join(s["title"][:50] for s in social_mentions[:3]) or "no discussions found"

        response = await llm.generate(
            system_prompt="You generate exactly 2 lines. Line 1: a specific insight with numbers. Line 2: an uncomfortable truth the user needs to hear. Be blunt. Use data from the search results.",
            messages=[{
                "role": "user",
                "content": f"Product: {product}\nCompetitors found: {comp_names}\nSearch summary: {search_context[:500]}\nSocial discussions: {social_topics}\n\nLine 1 (insight with specific data):\nLine 2 (uncomfortable truth):"
            }],
            tier=TaskTier.PARSING,
            max_tokens=200,
        )

        lines = [l.strip() for l in response.content.strip().split("\n") if l.strip()]
        if len(lines) >= 2:
            key_insight = lines[0].lstrip("12. :-").strip()
            uncomfortable_truth = lines[1].lstrip("12. :-").strip()
        elif len(lines) == 1:
            key_insight = lines[0].lstrip("12. :-").strip()
            uncomfortable_truth = "We need more data to identify risks. Sign up for a full analysis."
        else:
            key_insight = f"Found {len(competitors)} competitors and {len(social_mentions)} community discussions."
            uncomfortable_truth = "This market might be more crowded than you think."
    except Exception as e:
        logger.warning(f"Demo LLM insight failed: {e}")
        key_insight = f"Found {len(competitors)} competitors and {len(social_mentions)} community discussions."
        uncomfortable_truth = "Sign up for the full analysis with 13 expert perspectives."

    return QuickScanResult(
        product=product,
        competitors=competitors,
        social_mentions=social_mentions,
        key_insight=key_insight,
        uncomfortable_truth=uncomfortable_truth,
    )
