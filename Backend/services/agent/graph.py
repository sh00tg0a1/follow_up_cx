"""
LangGraph Agent 实现 - 智能日程助手

使用 LangGraph 构建状态图，实现意图识别和多轮对话。
"""
import json
from datetime import datetime
from typing import TypedDict, Optional, List, Literal, Annotated
from operator import add

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from config import settings
from models import Event, User
from logging_config import get_logger
from .prompts.intent import (
    INTENT_CLASSIFIER_PROMPT,
    CHAT_PROMPT,
    EVENT_EXTRACTION_PROMPT,
    EVENT_MATCH_PROMPT,
    EVENT_UPDATE_PROMPT,
)

logger = get_logger(__name__)


# ============================================================================
# Agent 状态定义
# ============================================================================

class AgentState(TypedDict):
    """Agent 状态"""
    # 输入
    message: str
    image_base64: Optional[str]
    user_id: int
    conversation_history: str
    
    # 处理结果
    intent: str
    confidence: float
    response: str
    action_result: Optional[dict]
    
    # 数据库会话（不序列化）
    db: Session


# ============================================================================
# 节点实现
# ============================================================================

def get_llm() -> ChatOpenAI:
    """获取 LLM 实例"""
    import os
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.3,
        api_key=api_key,
    )


def classify_intent(state: AgentState) -> AgentState:
    """意图分类节点"""
    logger.debug(f"Classifying intent for message: {state['message'][:50]}...")
    
    llm = get_llm()
    current_time = datetime.now().isoformat()
    
    # 构建图片说明
    image_note = ""
    if state.get("image_base64"):
        image_note = "（用户附带了一张图片）"
    
    # 调用 LLM 进行意图分类
    prompt = INTENT_CLASSIFIER_PROMPT.format_messages(
        current_time=current_time,
        message=state["message"],
        image_note=image_note,
        conversation_history=state.get("conversation_history", ""),
    )
    
    # 如果有图片，使用多模态
    if state.get("image_base64"):
        content = [
            {"type": "text", "text": prompt[1].content},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{state['image_base64']}"},
            },
        ]
        messages = [prompt[0], HumanMessage(content=content)]
    else:
        messages = prompt
    
    response = llm.invoke(messages)
    
    # 解析 JSON 结果
    try:
        # 尝试提取 JSON
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content.strip())
        intent = result.get("intent", "chat")
        confidence = result.get("confidence", 0.5)
        logger.info(f"Intent classified: {intent} (confidence={confidence})")
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning(f"Failed to parse intent result: {e}, defaulting to chat")
        intent = "chat"
        confidence = 0.5
    
    return {
        **state,
        "intent": intent,
        "confidence": confidence,
    }


def handle_chat(state: AgentState) -> AgentState:
    """处理闲聊对话"""
    logger.debug("Handling chat...")
    
    llm = get_llm()
    current_time = datetime.now().isoformat()
    
    prompt = CHAT_PROMPT.format_messages(
        current_time=current_time,
        message=state["message"],
        conversation_history=state.get("conversation_history", ""),
    )
    
    response = llm.invoke(prompt)
    
    return {
        **state,
        "response": response.content,
        "action_result": None,
    }


