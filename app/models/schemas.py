"""
Pydantic Schemas - 请求/响应数据验证
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ========== 用户 ==========

class UserCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255, description="企业名称")
    contact_email: EmailStr = Field(..., description="联系邮箱")
    password: str = Field(..., min_length=6, description="密码")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    company_name: str
    contact_email: str
    subscription_plan: str
    monthly_budget: float
    monthly_token_used: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ========== 监测任务 ==========

class TaskCreate(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=255, description="品牌名称，用户自由输入")
    platform: str = Field(..., min_length=1, max_length=100, description="平台名称，如：jd / taobao / tmall / pdd / xiaohongshu / douyin / weibo 等")
    task_type: str = Field(..., min_length=1, max_length=50, description="任务类型，如：price / promotion / sentiment / new_product")
    frequency: str = Field(default="daily", min_length=1, max_length=20, description="执行频率：hourly / daily / weekly")
    keywords: list[str] = Field(default_factory=list, description="搜索关键词，用户手动输入")
    product_url: Optional[str] = Field(None, max_length=500, description="商品链接（可选，直接监测指定商品）")
    config: dict = Field(default_factory=dict, description="任务配置")


class TaskUpdate(BaseModel):
    brand_name: Optional[str] = None
    platform: Optional[str] = None
    task_type: Optional[str] = None
    frequency: Optional[str] = None
    status: Optional[str] = Field(None, description="状态：active / paused / stopped")
    keywords: Optional[list[str]] = None
    product_url: Optional[str] = None
    config: Optional[dict] = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    brand_name: str
    platform: str
    task_type: str
    frequency: str
    status: str
    keywords: list = Field(default_factory=list)
    product_url: Optional[str] = None
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    config: dict
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 监测结果 ==========

class MonitoringResultResponse(BaseModel):
    id: int
    task_id: int
    data: dict
    change_detected: bool
    change_type: Optional[str]
    change_summary: Optional[str]
    severity: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MonitoringTrigger(BaseModel):
    task_id: Optional[int] = None
    platform: Optional[str] = None
    keywords: Optional[list[str]] = None
    product_url: Optional[str] = Field(None, description="指定商品URL直接监测")


# ========== 报告 ==========

class ReportGenerate(BaseModel):
    report_type: str = Field(..., min_length=1, max_length=50, description="报告类型，如：daily / weekly / monthly / custom")
    title: Optional[str] = None
    brands: list[str] = Field(default_factory=list, description="要分析的品牌列表，用户手动输入")
    custom_prompt: Optional[str] = Field(None, description="自定义分析指令")


class ReportResponse(BaseModel):
    id: int
    user_id: int
    report_type: str
    title: str
    content: str
    model_used: Optional[str]
    token_cost: float
    generated_at: datetime

    model_config = {"from_attributes": True}


# ========== RAG ==========

class RAGUpload(BaseModel):
    doc_type: str = Field(..., min_length=1, max_length=50, description="文档类型，如：report / sop / persona / industry_data / news / review 等")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, description="文档内容")
    metadata: dict = Field(default_factory=dict)


class RAGSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="搜索关键词")
    top_k: int = Field(default=5, ge=1, le=20, description="返回数量")
    doc_type: Optional[str] = None
    mode: str = Field(default="vector", description="检索模式：vector / keyword / hybrid")
    vector_top_k: int = Field(default=12, ge=1, le=50, description="向量召回数量(混合检索用)")
    keyword_top_k: int = Field(default=12, ge=1, le=50, description="关键词召回数量(混合检索用)")


class RAGDocumentResponse(BaseModel):
    id: int
    doc_type: str
    title: str
    content: str
    metadata: Optional[dict] = Field(None, alias="metadata_")
    similarity: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# ========== 通用 ==========

class MessageResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int


# ========== 用户产品 ==========

class UserProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, description="你的产品名称")
    industry: str = Field(..., min_length=1, max_length=100, description="所属行业，如：消费电子")
    category: str = Field(..., min_length=1, max_length=100, description="细分品类，如：户外蓝牙音箱")
    keywords: list[str] = Field(default_factory=list, description="搜索关键词，如 ['蓝牙音箱', '户外音箱']")
    price_range: dict = Field(default_factory=dict, description="目标价格带 {'min': 200, 'max': 3000}")
    platforms: list[str] = Field(default_factory=lambda: ["jd", "tmall"], description="要监测的平台")


class UserProductResponse(BaseModel):
    id: int
    user_id: int
    product_name: str
    industry: str
    category: str
    keywords: list
    price_range: dict
    platforms: list
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 竞品管理 ==========

class CompetitorProductCreate(BaseModel):
    """用户手动添加竞品"""
    brand: str = Field(..., min_length=1, max_length=100, description="竞品品牌名称，用户自由输入")
    product_name: str = Field(..., min_length=1, max_length=255, description="竞品产品名称")
    platform: Optional[str] = Field(None, max_length=50, description="平台，如 jd / tmall / pdd 等")
    price: Optional[float] = Field(None, ge=0, description="当前价格")
    promo_price: Optional[float] = Field(None, ge=0, description="促销价")
    specs: dict = Field(default_factory=dict, description="规格参数，如 {'颜色': '黑色', '功率': '30W'}")
    features: list[str] = Field(default_factory=list, description="功能特点")
    product_url: Optional[str] = Field(None, max_length=500, description="商品链接")


class CompetitorProductUpdate(BaseModel):
    """更新竞品信息"""
    brand: Optional[str] = Field(None, max_length=100)
    product_name: Optional[str] = Field(None, max_length=255)
    platform: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    promo_price: Optional[float] = Field(None, ge=0)
    specs: Optional[dict] = None
    features: Optional[list[str]] = None
    product_url: Optional[str] = Field(None, max_length=500)


class CompetitorProductResponse(BaseModel):
    id: int
    user_product_id: int
    brand: str
    product_name: str
    platform: Optional[str]
    price: Optional[float]
    promo_price: Optional[float]
    specs: dict
    features: list
    product_url: Optional[str]
    last_checked: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class CompetitorDiscoveryResponse(BaseModel):
    """LLM 自动发现的竞品候选（可选功能）"""
    id: int
    user_product_id: int
    brand: str
    product_name: str
    platform: Optional[str]
    price: Optional[float]
    monthly_sales: Optional[int]
    product_url: Optional[str]
    discovery_reason: Optional[str]
    relevance_score: float
    status: str
    discovered_at: datetime

    model_config = {"from_attributes": True}


class CompetitorConfirmAction(BaseModel):
    action: str = Field(..., pattern="^(confirm|reject)$", description="confirm 或 reject")
