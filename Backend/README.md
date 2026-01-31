# FollowUP Backend

智能日程助手后端服务，基于 FastAPI + LangGraph 构建。

## 架构概览

### Agent 架构图

```mermaid
flowchart TB
    subgraph Client["客户端"]
        User["👤 用户"]
        Flutter["📱 Flutter App"]
        WebTest["🌐 Web 测试页"]
    end

    subgraph API["FastAPI 后端"]
        ChatRouter["/api/chat\n智能对话接口"]
        ParseRouter["/api/parse\n日程解析接口"]
        EventsRouter["/api/events\n日程管理接口"]
    end

    subgraph Agent["LangGraph Agent"]
        direction TB
        IntentClassifier["🧠 意图分类器\nIntent Classifier"]
        
        subgraph Handlers["处理节点"]
            ChatHandler["💬 闲聊处理\nChat Handler"]
            CreateHandler["📅 创建日程\nCreate Event"]
            QueryHandler["🔍 查询日程\nQuery Event"]
            UpdateHandler["✏️ 修改日程\nUpdate Event"]
            DeleteHandler["🗑️ 删除日程\nDelete Event"]
            RejectHandler["❓ 不确定处理\nReject Handler"]
        end
        
        IntentClassifier -->|chat| ChatHandler
        IntentClassifier -->|create_event| CreateHandler
        IntentClassifier -->|query_event| QueryHandler
        IntentClassifier -->|update_event| UpdateHandler
        IntentClassifier -->|delete_event| DeleteHandler
        IntentClassifier -->|reject| RejectHandler
    end

    subgraph Services["服务层"]
        LLMService["🤖 LLM 服务\nOpenAI GPT-4o"]
        EmbeddingService["📊 Embedding 服务\ntext-embedding-3-small"]
        Memory["💾 对话记忆\nConversation Memory"]
    end

    subgraph Database["数据库"]
        SQLite["📁 SQLite\n(开发环境)"]
        PostgreSQL["🐘 PostgreSQL\n(生产环境)"]
        pgvector["🔢 pgvector\n向量搜索"]
    end

    User --> Flutter
    User --> WebTest
    Flutter --> ChatRouter
    WebTest --> ChatRouter
    Flutter --> ParseRouter
    Flutter --> EventsRouter
    
    ChatRouter --> Agent
    ParseRouter --> LLMService
    
    Agent --> LLMService
    Agent --> Memory
    QueryHandler --> EmbeddingService
    CreateHandler --> EmbeddingService
    
    Memory --> SQLite
    Memory --> PostgreSQL
    EmbeddingService --> pgvector
    
    CreateHandler --> EventsRouter
    QueryHandler --> EventsRouter
    UpdateHandler --> EventsRouter
    DeleteHandler --> EventsRouter
```

### Agent 流程图

```mermaid
sequenceDiagram
    participant U as 用户
    participant C as Chat API
    participant A as Agent
    participant I as 意图分类器
    participant H as 处理节点
    participant L as LLM
    participant D as 数据库

    U->>C: POST /api/chat {message, session_id}
    C->>A: run_agent_stream()
    
    Note over A: 发送 thinking 事件
    A-->>U: {"type": "thinking", "message": "正在理解您的请求..."}
    
    A->>I: 意图识别
    I->>L: 调用 GPT-4o 分析意图
    L-->>I: {intent: "create_event", confidence: 0.95}
    A-->>U: {"type": "intent", "intent": "create_event"}
    
    Note over A: 发送 thinking 事件
    A-->>U: {"type": "thinking", "message": "正在创建日程..."}
    
    A->>H: 路由到 CreateHandler
    H->>L: 提取日程信息
    L-->>H: {title, start_time, location...}
    H->>D: INSERT INTO events
    D-->>H: event_id = 123
    
    H-->>A: action_result
    A-->>U: {"type": "action", "action_result": {...}}
    A-->>U: {"type": "content", "content": "已创建日程..."}
    A-->>U: {"type": "done", "session_id": "xxx"}
```

### 意图分类决策树

```mermaid
flowchart TD
    Start["用户输入"] --> HasImage{"包含图片?"}
    
    HasImage -->|是| ImageAnalysis["分析图片内容"]
    ImageAnalysis --> HasEventInfo{"包含活动信息?"}
    HasEventInfo -->|是| CreateEvent["create_event"]
    HasEventInfo -->|否| AskUser["chat (询问用户)"]
    
    HasImage -->|否| TextAnalysis["分析文本内容"]
    
    TextAnalysis --> TimeKeyword{"包含时间关键词?"}
    TimeKeyword -->|是| ActionKeyword{"包含操作关键词?"}
    
    ActionKeyword -->|创建/安排/记一下| CreateEvent
    ActionKeyword -->|查看/看看/有什么| QueryEvent["query_event"]
    ActionKeyword -->|改/修改/调整| UpdateEvent["update_event"]
    ActionKeyword -->|删/取消/不要了| DeleteEvent["delete_event"]
    ActionKeyword -->|无明确操作| QueryEvent
    
    TimeKeyword -->|否| IsGreeting{"是问候/闲聊?"}
    IsGreeting -->|是| Chat["chat"]
    IsGreeting -->|否| AskUser
    
    style CreateEvent fill:#4CAF50
    style QueryEvent fill:#2196F3
    style UpdateEvent fill:#FF9800
    style DeleteEvent fill:#f44336
    style Chat fill:#9C27B0
    style AskUser fill:#607D8B
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | FastAPI |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| ORM | SQLAlchemy |
| LLM | LangChain + LangGraph + OpenAI |
| 向量搜索 | pgvector |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置 OPENAI_API_KEY

# 启动开发服务器
python main.py
```

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/chat` | 智能对话（支持流式） |
| POST | `/api/parse` | 解析文本/图片 |
| GET | `/api/events` | 获取日程列表 |
| GET | `/api/events/search` | 语义搜索日程 |
| POST | `/api/events` | 创建日程 |
| PUT | `/api/events/{id}` | 更新日程 |
| DELETE | `/api/events/{id}` | 删除日程 |

## 测试

```bash
# 运行测试
pytest

# 使用 Web 测试页面
# 启动服务器后访问 tests/chat_test.html
```

## 相关文档

- [AGENTS.md](AGENTS.md) - 开发规则和指南
- [CHAT_STREAMING.md](CHAT_STREAMING.md) - 流式响应文档
- [DATABASE.md](DATABASE.md) - 数据库设计文档
