"""
报告生成 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.task import Report
from app.models.schemas import ReportGenerate, ReportResponse, PaginatedResponse
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/reports", tags=["报告"])


@router.post("/generate", response_model=ReportResponse, summary="生成报告")
async def generate_report(
    body: ReportGenerate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    generator = ReportGenerator(db)
    report = await generator.generate(
        user_id=current_user["user_id"],
        report_type=body.report_type,
        brands=body.brands,
        title=body.title,
        custom_prompt=body.custom_prompt,
    )
    return report


@router.get("/list", response_model=PaginatedResponse, summary="报告列表")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Report).where(Report.user_id == current_user["user_id"])
    count_stmt = select(func.count()).select_from(Report).where(
        Report.user_id == current_user["user_id"]
    )

    if report_type:
        stmt = stmt.where(Report.report_type == report_type)
        count_stmt = count_stmt.where(Report.report_type == report_type)

    total = (await db.execute(count_stmt)).scalar()
    result = await db.execute(
        stmt.order_by(Report.generated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return PaginatedResponse(
        items=[ReportResponse.model_validate(r) for r in result.scalars().all()],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{report_id}", response_model=ReportResponse, summary="报告详情")
async def get_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user["user_id"],
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report
