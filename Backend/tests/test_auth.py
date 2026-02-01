"""
认证相关测试
"""
import pytest
from fastapi import status


def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] == test_user["token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == test_user["username"]


def test_login_invalid_username(client):
    """测试无效用户名"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]


def test_login_invalid_password(client, test_user):
    """测试无效密码"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user["username"],
            "password": "wrong_password",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]


def test_get_current_user_success(client, test_user):
    """测试获取当前用户信息（成功）"""
    response = client.get(
        "/api/user/me",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user["username"]
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_no_token(client):
    """测试获取当前用户信息（无 Token）"""
    response = client.get("/api/user/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client):
    """测试获取当前用户信息（无效 Token）"""
    response = client.get(
        "/api/user/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
