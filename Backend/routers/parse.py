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
    from config import settings
    # 检查 API key（同时检查 settings 和环境变量）
    LLM_AVAILABLE = bool(settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
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
    解析图片内容（Fallback）
    当 LLM 不可用时返回空列表，让调用方处理
    """
    logger.warning("Image parsing fallback called - LLM unavailable, cannot parse image")
    # 不再返回 mock 数据，返回空列表
    return []


def is_llm_available() -> bool:
    """动态检查 LLM 是否可用"""
    try:
        from config import settings
        return bool(settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
    except Exception:
        return False


class TextParseResult:
    """文本解析结果"""
    def __init__(self, events: list, needs_clarification: bool = False, clarification_question: str = None):
        self.events = events
        self.needs_clarification = needs_clarification
        self.clarification_question = clarification_question


def parse_text(text: str, additional_note: str = None) -> TextParseResult:
    """
    解析文字内容
    优先使用 LLM，如果 LLM 不可用则使用简单的关键词解析
    返回包含事件列表和可能的澄清问题
    """
    llm_available = is_llm_available()
    logger.debug(f"Parsing text (length={len(text)}, LLM_AVAILABLE={llm_available})")
    start_time = time.time()
    
    if llm_available:
        try:
            result = parse_text_with_llm(text, additional_note)
            elapsed = time.time() - start_time
            logger.info(f"LLM parsed {len(result.events)} event(s) from text in {elapsed:.2f}s")
            return TextParseResult(
                events=result.events,
                needs_clarification=result.needs_clarification,
                clarification_question=result.clarification_question,
            )
        except Exception as e:
            logger.error(f"LLM text parsing failed: {e}", exc_info=True)
    
    # 对于文本解析，使用简单的关键词匹配作为降级方案
    # 这不是 mock 数据，而是基于用户输入的实际解析
    logger.debug("Using keyword-based text parser (fallback)")
    events = parse_text_fallback(text, additional_note)
    if events:
        logger.info(f"Keyword parser extracted {len(events)} event(s) from text")
    return TextParseResult(events=events, needs_clarification=False, clarification_question=None)


class ImageParseResult:
    """图片解析结果"""
    def __init__(self, events: list, needs_clarification: bool = False, clarification_question: str = None):
        self.events = events
        self.needs_clarification = needs_clarification
        self.clarification_question = clarification_question


def parse_image(image_base64: str, additional_note: str = None) -> ImageParseResult:
    """
    解析单张图片内容
    使用 LLM Vision 解析图片中的日程信息
    同时生成缩略图附加到每个事件
    返回包含事件列表和可能的澄清问题
    """
    # 生成缩略图
    thumbnail = generate_thumbnail(image_base64)
    if thumbnail:
        logger.debug(f"Generated thumbnail for image, size: {len(thumbnail)} chars")
    
    llm_available = is_llm_available()
    logger.debug(f"Parsing image (LLM_AVAILABLE={llm_available})")
    
    if not llm_available:
        logger.error("Cannot parse image: LLM service unavailable (OPENAI_API_KEY not configured)")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="图片解析服务暂不可用，请联系管理员配置 OpenAI API Key",
        )
    
    # 解析图片
    try:
        result = parse_image_with_llm(image_base64, additional_note)
        logger.info(f"LLM parsed {len(result.events)} event(s) from image")
        
        # 为每个事件附加缩略图
        for event in result.events:
            event.source_thumbnail = thumbnail
        
        return ImageParseResult(
            events=result.events,
            needs_clarification=result.needs_clarification,
            clarification_question=result.clarification_question,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM image parsing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片解析失败: {str(e)}",
        )


def parse_images(images_base64: List[str], additional_note: str = None) -> list[ParsedEvent]:
    """
    批量解析多张图片内容
    使用 LLM Vision 批量处理，失败时逐个处理
    为每张图片生成缩略图并附加到对应的事件
    """
    llm_available = is_llm_available()
    logger.debug(f"Parsing {len(images_base64)} images (LLM_AVAILABLE={llm_available})")
    start_time = time.time()
    
    if not llm_available:
        logger.error("Cannot parse images: LLM service unavailable (OPENAI_API_KEY not configured)")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="图片解析服务暂不可用，请联系管理员配置 OpenAI API Key",
        )
    
    all_events = []
    
    try:
        from services.llm_service import parse_images_with_llm
        # 尝试批量处理
        events = parse_images_with_llm(images_base64, additional_note)
        if events:
            elapsed = time.time() - start_time
            logger.info(f"LLM batch parsed {len(events)} event(s) from {len(images_base64)} image(s) in {elapsed:.2f}s")
            
            # 为每个事件生成并附加缩略图（使用第一张图片的缩略图）
            if images_base64:
                thumbnail = generate_thumbnail(images_base64[0])
                for event in events:
                    event.source_thumbnail = thumbnail
            
            return events
        else:
            logger.warning("LLM batch returned no events, trying individual parsing")
    except HTTPException:
        raise
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
    
    当信息不完整时，会返回 needs_clarification=true 和澄清问题，
    前端可以将用户的回答放入 additional_note 再次调用解析接口。
    
    需要认证：Authorization: Bearer <token>
    """
    parse_id = str(uuid.uuid4())
    logger.info(
        f"Parse request from user {current_user.username}: "
        f"type={request.input_type}, parse_id={parse_id}"
    )
    
    # 初始化结果变量
    events = []
    needs_clarification = False
    clarification_question = None
    
    if request.input_type == "text":
        if not request.text_content:
            logger.warning(f"Parse failed: text_content is required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="text_content is required for text input type",
            )
        result = parse_text(request.text_content, request.additional_note)
        events = result.events
        needs_clarification = result.needs_clarification
        clarification_question = result.clarification_question
    
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
            result = parse_image(images_to_parse[0], request.additional_note)
            events = result.events
            needs_clarification = result.needs_clarification
            clarification_question = result.clarification_question
        else:
            # 多张图片：批量处理（暂不支持澄清问题）
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
        f"events_count={len(events)}, "
        f"needs_clarification={needs_clarification}"
    )
    
    return ParseResponse(
        events=events,
        parse_id=parse_id,
        needs_clarification=needs_clarification,
        clarification_question=clarification_question,
    )
