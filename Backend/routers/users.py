"""
用户路由 - /api/user/*

使用固定 Token 认证
"""
from fastapi import APIRouter, Depends

from schemas import UserResponse
from auth import get_current_user

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要在 Header 中携带 Authorization: Bearer <token>
    
    示例：Authorization: Bearer alice123
    """
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        created_at=current_user["created_at"],
    )
