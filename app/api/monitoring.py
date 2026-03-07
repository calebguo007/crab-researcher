"""
监测执行 API
可由应用内调度器或外部系统调用，触发数据抓取
支持: 价格监测 / 促销监测 / 舆情分析 / 新品检测
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.task import MonitoringTask
from app.models.schemas import MonitoringTrigger, MessageResponse
from app.services.scraper import ScraperService
from app.services.notification import NotificationService

router = APIRouter(prefix="/monitoring", tags=["监测执行"])
logger = logging.getLogger(__name__)


@router.post("/price", response_model=MessageResponse, summary="执行价格监测")
async def monitor_price(
    body: MonitoringTrigger,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """手动触发价格监测任务"""
    tasks = await _get_active_tasks(db, current_user["user_id"], "price", body)

    scraper = ScraperService(db)
    notifier = NotificationService()
    alerts = []
    errors = []

    try:
        for task in tasks:
            try:
                result = await scraper.scrape_price(task)
                task.last_run_at = datetime.utcnow()

                if result.change_detected:
                    alerts.append(result)
                    # 尝试发送丰富的价格告警卡片
                    products = result.data.get("products", [])
                    if products and settings_have_feishu():
                        p = products[0]
                        await notifier.send_feishu_price_alert(
                            brand=task.brand_name,
                            product_name=p.get("name", ""),
                            old_price=0,  # 从change_summary解析
                            new_price=p.get("price", 0),
                            change_pct=0,
                            platform=task.platform,
                            url=p.get("url", ""),
                        )
                    else:
                        await notifier.send_alert(
                            title=f"价格变动 - {task.brand_name}",
                            content=result.change_summary or "检测到价格变化",
                            severity=result.severity,
                        )
            except Exception as e:
                logger.error(f"[Monitor] 价格监测失败 task_id={task.id}: {e}")
                errors.append({"task_id": task.id, "error": str(e)})
    finally:
        await scraper.close()
        await notifier.close()

    await db.commit()

    return MessageResponse(
        message=f"监测完成: {len(tasks)}个任务, {len(alerts)}个告警, {len(errors)}个失败",
        data={"total": len(tasks), "alerts": len(alerts), "errors": errors},
    )


@router.post("/promotion", response_model=MessageResponse, summary="执行促销监测")
async def monitor_promotion(
    body: MonitoringTrigger,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """手动触发促销监测（复用价格监测逻辑，关注促销价变化）"""
    tasks = await _get_active_tasks(db, current_user["user_id"], "promotion", body)

    scraper = ScraperService(db)
    notifier = NotificationService()
    alerts = []
    errors = []

    try:
        for task in tasks:
            try:
                result = await scraper.scrape_price(task)
                task.last_run_at = datetime.utcnow()

                if result.change_detected:
                    alerts.append(result)
                    await notifier.send_alert(
                        title=f"促销变动 - {task.brand_name}",
                        content=result.change_summary or "检测到促销价格变化",
                        severity=result.severity,
                    )
            except Exception as e:
                logger.error(f"[Monitor] 促销监测失败 task_id={task.id}: {e}")
                errors.append({"task_id": task.id, "error": str(e)})
    finally:
        await scraper.close()
        await notifier.close()

    await db.commit()

    return MessageResponse(
        message=f"促销监测完成: {len(tasks)}个任务, {len(alerts)}个告警, {len(errors)}个失败",
        data={"total": len(tasks), "alerts": len(alerts), "errors": errors},
    )


@router.post("/sentiment", response_model=MessageResponse, summary="执行舆情分析")
async def monitor_sentiment(
    body: MonitoringTrigger,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """手动触发舆情监测任务"""
    tasks = await _get_active_tasks(db, current_user["user_id"], "sentiment", body)

    scraper = ScraperService(db)
    notifier = NotificationService()
    alerts = []
    errors = []

    try:
        for task in tasks:
            try:
                result = await scraper.scrape_sentiment(task)
                task.last_run_at = datetime.utcnow()

                if result.change_detected:
                    alerts.append(result)
                    # 使用丰富的舆情告警卡片
                    data = result.data or {}
                    if settings_have_feishu():
                        await notifier.send_feishu_sentiment_alert(
                            brand=task.brand_name,
                            platform=task.platform,
                            sentiment_score=data.get("sentiment_score", 0.5),
                            mention_count=sum(
                                m.get("count", 0) for m in data.get("mentions", [])
                            ),
                            hot_topics=data.get("hot_topics", []),
                            analysis=data.get("analysis", ""),
                        )
                    else:
                        await notifier.send_alert(
                            title=f"舆情预警 - {task.brand_name}",
                            content=result.change_summary or "检测到舆情变化",
                            severity=result.severity,
                        )
            except Exception as e:
                logger.error(f"[Monitor] 舆情监测失败 task_id={task.id}: {e}")
                errors.append({"task_id": task.id, "error": str(e)})
    finally:
        await scraper.close()
        await notifier.close()

    await db.commit()

    return MessageResponse(
        message=f"舆情分析完成: {len(tasks)}个任务, {len(alerts)}个告警, {len(errors)}个失败",
        data={"total": len(tasks), "alerts": len(alerts), "errors": errors},
    )


@router.post("/new_product", response_model=MessageResponse, summary="检测新品")
async def monitor_new_product(
    body: MonitoringTrigger,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """手动触发新品监测任务"""
    tasks = await _get_active_tasks(db, current_user["user_id"], "new_product", body)

    scraper = ScraperService(db)
    notifier = NotificationService()
    alerts = []
    errors = []

    try:
        for task in tasks:
            try:
                result = await scraper.scrape_new_product(task)
                task.last_run_at = datetime.utcnow()

                if result.change_detected:
                    alerts.append(result)
                    new_products = (result.data or {}).get("new_products", [])
                    if settings_have_feishu() and new_products:
                        await notifier.send_feishu_new_product_alert(
                            brand=task.brand_name,
                            platform=task.platform,
                            new_products=new_products,
                        )
                    else:
                        await notifier.send_alert(
                            title=f"新品上市 - {task.brand_name}",
                            content=result.change_summary or "检测到新品",
                            severity=result.severity,
                        )
            except Exception as e:
                logger.error(f"[Monitor] 新品监测失败 task_id={task.id}: {e}")
                errors.append({"task_id": task.id, "error": str(e)})
    finally:
        await scraper.close()
        await notifier.close()

    await db.commit()

    return MessageResponse(
        message=f"新品检测完成: {len(tasks)}个任务, {len(alerts)}个告警, {len(errors)}个失败",
        data={"total": len(tasks), "alerts": len(alerts), "errors": errors},
    )


# ================================================================
# 工具函数
# ================================================================

async def _get_active_tasks(
    db: AsyncSession, user_id: int, task_type: str, trigger: MonitoringTrigger
) -> list[MonitoringTask]:
    """获取活跃的监测任务"""
    stmt = select(MonitoringTask).where(
        MonitoringTask.user_id == user_id,
        MonitoringTask.task_type == task_type,
        MonitoringTask.status == "active",
    )

    if trigger.task_id:
        stmt = stmt.where(MonitoringTask.id == trigger.task_id)
    if trigger.platform:
        stmt = stmt.where(MonitoringTask.platform == trigger.platform)

    result = await db.execute(stmt)
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(
            status_code=404,
            detail=f"没有找到活跃的 {task_type} 监测任务。请先创建一个任务。",
        )

    return list(tasks)


def settings_have_feishu() -> bool:
    """检查是否配置了飞书 Webhook"""
    from app.core.config import get_settings
    return bool(get_settings().FEISHU_WEBHOOK_URL)
