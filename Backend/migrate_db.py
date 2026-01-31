"""
数据库迁移脚本 - 添加缺失的列和扩展

用于修复旧数据库表结构，添加新字段。
支持的迁移：
- source_thumbnail 列
- conversations 表
- pgvector 扩展和 embedding 列（仅 PostgreSQL）
"""
from sqlalchemy import text
from database import engine, SessionLocal
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# 检查是否为 PostgreSQL
def is_postgres() -> bool:
    return settings.DATABASE_URL.startswith("postgresql")


def migrate_events_table():
    """
    迁移 events 表，添加缺失的列
    
    这个函数是幂等的，可以安全地多次运行。
    如果列已存在，不会重复添加。
    """
    db = SessionLocal()
    try:
        # 检查 events 表是否存在
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='events'
        """))
        events_table_exists = result.scalar() is not None
        
        if events_table_exists:
            # 检查 source_thumbnail 列是否存在（通过尝试查询来判断）
            try:
                db.execute(text("SELECT source_thumbnail FROM events LIMIT 1"))
                logger.debug("source_thumbnail column already exists")
            except Exception:
                # 列不存在，需要添加
                logger.info("Adding source_thumbnail column to events table...")
                db.execute(text("""
                    ALTER TABLE events 
                    ADD COLUMN source_thumbnail TEXT NULL
                """))
                db.commit()
                logger.info("Successfully added source_thumbnail column")
        else:
            logger.debug("events table does not exist yet, will be created by init_db()")
        
        # 检查 conversations 表是否存在
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversations'
        """))
        table_exists = result.scalar() is not None
        
        if not table_exists:
            logger.info("Creating conversations table...")
            from models import Conversation
            from database import Base
            Base.metadata.create_all(bind=engine, tables=[Conversation.__table__])
            logger.info("Successfully created conversations table")
        else:
            logger.debug("conversations table already exists")
            
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def migrate_pgvector():
    """
    迁移 PostgreSQL 数据库，添加 pgvector 支持
    
    仅在 PostgreSQL 环境下运行。
    这个函数是幂等的，可以安全地多次运行。
    """
    if not is_postgres():
        logger.debug("Skipping pgvector migration (not PostgreSQL)")
        return
    
    db = SessionLocal()
    try:
        # 1. 启用 pgvector 扩展
        logger.info("Enabling pgvector extension...")
        try:
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            db.commit()
            logger.info("pgvector extension enabled")
        except Exception as e:
            logger.warning(f"Failed to enable pgvector extension (may already exist or not installed): {e}")
            db.rollback()
        
        # 2. 检查 embedding 列是否存在
        try:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'embedding'
            """))
            embedding_exists = result.scalar() is not None
            
            if not embedding_exists:
                logger.info("Adding embedding column to events table...")
                try:
                    db.execute(text("""
                        ALTER TABLE events 
                        ADD COLUMN embedding vector(1536)
                    """))
                    db.commit()
                    logger.info("Successfully added embedding column")
                except Exception as alter_error:
                    logger.error(f"Failed to add embedding column: {alter_error}")
                    db.rollback()
                    # 如果添加列失败，记录错误但不抛出异常
                    # 这样应用仍然可以启动，但 embedding 功能不可用
                    logger.warning("Embedding column not added. Vector search will not be available.")
            else:
                logger.debug("embedding column already exists")
        except Exception as e:
            logger.error(f"Failed to check/add embedding column: {e}", exc_info=True)
            db.rollback()
            # 不抛出异常，允许应用继续启动
        
        # 3. 创建向量索引（使用 IVFFlat 索引加速搜索）
        try:
            # 检查索引是否存在
            result = db.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'events' AND indexname = 'events_embedding_idx'
            """))
            index_exists = result.scalar() is not None
            
            if not index_exists:
                # 只有当有足够数据时才创建 IVFFlat 索引
                # 先检查是否有数据
                result = db.execute(text("""
                    SELECT COUNT(*) FROM events WHERE embedding IS NOT NULL
                """))
                count = result.scalar() or 0
                
                if count >= 100:
                    # 有足够数据，创建 IVFFlat 索引
                    logger.info("Creating IVFFlat index on embedding column...")
                    db.execute(text("""
                        CREATE INDEX events_embedding_idx 
                        ON events 
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100)
                    """))
                    db.commit()
                    logger.info("Successfully created embedding index")
                else:
                    logger.info(f"Skipping index creation (only {count} events with embeddings, need 100+)")
            else:
                logger.debug("embedding index already exists")
        except Exception as e:
            logger.warning(f"Failed to create embedding index: {e}")
            db.rollback()
            
    except Exception as e:
        logger.error(f"pgvector migration error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("[MIGRATE] Starting database migration...")
    try:
        migrate_events_table()
        migrate_pgvector()
        print("[OK] Database migration completed successfully")
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()
