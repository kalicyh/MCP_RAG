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

## 🏗️ Arquitectura

该项目采用模块化结构，将 MCP 服务器组件与图形用户界面 (GUI) 清晰地分离。这种组织方式有利于每个组件的独立维护、开发和使用。

### 项目结构

```
MCP_RAG/
├── 📁 mcp_server_organized/          # Servidor MCP principal
│   ├── 📄 server.py                  # Servidor MCP con herramientas RAG
│   ├── 📄 run_server_organized.bat   # Script para ejecutar el servidor
│   ├── 📁 src/                       # Código fuente del servidor
│   │   ├── 📄 rag_core.py            # Lógica principal del RAG
│   │   ├── 📄 rag_server_bk.py       # Servidor MCP (backup)
│   │   ├── 📁 models/                # Modelos de datos
│   │   ├── 📁 services/              # Servicios del servidor
│   │   ├── 📁 tools/                 # Herramientas MCP
│   │   └── 📁 utils/                 # Utilidades
│   ├── 📁 tests/                     # Pruebas del servidor
│   ├── 📁 data/                      # Datos del servidor
│   │   ├── 📁 documents/             # Documentos procesados
│   │   └── 📁 vector_store/          # Base de datos vectorial
│   └── 📁 embedding_cache/           # Cache de embeddings
│
├── 📁 bulk_ingest_GUI/               # Interfaz gráfica de usuario
│   ├── 📄 main.py                    # Punto de entrada principal
│   ├── 📄 launch.py                  # Lanzador de la aplicación
│   ├── 📄 start_app.py               # Inicialización de la app
│   ├── 📄 rag_core_wrapper.py        # Wrapper para rag_core
│   ├── 📁 views/                     # Vistas de la interfaz
│   │   └── 📄 main_view.py           # Vista principal
│   ├── 📁 controllers/               # Controladores
│   │   └── 📄 main_controller.py     # Controlador principal
│   ├── 📁 services/                  # Servicios de la GUI
│   │   ├── 📄 document_service.py    # Servicio de documentos
│   │   └── 📄 configuration_service.py # Servicio de configuración
│   ├── 📁 models/                    # Modelos de la GUI
│   ├── 📁 widgets/                   # Widgets personalizados
│   ├── 📁 gui_utils/                 # Utilidades de la GUI
│   ├── 📁 data/                      # Datos de la GUI
│   │   ├── 📁 documents/             # Documentos procesados
│   │   └── 📁 vector_store/          # Base de datos vectorial
│   └── 📁 embedding_cache/           # Cache de embeddings
│
├── 📄 start.bat                      # Script principal de arranque
├── 📄 run_gui.bat                    # Script para ejecutar la GUI
├── 📄 install_requirements.bat       # Instalación de dependencias
├── 📄 requirements.txt               # Dependencias del proyecto
├── 📄 README.md                      # Documentación principal
├── 📄 SCRIPTS_README.md              # Guía de scripts
├── 📄 GUI_ADVANCED_README.md         # Guía de la GUI para ingesta de documentos masivo
└── 📄 AGENT_INSTRUCTIONS.md          # Instrucciones para agentes IA
```

### 主要组件

#### 1）MCP 服务器（`mcp_server_organized/`）
- `server.py`：对外暴露 RAG 工具的 MCP 主服务器
- `src/rag_core.py`：RAG 的核心，包含全部处理逻辑
- `src/tools/`：MCP 工具（`learn_text`、`learn_document`、`ask_rag` 等）
- `src/services/`：服务器端服务（配置、日志等）
- `src/models/`：数据模型
- `src/utils/`：通用工具方法

#### 2）图形界面（`bulk_ingest_GUI/`）
- `main.py`：GUI 应用主入口
- `views/main_view.py`：多标签的主界面
- `controllers/main_controller.py`：界面控制逻辑
- `services/document_service.py`：文档处理服务
- `services/configuration_service.py`：配置管理
- `widgets/`：自定义控件
- `gui_utils/`：GUI 实用工具

#### 3）系统脚本
- `start.bat`：引导用户的启动脚本
- `run_gui.bat`：直接启动 GUI 应用
- `install_requirements.bat`：完整依赖安装
- `check_system.bat`：系统诊断
- `fix_dependencies.bat`：依赖修复

### 数据流

1. **文档提取**：GUI 使用 `rag_core_wrapper.py` 处理文档
2. **存储**：文档存储在向量数据库中
3. **查询**：MCP 服务器访问同一数据库以回答查询
4. **响应**：MCP 工具返回包含源的响应

### **职责分离**

