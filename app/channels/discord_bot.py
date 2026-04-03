"""
Discord Bot — CrabRes 增长 Agent 接入 Discord

接入步骤：
1. https://discord.com/developers/applications → New Application
2. 左侧 Bot → Add Bot → Copy Token → 填入 .env DISCORD_BOT_TOKEN
3. Bot 页面开启 MESSAGE CONTENT INTENT
4. OAuth2 → URL Generator → 勾选 bot + applications.commands
5. Bot Permissions: Send Messages, Read Message History, Embed Links, View Channels
6. 用生成的链接邀请 Bot 到你的 Server
7. 部署后 Bot 自动上线

用法：在 Discord 中 @CrabRes 或私信 Bot
"""

import asyncio
import logging
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/discord", tags=["Discord Bot"])

DISCORD_API = "https://discord.com/api/v10"


async def _call_agent(message: str, user_id: str) -> str:
    """调用 CrabRes Agent API"""
    try:
        from app.agent.engine.llm_adapter import AgentLLM
        from app.agent.engine.loop import AgentLoop
        from app.agent.tools import ToolRegistry
        from app.agent.tools.research import WebSearchTool, ScrapeWebsiteTool, SocialSearchTool
        from app.agent.experts import ExpertPool
        from app.agent.experts.market_researcher import MarketResearcher
        from app.agent.experts.economist import Economist
        from app.agent.experts.psychologist import ConsumerPsychologist
        from app.agent.experts.social_media import SocialMediaExpert
        from app.agent.experts.copywriter import MasterCopywriter
        from app.agent.experts.critic import StrategyCritic
        from app.agent.memory import GrowthMemory

        llm = AgentLLM(budget_limit_usd=0.5)
        tools = ToolRegistry()
        tools.register(WebSearchTool())
        tools.register(ScrapeWebsiteTool())
        tools.register(SocialSearchTool())

        experts = ExpertPool()
        for e in [MarketResearcher(), Economist(), ConsumerPsychologist(),
                  SocialMediaExpert(), MasterCopywriter(), StrategyCritic()]:
            experts.register(e)
        experts.set_llm(llm)

        memory = GrowthMemory(base_dir=f".crabres/memory/discord_{user_id}")
        loop = AgentLoop(
            session_id=f"discord-{user_id}",
            llm_service=llm, tool_registry=tools,
            expert_pool=experts, memory=memory,
        )

        outputs = []
        async for event in loop.run(message):
            if event.get("type") in ("message", "question"):
                outputs.append(event.get("content", ""))
            elif event.get("type") == "expert_thinking" and not event.get("content", "").endswith("is analyzing..."):
                expert_id = event.get("expert_id", "")
                outputs.append(f"**{expert_id}**: {event.get('content', '')[:500]}")

        return "\n\n".join(outputs) if outputs else "I'm thinking... please try again in a moment."

    except Exception as e:
        logger.error(f"Discord agent call failed: {e}")
        return f"Something went wrong: {str(e)[:200]}"


async def _send_discord_message(channel_id: str, content: str):
    """发送消息到 Discord 频道"""
    if not settings.DISCORD_BOT_TOKEN:
        return
    # Discord 消息最大 2000 字符
    chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
    async with httpx.AsyncClient() as client:
        for chunk in chunks:
            await client.post(
                f"{DISCORD_API}/channels/{channel_id}/messages",
                headers={"Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"},
                json={"content": chunk},
            )


@router.post("/webhook")
async def discord_webhook(request: Request):
    """
    Discord Interactions Endpoint
    
    配置步骤：在 Discord Developer Portal → General → Interactions Endpoint URL 填入：
    https://crab-researcher.onrender.com/api/discord/webhook
    """
    body = await request.json()

    # Discord 验证 ping
    if body.get("type") == 1:
        return JSONResponse({"type": 1})

    # 处理消息（Interaction）
    if body.get("type") == 2:  # APPLICATION_COMMAND
        data = body.get("data", {})
        options = data.get("options", [])
        message = options[0].get("value", "") if options else ""
        user = body.get("member", {}).get("user", {}) or body.get("user", {})
        user_id = user.get("id", "unknown")

        if not message:
            return JSONResponse({
                "type": 4,
                "data": {"content": "Please provide a message. Example: `/crabres I built an AI resume tool`"}
            })

        # 先回复"正在研究..."（避免 3 秒超时）
        # 然后异步处理
        asyncio.create_task(_handle_discord_interaction(body, message, user_id))

        return JSONResponse({
            "type": 5,  # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        })

    return JSONResponse({"status": "ok"})


async def _handle_discord_interaction(body: dict, message: str, user_id: str):
    """异步处理 Discord 交互"""
    token = body.get("token", "")
    app_id = body.get("application_id", "")

    result = await _call_agent(message, user_id)

    # 编辑原始回复
    chunks = [result[i:i+1900] for i in range(0, len(result), 1900)]
    async with httpx.AsyncClient() as client:
        # 编辑 deferred response
        await client.patch(
            f"{DISCORD_API}/webhooks/{app_id}/{token}/messages/@original",
            json={"content": chunks[0] if chunks else "No response generated."},
        )
        # 如果有多个 chunk，发送 follow-up
        for chunk in chunks[1:]:
            await client.post(
                f"{DISCORD_API}/webhooks/{app_id}/{token}",
                json={"content": chunk},
            )


@router.get("/health")
async def discord_health():
    return {
        "status": "ok",
        "bot_configured": bool(settings.DISCORD_BOT_TOKEN),
    }
