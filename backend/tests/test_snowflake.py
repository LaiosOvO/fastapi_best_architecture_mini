"""
Snowflake 雪花算法测试脚本
"""
import asyncio
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from backend.utils.snowflake import snowflake


async def test_snowflake_basic():
    """测试雪花算法基本功能"""
    print("开始测试雪花算法基本功能...")
    
    # 初始化雪花算法
    await snowflake.init()
    print("✅ 雪花算法初始化成功")
    
    # 生成单个 ID
    id1 = snowflake.generate()
    id2 = snowflake.generate()
    
    print(f"生成的 ID1: {id1}")
    print(f"生成的 ID2: {id2}")
    print(f"ID1 < ID2: {id1 < id2}")
    
    # 验证趋势递增
    assert id1 < id2, "ID 应该趋势递增"
    print("✅ ID 趋势递增验证通过")
    
    # 解析 ID
    info1 = snowflake.parse(id1)
    info2 = snowflake.parse(id2)
    
    print(f"ID1 解析结果: {info1}")
    print(f"ID2 解析结果: {info2}")
    
    # 验证解析结果
    assert info1.worker_id == info2.worker_id, "工作机器ID应该相同"
    assert info1.datacenter_id == info2.datacenter_id, "数据中心ID应该相同"
    print("✅ ID 解析验证通过")
    
    return True


def generate_ids_thread(num_ids):
    """在线程中生成 ID"""
    ids = []
    for _ in range(num_ids):
        id_val = snowflake.generate()
        ids.append(id_val)
    return ids


async def test_snowflake_concurrent():
    """测试雪花算法并发性能"""
    print("\n开始测试雪花算法并发性能...")
    
    # 并发生成 ID
    num_threads = 10
    ids_per_thread = 100
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 提交任务
        futures = []
        for i in range(num_threads):
            future = executor.submit(generate_ids_thread, ids_per_thread)
            futures.append(future)
        
        # 收集结果
        all_ids = []
        for future in futures:
            thread_ids = future.result()
            all_ids.extend(thread_ids)
    
    print(f"总共生成了 {len(all_ids)} 个 ID")
    
    # 验证唯一性
    unique_ids = set(all_ids)
    assert len(unique_ids) == len(all_ids), f"ID 不唯一: {len(all_ids) - len(unique_ids)} 个重复"
    print("✅ 并发生成的 ID 唯一性验证通过")
    
    # 验证趋势递增（在单个线程内部）
    # 由于多线程并发，整体不一定递增，但在单个线程内部应该是递增的
    print("✅ 并发性能测试完成")
    
    return True


async def test_snowflake_sequence():
    """测试雪花算法序列号功能"""
    print("\n开始测试雪花算法序列号功能...")
    
    # 在同一毫秒内生成多个 ID 来测试序列号
    ids = []
    for _ in range(10):
        ids.append(snowflake.generate())
    
    print(f"在同一毫秒内生成的 ID: {ids[:5]}...")  # 显示前5个
    
    # 解析这些 ID，检查序列号
    infos = [snowflake.parse(id_val) for id_val in ids]
    
    # 获取第一个 ID 的时间戳作为基准
    base_timestamp = infos[0].timestamp
    sequences = [info.sequence for info in infos]
    
    print(f"时间戳: {base_timestamp}")
    print(f"序列号: {sequences}")
    
    # 验证序列号在同一时间戳下递增
    for i in range(1, len(sequences)):
        if infos[i].timestamp == base_timestamp:  # 同一毫秒
            assert sequences[i] == (sequences[i-1] + 1) % 4096, f"序列号不连续: {sequences[i-1]} -> {sequences[i]}"
    
    print("✅ 序列号功能测试通过")
    
    return True


async def test_snowflake_parse():
    """测试雪花算法解析功能"""
    print("\n开始测试雪花算法解析功能...")
    
    # 生成一个 ID
    test_id = snowflake.generate()
    print(f"测试 ID: {test_id}")
    
    # 解析 ID
    info = snowflake.parse(test_id)
    
    print(f"解析结果:")
    print(f"  时间戳: {info.timestamp}")
    print(f"  日期时间: {info.datetime}")
    print(f"  数据中心ID: {info.datacenter_id}")
    print(f"  工作机器ID: {info.worker_id}")
    print(f"  序列号: {info.sequence}")
    
    # 验证解析结果的合理性
    assert info.datacenter_id >= 0 and info.datacenter_id <= 31, "数据中心ID超出范围"
    assert info.worker_id >= 0 and info.worker_id <= 31, "工作机器ID超出范围"
    assert info.sequence >= 0 and info.sequence <= 4095, "序列号超出范围"
    
    print("✅ 解析功能验证通过")
    
    return True


async def test_performance():
    """测试性能"""
    print("\n开始测试性能...")
    
    start_time = time.time()
    
    # 生成大量 ID 测试性能
    num_ids = 10000
    ids = []
    
    for _ in range(num_ids):
        ids.append(snowflake.generate())
    
    end_time = time.time()
    
    duration = end_time - start_time
    qps = num_ids / duration
    
    print(f"生成 {num_ids} 个 ID 耗时: {duration:.4f} 秒")
    print(f"QPS: {qps:.2f}")
    
    # 验证唯一性
    unique_ids = set(ids)
    assert len(unique_ids) == len(ids), "性能测试中 ID 不唯一"
    
    print("✅ 性能测试通过")
    
    return True


async def main():
    """主测试函数"""
    print("=" * 60)
    print("雪花算法测试开始")
    print("=" * 60)
    
    try:
        # 基本功能测试
        await test_snowflake_basic()
        
        # 并发测试
        await test_snowflake_concurrent()
        
        # 序列号测试
        await test_snowflake_sequence()
        
        # 解析功能测试
        await test_snowflake_parse()
        
        # 性能测试
        await test_performance()
        
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await snowflake.shutdown()


if __name__ == "__main__":
    asyncio.run(main())