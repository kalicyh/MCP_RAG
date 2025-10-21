# MCP RAG 工具集

基于模型上下文协议（MCP）的智能知识库系统，提供文档处理、知识问答和向量库管理功能。

> 支持使用豆包与OpenAI

## ✨ 主要特性

- **🧠 智能知识库**：基于向量检索的 RAG 系统，支持语义搜索和智能问答
- **📄 多格式文档处理**：支持超过 25 种文档格式，包括 PDF、DOCX、PPTX、XLSX、图片、邮件等
- **🌐 直观 Web 界面**：Bento 风格布局，分类展示所有工具功能
- **🤖 多模型支持**：兼容 OpenAI、豆包、Ollama 等主流 AI 模型
- **🔍 高级过滤搜索**：支持按文件类型、内容结构等条件进行精确检索
- **📊 统计分析**：提供知识库统计、嵌入缓存分析等数据洞察
- **⚡ 本地化处理**：支持本地模型推理，保护数据隐私
- **🔧 向量库管理**：提供缓存清理、数据库优化等维护功能

## 安装

```bash
# 安装工具
uv tool install mcp_rag

# 升级工具
uv tool install mcp_rag --upgrade

# 卸载工具
uv tool uninstall mcp_rag
```

## 使用

### 启动 MCP 服务器

```bash
mcp_rag server
```

### 启动 Web 界面

```bash
mcp_rag web
```

Web 界面提供直观的 Bento 布局，支持以下工具分类：

- **📥 添加内容**：添加文本和文档到知识库
- **❓ 智能问答**：基于知识库进行问答和检索
- **📊 数据统计**：查看知识库和系统统计信息
- **⚙️ 向量库管理**：优化和维护向量数据库

## 配置

在项目根目录创建 `.env` 文件进行配置：

```env
# OpenAI 配置
OPENAI_API_KEY=
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# 豆包 配置
# OPENAI_API_KEY=
# OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
# OPENAI_MODEL=doubao-1-5-pro-32k-250115
# OPENAI_TEMPERATURE=0
# OPENAI_EMBEDDING_MODEL=doubao-embedding-text-240715
```

#### mcp客户端配置（豆包为例）

```json
{
    "mcpServers": {
        "rag": {
            "command": "uv",
            "args": [
                "run",
                "mcp-rag",
                "serve"
            ],
            "env": {
                "PYTHONUNBUFFERED": "1",

                "OPENAI_API_KEY": "key",
                "OPENAI_API_BASE": "https://ark.cn-beijing.volces.com/api/v3",
                "OPENAI_MODEL": "doubao-1-5-pro-32k-250115",
                "OPENAI_TEMPERATURE": "0",

                "OPENAI_EMBEDDING_MODEL": "doubao-embedding-text-240715",
            }
        }
    }
}
```

## 可用工具

### 添加内容
- `learn_text(text, source_name)` - 添加文本到知识库
- `learn_document(file_path)` - 处理并添加文档到知识库

### 智能问答
- `ask_rag(query)` - 基于知识库回答问题
- `ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)` - 带过滤条件的智能检索

### 数据统计
- `get_knowledge_base_stats()` - 显示知识库统计信息
- `get_embedding_cache_stats()` - 显示嵌入缓存统计
- `get_data_paths()` - 查看存储路径信息

### 向量库管理
- `clear_embedding_cache_tool()` - 清理嵌入缓存
- `optimize_vector_database()` - 优化向量数据库性能
- `get_vector_database_stats()` - 显示向量数据库统计
- `reindex_vector_database()` - 重新索引向量数据库

## 支持格式

支持超过 25 种文档格式，包括 PDF、DOCX、PPTX、XLSX、图片、邮件等。
