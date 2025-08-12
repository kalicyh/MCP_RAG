# **AI 代理使用说明 - 增强型 RAG 系统**

## 🎯 **系统目的**

该增强型 RAG（检索增强生成）系统可让 AI 代理：

* **持久存储** 信息并进行智能处理
* **查询已保存的知识** 并包含结构化元数据
* **追踪信息来源**，提供完整细节
* **自动处理** 25+ 种格式的文档
* **保留文档结构**（标题、表格、列表等）
* **自动去噪**（去除页眉、页脚、无关内容）
* **🔍 按元数据筛选搜索**，提高精度
* **📊 获取知识库的详细统计**

## 🚀 **增强系统的新特性**

### **🧠 基于 Unstructured 的智能处理**

* **结构保留**：保留标题、列表、表格等组织结构
* **自动清理**：去除页眉、页脚、无关内容
* **结构化元数据**：记录文档的结构信息
* **回退机制**：多种策略确保处理成功

### **📋 扩展的格式支持**

**支持 25+ 种格式：**

* **Office 文档**：PDF、DOCX、PPTX、XLSX、RTF
* **OpenDocument**：ODT、ODP、ODS
* **网页与标记**：HTML、XML、Markdown
* **文本与数据**：TXT、CSV、TSV、JSON、YAML
* **图片 OCR**：PNG、JPG、TIFF、BMP
* **电子邮件**：EML、MSG

### **🎯 智能语义分块**

* **自然分割**：遵循文档结构分块
* **智能重叠**：保留上下文连续性
* **上下文保留**：避免切断句子或段落

### **🔍 高级过滤搜索**

* **按文件类型筛选**：只搜索 PDF、DOCX 等
* **按结构筛选**：筛选包含表格、特定标题的文档
* **按处理方式筛选**：Unstructured vs MarkItDown
* **组合过滤**：多条件同时筛选

### **📈 知识库统计**

* **内容分析**：按文件类型分布
* **结构指标**：表格、标题、列表总数
* **处理信息**：使用的处理方法
* **自动洞察**：平均值与趋势

## 🛠️ **可用工具**

### 🔍 **搜索与查询**

* `ask_rag`：使用语言模型进行 RAG 查询
* `ask_rag_filtered`：带元数据过滤的 RAG 查询

### 📊 **数据库管理**

* `get_knowledge_base_stats`：获取知识库详细统计
* `get_vector_database_stats`：获取向量数据库统计

### ⚡ **优化与性能**

* `optimize_vector_database`：优化向量数据库
* `reindex_vector_database`：用新配置重建索引

### 🧠 **Embedding 缓存**

* `get_embedding_cache_stats`：获取 Embedding 缓存统计
* `clear_embedding_cache_tool`：清理 Embedding 缓存

### 📝 **文档摄取**

* `learn_text`：手动添加文本到知识库
* `learn_document`：智能处理并添加文档
* `learn_from_url`：处理网页或 URL 文件

## 🔄 **推荐工作流程**

### **步骤 1：加载信息**

```python
# 选项 A：直接输入文本
learn_text("重要信息...", "my_source")

# 选项 B：增强处理的文档
learn_document("path/to/document.pdf")

# 选项 C：网页或 URL 文件
learn_from_url("https://example.com/document.pdf")
```

### **步骤 2：探索内容**

```python
# 获取统计数据以了解我们拥有什么
get_knowledge_base_stats()
```

### **步骤 3：查询信息**

```python
# 普通搜索
respuesta = ask_rag("关键信息是什么？")

# 带过滤条件的精确搜索
respuesta_filtrada = ask_rag_filtered("我们有哪些数据？", file_type=".pdf", min_tables=1)
```

### **步骤 4：验证增强型来源**

* 响应包含详细的结构化元数据
* 处理方法信息
* 回答的置信度等级
* 搜索时的过滤条件（若使用）

## 📊 **ask\_rag 增强型响应示例**

