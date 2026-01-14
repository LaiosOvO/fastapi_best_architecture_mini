"""
MongoDB 客户端封装
"""
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError

from backend.common.log import log
from backend.core.conf import settings


class MongoDBCli:
    """MongoDB 客户端"""

    def __init__(self) -> None:
        """初始化 MongoDB 客户端"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.uri = f"mongodb://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}/{settings.MONGODB_DATABASE}?authSource=admin"

    async def open(self) -> None:
        """初始化连接"""
        try:
            self.client = AsyncIOMotorClient(
                self.uri,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT * 1000,  # 超时时间（毫秒）
                connectTimeoutMS=settings.MONGODB_TIMEOUT * 1000,
                socketTimeoutMS=settings.MONGODB_TIMEOUT * 1000,
                maxPoolSize=100,  # 连接池大小
                minPoolSize=10,   # 最小连接池大小
            )
            self.database = self.client[settings.MONGODB_DATABASE]

            # 测试连接
            await self.client.admin.command('ping')
            log.info('✅ MongoDB 连接成功')
        except ServerSelectionTimeoutError:
            log.error('❌ MongoDB 连接超时')
            sys.exit()
        except ConnectionFailure as e:
            log.error(f'❌ MongoDB 连接失败: {e}')
            sys.exit()
        except Exception as e:
            log.error(f'❌ MongoDB 连接异常: {e}')
            sys.exit()

    async def close(self) -> None:
        """关闭连接"""
        if self.client:
            self.client.close()
            log.info('🔒 MongoDB 连接已关闭')

    async def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """获取集合对象"""
        if self.database is None:
            raise RuntimeError("MongoDB 未连接，请先调用 open()")
        return self.database[collection_name]

    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """插入单个文档"""
        collection = await self.get_collection(collection_name)
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """插入多个文档"""
        collection = await self.get_collection(collection_name)
        result = await collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def find_one(self, collection_name: str, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """查找单个文档"""
        collection = await self.get_collection(collection_name)
        return await collection.find_one(query, projection=projection)

    async def find(self, collection_name: str, query: Dict[str, Any] = None, skip: int = 0, limit: int = 0,
                   sort: Optional[List[tuple]] = None, projection: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """查找多个文档"""
        collection = await self.get_collection(collection_name)
        query = query or {}
        cursor = collection.find(query, projection=projection)

        if sort:
            cursor.sort(sort)
        if skip > 0:
            cursor.skip(skip)
        if limit > 0:
            cursor.limit(limit)

        return await cursor.to_list(length=limit or None)

    async def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> int:
        """更新单个文档"""
        collection = await self.get_collection(collection_name)
        # Check if update already contains operators like $set, $inc, etc.
        if any(key.startswith('$') for key in update.keys()):
            # Update dict already contains MongoDB operators
            result = await collection.update_one(query, update, upsert=upsert)
        else:
            # Wrap in $set operator
            result = await collection.update_one(query, {"$set": update}, upsert=upsert)
        return result.modified_count

    async def update_many(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """更新多个文档"""
        collection = await self.get_collection(collection_name)
        # Check if update already contains operators like $set, $inc, etc.
        if any(key.startswith('$') for key in update.keys()):
            # Update dict already contains MongoDB operators
            result = await collection.update_many(query, update)
        else:
            # Wrap in $set operator
            result = await collection.update_many(query, {"$set": update})
        return result.modified_count

    async def replace_one(self, collection_name: str, query: Dict[str, Any], document: Dict[str, Any], upsert: bool = False) -> int:
        """替换单个文档（完全替换，不使用更新操作符）"""
        collection = await self.get_collection(collection_name)
        result = await collection.replace_one(query, document, upsert=upsert)
        return result.modified_count

    async def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """删除单个文档"""
        collection = await self.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result.deleted_count

    async def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """删除多个文档"""
        collection = await self.get_collection(collection_name)
        result = await collection.delete_many(query)
        return result.deleted_count

    async def count_documents(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """统计文档数量"""
        collection = await self.get_collection(collection_name)
        return await collection.count_documents(query or {})

    async def create_index(self, collection_name: str, keys: Union[str, List[tuple]], **kwargs) -> str:
        """创建索引"""
        collection = await self.get_collection(collection_name)
        return await collection.create_index(keys, **kwargs)

    async def drop_collection(self, collection_name: str) -> None:
        """删除集合"""
        collection = await self.get_collection(collection_name)
        await collection.drop()

    async def aggregate(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """聚合查询"""
        collection = await self.get_collection(collection_name)
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def distinct(self, collection_name: str, field: str, query: Optional[Dict[str, Any]] = None) -> List[Any]:
        """获取字段的唯一值"""
        collection = await self.get_collection(collection_name)
        return await collection.distinct(field, query)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator:
        """获取数据库会话，用于事务操作"""
        if self.client is None:
            raise RuntimeError("MongoDB 未连接，请先调用 open()")
        async with await self.client.start_session() as session:
            yield session


# 创建 MongoDB 客户端单例
mongo_client: MongoDBCli = MongoDBCli()