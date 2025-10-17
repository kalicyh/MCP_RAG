"""
MCP 搜索工具
===========

此模块包含与知识库搜索和查询相关的工具。
从 rag_server.py 迁移而来，用于模块化架构。

注意：这些函数被设计为在主服务器中使用 @mcp.tool() 装饰器。
"""

from rag_core_openai import (
    get_qa_chain,
    create_metadata_filter
)
from utils.logger import log

# 导入结构化模型
try:
    from models import MetadataModel
except ImportError as e:
    log(f"警告：无法导入结构化模型：{e}")
    MetadataModel = None

# 必须在服务器中可用的全局变量
rag_state = {}
initialize_rag_func = None

def set_rag_state(state):
    """设置全局 RAG 状态。"""
    global rag_state
    rag_state = state

def set_initialize_rag_func(func):
    """设置 RAG 初始化函数。"""
    global initialize_rag_func
    initialize_rag_func = func

def initialize_rag():
    """初始化 RAG 系统。"""
    if initialize_rag_func:
        initialize_rag_func()
    elif "initialized" in rag_state:
        return
    # 此函数必须在主服务器中实现
    pass

def process_document_metadata(metadata: dict) -> dict:
    """
    使用 MetadataModel（如果可用）处理文档元数据。
    
    参数：
        metadata: 文档元数据字典
        
    返回：
        包含已处理文档信息的字典
    """
    if not metadata:
        return {"source": "未知来源"}
    
    # 如果 MetadataModel 可用，尝试创建结构化模型
    if MetadataModel is not None:
        try:
            metadata_model = MetadataModel.from_dict(metadata)
            return {
                "source": metadata_model.source,
                "file_path": metadata_model.file_path,
                "file_type": metadata_model.file_type,
                "processing_method": metadata_model.processing_method,
                "structural_info": metadata_model.structural_info,
                "titles_count": metadata_model.titles_count,
                "tables_count": metadata_model.tables_count,
                "lists_count": metadata_model.lists_count,
                "total_elements": metadata_model.total_elements,
                "is_rich_content": metadata_model.is_rich_content(),
                "chunking_method": metadata_model.chunking_method,
                "avg_chunk_size": metadata_model.avg_chunk_size
            }
        except Exception as e:
            log(f"MCP服务器警告：使用 MetadataModel 处理元数据时出错：{e}")
    
    # 回退到直接字典处理
    return {
        "source": metadata.get("source", "未知来源"),
        "file_path": metadata.get("file_path"),
        "file_type": metadata.get("file_type"),
        "processing_method": metadata.get("processing_method"),
        "structural_info": metadata.get("structural_info", {}),
        "titles_count": metadata.get("structural_titles_count", 0),
        "tables_count": metadata.get("structural_tables_count", 0),
        "lists_count": metadata.get("structural_lists_count", 0),
        "total_elements": metadata.get("structural_total_elements", 0),
        "is_rich_content": False,  # 没有模型无法确定
        "chunking_method": metadata.get("chunking_method", "未知"),
        "avg_chunk_size": metadata.get("avg_chunk_size", 0)
    }


def extract_brief_answer(full_text: str) -> str:
    """
    从增强回答文本中提取简洁回答（去掉前缀、来源和建议部分）。
    返回去掉杂项后的纯文本（如果无法提取则返回原文的简短形式或空字符串）。
    """
    if not full_text:
        return ""

    text = full_text.strip()

    # 常见前缀
    prefixes = ["🤖 回答：", "🔍 回答（已应用过滤器）：", "🔍 回答：", "回答："]
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].lstrip('\n ').lstrip()
            break

    # 截断到第一个来源或建议标记
    for marker in ["📚 使用的信息来源：", "📋 应用的过滤器：", "💡 建议：", "⚠️ 注意："]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].rstrip()
            break

    return text.strip()