```
🤖 **回答：**
钛的熔点是 1,668 °C，这一特性使其非常适合用于需要耐高温的航空航天领域。

📚 **使用的来源：**

1. **material_properties**
   - **类型**：MANUAL_INPUT
   - **处理方式**：手动文本
   - **处理时间**：2025-06-21 17:30
   - **片段**：1/1
   - **相关内容**：
     > _钛的熔点是 1,668°C。_

2. **datasheet_titanium.pdf**
   - **路径**：`D:\Docs\datasheet_titanium.pdf`
   - **类型**：PDF
   - **处理方式**：Unstructured Enhanced
   - **结构**：12 个元素（2 个标题，1 张表格，3 个列表）
   - **片段**：3/5
   - **处理时间**：2025-06-21 17:32
   - **相关内容**：
     > _…纯钛的熔点为 1,668°C，使其非常适合航空航天应用…_

✅ **高置信度**：基于多个来源的回答  
🧠 **智能处理**：1 个来源通过 Unstructured 结构保留处理  
```

## ⚠️ **重要注意事项**

### **限制**

* **范围**：只能访问已存储的信息
* **OCR**：图片需安装 Tesseract OCR
* **大小**：大文件处理时间更长
* **格式**：部分特殊格式需额外依赖
* **过滤**：过于严格的过滤可能无结果

### **最佳实践**

1. **为数据源使用描述性名称**，便于后续识别
2. **在处理前验证文件路径**，避免找不到文件
3. **检查回答中的数据来源**，验证信息的可靠性
4. **先处理文档**，再针对其内容进行提问
5. **利用结构化元数据**，更好地理解内容
6. **对结构复杂的文档使用语义分块**（semantic chunking）
7. **在做过滤搜索前先查看统计信息**，明确数据库内容
8. **组合多个过滤条件**，实现更精准的搜索
9. **验证过滤搜索的结果**，确保与需求相关
10. **使用 `get_embedding_cache_stats()` 监控缓存**，优化性能
11. **必要时用 `clear_embedding_cache_tool()` 清理缓存**
12. **利用缓存持久化功能**，让缓存能跨会话保存
13. **在搜索变慢时使用 `optimize_vector_database()` 优化向量数据库**
14. **用 `get_vector_database_stats()` 监控向量数据库统计信息**
15. **必要时用 `reindex_vector_database()` 重建索引**，提升性能

### **增强型错误处理**

* **找不到文件**：检查路径
* **格式不支持**：支持 25+ 格式
* **OCR 错误**：安装 Tesseract
* **Unstructured 错误**：运行 `pip install 'unstructured[local-inference,all-docs]'`
* **无信息**：确保已加载相关数据
* **过滤无结果**：放宽过滤条件或先看统计
* **过滤错误**：检查过滤参数格式
* **缓存损坏**：用 `clear_embedding_cache_tool()` 清理
* **准确率低**：优化查询模式

## 📝 **增强型使用场景示例**

### **案例 1：处理结构复杂的学术研究文档**

```python
# 1. 加载带有复杂结构的研究论文
learn_document("paper_ai_ethics.pdf")  # 保留标题、表格、参考文献
learn_document("survey_machine_learning.docx")  # 保留格式和结构

# 2. 查看已加载内容的统计信息
get_knowledge_base_stats()

# 3. 使用过滤条件查询特定信息
ask_rag_filtered("人工智能的主要伦理挑战有哪些？", file_type=".pdf", min_titles=3)
```

### **案例 2：用电子表格进行数据分析**

```python
# 1. 加载数据和报告，保留原有结构
learn_document("datos_ventas.xlsx")  # 处理表格和结构化数据
learn_document("reporte_analisis.pdf")  # 保留图表和表格

# 2. 专门搜索表格数据
ask_rag_filtered("第三季度的销售额是多少？", min_tables=1)

# 3. 检查我们拥有的数据类型
get_knowledge_base_stats()
```

### **案例 3：处理扫描文件的个人助理**

