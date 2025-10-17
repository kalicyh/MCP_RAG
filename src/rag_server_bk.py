import os
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown
from urllib.parse import urlparse

# --- 导入 RAG 核心模块 ---
from rag_core import (
    add_text_to_knowledge_base,           # 将文本添加到知识库的函数
    add_text_to_knowledge_base_enhanced,  # 增强版文本添加函数
    load_document_with_fallbacks,         # 带回退机制的文档加载函数
    get_qa_chain,                         # 获取问答链的函数
    get_vector_store,                     # 获取向量存储的函数
    search_with_metadata_filters,         # 带元数据过滤器的搜索函数
    create_metadata_filter,               # 创建元数据过滤器的函数
    get_document_statistics,              # 获取文档统计信息的函数
    get_cache_stats,                      # 获取缓存统计信息的函数
    print_cache_stats,                    # 打印缓存统计信息的函数
    clear_embedding_cache,                # 清除嵌入缓存的函数
    log,  # 导入日志函数
    optimize_vector_store,
    get_vector_store_stats,
    reindex_vector_store,
    get_optimal_vector_store_profile,
    load_document_with_elements
)

# --- 服务器初始化与配置 ---
load_dotenv()
mcp = FastMCP("ragmcp")

rag_state = {}  # 状态只保存已就绪的组件

md_converter = MarkItDown()  # 初始化 MarkItDown 转换器（用于 URL 处理）

# 用于保存 Markdown 副本的文件夹
CONVERTED_DOCS_DIR = "./converted_docs"

def warm_up_rag_system():
    """
    预加载 RAG 系统的重型组件，避免首次调用工具时的延迟和冲突。
    """
    if "warmed_up" in rag_state:
        return
    
    log("MCP服务器: 正在预热RAG系统...")
    log("MCP服务器: 正在预加载嵌入模型到内存...")
    
    # 此调用强制加载嵌入模型
    get_vector_store()
    
    rag_state["warmed_up"] = True
    log("MCP服务器: RAG系统已预热并准备就绪。")

def ensure_converted_docs_directory():
    """确保存在用于存储转换文档的文件夹。"""
    if not os.path.exists(CONVERTED_DOCS_DIR):
        os.makedirs(CONVERTED_DOCS_DIR)
        log(f"MCP服务器: 已创建转换文档文件夹: {CONVERTED_DOCS_DIR}")

def save_processed_copy(file_path: str, processed_content: str, processing_method: str = "非结构化") -> str:
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
    md_filepath = os.path.join(CONVERTED_DOCS_DIR, md_filename)
    
    # 保存内容到 Markdown 文件
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        log(f"MCP服务器: 已保存处理后的副本: {md_filepath}")
        return md_filepath
    except Exception as e:
        log(f"MCP服务器警告: 无法保存处理后的副本: {e}")
        return ""

def initialize_rag():
    """
    使用核心初始化 RAG 系统的所有组件。
    """
    if "initialized" in rag_state:
        return

    log("MCP服务器: 通过核心初始化RAG系统...")
    
    # 从核心获取向量存储和 QA 链
    vector_store = get_vector_store()
    qa_chain = get_qa_chain(vector_store)
    
    rag_state["vector_store"] = vector_store
    rag_state["qa_chain"] = qa_chain
    rag_state["initialized"] = True
    log("MCP服务器: RAG系统初始化成功。")

# --- 工具实现 ---

@mcp.tool()
def learn_text(text: str, source_name: str = "手动输入") -> str:
    """
    向 RAG 知识库添加一段新文本以供将来参考。
    使用场景：
    - 添加事实、定义或解释
    - 存储对话中的重要信息
    - 保存研究发现或笔记
    - 添加特定主题的上下文

    参数：
        text: 要学习并存储在知识库中的文本内容。
        source_name: 来源的描述性名称（例如 "用户笔记", "研究论文", "对话摘要"）。
    """
    log(f"MCP服务器: 正在处理来自 {source_name} 的文本，共 {len(text)} 字符")
    initialize_rag()
    
    try:
        # 创建源元数据
        source_metadata = {
            "source": source_name,
            "input_type": "手动文本",
            "processed_date": datetime.now().isoformat()
        }
        # 使用核心函数添加文本及元数据
        add_text_to_knowledge_base(text, rag_state["vector_store"], source_metadata)
        log(f"MCP服务器: 文本已成功添加到知识库")
        return f"文本已成功添加到知识库。片段: '{text[:70]}...' (来源: {source_name})"
    except Exception as e:
        log(f"MCP服务器: 添加文本时出错: {e}")
        return f"添加文本时出错: {e}"

