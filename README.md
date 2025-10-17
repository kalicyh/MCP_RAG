# 个人 RAG 服务器（基于 MCP）

本项目实现了一个兼容模型上下文协议（MCP，Model Context Protocol）的服务器，赋能 AI 客户端（如 Cursor、Claude for Desktop 等）具备增强检索生成（RAG，Retrieval-Augmented Generation）能力。允许语言模型访问基于你自己文本和文档的本地私有知识库。

## ✨ 主要特性

- **为你的 AI 提供持久记忆**：让 AI 学习新信息，并能跨会话记忆。
- **🆕 图形用户界面（GUI）**：直观的桌面应用，带有结构化脚本，方便安装与运行。
- **🚀 高级文档处理**：支持超过 25 种格式文件，包括 PDF、DOCX、PPTX、XLSX、图片（含 OCR）、邮件等。
- **🧠 智能处理引擎 Unstructured**：企业级文档处理，保持语义结构，自动去噪，支持复杂格式。
- **🔄 可靠回退机制**：多重处理策略确保所有文档均能成功处理。
- **📊 结构化元数据**：详细文档结构信息（标题、表格、列表），方便追踪。
- **🔍 高级搜索过滤**：基于元数据的精准过滤，提高搜索相关性。
- **📈 知识库统计信息**：详尽内容与结构分析。
- **本地私有大语言模型**：通过 [Ollama](https://ollama.com/) 使用本地模型（如 Llama 3、Mistral），保证数据和提问不出本机。
- **100% 本地离线运行**：语言模型和向量嵌入均本地执行，数据不联网，模型下载完成后无需网络。
- **批量导入支持**：专用脚本批量处理文档目录，高效构建知识库。
- **模块化架构**：RAG 逻辑与服务器、导入脚本分离，便于维护和扩展。
- **Markdown 备份**：自动保存处理后的每个文档为 Markdown 格式，便于验证和复用。
- **🆕 来源元数据**：完整的信息溯源，回答附带来源归属。
- **🆕 AI 代理优化**：详尽描述和智能错误处理，提升代理使用效率。
- **🆕 结构化脚本体系**：模块化脚本划分安装、运行和诊断流程。


---

#### OpenAI 配置（云端 GPT-3.5/4）

如需使用 OpenAI 或兼容 API（如代理/Azure），在 `.env` 设置：
```env
MODEL_TYPE=OPENAI
OPENAI_API_KEY=sk-xxxxxx
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
```
参数说明：
- `MODEL_TYPE`：`OPENAI` 或 `OLLAMA`
- `OPENAI_API_KEY`：OpenAI API 密钥
- `OPENAI_API_BASE`：API 地址（官方/代理/Azure）
- `OPENAI_MODEL`：如 `gpt-3.5-turbo`、`gpt-4`
- `OPENAI_TEMPERATURE`：生成温度（0~1）

**切换模型**：仅需修改 `.env` 的 `MODEL_TYPE` 字段。

**常见问题：**
- API Key 无效/额度不足：检查密钥与调用额度
- API 地址错误：确认 `OPENAI_API_BASE` 正确（代理/Azure）
- 模型名称不支持：确认所填模型已开放
- 网络问题：如连接超时，请检查网络或代理

**测试 OpenAI：**
```bash
curl --request POST \
    --url https://api.openai.com/v1/chat/completions \
    --header 'Authorization: Bearer sk-xxxxxx' \
    --header 'Content-Type: application/json' \
    --data '{
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好"}]
    }'
```

### 方式 3：配置 MCP 客户端（例如 Cursor）

为了让你的 AI 编辑器使用服务器，你必须对其进行配置。

1. **找到你编辑器的 MCP 服务器配置文件。** 对于 Cursor，请在其配置目录（Windows 上为“%APPDATA%\cursor”）中查找类似“mcp_servers.json”的文件。如果该文件不存在，你可以创建它。
2. **将以下配置添加到 JSON 文件。**

此方法使用 MCP 服务器脚本 (`run_server_organized.bat`) 来运行 RAG 服务器。

**重要提示！** 您必须将“D:\full\path\to\your\MCP_RAG\project”替换为您计算机上该项目文件夹的实际绝对路径。

```json
{
    "mcpServers": {
        "rag": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/app/mcp_server_organized_cloud",
                "server.py"
            ],
            "env": {
                "PYTHONUNBUFFERED": "1",
                "MODEL_TYPE": "OPENAI",

                "OLLAMA_MODEL": "phi3",
                "OLLAMA_TEMPERATURE": "0",

                "OPENAI_API_KEY": "key",
                "OPENAI_API_BASE": "https://api.openai.com/v1",
                "OPENAI_MODEL": "gpt-4o-mini",
                "OPENAI_TEMPERATURE": "0",

                "EMBEDDING_PROVIDER": "OPENAI",
                "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",

                "COLLECTION_NAME": "default_collection"
            }
        }
    }
}
```

3. **重启编辑器。** 启动后，编辑器会检测并启动 MCP 服务器，这将显示 RAG 工具以供聊天使用。

### 方式四：在聊天中直接调用工具

配置完成后，您可以直接在编辑器聊天中使用这些工具。

### 可用工具：



**1. `learn_text(text, source_name)` - 添加文本信息**
```
@rag learn_text("钛的熔点为 1.668 °C。", "material_properties")
```
- **使用场景**：添加事实、定义、讨论注释等。
- **参数**：
- `text`：要存储的内容
- `source_name`：源的描述性名称（可选，默认为“manual_input”）
**2. `learn_document(file_path)` - 处理文档**
```
@rag learn_document("C:\\Reports\\q3.pdf")
```

- **适用场景**：处理 PDF、DOCX、PPTX、XLSX、TXT、HTML、CSV、JSON、XML、图片、电子邮件以及超过 25 种其他格式
- **增强功能**：
- **智能处理**：使用非结构化数据去除噪音并保留结构
- **后备系统**：多种策略确保处理成功
- **结构化元数据**：标题、表格和列表的详细信息
- **自动转换**：根据文件类型优化处理
- **已保存副本**：处理后的文档保存在 `./converted_docs/` 中

**3. `ask_rag(query)` - 查询信息**
```
@rag ask_rag("钛的熔点是多少？")
```
- **使用场景**：搜索先前存储的信息
- **答案包含**：
- AI 生成的答案，并增强了上下文
- 📚 包含结构化元数据的来源列表
- 每个来源的相关性信息

**4. `ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)` - 使用过滤器搜索**
```
@rag ask_rag_filtered("我们有哪些数据表？", file_type=".pdf", min_tables=1)
```
- **何时使用**：使用元数据过滤器进行更精确的搜索
- **可用的过滤器**：
- `file_type`：文件类型（例如，".pdf"、".docx"、".xlsx"）
- `min_tables`：文档中表格的最小数量
- `min_titles`：文档中标题的最小数量
- `processing_method`：使用的处理方法
- **优点**：搜索更相关、更具体

**5. `get_knowledge_base_stats()` - 知识库统计信息**
```
@rag get_knowledge_base_stats()
```
- **使用场景**：获取存储内容信息
- **提供的信息**：
- 文档总数
- 按文件类型分布
- 结构统计信息（表格、标题、列表）
- 使用的处理方法

#### 完整流程示例：
```bash
@rag learn_text("钛的熔点是 1,668°C。", "material_properties")
@rag learn_document("C:\\Documents\\manual_titanium.pdf")
@rag ask_rag("钛的熔点是多少？")
@rag ask_rag_filtered("我们有哪些表格数据？", min_tables=1)
@rag get_knowledge_base_stats()
```

**预期回答：**

```
钛的熔点是 1668°C。

📚 信息来源：  
   1. material_properties（手动输入）  
   2. manual_titanio.pdf（第3页，“物理性能”章节）

📊 过滤后搜索统计：  
   • 发现包含表格的文档数量：3  
   • 文件类型：PDF（2份）、DOCX（1份）  
   • 表格总数：7  
```

---

## 🧪 测试与验证

### 测试系统

验证一切是否正常运行：

```bash
# 试用增强型 RAG 系统的所有功能
python test_enhanced_rag.py
```

#### **改进的测试脚本 (`test_enhanced_rag.py`)**

该测试脚本验证了所有已实施的改进：

**🧪 包含的测试：**
- **改进的文档处理**：使用结构化元数据验证非结构化系统
- **改进的知识库**：测试改进的分块和丰富的元数据
- **MCP 服务器集成**：验证改进的服务器工具
- **格式支持**：确认超过 25 种格式的配置

**📊 输出信息：**
- 每个测试的状态（✅ 通过 / ❌ 失败）
- 提取的结构化元数据
- 使用的处理方法
- 源和分块信息
- 完整的系统摘要

### 验证数据库
存储位置：
- 向量数据库：`./rag_mcp_db/`
- 转换副本：`./converted_docs/`（记录处理方法）

---

## 🤖 AI 代理使用

该系统针对 AI 代理进行了优化。请参阅 [`AGENT_INSTRUCTIONS.md`](./AGENT_INSTRUCTIONS.md) 了解以下内容：

- 详细使用指南
- 用例示例
- 最佳实践
- 错误处理
- 重要注意事项

### 代理功能：

- **每个工具的详细描述**
- **清晰具体的使用示例**
- **智能错误处理**并提供实用建议
- **源元数据**，实现全面可追溯性
- **结构化响应**，包含源信息

--

## 🔧 已实施的技术增强

本节介绍了将系统转变为企业级解决方案的高级技术增强功能。

### **A. 使用非结构化数据进行智能处理**

Unstructured 是一个文档处理库，它的功能远不止简单的文本提取。它能够分析文档的语义结构，从而：

- 识别元素：标题、段落、列表、表格
- 去除噪音：移除页眉、页脚和不相关的元素
- 保留上下文：维护文档的层次结构和结构
- 处理复杂格式：扫描的 PDF、包含表格的文档等。

#### **按文件类型优化配置：**

```python
UNSTRUCTURED_CONFIGS = {
    '.pdf': {
        'strategy': 'hi_res',        # Alta resolución para PDFs complejos
        'include_metadata': True,    # Incluir metadatos estructurales
        'include_page_breaks': True, # Preservar saltos de página
        'max_partition': 2000,       # Tamaño máximo de partición
        'new_after_n_chars': 1500    # Nuevo elemento después de N caracteres
    },
    '.docx': {
        'strategy': 'fast',          # Office 文档的快速处理
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    # ... 超过 25 种格式的配置
}
```

#### **智能元素处理：**

```python
def process_unstructured_elements(elements: List[Any]) -> str:
    """处理 Unstructured 元素，保持语义结构。"""
    for element in elements:
        element_type = type(element).__name__
        
        if element_type == 'Title':
            # Los títulos van con formato especial
            processed_parts.append(f"\n## {element.text.strip()}\n")
        elif element_type == 'ListItem':
            # Las listas mantienen su estructura
            processed_parts.append(f"• {element.text.strip()}")
        elif element_type == 'Table':
            # Las tablas se convierten a texto legible
            table_text = convert_table_to_text(element)
            processed_parts.append(f"\n{table_text}\n")
        elif element_type == 'NarrativeText':
            # El texto narrativo va tal como está
            processed_parts.append(element.text.strip())
```

### **B. 强大的回退系统**

#### **级联回退策略：**

系统会按优先顺序尝试多种策略：

1. **非结构化，采用最佳配置**
- 使用特定文件类型的设置
- 最高处理质量

2. **非结构化，采用基本配置**
- “快速”策略，确保兼容性
- 更简单但功能强大的处理

3. **语言链专用加载器**
- 每种文件类型使用专用加载器
- 针对有问题格式的最后解决方案

#### **回退示例：**

```python
def load_document_with_fallbacks(file_path: str) -> tuple[str, dict]:
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Estrategia 1: Unstructured óptimo
    try:
        config = UNSTRUCTURED_CONFIGS.get(file_extension, DEFAULT_CONFIG)
        elements = partition(filename=file_path, **config)
        processed_text = process_unstructured_elements(elements)
        metadata = extract_structural_metadata(elements, file_path)
        return processed_text, metadata
    except Exception as e:
        log(f"Core Warning: Unstructured óptimo falló: {e}")
    
    # Estrategia 2: Unstructured básico
    try:
        elements = partition(filename=file_path, strategy="fast")
        # ... procesamiento
    except Exception as e:
        log(f"Core Warning: Unstructured básico falló: {e}")
    
    # Estrategia 3: LangChain fallbacks
    try:
        fallback_text = load_with_langchain_fallbacks(file_path)
        # ... procesamiento
    except Exception as e:
        log(f"Core Warning: LangChain fallbacks fallaron: {e}")
    
    return "", {}  # Solo si todas las estrategias fallan
```

### **C. 丰富的结构元数据**

#### **捕获的结构信息：**

```python
def extract_structural_metadata(elements: List[Any], file_path: str) -> Dict[str, Any]:
    structural_info = {
        "total_elements": len(elements),
        "titles_count": sum(1 for e in elements if type(e).__name__ == 'Title'),
        "tables_count": sum(1 for e in elements if type(e).__name__ == 'Table'),
        "lists_count": sum(1 for e in elements if type(e).__name__ == 'ListItem'),
        "narrative_blocks": sum(1 for e in elements if type(e).__name__ == 'NarrativeText'),
        "total_text_length": total_text_length,
        "avg_element_length": total_text_length / len(elements) if elements else 0
    }
    
metadata = {
        "source": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": os.path.splitext(file_path)[1].lower(),
        "processed_date": datetime.now().isoformat(),
        "processing_method": "unstructured_enhanced",
        "structural_info": structural_info
    }
```

#### **结构化元数据的优势：**

- **可追溯性**：您可以准确了解文档的哪个部分被使用
- **质量**：内容结构信息
- **优化**：用于改进后续处理的数据
- **调试**：用于解决问题的详细信息

### **D. 改进的智能文本断字功能**

#### **优化配置：**

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Tamaño máximo de cada fragmento
    chunk_overlap=200,      # Caracteres que se comparten entre fragmentos
    length_function=len,    # Función para medir longitud
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Separadores inteligentes
)
```

#### **智能分隔符：**

系统会按以下顺序查找最佳断点：
1. **`\n\n`** - 段落（最佳选择）
2. **`\n`** - 换行符
3. **`. `** - 句尾
4. **`! `** - 感叹号结尾
5. **`? `** - 疑问句结尾
6. **` `** - 空格（最后选择）

### **E. 搜索引擎优化**

#### **当前配置：**

```python
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",  # Búsqueda con umbral de similitud
search_kwargs={
        "k": 5,                # Recupera 5 fragmentos más relevantes
        "score_threshold": 0.3, # Umbral de distancia (similitud > 0.7)
    }
)
```

#### **优化参数：**

- **`k=5`**：从 5 个不同来源获取信息，以获得更完整的答案
- **`score_threshold=0.3`**：确保仅使用高度相关的信息（相似度 > 70%）
- **相似度搜索**：查找语义上最相似的内容

### **F. 自动文本清理**

#### **清理过程：**

```python
def clean_text_for_rag(text: str) -> str:
    """Limpia y prepara el texto para mejorar la calidad de las búsquedas RAG."""
    if not text:
        return ""
    
    # Eliminar espacios múltiples y saltos de línea excesivos
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres especiales problemáticos pero mantener puntuación importante
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']', '', text)
    
    # Normalizar espacios alrededor de puntuación
    text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
    
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text
```

### **G. 高级元数据过滤系统**

#### **过滤功能：**

系统现已包含高级过滤功能，可实现更精确、更相关的搜索：

```python
def create_metadata_filter(file_type: str = None, processing_method: str = None,
                          min_tables: int = None, min_titles: int = None,
                          source_contains: str = None) -> dict:
    """Crea filtros de metadatos para búsquedas más precisas."""
    filters = []
    
    if file_type:
        filters.append({"file_type": file_type})
    if processing_method:
        filters.append({"processing_method": processing_method})
    if min_tables:
        filters.append({"structural_info_tables_count": {"$gte": min_tables}})
    if min_titles:
        filters.append({"structural_info_titles_count": {"$gte": min_titles}})
    if source_contains:
        filters.append({"source": {"$contains": source_contains}})
    
    return {"$and": filters} if len(filters) > 1 else filters[0] if filters else None
