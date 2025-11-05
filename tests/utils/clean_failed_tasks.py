#!/usr/bin/env python3
"""
清理 MinerU Tianshu 失败的任务
无需停止服务即可运行
"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime

# 数据库路径 - 可通过环境变量指定
DB_PATH = os.getenv(
    'TIANSHU_DB_PATH',
    str(Path(__file__).parent.parent.parent / 'projects/mineru_tianshu/mineru_tianshu.db')
)


def clean_failed_tasks():
    """清理失败的任务"""
    if not Path(DB_PATH).exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询失败任务数量
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
        failed_count = cursor.fetchone()[0]
        
        print(f"📊 当前数据库状态:")
        print(f"   数据库文件: {DB_PATH}")
        print(f"   失败任务数: {failed_count}")
        
        if failed_count == 0:
            print("\n✅ 没有失败的任务需要清理")
            conn.close()
            return
        
        # 显示失败任务详情
        cursor.execute("""
            SELECT task_id, file_name, error_message, created_at 
            FROM tasks 
            WHERE status = 'failed'
            ORDER BY created_at DESC
        """)
        
        failed_tasks = cursor.fetchall()
        print(f"\n📋 失败任务列表:")
        for task_id, file_name, error_msg, created_at in failed_tasks:
            error_preview = error_msg[:50] + "..." if error_msg and len(error_msg) > 50 else (error_msg or "无错误信息")
            print(f"   - {task_id[:8]}... | {file_name} | {error_preview}")
        
        # 确认删除
        print(f"\n⚠️  将删除 {failed_count} 个失败的任务")
        confirm = input("确认删除？(y/N): ").strip().lower()
        
        if confirm != 'y':
            print("❌ 已取消")
            conn.close()
            return
        
        # 删除失败任务
        cursor.execute("DELETE FROM tasks WHERE status = 'failed'")
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 已删除 {deleted_count} 个失败任务")
        
        # 显示清理后的状态
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM tasks 
            GROUP BY status
        """)
        
        print(f"\n📊 清理后的队列状态:")
        for status, count in cursor.fetchall():
            print(f"   {status:12s}: {count}")
        
        conn.close()
        print("\n🎉 清理完成！服务无需重启，继续正常运行")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def clean_all_tasks():
    """清理所有任务（慎用）"""
    if not Path(DB_PATH).exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询任务总数
        cursor.execute("SELECT COUNT(*), status FROM tasks GROUP BY status")
        results = cursor.fetchall()
        
        total = sum(count for count, _ in results)
        
        print(f"📊 当前所有任务:")
        for count, status in results:
            print(f"   {status:12s}: {count}")
        print(f"   {'总计':<12s}: {total}")
        
        if total == 0:
            print("\n✅ 没有任务需要清理")
            conn.close()
            return
        
        # 确认删除
        print(f"\n⚠️  警告：将删除所有 {total} 个任务！")
        confirm = input("确认删除所有任务？(y/N): ").strip().lower()
        
        if confirm != 'y':
            print("❌ 已取消")
            conn.close()
            return
        
        # 删除所有任务
        cursor.execute("DELETE FROM tasks")
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 已删除 {deleted_count} 个任务")
        print("🎉 数据库已清空！")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    import sys
    
    print("=" * 70)
    print("MinerU Tianshu 任务清理工具")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        clean_all_tasks()
    else:
        clean_failed_tasks()
        print("\n💡 提示: 使用 'python clean_failed_tasks.py --all' 可以清理所有任务")

