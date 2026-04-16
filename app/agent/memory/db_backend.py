"""
CrabRes Memory — PostgreSQL 后端

GrowthMemory 的 DB 实现，替代文件系统存储。
接口与原 GrowthMemory 完全兼容，上层代码无需修改。

设计：
- save/load 操作走 PostgreSQL（通过 SQLAlchemy async）
- 文件系统作为 fallback（DB 不可用时降级）
- journal 用独立表（append-only，不走 upsert）
"""

import json
import time
import hashlib
import logging
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger(__name__)


class DBGrowthMemory:
    """PostgreSQL-backed 记忆系统 — 接口兼容 GrowthMemory"""

    CATEGORIES = [
        "product", "goals", "research", "strategy",
        "execution", "feedback", "journal", "knowledge",
    ]

    def __init__(self, user_id: str = "global"):
        self.user_id = str(user_id)
        # 兼容 GrowthMemory 接口 — loop.py 用 memory.base_dir 构建 workspace 路径
        import os
        render_disk = os.environ.get("RENDER_DISK_PATH", ".crabres")
        self.base_dir = f"{render_disk}/memory/{user_id}"

    def _get_session_factory(self):
        """延迟导入，避免循环依赖"""
        from app.core.database import AsyncSessionLocal
        return AsyncSessionLocal

    async def save(self, key: str, data: Any, category: str = "product"):
        """
        保存记忆到 DB（带版本追踪）
        
        使用 PostgreSQL upsert（INSERT ... ON CONFLICT UPDATE）
        """
        from app.models.growth_memory import MemoryRecord

        # 版本追踪
        version = 1
        if isinstance(data, dict):
            content_str = json.dumps(
                {k: v for k, v in data.items() if not k.startswith("_")},
                ensure_ascii=False, default=str
            )
            content_hash = hashlib.md5(content_str.encode()).hexdigest()[:12]
            data["_version"] = version  # 会被 upsert 更新
            data["_updated_at"] = time.time()
            data["_content_hash"] = content_hash
        else:
            content_hash = ""

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                # 先查是否存在，获取当前版本号
                stmt = select(MemoryRecord).where(
                    and_(
                        MemoryRecord.user_id == self.user_id,
                        MemoryRecord.category == category,
                        MemoryRecord.key == key,
                    )
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    # 更新
                    version = existing.version + 1
                    if isinstance(data, dict):
                        data["_version"] = version
                    existing.data = data
                    existing.version = version
                    existing.content_hash = content_hash
                else:
                    # 新建
                    record = MemoryRecord(
                        user_id=self.user_id,
                        category=category,
                        key=key,
                        data=data,
                        version=version,
                        content_hash=content_hash,
                    )
                    session.add(record)

                await session.commit()
                logger.debug(f"DB Memory saved: {category}/{key} (v{version}) for user={self.user_id}")
        except Exception as e:
            logger.error(f"DB Memory save failed: {category}/{key} — {e}")
            raise

    async def load(self, key: str, category: str = "product") -> Optional[Any]:
        """从 DB 加载记忆"""
        from app.models.growth_memory import MemoryRecord

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                stmt = select(MemoryRecord).where(
                    and_(
                        MemoryRecord.user_id == self.user_id,
                        MemoryRecord.category == category,
                        MemoryRecord.key == key,
                    )
                )
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    return record.data
                return None
        except Exception as e:
            logger.error(f"DB Memory load failed: {category}/{key} — {e}")
            return None

    async def save_knowledge(self, key: str, content: str, source: str,
                             trigger: str = "", expires_days: int = 0):
        """保存外部知识引用"""
        data = {
            "content": content,
            "source": source,
            "trigger": trigger,
            "created_at": time.time(),
            "expires_at": time.time() + expires_days * 86400 if expires_days > 0 else 0,
        }
        await self.save(key, data, category="knowledge")
        logger.info(f"DB Knowledge saved: {key} ({len(content)} chars, source={source})")

    async def get_triggered_knowledge(self, task: str) -> list[dict]:
        """获取与当前任务匹配的外部知识"""
        from app.models.growth_memory import MemoryRecord

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                stmt = select(MemoryRecord).where(
                    and_(
                        MemoryRecord.user_id == self.user_id,
                        MemoryRecord.category == "knowledge",
                    )
                )
                result = await session.execute(stmt)
                records = result.scalars().all()

                results = []
                task_lower = task.lower()
                now = time.time()

                for record in records:
                    data = record.data
                    if not isinstance(data, dict):
                        continue
                    # 检查过期
                    expires_at = data.get("expires_at", 0)
                    if expires_at > 0 and now > expires_at:
                        continue
                    # 检查触发条件
                    trigger = data.get("trigger", "")
                    if trigger:
                        if trigger == "always":
                            results.append(data)
                        elif "contains" in trigger:
                            keyword = trigger.split("contains")[-1].strip()
                            if keyword.lower() in task_lower:
                                results.append(data)
                    else:
                        # 无触发条件 = 关键词匹配
                        key_words = record.key.replace("_", " ").split()
                        if any(word.lower() in task_lower for word in key_words if len(word) > 2):
                            results.append(data)

                return results
        except Exception as e:
            logger.error(f"DB get_triggered_knowledge failed: {e}")
            return []

    async def append_journal(self, entry: dict):
        """追加增长日志"""
        from datetime import datetime as dt
        from app.models.growth_memory import JournalEntry

        today = dt.now().strftime("%Y-%m-%d")
        ts = entry.get("timestamp", time.time())
        entry["timestamp"] = ts

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                record = JournalEntry(
                    user_id=self.user_id,
                    date=today,
                    data=entry,
                    timestamp=ts,
                )
                session.add(record)
                await session.commit()
        except Exception as e:
            logger.error(f"DB append_journal failed: {e}")

    async def list_memories(self, category: str) -> list[str]:
        """列出某个类别的所有记忆 key"""
        from app.models.growth_memory import MemoryRecord

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                stmt = select(MemoryRecord.key).where(
                    and_(
                        MemoryRecord.user_id == self.user_id,
                        MemoryRecord.category == category,
                    )
                )
                result = await session.execute(stmt)
                return [row[0] for row in result.all()]
        except Exception as e:
            logger.error(f"DB list_memories failed: {e}")
            return []

    async def search(self, query: str, categories: list[str] = None) -> list[dict]:
        """简单的关键词搜索记忆（DB 版本，用 JSON 全文搜索）"""
        from app.models.growth_memory import MemoryRecord
        from sqlalchemy import cast, String as SQLString

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                cats = categories or self.CATEGORIES
                stmt = select(MemoryRecord).where(
                    and_(
                        MemoryRecord.user_id == self.user_id,
                        MemoryRecord.category.in_(cats),
                    )
                )
                result = await session.execute(stmt)
                records = result.scalars().all()

                results = []
                query_lower = query.lower()
                for record in records:
                    content_str = json.dumps(record.data, ensure_ascii=False, default=str)
                    if query_lower in content_str.lower():
                        results.append({
                            "category": record.category,
                            "key": record.key,
                            "preview": content_str[:200],
                        })
                return results
        except Exception as e:
            logger.error(f"DB search failed: {e}")
            return []

    async def get_memory_stats(self) -> dict:
        """获取记忆系统统计"""
        from app.models.growth_memory import MemoryRecord, JournalEntry
        from sqlalchemy import func

        SessionLocal = self._get_session_factory()
        try:
            async with SessionLocal() as session:
                stats = {}
                for cat in self.CATEGORIES:
                    stmt = select(func.count()).where(
                        and_(
                            MemoryRecord.user_id == self.user_id,
                            MemoryRecord.category == cat,
                        )
                    )
                    result = await session.execute(stmt)
                    count = result.scalar() or 0
                    stats[cat] = {"count": count, "size_bytes": 0}

                # journal 单独统计
                stmt = select(func.count()).where(
                    JournalEntry.user_id == self.user_id
                )
                result = await session.execute(stmt)
                journal_count = result.scalar() or 0
                stats["journal"] = {"count": journal_count, "size_bytes": 0}

                return {
                    "categories": stats,
                    "total_files": sum(s["count"] for s in stats.values()),
                    "total_size_bytes": 0,
                    "total_size_mb": 0,
                    "backend": "postgresql",
                }
        except Exception as e:
            logger.error(f"DB get_memory_stats failed: {e}")
            return {"error": str(e), "backend": "postgresql"}

    async def semantic_search(self, query: str, categories: list[str] = None, limit: int = 10) -> list[dict]:
        """语义搜索 — DB 版本暂用关键词搜索"""
        return await self.search(query, categories)

    async def search_for_prompt(self, query: str, categories: list[str] = None, max_chars: int = 2000) -> str:
        """搜索并格式化为可注入 prompt 的文本"""
        results = await self.search(query, categories)
        if not results:
            return ""
        lines = ["## RELEVANT MEMORIES (from past sessions)"]
        total_chars = 0
        for r in results[:10]:
            line = f"- [{r['category']}/{r['key']}] {r['preview'][:200]}"
            if total_chars + len(line) > max_chars:
                break
            lines.append(line)
            total_chars += len(line)
        return "\n".join(lines)

    async def reindex(self):
        """DB 模式不需要 reindex"""
        return {"status": "db_backend_no_reindex_needed"}
