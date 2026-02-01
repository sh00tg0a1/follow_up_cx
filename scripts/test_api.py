#!/usr/bin/env python3
"""
本地 API 测试脚本
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def safe_print(text):
    """安全打印（处理编码问题）"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果编码失败，移除特殊字符
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"[OK] Status: {response.status_code}")
        print(f"     Response: {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_root():
    """测试根路径"""
    print_section("2. Root Path")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[OK] Status: {response.status_code}")
        try:
            data = response.json()
            print(f"     Message: {data.get('message')}")
            print(f"     API Endpoints: {len(data.get('api_endpoints', {}))} endpoints")
        except:
            # 可能是 HTML 响应（Flutter Web 已构建）
            print(f"     Response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_login(username="moni", password="moni123"):
    """测试登录"""
    print_section(f"3. Login ({username})")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        print(f"[OK] Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"     Token: {token[:10]}...")
            print(f"     User: {data.get('user', {}).get('username')}")
            return token
        else:
            print(f"     Error: {response.json()}")
            return None
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return None

def test_get_user(token):
    """测试获取用户信息"""
    print_section("4. 获取用户信息")
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"[OK] Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"     Username: {data.get('username')}")
            print(f"     ID: {data.get('id')}")
            return True
        else:
            print(f"     Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_parse(token):
    """测试解析日程"""
    print_section("5. Parse Event (Text)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/parse",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "input_type": "text",
                "text_content": "明天下午3点在星巴克开会",
                "additional_note": "记得带电脑"
            },
            timeout=10
        )
        print(f"[OK] Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            print(f"     Parsed {len(events)} event(s)")
            if events:
                event = events[0]
                print(f"     Title: {event.get('title')}")
                print(f"     Time: {event.get('start_time')}")
                print(f"     Location: {event.get('location')}")
            return True
        else:
            print(f"     Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_list_events(token):
    """测试获取活动列表"""
    print_section("6. List Events")
    try:
        response = requests.get(
            f"{BASE_URL}/api/events",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"[OK] Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            print(f"     Total: {len(events)} event(s)")
            for i, event in enumerate(events[:3], 1):
                print(f"     [{i}] {event.get('title')} @ {event.get('start_time')}")
            return True
        else:
            print(f"     Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_create_event(token):
    """测试创建活动"""
    print_section("7. Create Event")
    try:
        event_data = {
            "title": "测试会议",
            "start_time": (datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)).isoformat(),
            "end_time": (datetime.now().replace(hour=16, minute=30, second=0, microsecond=0)).isoformat(),
            "location": "会议室 A",
            "description": "这是一个测试活动",
            "source_type": "text",
            "is_followed": True,
        }
        response = requests.post(
            f"{BASE_URL}/api/events",
            headers={"Authorization": f"Bearer {token}"},
            json=event_data,
            timeout=5
        )
        print(f"[OK] Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"     Created! ID: {data.get('id')}")
            print(f"     Title: {data.get('title')}")
            return data.get('id')
        else:
            print(f"     Error: {response.json()}")
            return None
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return None

def main():
    """主测试函数"""
    print("\n[TEST] FollowUP API Local Test")
    print(f"[INFO] Base URL: {BASE_URL}")
    
    results = []
    
    # 1. Health check
    results.append(("Health Check", test_health()))
    
    # 2. Root path
    results.append(("Root Path", test_root()))
    
    # 3. Login (try moni first, fallback to alice)
    token = test_login("moni", "moni123")
    if not token:
        print("\n[INFO] moni login failed, trying alice...")
        token = test_login("alice", "alice123")
    results.append(("Login", token is not None))
    
    if not token:
        print("\n[FAIL] Login failed, cannot continue testing")
        print("[INFO] Make sure database is initialized: cd Backend && python init_db.py")
        return
    
    # 4. Get user info
    results.append(("Get User Info", test_get_user(token)))
    
    # 5. Parse event
    results.append(("Parse Event", test_parse(token)))
    
    # 6. List events
    results.append(("List Events", test_list_events(token)))
    
    # 7. Create event
    event_id = test_create_event(token)
    results.append(("Create Event", event_id is not None))
    
    # 总结
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"[RESULT] Passed: {passed}/{total}")
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"     {status} {name}")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
