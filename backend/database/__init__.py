"""
Database module initialization

注意：为了避免循环导入，不要在此处导入 db 模块
循环链：model.py → snowflake.py → database/__init__.py → db.py → model.py
请直接使用 `from backend.database.db import xxx` 导入
"""
from .redis import redis_client
from .mongo import mongo_client

__all__ = [
    'redis_client',
    'mongo_client',
]