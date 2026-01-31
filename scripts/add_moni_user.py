#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 moni 用户到数据库
"""
import sys
from pathlib import Path

# 添加 Backend 目录到路径
backend_dir = Path(__file__).parent.parent / "Backend"
sys.path.insert(0, str(backend_dir))

from datetime import datetime
from database import SessionLocal
from models import User

def add_moni_user():
    """添加 moni 用户"""
    # 确保数据库表存在
    init_db()
    
    db = SessionLocal()
    try:
        # 检查 moni 是否已存在
        existing = db.query(User).filter(User.username == "moni").first()
        if existing:
            print("[INFO] User 'moni' already exists")
            return
        
        # 创建 moni 用户
        moni = User(
            username="moni",
            password="moni123",
            created_at=datetime(2026, 1, 1, 10, 0, 0),
        )
        db.add(moni)
        db.commit()
        print("[OK] User 'moni' created successfully")
        print(f"     Username: moni")
        print(f"     Password: moni123")
        print(f"     Token: moni123")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_moni_user()
