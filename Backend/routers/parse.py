"""
日程解析路由 - /api/parse

使用 LangChain + OpenAI 进行智能日程解析
支持单张或多张图片批量解析
"""
import uuid
import os
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from schemas import ParseRequest, ParseResponse, ParsedEvent
from auth import get_current_user
from models import User
from logging_config import get_logger
from services.image_utils import generate_thumbnail

logger = get_logger(__name__)

# 尝试导入 LLM 服务，如果失败则使用 fallback
try:
    from services.llm_service import parse_text_with_llm, parse_image_with_llm
    LLM_AVAILABLE = os.getenv("OPENAI_API_KEY") is not None
    if LLM_AVAILABLE:
        logger.info("LLM service available (OpenAI API key configured)")
    else:
        logger.warning("LLM service unavailable (OpenAI API key not configured)")
except (ImportError, ValueError) as e:
    LLM_AVAILABLE = False
    logger.warning(f"LLM service unavailable: {e}")

router = APIRouter(tags=["日程解析"])


def parse_text_fallback(text: str, additional_note: str = None) -> list[ParsedEvent]:
    """
    解析文字内容（Fallback - 简单关键词匹配）
    当 LLM 不可用时使用
    """
    import re
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    # 简单的时间关键词识别
    if "明天" in text:
        event_date = now + timedelta(days=1)
    elif "后天" in text:
        event_date = now + timedelta(days=2)
    elif "下周" in text:
        event_date = now + timedelta(days=7)
    else:
        event_date = now + timedelta(days=3)
    
    # 简单的时间点识别
    hour = 14
    if "上午" in text or "早上" in text:
        hour = 10
    elif "下午" in text:
        hour = 14
    elif "晚上" in text:
        hour = 19
    
    # 尝试提取具体时间
    time_match = re.search(r'(\d{1,2})[点时]', text)
    if time_match:
        hour = int(time_match.group(1))
        if hour < 12 and ("下午" in text or "晚上" in text):
            hour += 12
    
    start_time = event_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # 提取标题
    title = "会议"
    keywords = {"开会": "会议", "聚餐": "聚餐", "吃饭": "聚餐", "音乐会": "音乐会", "演出": "演出", "面试": "面试", "约会": "约会"}
    for kw, t in keywords.items():
        if kw in text:
            title = t
            break
    else:
        title = text[:10].strip() if len(text) > 10 else text.strip()
    
    return [ParsedEvent(
        id=None,
        title=title,
        start_time=start_time,
        end_time=None,
        location=additional_note,
        description=text,
        source_type="text",
        is_followed=False,
    )]


def parse_image_fallback(image_base64: str, additional_note: str = None) -> list[ParsedEvent]:
    """
    解析图片内容（Fallback - 模拟数据）
    当 LLM 不可用时使用
    """
    from datetime import datetime
    
    now = datetime.now()
    next_month = now.month + 1 if now.month < 12 else 1
    next_year = now.year if now.month < 12 else now.year + 1
    
    return [ParsedEvent(
        id=None,
        title="汉堡爱乐乐团音乐会",
        start_time=datetime(next_year, next_month, 15, 19, 30),
        end_time=datetime(next_year, next_month, 15, 22, 0),
        location="Elbphilharmonie, Hamburg",
        description="贝多芬第九交响曲\n指挥：Alan Gilbert\n\n" + (additional_note or ""),
        source_type="image",
        is_followed=False,
    )]


def parse_text(text: str, additional_note: str = None) -> list[ParsedEvent]:
    """
    解析文字内容
    优先使用 LLM，失败时使用 fallback
    """
    logger.debug(f"Parsing text (length={len(text)}, LLM_AVAILABLE={LLM_AVAILABLE})")
    start_time = time.time()
    
    if LLM_AVAILABLE:
        try:
            events = parse_text_with_llm(text, additional_note)
            elapsed = time.time() - start_time
            if events:
                logger.info(f"LLM parsed {len(events)} event(s) from text in {elapsed:.2f}s")
                return events
            else:
                logger.warning(f"LLM returned no events, using fallback")
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}", exc_info=True)
    
    # Fallback to simple parsing
    logger.debug("Using fallback text parser")
    events = parse_text_fallback(text, additional_note)
    logger.info(f"Fallback parser returned {len(events)} event(s)")
    return events