@mcp.tool()
def learn_document(file_path: str) -> str:
    """
    读取并处理文档文件，采用高级 Unstructured 处理和真实语义分块，并将其添加到知识库。
    使用场景：
    - 处理复杂布局的论文或文章
    - 添加包含表格和列表的报告或手册内容
    - 导入带格式的电子表格数据
    - 将演示文稿转换为可搜索知识
    - 处理带 OCR 的扫描文档

    支持的文件类型：PDF、DOCX、PPTX、XLSX、TXT、HTML、CSV、JSON、XML、ODT、ODP、ODS、RTF、
    图像（PNG、JPG、TIFF、BMP，带 OCR）、邮件（EML、MSG）等 25+ 种格式。

    高级功能：
    - 基于文档结构（标题、章节、列表）的真实语义分块
    - 智能文档结构保存（标题、列表、表格）
    - 自动去噪（页眉、页脚、无关内容）
    - 结构化元数据提取
    - 强大回退系统，适用于任何文档类型
    - 通过语义边界增强上下文保存

    文档将通过真实语义分块智能处理，并与增强元数据一起存储。
    处理后的副本将保存以供验证。

    参数：
        file_path：要处理的文档文件的绝对路径或相对路径。
    """
    log(f"MCP服务器: 开始高级文档处理: {file_path}")
    log(f"MCP服务器: 调试 - 接收到路径: {repr(file_path)}")
    log(f"MCP服务器: 调试 - 检查绝对路径是否存在: {os.path.abspath(file_path)}")
    initialize_rag()  # 确保 RAG 系统已就绪
    
    try:
        if not os.path.exists(file_path):
            log(f"MCP服务器: 未找到文件路径: {file_path}")
            return f"错误: 未找到文件 '{file_path}'"

        log(f"MCP服务器: 正在用高级Unstructured系统处理文档...")

        # 使用新系统处理结构化元素
        processed_content, metadata, structural_elements = load_document_with_elements(file_path)

        if not processed_content or processed_content.isspace():
            log(f"MCP服务器: 警告: 文档已处理但未能提取内容: {file_path}")
            return f"警告: 文档 '{file_path}' 已处理，但未能提取文本内容。"

        log(f"MCP服务器: 文档处理成功（{len(processed_content)} 字符）")

        # 保存处理副本
        log(f"MCP服务器: 正在保存处理副本...")
        processing_method = metadata.get("processing_method", "未知")
        saved_copy_path = save_processed_copy(file_path, processed_content, processing_method)

        # 添加内容到知识库，使用真实语义分块
        log(f"MCP服务器: 正在添加内容到知识库（含结构化元数据）...")

        # 使用结构化元素进行真实语义分块
        add_text_to_knowledge_base_enhanced(
            processed_content,
            rag_state["vector_store"],
            metadata,
            use_semantic_chunking=True,
            structural_elements=structural_elements
        )

        log(f"MCP服务器: 处理完成 - 文档已成功处理")

        # 构建详细响应
        file_name = os.path.basename(file_path)
        file_type = metadata.get("file_type", "未知")
        processing_method = metadata.get("processing_method", "未知")

        # 分块信息
        chunking_info = ""
        if structural_elements and len(structural_elements) > 1:
            chunking_info = f"🧠 高级语义分块，共 {len(structural_elements)} 个结构化元素"
        elif metadata.get("structural_info", {}).get("total_elements", 0) > 1:
            chunking_info = f"📊 增强语义分块，基于结构化元数据"
        else:
            chunking_info = f"📝 传统分块 优化"

        return f"""✅ 文档处理成功
📄 文件: {file_name}
📋 类型: {file_type.upper()}
🔧 处理方法: {processing_method}
{chunking_info}
📊 处理字符数: {len(processed_content):,}
💾 副本保存路径: {saved_copy_path if saved_copy_path else "无"}"""

    except Exception as e:
        log(f"MCP服务器: 处理文档 '{file_path}' 时出错: {e}")
        return f"处理文档时出错: {e}"