- **MCP 服务器**：专注于向 AI 客户端公开工具
- **GUI**：专注于文档提取的用户体验
- **RAG 核心**：两个组件之间共享逻辑
- **脚本**：自动化和环境管理

这种模块化架构允许：
- ✅ 各个组件独立开发
- ✅ 服务器和 GUI 之间的代码复用
- ✅ 易于维护和调试
- ✅ 新功能的可扩展性
- ✅ 独立使用服务器或 GUI

### 文档清单
- [`AGENT_INSTRUCTIONS.md`](./AGENT_INSTRUCTIONS.md)：面向智能体的完整使用指南
- [`GUI_ADVANCED_README.md`](./GUI_ADVANCED_README.md)：批量导入 GUI 使用指南
- [`SCRIPTS_README.md`](./SCRIPTS_README.md)：脚本体系说明
- [`STORAGE_PROGRESS_README.md`](./STORAGE_PROGRESS_README.md)：存储进度系统文档
- `test_enhanced_rag.py`：系统验证脚本

---

## 🚀 安装和配置指南

请按照以下步骤启动并运行系统。

### 先决条件

- **Python 3.10 及以上版本**
- **Ollama**：确保 [Ollama 已安装](https://ollama.com/) 并正在您的系统上运行。
- **Tesseract OCR（可选）：**用于处理带有文本的图像。请从 [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) 下载或使用 `choco install tesseract`。

### 1. 安装（自动！）

得益于井然有序的脚本系统，安装过程极其简单。

#### **对于用户（推荐）：**
1. **运行主脚本：`start.bat`
2. **选择“1”**安装依赖项
3. **等待**自动安装完成
4. **应用程序将自动启动**

#### **对于开发者：**
- **完整安装：**`install_requirements.bat`
- **运行：**`run_gui.bat`
- **诊断：**`check_system.bat`

脚本系统会为您完成所有操作：
- ✅ 在 `.venv` 文件夹中创建 Python 虚拟环境
- ✅ 自动激活环境
- ✅ 从 `requirements.txt` 安装所有必要的依赖项
- ✅ 自动检测您是否拥有 NVIDIA GPU 并正确安装 PyTorch
- ✅ 安装具有高级功能的 Unstructured
- ✅ 启动应用程序

在后续运行中，脚本将直接激活环境并启动直接安装应用程序。

### 2. 手动安装依赖项（可选）

如果您希望手动安装依赖项或需要特定功能：

```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 安装 Unstructured（完整能力）
pip install "unstructured[local-inference,all-docs]"

# 一些性能相关的建议依赖
pip install python-docx openpyxl beautifulsoup4 pytesseract
```

### 3. 配置 Ollama（关键）

Ollama 是 RAG 系统正常运行所必需的，因为它提供了生成回答的本地语言模型。

#### Ollama 安装步骤

**Windows:**
1. 从 [ollama.com](https://ollama.com/) 下载 Ollama
2. 运行安装程序并按照指示完成安装
3. Ollama 会自动作为服务启动

macOS/Linux：
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 验证安装：

```bash
ollama --version

# 验证服务是否正在运行
ollama list
```

#### 下载模型：

RAG 系统需要一个语言模型来生成回答。我们选择 Ollama 是因为它是免费的：

```bash
# 推荐（速度与质量均衡）
ollama pull llama3

# 更快的替代
ollama pull phi3
ollama pull mistral

# 更强但更吃资源
ollama pull llama3.1:8b
```

#### 在系统中配置模型

模型下载完成后，确保 `rag_core.py` 使用了正确的模型：


```python
# 在 rag_core.py 文件大约第100行，确认使用你的模型：
llm = ChatOllama(model="llama3", temperature=0)
```

**注意：** 如果你下载了不同的模型，请将 `"llama3"` 改成你所使用模型的名称。

#### 测试 Ollama


```bash
# 测试模型是否正常工作
ollama run llama3 "Hello"
```

如果你看到生成的回答，说明 Ollama 正常运行。

#### 常见问题解决方案

**错误：“Ollama is not running”（Ollama 未运行）**

```bash
# 手动启动 Ollama 服务
ollama serve
```

**错误：“Model not found”（未找到模型）**

```bash
# 查看可用模型列表
ollama list

# 如果模型不存在，下载模型
ollama pull llama3
```

**错误：“Out of memory”（内存不足）**

* 使用更小的模型，例如：`ollama pull phi3`
* 关闭其他占用大量内存的应用程序
* 考虑在 Windows 系统中增加虚拟内存容量


### 4. 系统自检

在继续之前，让我们先验证一下一切是否正常运行：

#### 步骤 1：验证 Ollama
```bash
# 验证 Ollama 是否正在运行
ollama list

# 测试模型
ollama run llama3 "Test"
```

#### 步骤 2：检查 Python 依赖项
```bash
python -c "import mcp; print('✅ MCP OK')"
python -c "import langchain; print('✅ LangChain OK')"
python -c "import chromadb; print('✅ ChromaDB OK')"
python -c "import unstructured; print('✅ Unstructured OK')"
```

#### 步骤 3：测试 RAG 系统
```bash
# 运行增强测试脚本
python test_enhanced_rag.py
```

如果一切正常，您将看到：
- ✅ Ollama 正在响应命令
- ✅ 所有依赖项导入均无错误
- ✅ RAG 系统正在处理查询并显示源

**您的 RAG 系统已准备就绪！** 🚀

---

## 📋 支持的文件格式

系统支持 25+ 常见格式，针对每类有优化的处理流程：

### 📄 Office 文档
- PDF（.pdf）- 高分辨率处理
- Word（.docx, .doc）
- PowerPoint（.pptx, .ppt）
- Excel（.xlsx, .xls）
- RTF（.rtf）

### 📁 OpenDocument 文档
- ODT（.odt）
- ODP（.odp）
- ODS（.ods）

### 🌐 Web/标记语言
- HTML（.html, .htm）
- XML（.xml）
- Markdown（.md）

### 📝 纯文本/表格
- TXT（.txt）
- CSV（.csv）
- TSV（.tsv）

### 📊 数据格式
- JSON（.json）
- YAML（.yaml, .yml）

### 🖼️ 图片（含 OCR）
- PNG（.png）
- JPG/JPEG（.jpg, .jpeg）
- TIFF（.tiff）
- BMP（.bmp）

### 📧 邮件
- EML（.eml）
- MSG（.msg）

---

## 🛠️ 用户指南

### 方式 1：使用 GUI 填充知识库（推荐）

添加文档最简单、最直观的方法是使用图形界面。

1. **运行主脚本：** `start.bat`
2. **选择“1”**运行应用程序
3. **应用程序将启动**（安装依赖项可能需要一段时间）
4. **使用“浏览...”按钮**选择包含文档的文件夹
5. **点击“开始处理”**。文件将使用 Unstructured 的高级系统进行处理。
6. **转到“审阅”选项卡**，选择要保存的文件并预览其内容。
7. **转到“存储”选项卡**，然后点击“开始保存”，将选定的文档保存到数据库。

#### ✨ **带有预览和选择功能的批量文档提取 GUI**

为了全面掌控提取过程，我们添加了一个 **GUI**。此版本允许您 **预览** 每个已处理文档的内容，并 **手动选择** 您想要添加到知识库的文档。

**GUI 功能：**
- **智能处理：**使用非结构化数据去除噪音并保留结构
- **实时预览：**保存前查看已处理内容
- **精细选择：**单独标记/取消标记文档
- **结构化元数据：**每个文档的标题、表格和列表信息
- **后备系统：**多种策略确保每个文档都得到处理
- **进度系统：**详细跟踪保存过程

![GUI 处理选项卡](src/images/gui_processing.png)

➡️ **有关如何使用它的完整指南，请参阅[批量上传指南](./GUI_ADVANCED_README.md)。**

### 方式 2：从命令行填充知识库

如果您更喜欢使用命令行或需要自动提取数据。
1. **打开终端**
2. **激活虚拟环境：**
3. **运行脚本**
```bash
.\.venv\Scripts\activate
python bulk_ingest.py --directory "C:\\Path\\To\\Docs"
```

**增强的处理功能**
- **自动格式检测**：系统根据文件类型识别并优化处理
- **智能清理**：自动删除页眉、页脚和不相关内容
- **结构保存**：保持标题、列表和表格井然有序
- **丰富的元数据**：提供每个文档结构的详细信息
- **详细日志**：提供每个文件处理的完整信息

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
            "command": "D:\\your\\absolute\\path\\MCP_RAG\\mcp_server_organized\\run_server_organized.bat",
            "args": [],
            "workingDirectory": "D:\\your\\absolute\\path\\MCP_RAG"
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
        'strategy': 'fast',          # Procesamiento rápido para documentos de Office
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    # ... configuraciones para más de 25 formatos
}
```

#### **智能元素处理：**

```python
def process_unstructured_elements(elements: List[Any]) -> str:
    """Procesa elementos de Unstructured preservando estructura semántica."""
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
