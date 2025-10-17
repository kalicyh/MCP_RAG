"""
MCP 文档工具
===========

此模块包含与文档处理相关的工具。
从 rag_server.py 迁移而来，用于模块化架构。

注意：这些函数被设计为在主服务器中使用 @mcp.tool() 装饰器。
"""

import os
import tempfile
import requests
from datetime import datetime
from urllib.parse import urlparse
from rag_core_openai import (
    add_text_to_knowledge_base,
    add_text_to_knowledge_base_enhanced,
    load_document_with_elements
)
from utils.logger import log
from models import DocumentModel, MetadataModel

# 必须在服务器中可用的全局变量
rag_state = {}
initialize_rag_func = None
save_processed_copy_func = None
md_converter = None  # deprecated placeholder, MarkItDown support removed

def set_rag_state(state):
    """设置全局 RAG 状态。"""
    global rag_state
    rag_state = state

def set_initialize_rag_func(func):
    """设置 RAG 初始化函数。"""
    global initialize_rag_func
    initialize_rag_func = func

def set_md_converter(converter):
    """Deprecated: previously used to set a MarkItDown converter. This is now a no-op kept for API compatibility."""
    global md_converter
    md_converter = converter
    log("警告: set_md_converter 已弃用 — MarkItDown 支持已移除，传入的转换器将被忽略。")

def set_save_processed_copy_func(func):
    """设置保存处理副本的函数。"""
    global save_processed_copy_func
    save_processed_copy_func = func

def initialize_rag():
    """初始化 RAG 系统。"""
    if initialize_rag_func:
        initialize_rag_func()
    elif "initialized" in rag_state:
        return
    # 此函数必须在主服务器中实现
    pass

def save_processed_copy(file_path: str, processed_content: str, processing_method: str = "unstructured") -> str:
    """保存文档的处理副本。"""
    if save_processed_copy_func:
        return save_processed_copy_func(file_path, processed_content, processing_method)
    return ""

def learn_text(text: str, source_name: str = "manual_input") -> str:
    """
    将新的文本片段添加到 RAG 知识库以供将来参考。
    当您想要教授AI应该记住的新信息时使用此功能。
    
    使用场景示例：
    - 添加事实、定义或解释
    - 存储对话中的重要信息
    - 保存研究发现或笔记
    - 添加特定主题的上下文

    Args:
        text: 要学习并存储在知识库中的文本内容。
        source_name: 来源的描述性名称（例如，"user_notes"、"research_paper"、"conversation_summary"）。
    """
    log(f"MCP Server: 正在处理来自源 {source_name} 的 {len(text)} 个字符的文本")
    initialize_rag()
    
    try:
        # 使用 MetadataModel 创建结构化元数据
        metadata_model = MetadataModel(
            source=source_name,
            input_type="manual_text",
            processed_date=datetime.now(),
            processing_method="manual_input",
            chunking_method="standard",
            chunk_count=1,
            avg_chunk_size=len(text)
        )
        
        # 转换为字典以与核心兼容
        source_metadata = metadata_model.to_dict()
        
        # 使用核心函数将文本与元数据一起添加
        add_text_to_knowledge_base(text, rag_state["vector_store"], source_metadata)
        log(f"MCP Server: 文本已成功添加到知识库")
        return f"文本已成功添加到知识库。片段: '{text[:70]}...' (来源: {source_name})"
    except Exception as e:
        log(f"MCP Server: 添加文本时出错: {e}")
        return f"添加文本时出错: {e}"

