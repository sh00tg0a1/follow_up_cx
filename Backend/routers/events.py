"""
活动路由 - /api/events/*

CRUD 操作 + ICS 文件生成
使用固定 Token 认证
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from icalendar import Calendar, Event as ICalEvent

from schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
)
from auth import get_current_user
from mock_data import (
    get_events_by_user,
    add_event,
    get_event_by_id,
    update_event,
    delete_event,
)

router = APIRouter(prefix="/events", tags=["活动管理"])


def event_to_response(event: dict) -> EventResponse:
    """将内部事件字典转换为响应模型"""
    return EventResponse(
        id=event["id"],
        title=event["title"],
        start_time=event["start_time"],
        end_time=event.get("end_time"),
        location=event.get("location"),
        description=event.get("description"),
        source_type=event.get("source_type"),
        is_followed=event.get("is_followed", False),
        created_at=event["created_at"],
    )


@router.get("", response_model=EventListResponse)
async def list_events(
    followed_only: bool = Query(False, description="仅返回已 Follow 的活动"),
    current_user: dict = Depends(get_current_user),
):
    """
    获取用户的活动列表
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    events = get_events_by_user(user_id, followed_only)
    
    return EventListResponse(
        events=[event_to_response(e) for e in events]
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    创建新活动
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    
    event_data = {
        "title": request.title,
        "start_time": request.start_time,
        "end_time": request.end_time,
        "location": request.location,
        "description": request.description,
        "source_type": request.source_type,
        "is_followed": request.is_followed,
    }
    
    event = add_event(user_id, event_data)
    return event_to_response(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    获取单个活动详情
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    event = get_event_by_id(user_id, event_id)
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    return event_to_response(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event_endpoint(
    event_id: int,
    request: EventUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    更新活动
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    
    existing = get_event_by_id(user_id, event_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    update_data = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.start_time is not None:
        update_data["start_time"] = request.start_time
    if request.end_time is not None:
        update_data["end_time"] = request.end_time
    if request.location is not None:
        update_data["location"] = request.location
    if request.description is not None:
        update_data["description"] = request.description
    if request.is_followed is not None:
        update_data["is_followed"] = request.is_followed
    
    updated = update_event(user_id, event_id, update_data)
    return event_to_response(updated)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_endpoint(
    event_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    删除活动
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    
    success = delete_event(user_id, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    return None


@router.get("/{event_id}/ics")
async def download_ics(
    event_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    下载活动的 ICS 文件
    
    需要认证：Authorization: Bearer <token>
    """
    user_id = current_user["id"]
    event = get_event_by_id(user_id, event_id)
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    cal = Calendar()
    cal.add("prodid", "-//FollowUP//followup.app//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    
    ical_event = ICalEvent()
    ical_event.add("summary", event["title"])
    ical_event.add("dtstart", event["start_time"])
    
    if event.get("end_time"):
        ical_event.add("dtend", event["end_time"])
    
    if event.get("location"):
        ical_event.add("location", event["location"])
    
    if event.get("description"):
        ical_event.add("description", event["description"])
    
    ical_event.add("dtstamp", datetime.utcnow())
    ical_event.add("uid", f"event-{event_id}@followup.app")
    
    cal.add_component(ical_event)
    
    ics_content = cal.to_ical()
    
    safe_title = "".join(c for c in event["title"] if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title or 'event'}.ics"
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
