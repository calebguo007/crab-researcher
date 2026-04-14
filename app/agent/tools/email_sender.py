"""
CrabRes Email Sender — Agent 能真正发邮件

支持两种模式：
1. SMTP 直发（自建邮箱）
2. Resend API（推荐，免费 100 封/天）

用于：
- 冷邮件外联（influencer/partner/press）
- 用户通知
- 周报推送
"""

import logging
import json
from typing import Any, Optional

import httpx

from app.agent.tools import BaseTool, ToolDefinition
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SendEmailTool(BaseTool):
    """真正发送邮件 — 不是写草稿，是真的发出去"""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="send_email",
            description="Actually send an email. Supports SMTP and Resend API. Use write_email to draft first, then this to send.",
            parameters={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Email body (plain text or HTML)"},
                    "reply_to": {"type": "string", "description": "Optional reply-to address"},
                    "is_html": {"type": "boolean", "description": "Whether body is HTML", "default": False},
                },
                "required": ["to", "subject", "body"],
            },
            concurrent_safe=True,
            requires_auth=True,
        )

    async def execute(self, to: str, subject: str, body: str,
                      reply_to: str = "", is_html: bool = False, **kwargs) -> Any:
        # 优先用 Resend API（更可靠，更好的送达率）
        resend_key = settings.RESEND_API_KEY
        if resend_key:
            return await self._send_via_resend(resend_key, to, subject, body, reply_to, is_html)

        # 备选：SMTP
        smtp_host = settings.SMTP_HOST
        smtp_user = settings.SMTP_USER
        smtp_pass = settings.SMTP_PASSWORD
        if smtp_host and smtp_user and smtp_pass:
            return await self._send_via_smtp(smtp_host, smtp_user, smtp_pass, to, subject, body, reply_to, is_html)

        return {
            "status": "no_credentials",
            "to": to, "subject": subject,
            "note": "Email not configured. Set RESEND_API_KEY (recommended) or SMTP_HOST/USER/PASSWORD in .env.",
            "body_preview": body[:200],
        }

    async def _send_via_resend(self, api_key: str, to: str, subject: str,
                                body: str, reply_to: str, is_html: bool) -> dict:
        """通过 Resend API 发送（推荐）"""
        try:
            from_addr = settings.EMAIL_FROM or "CrabRes <noreply@crabres.dev>"
            payload = {
                "from": from_addr,
                "to": [to],
                "subject": subject,
            }
            if is_html:
                payload["html"] = body
            else:
                payload["text"] = body
            if reply_to:
                payload["reply_to"] = reply_to

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    json=payload,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "status": "sent",
                    "platform": "email",
                    "provider": "resend",
                    "email_id": data.get("id", ""),
                    "to": to,
                    "subject": subject,
                }
        except Exception as e:
            logger.error(f"Resend send failed: {e}")
            return {"status": "failed", "error": str(e), "to": to, "subject": subject}

    async def _send_via_smtp(self, host: str, user: str, password: str,
                              to: str, subject: str, body: str,
                              reply_to: str, is_html: bool) -> dict:
        """通过 SMTP 发送"""
        import asyncio
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            loop = asyncio.get_event_loop()

            def _send():
                msg = MIMEMultipart("alternative")
                msg["From"] = settings.EMAIL_FROM or user
                msg["To"] = to
                msg["Subject"] = subject
                if reply_to:
                    msg["Reply-To"] = reply_to

                content_type = "html" if is_html else "plain"
                msg.attach(MIMEText(body, content_type, "utf-8"))

                port = settings.SMTP_PORT or 587
                with smtplib.SMTP(host, port) as server:
                    server.starttls()
                    server.login(user, password)
                    server.sendmail(user, [to], msg.as_string())

            await loop.run_in_executor(None, _send)
            return {
                "status": "sent",
                "platform": "email",
                "provider": "smtp",
                "to": to,
                "subject": subject,
            }
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return {"status": "failed", "error": str(e), "to": to, "subject": subject}


class BulkEmailTool(BaseTool):
    """批量发送邮件 — 用于冷邮件序列"""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="bulk_email",
            description="Send personalized emails to a list of recipients. Each email can be customized with {{name}} and {{company}} placeholders.",
            parameters={
                "type": "object",
                "properties": {
                    "recipients": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"},
                                "name": {"type": "string"},
                                "company": {"type": "string"},
                            },
                            "required": ["email"],
                        },
                        "description": "List of recipients",
                    },
                    "subject_template": {"type": "string", "description": "Subject with {{name}}/{{company}} placeholders"},
                    "body_template": {"type": "string", "description": "Body with {{name}}/{{company}} placeholders"},
                    "delay_seconds": {"type": "integer", "description": "Delay between emails (default 30)", "default": 30},
                },
                "required": ["recipients", "subject_template", "body_template"],
            },
            concurrent_safe=False,
            requires_auth=True,
        )

    async def execute(self, recipients: list, subject_template: str,
                      body_template: str, delay_seconds: int = 30, **kwargs) -> Any:
        import asyncio

        sender = SendEmailTool()
        results = []
        sent = 0
        failed = 0

        for i, recipient in enumerate(recipients[:50]):  # 每批最多 50 封
            email = recipient.get("email", "")
            name = recipient.get("name", "")
            company = recipient.get("company", "")

            if not email:
                continue

            subject = subject_template.replace("{{name}}", name).replace("{{company}}", company)
            body = body_template.replace("{{name}}", name).replace("{{company}}", company)

            result = await sender.execute(to=email, subject=subject, body=body)
            results.append(result)

            if result.get("status") == "sent":
                sent += 1
            else:
                failed += 1

            # 间隔发送，避免被标记为垃圾邮件
            if i < len(recipients) - 1:
                await asyncio.sleep(delay_seconds)

        return {
            "status": "completed",
            "total": len(recipients),
            "sent": sent,
            "failed": failed,
            "results": results,
        }
