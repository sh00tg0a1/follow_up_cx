-- ============================================================================
-- FollowUP 数据库初始化脚本 - SQLite 版本
-- ============================================================================
-- 
-- 使用方法：
--   sqlite3 followup.db < init_sqlite.sql
--   或
--   sqlite3 followup.db
--   .read init_sqlite.sql
--
-- 警告：此脚本会删除所有现有数据！
-- ============================================================================

-- ============================================================================
-- 1. 删除现有表（如果存在，按依赖顺序删除）
-- ============================================================================

DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- 2. 创建 users 表
-- ============================================================================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);

-- ============================================================================
-- 3. 创建 events 表
-- ============================================================================

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    location VARCHAR(500) NULL,
    description TEXT NULL,
    source_type VARCHAR(50) NOT NULL DEFAULT 'manual',
    source_content TEXT NULL,
    source_thumbnail TEXT NULL,
    is_followed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束（SQLite 需要启用外键支持）
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_is_followed ON events(is_followed);

-- ============================================================================
-- 4. 创建 conversations 表
-- ============================================================================

CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    messages TEXT NOT NULL DEFAULT '[]',  -- SQLite 使用 TEXT 存储 JSON
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- ============================================================================
-- 5. 启用外键约束（SQLite 默认禁用）
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 6. 插入预置用户数据
-- ============================================================================

INSERT INTO users (username, password, created_at) VALUES
    ('alice', 'alice123', '2026-01-01 10:00:00'),
    ('bob', 'bob123', '2026-01-01 10:00:00'),
    ('jane', 'jane123', '2026-01-01 10:00:00'),
    ('xiao', 'xiao123', '2026-01-01 10:00:00'),
    ('moni', 'moni123', '2026-01-01 10:00:00');

-- ============================================================================
-- 完成提示
-- ============================================================================

SELECT 'Database initialized successfully!' AS status;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS event_count FROM events;
SELECT COUNT(*) AS conversation_count FROM conversations;