@mcp.tool()
def ask_rag(query: str) -> str:
    """
    向 RAG 知识库提问，并根据存储的信息返回答案。
    使用场景：
    - 询问特定主题或概念
    - 请求解释或定义
    - 从处理过的文档获取信息
    - 基于已学习的文本或文档获取答案

    系统将搜索所有存储的知识，并返回最相关的结果。

    参数：
        query: 要向知识库提出的问题或查询。
    """
    log(f"MCP服务器: 正在处理问题: {query}")
    initialize_rag()
    
    try:
        # 使用标准QA链（无过滤器）
        qa_chain = get_qa_chain(rag_state["vector_store"])
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])
        
        # 检查是否真的有相关信息
        if not source_documents:
            # 无可用来源，可能系统尚未加载相关信息
            enhanced_answer = f"🤖 回答:\n\n❌ 未找到与问题相关的信息，无法回答。\n\n"
            enhanced_answer += "💡 建议:\n"
            enhanced_answer += "• 确保已加载与问题相关的文档\n"
            enhanced_answer += "• 尝试使用更具体的关键词重新提问\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 检查知识库状态\n"
            enhanced_answer += "• 考虑加载更多相关文档\n\n"
            enhanced_answer += "⚠️ 提示: 系统仅基于已加载信息进行回答。"
            
            log(f"MCP服务器: 未找到相关信息来源")
            return enhanced_answer
        
        # 检查回答是否可能是幻觉
        # 如果没有来源但有回答，可能是幻觉结果
        if len(source_documents) == 0 and answer.strip():
            # 有回答但无来源，可能为幻觉结果
            enhanced_answer = f"🤖 回答:\n\n❌ 未找到特定信息，无法准确回答。\n\n"
            enhanced_answer += "💡 建议:\n"
            enhanced_answer += "• 确保已加载与问题相关的文档\n"
            enhanced_answer += "• 尝试使用更具体的关键词重新提问\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 检查知识库状态\n\n"
            enhanced_answer += "⚠️ 提示: 系统仅基于已加载信息进行回答。"
            
            log(f"MCP服务器: 检测到可能的幻觉回答（无来源）")
            return enhanced_answer
        
        # 如果有可用来源，构建正常回答
        enhanced_answer = f"🤖 回答:\n\n{answer}\n"
        
        # 添加来源信息及更多详情
        if source_documents:
            enhanced_answer += "📚 使用的信息来源:\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "未知来源")
                
                # --- 改进来源信息 ---
                source_info = f"   {i}. {source_name}"
                
                # 如果是文档则添加完整路径
                file_path = metadata.get("file_path")
                if file_path:
                    source_info += f"\n      - 路径: `{file_path}`"
                
                # 如果有文件类型则添加
                file_type = metadata.get("file_type")
                if file_type:
                    source_info += f"\n      - 类型: {file_type.upper()}"
                
                # 如果有处理方法则添加
                processing_method = metadata.get("processing_method")
                if processing_method:
                    method_display = processing_method.replace('_', ' ').title()
                    source_info += f"\n      - 处理方法: {method_display}"
                
                # 如果有结构信息则添加
                structural_info = metadata.get("structural_info")
                if structural_info:
                    source_info += f"\n      - 结构: {structural_info.get('total_elements', 'N/A')} 个元素"
                    titles_count = structural_info.get('titles_count', 0)
                    tables_count = structural_info.get('tables_count', 0)
                    lists_count = structural_info.get('lists_count', 0)
                    if titles_count > 0 or tables_count > 0 or lists_count > 0:
                        structure_details = []
                        if titles_count > 0:
                            structure_details.append(f"{titles_count} 个标题")
                        if tables_count > 0:
                            structure_details.append(f"{tables_count} 个表格")
                        if lists_count > 0:
                            structure_details.append(f"{lists_count} 个列表")
                        source_info += f" ({', '.join(structure_details)})"
                
                # 从扁平元数据重构结构信息
                structural_elements = []
                titles_count = metadata.get("structural_titles_count", 0)
                tables_count = metadata.get("structural_tables_count", 0)
                lists_count = metadata.get("structural_lists_count", 0)
                total_elements = metadata.get("structural_total_elements", 0)
                
                if total_elements > 0:
                    structural_details = []
                    if titles_count > 0:
                        structural_details.append(f"{titles_count} 个标题")
                    if tables_count > 0:
                        structural_details.append(f"{tables_count} 个表格")
                    if lists_count > 0:
                        structural_details.append(f"{lists_count} 个列表")
                    
                    if structural_details:
                        source_info += f"\n      - 结构: {', '.join(structural_details)}"
                
                enhanced_answer += source_info + "\n\n"
        
        # 添加回答质量信息
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ 高可信度: 回答基于多个来源"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ 中等可信度: 回答基于2个来源"
        else:
            enhanced_answer += "\n⚠️ 有限可信度: 回答基于1个来源"
        
        # 如果有文档使用了结构化元数据处理则添加信息
        enhanced_docs = [doc for doc in source_documents if hasattr(doc, 'metadata') and doc.metadata.get("processing_method") == "unstructured_enhanced"]
        if enhanced_docs:
            enhanced_answer += f"\n🧠 智能处理: {len(enhanced_docs)} 个来源使用了Unstructured处理（保留结构）"
        
        log(f"MCP服务器: 成功生成回答，共{len(source_documents)}个来源")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP服务器: 处理问题时出错: {e}")
        return f"❌ 处理问题时出错: {e}\n\n💡 建议:\n- 检查RAG系统是否正确初始化\n- 尝试重新表述您的问题\n- 如果问题持续，请重启服务器"

