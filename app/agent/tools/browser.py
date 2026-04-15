"""
CrabRes Browser Tool — Agent 的眼睛

让 Agent 能"看到"网页：
- 截图 + 多模态 LLM 理解（分析竞品落地页、提取视觉信息）
- JS 渲染后的内容提取（SPA/动态页面）
- 页面元数据（title, meta, OG tags）
- 移动端截图（检查响应式）

比 httpx 抓取强在：能处理 JS 渲染、能截图、能用 LLM "看"页面。
"""

import asyncio
import base64
import logging
from typing import Any, Optional
from pathlib import Path

from app.agent.tools import BaseTool, ToolDefinition

logger = logging.getLogger(__name__)

# 浏览器引擎：优先 Patchright（反检测），降级 Playwright
_playwright = None
_browser = None
_engine_name = "none"


async def _get_browser(auto_install: bool = True):
    """延迟初始化浏览器（按需启动）
    
    Render 免费版只有 512MB 内存，不能常驻 Chromium。
    策略：首次调用时检查 Chromium，未安装则自动安装，用完后调 _release_browser 释放。
    """
    global _playwright, _browser, _engine_name
    if _browser:
        return _browser

    try:
        from patchright.async_api import async_playwright
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
                  '--single-process', '--no-zygote'],
        )
        _engine_name = "patchright"
        logger.info("Browser initialized with Patchright (anti-detection)")
        return _browser
    except Exception as e:
        # Chromium 未安装 — 尝试自动安装（但限时 60s，超时直接降级）
        if auto_install and "executable doesn't exist" in str(e).lower():
            logger.info("Chromium not found, attempting quick install (60s limit)...")
            try:
                import subprocess
                proc = subprocess.run(
                    ['python3', '-m', 'patchright', 'install', 'chromium'],
                    check=True, timeout=60,
                    capture_output=True, text=True,
                )
                logger.info(f"Chromium installed: {proc.stdout[-200:] if proc.stdout else 'ok'}")
                return await _get_browser(auto_install=False)
            except subprocess.TimeoutExpired:
                logger.warning("Chromium install timed out (60s) — falling back to httpx")
                return None
            except Exception as install_err:
                logger.warning(f"Auto-install Chromium failed: {install_err}")
                return None
        logger.warning(f"No browser engine available (patchright failed: {e})")
        return None


async def _release_browser():
    """释放浏览器进程，回收内存（Render 512MB 限制）"""
    global _playwright, _browser, _engine_name
    try:
        if _browser:
            await _browser.close()
        if _playwright:
            await _playwright.stop()
    except Exception as e:
        logger.warning(f"Browser release error: {e}")
    finally:
        _browser = None
        _playwright = None
        _engine_name = "none"
        logger.info("Browser released to free memory")


