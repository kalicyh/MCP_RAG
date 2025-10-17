"""
MCP 服务器 - 主服务器
=====================================

这是主要的 MCP 服务器，采用模块化架构。
保留了所有现有功能，并进行了更好的组织。
现在支持结构化模型（DocumentModel 和 MetadataModel）。
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlparse

# 添加 src 目录到路径以支持导入
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# 导入工具
from utils.logger import log, log_mcp_server
from utils.config import Config

# 导入 RAG 核心功能（云端实现）
from rag_core_openai import (
    add_text_to_knowledge_base,
    add_text_to_knowledge_base_enhanced,
    load_document_with_fallbacks,
    get_qa_chain,
    get_vector_store,
    search_with_metadata_filters,
    create_metadata_filter,
    get_document_statistics,
    get_cache_stats,
    print_cache_stats,
    clear_embedding_cache,
    optimize_vector_store,
    get_vector_store_stats,
    reindex_vector_store,
    get_optimal_vector_store_profile,
    load_document_with_elements
)

# 导入结构化模型
try:
    from models import DocumentModel, MetadataModel
    MODELS_AVAILABLE = True
    log_mcp_server("✅ 结构化模型 (DocumentModel, MetadataModel) 可用")
except ImportError as e:
    MODELS_AVAILABLE = False
    log_mcp_server(f"⚠️ 结构化模型不可用: {e}")

# --- 初始化服务器和配置 ---
load_dotenv()
mcp = FastMCP(Config.SERVER_NAME)

# 状态现在包括有关结构化模型的信息
rag_state = {
    "models_available": MODELS_AVAILABLE,
    "structured_processing": MODELS_AVAILABLE,
    "document_models": [],  # 已处理的 DocumentModel 列表
    "metadata_cache": {}    # 每个文档的 MetadataModel 缓存
}

md_converter = None

def warm_up_rag_system():
    """
    预加载 RAG 系统的重型组件，以避免首次调用工具时的延迟和冲突。
    """
    if "warmed_up" in rag_state:
        return
    
    log_mcp_server("正在预热 RAG 系统...")
    log_mcp_server("初始化云端向量存储（OpenAI-only）...")
    
    rag_state["warmed_up"] = True
    log_mcp_server("RAG 系统已预热并准备就绪。")

def ensure_converted_docs_directory():
    """确保存在用于存储转换文档的文件夹。"""
    Config.ensure_directories()
    if not os.path.exists(Config.CONVERTED_DOCS_DIR):
        os.makedirs(Config.CONVERTED_DOCS_DIR)
        log_mcp_server(f"已创建转换文档文件夹: {Config.CONVERTED_DOCS_DIR}")

def save_processed_copy(file_path: str, processed_content: str, processing_method: str = "unstructured") -> str:
    """
    保存处理后的文档副本为 Markdown 格式。

    参数：
        file_path: 原始文件路径
        processed_content: 处理后的内容
        processing_method: 使用的处理方法

    返回：
        保存的 Markdown 文件路径
    """
    ensure_converted_docs_directory()
    
    # 获取原始文件名（无扩展名）
    original_filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(original_filename)[0]
    
    # 创建包含方法信息的 Markdown 文件名
    md_filename = f"{name_without_ext}_{processing_method}.md"
    md_filepath = os.path.join(Config.CONVERTED_DOCS_DIR, md_filename)
    
    # 保存内容到 Markdown 文件
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        log_mcp_server(f"已保存处理后的副本: {md_filepath}")
        return md_filepath
    except Exception as e:
        log_mcp_server(f"警告: 无法保存处理后的副本: {e}")
        return ""

def initialize_rag():
    """
    使用核心初始化 RAG 系统的所有组件。
    """
    if "initialized" in rag_state:
        return

    log_mcp_server("通过核心初始化 RAG 系统...")
    
    # 从云端核心获取向量存储和 QA 链
    vector_store = get_vector_store()
    qa_chain = get_qa_chain(vector_store)
    
    rag_state["vector_store"] = vector_store
    rag_state["qa_chain"] = qa_chain
    rag_state["initialized"] = True
    
    # 关于模型状态的信息
    if MODELS_AVAILABLE:
        log_mcp_server("✅ RAG 系统已初始化，支持结构化模型")
        log_mcp_server("🧠 DocumentModel 和 MetadataModel 可用于高级处理")
    else:
        log_mcp_server("⚠️ RAG 系统已初始化，但未启用结构化模型 (使用字典)")
    
    log_mcp_server("RAG 系统初始化成功。")

# --- 初始化自动化 RAG 系统 ---
log_mcp_server("自动初始化 RAG 系统...")
backend = "JSON"
log_mcp_server("RAG 后端: JSON")
initialize_rag()
warm_up_rag_system()
log_mcp_server("RAG 系统已初始化并准备就绪。")

# --- 在初始化 RAG 后配置模块化工具 ---
from tools import configure_rag_state, ALL_TOOLS

# 配置工具模块中的 RAG 状态
configure_rag_state(
    rag_state=rag_state,
    initialize_rag_func=initialize_rag,
    save_processed_copy_func=save_processed_copy
)

# --- Definir las herramientas MCP directamente en el servidor ---
@mcp.tool()
def learn_text(text: str, source_name: str = "manual_input") -> str:
    """
    向 RAG 知识库添加一段新文本以供将来参考。
    使用场景：
    - 添加事实、定义或解释
    - 存储对话中的重要信息
    - 保存研究发现或笔记
    - 添加特定主题的上下文

    参数：
        text: 要学习并存储在知识库中的文本内容。
        source_name: 来源的描述性名称（例如 "user_notes", "research_paper", "conversation_summary"）。
    """
    from tools.document_tools import learn_text as learn_text_logic
    return learn_text_logic(text, source_name)

@mcp.tool()
def learn_document(file_path: str) -> str:
    """
    使用高级非结构化处理技术（包含真正的语义分块）读取和处理文档文件，并将其添加到知识库。
    当您想通过智能处理文档文件来训练人工智能时，可以使用此功能。

    支持的文件类型：PDF、DOCX、PPTX、XLSX、TXT、HTML、CSV、JSON、XML、ODT、ODP、ODS、RTF、
    图像（PNG、JPG、TIFF、带 OCR 的 BMP）、电子邮件（EML、MSG）以及超过 25 种格式。

    高级功能：
    - 基于文档结构（标题、章节、列表）的 REAL 语义分块
    - 智能文档结构保存（标题、列表、表格）
    - 自动去噪（页眉、页脚、无关内容）
    - 结构化元数据提取
    - 适用于任何文档类型的强大回退系统
    - 通过语义边界增强上下文保存

    使用示例：
    - 处理布局复杂的研究论文或文章
    - 从包含表格和列表的报告或手册中添加内容
    - 从带格式的电子表格导入数据
    - 将演示文稿转换为可搜索的知识
    - 使用 OCR 处理扫描文档

    文档将通过 REAL 语义分块进行智能处理，并与增强的元数据一起存储。

    将保存处理后文档的副本以供验证。

    参数：
    file_path：要处理的文档文件的绝对路径或相对路径。
    """
    from tools.document_tools import learn_document as learn_document_logic
    return learn_document_logic(file_path)

@mcp.tool()
def ask_rag(query: str) -> str:
    """
    向 RAG 知识库提问，并根据存储的信息返回答案。
    使用场景：
    - 询问特定主题或概念
    - 请求解释或定义
    - 从处理过的文档中获取信息
    - 基于学习的文本或文档获取答案
    
    参数：
        query: 要向知识库提出的问题或查询。
    """
    from tools.search_tools import ask_rag as ask_rag_logic
    return ask_rag_logic(query)

@mcp.tool()
def ask_rag_filtered(query: str, file_type: str = None, min_tables: int = None, min_titles: int = None, processing_method: str = None) -> str:
    """
    向 RAG 知识库提问，并使用特定过滤器聚焦搜索。
    使用场景：
    - 仅搜索 PDF 文档：file_type=".pdf"
    - 查找包含表格的文档：min_tables=1
    - 查找结构良好的文档：min_titles=5
    - 搜索增强处理的文档：processing_method="unstructured_enhanced"
    
    参数：
        query: 要向知识库提出的问题或查询。
        file_type: 按文件类型过滤（例如 ".pdf", ".docx", ".txt"）。
        min_tables: 文档必须包含的最小表格数量。
        min_titles: 文档必须包含的最小标题数量。
        processing_method: 按处理方法过滤（例如 "unstructured_enhanced", "markitdown"）。
    """
    from tools.search_tools import ask_rag_filtered as ask_rag_filtered_logic
    return ask_rag_filtered_logic(query, file_type, min_tables, min_titles, processing_method)

@mcp.tool()
def get_knowledge_base_stats() -> str:
    """
    获取有关知识库的综合统计信息，包括文档类型、处理方法和结构信息。
    使用场景：
    - 检查知识库中有多少文档
    - 了解文件类型的分布
    - 查看使用了哪些处理方法
    - 分析存储文档的结构复杂性

    返回：
        有关知识库内容的详细统计信息。
    """
    from tools.utility_tools import get_knowledge_base_stats as get_knowledge_base_stats_logic
    return get_knowledge_base_stats_logic()

@mcp.tool()
def get_embedding_cache_stats() -> str:
    """
    获取有关嵌入缓存性能的详细统计信息。
    使用场景：
    - 检查缓存命中率以查看系统是否高效工作
    - 监控缓存的内存使用情况
    - 了解嵌入的重用频率
    - 调试性能问题

    返回：
        有关嵌入缓存性能的详细统计信息。
    """
    from tools.utility_tools import get_embedding_cache_stats as get_embedding_cache_stats_logic
    return get_embedding_cache_stats_logic()

@mcp.tool()
def clear_embedding_cache_tool() -> str:
    """
    清除嵌入缓存以释放内存和磁盘空间。
    使用场景：
    - 在系统内存不足时释放内存
    - 在更改嵌入模型后重置缓存
    - 清除不再需要的旧缓存嵌入
    - 排查与缓存相关的问题

    返回：
        有关缓存清理操作的确认消息。
    """
    from tools.utility_tools import clear_embedding_cache_tool as clear_embedding_cache_tool_logic
    return clear_embedding_cache_tool_logic()

@mcp.tool()
def optimize_vector_database() -> str:
    """
    优化向量数据库以提高搜索性能。
    使用场景：
    - 搜索速度变慢
    - 添加了许多新文档
    - 希望提高系统的整体性能

    返回：
        有关优化过程的信息。
    """
    from tools.utility_tools import optimize_vector_database as optimize_vector_database_logic
    return optimize_vector_database_logic()

@mcp.tool()
def get_vector_database_stats() -> str:
    """
    获取向量数据库的详细统计信息。
    使用场景：
    - 检查数据库状态
    - 分析文档分布
    - 诊断性能问题
    - 规划优化

    返回：
        向量数据库的详细统计信息。
    """
    from tools.utility_tools import get_vector_database_stats as get_vector_database_stats_logic
    return get_vector_database_stats_logic()

@mcp.tool()
def reindex_vector_database(profile: str = 'auto') -> str:
    """
    使用优化配置重新索引向量数据库。
    使用场景：
    - 更改配置文件
    - 搜索速度非常慢
    - 希望针对特定数据库大小进行优化
    - 存在持续的性能问题

    参数：
        profile: 配置文件（'small', 'medium', 'large', 'auto'）。
                 'auto' 会自动检测最佳配置文件

    返回：
        有关重新索引过程的信息。
    """
    from tools.utility_tools import reindex_vector_database as reindex_vector_database_logic
    return reindex_vector_database_logic(profile)

# --- 将所有工具函数暴露为 mcp 的方法，方便直接调用（全局作用域，所有函数定义之后） ---
mcp.learn_text = learn_text
mcp.learn_document = learn_document
mcp.ask_rag = ask_rag
mcp.ask_rag_filtered = ask_rag_filtered
mcp.get_knowledge_base_stats = get_knowledge_base_stats
mcp.get_embedding_cache_stats = get_embedding_cache_stats
mcp.clear_embedding_cache_tool = clear_embedding_cache_tool
mcp.optimize_vector_database = optimize_vector_database
mcp.get_vector_database_stats = get_vector_database_stats
mcp.reindex_vector_database = reindex_vector_database

# --- 启动 MCP RAG 服务器 ---
if __name__ == "__main__":
    log_mcp_server("启动 MCP RAG 服务器...")
    warm_up_rag_system()  # 启动时预热系统
    log_mcp_server("🚀 服务器已启动，运行模式: stdio (如需 Web 服务请设置 host/port)")
    # 将所有工具函数暴露为 mcp 的方法，方便直接调用
    mcp.learn_text = learn_text
    mcp.learn_document = learn_document
    mcp.ask_rag = ask_rag
    mcp.ask_rag_filtered = ask_rag_filtered
    mcp.get_knowledge_base_stats = get_knowledge_base_stats
    mcp.get_embedding_cache_stats = get_embedding_cache_stats
    mcp.clear_embedding_cache_tool = clear_embedding_cache_tool
    mcp.optimize_vector_database = optimize_vector_database
    mcp.get_vector_database_stats = get_vector_database_stats
    mcp.reindex_vector_database = reindex_vector_database
    # 如需 Web 服务可改为: mcp.run(host="127.0.0.1", port=8000)
    mcp.run(transport='stdio')