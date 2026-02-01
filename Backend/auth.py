"""
Authentication - Fixed Token Verification (Token = Password)

Query user from database and verify Token
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models import User
from logging_config import get_logger

logger = get_logger(__name__)

# Bearer Token 安全模式
security = HTTPBearer(auto_error=False)


def verify_token(token: str, db: Session) -> Optional[User]:
    """
    Verify fixed Token (Token = Password)

    Supported Tokens:
    - alice123 -> alice user
    - bob123 -> bob user
    - jane123 -> jane user
    - xiao123 -> xiao user
    - moni123 -> moni user
    """
    # Find user from database matching password
    user = db.query(User).filter(User.password == token).first()
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    依赖注入：获取当前登录用户

    使用固定 Token 验证：
    - Authorization: Bearer alice123
    - Authorization: Bearer bob123
    """
    if credentials is None:
        logger.warning("Authentication failed: no credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Use 'Authorization: Bearer alice123'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user = verify_token(token, db)

    if user is None:
        logger.warning(f"Authentication failed: invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Valid tokens: alice123, bob123, jane123, xiao123, moni123",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"User authenticated: {user.username} (id={user.id})")
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Optional authentication: Verify if Token is provided, otherwise return None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return verify_token(token, db)
