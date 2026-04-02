"""
CrabRes Growth Experiments API

用户可以：
- 查看当前实验和历史实验
- 手动提交一个已发布帖子的链接（触发追踪）
- 查看 action→result 数据
- 查看学到的增长规律
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.agent.memory.experiments import ExperimentTracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/growth", tags=["Growth Experiments"])


def _get_tracker(user_id: int) -> ExperimentTracker:
    return ExperimentTracker(base_dir=f".crabres/memory/{user_id}")


class SubmitActionRequest(BaseModel):
    url: str = Field(..., description="发布后的帖子/DM 链接")
    platform: str = Field("", description="reddit / x / linkedin / hackernews / email")
    action_type: str = Field("post", description="post / reply / dm / email")
    content_preview: str = Field("", description="发布内容摘要")
    experiment_id: str = Field("", description="关联的实验 ID（可选）")


class CreateExperimentRequest(BaseModel):
    goal: str = Field(..., description="实验目标，如 'Get 50 signups from Reddit'")
    hypothesis: str = Field("", description="假设")
    platform: str = Field("", description="主要平台")


@router.post("/actions/submit")
async def submit_action(
    req: SubmitActionRequest,
    current_user: dict = Depends(get_current_user),
):
    """用户手动提交一个已发布的帖子链接，触发效果追踪"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)

    # 自动检测平台
    platform = req.platform
    if not platform and req.url:
        url_lower = req.url.lower()
        if "reddit.com" in url_lower:
            platform = "reddit"
        elif "x.com" in url_lower or "twitter.com" in url_lower:
            platform = "x"
        elif "linkedin.com" in url_lower:
            platform = "linkedin"
        elif "news.ycombinator.com" in url_lower:
            platform = "hackernews"
        elif "producthunt.com" in url_lower:
            platform = "producthunt"

    action = await tracker.record_action(
        platform=platform,
        action_type=req.action_type,
        url=req.url,
        content_preview=req.content_preview,
        experiment_id=req.experiment_id,
    )

    return {"action_id": action.id, "platform": platform, "status": action.status}


@router.get("/actions")
async def list_actions(
    experiment_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """查看所有行动记录"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    actions = await tracker.get_actions(experiment_id=experiment_id, status=status)
    return {"actions": actions}


@router.get("/actions/{action_id}/results")
async def get_action_results(
    action_id: str,
    current_user: dict = Depends(get_current_user),
):
    """查看某个行动的效果数据"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    results = await tracker.get_results(action_id=action_id)
    return {"results": results}


@router.post("/experiments")
async def create_experiment(
    req: CreateExperimentRequest,
    current_user: dict = Depends(get_current_user),
):
    """创建一个新实验"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    exp = await tracker.create_experiment(
        goal=req.goal,
        hypothesis=req.hypothesis,
        platform=req.platform,
    )
    return {"experiment_id": exp.id, "goal": exp.goal}


@router.get("/experiments")
async def list_experiments(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """查看所有实验"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    experiments = await tracker.get_experiments(status=status)
    return {"experiments": experiments}


@router.get("/experiments/summary")
async def experiments_summary(
    current_user: dict = Depends(get_current_user),
):
    """实验追踪总览"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    return await tracker.get_summary()


@router.get("/learnings")
async def get_learnings(
    current_user: dict = Depends(get_current_user),
):
    """查看从实验中学到的增长规律"""
    user_id = current_user.get("user_id", 0)
    tracker = _get_tracker(user_id)
    learnings = await tracker.get_learnings()
    return {"learnings": learnings}
