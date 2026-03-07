"""
RAG 检索服务
支持: 向量检索 / 关键词检索 / 混合检索
"""

import logging
import re
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import RAGDocument
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 知识库检索服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService(db)

    async def upload_document(
        self,
        user_id: int,
        doc_type: str,
        title: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> RAGDocument:
        logger.info("[RAG] 上传文档: user=%s, title=%s", user_id, title)

        embedding = None
        try:
            embedding = await self.llm.generate_embedding(content[:8000])
        except Exception as e:
            logger.warning("[RAG] embedding 生成失败，降级为关键词检索可用: %s", e)

        doc = RAGDocument(
            user_id=user_id,
            doc_type=doc_type,
            title=title,
            content=content,
            embedding=embedding,
            metadata_=metadata or {},
        )
        self.db.add(doc)
        await self.db.flush()

        logger.info("[RAG] 文档上传成功: id=%s", doc.id)
        return doc

    async def search(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
    ) -> list[dict]:
        """向量检索"""
        try:
            query_embedding = await self.llm.generate_embedding(query)
        except Exception as e:
            logger.warning("[RAG] 向量检索降级为关键词检索: %s", e)
            return await self.keyword_search(user_id, query, top_k, doc_type)

        stmt = (
            select(
                RAGDocument,
                RAGDocument.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .where(RAGDocument.user_id == user_id, RAGDocument.embedding.is_not(None))
            .order_by("distance")
            .limit(top_k)
        )

        if doc_type:
            stmt = stmt.where(RAGDocument.doc_type == doc_type)

        rows = (await self.db.execute(stmt)).all()
        docs = []
        for rank, (doc, distance) in enumerate(rows, 1):
            similarity = max(0.0, 1 - float(distance))
            docs.append(
                {
                    "id": doc.id,
                    "doc_type": doc.doc_type,
                    "title": doc.title,
                    "content": doc.content,
                    "metadata": doc.metadata_,
                    "similarity": round(similarity, 4),
                    "vector_rank": rank,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
            )

        logger.info("[RAG] 向量检索命中: %s", len(docs))
        return docs

    async def keyword_search(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
    ) -> list[dict]:
        """关键词检索（标题/内容模糊匹配）"""
        keywords = self._extract_keywords(query)
        patterns = [f"%{k}%" for k in keywords if k]
        if not patterns:
            patterns = [f"%{query}%"]

        conditions = []
        for pattern in patterns:
            conditions.append(RAGDocument.title.ilike(pattern))
            conditions.append(RAGDocument.content.ilike(pattern))

        stmt = (
            select(RAGDocument)
            .where(RAGDocument.user_id == user_id, or_(*conditions))
            .order_by(RAGDocument.created_at.desc())
            .limit(top_k)
        )

        if doc_type:
            stmt = stmt.where(RAGDocument.doc_type == doc_type)

        rows = (await self.db.execute(stmt)).scalars().all()
        docs = []
        for rank, doc in enumerate(rows, 1):
            keyword_score = self._keyword_score(doc.title, doc.content, keywords)
            docs.append(
                {
                    "id": doc.id,
                    "doc_type": doc.doc_type,
                    "title": doc.title,
                    "content": doc.content,
                    "metadata": doc.metadata_,
                    "keyword_score": round(keyword_score, 4),
                    "keyword_rank": rank,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
            )

        logger.info("[RAG] 关键词检索命中: %s", len(docs))
        return docs

    async def hybrid_search(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
        vector_top_k: int = 12,
        keyword_top_k: int = 12,
    ) -> list[dict]:
        """混合检索：向量召回 + 关键词召回 + 轻量融合排序"""
        vector_results = await self.search(
            user_id=user_id,
            query=query,
            top_k=vector_top_k,
            doc_type=doc_type,
        )
        keyword_results = await self.keyword_search(
            user_id=user_id,
            query=query,
            top_k=keyword_top_k,
            doc_type=doc_type,
        )

        merged: dict[int, dict] = {}

        for idx, item in enumerate(vector_results, 1):
            doc_id = item["id"]
            merged.setdefault(doc_id, item.copy())
            merged[doc_id]["hybrid_score"] = merged[doc_id].get("hybrid_score", 0.0) + (0.7 / idx)

        for idx, item in enumerate(keyword_results, 1):
            doc_id = item["id"]
            if doc_id not in merged:
                merged[doc_id] = item.copy()
            else:
                merged[doc_id].update({k: v for k, v in item.items() if k not in {"content", "title"}})
            merged[doc_id]["hybrid_score"] = merged[doc_id].get("hybrid_score", 0.0) + (0.3 / idx)

        ranked = sorted(merged.values(), key=lambda x: x.get("hybrid_score", 0.0), reverse=True)[:top_k]
        for i, item in enumerate(ranked, 1):
            item["hybrid_rank"] = i
            item["hybrid_score"] = round(float(item.get("hybrid_score", 0.0)), 6)

        logger.info(
            "[RAG] 混合检索命中: total=%s vector=%s keyword=%s",
            len(ranked),
            len(vector_results),
            len(keyword_results),
        )
        return ranked

    async def search_and_augment(
        self,
        user_id: int,
        query: str,
        top_k: int = 3,
        doc_type: Optional[str] = None,
        mode: str = "hybrid",
    ) -> str:
        if mode == "keyword":
            docs = await self.keyword_search(user_id, query, top_k, doc_type)
        elif mode == "vector":
            docs = await self.search(user_id, query, top_k, doc_type)
        else:
            docs = await self.hybrid_search(user_id, query, top_k, doc_type)

        if not docs:
            return ""

        context_parts = ["以下是相关的参考资料:\n"]
        for i, doc in enumerate(docs, 1):
            score = doc.get("hybrid_score", doc.get("similarity", doc.get("keyword_score", 0.0)))
            context_parts.append(
                f"---\n"
                f"📄 参考资料 {i}: {doc['title']} (相关度: {float(score):.2f})\n"
                f"类型: {doc['doc_type']}\n"
                f"内容:\n{doc['content'][:2000]}\n"
            )
        context_parts.append("---\n请基于以上参考资料回答用户的问题。")

        return "\n".join(context_parts)

    @staticmethod
    def _extract_keywords(query: str) -> list[str]:
        base = query.strip()
        if not base:
            return []

        tokens = [t for t in re.split(r"[\s,，。；;、]+", base) if t]
        if base not in tokens:
            tokens.insert(0, base)
        # 去重并限制关键词数量
        dedup = []
        for t in tokens:
            if t not in dedup:
                dedup.append(t)
        return dedup[:6]

    @staticmethod
    def _keyword_score(title: str, content: str, keywords: list[str]) -> float:
        if not keywords:
            return 0.0
        text = f"{title}\n{content}".lower()
        score = 0.0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text:
                score += 1.0
        return score / len(keywords)
