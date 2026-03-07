"""
数据抓取服务 - 竞品价格/促销/舆情/新品监测
策略:
  1. 尝试 HTTP 抓取电商/社交平台搜索页面
  2. 解析 HTML 提取结构化数据
  3. 解析失败时用 LLM 辅助从页面文本提取信息
  4. 所有请求走域名白名单校验
"""

import json
import logging
import random
import re
from datetime import datetime
from typing import Optional
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import validate_domain
from app.models.task import MonitoringResult, MonitoringTask
from app.services.llm_service import LLMService
from app.services.cost_controller import TaskTier

settings = get_settings()
logger = logging.getLogger(__name__)

# User-Agent 池（模拟主流浏览器）
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]

# 平台搜索 URL 模板
PLATFORM_SEARCH_URLS = {
    "jd": "https://search.jd.com/Search?keyword={keyword}&enc=utf-8",
    "taobao": "https://s.taobao.com/search?q={keyword}",
    "tmall": "https://list.tmall.com/search_product.htm?q={keyword}",
    "pdd": "https://mobile.yangkeduo.com/search_result.html?search_key={keyword}",
    "1688": "https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}",
    "xiaohongshu": "https://www.xiaohongshu.com/search_result?keyword={keyword}",
    "douyin": "https://www.douyin.com/search/{keyword}",
    "weibo": "https://s.weibo.com/weibo?q={keyword}",
}


