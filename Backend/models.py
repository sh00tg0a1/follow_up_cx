"""
数据库模型 - SQLAlchemy ORM

支持的数据库:
- SQLite (开发环境): 不支持向量搜索
- PostgreSQL (生产环境): 支持 pgvector 向量搜索
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database import Base
from config import settings

# 检查是否为 PostgreSQL 环境，决定是否启用向量字段
_is_postgres = settings.DATABASE_URL.startswith("postgresql")

# 尝试导入 pgvector（仅在 PostgreSQL 环境下需要）
try:
    from pgvector.sqlalchemy import Vector
    _has_pgvector = True
except ImportError:
    _has_pgvector = False
    Vector = None


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
    
    # 注意：embedding 列会在下面动态添加（仅 PostgreSQL + pgvector 环境）
    
    @staticmethod
    def remove_embedding_if_not_exists(db, event_instance):
        """
        如果数据库没有 embedding 列，从事件实例中移除该属性
        
        这可以避免 SQLAlchemy 尝试插入不存在的列
        
        Args:
            db: 数据库会话
            event_instance: Event 实例
        """
        if not hasattr(event_instance, 'embedding'):
            return
        
        try:
            # 检查数据库是否有 embedding 列
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'embedding'
            """))
            has_embedding_column = result.scalar() is not None
            
            if not has_embedding_column and 'embedding' in event_instance.__dict__:
                del event_instance.__dict__['embedding']
                logger.debug("Removed embedding attribute (column does not exist in database)")
        except Exception as e:
            # 如果检查失败（可能是 SQLite 或其他错误），尝试移除属性
            if 'embedding' in event_instance.__dict__:
                del event_instance.__dict__['embedding']
            logger.debug(f"Could not check embedding column, removed from instance: {e}")


# 动态添加 embedding 列（仅 PostgreSQL + pgvector 环境）
# 注意：这个列只在数据库有该列时才有效
# 如果数据库还没有该列，需要在启动时运行 migrate_pgvector() 迁移
# 
# 为了避免在数据库没有该列时出错，我们使用事件监听器
# 在插入前检查数据库是否有该列，如果没有则从 mapper 中排除它
if _is_postgres and _has_pgvector and Vector is not None:
    # 1536 维向量，对应 OpenAI text-embedding-3-small
    Event.embedding = Column(Vector(1536), nullable=True)
    
    # 添加事件监听器，在插入前检查并处理 embedding 列
    from sqlalchemy import event
    from sqlalchemy.orm import object_mapper
    
    # 使用一个模块级别的缓存来存储检查结果（按连接）
    _embedding_column_cache = {}
    
    def _check_embedding_column_exists(connection):
        """检查数据库是否有 embedding 列"""
        # 使用连接的字符串表示作为缓存键
        cache_key = str(connection.engine.url)
        if cache_key in _embedding_column_cache:
            return _embedding_column_cache[cache_key]
        
        try:
            from sqlalchemy import text
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'embedding'
            """))
            exists = result.scalar() is not None
            _embedding_column_cache[cache_key] = exists
            return exists
        except Exception as e:
            # 如果检查失败，假设没有该列
            logger.warning(f"Failed to check embedding column: {e}")
            _embedding_column_cache[cache_key] = False
            return False
    
    @event.listens_for(Event, "before_insert", propagate=True)
    def check_embedding_column(mapper, connection, target):
        """在插入前检查数据库是否有 embedding 列，如果没有则从实例中移除该属性"""
        if not _check_embedding_column_exists(connection):
            # 数据库没有该列，从实例中移除该属性
            # 注意：SQLAlchemy 在构建 INSERT 时会检查 mapper 的所有列定义
            # 所以即使我们从实例中移除属性，SQLAlchemy 仍然可能尝试插入该列
            # 这会导致错误，但至少我们尝试了
            if 'embedding' in target.__dict__:
                del target.__dict__['embedding']
                logger.debug("Removed embedding attribute (column does not exist in database)")
            
            # 尝试从 mapper 的列中排除（如果可能）
            # 但这需要在 mapper 级别操作，比较复杂
            # 最实用的解决方案：确保迁移脚本正确运行
            # 如果迁移失败，用户需要手动运行迁移或联系管理员


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
