"""
小蟹研究员 - FastAPI 应用入口
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api import auth, tasks, monitoring, reports, rag, system, competitors
from app.services.scheduler import MonitoringScheduler

settings = get_settings()

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时创建表+启动调度器，关闭时清理连接"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = MonitoringScheduler()
    scheduler.start()
    app.state.monitoring_scheduler = scheduler

    logging.info("🦀 小蟹研究员启动成功!")
    yield

    scheduler.shutdown()
    await engine.dispose()
    logging.info("🦀 小蟹研究员已关闭")


app = FastAPI(
    title="🦀 小蟹研究员 API",
    description="B2B AI市场调研自动化助手 - 24/7自动监测竞品，主动汇报",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(rag.router, prefix=settings.API_PREFIX)
app.include_router(system.router, prefix=settings.API_PREFIX)
app.include_router(competitors.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["首页"])
async def root():
    return {
        "name": "🦀 小蟹研究员",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }
