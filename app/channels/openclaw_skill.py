"""
CrabRes as OpenClaw Skill — 让微信/飞书通过 OpenClaw 调用 CrabRes

OpenClaw 通过 HTTP 调用 Skill，格式类似 MCP 但有 OpenClaw 特有的字段。
微信用户: 微信 ClawBot → OpenClaw → CrabRes Skill → 返回增长建议
飞书用户: 飞书 OpenClaw Bot → CrabRes Skill → 返回增长建议

SKILL.md 文件放在仓库根目录，OpenClaw 会自动发现。
"""

import json
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.agent.tools.research import WebSearchTool, SocialSearchTool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/openclaw", tags=["OpenClaw Skill"])

_DAILY_OC_CALLS = 0
_DAILY_OC_RESET = 0


@router.post("/invoke")
async def openclaw_invoke(request: Request):
    """
    OpenClaw Skill 调用入口
    
    OpenClaw 发来的请求格式：
    {
        "skill": "crabres",
        "action": "analyze_growth",
        "input": { "product_description": "...", "budget": "..." },
        "context": { "user_id": "...", "channel": "wechat" }
    }
    """
    import time
    global _DAILY_OC_CALLS, _DAILY_OC_RESET
    now = int(time.time())
    if now - _DAILY_OC_RESET > 86400:
        _DAILY_OC_CALLS = 0
        _DAILY_OC_RESET = now
    _DAILY_OC_CALLS += 1
    if _DAILY_OC_CALLS > 200:
        return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    action = body.get("action", "analyze_growth")
    input_data = body.get("input", {})
    context = body.get("context", {})
    channel = context.get("channel", "unknown")

    logger.info(f"OpenClaw invoke: action={action}, channel={channel}")

    if action == "analyze_growth":
        result = await _analyze_growth(input_data)
    elif action == "find_competitors":
        result = await _find_competitors(input_data)
    elif action == "find_target_users":
        result = await _find_target_users(input_data)
    elif action == "quick_advice":
        result = await _quick_advice(input_data)
    else:
        result = {"error": f"Unknown action: {action}"}

    return JSONResponse({
        "skill": "crabres",
        "action": action,
        "output": result,
        "metadata": {
            "powered_by": "CrabRes — AI Growth Agent",
            "url": "https://crabres.com",
        },
    })


async def _analyze_growth(input_data: dict) -> dict:
    desc = input_data.get("product_description", "")
    budget = input_data.get("budget", "$0")

    searcher = WebSearchTool()
    social = SocialSearchTool()

    search_results = await searcher.execute(query=f"{desc} competitors alternatives", num_results=3)
    social_results = await social.execute(query=desc, platforms=["reddit", "hackernews"])

    output = f"## Growth Analysis\n\n**Product:** {desc}\n**Budget:** {budget}\n\n"

    if search_results.get("answer"):
        output += f"### Market Overview\n{search_results['answer']}\n\n"

    output += "### Competitors Found\n"
    for r in search_results.get("results", [])[:3]:
        output += f"- {r['title']}: {r.get('url', '')}\n"

    output += "\n### Where Your Users Are\n"
    for r in social_results.get("results", [])[:3]:
        output += f"- [{r.get('platform', '')}] {r['title']}\n"

    output += f"\n---\nFor a complete growth plan with written content: https://crabres.com"
    return {"text": output, "format": "markdown"}


async def _find_competitors(input_data: dict) -> dict:
    query = input_data.get("product_or_niche", "")
    searcher = WebSearchTool()
    results = await searcher.execute(query=f"{query} competitors alternatives 2026", num_results=5)

    output = f"## Competitors for: {query}\n\n"
    if results.get("answer"):
        output += f"{results['answer']}\n\n"
    for r in results.get("results", []):
        output += f"- **{r['title']}**: {r.get('content', '')[:100]}\n"

    return {"text": output, "format": "markdown"}


async def _find_target_users(input_data: dict) -> dict:
    desc = input_data.get("product_description", "")
    social = SocialSearchTool()
    results = await social.execute(query=desc, platforms=["reddit", "hackernews", "producthunt"])

    output = f"## Target Users for: {desc}\n\n"
    for r in results.get("results", []):
        output += f"- [{r.get('platform', '')}] {r['title']}: {r.get('url', '')}\n"

    return {"text": output, "format": "markdown"}


async def _quick_advice(input_data: dict) -> dict:
    """快速建议——不搜索，直接基于常识给出方向"""
    desc = input_data.get("product_description", "")
    return {
        "text": f"For '{desc}', I recommend:\n1. Search for competitors first\n2. Find where your users discuss this problem\n3. Get a full growth plan at https://crabres.com",
        "format": "markdown",
    }