@mcp.tool()
def ask_rag_filtered(query: str, file_type: str = None, min_tables: int = None, min_titles: int = None, processing_method: str = None) -> str:
    """
    向 RAG 知识库提出问题，使用特定过滤器聚焦搜索范围。
    适用于从特定类型的文档或具有特定特征的文档中获取信息。
    
    使用示例：
    - 仅在PDF文档中搜索: file_type=".pdf"
    - 查找包含表格的文档: min_tables=1
    - 查找结构良好的文档: min_titles=5
    - 在增强处理的文档中搜索: processing_method="unstructured_enhanced"
    
    通过过滤搜索范围提供更精准和相关的结果。

    参数：
        query: 向知识库提出的问题或查询。
        file_type: 按文件类型过滤（例如 ".pdf", ".docx", ".txt"）
        min_tables: 文档必须包含的最少表格数量
        min_titles: 文档必须包含的最少标题数量
        processing_method: 按处理方法过滤（例如 "unstructured_enhanced", "markitdown"）
    """
    log(f"MCP服务器: 正在处理带过滤器的问题: {query}")
    log(f"MCP服务器: 应用的过滤器 - 类型: {file_type}, 表格: {min_tables}, 标题: {min_titles}, 方法: {processing_method}")
    initialize_rag()
    
    try:
        # 创建元数据过滤器
        metadata_filter = create_metadata_filter(
            file_type=file_type,
            processing_method=processing_method,
            min_tables=min_tables,
            min_titles=min_titles
        )
        
        # 使用带过滤器的QA链
        qa_chain = get_qa_chain(rag_state["vector_store"], metadata_filter)
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])
        
        # 检查是否有符合过滤器的相关信息
        if not source_documents:
            # 没有符合过滤器的来源
            enhanced_answer = f"🔍 回答（已应用过滤器）:\n\n❌ 在知识库中未找到符合指定过滤器的相关信息。\n\n"
            
            # 显示应用的过滤器
            if metadata_filter:
                enhanced_answer += "📋 应用的过滤器:\n"
                for key, value in metadata_filter.items():
                    if key == "file_type":
                        enhanced_answer += f"   • 文件类型: {value}\n"
                    elif key == "processing_method":
                        enhanced_answer += f"   • 处理方法: {value.replace('_', ' ').title()}\n"
                    elif key == "structural_tables_count":
                        enhanced_answer += f"   • 最少表格数: {value['$gte']}\n"
                    elif key == "structural_titles_count":
                        enhanced_answer += f"   • 最少标题数: {value['$gte']}\n"
                enhanced_answer += "\n"
            
            enhanced_answer += "💡 建议:\n"
            enhanced_answer += "• 尝试放宽过滤器以获得更多结果\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 查看可用的文档类型\n"
            enhanced_answer += "• 考虑使用 `ask_rag()` 不带过滤器搜索整个知识库\n"
            enhanced_answer += "• 确认已加载符合指定条件的文档\n\n"
            enhanced_answer += "⚠️ 注意: 过滤器可能过于严格。尝试使用更宽松的过滤器。"
            
            log(f"MCP服务器: 未找到符合指定过滤器的来源")
            return enhanced_answer
        
        # 验证响应是否可能是幻觉
        if len(source_documents) == 0 and answer.strip():
            enhanced_answer = f"🔍 响应（已应用过滤器）:\n\n❌ 未找到符合指定过滤器的特定信息。\n\n"
            
            # 显示应用的过滤器
            if metadata_filter:
                enhanced_answer += "📋 应用的过滤器:\n"
                for key, value in metadata_filter.items():
                    if key == "file_type":
                        enhanced_answer += f"   • 文件类型: {value}\n"
                    elif key == "processing_method":
                        enhanced_answer += f"   • 处理方法: {value.replace('_', ' ').title()}\n"
                    elif key == "structural_tables_count":
                        enhanced_answer += f"   • Mínimo de tablas: {value['$gte']}\n"
                    elif key == "structural_titles_count":
                        enhanced_answer += f"   • Mínimo de títulos: {value['$gte']}\n"
                enhanced_answer += "\n💡 建议:\n"
            enhanced_answer += "• 尝试放宽过滤器以获得更多结果\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 查看可用的文档类型\n"
            enhanced_answer += "• 考虑使用不带过滤器的 `ask_rag()` 搜索整个知识库\n\n"
            enhanced_answer += "⚠️ 注意: 过滤器可能过于严格，请尝试使用更宽泛的过滤器。"
            
            log(f"MCP服务器: 过滤响应检测到可能的幻觉（无来源）")
            return enhanced_answer
        
        # 如果有来源，构建正常回答
        enhanced_answer = f"🔍 回答（已应用过滤器）:\n\n{answer}\n"
        
        # 显示应用的过滤器
        if metadata_filter:
            enhanced_answer += "\n📋 应用的过滤器:\n"
            for key, value in metadata_filter.items():
                if key == "file_type":
                    enhanced_answer += f"   • 文件类型: {value}\n"
                elif key == "processing_method":
                    enhanced_answer += f"   • 处理方法: {value.replace('_', ' ').title()}\n"
                elif key == "structural_tables_count":
                    enhanced_answer += f"   • Mínimo de tablas: {value['$gte']}\n"
                elif key == "structural_titles_count":
                    enhanced_answer += f"   • Mínimo de títulos: {value['$gte']}\n"
        
        # 添加来源信息
        if source_documents:
            enhanced_answer += f"\n📚 找到的来源 ({len(source_documents)}):\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "Fuente desconocida")
                
                source_info = f"   {i}. {source_name}"
                
                # Información estructural
                tables_count = metadata.get("structural_tables_count", 0)
                titles_count = metadata.get("structural_titles_count", 0)
                file_type = metadata.get("file_type", "")
                
                structural_details = []
                if tables_count > 0:
                    structural_details.append(f"{tables_count} tablas")
                if titles_count > 0:
                    structural_details.append(f"{titles_count} títulos")
                
                if structural_details:
                    source_info += f" ({', '.join(structural_details)})"
                
                if file_type:
                    source_info += f" [{file_type.upper()}]"
                
                enhanced_answer += source_info + "\n"
        
        # 过滤搜索信息
        enhanced_answer += f"\n🎯 过滤搜索: 结果仅限于符合指定条件的文档。"
        
        log(f"MCP服务器: 成功生成过滤回答，共{len(source_documents)}个来源")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP服务器: 处理过滤问题时出错: {e}")
        return f"❌ 处理过滤问题时出错: {e}"

