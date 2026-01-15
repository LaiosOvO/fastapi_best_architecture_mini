# Alembic 数据库迁移集成指南

## 1. 概述

Alembic 是 SQLAlchemy 的轻量级数据库迁移工具，用于管理数据库模式的版本控制。它允许开发者通过 Python 脚本跟踪数据库模式的变化，并在不同环境中应用这些变化。

## 2. 项目中的 Alembic 配置

### 2.1 目录结构
```
backend/
├── alembic/
│   ├── env.py              # Alembic 环境配置
│   ├── script.py.mako      # 迁移脚本模板
│   ├── versions/           # 迁移版本文件
│   └── README.md
├── alembic.ini             # Alembic 配置文件
├── core/
│   └── path_conf.py        # 路径配置
└── database/
    └── db.py              # 数据库配置
```

### 2.2 核心配置文件

**alembic.ini** - 主配置文件
```ini
[alembic]
script_location = alembic
file_template = %%(year)d-%%(month).2d-%%(day).2d-%%(hour).2d_%%(minute).2d_%%(second).2d-%%(rev)s_%%(slug)s
prepend_sys_path = .
version_path_separator = os
```

**env.py** - 环境配置文件
```python
# 配置 SQLAlchemy URL
alembic_config.set_main_option(
    'sqlalchemy.url',
    SQLALCHEMY_DATABASE_URL.render_as_string(hide_password=False).replace('%', '%%'),
)

# 使用项目的模型元数据
target_metadata = MappedBase.metadata
```

## 3. 安装和初始化

### 3.1 安装 Alembic
```bash
pip install alembic
```

### 3.2 初始化 Alembic (如果尚未初始化)
```bash
# 在项目根目录执行
cd backend
alembic init alembic
```

## 4. 配置数据库连接

### 4.1 修改 alembic.ini
```ini
# 将此行替换为实际的数据库连接字符串
sqlalchemy.url = postgresql+asyncpg://user:password@localhost/dbname
```

### 4.2 使用项目配置
在 `env.py` 中，项目已经配置为使用现有的数据库配置：
```python
from backend.database.db import SQLALCHEMY_DATABASE_URL

alembic_config.set_main_option(
    'sqlalchemy.url',
    SQLALCHEMY_DATABASE_URL.render_as_string(hide_password=False).replace('%', '%%'),
)
```

## 5. 模型映射配置

### 5.1 在 env.py 中配置目标元数据
```python
from backend.common.model import MappedBase

# 使用项目的模型基类
target_metadata = MappedBase.metadata
```

### 5.2 确保模型继承 MappedBase
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from backend.common.model import id_key

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[id_key] = mapped_column(init=False)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
```

## 6. 生成迁移脚本

### 6.1 自动检测模型变更
```bash
# 生成迁移脚本（自动检测模型变更）
alembic revision --autogenerate -m "描述性消息"
```

### 6.2 手动创建空迁移脚本
```bash
# 创建空的迁移脚本
alembic revision -m "描述性消息"
```

## 7. 应用迁移

### 7.1 升级到最新版本
```bash
# 应用所有待处理的迁移
alembic upgrade head
```

### 7.2 升级到特定版本
```bash
# 升级到特定版本
alembic upgrade abc123def456

# 升级到下一个版本
alembic upgrade +1

# 降级到上一个版本
alembic downgrade -1

# 降级到初始状态
alembic downgrade base
```

### 7.3 查看当前版本
```bash
# 查看当前数据库版本
alembic current

# 查看历史版本
alembic history

# 查看历史版本详细信息
alembic history --verbose
```

## 8. 项目特定配置

### 8.1 异步数据库支持
项目使用异步数据库连接，env.py 配置如下：
```python
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

### 8.2 自动跳过无变更迁移
```python
def process_revision_directives(context, revision, directives) -> None:
    if alembic_config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            print('\nNo changes in model detected')
```

## 9. 常用命令

### 9.1 开发流程
```bash
# 1. 修改模型后生成迁移
alembic revision --autogenerate -m "添加用户表字段"

# 2. 检查生成的迁移脚本
# 编辑 alembic/versions/xxx_add_user_field.py

# 3. 应用迁移
alembic upgrade head

# 4. 查看当前状态
alembic current
```

### 9.2 生产环境部署
```bash
# 部署前检查
alembic check

# 应用所有迁移
alembic upgrade head

# 验证版本
alembic current
```

## 10. 迁移脚本示例

### 10.1 自动生成的迁移脚本
```python
"""添加用户邮箱字段

Revision ID: abc123def456
Revises: def456ghi789
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = 'def456ghi789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 升级操作
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))


def downgrade() -> None:
    # 降级操作
    op.drop_column('users', 'email')
```

### 10.2 手动编写的复杂迁移
```python
def upgrade() -> None:
    # 创建新表
    op.create_table('new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 添加索引
    op.create_index('ix_new_table_name', 'new_table', ['name'])
    
    # 修改现有列
    op.alter_column('users', 'username', type_=sa.String(100))


def downgrade() -> None:
    op.drop_index('ix_new_table_name')
    op.drop_table('new_table')
    op.alter_column('users', 'username', type_=sa.String(50))
```

## 11. 最佳实践

### 11.1 迁移命名规范
- 使用描述性的提交消息
- 避免在生产环境中使用 `--autogenerate`
- 在应用迁移前先审查生成的脚本

### 11.2 数据迁移
```python
def upgrade() -> None:
    # 添加新列
    op.add_column('users', sa.Column('status', sa.String(20), default='active'))
    
    # 更新现有数据
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET status = 'active' WHERE status IS NULL"))
    
    # 修改列为非空
    op.alter_column('users', 'status', nullable=False)
```

### 11.3 环境特定配置
```python
# 根据环境使用不同的配置
import os

if os.getenv('ENVIRONMENT') == 'production':
    # 生产环境特殊配置
    pass
```

## 12. 故障排除

### 12.1 常见问题
```bash
# 如果遇到 "Can't locate revision identified by..." 错误
alembic stamp head  # 手动设置版本

# 如果迁移脚本损坏
alembic downgrade -1  # 先降级
# 修复脚本
alembic upgrade +1    # 再升级
```

### 12.2 版本冲突解决
```bash
# 查看分支情况
alembic branches

# 合并分支
alembic merge -m "merge branch"
```

## 13. 项目集成脚本

项目提供了便捷的迁移脚本 `migrate.sh`：
```bash
#!/usr/bin/env bash

# 自动检测变更并应用迁移
alembic revision --autogenerate
alembic upgrade head
```

使用方式：
```bash
cd backend
chmod +x migrate.sh
./migrate.sh
```

## 14. 与 FastAPI 集成

### 14.1 应用启动时检查迁移
```python
import asyncio
from alembic.config import Config
from alembic import command

async def check_migrations():
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        print("数据库迁移完成")
    except Exception as e:
        print(f"迁移失败: {e}")

# 在应用启动时调用
if __name__ == "__main__":
    asyncio.run(check_migrations())
```

通过以上配置和流程，Alembic 可以有效地管理 FastAPI 项目的数据库模式变更，确保在不同环境中数据库结构的一致性。