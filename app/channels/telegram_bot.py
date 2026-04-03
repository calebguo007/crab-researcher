"""
Telegram Bot — CrabRes 增长 Agent 接入 Telegram

接入步骤：
1. Telegram 搜索 @BotFather → /newbot → 按提示创建
2. 复制 Token → 填入 .env TELEGRAM_BOT_TOKEN
3. 设置 Webhook:
   curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
     -d "url=https://crab-researcher.onrender.com/api/telegram/webhook"
4. 完成！用户直接私信 Bot 即可

用法：私信 Bot 或在群里 @Bot
"""

import asyncio
import logging
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["Telegram Bot"])

TELEGRAM_API = "https://api.telegram.org"


async def _call_agent(message: str, user_id: str) -> str:
    """调用 CrabRes Agent（同 Discord 的逻辑）"""
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

        memory = GrowthMemory(base_dir=f".crabres/memory/tg_{user_id}")
        loop = AgentLoop(
            session_id=f"tg-{user_id}",
            llm_service=llm, tool_registry=tools,
            expert_pool=experts, memory=memory,
        )

        outputs = []
        async for event in loop.run(message):
            if event.get("type") in ("message", "question"):
                outputs.append(event.get("content", ""))
            elif event.get("type") == "expert_thinking" and not event.get("content", "").endswith("is analyzing..."):
                expert_id = event.get("expert_id", "")
                outputs.append(f"*{expert_id}*: {event.get('content', '')[:500]}")

        return "\n\n".join(outputs) if outputs else "I'm thinking... please try again."

    except Exception as e:
        logger.error(f"Telegram agent call failed: {e}")
        return f"Something went wrong: {str(e)[:200]}"


async def _send_telegram_message(chat_id: str, text: str, reply_to: int = None):
    """发送 Telegram 消息"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    # Telegram 消息最大 4096 字符
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    async with httpx.AsyncClient() as client:
        for chunk in chunks:
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "Markdown",
            }
            if reply_to:
                payload["reply_to_message_id"] = reply_to
            await client.post(
                f"{TELEGRAM_API}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json=payload,
            )


async def _send_typing(chat_id: str):
    """发送"正在输入"状态"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/bot{settings.TELEGRAM_BOT_TOKEN}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"},
        )


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram Webhook 端点
    
    Telegram 会把所有消息 POST 到这个地址。
    设置 Webhook: POST https://api.telegram.org/bot{TOKEN}/setWebhook
                  body: {"url": "https://crab-researcher.onrender.com/api/telegram/webhook"}
    """
    body = await request.json()

    message = body.get("message") or body.get("edited_message")
    if not message:
        return JSONResponse({"ok": True})

    text = message.get("text", "").strip()
    chat_id = str(message.get("chat", {}).get("id", ""))
    user_id = str(message.get("from", {}).get("id", ""))
    message_id = message.get("message_id")
    chat_type = message.get("chat", {}).get("type", "private")

    if not text or not chat_id:
        return JSONResponse({"ok": True})

    # 群聊中需要 @bot 才响应
    if chat_type in ("group", "supergroup"):
        bot_username = settings.TELEGRAM_BOT_TOKEN.split(":")[0] if settings.TELEGRAM_BOT_TOKEN else ""
        if f"@" not in text:
            return JSONResponse({"ok": True})
        # 去掉 @bot_name
        text = text.replace(f"@CrabRes_bot", "").replace(f"@crabres_bot", "").strip()

    # /start 命令
    if text == "/start":
        await _send_telegram_message(
            chat_id,
            "🦀 *CrabRes — Your AI Growth Agent*\n\n"
            "Tell me about your product and I'll research your market, "
            "find competitors, and create a growth plan.\n\n"
            "Example: _I built an AI resume optimizer for job seekers_\n\n"
            "Just type your product description to get started!",
        )
        return JSONResponse({"ok": True})

    # /help 命令
    if text == "/help":
        await _send_telegram_message(
            chat_id,
            "🦀 *CrabRes Commands*\n\n"
            "Just describe your product to start a growth research.\n\n"
            "Tips:\n"
            "• Include your product URL for deeper analysis\n"
            "• Mention your budget for budget-appropriate strategies\n"
            "• Use `@expert_id` to DM a specific expert\n"
            "  e.g., `@economist What's a good CAC for SaaS?`\n\n"
            "13 experts are ready to help.",
        )
        return JSONResponse({"ok": True})

    # 发送"正在输入"状态
    await _send_typing(chat_id)

    # 异步处理（避免 Telegram 的 60 秒超时）
    asyncio.create_task(_handle_telegram_message(chat_id, text, user_id, message_id))

    return JSONResponse({"ok": True})


async def _handle_telegram_message(chat_id: str, text: str, user_id: str, reply_to: int):
    """异步处理 Telegram 消息"""
    try:
        result = await _call_agent(text, user_id)
        await _send_telegram_message(chat_id, result, reply_to=reply_to)
    except Exception as e:
        logger.error(f"Telegram handler failed: {e}")
        await _send_telegram_message(chat_id, f"⚠️ Error: {str(e)[:200]}")


@router.get("/health")
async def telegram_health():
    return {
        "status": "ok",
        "bot_configured": bool(settings.TELEGRAM_BOT_TOKEN),
    }


@router.post("/set-webhook")
async def set_webhook():
    """一键设置 Telegram Webhook（方便部署）"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}

    webhook_url = f"{settings.FRONTEND_URL.replace('vercel.app', 'onrender.com')}/api/telegram/webhook"
    # 用 Render URL
    webhook_url = "https://crab-researcher.onrender.com/api/telegram/webhook"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{TELEGRAM_API}/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook",
            json={"url": webhook_url},
        )
        return resp.json()
