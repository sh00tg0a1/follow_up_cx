"""
Pydantic Schemas - Request/Response Models
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ============ User Related ============

class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """User information response"""
    id: int
    username: str
    created_at: datetime


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ 日程解析相关 ============

class ParseRequest(BaseModel):
    """日程解析请求"""
    input_type: Literal["text", "image"] = Field(..., description="输入类型: text 或 image")
    text_content: Optional[str] = Field(None, description="文字内容")
    image_base64: Optional[str] = Field(None, description="单张图片 base64 编码（向后兼容）")
    images_base64: Optional[List[str]] = Field(None, description="多张图片 base64 编码列表")
    additional_note: Optional[str] = Field(None, description="补充说明")


class ParsedEvent(BaseModel):
    """解析出的活动"""
    id: Optional[int] = None
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    source_type: str
    source_thumbnail: Optional[str] = None  # 图片来源的缩略图（base64）
    is_followed: bool = False


class ParseResponse(BaseModel):
    """日程解析响应"""
    events: List[ParsedEvent]
    parse_id: str
    needs_clarification: bool = False  # 是否需要用户澄清信息
    clarification_question: Optional[str] = None  # 澄清问题（当 needs_clarification=True 时）


# ============ Event Management Related ============

class EventCreate(BaseModel):
    """Create event request"""
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    source_type: Optional[str] = Field("manual", max_length=50)
    source_thumbnail: Optional[str] = Field(None, description="Thumbnail of image source (base64)")
    is_followed: bool = True
    recurrence_rule: Optional[str] = Field(None, max_length=255, description="RRULE format, e.g., 'FREQ=DAILY;INTERVAL=1' or 'FREQ=WEEKLY;BYDAY=MO,WE,FR'")
    recurrence_end: Optional[datetime] = Field(None, description="End date/time for recurrence")


class EventUpdate(BaseModel):
    """Update event request"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_followed: Optional[bool] = None
    recurrence_rule: Optional[str] = Field(None, max_length=255, description="RRULE format")
    recurrence_end: Optional[datetime] = Field(None, description="End date/time for recurrence")


class EventResponse(BaseModel):
    """活动响应"""
    id: int
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_thumbnail: Optional[str] = None  # 图片来源的缩略图（base64）
    is_followed: bool = False
    created_at: datetime
    recurrence_rule: Optional[str] = None  # RRULE format
    recurrence_end: Optional[datetime] = None  # End date/time for recurrence
    parent_event_id: Optional[int] = None  # Parent event ID if this is a recurrence instance
    ics_content: Optional[str] = None  # ICS 文件内容（base64 编码），创建事件时返回
    ics_download_url: Optional[str] = None  # ICS 文件下载 URL


class EventListResponse(BaseModel):
    """活动列表响应"""
    events: List[EventResponse]


class DuplicateGroup(BaseModel):
    """重复事件组"""
    key: str  # 重复的标识（如 "标题 @ 时间"）
    events: List[EventResponse]  # 该组中的所有重复事件
    keep_id: int  # 建议保留的事件 ID（通常是最早创建的）
    delete_ids: List[int]  # 建议删除的事件 ID 列表


class DuplicatesResponse(BaseModel):
    """重复事件查询响应"""
    total_duplicates: int  # 重复事件总数（不含保留的）
    groups: List[DuplicateGroup]  # 重复事件分组


class DeleteDuplicatesRequest(BaseModel):
    """删除重复事件请求"""
    event_ids: List[int] = Field(..., description="要删除的事件 ID 列表")


class DeleteDuplicatesResponse(BaseModel):
    """删除重复事件响应"""
    deleted_count: int  # 成功删除的数量
    deleted_ids: List[int]  # 成功删除的事件 ID


# ============ Smart Chat Related ============

class ChatRequest(BaseModel):
    """Smart chat request"""
    message: str = Field(..., min_length=1, description="User message")
    image_base64: Optional[str] = Field(None, description="Optional single image base64 encoded (backward compatibility)")
    images_base64: Optional[List[str]] = Field(None, description="Optional multiple images base64 encoded list")
    session_id: Optional[str] = Field(None, description="Session ID (optional, backend auto-generates if not provided)")


class ChatResponse(BaseModel):
    """Smart chat response"""
    message: str = Field(..., description="Agent reply message")
    intent: str = Field(..., description="Recognized intent: chat/create_event/update_event/delete_event/reject")
    session_id: str = Field(..., description="Session ID")
    action_result: Optional[dict] = Field(None, description="Action result (e.g., created event details)")


class ConversationMessage(BaseModel):
    """Conversation message"""
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


# ============ Common ============

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
