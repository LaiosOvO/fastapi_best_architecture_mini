"""
演示模型 - 展示 SQLAlchemy 各种字段类型

包含:
- JSON/JSONB 类型
- 加密/解密字段
- 枚举类型
- 数组类型
- UUID 类型
- 日期/时间类型
- 大数值类型
- 自定义类型装饰器
"""

import enum

from datetime import date, time, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone,CompressedJSON,EncryptedString,HashedPassword,MaskedString, id_key
from backend.core.conf import settings
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone




# ==================== 枚举类型 ====================

class DemoStatus(enum.IntEnum):
    """演示状态枚举（整数）"""
    DRAFT = 0       # 草稿
    PENDING = 1     # 待审核
    APPROVED = 2    # 已通过
    REJECTED = 3    # 已拒绝
    ARCHIVED = 4    # 已归档


class DemoType(enum.Enum):
    """演示类型枚举（字符串）"""
    ARTICLE = 'article'
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'


# ==================== 演示模型 ====================

class Demo(Base):
    """演示表 - 展示各种字段类型"""

    __tablename__ = 'demo'

    id: Mapped[id_key] = mapped_column(init=False)

    # ========== 必填字段（虽然有默认值，但业务上是必填）==========
    username: Mapped[str] = mapped_column(sa.String(64), default='', sort_order=-998, comment='用户名')
    # ========== 可选字段（有默认值）==========
    # UUID
    uuid: Mapped[str] = mapped_column(
        sa.String(64),
        init=False,
        default_factory=uuid4_str,
        unique=True,
        comment='UUID',
    )
    # ---------- 基础类型 ----------
    description: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='描述')
    status: Mapped[int] = mapped_column(default=1, index=True, comment='状态(0停用 1正常)')
    is_superuser: Mapped[bool] = mapped_column(default=False, comment='超级权限(0否 1是)')
    # ---------- 数值类型 ----------
    count: Mapped[int] = mapped_column(default=0, comment='计数')
    score: Mapped[float | None] = mapped_column(sa.Float, default=None, comment='分数')
    price: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2), default=None, comment='价格')
    dept_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='部门ID')
    # ---------- 日期时间类型 ----------
    birth_date: Mapped[date | None] = mapped_column(sa.Date, default=None, comment='出生日期')
    start_time: Mapped[time | None] = mapped_column(sa.Time, default=None, comment='开始时间')
    last_login_time: Mapped[datetime | None] = mapped_column(
        TimeZone,
        init=False,
        onupdate=timezone.now,
        comment='上次登录时间',
    )
    deleted: Mapped[int | None] = mapped_column(default=0,comment="逻辑删除")
    ext: Mapped[dict | None] = mapped_column(JSONB,default=None,comment='扩展字段')
    # ---------- JSON/JSONB 类型 ----------
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        default=None,
        comment='元数据 (JSONB，支持索引查询)',
    )
    config_json: Mapped[dict | None] = mapped_column(
        sa.JSON,
        default=None,
        comment='配置 (普通JSON)',
    )
    settings_json: Mapped[dict] = mapped_column(
        JSONB,
        default_factory=dict,
        comment='设置 (带默认值)',
    )
    # 压缩 JSON（适合大数据）
    large_data: Mapped[dict | None] = mapped_column(
        CompressedJSON,
        default=None,
        comment='大数据 (gzip压缩)',
    )
    # ---------- 数组类型（PostgreSQL）----------
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(sa.String(64)),
        default=None,
        comment='标签数组',
    )
    scores: Mapped[list[int] | None] = mapped_column(
        ARRAY(sa.Integer),
        default=None,
        comment='分数数组',
    )
    # ---------- 加密类型 ----------
    salt: Mapped[bytes | None] = mapped_column(
        sa.LargeBinary(255),
        default=None,
        comment='加密盐(二进制)',
    )
    secret_key: Mapped[str | None] = mapped_column(
        EncryptedString(),
        default=None,
        comment='密钥 (Fernet加密)',
    )
    api_token: Mapped[str | None] = mapped_column(
        EncryptedString(),
        default=None,
        comment='API Token (Fernet加密)',
    )
    # ---------- 哈希类型 ----------
    password_hash: Mapped[str | None] = mapped_column(
        HashedPassword(),
        default=None,
        comment='密码 (SHA256哈希)',
    )
    # ---------- 脱敏类型 ----------
    phone: Mapped[str | None] = mapped_column(
        MaskedString(mask_start=3, mask_end=4),
        default=None,
        comment='手机号 (读取时脱敏)',
    )
    id_card: Mapped[str | None] = mapped_column(
        MaskedString(mask_start=6, mask_end=4),
        default=None,
        comment='身份证 (读取时脱敏)',
    )
    # ---------- 网络类型 ----------
    ip_address: Mapped[str | None] = mapped_column(
        sa.String(45),
        default=None,
        comment='IP地址',
    )

    # 关联文档IDs - 存储为数组
    document_ids: Mapped[list[int] | None] = mapped_column(
        ARRAY(sa.Integer),
        default=None,
        comment='关联文档ID列表',
    )

    __table_args__ = (
        # JSONB GIN 索引（优化 JSON 查询）
        sa.Index('idx_demo_metadata_gin', 'metadata_json', postgresql_using='gin'),
        # 数组 GIN 索引（优化数组查询）
        sa.Index('idx_demo_tags_gin', 'tags', postgresql_using='gin'),
        sa.Index('idx_demo_document_ids_gin', 'document_ids', postgresql_using='gin'),
        {'comment': '演示表 - 展示各种字段类型'},
    )


# ==================== 使用示例 ====================

demo = Demo(
    username='test_user',
    description='测试用户',

    # JSON 类型
    metadata_json={'role': 'admin', 'permissions': ['read', 'write']},
    config_json={'theme': 'dark', 'language': 'zh-CN'},
    settings_json={'notifications': True},

    # 数组类型
    tags=['python', 'fastapi', 'sqlalchemy'],
    scores=[90, 85, 95],

    # 加密字段（自动加密存储）
    secret_key='my-secret-api-key',
    api_token='sk-xxxxxxxxxxxxx',

    # 哈希字段（自动哈希存储）
    password_hash='user_password_123',

    # 脱敏字段（存储原值，读取时脱敏）
    phone='13812345678',      # 读取时: 138****5678
    id_card='110101199001011234',  # 读取时: 110101********1234
)