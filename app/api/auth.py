"""
用户认证 API
- 注册 / 登录 / 获取当前用户信息
"""

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.task import User
from app.models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["认证"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(User).where(User.contact_email == body.contact_email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    user = User(
        company_name=body.company_name,
        contact_email=body.contact_email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"user_id": user.id, "email": user.contact_email})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.contact_email == body.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    token = create_access_token({"user_id": user.id, "email": user.contact_email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
