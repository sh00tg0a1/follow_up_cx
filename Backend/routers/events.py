"""
活动路由 - /api/events/*

CRUD 操作 + ICS 文件生成
使用固定 Token 认证
从数据库查询和操作
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
    DuplicateGroup,
    DuplicatesResponse,
    DeleteDuplicatesRequest,
    DeleteDuplicatesResponse,
)
from auth import get_current_user
from database import get_db
from models import User, Event
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/events", tags=["活动管理"])


def event_to_response(event: Event, include_ics: bool = False) -> EventResponse:
    """
    将数据库模型转换为响应模型
    
    Args:
        event: Event 模型实例
        include_ics: 是否包含 ICS 文件内容
    """
    ics_content = None
    ics_download_url = None
    
    if include_ics:
        from services.ics_service import generate_ics_content
        ics_content = generate_ics_content(event)
        ics_download_url = f"/api/events/{event.id}/ics"
    
    return EventResponse(
        id=event.id,
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        description=event.description,
        source_type=event.source_type,
        source_thumbnail=event.source_thumbnail,
        is_followed=event.is_followed,
        created_at=event.created_at,
        ics_content=ics_content,
        ics_download_url=ics_download_url,
    )


@router.get("", response_model=EventListResponse)
async def list_events(
    followed_only: bool = Query(False, description="仅返回已 Follow 的活动"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取用户的活动列表

    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Listing events for user {current_user.username} (followed_only={followed_only})")
    
    query = db.query(Event).filter(Event.user_id == current_user.id)

    if followed_only:
        query = query.filter(Event.is_followed == True)  # noqa: E712

    events = query.order_by(Event.start_time).all()
    logger.info(f"Found {len(events)} event(s) for user {current_user.username}")

    return EventListResponse(
        events=[event_to_response(e) for e in events]
    )


@router.get("/search", response_model=EventListResponse)
async def search_events(
    q: str = Query(..., min_length=1, description="搜索查询（自然语言）"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    搜索活动（使用文本搜索）

    需要认证：Authorization: Bearer <token>
    """
    from sqlalchemy import or_
    
    logger.info(f"Searching events for user {current_user.username}: '{q}' (limit={limit})")
    
    # 使用 LIKE 文本搜索
    search_pattern = f"%{q}%"
    events = db.query(Event).filter(
        Event.user_id == current_user.id,
        or_(
            Event.title.ilike(search_pattern),
            Event.description.ilike(search_pattern),
            Event.location.ilike(search_pattern),
        )
    ).order_by(Event.start_time).limit(limit).all()
    
    logger.info(f"Text search found {len(events)} event(s)")
    
    return EventListResponse(
        events=[event_to_response(e) for e in events]
    )


