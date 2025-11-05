# MinerU 测试工具集

用于管理和维护 MinerU Tianshu 服务的工具脚本。

## 📋 工具列表

### 1. clean_failed_tasks.py - 清理失败任务

**功能：** 清理数据库中失败的任务记录，无需停止服务。

**使用方法：**
```bash
# 清理所有失败的任务
python tests/utils/clean_failed_tasks.py

# 清理所有任务（慎用！）
python tests/utils/clean_failed_tasks.py --all
```

**特点：**
- ✅ 无需停止服务
- ✅ 显示失败任务详情
- ✅ 需要用户确认
- ✅ 保留成功任务记录
- ✅ 支持自定义数据库路径

**输出示例：**
```
======================================================================
MinerU Tianshu 任务清理工具
======================================================================

📊 当前数据库状态:
   数据库文件: projects/mineru_tianshu/mineru_tianshu.db
   失败任务数: 1

📋 失败任务列表:
   - 1dc7a50d... | test.pdf | Torch not compiled with CUDA enabled

⚠️  将删除 1 个失败的任务
确认删除？(y/N): y

✅ 已删除 1 个失败任务

📊 清理后的队列状态:
   completed   : 17

🎉 清理完成！服务无需重启，继续正常运行
```

### 2. clean_db.sh - 重置数据库

**功能：** 完全重置数据库（会自动备份原数据库）。

**使用方法：**
```bash
# 重置数据库
bash tests/utils/clean_db.sh
```

**特点：**
- ✅ 自动备份原数据库
- ✅ 需要用户确认
- ✅ 显示备份文件位置
- ✅ 支持自定义数据库路径

**输出示例：**
```
🧹 清理 Tianshu 数据库...

📊 当前数据库信息:
-rw-r--r--@ 1 user  staff  28K Nov  5 12:28 mineru_tianshu.db

确认删除数据库吗？(y/N): y

📦 备份到: mineru_tianshu.db.backup.20251105_123456
✅ 数据库已清理!
💡 备份已保存，如需恢复可运行:
   cp mineru_tianshu.db.backup.20251105_123456 mineru_tianshu.db

🚀 现在可以重启 Tianshu 服务，会自动创建新的干净数据库
```

## 🔧 环境变量

### TIANSHU_DB_PATH

指定 Tianshu 数据库文件的路径。

**默认值：** `<项目根目录>/projects/mineru_tianshu/mineru_tianshu.db`

**使用示例：**
```bash
# 使用自定义数据库路径
export TIANSHU_DB_PATH=/path/to/custom/mineru_tianshu.db
python tests/utils/clean_failed_tasks.py

# 或者一次性指定
TIANSHU_DB_PATH=/tmp/test.db python tests/utils/clean_failed_tasks.py
```

## 📝 使用场景

### 场景 1：定期清理失败任务

如果你的服务长期运行，可能会积累一些失败的任务记录。

```bash
# 每周运行一次清理脚本
python tests/utils/clean_failed_tasks.py
```

### 场景 2：测试后清理

在测试完成后，清理所有测试任务。

```bash
# 清理所有任务（包括成功的）
python tests/utils/clean_failed_tasks.py --all
```

### 场景 3：数据库损坏或需要重置

如果数据库出现问题或需要从零开始。

```bash
# 1. 停止服务
# Ctrl+C 停止运行中的服务

# 2. 重置数据库（会自动备份）
bash tests/utils/clean_db.sh

# 3. 重启服务
cd projects/mineru_tianshu
python start_all.py --api-port 8000 --accelerator cpu
```

### 场景 4：迁移或备份

手动备份数据库。

```bash
# 获取数据库路径
DB_PATH="projects/mineru_tianshu/mineru_tianshu.db"

# 创建备份
cp "$DB_PATH" "${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"

# 恢复备份
cp "${DB_PATH}.backup.20251105_123456" "$DB_PATH"
```

## 💡 最佳实践

### 1. 清理前先备份

虽然 `clean_db.sh` 会自动备份，但重要数据建议额外备份。

```bash
# 手动备份
cp projects/mineru_tianshu/mineru_tianshu.db \
   projects/mineru_tianshu/mineru_tianshu.db.backup
```

### 2. 使用 clean_failed_tasks.py 而不是 clean_db.sh

- `clean_failed_tasks.py` 只清理失败任务，保留成功记录
- 无需停止服务
- 更安全

### 3. 定期清理

建议每周或每月运行一次清理脚本，避免数据库过大。

```bash
# 添加到 crontab（每周日凌晨 2 点运行）
0 2 * * 0 cd /Users/shulei/git/MinerU && python tests/utils/clean_failed_tasks.py <<< "y"
```

### 4. 监控数据库大小

```bash
# 查看数据库文件大小
ls -lh projects/mineru_tianshu/mineru_tianshu.db

# 查看任务统计
curl http://localhost:8000/api/v1/queue/stats
```

## 🚨 注意事项

### ⚠️ clean_db.sh 会删除所有任务记录

包括成功和失败的任务，使用前请确认。

### ⚠️ 数据库被锁定

如果遇到 "database is locked" 错误：
- 等待正在进行的操作完成
- 或停止服务后再操作

### ⚠️ 权限问题

如果遇到权限错误：
```bash
# 给脚本添加执行权限
chmod +x tests/utils/clean_db.sh
chmod +x tests/utils/clean_failed_tasks.py
```

## 📚 相关命令

### 查看数据库内容

```bash
# 使用 SQLite 命令行工具
sqlite3 projects/mineru_tianshu/mineru_tianshu.db

# 查看所有表
.tables

# 查看任务表结构
.schema tasks

# 查询所有任务
SELECT task_id, file_name, status, created_at FROM tasks ORDER BY created_at DESC;

# 统计各状态任务数
SELECT status, COUNT(*) FROM tasks GROUP BY status;

# 退出
.quit
```

### 直接清理（高级用户）

```bash
# 删除失败任务（直接 SQL）
sqlite3 projects/mineru_tianshu/mineru_tianshu.db \
  "DELETE FROM tasks WHERE status = 'failed';"

# 删除所有任务
sqlite3 projects/mineru_tianshu/mineru_tianshu.db \
  "DELETE FROM tasks;"
```

## 🔗 相关资源

- [API 测试文档](../api_tests/README.md)
- [Tianshu 项目文档](../../projects/mineru_tianshu/README.md)
- [SQLite 官方文档](https://www.sqlite.org/docs.html)

---

**提示：** 这些工具设计为安全且用户友好，都会在执行危险操作前要求确认。