def handle_create_event(state: AgentState) -> AgentState:
    """处理创建日程"""
    logger.debug("Handling create event...")
    
    llm = get_llm()
    current_time = datetime.now().isoformat()
    
    # 构建图片说明
    image_note = ""
    if state.get("image_base64"):
        image_note = "（用户附带了图片，请从图片中提取日程信息）"
    
    # 提取日程信息
    prompt = EVENT_EXTRACTION_PROMPT.format_messages(
        current_time=current_time,
        message=state["message"],
        image_note=image_note,
    )
    
    # 如果有图片，使用多模态
    if state.get("image_base64"):
        content = [
            {"type": "text", "text": prompt[1].content},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{state['image_base64']}"},
            },
        ]
        messages = [prompt[0], HumanMessage(content=content)]
    else:
        messages = prompt
    
    response = llm.invoke(messages)
    
    # 解析事件信息
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        event_data = json.loads(content.strip())
        
        # 创建事件
        db = state["db"]
        event = Event(
            user_id=state["user_id"],
            title=event_data.get("title", "新日程"),
            start_time=datetime.fromisoformat(event_data["start_time"]),
            end_time=datetime.fromisoformat(event_data["end_time"]) if event_data.get("end_time") else None,
            location=event_data.get("location"),
            description=event_data.get("description"),
            source_type="agent",
            is_followed=True,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        
        logger.info(f"Created event: {event.title} (id={event.id})")
        
        # 构建响应
        response_text = f"好的，我已经为您创建了日程：\n\n"
        response_text += f"📅 **{event.title}**\n"
        response_text += f"⏰ 时间：{event.start_time.strftime('%Y年%m月%d日 %H:%M')}"
        if event.end_time:
            response_text += f" - {event.end_time.strftime('%H:%M')}"
        response_text += "\n"
        if event.location:
            response_text += f"📍 地点：{event.location}\n"
        if event.description:
            response_text += f"📝 备注：{event.description}\n"
        
        return {
            **state,
            "response": response_text,
            "action_result": {
                "action": "create_event",
                "event_id": event.id,
                "event_title": event.title,
            },
        }
        
    except Exception as e:
        logger.error(f"Failed to create event: {e}")
        return {
            **state,
            "response": "抱歉，我无法从您的输入中提取日程信息。请提供更详细的信息，例如：时间、地点、活动内容。",
            "action_result": {"action": "create_event", "error": str(e)},
        }


def handle_update_event(state: AgentState) -> AgentState:
    """处理修改日程"""
    logger.debug("Handling update event...")
    
    db = state["db"]
    user_id = state["user_id"]
    
    # 获取用户的日程列表
    events = db.query(Event).filter(Event.user_id == user_id).order_by(Event.start_time).all()
    
    if not events:
        return {
            **state,
            "response": "您目前没有任何日程，无法进行修改。",
            "action_result": {"action": "update_event", "error": "no_events"},
        }
    
    # 使用 LLM 匹配目标日程
    llm = get_llm()
    events_list = json.dumps([
        {
            "id": e.id,
            "title": e.title,
            "start_time": e.start_time.isoformat(),
            "location": e.location,
        }
        for e in events
    ], ensure_ascii=False)
    
    match_prompt = EVENT_MATCH_PROMPT.format_messages(
        events_list=events_list,
        user_description=state["message"],
    )
    
    match_response = llm.invoke(match_prompt)
    
    try:
        content = match_response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        match_result = json.loads(content.strip())
        matched_id = match_result.get("matched_event_id")
        
        if not matched_id:
            return {
                **state,
                "response": "抱歉，我没有找到匹配的日程。请更详细地描述您想修改的日程。",
                "action_result": {"action": "update_event", "error": "no_match"},
            }
        
        # 获取目标事件
        event = db.query(Event).filter(Event.id == matched_id, Event.user_id == user_id).first()
        if not event:
            return {
                **state,
                "response": "抱歉，找不到该日程。",
                "action_result": {"action": "update_event", "error": "event_not_found"},
            }
        
        # 提取更新信息
        original_event = json.dumps({
            "title": event.title,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "location": event.location,
            "description": event.description,
        }, ensure_ascii=False)
        
        update_prompt = EVENT_UPDATE_PROMPT.format_messages(
            original_event=original_event,
            user_message=state["message"],
        )
        
        update_response = llm.invoke(update_prompt)
        
        content = update_response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        update_data = json.loads(content.strip())
        
        # 更新事件
        if "title" in update_data and update_data["title"]:
            event.title = update_data["title"]
        if "start_time" in update_data and update_data["start_time"]:
            event.start_time = datetime.fromisoformat(update_data["start_time"])
        if "end_time" in update_data and update_data["end_time"]:
            event.end_time = datetime.fromisoformat(update_data["end_time"])
        if "location" in update_data and update_data["location"]:
            event.location = update_data["location"]
        if "description" in update_data and update_data["description"]:
            event.description = update_data["description"]
        
        db.commit()
        db.refresh(event)
        
        logger.info(f"Updated event: {event.title} (id={event.id})")
        
        response_text = f"好的，我已经为您更新了日程「{event.title}」：\n"
        response_text += f"⏰ 时间：{event.start_time.strftime('%Y年%m月%d日 %H:%M')}\n"
        if event.location:
            response_text += f"📍 地点：{event.location}\n"
        
        return {
            **state,
            "response": response_text,
            "action_result": {"action": "update_event", "event_id": event.id},
        }
        
    except Exception as e:
        logger.error(f"Failed to update event: {e}")
        return {
            **state,
            "response": "抱歉，修改日程时出错了。请稍后重试。",
            "action_result": {"action": "update_event", "error": str(e)},
        }


def handle_delete_event(state: AgentState) -> AgentState:
    """处理删除日程"""
    logger.debug("Handling delete event...")
    
    db = state["db"]
    user_id = state["user_id"]
    
    # 获取用户的日程列表
    events = db.query(Event).filter(Event.user_id == user_id).order_by(Event.start_time).all()
    
    if not events:
        return {
            **state,
            "response": "您目前没有任何日程，无法进行删除。",
            "action_result": {"action": "delete_event", "error": "no_events"},
        }
    
    # 使用 LLM 匹配目标日程
    llm = get_llm()
    events_list = json.dumps([
        {
            "id": e.id,
            "title": e.title,
            "start_time": e.start_time.isoformat(),
            "location": e.location,
        }
        for e in events
    ], ensure_ascii=False)
    
    match_prompt = EVENT_MATCH_PROMPT.format_messages(
        events_list=events_list,
        user_description=state["message"],
    )
    
    match_response = llm.invoke(match_prompt)
    
    try:
        content = match_response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        match_result = json.loads(content.strip())
        matched_id = match_result.get("matched_event_id")
        
        if not matched_id:
            return {
                **state,
                "response": "抱歉，我没有找到匹配的日程。请更详细地描述您想删除的日程。",
                "action_result": {"action": "delete_event", "error": "no_match"},
            }
        
        # 获取并删除目标事件
        event = db.query(Event).filter(Event.id == matched_id, Event.user_id == user_id).first()
        if not event:
            return {
                **state,
                "response": "抱歉，找不到该日程。",
                "action_result": {"action": "delete_event", "error": "event_not_found"},
            }
        
        event_title = event.title
        db.delete(event)
        db.commit()
        
        logger.info(f"Deleted event: {event_title} (id={matched_id})")
        
        return {
            **state,
            "response": f"好的，我已经为您删除了日程「{event_title}」。",
            "action_result": {"action": "delete_event", "event_id": matched_id},
        }
        
    except Exception as e:
        logger.error(f"Failed to delete event: {e}")
        return {
            **state,
            "response": "抱歉，删除日程时出错了。请稍后重试。",
            "action_result": {"action": "delete_event", "error": str(e)},
        }


def handle_reject(state: AgentState) -> AgentState:
    """处理无法处理的请求"""
    logger.debug("Handling reject...")
    
    return {
        **state,
        "response": "抱歉，这个请求超出了我的能力范围。我是一个日程助手，可以帮您创建、修改和删除日程，也可以和您闲聊。如果有日程相关的需求，请告诉我！",
        "action_result": None,
    }


# ============================================================================
# 路由函数
# ============================================================================

def route_by_intent(state: AgentState) -> str:
    """根据意图路由到不同的处理节点"""
    intent = state.get("intent", "chat")
    
    if intent == "create_event":
        return "create_event"
    elif intent == "update_event":
        return "update_event"
    elif intent == "delete_event":
        return "delete_event"
    elif intent == "reject":
        return "reject"
    else:
        return "chat"


# ============================================================================
# 构建图
# ============================================================================

def create_agent_graph() -> StateGraph:
    """创建 Agent 状态图"""
    
    # 创建图
    graph = StateGraph(AgentState)
    
    # 添加节点
    graph.add_node("intent_classifier", classify_intent)
    graph.add_node("chat", handle_chat)
    graph.add_node("create_event", handle_create_event)
    graph.add_node("update_event", handle_update_event)
    graph.add_node("delete_event", handle_delete_event)
    graph.add_node("reject", handle_reject)
    
    # 设置入口
    graph.set_entry_point("intent_classifier")
    
    # 添加条件边（根据意图路由）
    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "chat": "chat",
            "create_event": "create_event",
            "update_event": "update_event",
            "delete_event": "delete_event",
            "reject": "reject",
        }
    )
    
    # 所有处理节点都结束
    graph.add_edge("chat", END)
    graph.add_edge("create_event", END)
    graph.add_edge("update_event", END)
    graph.add_edge("delete_event", END)
    graph.add_edge("reject", END)
    
    return graph.compile()


# ============================================================================
# 运行 Agent
# ============================================================================

def run_agent(
    message: str,
    user_id: int,
    db: Session,
    image_base64: Optional[str] = None,
    conversation_history: str = "",
) -> dict:
    """
    运行 Agent 处理用户请求
    
    Args:
        message: 用户消息
        user_id: 用户 ID
        db: 数据库会话
        image_base64: 可选的图片 base64
        conversation_history: 对话历史
        
    Returns:
        包含 intent, response, action_result 的字典
    """
    logger.info(f"Running agent for user {user_id}: {message[:50]}...")
    
    # 创建并运行图
    agent = create_agent_graph()
    
    initial_state = AgentState(
        message=message,
        image_base64=image_base64,
        user_id=user_id,
        conversation_history=conversation_history,
        intent="",
        confidence=0.0,
        response="",
        action_result=None,
        db=db,
    )
    
    # 运行图
    result = agent.invoke(initial_state)
    
    logger.info(f"Agent completed: intent={result['intent']}")
    
    return {
        "intent": result["intent"],
        "response": result["response"],
        "action_result": result["action_result"],
    }
