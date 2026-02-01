"""
数据库模型 - SQLAlchemy ORM

支持的数据库:
- SQLite (开发环境)
- PostgreSQL (生产环境)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database import Base
from logging_config import get_logger

logger = get_logger(__name__)


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 存储明文密码（固定 Token 方案）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Event(Base):
    """活动模型"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 活动基本信息
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    location = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # 来源信息
    source_type = Column(String(50), default="manual", nullable=False)  # text/image/voice/manual
    source_content = Column(Text, nullable=True)  # 原始输入内容
    source_thumbnail = Column(Text, nullable=True)  # 图片来源的缩略图（base64 编码，约 200x200）
    
    # 状态
    is_followed = Column(Boolean, default=False, nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="events")


class Conversation(Base):
    """对话模型 - 存储用户与 Agent 的对话历史"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 对话历史（JSON 格式存储消息列表）
    messages = Column(JSON, default=list, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="conversations")