def learn_document(file_path: str) -> str:
    """
    使用高级 Unstructured 处理和真正的语义分块读取和处理文档文件，并将其添加到知识库。
    当您想要通过智能处理从文档文件中教授AI时使用此功能。
    
    支持的文件类型：PDF、DOCX、PPTX、XLSX、TXT、HTML、CSV、JSON、XML、ODT、ODP、ODS、RTF、
    图像（PNG、JPG、TIFF、BMP 带OCR）、电子邮件（EML、MSG）以及总共超过25种格式。
    
    高级功能：
    - 基于文档结构（标题、段落、列表）的真正语义分块
    - 智能文档结构保持（标题、列表、表格）
    - 自动噪音去除（页眉、页脚、无关内容）
    - 结构元数据提取
    - 任何文档类型的健壮回退系统
    - 通过语义边界增强上下文保持
    
    使用场景示例：
    - 处理具有复杂布局的研究论文或文章
    - 从带有表格和列表的报告或手册中添加内容
    - 从带有格式的电子表格导入数据
    - 将演示文稿转换为可搜索的知识
    - 使用OCR处理扫描文档
    
    文档将通过真正的语义分块进行智能处理，并使用增强的元数据存储。
    处理后的文档副本将被保存以供验证。

    Args:
        file_path: 要处理的文档文件的绝对或相对路径。
    """
    log(f"MCP Server: 开始高级文档处理: {file_path}")
    log(f"MCP Server: DEBUG - 接收到的路径: {repr(file_path)}")
    log(f"MCP Server: DEBUG - 检查绝对路径是否存在: {os.path.abspath(file_path)}")
    initialize_rag()  # 确保 RAG 系统已准备就绪
    
    try:
        if not os.path.exists(file_path):
            log(f"MCP Server: 在路径中未找到文件: {file_path}")
            return f"错误: 在 '{file_path}' 中未找到文件"

        log(f"MCP Server: 使用高级 Unstructured 系统处理文档...")
        
        # 使用新的带结构元素的处理系统
        processed_content, raw_metadata, structural_elements = load_document_with_elements(file_path)

        if not processed_content or processed_content.isspace():
            log(f"MCP Server: 警告: 文档已处理但无法提取内容: {file_path}")
            return f"警告: 文档 '{file_path}' 已处理，但无法提取文本内容。"

        log(f"MCP Server: 文档处理成功 ({len(processed_content)} 个字符)")
        
        # 创建结构化文档模型
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # 提取结构信息
        structural_info = raw_metadata.get("structural_info", {})
        titles_count = structural_info.get("titles_count", 0)
        tables_count = structural_info.get("tables_count", 0)
        lists_count = structural_info.get("lists_count", 0)
        total_elements = structural_info.get("total_elements", 0)
        
        # 创建 DocumentModel
        document_model = DocumentModel(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            content=processed_content,  # 原始内容（在这种情况下与处理后的内容相同）
            processed_content=processed_content,
            processing_method=raw_metadata.get("processing_method", "unstructured_enhanced"),
            processing_date=datetime.now(),
            structural_elements=structural_elements or [],
            total_elements=total_elements,
            titles_count=titles_count,
            tables_count=tables_count,
            lists_count=lists_count,
            chunk_count=0  # 分块后将计算
        )
        
        # 创建 MetadataModel
        metadata_model = MetadataModel(
            source=file_name,
            input_type="file_upload",
            processed_date=datetime.now(),
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processing_method=raw_metadata.get("processing_method", "unstructured_enhanced"),
            structural_info=structural_info,
            total_elements=total_elements,
            titles_count=titles_count,
            tables_count=tables_count,
            lists_count=lists_count,
            narrative_blocks=structural_info.get("narrative_blocks", 0),
            other_elements=structural_info.get("other_elements", 0),
            chunking_method="semantic" if structural_elements else "standard",
            avg_chunk_size=len(processed_content) / max(total_elements, 1)
        )
        
        # 验证文档
        if not document_model.is_valid():
            log(f"MCP Server: 错误: 根据模型标准文档无效")
            return f"错误: 处理后的文档不符合有效性标准"
        
        log(f"MCP Server: 文档和元数据模型创建成功")
        log(f"MCP Server: 文档摘要: {document_model.get_summary()}")
        log(f"MCP Server: 元数据摘要: {metadata_model.get_summary()}")
        
        # 保存处理后的副本
        log(f"MCP Server: 保存处理后的副本...")
        saved_copy_path = save_processed_copy(file_path, processed_content, document_model.processing_method)
        
        # 使用真正的语义分块将内容添加到知识库
        log(f"MCP Server: 使用结构元数据将内容添加到知识库...")
        
        # 将元数据转换为字典以与核心兼容
        enhanced_metadata = metadata_model.to_dict()
        
        # 使用增强函数和结构元素进行真正的语义分块
        add_text_to_knowledge_base_enhanced(
            processed_content, 
            rag_state["vector_store"], 
            enhanced_metadata, 
            use_semantic_chunking=True,
            structural_elements=structural_elements
        )
        
        log(f"MCP Server: 处理完成 - 文档处理成功")
        
        # 使用的分块信息
        chunking_info = ""
        if structural_elements and len(structural_elements) > 1:
            chunking_info = f"🧠 高级语义分块 包含 {len(structural_elements)} 个结构元素"
        elif metadata_model.is_rich_content():
            chunking_info = f"📊 增强语义分块 基于结构元数据"
        else:
            chunking_info = f"📝 优化传统分块"
        
        return f"""✅ 文档处理成功
📄 文件: {document_model.file_name}
📋 类型: {(document_model.file_type or 'unknown').upper()}
🔧 方法: {document_model.processing_method}
{chunking_info}
📊 处理字符数: {len(processed_content):,}
📈 结构: {titles_count} 个标题, {tables_count} 个表格, {lists_count} 个列表
💾 保存的副本: {saved_copy_path if saved_copy_path else "不可用"}
✅ 验证: 使用结构化模型处理的文档"""

    except Exception as e:
        log(f"MCP Server: 处理文档 '{file_path}' 时出错: {e}")
        return f"处理文档时出错: {e}"

