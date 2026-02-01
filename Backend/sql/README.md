# 数据库初始化 SQL 脚本

本目录包含用于重新初始化数据库的 SQL 脚本。

## ⚠️ 警告

**这些脚本会删除所有现有数据！** 请在生产环境使用前备份数据库。

## 文件说明

- `init_postgresql.sql` - PostgreSQL 数据库初始化脚本
- `init_sqlite.sql` - SQLite 数据库初始化脚本
- `run_init.py` - Python 脚本执行器（自动检测数据库类型）
- `README.md` - 本说明文档

## 使用方法

### PostgreSQL

```bash
# 方法1: 使用 psql 命令行工具
psql -U username -d database_name -f sql/init_postgresql.sql

# 方法2: 使用连接字符串
psql postgresql://user:password@host:port/database -f sql/init_postgresql.sql

# 方法3: 在 psql 交互式环境中
psql -U username -d database_name
\i sql/init_postgresql.sql
```

### SQLite

```bash
# 方法1: 直接执行
sqlite3 followup.db < sql/init_sqlite.sql

# 方法2: 在 sqlite3 交互式环境中
sqlite3 followup.db
.read sql/init_sqlite.sql
```

## 脚本功能

两个脚本都会：

1. ✅ 删除所有现有表（按依赖顺序）
2. ✅ 创建所有必需的表结构
3. ✅ 创建所有索引
4. ✅ 插入预置用户数据（5个测试用户）

### PostgreSQL 版本特点

- ✅ 使用标准 PostgreSQL 数据类型

### SQLite 版本特点

- ✅ 启用外键约束
- ✅ 使用 TEXT 类型存储 JSON（conversations.messages）

## 预置用户

脚本会创建以下测试用户：

| Username | Password | Token |
|----------|----------|-------|
| alice    | alice123 | alice123 |
| bob      | bob123   | bob123 |
| jane     | jane123  | jane123 |
| xiao     | xiao123  | xiao123 |
| moni     | moni123  | moni123 |

## 表结构

### users 表

- `id` - 主键（自增）
- `username` - 用户名（唯一）
- `password` - 密码
- `created_at` - 创建时间

### events 表

- `id` - 主键（自增）
- `user_id` - 外键 -> users.id
- `title` - 活动标题
- `start_time` - 开始时间
- `end_time` - 结束时间（可空）
- `location` - 地点（可空）
- `description` - 描述（可空）
- `source_type` - 来源类型
- `source_content` - 原始内容（可空）
- `source_thumbnail` - 缩略图（可空）
- `is_followed` - 是否已 Follow
- `created_at` - 创建时间

### conversations 表

- `id` - 主键（自增）
- `session_id` - 会话ID（唯一）
- `user_id` - 外键 -> users.id
- `messages` - 消息列表（JSON）
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 验证

脚本执行完成后会显示：

```sql
status: Database initialized successfully!
user_count: 5
event_count: 0
conversation_count: 0
```

## 注意事项

1. **备份数据**：执行前请备份现有数据
2. **生产环境**：生产环境建议使用迁移脚本而非直接执行 SQL
3. **向量索引**：PostgreSQL 版本的向量索引默认已注释，当数据量 >= 100 时再创建
4. **外键约束**：SQLite 版本会自动启用外键约束

## 替代方案

如果不想使用 SQL 脚本，也可以使用 Python 脚本：

```bash
# 使用 Python 初始化脚本（会检查现有数据）
cd Backend
python init_db.py

# 或使用迁移脚本（幂等，安全）
python migrate_db.py
```

## 故障排除

### SQLite: 外键约束未生效

确保在连接时启用外键：

```python
# 在 database.py 中已配置
connect_args={"check_same_thread": False}
# 但需要在每个连接中执行: PRAGMA foreign_keys = ON;
```

## 相关文档

- [数据库迁移指南](../DB_MIGRATION.md)
- [数据库使用说明](../DATABASE.md)
