# LLM Service

使用 LangChain + OpenAI 进行智能日程解析。

## 配置

在 `.env` 文件中设置：

```bash
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini  # 可选，默认使用 gpt-4o-mini
```

## 功能

### 文字解析 (`parse_text_with_llm`)

从自然语言文本中提取日程信息：

```python
from services.llm_service import parse_text_with_llm

events = parse_text_with_llm(
    text="明天下午3点在星巴克开会",
    additional_note="记得带电脑"
)
```

### 图片解析 (`parse_image_with_llm`)

从图片（海报、传单等）中识别日程信息：

```python
from services.llm_service import parse_image_with_llm

events = parse_image_with_llm(
    image_base64="iVBORw0KGgo...",  # Base64 编码的图片
    additional_note="朋友推荐"
)
```

## Fallback 机制

如果 LLM 不可用（API Key 未设置或调用失败），系统会自动使用简单的关键词匹配作为 fallback，确保服务始终可用。

## 依赖

- `langchain>=0.3.0`
- `langchain-openai>=0.2.0`

## 更新依赖

```bash
uv sync
# 或
pip install -U langchain langchain-openai
```