@mcp.tool()
def get_knowledge_base_stats() -> str:
    """
    获取知识库的综合统计信息，包括文档类型、处理方法和结构信息。
    用于了解知识库中有哪些信息以及如何处理的。
    
    使用示例：
    - 检查知识库中有多少文档
    - 了解文件类型的分布
    - 查看使用了哪些处理方法
    - 分析存储文档的结构复杂性
    
    这有助于您就搜索内容和如何过滤查询做出明智的决定。

    返回：
        关于知识库内容的详细统计信息。
    """
    log(f"MCP服务器: 正在获取知识库统计信息...")
    initialize_rag()
    
    try:
        stats = get_document_statistics(rag_state["vector_store"])
        
        if "error" in stats:
            return f"❌ 获取统计信息时出错: {stats['error']}"
        
        if stats.get("total_documents", 0) == 0:
            return "📊 知识库为空\n\n知识库中没有存储的文档。"
        
        # 构建详细回答
        response = f"📊 知识库统计信息\n\n"
        response += f"📚 文档总数: {stats['total_documents']}\n\n"
        
        # 文件类型
        if stats["file_types"]:
            response += "📄 文件类型:\n"
            for file_type, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total_documents"]) * 100
                response += f"   • {file_type.upper()}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # 处理方法
        if stats["processing_methods"]:
            response += "🔧 处理方法:\n"
            for method, count in sorted(stats["processing_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total_documents"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # 结构统计
        structural = stats["structural_stats"]
        response += "🏗️ 结构信息:\n"
        response += f"   • 包含表格的文档: {structural['documents_with_tables']}\n"
        response += f"   • 包含标题的文档: {structural['documents_with_titles']}\n"
        response += f"   • 包含列表的文档: {structural['documents_with_lists']}\n"
        response += f"   • 每文档平均表格数: {structural['avg_tables_per_doc']:.1f}\n"
        response += f"   • 每文档平均标题数: {structural['avg_titles_per_doc']:.1f}\n"
        response += f"   • 每文档平均列表数: {structural['avg_lists_per_doc']:.1f}\n\n"
        
        # 搜索建议
        response += "💡 搜索建议:\n"
        if structural['documents_with_tables'] > 0:
            response += f"   • 使用 `ask_rag_filtered` 带 `min_tables=1` 搜索包含表格的文档信息\n"
        if structural['documents_with_titles'] > 5:
            response += f"   • 使用 `ask_rag_filtered` 带 `min_titles=5` 搜索结构良好的文档\n"
        if ".pdf" in stats["file_types"]:
            response += f"   • 使用 `ask_rag_filtered` 带 `file_type=\".pdf\"` 仅搜索PDF文档\n"
        
        log(f"MCP服务器: 成功获取统计信息")
        return response
        
    except Exception as e:
        log(f"MCP服务器: 获取统计信息时出错: {e}")
        return f"❌ 获取统计信息时出错: {e}"

@mcp.tool()
def get_embedding_cache_stats() -> str:
    """
    获取嵌入缓存性能的详细统计信息。
    用于监控缓存效率并了解系统性能。
    
    使用示例：
    - 检查缓存命中率以查看系统是否高效运行
    - 监控缓存的内存使用情况
    - 了解嵌入重复使用的频率
    - 调试性能问题
    
    这有助于您优化系统并了解其行为。

    返回：
        关于嵌入缓存性能的详细统计信息。
    """
    log(f"MCP服务器: 正在获取嵌入缓存统计信息...")
    
    try:
        stats = get_cache_stats()
        
        if not stats:
            return "📊 嵌入缓存不可用\n嵌入缓存未初始化。"
        
        # 构建详细回答
        response = f"📊 嵌入缓存统计信息\n\n"
        
        # 主要指标
        response += f"🔄 缓存活动:\n"
        response += f"   • 总请求数: {stats['total_requests']}\n"
        response += f"   • 内存命中次数: {stats['memory_hits']}\n"
        response += f"   • 磁盘命中次数: {stats['disk_hits']}\n"
        response += f"   • 未命中次数: {stats['misses']}\n\n"
        
        # 成功率
        response += f"📈 成功率:\n"
        response += f"   • 内存命中率: {stats['memory_hit_rate']}\n"
        response += f"   • 磁盘命中率: {stats['disk_hit_rate']}\n"
        response += f"   • 总命中率: {stats['overall_hit_rate']}\n\n"
        
        # 内存使用
        response += f"💾 内存使用:\n"
        response += f"   • 内存中的嵌入: {stats['memory_cache_size']}\n"
        response += f"   • 最大内存大小: {stats['max_memory_size']}\n"
        response += f"   • 缓存目录: {stats['cache_directory']}\n\n"
        
        # 性能分析
        total_requests = stats['total_requests']
        if total_requests > 0:
            memory_hit_rate = float(stats['memory_hit_rate'].rstrip('%'))
            overall_hit_rate = float(stats['overall_hit_rate'].rstrip('%'))
            
            response += f"🎯 性能分析:\n"
            
            if overall_hit_rate > 70:
                response += f"   • ✅ 性能卓越: {overall_hit_rate:.1f}% 命中率\n"
            elif overall_hit_rate > 50:
                response += f"   • ⚠️ 性能中等: {overall_hit_rate:.1f}% 命中率\n"
            else:
                response += f"   • ❌ 性能较低: {overall_hit_rate:.1f}% 命中率\n"
            
            if memory_hit_rate > 50:
                response += f"   • 🚀 内存缓存高效: {memory_hit_rate:.1f}% 内存命中率\n"
            else:
                response += f"   • 💾 依赖磁盘存储: {memory_hit_rate:.1f}% 内存命中率\n"
            
            # 优化建议
            response += f"\n💡 优化建议:\n"
            if overall_hit_rate < 30:
                response += f"   • 考虑同时处理相似的文档\n"
                response += f"   • 检查是否有很多不重复的独特文本\n"
            
            if memory_hit_rate < 30 and total_requests > 100:
                response += f"   • 考虑增加内存缓存大小\n"
                response += f"   • 磁盘命中比内存命中速度慢\n"
            
            if stats['memory_cache_size'] >= stats['max_memory_size'] * 0.9:
                response += f"   • 内存缓存接近满载\n"
                response += f"   • 如有可用RAM，考虑增加max_memory_size\n"
        
        log(f"MCP服务器: 成功获取缓存统计信息")
        return response
        
    except Exception as e:
        log(f"MCP服务器: 获取缓存统计信息时出错: {e}")
        return f"❌ 获取缓存统计信息时出错: {e}"

@mcp.tool()
def clear_embedding_cache_tool() -> str:
    """
    清除嵌入缓存以释放内存和磁盘空间。
    当您想重置缓存或释放资源时使用此功能。
    
    使用示例：
    - 系统内存不足时释放内存
    - 更改嵌入模型后重置缓存
    - 清除不再需要的旧缓存嵌入
    - 故障排除缓存相关问题
    
    警告: 这将删除所有缓存的嵌入，需要重新计算。

    返回：
        关于缓存清除操作的确认消息。
    """
    log(f"MCP服务器: 正在清除嵌入缓存...")
    
    try:
        clear_embedding_cache()
        
        response = "🧹 嵌入缓存清除成功\n\n"
        response += "✅ 已删除所有缓存中存储的嵌入。\n"
        response += "📝 下次需要时将从头计算嵌入。\n"
        response += "💾 已释放内存和磁盘空间。\n\n"
        response += "⚠️ 注意: 需要时嵌入将自动重新计算。"
        
        log(f"MCP服务器: 嵌入缓存清除成功")
        return response
        
    except Exception as e:
        log(f"MCP服务器: 清除缓存时出错: {e}")
        return f"❌ 清除缓存时出错: {e}"

@mcp.tool()
def optimize_vector_database() -> str:
    """
    优化向量数据库以提高搜索性能。
    此工具重新组织内部索引以实现更快的搜索。
    
    使用此工具当：
    - 搜索速度缓慢
    - 添加了许多新文档
    - 想要提高系统整体性能
    
    返回：
        关于优化过程的信息
    """
    log("MCP服务器: 正在优化向量数据库...")
    
    try:
        result = optimize_vector_store()

        if result.get("status") == "success":
            response = f"✅ 向量数据库优化成功\n\n"
            response += f"📊 优化前统计:\n"
            stats_before = result.get("stats_before", {})
            response += f"   • 文档总数: {stats_before.get('total_documents', 'N/A')}\n"

            response += f"\n📊 优化后统计:\n"
            stats_after = result.get("stats_after", {})
            response += f"   • 文档总数: {stats_after.get('total_documents', 'N/A')}\n"

            response += f"\n🚀 优势:\n"
            response += f"   • 搜索速度更快\n"
            response += f"   • 结果精度更高\n"
            response += f"   • 索引已优化\n"
        else:
            msg = result.get('message', '未知错误')
            response = f"❌ 优化数据库时出错: {msg}"

        return response
        
    except Exception as e:
        log(f"MCP服务器错误: 优化出错: {e}")
        return f"❌ 优化向量数据库时出错: {str(e)}"

@mcp.tool()
def get_vector_database_stats() -> str:
    """
    获取向量数据库的详细统计信息。
    包括文档、文件类型和配置信息。
    
    使用此工具来：
    - 检查数据库状态
    - 分析文档分布
    - 诊断性能问题
    - 规划优化
    
    返回：
        向量数据库的详细统计信息
    """
    log("MCP服务器: 正在获取向量数据库统计信息...")
    
    try:
        stats = get_vector_store_stats()
        
        if "error" in stats:
            return f"❌ 获取统计信息时出错: {stats['error']}"
        
        response = f"📊 向量数据库统计信息\n\n"
        
        response += f"📚 基本信息:\n"
        response += f"   • 文档总数: {stats.get('total_documents', 0)}\n"
        response += f"   • 集合名称: {stats.get('collection_name', 'N/A')}\n"
        response += f"   • 嵌入维度: {stats.get('embedding_dimension', 'N/A')}\n"
        
        # 文件类型
        file_types = stats.get('file_types', {})
        if file_types:
            response += f"\n📄 按文件类型分布:\n"
            for file_type, count in file_types.items():
                response += f"   • {file_type}: {count} 个文档\n"
        
        # 处理方法
        processing_methods = stats.get('processing_methods', {})
        if processing_methods:
            response += f"\n🔧 处理方法:\n"
            for method, count in processing_methods.items():
                response += f"   • {method}: {count} 个文档\n"
        
        # 推荐配置文件
        try:
            recommended_profile = get_optimal_vector_store_profile()
            response += f"\n🎯 推荐配置: {recommended_profile}\n"
        except:
            pass
        
        return response
        
    except Exception as e:
        log(f"MCP服务器错误: 获取统计信息出错: {e}")
        return f"❌ 获取数据库统计信息时出错: {str(e)}"

@mcp.tool()
def reindex_vector_database(profile: str = 'auto') -> str:
    """
    使用优化配置重新索引向量数据库。
    此工具用当前大小的优化参数重新创建索引。
    
    参数:
        profile: 配置文件 ('small', 'medium', 'large', 'auto')
                 'auto' 自动检测最佳配置
    
    使用此工具当：
    - 更改配置文件
    - 搜索非常缓慢
    - 想要为特定数据库大小优化
    - 存在持续的性能问题
    
    ⚠️ 注意: 此过程可能需要时间，取决于数据库大小。
    
    返回：
        关于重新索引过程的信息
    """
    log(f"MCP服务器: 正在使用配置'{profile}'重新索引向量数据库...")
    
    try:
        result = reindex_vector_store(profile=profile)
        
        if result["status"] == "success":
            response = f"✅ 向量数据库重新索引成功\n\n"
            response += f"📊 处理信息:\n"
            response += f"   • 应用的配置: {profile}\n"
            response += f"   • 处理的文档: {result.get('documents_processed', 0)}\n"
            
            response += f"\n🚀 重新索引的好处:\n"
            response += f"   • 针对当前大小优化的索引\n"
            response += f"   • 更快更精确的搜索\n"
            response += f"   • 更好的内存使用\n"
            
        elif result["status"] == "warning":
            response = f"⚠️ 警告: {result.get('message', '没有文档需要重新索引')}"
            
        else:
            response = f"❌ 重新索引数据库时出错: {result.get('message', '未知错误')}"
            
        return response
        
    except Exception as e:
        log(f"MCP服务器错误: 重新索引出错: {e}")
        return f"❌ 重新索引向量数据库时出错: {str(e)}"

# --- 运行服务器的入口点 ---
if __name__ == "__main__":
    log("正在启动MCP RAG服务器...")
    warm_up_rag_system()  # 启动时预热系统
    mcp.run(transport='stdio') 