#!/usr/bin/env python3
"""
测试 MinerU Tianshu 异步 API - 高级功能
包括：批量任务、优先级队列、任务取消等
"""
import requests
import time
from pathlib import Path
import asyncio
import aiohttp


def get_test_file():
    """获取测试文件路径"""
    import os
    return os.getenv('TEST_PDF_PATH', str(Path(__file__).parent.parent / 'unittest/pdfs/test.pdf'))


def test_batch_submit():
    """测试批量提交任务"""
    print("\n" + "=" * 70)
    print("📦 测试1: 批量提交任务")
    print("=" * 70)
    
    test_file = get_test_file()
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return []
    
    # 批量提交3个任务
    task_ids = []
    for i in range(3):
        with open(test_file, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/api/v1/tasks/submit',
                files={'file': f},
                data={'lang': 'ch', 'priority': 0}
            )
            if response.status_code == 200:
                result = response.json()
                task_id = result['task_id']
                task_ids.append(task_id)
                print(f"✅ 任务 {i+1} 已提交: {task_id[:8]}...")
            else:
                print(f"❌ 任务 {i+1} 提交失败")
    
    print(f"\n📊 共提交了 {len(task_ids)} 个任务")
    return task_ids


def test_priority_queue():
    """测试优先级队列"""
    print("\n" + "=" * 70)
    print("🔥 测试2: 优先级队列")
    print("=" * 70)
    
    test_file = get_test_file()
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return []
    
    # 提交低优先级任务
    with open(test_file, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/v1/tasks/submit',
            files={'file': f},
            data={'lang': 'ch', 'priority': 0}
        )
        low_task = response.json()['task_id']
        print(f"📝 低优先级任务: {low_task[:8]}... (priority=0)")
    
    time.sleep(0.5)
    
    # 提交高优先级任务
    with open(test_file, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/v1/tasks/submit',
            files={'file': f},
            data={'lang': 'ch', 'priority': 10}
        )
        high_task = response.json()['task_id']
        print(f"🔥 高优先级任务: {high_task[:8]}... (priority=10)")
    
    print("\n💡 高优先级任务应该先被处理")
    return [low_task, high_task]


def test_cancel_task():
    """测试取消任务"""
    print("\n" + "=" * 70)
    print("🚫 测试3: 取消任务")
    print("=" * 70)
    
    test_file = get_test_file()
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    # 提交任务
    with open(test_file, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/v1/tasks/submit',
            files={'file': f},
            data={'lang': 'ch', 'priority': -10}  # 低优先级，确保在队列中
        )
        task_id = response.json()['task_id']
        print(f"📝 任务已提交: {task_id[:8]}...")
    
    # 立即取消
    time.sleep(0.5)
    response = requests.delete(f'http://localhost:8000/api/v1/tasks/{task_id}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ 任务已取消: {task_id[:8]}...")
        else:
            print(f"⚠️  取消失败: {result.get('message')}")
    else:
        print(f"❌ 取消请求失败")
    
    # 验证状态
    time.sleep(0.5)
    response = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
    if response.status_code == 200:
        status = response.json()['status']
        print(f"📊 当前状态: {status}")


def test_queue_stats():
    """测试队列统计"""
    print("\n" + "=" * 70)
    print("📊 测试4: 队列统计")
    print("=" * 70)
    
    response = requests.get('http://localhost:8000/api/v1/queue/stats')
    if response.status_code == 200:
        result = response.json()
        print(f"\n当前队列状态:")
        print(f"   总任务数: {result.get('total', 0)}")
        for status, count in result.get('stats', {}).items():
            print(f"   {status:12s}: {count}")
    else:
        print("❌ 获取队列统计失败")


def test_concurrent_requests():
    """测试并发请求"""
    print("\n" + "=" * 70)
    print("⚡ 测试5: 并发请求性能")
    print("=" * 70)
    
    test_file = get_test_file()
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    import concurrent.futures
    
    def submit_task(i):
        start = time.time()
        with open(test_file, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/api/v1/tasks/submit',
                files={'file': f},
                data={'lang': 'ch'}
            )
        elapsed = time.time() - start
        return response.status_code == 200, elapsed
    
    # 并发提交10个任务
    print("📤 并发提交 10 个任务...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(submit_task, range(10)))
    
    total_time = time.time() - start_time
    
    success_count = sum(1 for success, _ in results if success)
    avg_response_time = sum(elapsed for _, elapsed in results) / len(results)
    
    print(f"\n✅ 成功提交: {success_count}/10")
    print(f"⏱️  总耗时: {total_time:.2f}秒")
    print(f"⚡ 平均响应时间: {avg_response_time*1000:.1f}ms")
    print(f"🚀 吞吐量: {10/total_time:.1f} 任务/秒")


def wait_for_queue_clear(timeout=300):
    """等待队列清空"""
    print("\n⏳ 等待所有任务完成...")
    start = time.time()
    
    while time.time() - start < timeout:
        response = requests.get('http://localhost:8000/api/v1/queue/stats')
        if response.status_code == 200:
            stats = response.json()
            pending = stats['stats'].get('pending', 0)
            processing = stats['stats'].get('processing', 0)
            
            if pending == 0 and processing == 0:
                print("✅ 所有任务已完成!")
                return True
            
            print(f"⏳ 等待中... (pending: {pending}, processing: {processing})", end='\r')
        
        time.sleep(2)
    
    print(f"\n⏱️  超时: {timeout}秒")
    return False


def main():
    """主测试函数"""
    print("=" * 70)
    print("MinerU Tianshu 异步 API - 高级功能测试")
    print("=" * 70)
    
    try:
        # 测试1: 批量提交
        task_ids = test_batch_submit()
        
        # 测试2: 优先级队列
        priority_tasks = test_priority_queue()
        
        # 测试3: 取消任务
        test_cancel_task()
        
        # 测试4: 队列统计
        test_queue_stats()
        
        # 测试5: 并发性能
        test_concurrent_requests()
        
        # 等待队列清空
        wait_for_queue_clear(timeout=600)
        
        # 最终统计
        test_queue_stats()
        
        print("\n" + "=" * 70)
        print("🎉 所有测试完成!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器!")
        print("\n请先启动 Tianshu 服务:")
        print("  cd projects/mineru_tianshu")
        print("  python start_all.py --api-port 8000 --accelerator cpu")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

