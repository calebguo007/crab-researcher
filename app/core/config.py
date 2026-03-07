"""
应用配置管理
所有配置项通过环境变量注入，支持 .env 文件
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ========== 应用基础 ==========
    APP_NAME: str = "小蟹研究员"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # ========== 数据库 ==========
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/crab_researcher"
    DATABASE_URL_SYNC: str = "postgresql://postgres:password@localhost:5432/crab_researcher"
    REDIS_URL: str = "redis://localhost:6379"

    # ========== LLM API Keys ==========
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    MOONSHOT_API_KEY: Optional[str] = None

    # ========== 消息平台 ==========
    WECOM_WEBHOOK_URL: Optional[str] = None
    FEISHU_WEBHOOK_URL: Optional[str] = None
    FEISHU_WEBHOOK_SECRET: Optional[str] = None

    # ========== 安全 ==========
    JWT_SECRET: str = "change-me-in-production"
    API_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # ========== 成本控制 ==========
    MONTHLY_BUDGET_PER_USER: float = 100.0  # 人民币
    TOKEN_USAGE_ALERT_THRESHOLD: float = 0.8  # 80%时告警

    # ========== 爬虫安全白名单 ==========
    ALLOWED_SCRAPE_DOMAINS: list[str] = [
        "taobao.com",
        "tmall.com",
        "jd.com",
        "pdd.com",
        "1688.com",
        "xiaohongshu.com",
        "douyin.com",
        "weibo.com",
    ]

    # ========== 允许的操作白名单 ==========
    ALLOWED_ACTIONS: list[str] = [
        "fetch_data",
        "generate_report",
        "send_notification",
        "search_rag",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