def ask_rag(query: str) -> str:
    """
    向 RAG 知识库提问并基于存储的信息返回答案。
    当您想从之前学习的知识库中获取信息时使用此功能。
    
    使用场景示例：
    - 询问特定主题或概念
    - 请求解释或定义
    - 从处理过的文档中寻求信息
    - 基于学习的文本或文档获取答案
    
    系统将搜索所有存储的信息并提供最相关的答案。

    参数：
        query: 向知识库提出的问题或查询。
    """
    log(f"MCP服务器：正在处理问题：{query}")
    initialize_rag()
    
    try:
        # 使用标准 QA 链（无过滤器）
        qa_chain = get_qa_chain(rag_state["vector_store"])
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])

        # 优先返回简洁的回答文本（去掉来源与建议）
        concise = extract_brief_answer(response.get("result", ""))
        if concise:
            log(f"MCP服务器：成功生成简洁回答，使用了 {len(source_documents)} 个来源")
            return concise
        
        # 验证是否真的有相关信息
        if not source_documents:
            # 没有来源 - LLM 可能在产生幻觉
            enhanced_answer = f"🤖 回答：\n\n❌ 在知识库中未找到相关信息来回答您的问题。\n\n"
            enhanced_answer += "💡 建议：\n"
            enhanced_answer += "• 验证您是否已加载与问题相关的文档\n"
            enhanced_answer += "• 尝试用更具体的术语重新表述您的问题\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 查看可用信息\n"
            enhanced_answer += "• 考虑加载更多关于您感兴趣主题的文档\n\n"
            enhanced_answer += "⚠️ 注意： 系统只能基于之前加载到知识库中的信息进行回答。"
            
            log(f"MCP服务器：未找到相关来源回答问题")
            return enhanced_answer
        
        # 验证回答是否可能是幻觉
        # 如果没有来源但有回答，可能是幻觉
        if len(source_documents) == 0 and answer.strip():
            enhanced_answer = f"🤖 回答：\n\n❌ 在知识库中未找到特定信息来回答您的问题。\n\n"
            enhanced_answer += "💡 建议：\n"
            enhanced_answer += "• 验证您是否已加载与问题相关的文档\n"
            enhanced_answer += "• 尝试用更具体的术语重新表述您的问题\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 查看可用信息\n\n"
            enhanced_answer += "⚠️ 注意： 系统只能基于之前加载到知识库中的信息进行回答。"
            
            log(f"MCP服务器：检测到可能的幻觉回答（无来源）")
            return enhanced_answer
        
        # 如果有来源，构建正常回答
        enhanced_answer = f"🤖 回答：\n\n{answer}\n"
        
        # 使用结构化模型添加更详细的来源信息
        if source_documents:
            enhanced_answer += "📚 使用的信息来源：\n\n"
            for i, doc in enumerate(source_documents, 1):
                raw_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                
                # 使用结构化模型处理元数据
                doc_info = process_document_metadata(raw_metadata)
                
                # --- 改进来源信息 ---
                source_info = f"   {i}. {doc_info['source']}"
                
                # 如果是文档，添加完整路径
                if doc_info['file_path']:
                    source_info += f"\n      - 路径： `{doc_info['file_path']}`"
                
                # 如果可用，添加文件类型
                if doc_info['file_type']:
                    source_info += f"\n      - 类型： {(doc_info.get('file_type') or 'unknown').upper()}"
                
                # 如果可用，添加处理方法
                if doc_info['processing_method']:
                    method_display = doc_info['processing_method'].replace('_', ' ').title()
                    source_info += f"\n      - 处理： {method_display}"
                
                # 使用模型数据添加结构信息
                if doc_info['total_elements'] > 0:
                    source_info += f"\n      - 结构： {doc_info['total_elements']} 个元素"
                    
                    structural_details = []
                    if doc_info['titles_count'] > 0:
                        structural_details.append(f"{doc_info['titles_count']} 个标题")
                    if doc_info['tables_count'] > 0:
                        structural_details.append(f"{doc_info['tables_count']} 个表格")
                    if doc_info['lists_count'] > 0:
                        structural_details.append(f"{doc_info['lists_count']} 个列表")
                    
                    if structural_details:
                        source_info += f" ({', '.join(structural_details)})"
                
                # 如果可用，添加分块信息
                if doc_info['chunking_method'] and doc_info['chunking_method'] != "未知":
                    chunking_display = doc_info['chunking_method'].replace('_', ' ').title()
                    source_info += f"\n      - 分块： {chunking_display}"
                
                # 如果可用，添加丰富内容指示器
                if doc_info.get('is_rich_content', False):
                    source_info += f"\n      - 质量： 结构丰富的内容"
                
                enhanced_answer += source_info + "\n\n"
        
        # 添加回答质量信息
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ 高可信度： 基于多个来源的回答"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ 中等可信度： 基于 2 个来源的回答"
        else:
            enhanced_answer += "\n⚠️ 有限可信度： 基于 1 个来源的回答"
        
        # 使用结构化模型添加处理信息
        enhanced_docs = []
        rich_content_docs = []
        
        for doc in source_documents:
            if hasattr(doc, 'metadata') and doc.metadata:
                doc_info = process_document_metadata(doc.metadata)
                if doc_info['processing_method'] == "unstructured_enhanced":
                    enhanced_docs.append(doc)
                if doc_info.get('is_rich_content', False):
                    rich_content_docs.append(doc)
        
        if enhanced_docs:
            enhanced_answer += f"\n🧠 智能处理： {len(enhanced_docs)} 个来源使用 Unstructured 处理（保留结构）"
        
        if rich_content_docs:
            enhanced_answer += f"\n📊 结构化内容： {len(rich_content_docs)} 个来源具有丰富结构（标题、表格、列表）"
        
        log(f"MCP服务器：成功生成回答，使用了 {len(source_documents)} 个来源")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP服务器：处理问题时出错：{e}")
        return f"❌ 处理问题时出错： {e}\n\n💡 建议：\n- 验证 RAG 系统是否正确初始化\n- 尝试重新表述您的问题\n- 如果问题持续存在，请重启服务器"

