# MinerU Tianshu 故障排查指南

## 🚀 快速索引

| 问题 | 跳转 |
|-----|------|
| 健康检查失败（HTTP/0.9） | [#健康检查失败](#健康检查失败) |
| 端口被占用 | [#端口被占用](#端口被占用) |
| 数据库锁定 | [#数据库锁定](#数据库锁定) |
| CUDA/GPU 错误 | [#cuda-错误](#cuda-错误) |
| 任务不被处理 | [#任务不被处理](#任务不被处理) |
| 处理速度慢 | [#处理速度慢](#处理速度慢) |

---

## 🐛 常见问题

### 健康检查失败

**错误信息：**
```
Health check error: 400, message="Expected HTTP/..."
或
curl: (1) Received HTTP/0.9 when not allowed
```

**原因：** Worker 请求处理问题

**解决：**
```bash
# 重启服务即可
cd projects/mineru_tianshu
bash restart_service.sh
# 或手动重启
python start_all.py --api-port 8000 --accelerator cpu
```

**验证：**
```bash
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"action":"health"}' | python3 -m json.tool
# 应返回：{"status": "healthy", ...}
```

---

### 端口被占用

**错误：** `Address already in use`

**解决：**
```bash
# 查找并终止占用进程
lsof -i :8000 -t | xargs kill -9
lsof -i :9000 -t | xargs kill -9
```

---

### 数据库锁定

**错误：** `database is locked`

**解决：**
- 等待当前操作完成
- 或停止服务后重启
- 确保只有一个服务实例在运行

---

### CUDA 错误

**错误：** `Torch not compiled with CUDA enabled` (macOS)

**解决：**
```bash
# CPU 模式
python start_all.py --accelerator cpu

# MPS 模式（Apple Silicon）
python start_all.py --accelerator mps
```

---

### 任务不被处理

**症状：** 任务一直 `pending`

**排查：**
```bash
# 1. 检查队列
curl http://localhost:8000/api/v1/queue/stats

# 2. 检查 Worker 健康
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"action":"health"}'

# 3. 检查进程
ps aux | grep -E "litserve|start_all" | grep -v grep
```

**解决：**
- 确认 Worker 服务已启动
- 查看日志排查错误
- 重启服务

---

### 处理速度慢

**优化选项：**
```bash
# 增加 Worker 数量
python start_all.py --workers-per-device 2

# 使用多 GPU
python start_all.py --devices 0,1

# 减少轮询间隔
python start_all.py --poll-interval 0.3
```

---

## 📊 监控命令

### 查看队列状态
```bash
curl http://localhost:8000/api/v1/queue/stats | python3 -m json.tool
```

### 查看 Worker 状态
```bash
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"action":"health"}' | python3 -m json.tool
```

### 查看数据库
```bash
sqlite3 projects/mineru_tianshu/mineru_tianshu.db \
  "SELECT status, COUNT(*) FROM tasks GROUP BY status;"
```

### 查看运行进程
```bash
ps aux | grep -E "start_all|litserve|api_server" | grep -v grep
```

### 查看端口监听
```bash
lsof -i :8000  # API 服务
lsof -i :9000  # Worker 服务
```

---

## 🛠️ 维护操作

### 完全重启服务

**使用脚本：**
```bash
cd projects/mineru_tianshu
bash restart_service.sh
```

**手动操作：**
```bash
# 1. 停止服务（Ctrl+C）

# 2. 清理进程
pkill -f "start_all.py"
pkill -f "litserve_worker"

# 3. 重启
python start_all.py --api-port 8000 --accelerator cpu
```

### 清理失败任务
```bash
python tests/utils/clean_failed_tasks.py
```

### 重置数据库
```bash
bash tests/utils/clean_db.sh  # 会自动备份
```

### 清理旧任务（保留 N 天）
```bash
curl -X POST "http://localhost:8000/api/v1/admin/cleanup?days=7"
```

---

## 🔧 配置优化

### 启动参数说明

| 参数 | 说明 | 默认值 | 示例 |
|-----|------|--------|------|
| `--api-port` | API 服务端口 | 8000 | `--api-port 8080` |
| `--accelerator` | 加速器类型 | auto | `--accelerator cpu` |
| `--workers-per-device` | 每设备 Worker 数 | 1 | `--workers-per-device 2` |
| `--devices` | 使用的设备 | auto | `--devices 0,1` |
| `--poll-interval` | 轮询间隔（秒）| 0.5 | `--poll-interval 0.3` |

### 推荐配置

**开发环境（CPU）：**
```bash
python start_all.py --accelerator cpu
```

**生产环境（单 GPU）：**
```bash
python start_all.py \
  --accelerator cuda \
  --workers-per-device 2 \
  --devices 0
```

**生产环境（多 GPU）：**
```bash
python start_all.py \
  --accelerator cuda \
  --workers-per-device 2 \
  --devices 0,1,2
```

**macOS（Apple Silicon）：**
```bash
python start_all.py --accelerator mps
```

---

## 📝 日志分析

### 日志位置
```bash
# 服务运行时在终端查看
# 或重定向到文件
python start_all.py > tianshu.log 2>&1 &
```

### 常见日志信息

**正常启动：**
```
✅ Worker tianshu-xxx ready
🔄 Worker loop started
📡 API Server running on http://0.0.0.0:8000
```

**任务处理：**
```
🔄 Processing task xxx: file.pdf
✅ Task xxx completed
```

**错误信息：**
```
❌ Task xxx failed: [错误原因]
⚠️ Workers health check failed
```

---

## 🐞 调试技巧

### 1. 逐步排查

```bash
# Step 1: 检查服务是否运行
ps aux | grep start_all

# Step 2: 检查端口
lsof -i :8000
lsof -i :9000

# Step 3: 测试 API
curl http://localhost:8000/api/v1/health

# Step 4: 测试 Worker
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"action":"health"}'

# Step 5: 查看队列
curl http://localhost:8000/api/v1/queue/stats
```

### 2. 提交测试任务

```bash
# 使用测试脚本
python tests/api_tests/test_async_api.py

# 或手动提交
curl -X POST http://localhost:8000/api/v1/tasks/submit \
  -F "file=@test.pdf" \
  -F "lang=ch"
```

### 3. 查看详细日志

启用调试模式查看更详细的日志：
```bash
# 设置日志级别
export LOGURU_LEVEL=DEBUG
python start_all.py
```

---

## 📞 获取帮助

### 自助排查清单

- [ ] 服务是否正常运行？
- [ ] 端口是否被占用？
- [ ] 健康检查是否通过？
- [ ] 数据库是否可访问？
- [ ] 日志中有无错误信息？

### 提交 Issue

如果问题无法解决，请到 [GitHub Issues](https://github.com/opendatalab/MinerU/issues) 提交，包含：

1. **错误信息**（完整的错误堆栈）
2. **环境信息**
   ```bash
   python --version
   pip list | grep -E "mineru|litserve|torch"
   uname -a
   ```
3. **重现步骤**
4. **相关日志**

---

## 📚 相关文档

- [Tianshu README](README.md) - 项目介绍和快速开始
- [API 文档](http://localhost:8000/docs) - 需要先启动服务
- [测试指南](../../tests/api_tests/README.md) - API 测试文档

---

**最后更新：** 2025-11-05  
**版本：** v2.0
