# 📁 `tests/` 文件夹 - MCP 服务器单元测试

## 🎯 **这个文件夹的用途是什么？**

`tests/` 文件夹是 Python 项目中用于组织**单元测试和集成测试**的**标准惯例**。其用途如下：

### 🔍 **主要目标**

1. **单元测试**：独立测试各个函数
2. **集成测试**：验证模块是否能够正常工作
3. **回归测试**：确保更改不会破坏现有功能
4. **实时文档**：测试作为预期行为的文档

### 🔄 与其他测试脚本的区别

| 类型 | 文件 | 目的 |
|------|------|------|
| 系统验证 | `test_mcp_server_validation.py` | 全链路系统与架构验证 |
| 单元测试 | `tests/` | 细粒度单测与具体用例 |

## 📋 目录内容

```
tests/
├── __init__.py                    # 使 tests 成为 Python 包
├── test_document_tools.py         # 文档工具测试
├── test_search_tools.py           # 检索工具测试
├── test_utility_tools.py          # 工具/维护功能测试
├── run_all_tests.py              # 运行全部测试的脚本
└── README.md                     # 本文件
```

## 🧪 可用测试文件

### 1) `test_document_tools.py`
覆盖文档处理相关函数：
- ✅ `learn_text()` 手动添加文本
- ✅ `learn_document()` 处理文件
- ✅ `learn_from_url()` 处理 URL
- ✅ 错误与边界条件处理
- ✅ RAG 状态配置

### 2) `test_search_tools.py`
覆盖搜索与问答：
- ✅ `ask_rag()` 基本问答
- ✅ `ask_rag_filtered()` 带过滤问答
- ✅ 检索器与 QA 链配置
- ✅ 向量库错误处理
- ✅ 回答中的来源文档

### 3) `test_utility_tools.py`
维护与实用功能：
- ✅ `get_knowledge_base_stats()` 知识库统计
- ✅ `get_embedding_cache_stats()` 嵌入缓存统计
- ✅ `clear_embedding_cache_tool()` 清理缓存
- ✅ `optimize_vector_database()` 优化数据库
- ✅ `get_vector_database_stats()` 数据库统计
- ✅ `reindex_vector_database()` 重建索引

## 🚀 如何运行测试

方式一：全部运行
```bash
# 于 mcp_server_organized 目录下
python tests/run_all_tests.py
```

### **选项 2：运行特定测试**
```bash
# 文档工具测试
python -m unittest tests.test_document_tools

# 搜索工具测试
python -m unittest tests.test_search_tools

# 实用工具测试
python -m unittest tests.test_utility_tools
```

### **选项 3：更详细地运行**
```bash
# 增加详细程度
python -m unittest tests.test_document_tools -v

# 运行特定的课程
python -m unittest tests.test_document_tools.TestDocumentTools -v

# 执行特定方法
python -m unittest tests.test_document_tools.TestDocumentTools.test_learn_text_basic -v
```

## 📊 **包含的测试类型：**

### **基本测试**
- ✅ 函数正常运行
- ✅ 有效参数
- ✅ 预期响应

### **错误测试**
- ✅ 无效参数
- ✅ 未初始化的 RAG 状态
- ✅ 向量存储失败
- ✅ 配置错误

### **配置测试**
- ✅ RAG 状态配置
- ✅ 配置持久化
- ✅ 模块间状态共享

### **集成测试**
- ✅ 完整工作流
- ✅ 模块间交互
- ✅ 真实数据

### **边缘案例测试**
- ✅ 空向量存储
- ✅ 大型向量存储
- ✅ 极端参数

## 🔧 **技术特性：**

### **模拟和仿真**
- 🔄 使用 `unittest.mock` 模拟依赖关系
- 🔄 模拟向量存储隔离测试
- 🔄 模拟 QA 链，用于控制响应
- 🔄 模拟嵌入缓存

### **自动配置**
- 🔄 每次测试自动执行 `setUp()`
- 🔄 自动清理临时文件
- 🔄 每次测试后恢复状态

### **详细报告**
- 📊 每个模块的统计数据
- 📊 总体成功率
- 📊 识别具体问题
- 📊 自动保存报告

## 📈 **单元测试的优势：**

### **开发阶段**
- 🚀 **早期错误检测**
- 🚀 **安全重构**
- 🚀 **行为文档**
- 🚀 **代码信心**

### **维护阶段**
- 🔧 **快速回归识别**
- 🔧 **变更验证**
- 🔧 **坚实的改进基础**
- 🔧 **减少生产环境中的 Bug**

### **团队阶段**
- 👥 **代码理解共享**
- 👥 **更轻松的入职培训**
- 👥 **质量标准**
- 👥 **增强协作**

## 🎯 **何时使用这些测试：**

### **开发阶段**
- ✅ 开发之前提交
- ✅ 添加新功能时
- ✅ 重构现有代码时
- ✅ 修复错误时

### **在 CI/CD 中**
- ✅ 在每个拉取请求中
- ✅ 每次发布前
- ✅ 在自动构建中
- ✅ 用于质量验证

### **用于验证**
- ✅ 验证代码是否正常运行
- ✅ 确保没有任何问题
- ✅ 验证边缘情况
- ✅ 确认预期行为

## 💡 **后续步骤：**

1. **运行测试**以验证当前状态
2. **审查失败的测试**并修复问题
3. **添加新测试**以添加更多功能
4. **集成到 CI/CD**以实现自动化
5. **记录具体用例**

## 🔗 **与其他文件的关系：**

- **`test_mcp_server_validation.py`**：系统级测试
- **`src/tools/`**：被测试的源代码
- **`server.py`**：MCP 主服务器
- **`requirements.txt`**：依赖清单

---

**单元测试是“稳健、可维护”代码的基石！**🧪✨ 
