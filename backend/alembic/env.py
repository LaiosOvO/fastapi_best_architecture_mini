from logging.config import fileConfig

from sqlalchemy import engine_from_config, URL
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# 注意：为了避免循环导入，这里直接从 conf 读取配置构建 URL
# 而不是从 backend.database.db 导入

from backend.core.conf import settings
from backend.common.enums import DataBaseType

# 构建数据库 URL（同步驱动，用于 Alembic）
def get_alembic_database_url() -> str:
    """构建 Alembic 使用的同步数据库 URL"""
    # Alembic 默认使用同步驱动
    if DataBaseType.mysql == settings.DATABASE_TYPE:
        drivername = 'mysql+pymysql'
    else:
        drivername = 'postgresql+psycopg2'

    url = URL.create(
        drivername=drivername,
        username=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_SCHEMA,
    )
    return url.render_as_string(hide_password=False).replace('%', '%%')

# 导入模型元数据
from backend.common.model import (
    MappedBase,
    TimeZone,
    CompressedJSON,
    EncryptedString,
    HashedPassword,
    MaskedString,
)

# 导入第三方扩展类型（用于 render_item）
from pgvector.sqlalchemy import Vector
from geoalchemy2 import Geometry

# 重要：必须显式导入所有模型，才能注册到 metadata 中
# 否则 Alembic autogenerate 无法检测到这些表
from backend.app.demo.model import Demo, Location, Document

target_metadata = MappedBase.metadata

# 设置数据库 URL
alembic_config.set_main_option('sqlalchemy.url', get_alembic_database_url())

# 需要忽略的表（PostGIS/PGVector 扩展的系统表）
EXCLUDE_TABLES = {
    'spatial_ref_sys',  # PostGIS 空间参考系统表
    'layer',            # PostGIS topology 层表
    'topology',         # PostGIS topology 表
}

def include_object(object, name, type_, reflected, compare_to):
    """
    过滤 Alembic autogenerate 检测的对象
    返回 False 表示忽略该对象
    """
    if type_ == 'table' and name in EXCLUDE_TABLES:
        return False
    return True


def render_item(type_, obj, autogen_context):
    """
    自定义类型渲染函数
    将自定义 TypeDecorator 和第三方类型转换为正确的渲染格式
    """
    if type_ == 'type':
        # 处理自定义类型装饰器
        if isinstance(obj, TimeZone):
            return 'sa.DateTime(timezone=True)'
        if isinstance(obj, CompressedJSON):
            return 'sa.LargeBinary()'
        if isinstance(obj, EncryptedString):
            return 'sa.Text()'
        if isinstance(obj, HashedPassword):
            return 'sa.String(128)'
        if isinstance(obj, MaskedString):
            return 'sa.String(256)'

        # 处理 PGVector 类型
        if isinstance(obj, Vector):
            # 添加导入并返回正确的类型字符串
            autogen_context.imports.add('from pgvector.sqlalchemy import Vector')
            return f'Vector({obj.dim})'

        # 处理 GeoAlchemy2 类型
        if isinstance(obj, Geometry):
            autogen_context.imports.add('from geoalchemy2 import Geometry')
            params = []
            if obj.geometry_type:
                params.append(f"geometry_type='{obj.geometry_type}'")
            if obj.srid != -1:
                params.append(f'srid={obj.srid}')
            # 关键：禁用自动创建索引，由 Alembic 单独管理
            params.append('spatial_index=False')
            return f"Geometry({', '.join(params)})"

    # 返回 False 表示使用默认渲染
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
