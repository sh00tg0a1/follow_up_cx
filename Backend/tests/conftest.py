"""
Pytest 配置和共享 fixtures
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 设置测试环境变量（在导入 app 之前）
os.environ["TESTING"] = "1"

# 使用内存 SQLite 数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 创建测试专用的 Base（绑定到 test_engine）
TestBase = declarative_base()

# 导入主应用（在创建 TestBase 之后）
from main import app
from database import get_db

# 导入模型
from models import User, Event

# 将模型绑定到 TestBase（而不是主应用的 Base）
# 注意：需要重新创建表结构
User.__table__.metadata = TestBase.metadata
Event.__table__.metadata = TestBase.metadata


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 先清理旧表（如果存在）
    Base.metadata.drop_all(bind=test_engine)
    # 创建表
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    
    # 创建测试用户
    from models import User
    from datetime import datetime
    
    users_data = [
        {"username": "alice", "password": "alice123"},
        {"username": "bob", "password": "bob123"},
        {"username": "jane", "password": "jane123"},
        {"username": "xiao", "password": "xiao123"},
        {"username": "moni", "password": "moni123"},
    ]
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            password=user_data["password"],
            created_at=datetime(2026, 1, 1, 10, 0, 0),
        )
        db.add(user)
    db.commit()
    # 刷新以确保数据已写入
    db.flush()
    
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        # 清理表
        TestBase.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    # 覆盖 get_db 依赖，返回测试数据库会话
    # 注意：必须使用闭包捕获 db，确保每次调用都返回同一个会话
    def override_get_db():
        # 直接返回 db 会话，它已经绑定到 test_engine 并包含所有数据
        try:
            yield db
        finally:
            # 不关闭 db，因为它在 fixture 的 finally 中关闭
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # 清理
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """测试用户数据"""
    return {
        "username": "alice",
        "password": "alice123",
        "token": "alice123",
    }
