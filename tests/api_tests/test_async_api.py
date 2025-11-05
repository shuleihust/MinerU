#!/usr/bin/env python3
"""
测试 MinerU Tianshu 异步 API
使用异步任务队列处理长时间运行的 PDF 解析
"""
import requests
import time
from pathlib import Path


def submit_task(file_path: str, lang: str = 'ch') -> str:
    """提交任务，立即返回 task_id"""
    url = 'http://localhost:8000/api/v1/tasks/submit'
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'lang': lang,
            'backend': 'pipeline',
            'priority': 0
        }
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        task_id = result['task_id']
        print(f"✅ 任务已提交: {task_id}")
        print(f"   响应时间: <100ms (立即返回)")
        return task_id


def get_task_status(task_id: str) -> dict:
    """查询任务状态"""
    url = f'http://localhost:8000/api/v1/tasks/{task_id}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def wait_for_completion(task_id: str, timeout: int = 600, poll_interval: int = 2):
    """等待任务完成"""
    print(f"\n⏳ 等待任务完成...")
    start_time = time.time()
    
    while True:
        result = get_task_status(task_id)
        status = result['status']
        
        if status == 'completed':
            elapsed = time.time() - start_time
            print(f"\n✅ 任务完成! 总耗时: {elapsed:.1f}秒")
            
            # 获取解析内容
            if result.get('data'):
                data = result['data']
                content = data.get('content', '')
                print(f"\n📄 解析结果:")
                print(f"   文件名: {data.get('markdown_file')}")
                print(f"   内容长度: {len(content)} 字符")
                print(f"   包含图片: {data.get('has_images', False)}")
                
                # 保存结果到项目根目录的 output 目录
                output_dir = Path(__file__).parent.parent.parent / 'output'
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / 'test_async_result.md'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   已保存到: {output_file}")
                
                # 显示内容预览
                print(f"\n📖 内容预览:")
                print("-" * 60)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 60)
            else:
                print(f"⚠️  结果文件已被清理")
            
            return result
            
        elif status == 'failed':
            print(f"\n❌ 任务失败!")
            print(f"   错误信息: {result.get('error_message')}")
            return result
            
        elif status == 'processing':
            elapsed = time.time() - start_time
            print(f"⏳ 处理中... 已等待: {elapsed:.1f}秒", end='\r')
            
        elif status == 'pending':
            print(f"📝 等待队列中...", end='\r')
        
        # 检查超时
        if time.time() - start_time > timeout:
            print(f"\n⏱️  超时! 已等待 {timeout} 秒")
            return {'status': 'timeout'}
        
        time.sleep(poll_interval)


def get_queue_stats():
    """获取队列统计"""
    url = 'http://localhost:8000/api/v1/queue/stats'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main():
    """主测试函数"""
    print("=" * 70)
    print("MinerU Tianshu 异步 API 测试")
    print("=" * 70)
    
    # 测试文件路径 - 可以通过环境变量或参数指定
    import os
    test_file = os.getenv('TEST_PDF_PATH', str(Path(__file__).parent.parent / 'unittest/pdfs/test.pdf'))
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    try:
        # 1. 查看队列状态
        print("\n📊 当前队列状态:")
        stats = get_queue_stats()
        for status, count in stats.get('stats', {}).items():
            print(f"   {status:12s}: {count}")
        
        # 2. 提交任务
        print(f"\n📤 提交任务: {test_file}")
        task_id = submit_task(test_file, lang='ch')
        
        # 3. 等待完成
        result = wait_for_completion(task_id)
        
        # 4. 查看最终队列状态
        print(f"\n📊 最终队列状态:")
        stats = get_queue_stats()
        for status, count in stats.get('stats', {}).items():
            print(f"   {status:12s}: {count}")
        
        print("\n" + "=" * 70)
        print("测试完成!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器!")
        print("\n请先启动 Tianshu 服务:")
        print("  cd projects/mineru_tianshu")
        print("  python start_all.py --api-port 8000")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

