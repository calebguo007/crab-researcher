"""
监测任务管理 API
CRUD: 创建 / 列表 / 更新 / 删除 / 查看结果
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.task import MonitoringTask, MonitoringResult
from app.models.schemas import (
    TaskCreate, TaskUpdate, TaskResponse,
    MonitoringResultResponse, MessageResponse, PaginatedResponse,
)

router = APIRouter(prefix="/tasks", tags=["监测任务"])


@router.post("/create", response_model=TaskResponse, summary="创建监测任务")
async def create_task(
    body: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = MonitoringTask(
        user_id=current_user["user_id"],
        brand_name=body.brand_name,
        platform=body.platform,
        task_type=body.task_type,
        frequency=body.frequency,
        keywords=body.keywords,
        product_url=body.product_url,
        config=body.config,
    )
    db.add(task)
    await db.flush()
    return task


@router.get("/list", response_model=PaginatedResponse, summary="获取任务列表")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None, description="按状态过滤：active / paused / stopped"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(MonitoringTask).where(
        MonitoringTask.user_id == current_user["user_id"]
    )
    count_stmt = select(func.count()).select_from(MonitoringTask).where(
        MonitoringTask.user_id == current_user["user_id"]
    )

    if status:
        stmt = stmt.where(MonitoringTask.status == status)
        count_stmt = count_stmt.where(MonitoringTask.status == status)

    total = (await db.execute(count_stmt)).scalar()
    result = await db.execute(
        stmt.order_by(MonitoringTask.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tasks = result.scalars().all()

    return PaginatedResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{task_id}/update", response_model=TaskResponse, summary="更新任务")
async def update_task(
    task_id: int,
    body: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.id == task_id,
            MonitoringTask.user_id == current_user["user_id"],
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    return task


@router.delete("/{task_id}", response_model=MessageResponse, summary="删除任务")
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.id == task_id,
            MonitoringTask.user_id == current_user["user_id"],
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    await db.delete(task)
    return MessageResponse(message="任务已删除")


@router.get("/{task_id}/results", response_model=PaginatedResponse, summary="获取任务结果")
async def get_task_results(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 验证任务归属
    task_result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.id == task_id,
            MonitoringTask.user_id == current_user["user_id"],
        )
    )
    if not task_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="任务不存在")

    count_stmt = select(func.count()).select_from(MonitoringResult).where(
        MonitoringResult.task_id == task_id
    )
    total = (await db.execute(count_stmt)).scalar()

    stmt = (
        select(MonitoringResult)
        .where(MonitoringResult.task_id == task_id)
        .order_by(MonitoringResult.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    results = await db.execute(stmt)

    return PaginatedResponse(
        items=[MonitoringResultResponse.model_validate(r) for r in results.scalars().all()],
        total=total,
        page=page,
        page_size=page_size,
    )
