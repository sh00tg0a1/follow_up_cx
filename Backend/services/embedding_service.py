"""
Embedding 服务 - 生成文本向量

使用 OpenAI text-embedding-3-small 模型生成 1536 维向量。
仅在 PostgreSQL 环境下使用，SQLite 环境降级返回 None。
"""
from typing import Optional, List
import os

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# Embedding 维度（text-embedding-3-small）
EMBEDDING_DIMENSION = 1536

# 检查是否为 PostgreSQL 环境
def is_postgres() -> bool:
    """检查当前是否使用 PostgreSQL"""
    return settings.DATABASE_URL.startswith("postgresql")


def get_embedding_client():
    """获取 OpenAI 客户端"""
    try:
        from openai import OpenAI
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not configured, embedding disabled")
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        logger.warning("openai package not installed, embedding disabled")
        return None


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    生成文本的向量嵌入
    
    Args:
        text: 要生成向量的文本
        
    Returns:
        1536 维向量列表，如果生成失败或在 SQLite 环境则返回 None
    """
    # SQLite 环境下不生成 embedding
    if not is_postgres():
        logger.debug("Skipping embedding generation (SQLite environment)")
        return None
    
    if not text or not text.strip():
        logger.debug("Skipping embedding generation (empty text)")
        return None
    
    client = get_embedding_client()
    if not client:
        return None
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text.strip(),
        )
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding for text: {text[:50]}... (dim={len(embedding)})")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def generate_event_embedding(
    title: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Optional[List[float]]:
    """
    为日程生成向量嵌入
    
    将日程的标题、描述、地点合并为文本后生成向量。
    
    Args:
        title: 日程标题
        description: 日程描述（可选）
        location: 日程地点（可选）
        
    Returns:
        1536 维向量列表，如果生成失败则返回 None
    """
    # 构建文本：标题 + 描述 + 地点
    parts = [title]
    if description:
        parts.append(description)
    if location:
        parts.append(f"地点: {location}")
    
    text = " | ".join(parts)
    return generate_embedding(text)


def search_similar_events_sql(
    query_embedding: List[float],
    user_id: int,
    limit: int = 10,
    threshold: float = 0.7,
) -> str:
    """
    生成向量相似度搜索的 SQL 语句（PostgreSQL + pgvector）
    
    Args:
        query_embedding: 查询向量
        user_id: 用户 ID
        limit: 返回结果数量
        threshold: 相似度阈值（余弦相似度，0-1）
        
    Returns:
        SQL 查询语句
    """
    # 使用余弦距离（<=>）进行相似度搜索
    # 注意：pgvector 的 <=> 返回的是距离，所以需要用 1 - distance 得到相似度
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    sql = f"""
    SELECT 
        id, title, start_time, end_time, location, description,
        1 - (embedding <=> '{embedding_str}'::vector) as similarity
    FROM events
    WHERE user_id = {user_id}
        AND embedding IS NOT NULL
        AND 1 - (embedding <=> '{embedding_str}'::vector) >= {threshold}
    ORDER BY embedding <=> '{embedding_str}'::vector
    LIMIT {limit}
    """
    return sql
