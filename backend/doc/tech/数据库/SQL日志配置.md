# SQLAlchemy SQL 日志配置指南

## 概述

SQLAlchemy 提供了强大的 SQL 日志功能，可以打印实际执行的 SQL 语句、参数和查询结果，方便开发调试。

---

## 快速开始

### 1. 启用 SQL 日志

编辑 `.env` 文件：

```bash
# .env
DATABASE_ECHO=True          # 打印 SQL 语句
DATABASE_POOL_ECHO=False    # 不打印连接池日志（可选）
```

### 2. 重启服务

```bash
# 重启 FastAPI 服务
uvicorn backend.main:app --reload
```

### 3. 查看日志输出

执行任何数据库操作，控制台会打印 SQL 日志：

```sql
2026-01-14 12:00:00,123 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-01-14 12:00:00,124 INFO sqlalchemy.engine.Engine SELECT demo.id, demo.username, demo.created_time
FROM demo
WHERE demo.deleted = $1::INTEGER
2026-01-14 12:00:00,125 INFO sqlalchemy.engine.Engine [generated in 0.00012s] (0,)
2026-01-14 12:00:00,130 INFO sqlalchemy.engine.Engine COMMIT
```

---

## 配置选项详解

### 1. DATABASE_ECHO - SQL 语句日志

**配置：**
```python
# backend/core/conf.py
DATABASE_ECHO: bool | Literal['debug'] = False
```

**选项说明：**

| 值 | 说明 | 输出内容 |
|---|-----|---------|
| `False` | 禁用（默认） | 不打印任何 SQL |
| `True` | 启用 | 打印 SQL 语句和参数 |
| `'debug'` | 调试模式 | 打印 SQL 语句、参数、结果集元数据 |

**示例输出：**

```python
# DATABASE_ECHO=True
DATABASE_ECHO=True
```

**控制台输出：**
```sql
INFO sqlalchemy.engine.Engine SELECT demo.id, demo.username
FROM demo
WHERE demo.deleted = $1::INTEGER
INFO sqlalchemy.engine.Engine [cached since 0.001s ago] (0,)
```

```python
# DATABASE_ECHO='debug'
DATABASE_ECHO='debug'
```

**控制台输出：**
```sql
DEBUG sqlalchemy.engine.Engine SELECT demo.id, demo.username
FROM demo
WHERE demo.deleted = %(deleted_1)s
DEBUG sqlalchemy.engine.Engine [cached since 0.001s ago] {'deleted_1': 0}
DEBUG sqlalchemy.engine.Engine Col ('id', 'username')
DEBUG sqlalchemy.engine.Engine Row (1, 'test_user')
```

---

### 2. DATABASE_POOL_ECHO - 连接池日志

**配置：**
```python
# backend/core/conf.py
DATABASE_POOL_ECHO: bool | Literal['debug'] = False
```

**选项说明：**

| 值 | 说明 | 输出内容 |
|---|-----|---------|
| `False` | 禁用（默认） | 不打印连接池日志 |
| `True` | 启用 | 打印连接池操作（获取、释放连接） |
| `'debug'` | 调试模式 | 打印详细的连接池调试信息 |

**示例输出：**

```python
# DATABASE_POOL_ECHO=True
DATABASE_POOL_ECHO=True
```

**控制台输出：**
```
INFO sqlalchemy.pool.impl.AsyncAdaptedQueuePool Created new connection <asyncpg.connection.Connection object at 0x10a1b2c30>
INFO sqlalchemy.pool.impl.AsyncAdaptedQueuePool Connection <asyncpg.connection.Connection object at 0x10a1b2c30> checked out from pool
INFO sqlalchemy.pool.impl.AsyncAdaptedQueuePool Connection <asyncpg.connection.Connection object at 0x10a1b2c30> being returned to pool
```

---

## 实际使用场景

### 场景 1：开发环境调试

**.env 配置：**
```bash
ENVIRONMENT='dev'
DATABASE_ECHO=True
DATABASE_POOL_ECHO=False
```

**效果：**
- ✅ 打印所有 SQL 语句
- ✅ 方便调试查询逻辑
- ❌ 不打印连接池日志（减少噪音）

---

### 场景 2：性能分析

**.env 配置：**
```bash
DATABASE_ECHO='debug'
DATABASE_POOL_ECHO=True
```

**效果：**
- ✅ 打印 SQL 执行时间
- ✅ 打印查询结果
- ✅ 打印连接池操作
- 🔍 分析慢查询
- 🔍 检查 N+1 查询问题

---

### 场景 3：生产环境

**.env 配置：**
```bash
ENVIRONMENT='prod'
DATABASE_ECHO=False
DATABASE_POOL_ECHO=False
```

**效果：**
- ✅ 不打印任何日志
- ✅ 提升性能
- ✅ 减少日志文件大小

---

## 代码中动态控制日志

### 方法 1：临时启用 SQL 日志

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

# 临时启用 SQL 日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 执行查询
result = await db.execute(select(Demo))
```

---

### 方法 2：为特定查询启用日志

```python
# 使用 execution_options 启用日志
stmt = select(Demo).execution_options(logging_token='slow_query')
result = await db.execute(stmt)
```

---

### 方法 3：自定义日志处理器

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """在执行 SQL 前触发"""
    print(f"执行 SQL: {statement}")
    print(f"参数: {parameters}")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """在执行 SQL 后触发"""
    print(f"执行完成，耗时: {context.execution_time:.4f}s")
```

