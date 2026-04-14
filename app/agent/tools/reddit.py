"""
CrabRes Reddit API 集成 — Agent 能真正在 Reddit 发帖和评论

使用 Reddit OAuth2 Script 模式：
- 读取：搜索帖子、获取子版块热帖
- 写入：发帖、评论（需要 Script App 授权）

Reddit API 文档：https://www.reddit.com/dev/api/
"""

import logging
import time
from typing import Any, Optional

import httpx

from app.agent.tools import BaseTool, ToolDefinition
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

REDDIT_AUTH_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_API_BASE = "https://oauth.reddit.com"
USER_AGENT = "CrabRes/2.0 (by /u/crabres_bot)"


class RedditAuth:
    """Reddit OAuth2 认证管理"""

    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    async def get_token(self) -> Optional[str]:
        client_id = settings.REDDIT_CLIENT_ID
        client_secret = settings.REDDIT_CLIENT_SECRET
        username = settings.REDDIT_USERNAME
        password = settings.REDDIT_PASSWORD

        if not all([client_id, client_secret, username, password]):
            return None

        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    REDDIT_AUTH_URL,
                    auth=(client_id, client_secret),
                    data={
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    },
                    headers={"User-Agent": USER_AGENT},
                )
                resp.raise_for_status()
                data = resp.json()
                self._access_token = data["access_token"]
                self._token_expires_at = time.time() + data.get("expires_in", 3600)
                logger.info("Reddit OAuth token acquired")
                return self._access_token
        except Exception as e:
            logger.error(f"Reddit auth failed: {e}")
            return None


_reddit_auth = RedditAuth()


class RedditPostTool(BaseTool):
    """在 Reddit 真正发帖"""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reddit_post",
            description="Actually submit a post to a Reddit subreddit. This POSTS it live.",
            parameters={
                "type": "object",
                "properties": {
                    "subreddit": {"type": "string", "description": "Subreddit name without r/ (e.g., 'SideProject')"},
                    "title": {"type": "string", "description": "Post title (max 300 chars)"},
                    "text": {"type": "string", "description": "Post body (markdown)"},
                    "flair_text": {"type": "string", "description": "Optional flair"},
                },
                "required": ["subreddit", "title", "text"],
            },
            concurrent_safe=False,
            requires_auth=True,
        )

    async def execute(self, subreddit: str, title: str, text: str, flair_text: str = "", **kwargs) -> Any:
        token = await _reddit_auth.get_token()
        if not token:
            return {
                "status": "no_credentials",
                "subreddit": subreddit, "title": title, "text": text,
                "note": "Reddit API not configured. Set REDDIT_CLIENT_ID/SECRET/USERNAME/PASSWORD in .env.",
            }

        if len(title) > 300:
            return {"error": f"Title too long: {len(title)} chars (max 300)"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                data = {
                    "sr": subreddit, "kind": "self",
                    "title": title, "text": text,
                    "resubmit": True, "send_replies": True,
                }
                if flair_text:
                    data["flair_text"] = flair_text

                resp = await client.post(
                    f"{REDDIT_API_BASE}/api/submit",
                    data=data,
                    headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
                )
                resp.raise_for_status()
                result = resp.json()

                post_data = result.get("json", {}).get("data", {})
                errors = result.get("json", {}).get("errors", [])
                if errors:
                    return {"status": "failed", "errors": errors, "title": title}

                return {
                    "status": "posted",
                    "platform": "reddit",
                    "subreddit": subreddit,
                    "post_id": post_data.get("id", ""),
                    "url": post_data.get("url", ""),
                    "title": title,
                }
        except Exception as e:
            logger.error(f"Reddit post failed: {e}")
            return {"status": "failed", "error": str(e), "title": title}


class RedditCommentTool(BaseTool):
    """在 Reddit 帖子下真正发评论"""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reddit_comment",
            description="Post a comment on a Reddit thread.",
            parameters={
                "type": "object",
                "properties": {
                    "thing_id": {"type": "string", "description": "Reddit fullname (t3_xxx for post, t1_xxx for comment)"},
                    "text": {"type": "string", "description": "Comment text (markdown)"},
                },
                "required": ["thing_id", "text"],
            },
            concurrent_safe=False,
            requires_auth=True,
        )

    async def execute(self, thing_id: str, text: str, **kwargs) -> Any:
        token = await _reddit_auth.get_token()
        if not token:
            return {"status": "no_credentials", "thing_id": thing_id, "text": text}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{REDDIT_API_BASE}/api/comment",
                    data={"thing_id": thing_id, "text": text},
                    headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
                )
                resp.raise_for_status()
                result = resp.json()
                things = result.get("json", {}).get("data", {}).get("things", [])
                comment_id = things[0].get("data", {}).get("id", "") if things else ""
                return {"status": "posted", "platform": "reddit", "comment_id": comment_id, "parent": thing_id}
        except Exception as e:
            logger.error(f"Reddit comment failed: {e}")
            return {"status": "failed", "error": str(e)}


class RedditSearchTool(BaseTool):
    """搜索 Reddit 帖子 — 找相关讨论"""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reddit_search",
            description="Search Reddit for relevant discussions. Works without auth.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "subreddit": {"type": "string", "description": "Optional: limit to subreddit"},
                    "sort": {"type": "string", "enum": ["relevance", "hot", "new", "top"]},
                    "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"]},
                    "limit": {"type": "integer", "description": "Max results (1-25)"},
                },
                "required": ["query"],
            },
            concurrent_safe=True,
        )

    async def execute(self, query: str, subreddit: str = "", sort: str = "relevance",
                      time_filter: str = "week", limit: int = 10, **kwargs) -> Any:
        token = await _reddit_auth.get_token()
        headers = {"User-Agent": USER_AGENT}
        base_url = "https://www.reddit.com"
        if token:
            headers["Authorization"] = f"Bearer {token}"
            base_url = REDDIT_API_BASE

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {"q": query, "sort": sort, "t": time_filter,
                          "limit": min(max(limit, 1), 25), "type": "link"}
                if subreddit:
                    params["restrict_sr"] = True
                    url = f"{base_url}/r/{subreddit}/search.json"
                else:
                    url = f"{base_url}/search.json"

                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                posts = []
                for child in data.get("data", {}).get("children", []):
                    p = child.get("data", {})
                    posts.append({
                        "id": p.get("id", ""),
                        "fullname": p.get("name", ""),
                        "title": p.get("title", ""),
                        "subreddit": p.get("subreddit", ""),
                        "author": p.get("author", ""),
                        "score": p.get("score", 0),
                        "num_comments": p.get("num_comments", 0),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "selftext": (p.get("selftext", "") or "")[:300],
                        "created_utc": p.get("created_utc", 0),
                    })
                return {"query": query, "count": len(posts), "posts": posts}
        except Exception as e:
            logger.error(f"Reddit search failed: {e}")
            return {"error": str(e), "query": query, "posts": []}