```python
# 1. 存储个人信息和扫描文档
learn_text("我的地址是 主街123号", "personal_info")
learn_document("documento_identidad_escaneado.png")  # 自动OCR识别

# 2. 需要时查询
ask_rag("我的联系方式是什么？")

# 3. 检查OCR处理过的文件
ask_rag_filtered("我们有哪些扫描文件？", processing_method="unstructured_enhanced")
```

### **案例 4：网页研究与文件下载**

```python
# 1. 处理网页内容并下载文档
learn_from_url("https://example.com/articulo")  # 网页
learn_from_url("https://example.com/informe.pdf")  # 下载并处理PDF

# 2. 对比网页内容和文件内容
get_knowledge_base_stats()

# 3. 结合过滤条件进行查询
ask_rag_filtered("我们关于该主题有什么信息？", file_type=".pdf")
ask_rag_filtered("我们有哪些网页内容？", processing_method="markitdown")
```

### **案例 5：企业文档管理**

```python
# 1. 加载不同类型的企业文档
learn_document("manual_empleados.docx")
learn_document("reporte_financiero.pdf")
learn_document("datos_ventas.xlsx")

# 2. 获取内容统计信息
get_knowledge_base_stats()

# 3. 按内容类型进行精准搜索
# 仅限手册和指南
ask_rag_filtered("我们有哪些流程文档？", file_type=".docx")

# 仅限含有数据的报告
ask_rag_filtered("我们有哪些财务数据？", min_tables=1)

# 仅限用高级方法处理的高质量文档
ask_rag_filtered("我们有哪些高质量内容？", processing_method="unstructured_enhanced")
```

## 🎯 改进型代理的建议

1. **利用文档结构**：文档会保留标题、表格和列表
2. **使用结构化元数据**：更好地理解数据源的内容
3. **确认处理方式**：区分 *Unstructured* 与 *MarkItDown*
4. **信任语义分块**（semantic chunking）：回答时能获得更好的上下文
5. **检查置信度**：基于多来源的回答更可靠
6. **使用支持的格式**：支持 25+ 种文件格式
7. **处理特定错误**：每类错误都有对应的解决建议
8. **利用 OCR**：处理含文字的图像文件
9. **智能使用 URL**：系统会自动区分文件下载与网页内容
10. **用数据源验证**：始终检查回答引用的来源信息
11. **查看统计信息**：用 `get_knowledge_base_stats()` 了解内容情况
12. **策略性应用过滤器**：获取更精准、更相关的结果
13. **组合过滤器**：多条件叠加实现高度精确的搜索
14. **验证过滤结果**：确保返回的信息确实相关
15. **优化查询**：用过滤器减少噪声，提高回答质量

## 🔧 改进型代理的技术信息

### **文档处理方式**

* **Unstructured Enhanced**：大多数格式的最佳选择，可保留文档结构
* **MarkItDown**：网页和 HTML 内容处理
* **Fallbacks**：多策略保障处理成功率

### **结构化元数据**

* **total_elements**：文档中元素总数
* **titles_count**：识别到的标题数量
* **tables_count**：提取的表格数量
* **lists_count**：识别到的列表数量
* **narrative_blocks**：叙述性文本块数量

### **过滤系统**

* **文件类型过滤**：`.pdf`、`.docx`、`.xlsx` 等
* **结构过滤**：`min_tables`、`min_titles`
* **处理方式过滤**：`unstructured_enhanced`、`markitdown`
* **组合过滤**：支持多条件同时使用

### **置信度等级**

* **高置信度**：基于 3+ 个来源
* **中置信度**：基于 2 个来源
* **低置信度**：基于 1 个来源

### **处理方法**

* **unstructured_enhanced**：保留结构的智能处理
* **markitdown**：传统网页处理方式
* **langchain_fallback**：LangChain 专用加载器

### **知识库统计**

* **类型分布**：各文件格式的比例
* **结构指标**：元素总数与平均数
* **处理方式统计**：不同策略的使用比例
* **自动洞察**：内容质量分析