---

## 日志格式说明

### 标准日志格式

```
<时间戳> <日志级别> <模块> <SQL语句>
<时间戳> <日志级别> <模块> [参数信息] (参数值,)
```

**示例：**
```sql
2026-01-14 12:00:00,123 INFO sqlalchemy.engine.Engine SELECT demo.id FROM demo WHERE demo.deleted = $1
2026-01-14 12:00:00,124 INFO sqlalchemy.engine.Engine [generated in 0.00012s] (0,)
```

**解读：**
- `$1` - PostgreSQL 参数占位符（MySQL 使用 `%s`）
- `[generated in 0.00012s]` - SQL 编译耗时
- `(0,)` - 参数值 `deleted=0`

---

### 缓存 SQL 日志

```sql
INFO sqlalchemy.engine.Engine [cached since 0.001s ago] (0,)
```

**说明：**
- SQLAlchemy 会缓存已编译的 SQL 语句
- 第二次执行相同查询时，会显示 `[cached since ...]`

---

## 性能影响

### DATABASE_ECHO 性能开销

| 设置 | CPU 开销 | I/O 开销 | 适用场景 |
|------|---------|---------|---------|
| `False` | 无 | 无 | 生产环境 |
| `True` | 低 (~1-2%) | 中 | 开发环境 |
| `'debug'` | 中 (~3-5%) | 高 | 调试/性能分析 |

**建议：**
- 开发环境：使用 `True`
- 生产环境：使用 `False`
- 性能分析：临时使用 `'debug'`

---

## 常见问题

### Q1：为什么看不到 SQL 日志？

**检查清单：**
1. ✅ 确认 `.env` 中 `DATABASE_ECHO=True`
2. ✅ 重启了 FastAPI 服务
3. ✅ 确认配置被正确加载（打印 `settings.DATABASE_ECHO`）

**调试代码：**
```python
from backend.core.conf import settings
print(f"DATABASE_ECHO: {settings.DATABASE_ECHO}")
```

---

### Q2：日志太多，如何过滤？

**方法 A：仅打印特定表的查询**

```python
import logging

# 只打印 INFO 级别日志
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 过滤掉连接池日志
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
```

**方法 B：自定义日志过滤器**

```python
class SQLFilter(logging.Filter):
    def filter(self, record):
        # 只记录包含 'demo' 表的查询
        return 'demo' in record.getMessage().lower()

logging.getLogger('sqlalchemy.engine').addFilter(SQLFilter())
```

---

### Q3：如何记录慢查询？

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # 超过 1 秒的查询
        log.warning(f"慢查询 ({total:.2f}s): {statement}")
```

---

### Q4：如何保存 SQL 日志到文件？

**方法 A：使用 Python logging**

```python
import logging

# 配置文件处理器
file_handler = logging.FileHandler('sql.log')
file_handler.setLevel(logging.INFO)

# 配置格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加到 SQLAlchemy logger
logging.getLogger('sqlalchemy.engine').addHandler(file_handler)
```

**方法 B：使用 loguru（推荐）**

项目已使用 loguru，SQL 日志会自动写入日志文件。

---

## 调试技巧

### 1. 查看编译后的 SQL（不执行）

```python
from sqlalchemy.dialects import postgresql

stmt = select(Demo).where(Demo.deleted == 0)

# 查看 PostgreSQL 格式的 SQL
compiled = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
print(compiled)

# 输出：SELECT demo.id, demo.username FROM demo WHERE demo.deleted = 0
```

---

### 2. 打印查询的参数

```python
from sqlalchemy import select

stmt = select(Demo).where(Demo.username == 'test')

# 打印 SQL 和参数
print(f"SQL: {stmt}")
print(f"参数: {stmt.compile().params}")
```

---

### 3. 检测 N+1 查询问题

```python
# 启用 SQL 日志
DATABASE_ECHO=True

# 执行查询
users = await db.execute(select(User))
for user in users.scalars():
    # 如果这里访问关联对象，会触发额外查询
    orders = user.orders  # ❌ N+1 查询

# 查看日志，如果出现多次类似查询，说明存在 N+1 问题

# 解决方案：使用 joinedload
from sqlalchemy.orm import joinedload

stmt = select(User).options(joinedload(User.orders))
users = await db.execute(stmt)
```

---

## 推荐配置

### 开发环境

```bash
# .env
DATABASE_ECHO=True
DATABASE_POOL_ECHO=False
```

### 测试环境

```bash
# .env
DATABASE_ECHO='debug'
DATABASE_POOL_ECHO=True
```

### 生产环境

```bash
# .env
DATABASE_ECHO=False
DATABASE_POOL_ECHO=False
```

---

## 总结

✅ **快速启用**：`.env` 中设置 `DATABASE_ECHO=True`
✅ **调试模式**：使用 `DATABASE_ECHO='debug'` 查看详细信息
✅ **生产环境**：设置为 `False` 提升性能
✅ **性能分析**：结合慢查询监控，优化数据库访问

SQL 日志是开发和调试的重要工具，合理使用可以大大提高开发效率！
