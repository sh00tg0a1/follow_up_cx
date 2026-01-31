"""
智能对话路由 - /api/chat

基于 LangGraph 的智能 Agent，支持：
- 意图识别（闲聊/创建/修改/删除日程）
- 图片+文字输入
- 对话记忆
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import ChatRequest, ChatResponse
from auth import get_current_user
from database import get_db
from models import User
from logging_config import get_logger
from services.agent import run_agent, ConversationMemory

logger = get_logger(__name__)

router = APIRouter(tags=["智能对话"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
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
    
    需要认证：Authorization: Bearer <token>
    """
    logger.info(f"Chat request from user {current_user.username}: {request.message[:50]}...")
    
    try:
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
        
        # 运行 Agent
        result = run_agent(
            message=request.message,
            user_id=current_user.id,
            db=db,
            image_base64=request.image_base64,
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
