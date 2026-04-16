"""
CrabRes 记忆持久化 — PostgreSQL ORM 模型

替代文件系统的 .crabres/memory/{user_id}/{category}/{key}.json
部署重启后记忆不丢失。
"""

from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, JSON,
    Index,
)

from app.core.database import Base


class MemoryRecord(Base):
    """
    记忆记录 — 替代文件系统的 .crabres/memory/{user_id}/{category}/{key}.json
    
    每条记忆是一个 category + key 的唯一组合。
    支持版本追踪、内容 hash 去重、JSON 数据存储。
    """
    __tablename__ = "memory_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, comment="用户 ID（字符串，兼容 'global'）")
    category = Column(String(50), nullable=False, comment="记忆类别: product/goals/research/strategy/execution/feedback/journal/knowledge")
    key = Column(String(255), nullable=False, comment="记忆 key（如 product_info, loop_state_xxx）")
    
    data = Column(JSON, nullable=False, default=dict, comment="记忆内容（完整 JSON）")
    version = Column(Integer, default=1, comment="版本号，每次更新递增")
    content_hash = Column(String(20), default="", comment="内容 hash，用于去重")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_memory_records_user_cat_key", "user_id", "category", "key", unique=True),
        Index("ix_memory_records_user_cat", "user_id", "category"),
    )


class JournalEntry(Base):
    """
    增长日志 — 替代文件系统的 .crabres/memory/{user_id}/journal/{date}.jsonl
    
    每条是一个 append-only 的日志条目（Write-Ahead Log 模式）。
    """
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False)
    date = Column(String(10), nullable=False, comment="YYYY-MM-DD")
    data = Column(JSON, nullable=False, default=dict, comment="日志条目内容")
    timestamp = Column(Float, nullable=False, comment="Unix timestamp")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_journal_entries_user_date", "user_id", "date"),
    )
