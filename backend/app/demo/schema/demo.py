import random

from decimal import Decimal

from google.protobuf.descriptor import FieldDescriptor
from pydantic import BaseModel, ConfigDict, EmailStr, Field, validate_email

from backend.common.schema import SchemaBase, ser_string
from backend.utils.timezone import timezone
from datetime import date, time, datetime


class GetDemoDetail(SchemaBase):
    """Demo 详情响应 Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    uuid: str
    description: str | None = None
    status: int
    is_superuser: bool
    count: int
    score: float | None = None
    price: Decimal | None = None
    dept_id: int | None = None
    birth_date: date | None = None
    start_time: time | None = None
    last_login_time: datetime | None = None
    metadata_json: dict | None = None
    config_json: dict | None = None
    settings_json: dict
    large_data: dict | None = None
    tags: list[str] | None = None
    scores: list[int] | None = None
    salt: bytes | None = None
    secret_key: str | None = None
    api_token: str | None = None
    password_hash: str | None = None
    phone: str | None = None
    id_card: str | None = None
    ip_address: str | None = None
    document_ids: list[int] | None = None
    created_time: datetime
    updated_time: datetime | None = None


class AddDemoParam(SchemaBase):
    """添加用户参数"""
    username: str | None = Field(default='test_user', description='昵称'),
    description: str| None = Field(default='test user',description='测试描述')

    # JSON 类型
    metadata_json: dict | None = Field(default={'role': 'admin', 'permissions': ['read', 'write']},description="meta json测试" )
    config_json: dict | None = Field(default={'theme': 'dark', 'language': 'zh-CN'}),
    settings_json: dict |None = Field(default={'notifications': True}),

    # 数组类型
    tags: list[str] | None = Field(default=['python', 'fastapi', 'sqlalchemy']),
    scores:list[int] | None = Field(default=[90, 85, 95]),

    # 加密字段（自动加密存储）
    secret_key: str | None = Field(default='my-secret-api-key'),
    api_token: str | None = Field(default='sk-xxxxxxxxxxxxx'),

    # 哈希字段（自动哈希存储）
    password_hash: str | None = Field(default='user_password_123'),

    # 脱敏字段（存储原值，读取时脱敏）
    phone: str | None = Field(default='13812345678'),      # 读取时: 138****5678
    id_card: str | None = Field(default='110101199001011234'),  # 读取时: 110101********1234

    score: float | None = Field(default=0.13)
    price: Decimal | None = Field(default=3.14)

    birth_date: date | None = Field(default_factory=lambda: timezone.now().date())
    start_time: time | None = Field(default_factory=lambda: timezone.now().time())
    document_ids: list[int] | None = Field(default=[], description='关联文档ID列表')

    @staticmethod
    def mock():
        req = AddDemoParam(
            username='test_user'+ random.randint(100,10000).__str__(),
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
            phone='13812345678',  # 读取时: 138****5678
            id_card='110101199001011234',  # 读取时: 110101********1234

        )

        return req


