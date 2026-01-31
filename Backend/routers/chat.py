"""
智能对话路由 - /api/chat

基于 LangGraph 的智能 Agent，支持：
- 意图识别（闲聊/创建/修改/删除日程）
- 图片+文字输入
- 对话记忆
- 流式响应（SSE）
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from schemas import ChatRequest, ChatResponse
from auth import get_current_user
from database import get_db
from models import User
from logging_config import get_logger
from services.agent import run_agent, run_agent_stream, ConversationMemory

logger = get_logger(__name__)

router = APIRouter(tags=["智能对话"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    stream: bool = Query(False, description="是否使用流式响应（SSE）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    智能对话接口
    
    支持意图识别和多轮对话：
    - 闲聊：直接用 LLM 回复
    - 创建日程：解析输入并创建日程
    - 修改日程：根据描述匹配并修改日程
    - 删除日程：根据描述匹配并删除日程
    
    支持图片输入，会使用 Vision 模型分析图片内容。
    
    参数：
    - stream: 是否使用流式响应（SSE），默认 false
    
    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Chat request from user {current_user.username}: {request.message[:50]}... (stream={stream})")
    
    # 初始化对话记忆
    memory = ConversationMemory(
        db=db,
        user_id=current_user.id,
        session_id=request.session_id,
    )
    
    # 获取对话历史
    conversation_history = memory.get_formatted_history(limit=10)
    
    # 添加用户消息到记忆
    memory.add_message("user", request.message)
    
    # 处理图片：支持单张或多张图片
    images_base64 = []
    if request.images_base64:
        images_base64 = request.images_base64
    elif request.image_base64:
        # 向后兼容：单张图片
        images_base64 = [request.image_base64]
    
    # 传递给 agent 的图片（chat 接口目前只支持单张图片，多张图片会使用第一张）
    image_base64_for_agent = images_base64[0] if images_base64 else None
    
    if stream:
        # 流式响应
        async def generate_stream():
            try:
                full_response = ""
                intent = ""
                action_result = None
                
                # 发送初始事件（意图识别）
                yield f"data: {json.dumps({'type': 'status', 'message': '正在识别意图...'}, ensure_ascii=False)}\n\n"
                
                async for chunk in run_agent_stream(
                    message=request.message,
                    user_id=current_user.id,
                    db=db,
                    image_base64=image_base64_for_agent,
                    images_base64=images_base64 if len(images_base64) > 1 else None,
                    conversation_history=conversation_history,
                ):
                    if chunk["type"] == "intent":
                        intent = chunk["intent"]
                        yield f"data: {json.dumps({'type': 'intent', 'intent': intent}, ensure_ascii=False)}\n\n"
                    elif chunk["type"] == "token":
                        token = chunk["token"]
                        full_response += token
                        yield f"data: {json.dumps({'type': 'token', 'token': token}, ensure_ascii=False)}\n\n"
                    elif chunk["type"] == "action":
                        action_result = chunk["action_result"]
                        yield f"data: {json.dumps({'type': 'action', 'action_result': action_result}, ensure_ascii=False)}\n\n"
                    elif chunk["type"] == "done":
                        # 保存完整回复到记忆
                        memory.add_message("assistant", full_response)
                        logger.info(f"Chat completed: intent={intent}, session_id={memory.conversation_id}")
                        yield f"data: {json.dumps({'type': 'done', 'session_id': memory.conversation_id}, ensure_ascii=False)}\n\n"
                        break
                    elif chunk["type"] == "error":
                        error_msg = chunk.get("error", "未知错误")
                        yield f"data: {json.dumps({'type': 'error', 'error': error_msg}, ensure_ascii=False)}\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"Stream chat error: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            }
        )
    else:
        # 非流式响应（原有逻辑）
        try:
            result = run_agent(
                message=request.message,
                user_id=current_user.id,
                db=db,
                image_base64=image_base64_for_agent,
                images_base64=images_base64 if len(images_base64) > 1 else None,
                conversation_history=conversation_history,
            )
            
            # 添加助手回复到记忆
            memory.add_message("assistant", result["response"])
            
            logger.info(f"Chat completed: intent={result['intent']}, session_id={memory.conversation_id}")
            
            return ChatResponse(
                message=result["response"],
                intent=result["intent"],
                session_id=memory.conversation_id,
                action_result=result["action_result"],
            )
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"处理请求时出错：{str(e)}",
            )


@router.delete("/chat/{session_id}")
async def clear_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    清除对话历史
    
    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Clear conversation request from user {current_user.username}: session_id={session_id}")
    
    try:
        memory = ConversationMemory(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )
        memory.clear()
        
        return {"message": "对话历史已清除", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Clear conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除对话历史时出错：{str(e)}",
        )
