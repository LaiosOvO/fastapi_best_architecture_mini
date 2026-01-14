# 数据库功能使用指南

本目录包含数据库相关的功能文档。

## 目录

1. [逻辑删除.md](./逻辑删除.md) - 全局逻辑删除（软删除）功能
2. [SQL日志配置.md](./SQL日志配置.md) - SQLAlchemy SQL 日志配置

---

## 快速开始

### 1. 启用 SQL 日志

编辑 `.env` 文件：

```bash
# .env
DATABASE_ECHO=True          # 打印 SQL 语句
DATABASE_POOL_ECHO=False    # 不打印连接池日志
```

重启服务后，控制台会打印所有执行的 SQL：

```sql
INFO sqlalchemy.engine.Engine SELECT demo.id, demo.username FROM demo WHERE demo.deleted = 0
INFO sqlalchemy.engine.Engine [generated in 0.00012s] (0,)
```

---

### 2. 使用逻辑删除

所有模型自动包含 `deleted` 字段，查询时自动过滤已删除记录：

```python
# 正常查询（自动过滤 deleted=0）
result = await db.execute(select(Demo))
demos = result.scalars().all()  # 只返回未删除的记录

# 软删除
from backend.common.soft_delete import soft_delete_method
demo = await db.get(Demo, 1)
soft_delete_method(demo)
await db.commit()

# 查询包括已删除的记录
from backend.common.soft_delete import include_deleted
stmt = include_deleted(select(Demo))
result = await db.execute(stmt)
all_demos = result.scalars().all()  # 包含已删除的记录
```

---

## 功能特性

### ✅ 全局逻辑删除

- 所有继承 `Base` 的模型自动包含 `deleted` 字段
- 查询时自动过滤 `deleted=0`
- 提供软删除、恢复、查询全部等工具函数
- 详见：[逻辑删除.md](./逻辑删除.md)

### ✅ SQL 日志打印

- 支持打印 SQL 语句、参数、执行时间
- 支持打印连接池操作日志
- 灵活的日志级别配置（`True`/`False`/`'debug'`）
- 详见：[SQL日志配置.md](./SQL日志配置.md)

---

## 常见问题

### Q: 如何临时禁用逻辑删除过滤？

```python
from backend.common.soft_delete import include_deleted

# 查询包括已删除的记录
stmt = include_deleted(select(Demo))
result = await db.execute(stmt)
```

---

### Q: 如何恢复已删除的记录？

```python
from backend.common.soft_delete import restore_deleted, include_deleted

# 先查询包括已删除的记录
stmt = include_deleted(select(Demo).where(Demo.id == 1))
result = await db.execute(stmt)
demo = result.scalar_one_or_none()

# 恢复
restore_deleted(demo)
await db.commit()
```

---

### Q: 生产环境是否应该启用 SQL 日志？

**不建议**。SQL 日志会影响性能（约 1-5%），且会产生大量日志文件。

建议配置：
- **开发环境**：`DATABASE_ECHO=True`
- **测试环境**：`DATABASE_ECHO='debug'`
- **生产环境**：`DATABASE_ECHO=False`

---

### Q: 如何查看某个查询的实际 SQL？

**方法 1：启用 SQL 日志（推荐）**

```bash
# .env
DATABASE_ECHO=True
```

**方法 2：手动编译查询**

```python
from sqlalchemy.dialects import postgresql

stmt = select(Demo).where(Demo.deleted == 0)
compiled = stmt.compile(
    dialect=postgresql.dialect(),
    compile_kwargs={"literal_binds": True}
)
print(compiled)
```

---

## 最佳实践

### 1. 开发调试

```bash
# .env
DATABASE_ECHO=True
DATABASE_POOL_ECHO=False
```

- ✅ 打印 SQL 语句，方便调试
- ✅ 不打印连接池日志，减少噪音

---

### 2. 性能分析

```bash
# .env
DATABASE_ECHO='debug'
DATABASE_POOL_ECHO=True
```

- ✅ 打印详细的 SQL 信息
- ✅ 打印连接池操作
- 🔍 分析慢查询和 N+1 问题

---

### 3. 生产环境

```bash
# .env
DATABASE_ECHO=False
DATABASE_POOL_ECHO=False
```

- ✅ 关闭所有数据库日志
- ✅ 提升性能
- ✅ 减少日志文件大小

---

### 4. 软删除场景

**推荐使用软删除的场景：**
- ✅ 用户数据（防止误删）
- ✅ 订单记录（需要审计）
- ✅ 文章/内容（支持恢复）
- ✅ 重要业务数据

**不推荐使用软删除的场景：**
- ❌ 日志表（数据量大，无需恢复）
- ❌ 临时数据（无保留价值）
- ❌ 缓存数据（可重新生成）

---

## 数据库迁移注意事项

### 添加 deleted 字段

如果你的数据库中已有表，需要添加 `deleted` 字段：

```sql
-- PostgreSQL
ALTER TABLE your_table ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0;
CREATE INDEX idx_your_table_deleted ON your_table(deleted);

-- MySQL
ALTER TABLE your_table ADD COLUMN deleted INT NOT NULL DEFAULT 0;
CREATE INDEX idx_your_table_deleted ON your_table(deleted);
```

### 使用 Alembic 迁移

```python
# alembic/versions/xxx_add_deleted_field.py

def upgrade():
    op.add_column('demo', sa.Column('deleted', sa.Integer(), nullable=False, server_default='0'))
    op.create_index(op.f('ix_demo_deleted'), 'demo', ['deleted'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_demo_deleted'), table_name='demo')
    op.drop_column('demo', 'deleted')
```

---

## 技术架构

### 逻辑删除实现原理

```python
# 1. SoftDeleteMixin 添加 deleted 字段
class SoftDeleteMixin(MappedAsDataclass):
    deleted: Mapped[int] = mapped_column(default=0, index=True)

# 2. Base 模型继承 SoftDeleteMixin
class Base(DataClassBase, DateTimeMixin, SoftDeleteMixin):
    __abstract__ = True

# 3. SQLAlchemy 事件监听器自动过滤
@event.listens_for(session_factory, 'do_orm_execute')
def _soft_delete_filter(execute_state):
    if execute_state.is_select and not include_deleted:
        statement = statement.where(entity.deleted == 0)
```

### SQL 日志实现原理

```python
# 创建引擎时传递 echo 参数
engine = create_async_engine(
    url,
    echo=settings.DATABASE_ECHO,        # SQL 语句日志
    echo_pool=settings.DATABASE_POOL_ECHO,  # 连接池日志
)
```

---

## 相关资源

- SQLAlchemy 官方文档：https://docs.sqlalchemy.org/
- FastAPI 官方文档：https://fastapi.tiangolo.com/
- 项目架构文档：`../01-项目架构总览.md`

---

## 反馈与贡献

如有问题或建议，请联系开发团队或提交 Issue。
