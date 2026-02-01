"""
对话记忆管理 - 使用数据库存储对话历史
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from models import Conversation
from logging_config import get_logger

logger = get_logger(__name__)


class ConversationMemory:
    """对话记忆管理器"""
    
    def __init__(self, db: Session, user_id: int, session_id: Optional[str] = None):
        """
        初始化对话记忆
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            session_id: 会话 ID（可选，不传则自动生成）
        """
        self.db = db
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self._conversation: Optional[Conversation] = None
        
        # 加载或创建会话
        self._load_or_create()
    
    def _load_or_create(self):
        """加载现有会话或创建新会话"""
        self._conversation = self.db.query(Conversation).filter(
            Conversation.session_id == self.session_id,
            Conversation.user_id == self.user_id,
        ).first()
        
        if self._conversation is None:
            logger.debug(f"Creating new conversation: session_id={self.session_id}, user_id={self.user_id}")
            self._conversation = Conversation(
                session_id=self.session_id,
                user_id=self.user_id,
                messages=[],
            )
            self.db.add(self._conversation)
            self.db.commit()
            self.db.refresh(self._conversation)
        else:
            logger.debug(f"Loaded existing conversation: session_id={self.session_id}, messages_count={len(self._conversation.messages)}")
    
    def add_message(self, role: str, content: str):
        """
        添加消息到对话历史
        
        Args:
            role: 消息角色 (user/assistant)
            content: 消息内容
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # 更新消息列表
        messages = list(self._conversation.messages) if self._conversation.messages else []
        messages.append(message)
        self._conversation.messages = messages
        self._conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        logger.debug(f"Added message: role={role}, content_length={len(content)}")
    
    def get_messages(self, limit: int = 10) -> List[dict]:
        """
        获取最近的对话消息
        
        Args:
            limit: 返回的最大消息数量
            
        Returns:
            消息列表
        """
        messages = self._conversation.messages or []
        return messages[-limit:] if len(messages) > limit else messages
    
    def get_formatted_history(self, limit: int = 10) -> str:
        """
        获取格式化的对话历史（用于 prompt）
        
        Args:
            limit: 返回的最大消息数量
            
        Returns:
            格式化的对话历史字符串
        """
        messages = self.get_messages(limit)
        if not messages:
            return "（无历史对话）"
        
        formatted = []
        for msg in messages:
            role = "用户" if msg["role"] == "user" else "助手"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def clear(self):
        """清空对话历史"""
        self._conversation.messages = []
        self._conversation.updated_at = datetime.utcnow()
        self.db.commit()
        logger.debug(f"Cleared conversation: session_id={self.session_id}")
    
    @property
    def conversation_id(self) -> str:
        """返回会话 ID"""
        return self.session_id