def learn_from_url(url: str) -> str:
    """
    处理来自 URL（网页或 YouTube 视频）的内容并将其添加到知识库。
    当您想要从网络内容中教授AI而无需下载文件时使用此功能。
    
    支持的 URL 类型：
    - 网页（HTML 内容）
    - YouTube 视频（转录文本）
    - MarkItDown 可以处理的任何 URL
    - 直接文件下载（PDF、DOCX 等）- 将使用增强的 Unstructured 处理
    
    使用场景示例：
    - 从新闻文章或博客文章添加内容
    - 处理 YouTube 视频转录文本
    - 从网页导入信息
    - 将网络内容转换为可搜索的知识
    - 直接从 URL 处理文档
    
    内容将被智能处理并使用增强的元数据存储。
    处理内容的副本将被保存以供验证。

    Args:
        url: 要处理的网页或视频的 URL。
    """
    log(f"MCP Server: 开始处理 URL: {url}")
    initialize_rag()
    
    try:
        # 检查是否为直接文件下载 URL
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1].lower()
        
        # 支持增强处理的扩展名列表
        enhanced_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', 
                              '.txt', '.html', '.htm', '.csv', '.json', '.xml', '.rtf',
                              '.odt', '.odp', '.ods', '.md', '.yaml', '.yml']
        
        if file_extension in enhanced_extensions:
            log(f"MCP Server: 检测到可下载文件 ({file_extension})，使用增强处理...")
            
            # 设置下载超时
            timeout_seconds = 30
            
            # 使用超时下载文件
            log(f"MCP Server: 使用 {timeout_seconds} 秒超时下载文件...")
            response = requests.get(url, stream=True, timeout=timeout_seconds)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            log(f"MCP Server: 文件临时下载到: {temp_file_path}")
            
            try:
                # 使用超时增强处理
                log(f"MCP Server: 开始 Unstructured 处理（大型 PDF 可能需要几分钟）...")
                
                # 对于 PDF，使用更快的配置避免挂起
                # 统一使用云端核心的加载函数（最小实现）
                processed_content, metadata, structural_elements = load_document_with_elements(temp_file_path)
                
                log(f"MCP Server: 下载的文件处理成功 ({len(processed_content)} 个字符)")
                
                # 保存处理后的副本
                log(f"MCP Server: 保存处理后的副本...")
                processing_method = metadata.get("processing_method", "unstructured_enhanced")
                domain = parsed_url.netloc.replace('.', '_')
                path = parsed_url.path.replace('/', '_').replace('.', '_')
                if not path or path == '_':
                    path = 'homepage'
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{domain}_{path}_{timestamp}_{processing_method}.md"
                processed_filepath = os.path.join("./data/documents", filename)
                
                try:
                    os.makedirs("./data/documents", exist_ok=True)
                    with open(processed_filepath, 'w', encoding='utf-8') as f:
                        f.write(processed_content)
                    log(f"MCP Server: 处理后的副本保存在: {processed_filepath}")
                except Exception as e:
                    log(f"MCP Server 警告: 无法保存处理后的副本: {e}")
                    processed_filepath = ""
                
                # 丰富元数据
                enhanced_metadata = metadata.copy()
                enhanced_metadata.update({
                    "source": url,
                    "domain": parsed_url.netloc,
                    "input_type": "url_download",
                    "converted_to_md": processed_filepath if processed_filepath else "No",
                    "server_processed_date": datetime.now().isoformat()
                })
                
                # 使用增强处理
                log(f"MCP Server: 将内容添加到知识库...")
                add_text_to_knowledge_base_enhanced(
                    processed_content, 
                    rag_state["vector_store"], 
                    enhanced_metadata, 
                    use_semantic_chunking=True,
                    structural_elements=structural_elements if 'structural_elements' in locals() else None
                )
                
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                    log(f"MCP Server: 临时文件已删除: {temp_file_path}")
                except Exception as e:
                    log(f"MCP Server 警告: 无法删除临时文件: {e}")
                
                log(f"MCP Server: 处理完成 - URL 处理成功")
                
                # 准备信息响应
                file_name = os.path.basename(parsed_url.path) if parsed_url.path != '/' else parsed_url.netloc
                file_type = metadata.get("file_type", file_extension)
                processing_method = metadata.get("processing_method", "unstructured_enhanced")
                
                return f"""✅ URL 处理成功
🌐 URL: {url}
📄 文件: {file_name}
📋 类型: {(file_type or 'unknown').upper()}
🔧 方法: {processing_method}
📊 处理字符数: {len(processed_content):,}
💾 保存的副本: {processed_filepath if processed_filepath else "不可用"}"""
                
            except Exception as e:
                # 出错时清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                raise e
        else:
            method_used = None
            log("MCP Server: 使用轻量回退（requests + 简单清洗）处理网页...")
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                html = resp.text
                # 基础清洗：移除 script/style，去标签，压缩空白
                import re
                # 去掉 script/style 内容
                html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
                html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
                # 替换常见块标签为换行
                html = re.sub(r"</?(p|div|br|li|ul|ol|tr|td|th|h[1-6])[^>]*>", "\n", html, flags=re.IGNORECASE)
                # 去所有其余标签
                text = re.sub(r"<[^>]+>", " ", html)
                # HTML 实体最简替换
                text = (text
                        .replace("&nbsp;", " ")
                        .replace("&amp;", "&")
                        .replace("&lt;", "<")
                        .replace("&gt;", ">")
                        )
                # 压缩空白并截断尾部空行
                text = re.sub(r"\s+", " ", text).strip()
                processed_content = text
                if not processed_content:
                    return f"警告: URL '{url}' 已获取，但内容为空。"
                log(f"MCP Server: 回退网页提取成功 ({len(processed_content)} 个字符)")
                method_used = "html_fallback"
            except Exception as e:
                log(f"MCP Server: 回退网页提取失败: {e}")
                return f"处理 URL 时出错: {e}"
            
            # 保存处理后的副本
            log(f"MCP Server: 保存处理后的副本...")
            domain = parsed_url.netloc.replace('.', '_')
            path = parsed_url.path.replace('/', '_').replace('.', '_')
            if not path or path == '_':
                path = 'homepage'
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{path}_{timestamp}_web.md"
            processed_filepath = os.path.join("./data/documents", filename)
            
            try:
                os.makedirs("./data/documents", exist_ok=True)
                with open(processed_filepath, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                log(f"MCP Server: 处理后的副本保存在: {processed_filepath}")
            except Exception as e:
                log(f"MCP Server 警告: 无法保存处理后的副本: {e}")
                processed_filepath = ""
            
            # 创建元数据
            metadata = {
                "source": url,
                "domain": parsed_url.netloc,
                "input_type": "url_web",
                "processed_date": datetime.now().isoformat(),
                "processing_method": method_used or "html_fallback",
                "converted_to_md": processed_filepath if processed_filepath else "No",
                "server_processed_date": datetime.now().isoformat()
            }
            
            # 将内容添加到知识库
            log(f"MCP Server: 将内容添加到知识库...")
            add_text_to_knowledge_base(processed_content, rag_state["vector_store"], metadata)
            
            log(f"MCP Server: 处理完成 - URL 处理成功")
            
            # 准备信息响应
            return f"""✅ URL 处理成功
🌐 URL: {url}
📋 类型: 网页
🔧 方法: {('HTML 回退')}
📊 处理字符数: {len(processed_content):,}
💾 保存的副本: {processed_filepath if processed_filepath else "不可用"}"""
                
    except Exception as e:
        log(f"MCP Server: 处理 URL '{url}' 时出错: {e}")
        return f"处理 URL 时出错: {e}" 