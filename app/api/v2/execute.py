"""
CrabRes 一键执行 — 帮用户尽可能减少执行摩擦

目前：生成内容 + 复制到剪贴板的链接 + 打开对应平台
未来：API 直接发布（需各平台 OAuth）
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.security import get_current_user

router = APIRouter(prefix="/execute", tags=["One-Click Execute"])


# 各平台的发帖/发布 URL 模板
PLATFORM_URLS = {
    "reddit": {
        "post": "https://www.reddit.com/{subreddit}/submit?selftext=true&title={title}",
        "comment": "https://www.reddit.com{thread_url}",
    },
    "x": {
        "post": "https://twitter.com/intent/tweet?text={text}",
    },
    "linkedin": {
        "post": "https://www.linkedin.com/feed/?shareActive=true",
    },
    "hackernews": {
        "post": "https://news.ycombinator.com/submitlink?u={url}&t={title}",
        "show": "https://news.ycombinator.com/submit",
    },
    "producthunt": {
        "post": "https://www.producthunt.com/posts/new",
    },
    "indiehackers": {
        "post": "https://www.indiehackers.com/post/new",
    },
}


class ExecuteAction(BaseModel):
    platform: str
    action_type: str = "post"  # post / comment / email
    content: str               # 要发布的内容
    title: Optional[str] = None
    subreddit: Optional[str] = None
    thread_url: Optional[str] = None
    url: Optional[str] = None
    recipient_email: Optional[str] = None


@router.post("/prepare")
async def prepare_execution(
    action: ExecuteAction,
    current_user: dict = Depends(get_current_user),
):
    """
    准备一键执行：返回内容 + 目标 URL
    
    前端用这个来：
    1. 把内容复制到剪贴板
    2. 打开对应平台的发帖页面
    """
    import urllib.parse

    platform = action.platform.lower()
    result = {
        "platform": platform,
        "content": action.content,
        "ready": True,
    }

    if platform == "reddit" and action.subreddit:
        title_encoded = urllib.parse.quote(action.title or "")
        result["url"] = f"https://www.reddit.com/r/{action.subreddit}/submit?selftext=true&title={title_encoded}"
        result["instructions"] = f"1. Click the link to open r/{action.subreddit}\n2. Paste the content\n3. Submit"

    elif platform == "x":
        # X/Twitter 有字数限制，截断到 280
        text = action.content[:270]
        result["url"] = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(text)}"
        result["instructions"] = "Tweet will be pre-filled. Just click 'Post'."

    elif platform == "linkedin":
        result["url"] = "https://www.linkedin.com/feed/?shareActive=true"
        result["instructions"] = "1. LinkedIn will open with share dialog\n2. Paste the content\n3. Post"

    elif platform == "hackernews":
        if action.url:
            result["url"] = f"https://news.ycombinator.com/submitlink?u={urllib.parse.quote(action.url)}&t={urllib.parse.quote(action.title or '')}"
        else:
            result["url"] = "https://news.ycombinator.com/submit"
        result["instructions"] = "1. HN submit page will open\n2. Add title and URL\n3. Submit"

    elif platform == "producthunt":
        result["url"] = "https://www.producthunt.com/posts/new"
        result["instructions"] = "1. PH new post page will open\n2. Fill in details\n3. Schedule or publish"

    elif platform == "email" and action.recipient_email:
        subject = urllib.parse.quote(action.title or "")
        body = urllib.parse.quote(action.content)
        result["url"] = f"mailto:{action.recipient_email}?subject={subject}&body={body}"
        result["instructions"] = "Email client will open with pre-filled subject and body."

    else:
        result["ready"] = False
        result["instructions"] = f"Platform '{platform}' execution not yet supported. Copy the content manually."

    return result