@router.get("/duplicates", response_model=DuplicatesResponse)
async def find_duplicates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    查询用户的重复事件
    
    重复定义：标题相同且开始时间相同的事件
    
    返回分组的重复事件列表，每组包含：
    - key: 重复标识
    - events: 该组所有重复事件
    - keep_id: 建议保留的事件 ID（最早创建的）
    - delete_ids: 建议删除的事件 ID 列表
    
    需要认证：Authorization: Bearer <token>
    """
    from sqlalchemy import func
    from collections import defaultdict
    
    logger.info(f"Finding duplicate events for user {current_user.username}")
    
    # 查询所有事件
    all_events = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(Event.created_at).all()
    
    # 按 (title, start_time) 分组
    groups_dict = defaultdict(list)
    for event in all_events:
        key = (event.title, event.start_time)
        groups_dict[key].append(event)
    
    # 过滤出有重复的组
    duplicate_groups = []
    total_duplicates = 0
    
    for (title, start_time), events in groups_dict.items():
        if len(events) > 1:
            # 有重复
            key_str = f"{title} @ {start_time.strftime('%Y-%m-%d %H:%M')}"
            
            # 按创建时间排序，保留最早的
            sorted_events = sorted(events, key=lambda e: e.created_at)
            keep_event = sorted_events[0]
            delete_events = sorted_events[1:]
            
            duplicate_groups.append(DuplicateGroup(
                key=key_str,
                events=[event_to_response(e) for e in sorted_events],
                keep_id=keep_event.id,
                delete_ids=[e.id for e in delete_events],
            ))
            
            total_duplicates += len(delete_events)
    
    logger.info(f"Found {len(duplicate_groups)} duplicate group(s), {total_duplicates} event(s) to delete")
    
    return DuplicatesResponse(
        total_duplicates=total_duplicates,
        groups=duplicate_groups,
    )


@router.delete("/duplicates", response_model=DeleteDuplicatesResponse)
async def delete_duplicates(
    request: DeleteDuplicatesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    批量删除重复事件
    
    传入要删除的事件 ID 列表，只会删除属于当前用户的事件。
    建议先调用 GET /api/events/duplicates 获取重复事件列表，
    确认后将 delete_ids 传入此接口。
    
    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Deleting duplicate events for user {current_user.username}: {request.event_ids}")
    
    # 查询要删除的事件（只删除属于当前用户的）
    events_to_delete = db.query(Event).filter(
        Event.id.in_(request.event_ids),
        Event.user_id == current_user.id,
    ).all()
    
    deleted_ids = []
    for event in events_to_delete:
        logger.debug(f"Deleting duplicate event {event.id}: {event.title}")
        db.delete(event)
        deleted_ids.append(event.id)
    
    db.commit()
    
    logger.info(f"Deleted {len(deleted_ids)} duplicate event(s)")
    
    return DeleteDuplicatesResponse(
        deleted_count=len(deleted_ids),
        deleted_ids=deleted_ids,
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新活动

    需要认证：Authorization: Bearer <token>
    """
    # 检查是否重复
    duplicate = db.query(Event).filter(
        Event.user_id == current_user.id,
        Event.title == request.title,
        Event.start_time == request.start_time,
    ).first()
    
    if duplicate:
        logger.info(f"Duplicate event detected for user {current_user.username}: {request.title} at {request.start_time}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"这个日程已经存在了：{duplicate.title}（{duplicate.start_time.strftime('%Y年%m月%d日 %H:%M')}）。需要我帮您修改吗？",
        )
    
    event = Event(
        user_id=current_user.id,
        title=request.title,
        start_time=request.start_time,
        end_time=request.end_time,
        location=request.location,
        description=request.description,
        source_type=request.source_type or "manual",
        source_thumbnail=request.source_thumbnail,
        is_followed=request.is_followed,
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)

    # 创建事件时返回 ICS 内容
    return event_to_response(event, include_ics=True)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取单个活动详情

    需要认证：Authorization: Bearer <token>
    """
    logger.debug(f"Getting event {event_id} for user {current_user.username}")
    
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id,
    ).first()

    if event is None:
        logger.warning(f"Event {event_id} not found for user {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    logger.debug(f"Event {event_id} retrieved: {event.title}")
    return event_to_response(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event_endpoint(
    event_id: int,
    request: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新活动

    需要认证：Authorization: Bearer <token>
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id,
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # 更新字段
    if request.title is not None:
        event.title = request.title
    if request.start_time is not None:
        event.start_time = request.start_time
    if request.end_time is not None:
        event.end_time = request.end_time
    if request.location is not None:
        event.location = request.location
    if request.description is not None:
        event.description = request.description
    if request.is_followed is not None:
        event.is_followed = request.is_followed

    db.commit()
    db.refresh(event)

    return event_to_response(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_endpoint(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除活动

    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Deleting event {event_id} for user {current_user.username}")
    
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id,
    ).first()

    if event is None:
        logger.warning(f"Event {event_id} not found for user {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    logger.info(f"Deleting event {event_id}: {event.title}")
    db.delete(event)
    db.commit()
    logger.info(f"Event {event_id} deleted successfully")

    return None


@router.get("/{event_id}/ics")
async def download_ics(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    下载活动的 ICS 文件

    需要认证：Authorization: Bearer <token>
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id,
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # 使用 ICS 服务生成内容
    from services.ics_service import generate_ics_bytes
    ics_content = generate_ics_bytes(event)

    # 使用 ASCII 安全的文件名，避免 HTTP 头编码问题
    safe_title = "".join(c for c in event.title if c.isascii() and (c.isalnum() or c in " -_")).strip()
    filename = f"{safe_title or 'event'}.ics"
    
    # 对于包含非 ASCII 字符的标题，使用 RFC 5987 编码
    from urllib.parse import quote
    filename_encoded = quote(f"{event.title}.ics", safe="")

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{filename_encoded}",
        },
    )