def parse_image(image_base64: str, additional_note: str = None) -> list[ParsedEvent]:
    """
    解析单张图片内容
    优先使用 LLM Vision，失败时使用 fallback
    同时生成缩略图附加到每个事件
    """
    # 生成缩略图
    thumbnail = generate_thumbnail(image_base64)
    if thumbnail:
        logger.debug(f"Generated thumbnail for image, size: {len(thumbnail)} chars")
    
    # 解析图片
    if LLM_AVAILABLE:
        events = parse_image_with_llm(image_base64, additional_note)
        if events:
            # 为每个事件附加缩略图
            for event in events:
                event.source_thumbnail = thumbnail
            return events
    
    # Fallback to simple parsing
    events = parse_image_fallback(image_base64, additional_note)
    # 为每个事件附加缩略图
    for event in events:
        event.source_thumbnail = thumbnail
    return events


def parse_images(images_base64: List[str], additional_note: str = None) -> list[ParsedEvent]:
    """
    批量解析多张图片内容
    优先使用 LLM Vision 批量处理，失败时逐个处理
    为每张图片生成缩略图并附加到对应的事件
    """
    logger.debug(f"Parsing {len(images_base64)} images (LLM_AVAILABLE={LLM_AVAILABLE})")
    start_time = time.time()
    
    all_events = []
    
    if LLM_AVAILABLE:
        try:
            from services.llm_service import parse_images_with_llm
            # 尝试批量处理
            events = parse_images_with_llm(images_base64, additional_note)
            if events:
                elapsed = time.time() - start_time
                logger.info(f"LLM batch parsed {len(events)} event(s) from {len(images_base64)} image(s) in {elapsed:.2f}s")
                
                # 为每个事件生成并附加缩略图（使用第一张图片的缩略图，或可以改进为关联到对应图片）
                # 注意：批量处理时，LLM 可能无法准确关联事件到具体图片，这里使用第一张图片的缩略图
                if images_base64:
                    thumbnail = generate_thumbnail(images_base64[0])
                    for event in events:
                        event.source_thumbnail = thumbnail
                
                return events
        except Exception as e:
            logger.warning(f"Batch parsing failed, falling back to individual parsing: {e}")
    
    # Fallback: 逐个处理每张图片
    logger.debug("Using individual image parsing (fallback)")
    for idx, image_base64 in enumerate(images_base64):
        try:
            events = parse_image(image_base64, additional_note)
            all_events.extend(events)
            logger.debug(f"Parsed image {idx+1}/{len(images_base64)}: {len(events)} event(s)")
        except Exception as e:
            logger.warning(f"Failed to parse image {idx+1}: {e}")
            continue
    
    elapsed = time.time() - start_time
    logger.info(f"Parsed {len(all_events)} total event(s) from {len(images_base64)} image(s) in {elapsed:.2f}s")
    return all_events


@router.post("/parse", response_model=ParseResponse)
async def parse_event(
    request: ParseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    解析日程信息
    
    支持文字和图片两种输入类型：
    - text: 从文字描述中提取日程
    - image: 从图片（海报等）中识别日程
    
    需要认证：Authorization: Bearer <token>
    """
    parse_id = str(uuid.uuid4())
    logger.info(
        f"Parse request from user {current_user.username}: "
        f"type={request.input_type}, parse_id={parse_id}"
    )
    
    if request.input_type == "text":
        if not request.text_content:
            logger.warning(f"Parse failed: text_content is required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="text_content is required for text input type",
            )
        events = parse_text(request.text_content, request.additional_note)
    
    elif request.input_type == "image":
        # 支持单张或多张图片
        images_to_parse = []
        
        # 优先使用 images_base64（多图片）
        if request.images_base64:
            images_to_parse = request.images_base64
        # 向后兼容：支持单张图片 image_base64
        elif request.image_base64:
            images_to_parse = [request.image_base64]
        else:
            logger.warning(f"Parse failed: image_base64 or images_base64 is required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_base64 or images_base64 is required for image input type",
            )
        
        # 处理多张图片
        if len(images_to_parse) == 1:
            # 单张图片：使用原有逻辑（包含缩略图生成）
            events = parse_image(images_to_parse[0], request.additional_note)
        else:
            # 多张图片：批量处理
            events = parse_images(images_to_parse, request.additional_note)
    
    else:
        logger.warning(f"Parse failed: invalid input_type={request.input_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="input_type must be 'text' or 'image'",
        )
    
    logger.info(
        f"Parse completed: parse_id={parse_id}, "
        f"user={current_user.username}, "
        f"events_count={len(events)}"
    )
    
    return ParseResponse(
        events=events,
        parse_id=parse_id,
    )
