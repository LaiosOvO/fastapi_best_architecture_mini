"""
MongoDB 测试脚本 - 演示常见 MongoDB 操作
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.database.mongo import mongo_client


async def test_mongodb_operations():
    """测试 MongoDB 常见操作"""
    print("开始测试 MongoDB 操作...")

    try:
        # 测试连接
        print("\n1. 测试 MongoDB 连接...")
        await mongo_client.open()
        print("✅ MongoDB 连接成功")

        # 定义测试集合名
        test_collection = "test_users"

        # 清理之前的测试数据
        await mongo_client.drop_collection(test_collection)
        print(f"   清理测试集合 {test_collection}")

        # 测试插入单个文档
        print("\n2. 测试插入单个文档...")
        user_doc = {
            "username": "test_user",
            "email": "test@example.com",
            "age": 25,
            "created_at": datetime.utcnow(),
            "profile": {
                "city": "Beijing",
                "country": "China"
            },
            "tags": ["developer", "python", "fastapi"]
        }

        inserted_id = await mongo_client.insert_one(test_collection, user_doc)
        print(f"   插入文档 ID: {inserted_id}")

        # 测试插入多个文档
        print("\n3. 测试插入多个文档...")
        users_docs = [
            {
                "username": "user1",
                "email": "user1@example.com",
                "age": 30,
                "created_at": datetime.utcnow(),
                "profile": {"city": "Shanghai", "country": "China"},
                "tags": ["user", "tester"]
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "age": 28,
                "created_at": datetime.utcnow(),
                "profile": {"city": "Guangzhou", "country": "China"},
                "tags": ["user", "analyst"]
            }
        ]

        inserted_ids = await mongo_client.insert_many(test_collection, users_docs)
        print(f"   批量插入 {len(inserted_ids)} 个文档")

        # 测试查找单个文档
        print("\n4. 测试查找单个文档...")
        found_user = await mongo_client.find_one(test_collection, {"username": "test_user"})
        print(f"   查找用户: {found_user['username']} (ID: {found_user['_id']})")

        # 测试查找单个文档带投影
        print("\n5. 测试查找单个文档（带投影）...")
        found_user_proj = await mongo_client.find_one(test_collection, {"username": "test_user"}, projection={"email": 1, "age": 1})
        print(f"   投影查询结果: {found_user_proj}")

        # 测试查找多个文档
        print("\n6. 测试查找多个文档...")
        all_users = await mongo_client.find(test_collection)
        print(f"   总共找到 {len(all_users)} 个用户")

        # 测试查找带条件的文档
        print("\n7. 测试条件查询...")
        young_users = await mongo_client.find(test_collection, {"age": {"$lt": 30}})
        print(f"   年龄小于30的用户数量: {len(young_users)}")

        # 测试分页查询
        print("\n8. 测试分页查询...")
        paged_users = await mongo_client.find(test_collection, skip=1, limit=2)
        print(f"   分页查询结果数量: {len(paged_users)}")

        # 测试排序查询
        print("\n9. 测试排序查询...")
        sorted_users = await mongo_client.find(test_collection, sort=[("age", -1)])  # 按年龄降序
        print(f"   按年龄降序排序: {[user['age'] for user in sorted_users]}")

        # 测试更新单个文档
        print("\n10. 测试更新单个文档...")
        update_result = await mongo_client.update_one(
            test_collection,
            {"username": "test_user"},
            {"age": 26, "updated_at": datetime.utcnow()}
        )
        print(f"   更新了 {update_result} 个文档")

        # 验证更新结果
        updated_user = await mongo_client.find_one(test_collection, {"username": "test_user"})
        print(f"   更新后的年龄: {updated_user['age']}")

        # 测试更新多个文档
        print("\n11. 测试更新多个文档...")
        multi_update_result = await mongo_client.update_many(
            test_collection,
            {"age": {"$gte": 25}},
            {"$set": {"status": "active"}}
        )
        print(f"   批量更新了 {multi_update_result} 个文档")

        # 测试替换文档
        print("\n12. 测试替换文档...")
        replace_doc = {
            "username": "replaced_user",
            "email": "replaced@example.com",
            "age": 35,
            "status": "replaced"
        }
        replace_result = await mongo_client.replace_one(
            test_collection,
            {"username": "user2"},
            replace_doc,
            upsert=False
        )
        print(f"   替换了 {replace_result} 个文档")

        # 测试统计文档数量
        print("\n13. 测试统计文档数量...")
        total_count = await mongo_client.count_documents(test_collection)
        active_count = await mongo_client.count_documents(test_collection, {"status": "active"})
        print(f"   总文档数: {total_count}")
        print(f"   活跃用户数: {active_count}")

        # 测试distinct操作
        print("\n14. 测试distinct操作...")
        statuses = await mongo_client.distinct(test_collection, "status")
        print(f"   不同状态值: {statuses}")

        # 测试聚合查询
        print("\n15. 测试聚合查询...")
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        agg_result = await mongo_client.aggregate(test_collection, pipeline)
        print(f"   聚合结果: {agg_result}")

        # 测试删除单个文档
        print("\n16. 测试删除单个文档...")
        delete_result = await mongo_client.delete_one(test_collection, {"username": "user1"})
        print(f"   删除了 {delete_result} 个文档")

        # 验证删除结果
        remaining_count = await mongo_client.count_documents(test_collection)
        print(f"   删除后剩余文档数: {remaining_count}")

        # 测试删除多个文档
        print("\n17. 测试删除多个文档...")
        multi_delete_result = await mongo_client.delete_many(test_collection, {"age": {"$lt": 30}})
        print(f"   批量删除了 {multi_delete_result} 个文档")

        # 最终统计
        final_count = await mongo_client.count_documents(test_collection)
        print(f"   最终剩余文档数: {final_count}")

        # 测试索引创建
        print("\n18. 测试创建索引...")
        index_name = await mongo_client.create_index(test_collection, "username", unique=True)
        print(f"   创建索引: {index_name}")

        # 清理测试集合
        await mongo_client.drop_collection(test_collection)
        print(f"   清理测试集合 {test_collection}")

        print("\n✅ MongoDB 测试完成！")

    except Exception as e:
        print(f"\n❌ MongoDB 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        await mongo_client.close()


if __name__ == "__main__":
    asyncio.run(test_mongodb_operations())