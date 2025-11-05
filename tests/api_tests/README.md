# MinerU API 测试套件

MinerU Tianshu 异步 API 的测试脚本集合。

## 📁 目录结构

```
tests/
├── api_tests/              # API 测试脚本
│   ├── test_async_api.py          # 基础异步 API 测试
│   ├── test_async_advanced.py     # 高级功能测试（批量、优先级、并发等）
│   └── README.md                  # 本文件
├── utils/                  # 工具脚本
│   ├── clean_failed_tasks.py      # 清理失败的任务
│   └── clean_db.sh                # 重置数据库
└── unittest/               # 单元测试
    └── pdfs/               # 测试 PDF 文件
        └── test.pdf
```

## 🚀 快速开始

### 1. 启动 Tianshu 服务

```bash
# 进入项目目录
cd /Users/shulei/git/MinerU

# 启动服务（使用 CPU 模式，适合 macOS）
cd projects/mineru_tianshu
python start_all.py --api-port 8000 --accelerator cpu

# 或使用 MPS 模式（Apple Silicon Mac）
python start_all.py --api-port 8000 --accelerator mps
```

### 2. 运行测试

```bash
# 基础 API 测试
cd /Users/shulei/git/MinerU
python tests/api_tests/test_async_api.py

# 高级功能测试（批量、优先级、并发）
python tests/api_tests/test_async_advanced.py
```

## 📋 测试说明

### test_async_api.py - 基础测试

测试异步 API 的基本功能：

- ✅ 任务提交（立即返回 task_id）
- ✅ 任务状态查询
- ✅ 轮询等待任务完成
- ✅ 获取解析结果内容

**预期结果：**
- 提交响应时间 < 100ms
- 后台解析完成后自动返回 Markdown 内容
- 保存结果到 `output_async.md`

**运行示例：**
```bash
python tests/api_tests/test_async_api.py

# 使用自定义测试文件
export TEST_PDF_PATH=/path/to/your/test.pdf
python tests/api_tests/test_async_api.py
```

### test_async_advanced.py - 高级测试

测试异步 API 的高级功能：

#### 测试 1：批量提交任务
- 并发提交 3 个任务
- 验证任务 ID 正确返回

#### 测试 2：优先级队列
- 提交低优先级任务（priority=0）
- 提交高优先级任务（priority=10）
- 验证高优先级任务先被处理

#### 测试 3：取消任务
- 提交任务
- 在处理前取消
- 验证状态变为 `cancelled`

#### 测试 4：队列统计
- 查询队列状态
- 显示各状态任务数量

#### 测试 5：并发请求性能
- 并发提交 10 个任务
- 测量响应时间和吞吐量
- 预期：平均响应时间 < 50ms

**运行示例：**
```bash
python tests/api_tests/test_async_advanced.py

# 使用自定义测试文件
export TEST_PDF_PATH=/path/to/your/test.pdf
python tests/api_tests/test_async_advanced.py
```

## 🛠️ 工具脚本

### clean_failed_tasks.py - 清理失败任务

无需停止服务即可清理失败的任务记录。

```bash
# 清理所有失败的任务
python tests/utils/clean_failed_tasks.py

# 清理所有任务（慎用）
python tests/utils/clean_failed_tasks.py --all

# 使用自定义数据库路径
export TIANSHU_DB_PATH=/path/to/mineru_tianshu.db
python tests/utils/clean_failed_tasks.py
```

### clean_db.sh - 重置数据库

完全重置数据库（会自动备份）。

```bash
# 重置数据库
bash tests/utils/clean_db.sh

# 使用自定义数据库路径
export TIANSHU_DB_PATH=/path/to/mineru_tianshu.db
bash tests/utils/clean_db.sh
```

## 🔧 环境变量

所有脚本支持通过环境变量自定义配置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `TEST_PDF_PATH` | 测试 PDF 文件路径 | `tests/unittest/pdfs/test.pdf` |
| `TIANSHU_DB_PATH` | Tianshu 数据库路径 | `projects/mineru_tianshu/mineru_tianshu.db` |
| `API_URL` | API 服务地址 | `http://localhost:8000` |

**使用示例：**
```bash
# 使用自定义配置
export TEST_PDF_PATH=/path/to/custom.pdf
export API_URL=http://192.168.1.100:8000
python tests/api_tests/test_async_api.py
```

## 📊 测试结果示例

### 基础测试输出

```
======================================================================
MinerU Tianshu 异步 API 测试
======================================================================

📊 当前队列状态:
   completed   : 2

📤 提交任务: tests/unittest/pdfs/test.pdf
✅ 任务已提交: 8b0a371f...
   响应时间: <100ms (立即返回)

⏳ 等待任务完成...
✅ 任务完成! 总耗时: 14.1秒

📄 解析结果:
   文件名: test.md
   内容长度: 1090 字符
   包含图片: True
   已保存到: output_async.md

======================================================================
测试完成!
======================================================================
```

### 高级测试输出

```
======================================================================
⚡ 测试5: 并发请求性能
======================================================================
📤 并发提交 10 个任务...

✅ 成功提交: 10/10
⏱️  总耗时: 0.02秒
⚡ 平均响应时间: 13.1ms
🚀 吞吐量: 448.1 任务/秒
```

## 💡 常见问题

### 1. 连接失败

```
❌ 无法连接到服务器!
```

**解决方案：** 确保 Tianshu 服务已启动
```bash
cd projects/mineru_tianshu
python start_all.py --api-port 8000 --accelerator cpu
```

### 2. 测试文件不存在

```
❌ 测试文件不存在: tests/unittest/pdfs/test.pdf
```

**解决方案：** 复制测试 PDF 到指定位置或设置环境变量
```bash
# 方法1：复制文件
cp /path/to/your/test.pdf tests/unittest/pdfs/

# 方法2：使用环境变量
export TEST_PDF_PATH=/path/to/your/test.pdf
```

### 3. 数据库错误

```
❌ 数据库错误: database is locked
```

**解决方案：** 
- 等待其他操作完成
- 或者停止服务后再进行数据库操作

### 4. CUDA 错误（macOS）

```
❌ Torch not compiled with CUDA enabled
```

**解决方案：** 使用 CPU 或 MPS 模式启动服务
```bash
# CPU 模式
python start_all.py --accelerator cpu

# MPS 模式（Apple Silicon）
python start_all.py --accelerator mps
```

## 📚 相关文档

- [MinerU 主文档](../../README.md)
- [Tianshu 项目文档](../../projects/mineru_tianshu/README.md)
- [API 接口文档](http://localhost:8000/docs)（需先启动服务）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果你添加了新的测试用例，请：
1. 确保测试可以独立运行
2. 添加清晰的注释说明
3. 更新本 README 文档

