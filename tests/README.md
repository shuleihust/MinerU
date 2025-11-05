# MinerU 测试套件

MinerU 项目的完整测试套件，包括 API 测试、工具脚本和单元测试。

## 📁 目录结构

```
tests/
├── api_tests/                      # API 测试脚本
│   ├── test_async_api.py          # 基础异步 API 测试
│   ├── test_async_advanced.py     # 高级功能测试
│   └── README.md                  # API 测试文档
│
├── utils/                          # 工具脚本
│   ├── clean_failed_tasks.py      # 清理失败任务
│   ├── clean_db.sh                # 重置数据库
│   └── README.md                  # 工具使用文档
│
├── unittest/                       # 单元测试
│   ├── pdfs/                      # 测试 PDF 文件
│   │   └── test.pdf
│   └── test_e2e.py                # 端到端测试
│
├── clean_coverage.py               # 清理覆盖率数据
├── get_coverage.py                 # 生成覆盖率报告
└── README.md                       # 本文件
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 MinerU 及其依赖：

```bash
cd /Users/shulei/git/MinerU
pip install -e .
```

### 2. 启动 Tianshu 服务

```bash
cd projects/mineru_tianshu
python start_all.py --api-port 8000 --accelerator cpu
```

### 3. 运行测试

```bash
# 基础 API 测试
python tests/api_tests/test_async_api.py

# 高级功能测试
python tests/api_tests/test_async_advanced.py

# 端到端测试
python tests/unittest/test_e2e.py
```

## 📋 测试分类

### API 测试（api_tests/）

测试 MinerU Tianshu 异步 API 的功能和性能。

**特点：**
- ✅ 测试异步任务队列
- ✅ 测试批量提交、优先级队列
- ✅ 测试并发性能和吞吐量
- ✅ 测试任务取消和状态查询

**详细文档：** [api_tests/README.md](api_tests/README.md)

### 工具脚本（utils/）

用于维护和管理 Tianshu 服务的工具。

**包含：**
- 🧹 清理失败任务
- 🔄 重置数据库
- 📊 数据库管理

**详细文档：** [utils/README.md](utils/README.md)

### 单元测试（unittest/）

MinerU 核心功能的单元测试。

**包含：**
- 端到端解析测试
- PDF 处理测试
- 模型输出验证

## 📊 测试数据

### 测试 PDF 文件

位置：`tests/unittest/pdfs/test.pdf`

**内容：**
- 图片
- LaTeX 数学公式
- 表格
- 文本段落

**特点：**
- 文件大小适中（~126KB）
- 包含多种元素类型
- 适合快速测试

### 自定义测试文件

所有测试脚本支持通过环境变量指定自定义测试文件：

```bash
export TEST_PDF_PATH=/path/to/your/test.pdf
python tests/api_tests/test_async_api.py
```

## 🔧 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TEST_PDF_PATH` | 测试 PDF 文件路径 | `tests/unittest/pdfs/test.pdf` |
| `TIANSHU_DB_PATH` | Tianshu 数据库路径 | `projects/mineru_tianshu/mineru_tianshu.db` |
| `API_URL` | API 服务地址 | `http://localhost:8000` |

## 💡 常用命令

### 运行所有 API 测试

```bash
# 顺序运行
python tests/api_tests/test_async_api.py
python tests/api_tests/test_async_advanced.py
```

### 清理测试数据

```bash
# 清理失败任务
python tests/utils/clean_failed_tasks.py

# 重置数据库（慎用）
bash tests/utils/clean_db.sh
```

### 查看队列状态

```bash
curl http://localhost:8000/api/v1/queue/stats | python3 -m json.tool
```

### 生成覆盖率报告

```bash
python tests/get_coverage.py
```

## 📈 性能基准

### 异步 API 性能

基于 `test_async_advanced.py` 的测试结果：

| 指标 | 结果 |
|-----|------|
| **任务提交响应** | < 100ms |
| **平均响应时间** | ~13ms |
| **并发吞吐量** | ~450 任务/秒 |
| **单任务处理时间** | ~14秒（CPU 模式）|

### 同步 API vs 异步 API

| 特性 | 同步 API | 异步 API |
|-----|---------|---------|
| 提交响应 | 20+ 秒（阻塞）| < 100ms |
| 并发能力 | 单任务阻塞 | 大量并发 |
| 任务持久化 | ❌ | ✅ |
| 进度查询 | ❌ | ✅ |
| 优先级队列 | ❌ | ✅ |

## 🐛 故障排查

### 1. 服务连接失败

```
❌ 无法连接到服务器!
```

**检查：**
```bash
# 确认服务是否运行
curl http://localhost:8000/api/v1/queue/stats

# 查看端口占用
lsof -i :8000
```

**解决：**
```bash
cd projects/mineru_tianshu
python start_all.py --api-port 8000 --accelerator cpu
```

### 2. 测试文件不存在

```
❌ 测试文件不存在: tests/unittest/pdfs/test.pdf
```

**解决：**
```bash
# 复制测试文件
cp /path/to/your/test.pdf tests/unittest/pdfs/

# 或使用环境变量
export TEST_PDF_PATH=/path/to/your/test.pdf
```

### 3. 数据库锁定

```
❌ 数据库错误: database is locked
```

**解决：**
- 等待当前操作完成
- 停止服务后再操作
- 检查是否有多个进程访问数据库

### 4. macOS CUDA 错误

```
❌ Torch not compiled with CUDA enabled
```

**解决：**
```bash
# 使用 CPU 模式
python start_all.py --accelerator cpu

# 或 MPS 模式（Apple Silicon）
python start_all.py --accelerator mps
```

## 📚 相关文档

- **主项目文档：** [README.md](../README.md)
- **Tianshu 文档：** [projects/mineru_tianshu/README.md](../projects/mineru_tianshu/README.md)
- **API 文档：** http://localhost:8000/docs（需先启动服务）

## 🤝 贡献指南

### 添加新测试

1. 在相应目录下创建测试文件
2. 遵循现有命名规范（`test_*.py`）
3. 添加清晰的文档字符串
4. 更新相关 README

### 测试规范

```python
#!/usr/bin/env python3
"""
测试描述
"""

def test_feature():
    """测试某个功能"""
    # 准备
    ...
    
    # 执行
    ...
    
    # 验证
    assert result == expected
    
    # 清理（如需要）
    ...
```

### 提交测试

```bash
# 运行所有测试确保通过
python tests/api_tests/test_async_api.py
python tests/api_tests/test_async_advanced.py

# 提交代码
git add tests/
git commit -m "Add: 新测试功能描述"
git push
```

## 📞 获取帮助

遇到问题？

1. 查看相关 README 文档
2. 检查 [FAQ](api_tests/README.md#💡-常见问题)
3. 提交 Issue：https://github.com/opendatalab/MinerU/issues

---

**测试愉快！** 🎉

