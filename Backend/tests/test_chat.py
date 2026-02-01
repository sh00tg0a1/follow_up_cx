"""
智能对话相关测试

注意：这些测试需要配置 OPENAI_API_KEY 环境变量才能运行。
如果未配置，测试将被跳过。
"""
import os
import uuid
import pytest
from fastapi import status


# 检查是否有 OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
skip_without_api_key = pytest.mark.skipif(
    not OPENAI_API_KEY,
    reason="OPENAI_API_KEY not configured"
)


@skip_without_api_key
def test_chat_success(client, test_user):
    """测试智能对话（成功）"""
    session_id = str(uuid.uuid4())
    response = client.post(
        "/api/chat",
        json={
            "message": "你好，今天天气怎么样？",
            "session_id": session_id,
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "intent" in data
    assert "session_id" in data
    assert data["session_id"] == session_id
    # 闲聊应该返回 chat 意图
    assert data["intent"] in ["chat", "reject"]


@skip_without_api_key
def test_chat_create_event_intent(client, test_user):
    """测试创建日程意图识别"""
    session_id = str(uuid.uuid4())
    response = client.post(
        "/api/chat",
        json={
            "message": "帮我创建一个明天下午3点的会议",
            "session_id": session_id,
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "intent" in data
    # 应该识别为创建日程意图
    assert data["intent"] in ["create_event", "chat"]


@skip_without_api_key
def test_chat_with_session(client, test_user):
    """测试带会话ID的对话（多轮对话）"""
    session_id = str(uuid.uuid4())
    
    # 第一轮对话
    response1 = client.post(
        "/api/chat",
        json={
            "message": "你好",
            "session_id": session_id,
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response1.status_code == status.HTTP_200_OK
    assert response1.json()["session_id"] == session_id
    
    # 第二轮对话（使用相同 session_id）
    response2 = client.post(
        "/api/chat",
        json={
            "message": "你叫什么名字？",
            "session_id": session_id,
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response2.status_code == status.HTTP_200_OK
    # 应该使用相同的 session_id
    assert response2.json()["session_id"] == session_id


def test_chat_no_auth(client):
    """测试智能对话（无认证）"""
    response = client.post(
        "/api/chat",
        json={
            "message": "你好",
            "session_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_chat_empty_message(client, test_user):
    """测试空消息"""
    response = client.post(
        "/api/chat",
        json={
            "message": "",
            "session_id": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    # Pydantic 验证应该失败
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@skip_without_api_key
def test_clear_conversation(client, test_user):
    """测试清除对话历史"""
    session_id = str(uuid.uuid4())
    
    # 先创建一个对话
    response1 = client.post(
        "/api/chat",
        json={
            "message": "你好",
            "session_id": session_id,
        },
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response1.status_code == status.HTTP_200_OK
    
    # 清除对话
    response2 = client.delete(
        f"/api/chat/{session_id}",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )
    assert response2.status_code == status.HTTP_200_OK
    assert response2.json()["session_id"] == session_id
