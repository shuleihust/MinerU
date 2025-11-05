#!/bin/bash
# 完全重启 Tianshu 服务

echo "🛑 停止所有 Tianshu 相关进程..."

# 停止 start_all.py
pkill -f "start_all.py"

# 停止 litserve_worker.py
pkill -f "litserve_worker.py"

# 停止 task_scheduler.py  
pkill -f "task_scheduler.py"

# 停止 api_server.py
pkill -f "api_server.py"

# 等待进程完全停止
sleep 2

# 确认是否还有残留进程
REMAINING=$(ps aux | grep -E "start_all|litserve_worker|task_scheduler|api_server" | grep mineru_tianshu | grep -v grep | wc -l)

if [ $REMAINING -gt 0 ]; then
    echo "⚠️  还有 $REMAINING 个进程未停止，强制终止..."
    pkill -9 -f "mineru_tianshu"
    sleep 1
fi

echo "✅ 所有进程已停止"
echo ""

# 检查端口占用
echo "🔍 检查端口占用..."
PORT_8000=$(lsof -i :8000 -t 2>/dev/null | wc -l)
PORT_9000=$(lsof -i :9000 -t 2>/dev/null | wc -l)

if [ $PORT_8000 -gt 0 ]; then
    echo "⚠️  端口 8000 仍被占用，尝试释放..."
    lsof -i :8000 -t | xargs kill -9 2>/dev/null
fi

if [ $PORT_9000 -gt 0 ]; then
    echo "⚠️  端口 9000 仍被占用，尝试释放..."
    lsof -i :9000 -t | xargs kill -9 2>/dev/null
fi

sleep 1
echo "✅ 端口已清理"
echo ""

# 重新启动服务
echo "🚀 重新启动 Tianshu 服务..."
cd /Users/shulei/git/MinerU/projects/mineru_tianshu

python start_all.py --api-port 8000 --accelerator cpu "$@"

