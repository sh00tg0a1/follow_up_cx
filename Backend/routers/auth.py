"""
认证路由 - /api/auth/*

使用固定 Token 认证（Token = 密码）
"""
from fastapi import APIRouter, HTTPException, status

from schemas import LoginRequest, LoginResponse, UserResponse
from mock_data import get_user_by_username

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    验证用户名和密码，返回 Token（Token = 密码）
    
    预置用户：
    - alice / alice123
    - bob / bob123
    - jane / jane123
    - xiao / xiao123
    """
    user = get_user_by_username(request.username)
    
    if user is None or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Token 就是密码
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