class BrowseWebsiteTool(BaseTool):
    """
    浏览网页——截图 + JS 渲染内容提取
    
    比 scrape_website（httpx）强在：
    - 能处理 SPA/JS 渲染页面
    - 能截图（Agent 能"看到"页面设计）
    - 能提取渲染后的完整 DOM
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="browse_website",
            description="Open a URL in a real browser, take a screenshot, and extract rendered content. Use for: analyzing competitor landing pages, checking product pages, seeing how websites look on mobile. More powerful than scrape_website — handles JavaScript-rendered pages.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to browse"},
                    "screenshot": {"type": "boolean", "description": "Take a screenshot", "default": True},
                    "mobile": {"type": "boolean", "description": "Emulate mobile device", "default": False},
                    "wait_seconds": {"type": "integer", "description": "Wait N seconds for page to load", "default": 3},
                },
                "required": ["url"],
            },
            concurrent_safe=False,  # 浏览器不并发
            result_budget=30_000,
        )

    async def execute(self, url: str, screenshot: bool = True, mobile: bool = False, wait_seconds: int = 3, analyze: bool = True) -> Any:
        browser = await _get_browser()
        if not browser:
            # 降级到普通 scrape
            from app.agent.tools.research import ScrapeWebsiteTool
            logger.info("Playwright not available, falling back to httpx scrape")
            fallback = ScrapeWebsiteTool()
            result = await fallback.execute(url=url)
            result["note"] = "Rendered with httpx (Playwright not available). No screenshot."
            return result

        page = None
        try:
            context_options = {}
            if mobile:
                context_options = {
                    "viewport": {"width": 375, "height": 812},
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                    "device_scale_factor": 3,
                    "is_mobile": True,
                }
            else:
                context_options = {
                    "viewport": {"width": 1280, "height": 800},
                }

            context = await browser.new_context(**context_options)
            page = await context.new_page()

            # 导航
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(wait_seconds * 1000)

            # 提取内容
            title = await page.title()
            
            # 提取元数据
            meta = await page.evaluate("""() => {
                const metas = {};
                document.querySelectorAll('meta').forEach(m => {
                    const name = m.getAttribute('name') || m.getAttribute('property') || '';
                    const content = m.getAttribute('content') || '';
                    if (name && content) metas[name] = content;
                });
                return metas;
            }""")

            # 提取可见文本（去掉 script/style）
            text_content = await page.evaluate("""() => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                return clone.innerText.substring(0, 15000);
            }""")

            # 提取链接
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({text: a.innerText.trim().substring(0, 50), href: a.href}))
                    .filter(l => l.text && l.href.startsWith('http'))
                    .slice(0, 20);
            }""")

            result = {
                "url": url,
                "title": title,
                "meta": meta,
                "content_preview": text_content[:5000],
                "content_length": len(text_content),
                "links_count": len(links),
                "links": links[:10],
                "rendered": True,
                "mobile": mobile,
            }

            # 截图
            screenshot_bytes = None
            if screenshot:
                screenshot_bytes = await page.screenshot(full_page=False, type="png")
                # 存到 workspace
                workspace = Path(".crabres/memory/workspace/assets")
                workspace.mkdir(parents=True, exist_ok=True)
                import hashlib
                filename = f"screenshot_{hashlib.md5(url.encode()).hexdigest()[:8]}.png"
                filepath = workspace / filename
                filepath.write_bytes(screenshot_bytes)
                result["screenshot_path"] = str(filepath)
                result["screenshot_size"] = len(screenshot_bytes)
                result["screenshot_note"] = f"Screenshot saved: {filepath} ({len(screenshot_bytes)//1024}KB)"

            await context.close()

            # 多模态 LLM 理解截图（如果截图成功且 analyze=True）
            if screenshot_bytes and analyze:
                visual_analysis = await self._analyze_screenshot(screenshot_bytes, url, title)
                if visual_analysis:
                    result["visual_analysis"] = visual_analysis

            logger.info(f"Browse {url}: title='{title[:50]}', {len(text_content)} chars, screenshot={'yes' if screenshot else 'no'}, analyzed={'yes' if screenshot_bytes and analyze else 'no'}")
            return result

        except Exception as e:
            if page:
                try:
                    await page.context.close()
                except Exception:
                    pass
            logger.error(f"Browse failed for {url}: {e}")
            # 降级
            from app.agent.tools.research import ScrapeWebsiteTool
            fallback = ScrapeWebsiteTool()
            result = await fallback.execute(url=url)
            result["browse_error"] = str(e)[:200]
            result["note"] = "Playwright failed, fell back to httpx scrape"
            return result
        finally:
            # Render 512MB 限制：用完立即释放浏览器进程
            await _release_browser()

    async def _analyze_screenshot(self, screenshot_bytes: bytes, url: str, title: str) -> Optional[str]:
        """
        用多模态 LLM 理解截图内容。

        比解析 HTML 更鲁棒：网页结构会变，但视觉布局相对稳定。
        能理解：产品定位、定价、CTA 按钮、设计风格、信任信号等。
        """
        try:
            from app.core.config import get_settings
            settings = get_settings()

            # 用 OpenRouter（支持多模态）或 OpenAI
            api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
            if not api_key:
                return None

            import httpx

            b64_image = base64.b64encode(screenshot_bytes).decode("utf-8")

            # 选择 API 端点
            if settings.OPENROUTER_API_KEY:
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                model = "google/gemini-2.0-flash-001"  # 便宜且支持视觉
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://crabres.com",
                }
            else:
                api_url = "https://api.openai.com/v1/chat/completions"
                model = "gpt-4o-mini"
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}

            payload = {
                "model": model,
                "max_tokens": 800,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"Analyze this screenshot of {url} (title: '{title}'). "
                                    f"In 3-5 bullet points, describe:\n"
                                    f"1. What product/service this is\n"
                                    f"2. Their main value proposition (from the hero section)\n"
                                    f"3. Pricing if visible\n"
                                    f"4. Key trust signals (logos, testimonials, numbers)\n"
                                    f"5. Design quality and overall impression\n"
                                    f"Be specific and concise."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}",
                                    "detail": "low",  # 省 token
                                },
                            },
                        ],
                    }
                ],
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                analysis = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if analysis:
                    logger.info(f"Visual analysis complete for {url}: {len(analysis)} chars")
                return analysis

        except Exception as e:
            logger.warning(f"Screenshot analysis failed for {url}: {e}")
            return None
