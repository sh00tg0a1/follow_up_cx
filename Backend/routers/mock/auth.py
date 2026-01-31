"""
Mock 认证路由 - /mock/auth/*

无需认证，直接返回固定 Token
"""
from fastapi import APIRouter, HTTPException, status

from schemas import LoginRequest, LoginResponse, UserResponse
from mock_data import get_user_by_username

router = APIRouter(prefix="/auth", tags=["Mock-认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    [Mock] 用户登录

    使用预置用户账号登录，Token = 密码

    预置用户：
    - alice / alice123 → Token: alice123
    - bob / bob123 → Token: bob123
    - jane / jane123 → Token: jane123
    - xiao / xiao123 → Token: xiao123
    """
    user = get_user_by_username(request.username)

    if user is None or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Token = 密码
    access_token = request.password

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            created_at=user["created_at"],
        ),
    )
