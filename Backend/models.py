"""
数据库模型 - SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 存储明文密码（固定 Token 方案）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")


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
    
    # 状态
    is_followed = Column(Boolean, default=False, nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="events")