```

#### **使用过滤器搜索：**

```python
def search_with_metadata_filters(vector_store: Chroma, query: str, 
                                metadata_filter: dict = None, k: int = 5) -> List[Any]:
    """Realiza búsquedas con filtros de metadatos para mayor precisión."""
    if metadata_filter:
        # Búsqueda con filtros específicos
        results = vector_store.similarity_search_with_relevance_scores(
            query, k=k, filter=metadata_filter
        )
    else:
        # Búsqueda normal sin filtros
        results = vector_store.similarity_search_with_relevance_scores(query, k=k)
    
    return results
```

#### **知识库统计：**

```python
def get_document_statistics(vector_store: Chroma) -> dict:
    """Obtiene estadísticas detalladas sobre la base de conocimientos."""
    all_docs = vector_store.get()
    
    if not all_docs or not all_docs.get('metadatas'):
        return {"total_documents": 0}
    
    metadatas = all_docs['metadatas']
    
    # Análisis por tipo de archivo
    file_types = {}
    processing_methods = {}
    total_tables = 0
    total_titles = 0
    
    for metadata in metadatas:
        file_type = metadata.get("file_type", "unknown")
        processing_method = metadata.get("processing_method", "unknown")
        tables_count = metadata.get("structural_info_tables_count", 0)
        titles_count = metadata.get("structural_info_titles_count", 0)
        
        file_types[file_type] = file_types.get(file_type, 0) + 1
        processing_methods[processing_method] = processing_methods.get(processing_method, 0) + 1
        total_tables += tables_count
        total_titles += titles_count
    
    return {
        "total_documents": len(metadatas),
        "file_types": file_types,
        "processing_methods": processing_methods,
        "total_tables": total_tables,
        "total_titles": total_titles,
        "avg_tables_per_doc": total_tables / len(metadatas) if metadatas else 0,
        "avg_titles_per_doc": total_titles / len(metadatas) if metadatas else 0
    }
