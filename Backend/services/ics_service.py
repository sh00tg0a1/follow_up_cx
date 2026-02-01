"""
ICS 文件生成服务

用于生成日历事件的标准 ICS 格式文件。
"""
import base64
from datetime import datetime
from icalendar import Calendar, Event as ICalEvent

from models import Event
from logging_config import get_logger

logger = get_logger(__name__)


def generate_ics_content(event: Event) -> str:
    """
    生成单个事件的 ICS 文件内容（base64 编码）
    
    Args:
        event: Event 模型实例
        
    Returns:
        base64 编码的 ICS 文件内容字符串
    """
    cal = Calendar()
    cal.add("prodid", "-//FollowUP//followup.app//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    ical_event = ICalEvent()
    ical_event.add("summary", event.title)
    ical_event.add("dtstart", event.start_time)

    if event.end_time:
        ical_event.add("dtend", event.end_time)

    if event.location:
        ical_event.add("location", event.location)

    if event.description:
        ical_event.add("description", event.description)

    ical_event.add("dtstamp", datetime.utcnow())
    ical_event.add("uid", f"event-{event.id}@followup.app")

    cal.add_component(ical_event)

    ics_content = cal.to_ical()
    
    # 返回 base64 编码的内容
    return base64.b64encode(ics_content).decode('utf-8')


def generate_ics_bytes(event: Event) -> bytes:
    """
    生成单个事件的 ICS 文件内容（原始字节）
    
    Args:
        event: Event 模型实例
        
    Returns:
        ICS 文件内容的原始字节
    """
    cal = Calendar()
    cal.add("prodid", "-//FollowUP//followup.app//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    ical_event = ICalEvent()
    ical_event.add("summary", event.title)
    ical_event.add("dtstart", event.start_time)

    if event.end_time:
        ical_event.add("dtend", event.end_time)

    if event.location:
        ical_event.add("location", event.location)

    if event.description:
        ical_event.add("description", event.description)

    ical_event.add("dtstamp", datetime.utcnow())
    ical_event.add("uid", f"event-{event.id}@followup.app")

    cal.add_component(ical_event)

    return cal.to_ical()
