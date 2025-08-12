# 批量导入 GUI - 模块化 RAG 系统

## 🚀 简介

Bulk Ingest GUI 是一款现代桌面应用，用于在模块化 RAG（检索增强生成）系统中处理与存储文档。它以 `rag_core.py` 为系统核心，提供高级处理、语义分块、嵌入缓存与向量存储等功能。

## 🏗️ 架构

应用遵循 **MVC + Services** 的模块化结构：

```
bulk_ingest_GUI/
├── controllers/          # 控制器（应用逻辑）
│   └── main_controller.py
├── models/              # 数据模型
│   └── document_model.py
├── services/            # 服务（业务逻辑）
│   ├── configuration_service.py
│   └── document_service.py
├── views/               # 视图（GUI 界面）
│   └── main_view.py
├── widgets/             # 自定义控件
│   ├── document_preview_widget.py
│   └── statistics_widget.py
├── utils/               # 工具与常量
│   ├── constants.py
│   └── exceptions.py
├── main.py              # 主入口
└── run_gui.py           # 启动脚本
```

## 🔧 功能特性

### ✅ 核心功能
- 文档处理：支持多种格式（PDF、DOCX、TXT 等）
- 高级语义分块：利用结构化元素提升质量
- 嵌入缓存：内存+磁盘缓存优化性能
- 向量存储：与 ChromaDB 深度集成
- 现代界面：基于 Tkinter 的直观 GUI

### ✅ 进阶功能
- 文档预览：存储前先看内容
- 详细统计：处理、缓存、数据库状态
- 筛选与搜索：快速定位文档
- 导入/导出：保存与加载文档清单
- 批处理：高效处理大批量数据

## 🚀 安装与使用

### 依赖
- Python 3.8+
- `rag_core.py` 的依赖
- Tkinter（随 Python 提供）

### 安装
```bash
git clone <repository-url>
cd MCP_RAG
pip install -r requirements.txt
python bulk_ingest_GUI/run_gui.py
```

### 基本用法
1) 选择目录：点击“浏览”并选中文档文件夹
2) 处理：点击“处理”提取内容
3) 复审：用筛选与预览检查文档
4) 选择：勾选准备存储的文档
5) 存储：点击“存储所选”写入向量库

## 🔄 数据流

```
1. 用户选择目录
   ↓
2. MainView 调用 MainController
   ↓
3. MainController 使用 DocumentService
   ↓
4. DocumentService 调用 rag_core.py
   ↓
5. rag_core.py 通过 Unstructured 进行处理
   ↓
6. DocumentService 使用 ChromaDB 存储
   ↓
7. UI 更新显示结果
```

## 🎯 与 rag_core.py 的集成

应用以 `rag_core.py` 为核心，复用其优化能力：

- `load_document_with_elements()`：按结构元素加载文档
- `add_text_to_knowledge_base_enhanced()`：语义分块后的存储
- `get_vector_store()`：优化配置的 ChromaDB
- `get_cache_stats()`：嵌入缓存统计
- `clear_embedding_cache()`：缓存管理

## � 可用控件

### DocumentPreviewWidget
- 以格式化方式展示文档内容
- 提供大小与词数统计
- 一键复制内容
- 长文档自动滚动

### StatisticsWidget
- 处理统计页：处理结果统计
- 缓存统计页：嵌入缓存信息
- 数据库页：向量库状态
- 提供刷新与优化按钮

## 🔧 配置

通过 `ConfigurationService` 管理配置：

```python
config = {
    'ui.window_size': '1200x800',
    'processing.max_preview_length': 2000,
    'processing.batch_size': 10,
    'storage.use_semantic_chunking': True
}
```

## � 故障排查

### 导入错误
```bash
cd MCP_RAG
python bulk_ingest_GUI/run_gui.py
```

### 依赖错误
```bash
pip install -r requirements.txt
```

### 权限错误
```bash
# Windows：必要时以管理员运行
# Linux/Mac：检查写权限
```

## 🚀 后续规划

- [ ] 更多文件格式支持
- [ ] 集成 RAG 查询界面
- [ ] 高级分块配置
- [ ] 导出多种格式
- [ ] 对接外部 API
- [ ] 深/浅色主题
- [ ] 快捷键支持
- [ ] 详细日志文件

## 📝 贡献指南

1) Fork 项目
2) 新建分支：`git checkout -b feature/AmazingFeature`
3) 提交修改：`git commit -m 'Add some AmazingFeature'`
4) 推送分支：`git push origin feature/AmazingFeature`
5) 发起 Pull Request

## 📄 许可证

与主项目相同的许可证。

## 🤝 支持

遇到问题请：
- 查阅 `rag_core.py` 文档
- 在仓库提交 issue
- 查看应用日志获取更多细节 
