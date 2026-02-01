"""
Event Extraction Prompts

Contains prompt templates for text parsing and image parsing.
"""
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_core.pydantic_v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class EventExtraction(BaseModel):
    """Event extraction result"""
    title: str = Field(description="Event title")
    start_time: str = Field(description="Start time, ISO 8601 format, e.g.: 2026-02-01T15:00:00")
    end_time: Optional[str] = Field(None, description="End time, ISO 8601 format, optional")
    location: Optional[str] = Field(None, description="Location")
    description: Optional[str] = Field(None, description="Event description")


class EventExtractionList(BaseModel):
    """Event list"""
    events: List[EventExtraction] = Field(description="List of extracted events")
    needs_clarification: bool = Field(
        default=False,
        description="Whether clarification is needed from user"
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Clarification question to ask user"
    )


# ============================================================================
# Text Parsing Prompt
# ============================================================================

TEXT_PARSE_SYSTEM = """你是一个智能日程助手，擅长从自然语言文本中提取日程信息。

请仔细分析用户输入的文字，提取出所有可能的日程事件。对于每个事件，你需要：
1. 提取事件标题
2. 推断开始时间（如果文本中没有明确时间，使用当前时间作为参考）
3. 推断结束时间（如果可能）
4. 提取地点信息（如果有）
5. 提取事件描述

当前时间：{current_time}

**重要：信息不完整时需要反问用户**
如果以下关键信息缺失或模糊，请设置 needs_clarification=true 并提出澄清问题：
- 时间不明确（如"下周"但没说具体哪天，"晚上"但没说几点）
- 事件类型不清楚
- 有多种可能的理解方式

澄清问题应该简洁友好，一次只问一个最重要的问题。

请以 JSON 格式返回结果：
- events: 事件数组，每个事件包含 title, start_time, end_time, location, description
- needs_clarification: 是否需要澄清（布尔值）
- clarification_question: 澄清问题（仅当 needs_clarification=true 时）

示例1 - 信息完整：
{{"events": [...], "needs_clarification": false, "clarification_question": null}}

示例2 - 需要澄清：
{{"events": [], "needs_clarification": true, "clarification_question": "请问「下周开会」是指下周几呢？大概几点开始？"}}

示例3 - 部分信息可提取，但仍需澄清：
{{"events": [{{"title": "开会", "start_time": "2026-02-03T14:00:00", ...}}], "needs_clarification": true, "clarification_question": "我暂时假设是下周一下午2点，请问这个时间对吗？"}}"""

TEXT_PARSE_USER = "用户输入：{text}\n补充说明：{additional_note}"

TEXT_PARSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", TEXT_PARSE_SYSTEM),
    ("user", TEXT_PARSE_USER),
])


# ============================================================================
# Image Parsing Prompt
# ============================================================================

IMAGE_PARSE_SYSTEM_PROMPT = """You are a smart calendar assistant, skilled at recognizing event information from images (such as posters, flyers, screenshots).

Please carefully analyze the image content and extract all possible event information. For each event, you need to:
1. Identify event title
2. Extract start time (date and time)
3. Extract end time (if available)
4. Extract location information
5. Extract event description and other relevant information

Current time: {current_time}

**Important: Ask user when information is incomplete**
If the following key information is missing or unrecognizable in the image, set needs_clarification=true and ask a clarification question:
- Date or time is unclear (e.g., only time without date, or year is unclear)
- Location information is ambiguous
- Image quality is poor and cannot be fully recognized

Clarification questions should be concise and friendly, ask only one most important question at a time.

Please return results in JSON format:
- events: Event array, each event contains title, start_time, end_time, location, description
- needs_clarification: Whether clarification is needed (boolean)
- clarification_question: Clarification question (only when needs_clarification=true)

Example 1 - Complete information:
{{"events": [...], "needs_clarification": false, "clarification_question": null}}

Example 2 - Needs clarification:
{{"events": [], "needs_clarification": true, "clarification_question": "Is the event in the image happening this year or next year?"}}

Example 3 - Partial information extractable, but still needs clarification:
{{"events": [{{"title": "Concert", "start_time": "2026-03-15T19:30:00", ...}}], "needs_clarification": true, "clarification_question": "The image doesn't show the year, I'm assuming it's 2026, is that correct?"}}"""
