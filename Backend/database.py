"""
数据库连接和会话管理

支持的数据库:
- SQLite (开发环境): DATABASE_URL=sqlite:///./followup.db
- PostgreSQL (生产环境): DATABASE_URL=postgresql://user:password@host:port/database
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)


def _get_engine_kwargs():
    """根据数据库类型返回合适的引擎配置"""
    db_url = settings.DATABASE_URL
    
    if db_url.startswith("sqlite"):
        # SQLite 配置
        return {
            "connect_args": {"check_same_thread": False},
            "echo": False,
        }
    elif db_url.startswith("postgresql"):
        # PostgreSQL 配置 - 生产环境连接池优化
        return {
            "pool_size": 5,           # 连接池大小
            "max_overflow": 10,       # 超出 pool_size 后最多可以创建的连接数
            "pool_timeout": 30,       # 获取连接的超时时间（秒）
            "pool_recycle": 1800,     # 连接回收时间（秒），防止数据库断开空闲连接
            "pool_pre_ping": True,    # 每次使用连接前先 ping，确保连接有效
            "echo": False,
        }
    else:
        # 其他数据库使用默认配置
        return {"echo": False}


# 创建数据库引擎
db_type = "PostgreSQL" if settings.DATABASE_URL.startswith("postgresql") else "SQLite"
logger.info(f"Initializing database ({db_type}): {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
engine = create_engine(settings.DATABASE_URL, **_get_engine_kwargs())

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    数据库会话依赖注入
    
    使用示例：
    @router.get("/items")
    async def get_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建表）"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
