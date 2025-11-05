#!/bin/bash
# 清理 MinerU Tianshu 数据库

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 数据库路径 - 可通过环境变量指定
DB_FILE="${TIANSHU_DB_PATH:-$PROJECT_ROOT/projects/mineru_tianshu/mineru_tianshu.db}"

echo "🧹 清理 Tianshu 数据库..."
echo ""

# 检查数据库是否存在
if [ ! -f "$DB_FILE" ]; then
    echo "❌ 数据库文件不存在: $DB_FILE"
    exit 1
fi

# 显示当前数据库大小
echo "📊 当前数据库信息:"
ls -lh "$DB_FILE"
echo ""

# 询问确认
read -p "确认删除数据库吗？(y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份数据库
    BACKUP_FILE="${DB_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 备份到: $BACKUP_FILE"
    cp "$DB_FILE" "$BACKUP_FILE"
    
    # 删除数据库
    rm "$DB_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ 数据库已清理!"
        echo "💡 备份已保存，如需恢复可运行:"
        echo "   cp $BACKUP_FILE $DB_FILE"
        echo ""
        echo "🚀 现在可以重启 Tianshu 服务，会自动创建新的干净数据库"
    else
        echo "❌ 清理失败"
        exit 1
    fi
else
    echo "❌ 已取消"
    exit 0
fi

