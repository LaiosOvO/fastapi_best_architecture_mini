"""
Database module initialization
"""
from .db import *
from .redis import redis_client
from .mongo import mongo_client

__all__ = [
    'redis_client',
    'mongo_client',
]
# Extend with items from db module
__all__.extend([name for name in dir() if not name.startswith('_')])