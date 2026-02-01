"""
Pydantic Schemas - 请求/响应模型
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ============ 用户相关 ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    created_at: datetime


class LoginResponse(BaseModel):
    """登录响应"""
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


# ============ 活动管理相关 ============

class EventCreate(BaseModel):
    """创建活动请求"""
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    source_type: Optional[str] = Field("manual", max_length=50)
    source_thumbnail: Optional[str] = Field(None, description="图片来源的缩略图（base64）")
    is_followed: bool = True


class EventUpdate(BaseModel):
    """更新活动请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_followed: Optional[bool] = None


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


# ============ 智能对话相关 ============

class ChatRequest(BaseModel):
    """智能对话请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    image_base64: Optional[str] = Field(None, description="可选的单张图片 base64 编码（向后兼容）")
    images_base64: Optional[List[str]] = Field(None, description="可选的多张图片 base64 编码列表")
    session_id: Optional[str] = Field(None, description="会话ID（可选，不传则后端自动生成）")


class ChatResponse(BaseModel):
    """智能对话响应"""
    message: str = Field(..., description="Agent 回复消息")
    intent: str = Field(..., description="识别的意图: chat/create_event/update_event/delete_event/reject")
    session_id: str = Field(..., description="会话ID")
    action_result: Optional[dict] = Field(None, description="操作结果（如创建的日程详情）")


class ConversationMessage(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="消息时间")


# ============ 通用 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
