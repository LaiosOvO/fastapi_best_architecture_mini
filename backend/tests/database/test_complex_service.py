"""
测试脚本 - 演示跨服务查询功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.demo.service.demo_complex_service import demo_complex_service
from backend.app.demo.schema.demo import AddDemoParam
from backend.app.demo.schema.document import CreateDocumentParam
from backend.app.demo.schema.location import CreateLocationParam
from backend.core.conf import settings
from backend.database.db import create_database_url


async def test_complex_operations():
    """测试复杂操作功能"""

    # 创建数据库引擎和会话
    db_url = create_database_url()
    engine = create_async_engine(str(db_url))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("开始测试复杂操作...")
        
        # 测试创建demo及关联的文档和位置
        demo_data = {
            "username": "test_user_complex",
            "description": "测试用户-复杂操作",
            "document_ids": []
        }
        
        documents_data = [
            {
                "title": "测试文档1",
                "content": "这是第一个测试文档的内容",
                "category": "测试分类"
            },
            {
                "title": "测试文档2", 
                "content": "这是第二个测试文档的内容",
                "category": "测试分类"
            }
        ]
        
        locations_data = [
            {
                "name": "测试位置1",
                "description": "这是一个测试位置",
                "address": "北京市测试区",
                "category": "测试地点",
                "lng": 116.4074,
                "lat": 39.9042
            }
        ]
        
        print("创建demo及关联数据...")
        result = await demo_complex_service.create_demo_with_documents_and_locations(
            db=db,
            demo_data=demo_data,
            documents_data=documents_data,
            locations_data=locations_data
        )
        
        print(f"创建成功！Demo ID: {result['demo'].id}")
        print(f"创建了 {len(result['documents'])} 个文档")
        print(f"创建了 {len(result['locations'])} 个位置")
        
        # 测试查询demo及关联数据
        print("\n查询demo及关联数据...")
        query_result = await demo_complex_service.get_demo_with_documents_and_locations(
            db=db,
            demo_id=result['demo'].id
        )
        
        print(f"查询到 Demo: {query_result['demo'].username}")
        print(f"关联文档数量: {len(query_result['documents'])}")
        print(f"关联位置数量: {len(query_result['locations'])}")
        
        # 清理测试数据（可选）
        print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(test_complex_operations())