"""
Authentication - 简单的固定 Token 验证（开发用）
"""
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mock_data import get_user_by_username, USERS

# Bearer Token 安全模式
security = HTTPBearer(auto_error=False)

# 固定 Token 映射（用户名 -> token）
# Token 格式：用户名 + "123"
FIXED_TOKENS = {
    "alice123": "alice",
    "bob123": "bob",
    "jane123": "jane",
    "xiao123": "xiao",
}


def verify_token(token: str) -> Optional[dict]:
    """
    验证固定 Token
    
    支持的 Token：
    - alice123 -> alice 用户
    - bob123 -> bob 用户
    - jane123 -> jane 用户
    - xiao123 -> xiao 用户
    """
    username = FIXED_TOKENS.get(token)
    if username:
        return get_user_by_username(username)
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    依赖注入：获取当前登录用户
    
    使用固定 Token 验证：
    - Authorization: Bearer alice123
    - Authorization: Bearer bob123
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Use 'Authorization: Bearer alice123'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = verify_token(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Valid tokens: alice123, bob123, jane123, xiao123",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """
    可选认证：如果提供了 Token 则验证，否则返回 None
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    return verify_token(token)
