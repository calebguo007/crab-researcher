"""
RAG 知识库 API
文档上传 / 向量检索 / 混合检索
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import RAGSearchQuery, RAGUpload, MessageResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG知识库"])


@router.post("/upload", response_model=MessageResponse, summary="上传文档到知识库")
async def upload_document(
    body: RAGUpload,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rag = RAGService(db)
    doc = await rag.upload_document(
        user_id=current_user["user_id"],
        doc_type=body.doc_type,
        title=body.title,
        content=body.content,
        metadata=body.metadata,
    )
    return MessageResponse(
        message="文档上传成功",
        data={"id": doc.id, "title": doc.title},
    )


@router.post("/search", response_model=list[dict], summary="检索知识库")
async def search_documents(
    body: RAGSearchQuery,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rag = RAGService(db)

    if body.mode == "keyword":
        return await rag.keyword_search(
            user_id=current_user["user_id"],
            query=body.query,
            top_k=body.top_k,
            doc_type=body.doc_type,
        )

    if body.mode == "hybrid":
        return await rag.hybrid_search(
            user_id=current_user["user_id"],
            query=body.query,
            top_k=body.top_k,
            doc_type=body.doc_type,
            vector_top_k=body.vector_top_k,
            keyword_top_k=body.keyword_top_k,
        )

    return await rag.search(
        user_id=current_user["user_id"],
        query=body.query,
        top_k=body.top_k,
        doc_type=body.doc_type,
    )