def ask_rag_filtered(query: str, file_type: str = None, min_tables: int = None, min_titles: int = None, processing_method: str = None) -> str:
    """
    使用特定过滤器向 RAG 知识库提问以聚焦搜索。
    当您想从特定类型的文档或具有某些特征的文档中获取信息时使用此功能。
    
    使用场景示例：
    - 仅在 PDF 文档中搜索：file_type=".pdf"
    - 查找包含表格的文档：min_tables=1
    - 查找结构良好的文档：min_titles=5
    - 在增强处理的文档中搜索：processing_method="unstructured_enhanced"
    
    通过过滤搜索范围提供更有针对性和相关的结果。

    参数：
        query: 向知识库提出的问题或查询。
        file_type: 按文件类型过滤（例如，".pdf"、".docx"、".txt"）
        min_tables: 文档必须具有的最少表格数
        min_titles: 文档必须具有的最少标题数
        processing_method: 按处理方法过滤（例如，"unstructured_enhanced"、"markitdown"）
    """
    log(f"MCP服务器：使用过滤器处理问题：{query}")
    log(f"MCP服务器：应用的过滤器 - 类型：{file_type}，表格：{min_tables}，标题：{min_titles}，方法：{processing_method}")
    initialize_rag()
    
    try:
        # 创建元数据过滤器
        metadata_filter = create_metadata_filter(
            file_type=file_type,
            processing_method=processing_method,
            min_tables=min_tables,
            min_titles=min_titles
        )
        
        # 使用带过滤器的 QA 链
        qa_chain = get_qa_chain(rag_state["vector_store"], metadata_filter)
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])

        # 优先返回简洁的回答文本（去掉来源与建议）
        concise = extract_brief_answer(response.get("result", ""))
        if concise:
            log(f"MCP服务器：成功生成简洁过滤回答，使用了 {len(source_documents)} 个来源")
            return concise
        
        # 验证是否真的有符合过滤器的相关信息
        if not source_documents:
            # 没有符合过滤器的来源
            enhanced_answer = f"🔍 回答（已应用过滤器）：\n\n❌ 在知识库中未找到符合指定过滤器的相关信息。\n\n"
            
            # 显示应用的过滤器
            if metadata_filter:
                enhanced_answer += "📋 应用的过滤器：\n"
                for key, value in metadata_filter.items():
                    if key == "file_type":
                        enhanced_answer += f"   • 文件类型：{value}\n"
                    elif key == "processing_method":
                        enhanced_answer += f"   • 处理方法：{value.replace('_', ' ').title()}\n"
                    elif key == "structural_tables_count":
                        enhanced_answer += f"   • 最少表格数：{value['$gte']}\n"
                    elif key == "structural_titles_count":
                        enhanced_answer += f"   • 最少标题数：{value['$gte']}\n"
                    else:
                        enhanced_answer += f"   • {key}：{value}\n"
            
            enhanced_answer += "\n💡 建议：\n"
            enhanced_answer += "• 尝试放宽过滤器以获得更多结果\n"
            enhanced_answer += "• 验证您有符合指定条件的文档\n"
            enhanced_answer += "• 使用 `get_knowledge_base_stats()` 查看可用的文档类型\n"
            enhanced_answer += "• 考虑加载更多符合过滤器的文档\n\n"
            enhanced_answer += "⚠️ 注意： 过滤器可能过于严格，如果没有获得结果，请尝试使用更宽松的过滤器。"
            
            log(f"MCP服务器：未找到符合指定过滤器的来源")
            return enhanced_answer
        
        # 如果有来源，构建正常回答
        enhanced_answer = f"🔍 回答（已应用过滤器）：\n{answer}\n"
        
        # 显示应用的过滤器
        if metadata_filter:
            enhanced_answer += "\n📋 应用的过滤器：\n"
            for key, value in metadata_filter.items():
                if key == "file_type":
                    enhanced_answer += f"   • 文件类型：{value}\n"
                elif key == "processing_method":
                    enhanced_answer += f"   • 处理方法：{value.replace('_', ' ').title()}\n"
                elif key == "structural_tables_count":
                    enhanced_answer += f"   • 最少表格数：{value['$gte']}\n"
                elif key == "structural_titles_count":
                    enhanced_answer += f"   • 最少标题数：{value['$gte']}\n"
                else:
                    enhanced_answer += f"   • {key}：{value}\n"
        
        # 添加来源信息
        if source_documents:
            enhanced_answer += "\n📚 使用的信息来源：\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "未知来源")
                
                source_info = f"   {i}. {source_name}"
                
                # 添加来源的附加信息
                file_path = metadata.get("file_path")
                if file_path:
                    source_info += f"\n      - 路径： `{file_path}`"
                
                file_type = metadata.get("file_type")
                if file_type:
                    source_info += f"\n      - 类型： {(file_type or 'unknown').upper()}"
                
                processing_method = metadata.get("processing_method")
                if processing_method:
                    method_display = processing_method.replace('_', ' ').title()
                    source_info += f"\n      - 处理： {method_display}"
                
                # 添加结构信息
                structural_info = metadata.get("structural_info")
                if structural_info:
                    source_info += f"\n      - 结构： {structural_info.get('total_elements', 'N/A')} 个元素"
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
                
                enhanced_answer += source_info + "\n\n"
        
        # 添加回答质量信息
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ 高可信度： 基于多个过滤来源的回答"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ 中等可信度： 基于 2 个过滤来源的回答"
        else:
            enhanced_answer += "\n⚠️ 有限可信度： 基于 1 个过滤来源的回答"
        
        log(f"MCP服务器：成功生成过滤回答，使用了 {len(source_documents)} 个来源")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP服务器：处理过滤问题时出错：{e}")
        return f"❌ 处理过滤问题时出错： {e}\n\n💡 建议：\n- 验证 RAG 系统是否正确初始化\n- 尝试使用限制较少的过滤器\n- 如果问题持续存在，请重启服务器" 