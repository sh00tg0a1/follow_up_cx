# 创建测试事件脚本

## 使用方法

### 方式一：直接运行批处理文件（Windows）

```bash
scripts\create_events.bat
```

### 方式二：运行 Python 脚本

```bash
# 确保已安装 requests
pip install requests

# 运行脚本
python scripts/create_events.py
```

## 配置

编辑 `scripts/create_events.py` 修改配置：

```python
BASE_URL = "https://web-production-d2e00.up.railway.app"  # 线上地址
# BASE_URL = "http://localhost:8000"  # 本地地址
USERNAME = "alice"
PASSWORD = "alice123"
```

## 功能

脚本会：
1. 登录获取 Token
2. 创建 10 个不同的事件（会议、音乐会、聚餐等）
3. 验证创建结果并显示事件列表

## 事件列表

1. 团队周会
2. 汉堡爱乐音乐会
3. 同学聚餐
4. 项目评审会议
5. 健身房训练
6. 技术分享会
7. 周末郊游
8. 电影首映
9. 医生预约
10. 生日派对
