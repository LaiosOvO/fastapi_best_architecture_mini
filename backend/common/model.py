from datetime import datetime
from typing import Annotated

import sqlalchemy as sa

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy import BigInteger, DateTime, Text, TypeDecorator
from sqlalchemy.dialects.mysql import LONGTEXT

from backend.common.enums import DataBaseType, PrimaryKeyType
from backend.utils.timezone import timezone
# from backend.utils.snowflake import snowflake
from backend.core.conf import settings

import base64
import hashlib
import json
import secrets

snowflake = {}

id_key = Annotated[
    int,
    mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
        sort_order=-999,
        comment='主键 ID',
    )
    if PrimaryKeyType.autoincrement == settings.DATABASE_PK_MODE
    # 雪花算法 Mapped 类型主键
    # 详情：https://fastapi-practices.github.io/fastapi_best_architecture_docs/backend/reference/pk.html
    else mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        default=snowflake.generate,
        sort_order=-999,
        comment='雪花算法主键 ID',
    ),
]

class TimeZone(TypeDecorator[datetime]):
    """PostgreSQL、MySQL 兼容性时区感知类型"""

    impl = DateTime(timezone=True)
    cache_ok = True

    @property
    def python_type(self) -> type[datetime]:
        return datetime

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:  # noqa: ANN001
        if value is not None and value.utcoffset() != timezone.now().utcoffset():
            # TODO 处理夏令时偏移
            value = timezone.from_datetime(value)
        return value

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:  # noqa: ANN001
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.tz_info)
        return value



class UniversalText(TypeDecorator[str]):
    """PostgreSQL、MySQL 兼容性（长）文本类型"""

    impl = LONGTEXT if DataBaseType.mysql == settings.DATABASE_TYPE else Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:  # noqa: ANN001
        return value

    def process_result_value(self, value: str | None, dialect) -> str | None:  # noqa: ANN001
        return value


# Mixin: 一种面向对象编程概念, 使结构变得更加清晰, `Wiki <https://en.wikipedia.org/wiki/Mixin/>`__
class UserMixin(MappedAsDataclass):
    """用户 Mixin 数据类"""

    created_by: Mapped[int] = mapped_column(sort_order=998, comment='创建者')
    updated_by: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=998, comment='修改者')



class DateTimeMixin(MappedAsDataclass):
    """日期时间 Mixin 数据类"""

    created_time: Mapped[datetime] = mapped_column(
        TimeZone,
        init=False,
        default_factory=timezone.now,
        sort_order=999,
        comment='创建时间',
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        TimeZone,
        init=False,
        default=None,
        onupdate=timezone.now,
        sort_order=999,
        comment='更新时间',
    )


class SoftDeleteMixin(MappedAsDataclass):
    """逻辑删除 Mixin 数据类"""

    deleted: Mapped[int] = mapped_column(
        sa.Integer,
        init=False,
        default=0,
        index=True,
        sort_order=1000,  # 确保在所有其他字段之后
        comment='逻辑删除(0否 1是)',
    )



class MappedBase(AsyncAttrs, DeclarativeBase):
    """
    声明式基类, 作为所有基类或数据模型类的父类而存在

    `AsyncAttrs <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs>`__

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__

    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    """

    @declared_attr.directive
    def __tablename__(self) -> str:
        """生成表名"""
        return self.__name__.lower()

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """表配置"""
        return {'comment': self.__doc__ or ''}


class DataClassBase(MappedAsDataclass, MappedBase):
    """
    声明性数据类基类, 带有数据类集成,
    允许使用更高级配置, 但你必须注意它的一些特性,
    尤其是和 DeclarativeBase 一起使用时

    `MappedAsDataclass <https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses>`__
    """

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin, SoftDeleteMixin):
    """
    声明性数据类基类, 带有数据类集成, 并包含 MiXin 数据类基础表结构
    包含创建时间、更新时间和逻辑删除字段
    """

    __abstract__ = True


# ==================== 自定义类型装饰器 ====================

class EncryptedString(TypeDecorator[str]):
    """
    加密字符串类型 (使用 Fernet 对称加密)

    适用于存储敏感信息如：
    - API 密钥
    - 第三方凭证
    - 敏感配置

    注意：需要安装 cryptography: pip install cryptography
    """
    impl = sa.Text
    cache_ok = True

    def __init__(self, secret_key: str | None = None):
        super().__init__()
        self._secret_key = secret_key

    def _get_fernet(self):
        """延迟初始化 Fernet"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            key = (self._secret_key or settings.TOKEN_SECRET_KEY).encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fba_salt_v1',
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(key))
            return Fernet(derived_key)
        except ImportError:
            return None

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """存储时加密"""
        if value is None:
            return None
        fernet = self._get_fernet()
        if fernet is None:
            # 如果没有安装 cryptography，使用 base64 编码
            return base64.b64encode(value.encode()).decode()
        encrypted = fernet.encrypt(value.encode())
        return encrypted.decode()

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """读取时解密"""
        if value is None:
            return None
        fernet = self._get_fernet()
        if fernet is None:
            try:
                return base64.b64decode(value.encode()).decode()
            except Exception:
                return value
        try:
            decrypted = fernet.decrypt(value.encode())
            return decrypted.decode()
        except Exception:
            return value


class HashedPassword(TypeDecorator[str]):
    """
    哈希密码类型 (SHA256 + 盐值)

    适用于：
    - 用户密码
    - PIN 码

    注意：这是单向哈希，无法解密，只能验证
    """
    impl = sa.String(128)
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """存储时哈希"""
        if value is None:
            return None
        # 如果已经是哈希值（128字符），直接返回
        if len(value) == 128 and all(c in '0123456789abcdef' for c in value.lower()):
            return value
        # 生成盐值 + 哈希
        salt = secrets.token_hex(32)
        hashed = hashlib.sha256((salt + value).encode()).hexdigest()
        return salt + hashed

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """读取时直接返回哈希值"""
        return value

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        if not hashed_password or len(hashed_password) != 128:
            return False
        salt = hashed_password[:64]
        stored_hash = hashed_password[64:]
        computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)


class CompressedJSON(TypeDecorator[dict]):
    """
    压缩 JSON 类型

    对大型 JSON 数据进行 gzip 压缩存储，节省空间
    """
    impl = sa.LargeBinary
    cache_ok = True

    def process_bind_param(self, value: dict | None, dialect) -> bytes | None:
        """存储时压缩"""
        if value is None:
            return None
        import gzip
        json_str = json.dumps(value, ensure_ascii=False)
        return gzip.compress(json_str.encode())

    def process_result_value(self, value: bytes | None, dialect) -> dict | None:
        """读取时解压"""
        if value is None:
            return None
        import gzip
        json_str = gzip.decompress(value).decode()
        return json.loads(json_str)


class MaskedString(TypeDecorator[str]):
    """
    脱敏字符串类型

    存储原值，读取时自动脱敏，适用于：
    - 手机号: 138****5678
    - 身份证: 110101********1234
    - 银行卡: 6222****1234
    """
    impl = sa.String(256)
    cache_ok = True

    def __init__(self, mask_start: int = 3, mask_end: int = 4, mask_char: str = '*'):
        super().__init__()
        self.mask_start = mask_start
        self.mask_end = mask_end
        self.mask_char = mask_char

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """存储原值"""
        return value

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """读取时脱敏"""
        if value is None or len(value) <= self.mask_start + self.mask_end:
            return value
        mask_length = len(value) - self.mask_start - self.mask_end
        return value[:self.mask_start] + self.mask_char * mask_length + value[-self.mask_end:]
