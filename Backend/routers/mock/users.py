"""
Mock 用户路由 - /mock/user/*

无需认证，直接返回默认用户
"""
from datetime import datetime
from fastapi import APIRouter

from schemas import UserResponse

router = APIRouter(prefix="/user", tags=["Mock-用户"])

# 默认用户（无需登录）
DEFAULT_USER = {
    "id": 1,
    "username": "alice",
    "created_at": datetime(2026, 1, 1, 10, 0, 0),
}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info():
    """
    [Mock] 获取当前用户信息
    
    无需认证，返回默认用户 alice
    """
    return UserResponse(
        id=DEFAULT_USER["id"],
        username=DEFAULT_USER["username"],
        created_at=DEFAULT_USER["created_at"],
    )
