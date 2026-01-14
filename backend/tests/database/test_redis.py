"""
Redis 测试脚本 - 演示常见 Redis 操作
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.database.redis import redis_client


async def test_redis_operations():
    """测试 Redis 常见操作"""
    print("开始测试 Redis 操作...")
    
    try:
        # 测试连接
        print("\n1. 测试 Redis 连接...")
        await redis_client.open()
        print("✅ Redis 连接成功")
        
        # 测试字符串操作
        print("\n2. 测试字符串操作...")
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        print(f"   设置 test_key = test_value")
        print(f"   获取 test_key = {value}")
        
        # 测试过期时间
        await redis_client.setex("expiring_key", 10, "will expire")
        ttl = await redis_client.ttl("expiring_key")
        print(f"   设置 expiring_key 过期时间为 {ttl} 秒")
        
        # 测试哈希操作
        print("\n3. 测试哈希操作...")
        await redis_client.hset("test_hash", mapping={"field1": "value1", "field2": "value2"})
        hash_values = await redis_client.hgetall("test_hash")
        print(f"   哈希内容: {hash_values}")
        
        field_value = await redis_client.hget("test_hash", "field1")
        print(f"   获取 field1 = {field_value}")
        
        # 测试列表操作
        print("\n4. 测试列表操作...")
        await redis_client.lpush("test_list", "item1", "item2", "item3")
        list_len = await redis_client.llen("test_list")
        list_items = await redis_client.lrange("test_list", 0, -1)
        print(f"   列表长度: {list_len}")
        print(f"   列表内容: {list_items}")
        
        # 测试集合操作
        print("\n5. 测试集合操作...")
        await redis_client.sadd("test_set", "member1", "member2", "member3")
        set_members = await redis_client.smembers("test_set")
        print(f"   集合成员: {set_members}")
        
        is_member = await redis_client.sismember("test_set", "member1")
        print(f"   member1 是否在集合中: {is_member}")
        
        # 测试有序集合操作
        print("\n6. 测试有序集合操作...")
        await redis_client.zadd("test_zset", {"member1": 1, "member2": 2, "member3": 3})
        zset_members = await redis_client.zrange("test_zset", 0, -1, withscores=True)
        print(f"   有序集合成员: {zset_members}")
        
        # 测试键操作
        print("\n7. 测试键操作...")
        keys = await redis_client.get_prefix("test_*")
        print(f"   以 'test_' 开头的键: {keys}")
        
        # 测试 exists 操作
        exists = await redis_client.exists("test_key")
        print(f"   test_key 是否存在: {exists}")
        
        # 测试删除操作
        print("\n8. 测试删除操作...")
        deleted = await redis_client.delete("test_key")
        print(f"   删除 test_key: {deleted} 个键被删除")
        
        # 测试批量删除
        await redis_client.delete_prefix("test_*", exclude=["test_hash"])  # 保留 test_hash
        remaining_keys = await redis_client.get_prefix("test_*")
        print(f"   删除后剩余的 test_* 键: {remaining_keys}")
        
        # 最终清理
        await redis_client.delete("test_hash")  # 清理保留的键
        print("\n✅ Redis 测试完成！")
        
    except Exception as e:
        print(f"\n❌ Redis 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_redis_operations())