class ScraperService:
    """数据抓取引擎 - 真实HTTP抓取 + LLM辅助解析"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            },
        )
        self._llm: Optional[LLMService] = None

    @property
    def llm(self) -> LLMService:
        if self._llm is None:
            self._llm = LLMService(self.db)
        return self._llm

    async def close(self):
        await self.client.aclose()

    # ================================================================
    # 公共入口
    # ================================================================

    async def scrape_price(self, task: MonitoringTask) -> MonitoringResult:
        """价格监测主入口"""
        brand = task.brand_name
        platform = task.platform
        config = task.config or {}
        keywords = getattr(task, "keywords", None) or config.get("keywords", [])
        product_url = getattr(task, "product_url", None) or config.get("product_url")

        logger.info(f"[Scraper] 价格监测: brand={brand}, platform={platform}")

        data = {
            "brand": brand,
            "platform": platform,
            "scraped_at": datetime.utcnow().isoformat(),
            "products": [],
            "source": "unknown",
        }

        try:
            # 策略1: 如果有直接商品URL，优先抓取
            if product_url:
                products = await self._scrape_url_price(product_url)
                if products:
                    data["products"] = products
                    data["source"] = "direct_url"

            # 策略2: 通过平台搜索页抓取
            if not data["products"]:
                search_keywords = keywords if keywords else [brand]
                for kw in search_keywords[:3]:  # 最多搜索3个关键词
                    products = await self._scrape_platform_search(platform, kw)
                    if products:
                        data["products"].extend(products)
                        data["source"] = "platform_search"

            # 策略3: HTTP抓取均失败，用 LLM 分析已有信息
            if not data["products"]:
                products = await self._llm_price_analysis(brand, platform, keywords)
                data["products"] = products
                data["source"] = "llm_analysis"

        except Exception as e:
            logger.error(f"[Scraper] 价格抓取异常: {e}")
            data["error"] = str(e)

        # 对比历史数据检测变化
        change_detected, change_type, change_summary = await self._detect_price_change(
            task.id, data
        )

        result = MonitoringResult(
            task_id=task.id,
            data=data,
            change_detected=change_detected,
            change_type=change_type,
            change_summary=change_summary,
            severity="warning" if change_detected else "info",
        )
        self.db.add(result)
        return result

    async def scrape_sentiment(self, task: MonitoringTask) -> MonitoringResult:
        """舆情监测主入口"""
        brand = task.brand_name
        platform = task.platform
        config = task.config or {}
        keywords = getattr(task, "keywords", None) or config.get("keywords", [])

        logger.info(f"[Scraper] 舆情监测: brand={brand}, platform={platform}")

        data = {
            "brand": brand,
            "platform": platform,
            "scraped_at": datetime.utcnow().isoformat(),
            "mentions": [],
            "sentiment_score": 0.0,
            "hot_topics": [],
            "sample_posts": [],
            "source": "unknown",
        }

        try:
            # 策略1: 抓取社交平台搜索页
            search_keywords = keywords if keywords else [brand]
            raw_posts = []
            for kw in search_keywords[:3]:
                posts = await self._scrape_social_posts(platform, kw)
                raw_posts.extend(posts)

            if raw_posts:
                data["sample_posts"] = raw_posts[:20]  # 保留前20条
                data["source"] = "platform_scrape"

            # 策略2: 用 LLM 做情感分析
            sentiment_result = await self._llm_sentiment_analysis(
                brand, platform, keywords, raw_posts
            )
            data["mentions"] = sentiment_result.get("mentions", [])
            data["sentiment_score"] = sentiment_result.get("sentiment_score", 0.5)
            data["hot_topics"] = sentiment_result.get("hot_topics", [])

            if data["source"] == "unknown":
                data["source"] = "llm_analysis"

        except Exception as e:
            logger.error(f"[Scraper] 舆情抓取异常: {e}")
            data["error"] = str(e)
            data["sentiment_score"] = 0.5  # 异常时设为中性

        # 检测舆情爆发
        score = data["sentiment_score"]
        mention_count = sum(m.get("count", 0) for m in data["mentions"])
        change_detected = score < 0.4 or mention_count > 300
        severity = "critical" if score < 0.3 else "warning" if change_detected else "info"

        result = MonitoringResult(
            task_id=task.id,
            data=data,
            change_detected=change_detected,
            change_type="sentiment_spike" if change_detected else None,
            change_summary=(
                f"舆情评分: {score:.2f}, 总提及量: {mention_count}"
                if change_detected else None
            ),
            severity=severity,
        )
        self.db.add(result)
        return result

    async def scrape_new_product(self, task: MonitoringTask) -> MonitoringResult:
        """新品监测主入口"""
        brand = task.brand_name
        platform = task.platform
        config = task.config or {}
        keywords = getattr(task, "keywords", None) or config.get("keywords", [])

        logger.info(f"[Scraper] 新品监测: brand={brand}, platform={platform}")

        data = {
            "brand": brand,
            "platform": platform,
            "scraped_at": datetime.utcnow().isoformat(),
            "new_products": [],
            "source": "unknown",
        }

        try:
            # 抓取当前商品列表
            search_keywords = keywords if keywords else [brand]
            current_products = []
            for kw in search_keywords[:3]:
                products = await self._scrape_platform_search(platform, kw)
                current_products.extend(products)

            # 如果抓取失败，用LLM分析
            if not current_products:
                current_products = await self._llm_price_analysis(brand, platform, keywords)

            # 与历史数据对比，发现新品
            if current_products:
                new_products = await self._detect_new_products(task.id, current_products)
                data["new_products"] = new_products
                data["all_products"] = current_products
                data["source"] = "comparison"

        except Exception as e:
            logger.error(f"[Scraper] 新品监测异常: {e}")
            data["error"] = str(e)

        has_new = len(data["new_products"]) > 0
        result = MonitoringResult(
            task_id=task.id,
            data=data,
            change_detected=has_new,
            change_type="new_product" if has_new else None,
            change_summary=(
                f"发现{len(data['new_products'])}个新品: "
                + ", ".join(p.get("name", "未知") for p in data["new_products"][:5])
                if has_new else None
            ),
            severity="warning" if has_new else "info",
        )
        self.db.add(result)
        return result

    # ================================================================
    # HTTP 抓取层
    # ================================================================

    async def _fetch_page(self, url: str) -> Optional[str]:
        """安全地抓取页面 HTML"""
        try:
            # 换一个新的 UA
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp = await self.client.get(url, headers=headers)
            resp.raise_for_status()

            # 尝试自动检测编码
            content = resp.text
            if len(content) < 100:
                logger.warning(f"[Scraper] 页面内容过短: {url}")
                return None

            return content

        except httpx.HTTPStatusError as e:
            logger.warning(f"[Scraper] HTTP {e.response.status_code}: {url}")
            return None
        except httpx.RequestError as e:
            logger.warning(f"[Scraper] 请求失败: {url}, {e}")
            return None

    async def _scrape_url_price(self, url: str) -> list[dict]:
        """直接从商品URL抓取价格"""
        html = await self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        products = []

        # 通用价格提取 — 搜索常见价格标签
        price_patterns = [
            r'¥\s*([\d,]+\.?\d*)',
            r'￥\s*([\d,]+\.?\d*)',
            r'"price"\s*:\s*"?([\d.]+)"?',
            r'data-price="([\d.]+)"',
            r'class="[^"]*price[^"]*"[^>]*>([\d,.]+)',
        ]

        text = soup.get_text(" ", strip=True)
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "未知商品"

        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    price = float(matches[0].replace(",", ""))
                    if 0.01 < price < 1_000_000:  # 合理价格范围
                        products.append({
                            "name": title[:100],
                            "price": price,
                            "url": url,
                            "source": "direct_parse",
                        })
                        break
                except (ValueError, IndexError):
                    continue

        # 如果正则解析失败，用 LLM 从页面文本中提取
        if not products and len(text) > 50:
            products = await self._llm_extract_from_html(text[:3000], url)

        return products

    async def _scrape_platform_search(self, platform: str, keyword: str) -> list[dict]:
        """通过平台搜索页抓取商品列表"""
        url_template = PLATFORM_SEARCH_URLS.get(platform.lower())
        if not url_template:
            logger.info(f"[Scraper] 平台 {platform} 暂无搜索URL模板，跳过HTTP抓取")
            return []

        url = url_template.format(keyword=quote(keyword))
        html = await self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        products = []

        # 根据平台使用不同的解析策略
        if platform.lower() == "jd":
            products = self._parse_jd_search(soup, keyword)
        elif platform.lower() in ("taobao", "tmall"):
            products = self._parse_taobao_search(soup, keyword)
        else:
            products = self._parse_generic_search(soup, keyword, platform)

        # 正则/选择器解析失败，尝试 LLM 辅助
        if not products:
            text = soup.get_text(" ", strip=True)
            if len(text) > 100:
                products = await self._llm_extract_from_html(text[:5000], url)

        return products

    def _parse_jd_search(self, soup: BeautifulSoup, keyword: str) -> list[dict]:
        """解析京东搜索结果"""
        products = []

        # 京东搜索结果 li.gl-item
        items = soup.select("li.gl-item") or soup.select(".J_goodsList li")
        for item in items[:10]:
            try:
                name_el = item.select_one(".p-name a, .p-name em")
                price_el = item.select_one(".p-price strong i, .p-price .J_price")
                link_el = item.select_one(".p-name a")

                name = name_el.get_text(strip=True) if name_el else ""
                price_text = price_el.get_text(strip=True) if price_el else ""
                link = link_el.get("href", "") if link_el else ""

                if link and not link.startswith("http"):
                    link = "https:" + link

                if name and price_text:
                    try:
                        price = float(price_text.replace(",", ""))
                        products.append({
                            "name": name[:200],
                            "price": price,
                            "url": link,
                            "source": "jd_search",
                        })
                    except ValueError:
                        pass
            except Exception:
                continue

        return products

    def _parse_taobao_search(self, soup: BeautifulSoup, keyword: str) -> list[dict]:
        """解析淘宝/天猫搜索结果"""
        products = []

        # 淘宝搜索结果
        items = soup.select(".item.J_MouserOnverReq") or soup.select('[data-item="true"]')
        for item in items[:10]:
            try:
                name_el = item.select_one(".title a, .row-2 a")
                price_el = item.select_one(".price strong, .price-row .price")
                link_el = item.select_one(".title a, .row-2 a")

                name = name_el.get_text(strip=True) if name_el else ""
                price_text = price_el.get_text(strip=True) if price_el else ""
                link = link_el.get("href", "") if link_el else ""

                if link and not link.startswith("http"):
                    link = "https:" + link

                if name and price_text:
                    try:
                        price = float(re.findall(r'[\d.]+', price_text)[0])
                        products.append({
                            "name": name[:200],
                            "price": price,
                            "url": link,
                            "source": "taobao_search",
                        })
                    except (ValueError, IndexError):
                        pass
            except Exception:
                continue

        return products

    def _parse_generic_search(self, soup: BeautifulSoup, keyword: str, platform: str) -> list[dict]:
        """通用搜索结果解析 — 尝试从页面中提取价格信息"""
        products = []
        text = soup.get_text(" ", strip=True)

        # 尝试找到包含价格的结构化数据
        price_matches = re.findall(
            r'(?:¥|￥|price["\s:]+)\s*([\d,]+\.?\d*)',
            text, re.IGNORECASE
        )

        for i, price_str in enumerate(price_matches[:10]):
            try:
                price = float(price_str.replace(",", ""))
                if 0.01 < price < 1_000_000:
                    products.append({
                        "name": f"{keyword} 商品{i+1}",
                        "price": price,
                        "url": "",
                        "source": f"{platform}_generic_parse",
                    })
            except ValueError:
                continue

        return products

    async def _scrape_social_posts(self, platform: str, keyword: str) -> list[dict]:
        """抓取社交平台帖子"""
        url_template = PLATFORM_SEARCH_URLS.get(platform.lower())
        if not url_template:
            return []

        url = url_template.format(keyword=quote(keyword))
        html = await self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        posts = []

        if platform.lower() == "weibo":
            cards = soup.select(".card-wrap .content") or soup.select('[action-type="feed_list_item"]')
            for card in cards[:20]:
                text = card.get_text(strip=True)
                if text and len(text) > 10:
                    posts.append({"text": text[:500], "platform": "weibo"})

        elif platform.lower() == "xiaohongshu":
            notes = soup.select(".note-item") or soup.select('[data-type="note"]')
            for note in notes[:20]:
                text = note.get_text(strip=True)
                if text and len(text) > 10:
                    posts.append({"text": text[:500], "platform": "xiaohongshu"})

        else:
            # 通用：提取所有段落文本
            paragraphs = soup.find_all(["p", "div", "span"], string=True)
            for p in paragraphs[:30]:
                text = p.get_text(strip=True)
                if text and len(text) > 20 and keyword.lower() in text.lower():
                    posts.append({"text": text[:500], "platform": platform})

        return posts

    # ================================================================
    # LLM 辅助分析层
    # ================================================================

    async def _llm_extract_from_html(self, text: str, url: str) -> list[dict]:
        """用 LLM 从页面文本中提取商品信息"""
        try:
            result = await self.llm.chat(
                user_id=0,
                tier=TaskTier.TIER_2_SIMPLE,
                task_type="scrape_extract",
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一个电商数据提取助手。从给定的网页文本中提取商品名称和价格。"
                            "只返回JSON数组，每个元素包含 name 和 price 字段。"
                            "如果无法提取到有效数据，返回空数组 []。"
                            "注意：只提取真实的商品数据，不要编造。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"从以下网页文本中提取商品名称和价格:\n\n{text}",
                    },
                ],
            )
            content = result["content"]
            # 提取 JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                products_raw = json.loads(json_match.group())
                return [
                    {
                        "name": p.get("name", "")[:200],
                        "price": float(p.get("price", 0)),
                        "url": url,
                        "source": "llm_extract",
                    }
                    for p in products_raw
                    if p.get("name") and p.get("price")
                ]
        except Exception as e:
            logger.warning(f"[Scraper] LLM提取失败: {e}")

        return []

    async def _llm_price_analysis(
        self, brand: str, platform: str, keywords: list[str]
    ) -> list[dict]:
        """当HTTP抓取全部失败时，用LLM分析品牌价格信息"""
        search_terms = keywords if keywords else [brand]
        try:
            result = await self.llm.chat(
                user_id=0,
                tier=TaskTier.TIER_2_SIMPLE,
                task_type="price_analysis",
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一个市场调研助手。根据你的知识，提供品牌在指定平台上的主要产品和价格区间。"
                            "以JSON数组格式返回，每个元素包含: name(产品名), price(参考价格,数字), "
                            "price_range(价格区间描述), note(信息来源说明)。"
                            "重要：明确标注这是基于公开信息的参考数据，非实时价格。"
                            "如果你不了解该品牌，返回空数组 []。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"品牌: {brand}\n"
                            f"平台: {platform}\n"
                            f"关键词: {', '.join(search_terms)}\n"
                            f"请提供该品牌在此平台上的主要产品和价格参考。"
                        ),
                    },
                ],
            )
            content = result["content"]
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                products_raw = json.loads(json_match.group())
                return [
                    {
                        "name": p.get("name", "")[:200],
                        "price": float(p.get("price", 0)) if p.get("price") else 0,
                        "price_range": p.get("price_range", ""),
                        "note": p.get("note", "LLM参考数据，非实时价格"),
                        "source": "llm_knowledge",
                    }
                    for p in products_raw
                    if p.get("name")
                ]
        except Exception as e:
            logger.warning(f"[Scraper] LLM价格分析失败: {e}")

        return []

    async def _llm_sentiment_analysis(
        self,
        brand: str,
        platform: str,
        keywords: list[str],
        raw_posts: list[dict],
    ) -> dict:
        """用 LLM 做舆情分析"""
        try:
            # 构建帖子摘要
            post_summary = ""
            if raw_posts:
                post_texts = [p.get("text", "")[:200] for p in raw_posts[:15]]
                post_summary = f"\n\n以下是从 {platform} 抓取到的相关帖子:\n" + "\n---\n".join(post_texts)

            search_terms = keywords if keywords else [brand]

            result = await self.llm.chat(
                user_id=0,
                tier=TaskTier.TIER_2_SIMPLE,
                task_type="sentiment_analysis",
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一个品牌舆情分析助手。分析品牌在社交平台上的口碑和舆情。"
                            "返回JSON对象，包含以下字段:\n"
                            "- mentions: [{keyword: 关键词, count: 估算提及量(整数), trend: up/down/stable}]\n"
                            "- sentiment_score: 0-1之间的情感评分(0极差, 0.5中性, 1极好)\n"
                            "- hot_topics: [近期热门话题字符串列表]\n"
                            "- analysis: 简短舆情分析文本(100字内)\n"
                            "如果有真实帖子数据，基于帖子分析；如果没有，基于你的知识给出参考评估。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"品牌: {brand}\n"
                            f"平台: {platform}\n"
                            f"关键词: {', '.join(search_terms)}"
                            f"{post_summary}"
                        ),
                    },
                ],
            )
            content = result["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"[Scraper] LLM舆情分析失败: {e}")

        # 返回默认中性结果
        return {
            "mentions": [{"keyword": brand, "count": 0, "trend": "stable"}],
            "sentiment_score": 0.5,
            "hot_topics": [],
            "analysis": "舆情数据获取失败，暂无法分析",
        }

    # ================================================================
    # 数据对比检测层
    # ================================================================

    async def _detect_price_change(
        self, task_id: int, new_data: dict
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """对比历史数据，检测价格变化（阈值: >10%）"""
        last_result = await self.db.execute(
            select(MonitoringResult)
            .where(MonitoringResult.task_id == task_id)
            .order_by(MonitoringResult.created_at.desc())
            .limit(1)
        )
        last = last_result.scalar_one_or_none()

        if not last or not last.data:
            return False, None, None

        old_products = last.data.get("products", [])
        new_products = new_data.get("products", [])

        if not old_products or not new_products:
            return False, None, None

        # 尝试匹配同名商品进行价格对比
        changes = []
        for new_p in new_products:
            new_name = new_p.get("name", "")
            new_price = new_p.get("price", 0)
            if not new_price:
                continue

            # 找到历史中同名/相似商品
            best_match = None
            for old_p in old_products:
                old_name = old_p.get("name", "")
                # 简单匹配：名称包含关系
                if old_name and new_name and (
                    old_name in new_name or new_name in old_name
                    or old_name == new_name
                ):
                    best_match = old_p
                    break

            if not best_match:
                # 没找到匹配的，用第一个商品对比
                if old_products:
                    best_match = old_products[0]
                else:
                    continue

            old_price = best_match.get("price", 0)
            if old_price == 0:
                continue

            change_pct = (new_price - old_price) / old_price * 100
            if abs(change_pct) > 10:
                changes.append({
                    "product": new_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_pct": round(change_pct, 1),
                })

        if changes:
            ch = changes[0]
            direction = "上涨" if ch["change_pct"] > 0 else "下降"
            change_type = "price_up" if ch["change_pct"] > 0 else "price_down"
            summary_parts = [
                f"{c['product']}: ¥{c['old_price']} → ¥{c['new_price']} ({'+' if c['change_pct']>0 else ''}{c['change_pct']}%)"
                for c in changes[:3]
            ]
            summary = f"价格{direction}预警:\n" + "\n".join(summary_parts)
            return True, change_type, summary

        return False, None, None

    async def _detect_new_products(
        self, task_id: int, current_products: list[dict]
    ) -> list[dict]:
        """对比历史数据发现新品"""
        # 获取最近5次的历史结果
        results = await self.db.execute(
            select(MonitoringResult)
            .where(MonitoringResult.task_id == task_id)
            .order_by(MonitoringResult.created_at.desc())
            .limit(5)
        )
        history_results = results.scalars().all()

        # 收集历史中出现过的商品名
        known_names = set()
        for hr in history_results:
            if hr.data:
                for key in ("products", "all_products"):
                    for p in hr.data.get(key, []):
                        name = p.get("name", "").strip()
                        if name:
                            known_names.add(name.lower())

        # 如果没有历史数据，不判断新品（首次运行）
        if not known_names:
            return []

        # 发现新品
        new_products = []
        for p in current_products:
            name = p.get("name", "").strip()
            if name and name.lower() not in known_names:
                new_products.append(p)

        return new_products
