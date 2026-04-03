"""
CrabRes Growth System — PostgreSQL 数据模型

这是增长操作系统的数据骨架。
所有核心数据（行动、结果、策略、学习、Playbook）全部存 PostgreSQL。

设计原则：
1. 每个 action 必须有 result — 没有 result 的 action 是浪费
2. 每个 result 有自动评分 — 系统知道什么是"好"
3. learnings 从 action→result 自动提取 — 越用越准
4. 跨用户可聚合 — 匿名化后的数据是壁垒
5. channel_weights 动态计算 — 基于真实数据调整策略
"""

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    Index, Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ===== 增长行动 =====

class GrowthAction(Base):
    """
    增长行动记录 — 用户做的每一件增长动作
    
    例：发了一条 Reddit 帖子、DM 了一个博主、投了一条广告
    """
    __tablename__ = "growth_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(20), unique=True, nullable=False, comment="业务 ID: act-xxxx")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 核心字段
    date = Column(String(10), nullable=False, comment="YYYY-MM-DD")
    platform = Column(String(30), nullable=False, comment="reddit/x/xiaohongshu/linkedin/email/other")
    action_type = Column(String(30), nullable=False, comment="post/reply/dm/email/thread/outreach/other")
    description = Column(Text, nullable=False, comment="一句话描述做了什么")
    
    # 详情
    content_preview = Column(Text, default="", comment="发布内容摘要（前 500 字）")
    url = Column(String(1000), default="", comment="发布后的链接")
    target = Column(String(255), default="", comment="目标（r/SaaS, @某博主）")
    time_spent_min = Column(Integer, default=0, comment="花了多少分钟")
    
    # 关联
    experiment_id = Column(Integer, ForeignKey("growth_experiments.id"), nullable=True)
    playbook_id = Column(String(20), nullable=True, comment="关联的 playbook ID")
    
    # 状态
    status = Column(String(20), default="posted", comment="pending/posted/tracked/failed")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    results = relationship("GrowthResult", back_populates="action", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_growth_actions_user_date", "user_id", "date"),
        Index("ix_growth_actions_platform", "user_id", "platform"),
    )


class GrowthResult(Base):
    """
    行动结果 — 每个 action 的效果追踪
    
    自动评分：verdict (great/good/mediocre/poor) + score (0-100)
    """
    __tablename__ = "growth_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(Integer, ForeignKey("growth_actions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(String(10), nullable=False)
    metrics = Column(JSON, default=dict, comment='{"likes": 10, "upvotes": 50, "comments": 3}')
    
    # 自动评分
    verdict = Column(String(20), default="pending", comment="great/good/mediocre/poor/pending")
    score = Column(Integer, default=0, comment="0-100 综合评分")
    
    # 来源
    auto_tracked = Column(Boolean, default=False, comment="自动追踪 vs 手动填写")
    notes = Column(Text, default="", comment="判定原因或用户备注")
    
    tracked_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    action = relationship("GrowthAction", back_populates="results")

    __table_args__ = (
        Index("ix_growth_results_user_date", "user_id", "date"),
        Index("ix_growth_results_verdict", "user_id", "verdict"),
    )


# ===== 增长实验 =====

class GrowthExperiment(Base):
    """
    增长实验 — 一批有目标的行动
    
    例："用数字标题在 r/SaaS 发 5 篇帖子，验证是否比叙事标题效果好"
    """
    __tablename__ = "growth_experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(20), unique=True, nullable=False, comment="业务 ID: exp-xxxx")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    goal = Column(Text, nullable=False, comment="实验目标")
    hypothesis = Column(Text, default="", comment="假设")
    platform = Column(String(30), default="", comment="主要平台")
    
    status = Column(String(20), default="active", comment="active/completed/abandoned")
    conclusion = Column(Text, default="", comment="实验结论")
    learnings = Column(JSON, default=list, comment="提取的规律列表")
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_growth_experiments_user_status", "user_id", "status"),
    )


# ===== 增长规律 =====

class GrowthLearning(Base):
    """
    从实验数据中提取的增长规律
    
    例："Reddit 数字标题帖 vs 叙事帖转化率高 3.5x"
    这是壁垒：Google 搜不到、AI 猜不出的真实坑位数据
    """
    __tablename__ = "growth_learnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    learning = Column(Text, nullable=False, comment="规律描述")
    platform = Column(String(30), default="", comment="适用平台")
    confidence = Column(Float, default=0.5, comment="置信度 0-1（数据点越多越高）")
    data_points = Column(Integer, default=1, comment="支撑这条规律的数据点数量")
    
    experiment_id = Column(Integer, ForeignKey("growth_experiments.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_growth_learnings_user_platform", "user_id", "platform"),
    )


# ===== 增长策略 =====

class GrowthStrategy(Base):
    """
    每日策略记录
    
    明天要做什么 + 为什么这么安排 + 基于什么数据
    """
    __tablename__ = "growth_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(String(10), nullable=False, comment="YYYY-MM-DD（这是哪天的策略）")
    actions = Column(JSON, default=list, comment="今天要做的事列表")
    reasoning = Column(Text, default="", comment="为什么这么安排")
    based_on = Column(JSON, default=list, comment="基于哪些数据/规律")
    
    generated_by = Column(String(20), default="rules", comment="rules/ai/manual")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_growth_strategies_user_date", "user_id", "date"),
    )


# ===== 渠道权重 =====

class ChannelWeight(Base):
    """
    渠道权重快照 — 基于真实数据动态计算
    
    每天计算一次，记录下来。可以看到权重随时间的变化趋势。
    """
    __tablename__ = "channel_weights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(String(10), nullable=False)
    platform = Column(String(30), nullable=False)
    weight = Column(Float, nullable=False, comment="0-1 权重")
    avg_score = Column(Float, default=0, comment="该渠道平均分")
    action_count = Column(Integer, default=0, comment="该渠道总行动数")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_channel_weights_user_date", "user_id", "date"),
    )


# ===== Playbook =====

class PlaybookRecord(Base):
    """
    Playbook 执行记录
    
    phases 和 steps 存在 JSON 字段中（结构灵活）
    """
    __tablename__ = "playbook_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(20), unique=True, nullable=False, comment="业务 ID: pb-xxxx")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    suitable_for = Column(Text, default="")
    
    phases = Column(JSON, default=list, comment="Phase→Step 完整结构")
    total_budget = Column(String(50), default="")
    expected_timeline = Column(String(100), default="")
    expected_results = Column(Text, default="")
    risk_factors = Column(JSON, default=list)
    
    status = Column(String(20), default="draft", comment="draft/active/completed/abandoned")
    priority = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_playbook_records_user_status", "user_id", "status"),
    )


# ===== Agent 会话 =====

class AgentSession(Base):
    """
    Agent 会话记录 — 替代文件系统的 loop_state.json
    """
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    phase = Column(String(30), default="intake")
    turn_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    is_waiting = Column(Boolean, default=False)
    
    # 大字段存 JSON
    message_history = Column(JSON, default=list, comment="对话历史")
    expert_outputs = Column(JSON, default=dict, comment="专家输出缓存")
    pending_tasks = Column(JSON, default=list, comment="待用户完成的任务")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_agent_sessions_user", "user_id"),
    )