```

#### **过滤用例：**

1) 按文件类型过滤 PDF：
```python
pdf_filter = create_metadata_filter(file_type=".pdf")
results = search_with_metadata_filters(vector_store, "datos", pdf_filter)
```

2) 仅含表格的文档：
```python
tables_filter = create_metadata_filter(min_tables=1)
results = search_with_metadata_filters(vector_store, "datos tabulares", tables_filter)
```

3) 按处理方法过滤（仅 Unstructured 增强）：
```python
unstructured_filter = create_metadata_filter(processing_method="unstructured_enhanced")
results = search_with_metadata_filters(vector_store, "contenido", unstructured_filter)
```

4) 组合过滤：
```python
complex_filter = create_metadata_filter(file_type=".pdf", min_tables=1, processing_method="unstructured_enhanced")
results = search_with_metadata_filters(vector_store, "datos", complex_filter)
```

### **H. 增强型 MCP 工具**

#### **新增工具：**

1. **`ask_rag_filtered`**：使用元数据过滤器进行搜索
2. **`get_knowledge_base_stats`**：详细的知识库统计信息

#### **与 AI 代理集成：**

新工具针对 AI 代理进行了优化，具有以下特点：
- **参数和用例的详细描述**
- **每个工具的具体示例**
- **智能错误处理**并提供实用建议
- **结构化响应**并提供元数据信息

---

## 🧲 向量嵌入提供商切换（HF 本地 vs OpenAI 云端）

系统同时支持两种嵌入方案：

- 本地 HuggingFace（默认 all-MiniLM-L6-v2，768 维）：免费、低延迟，可用 CPU/GPU 计算
- OpenAI Embeddings（默认 text-embedding-3-large，≈3072 维）：精度高、需网络与费用

在根目录 `.env` 中配置：

```ini
# 嵌入提供商：HF 或 OPENAI（默认 HF）
EMBEDDING_PROVIDER=OPENAI

# OpenAI 嵌入模型（可选，默认 text-embedding-3-large）
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# 可选：覆盖集合名前缀（系统会自动派生提供商/模型后缀）
# COLLECTION_NAME=default_collection
```

注意事项：
- 切换提供商/模型会改变嵌入向量维度。为避免维度冲突，系统自动为 Chroma 集合名追加后缀（例如 `default_collection-openai_text-embedding-3-large` 或 `default_collection-hf_all-MiniLM-L6-v2`）。
- 如需继续使用既有旧集合，可把 EMBEDDING_PROVIDER 切回原值；如果想迁移，请重新入库（re-ingest）。
- 日志会标明当前嵌入分支：
    - HF 本地：显示“使用 GPU/CPU 进行 embeddings 计算”
    - OpenAI：显示“使用 OpenAI Embeddings: text-embedding-3-large …”

常见问题：
- OpenAI 调用失败：检查 OPENAI_API_KEY、OPENAI_API_BASE（代理/Azure）、网络连通性与配额
- 维度不匹配错误：确保检索使用与入库一致的提供商/模型，或使用系统自动区分的集合名
- 性能与成本：HF 免费但精度稍低；OpenAI 精度更高但有调用成本

