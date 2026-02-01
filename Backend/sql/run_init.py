#!/usr/bin/env python3
"""
数据库初始化脚本执行器

自动检测数据库类型并执行相应的 SQL 初始化脚本。
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径，以便导入配置
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from database import engine
from logging_config import get_logger

logger = get_logger(__name__)


def is_postgres() -> bool:
    """检查是否使用 PostgreSQL"""
    return settings.DATABASE_URL.startswith("postgresql")


def execute_sql_file(db_url: str, sql_file: Path):
    """执行 SQL 文件"""
    if not sql_file.exists():
        logger.error(f"SQL 文件不存在: {sql_file}")
        return False
    
    logger.info(f"执行 SQL 脚本: {sql_file}")
    
    if is_postgres():
        # PostgreSQL: 使用 psycopg2
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # 解析数据库 URL
            parsed = urlparse(db_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # 去掉开头的 '/'
                user=parsed.username,
                password=parsed.password,
            )
            conn.autocommit = False
            
            cursor = conn.cursor()
            
            # 读取并执行 SQL 文件
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            try:
                cursor.execute(sql_content)
                conn.commit()
                logger.info("✅ SQL 脚本执行成功")
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ SQL 脚本执行失败: {e}")
                return False
            finally:
                cursor.close()
                conn.close()
                
        except ImportError:
            logger.error("❌ 需要安装 psycopg2: pip install psycopg2-binary")
            return False
        except Exception as e:
            logger.error(f"❌ 连接数据库失败: {e}")
            return False
    else:
        # SQLite: 使用 sqlite3
        try:
            import sqlite3
            
            # 从 URL 提取数据库文件路径
            # sqlite:///./followup.db -> ./followup.db
            db_path = db_url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 读取并执行 SQL 文件
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            try:
                # SQLite 需要逐句执行（不支持多语句）
                statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
                
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                
                conn.commit()
                logger.info("✅ SQL 脚本执行成功")
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ SQL 脚本执行失败: {e}")
                return False
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ 执行 SQLite 脚本失败: {e}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("数据库初始化脚本执行器")
    print("=" * 60)
    
    db_url = settings.DATABASE_URL
    db_type = "PostgreSQL" if is_postgres() else "SQLite"
    
    print(f"数据库类型: {db_type}")
    print(f"数据库 URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()
    
    # 确认操作
    print("⚠️  警告：此操作会删除所有现有数据！")
    response = input("确认继续？(yes/no): ").strip().lower()
    
    if response != 'yes':
        print("操作已取消")
        return False
    
    # 确定 SQL 文件
    script_dir = Path(__file__).parent
    if is_postgres():
        sql_file = script_dir / "init_postgresql.sql"
    else:
        sql_file = script_dir / "init_sqlite.sql"
    
    # 执行 SQL 脚本
    success = execute_sql_file(db_url, sql_file)
    
    if success:
        print()
        print("=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ 数据库初始化失败！")
        print("=" * 60)
        print("请检查错误信息并手动执行 SQL 脚本")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
