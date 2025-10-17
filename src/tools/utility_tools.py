"""
MCP 实用工具
============

此模块包含实用工具和维护功能。
从 rag_server.py 迁移而来，用于模块化架构。

注意：这些函数被设计为在主服务器中使用 @mcp.tool() 装饰器。
"""

from rag_core_openai import (
    get_document_statistics,
    get_cache_stats,
    clear_embedding_cache,
    optimize_vector_store,
    get_vector_store_stats,
    reindex_vector_store
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

def analyze_documents_with_models(vector_store) -> dict:
    """
    使用结构化模型分析文档以获取更详细的信息。
    
    参数：
        vector_store: 向量数据库
        
    Returns:
        使用模型的详细分析字典
    """
    if MetadataModel is None:
        return {"error": "MetadataModel 不可用"}
    
    try:
        # 获取所有文档
        all_docs = vector_store.get()
        
        if not all_docs or not all_docs['documents']:
            return {"total_documents": 0, "message": "数据库为空"}
        
        documents = all_docs['documents']
        metadatas = all_docs.get('metadatas', [])
        
        # 转换为结构化模型
        metadata_models = []
        for metadata in metadatas:
            if metadata:
                try:
                    metadata_model = MetadataModel.from_dict(metadata)
                    metadata_models.append(metadata_model)
                except Exception as e:
                    log(f"MCP 服务器警告: 将元数据转换为模型时出错: {e}")
        
        # 使用结构化模型进行分析
        analysis = {
            "total_documents": len(documents),
            "structured_models": len(metadata_models),
            "file_types": {},
            "processing_methods": {},
            "chunking_methods": {},
            "content_quality": {
                "rich_content": 0,
                "standard_content": 0,
                "poor_content": 0
            },
            "structural_analysis": {
                "documents_with_tables": 0,
                "documents_with_titles": 0,
                "documents_with_lists": 0,
                "avg_tables_per_doc": 0,
                "avg_titles_per_doc": 0,
                "avg_lists_per_doc": 0,
                "avg_chunk_size": 0
            },
            "processing_quality": {
                "unstructured_enhanced": 0,
                "manual_input": 0,
                "markitdown": 0,
                "other": 0
            }
        }
        
        total_tables = 0
        total_titles = 0
        total_lists = 0
        total_chunk_sizes = 0
        
        for model in metadata_models:
            # 文件类型
            file_type = model.file_type or "unknown"
            analysis["file_types"][file_type] = analysis["file_types"].get(file_type, 0) + 1
            
            # 处理方法
            processing_method = model.processing_method or "unknown"
            analysis["processing_methods"][processing_method] = analysis["processing_methods"].get(processing_method, 0) + 1
            
            # 分块方法
            chunking_method = model.chunking_method or "unknown"
            analysis["chunking_methods"][chunking_method] = analysis["chunking_methods"].get(chunking_method, 0) + 1
            
            # 内容质量
            if model.is_rich_content():
                analysis["content_quality"]["rich_content"] += 1
            elif model.total_elements > 1:
                analysis["content_quality"]["standard_content"] += 1
            else:
                analysis["content_quality"]["poor_content"] += 1
            
            # 结构分析
            if model.tables_count > 0:
                analysis["structural_analysis"]["documents_with_tables"] += 1
                total_tables += model.tables_count
            
            if model.titles_count > 0:
                analysis["structural_analysis"]["documents_with_titles"] += 1
                total_titles += model.titles_count
            
            if model.lists_count > 0:
                analysis["structural_analysis"]["documents_with_lists"] += 1
                total_lists += model.lists_count
            
            # 块大小
            if model.avg_chunk_size > 0:
                total_chunk_sizes += model.avg_chunk_size
            
            # 处理质量
            if processing_method == "unstructured_enhanced":
                analysis["processing_quality"]["unstructured_enhanced"] += 1
            elif processing_method == "manual_input":
                analysis["processing_quality"]["manual_input"] += 1
            elif processing_method == "markitdown":
                analysis["processing_quality"]["markitdown"] += 1
            else:
                analysis["processing_quality"]["other"] += 1
        
        # 计算平均值
        if len(metadata_models) > 0:
            analysis["structural_analysis"]["avg_tables_per_doc"] = total_tables / len(metadata_models)
            analysis["structural_analysis"]["avg_titles_per_doc"] = total_titles / len(metadata_models)
            analysis["structural_analysis"]["avg_lists_per_doc"] = total_lists / len(metadata_models)
            analysis["structural_analysis"]["avg_chunk_size"] = total_chunk_sizes / len(metadata_models)
        
        return analysis
        
    except Exception as e:
        log(f"MCP 服务器错误: 使用模型分析时出错: {e}")
        return {"error": str(e)}

def get_knowledge_base_stats() -> str:
    """
    获取知识库的综合统计信息，包括文档类型、处理方法和结构信息。
    使用此功能了解知识库中可用的信息以及如何处理这些信息。
    
    使用场景示例：
    - 检查知识库中有多少文档
    - 了解文件类型的分布
    - 查看使用了哪些处理方法
    - 分析存储文档的结构复杂性
    
    这有助于您对搜索内容和过滤查询做出明智决策。

    返回：
        关于知识库内容的详细统计信息。
    """
    log(f"MCP服务器：正在获取知识库统计信息...")
    initialize_rag()
    
    try:
        # 获取基本统计信息
        basic_stats = get_document_statistics(rag_state["vector_store"])
        
        if "error" in basic_stats:
            return f"❌ 获取统计信息时出错： {basic_stats['error']}"
        
        if basic_stats.get("total_documents", 0) == 0:
            return "📊 知识库为空\n\n知识库中没有存储任何文档。"
        
        # 获取结构化模型分析
        model_analysis = analyze_documents_with_models(rag_state["vector_store"])
        
        # 构建详细响应
        response = f"📊 知识库统计信息\n\n"
        response += f"📚 文档总数: {basic_stats['total_documents']}\n"
        
        # 关于结构化模型的信息（如果可用）
        if "error" not in model_analysis and model_analysis.get("structured_models", 0) > 0:
            response += f"🧠 结构化模型文档: {model_analysis['structured_models']}\n"
            response += f"📈 高级分析可用: ✅\n"
        else:
            response += f"📈 高级分析可用: ❌ (使用基础分析)\n"
        
        response += "\n"
        
        # 文件类型
        if basic_stats["file_types"]:
            response += "📄 文件类型:\n"
            for file_type, count in sorted(basic_stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / basic_stats["total_documents"]) * 100
                display_ft = (file_type.upper() if isinstance(file_type, str) else "UNKNOWN")
                response += f"   • {display_ft}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # 处理方法
        if basic_stats["processing_methods"]:
            response += "🔧 处理方法:\n"
            for method, count in sorted(basic_stats["processing_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / basic_stats["total_documents"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # 分块方法（仅当有模型分析时）
        if "error" not in model_analysis and model_analysis.get("chunking_methods"):
            response += "🧩 分块方法:\n"
            for method, count in sorted(model_analysis["chunking_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / model_analysis["structured_models"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # 内容质量（仅当有模型分析时）
        if "error" not in model_analysis and model_analysis.get("content_quality"):
            response += "📊 内容质量:\n"
            quality = model_analysis["content_quality"]
            total_analyzed = quality["rich_content"] + quality["standard_content"] + quality["poor_content"]
            
            if total_analyzed > 0:
                rich_pct = (quality["rich_content"] / total_analyzed) * 100
                standard_pct = (quality["standard_content"] / total_analyzed) * 100
                poor_pct = (quality["poor_content"] / total_analyzed) * 100
                
                response += f"   • 🟢 结构丰富的内容: {quality['rich_content']} ({rich_pct:.1f}%)\n"
                response += f"   • 🟡 标准内容: {quality['standard_content']} ({standard_pct:.1f}%)\n"
                response += f"   • 🔴 基础内容: {quality['poor_content']} ({poor_pct:.1f}%)\n"
            response += "\n"
        
        # 结构统计信息
        structural = basic_stats["structural_stats"]
        response += "🏗️ 结构信息:\n"
        response += f"   • 包含表格的文档: {structural['documents_with_tables']}\n"
        response += f"   • 包含标题的文档: {structural['documents_with_titles']}\n"
        response += f"   • 包含列表的文档: {structural['documents_with_lists']}\n"
        response += f"   • 每个文档的平均表格数: {structural['avg_tables_per_doc']:.1f}\n"
        response += f"   • 每个文档的平均标题数: {structural['avg_titles_per_doc']:.1f}\n"
        response += f"   • 每个文档的平均列表数: {structural['avg_lists_per_doc']:.1f}\n"
        
        # 模型的额外信息（如果可用）
        if "error" not in model_analysis and model_analysis.get("structural_analysis"):
            model_structural = model_analysis["structural_analysis"]
            response += f"   • 平均块大小: {model_structural['avg_chunk_size']:.0f} 个字符\n"
        
        response += "\n"
        
        # 增强的搜索建议
        response += "💡 搜索建议:\n"
        if structural['documents_with_tables'] > 0:
            response += f"   • 使用 `ask_rag_filtered` 加上 `min_tables=1` 在包含表格的文档中搜索信息\n"
        if structural['documents_with_titles'] > 5:
            response += f"   • 使用 `ask_rag_filtered` 加上 `min_titles=5` 在结构良好的文档中搜索\n"
        if ".pdf" in basic_stats["file_types"]:
            response += f"   • 使用 `ask_rag_filtered` 加上 `file_type=\".pdf\"` 仅在PDF文档中搜索\n"
        
        # 基于模型分析的额外建议
        if "error" not in model_analysis:
            if model_analysis["content_quality"]["rich_content"] > 0:
                response += f"   • 您有 {model_analysis['content_quality']['rich_content']} 个结构丰富的文档 - 利用语义分块\n"
            if model_analysis["processing_quality"]["unstructured_enhanced"] > 0:
                response += f"   • {model_analysis['processing_quality']['unstructured_enhanced']} 个文档使用增强的Unstructured处理\n"
        
        log(f"MCP 服务器: 统计信息获取成功")
        return response
        
    except Exception as e:
        log(f"MCP 服务器: 获取统计信息时出错: {e}")
        return f"❌ 获取统计信息时出错: {e}"

def get_embedding_cache_stats() -> str:
    """
    获取嵌入缓存性能的详细统计信息。
    使用此功能监控缓存效率并了解系统性能。
    
    使用场景示例：
    - 检查缓存命中率以查看系统是否高效工作
    - 监控缓存的内存使用情况
    - 了解嵌入被重用的频率
    - 调试性能问题
    
    这有助于您优化系统并了解其行为。

    返回：
        关于嵌入缓存性能的详细统计信息。
    """
    log(f"MCP服务器：正在获取嵌入缓存统计信息...")
    
    try:
        stats = get_cache_stats()
        
        if not stats:
            return "📊 嵌入缓存不可用\n\n嵌入缓存未初始化。"
        
        # 构建详细响应
        response = f"📊 嵌入缓存统计信息\n\n"
        
        # 主要指标
        response += f"🔄 缓存活动:\n"
        response += f"   • 总请求数: {stats['total_requests']}\n"
        response += f"   • 内存命中数: {stats['memory_hits']}\n"
        response += f"   • 磁盘命中数: {stats['disk_hits']}\n"
        response += f"   • 未命中数（未找到）: {stats['misses']}\n\n"
        
        # 成功率
        response += f"📈 成功率:\n"
        response += f"   • 内存命中率: {stats['memory_hit_rate']}\n"
        response += f"   • 磁盘命中率: {stats['disk_hit_rate']}\n"
        response += f"   • 总命中率: {stats['overall_hit_rate']}\n\n"
        
        # 内存使用
        response += f"💾 内存使用:\n"
        response += f"   • 内存中的嵌入: {stats['memory_cache_size']}\n"
        response += f"   • 最大大小: {stats['max_memory_size']}\n"
        response += f"   • 缓存目录: {stats['cache_directory']}\n\n"
        
        # 性能分析
        total_requests = stats['total_requests']
        if total_requests > 0:
            memory_hit_rate = float(stats['memory_hit_rate'].rstrip('%'))
            overall_hit_rate = float(stats['overall_hit_rate'].rstrip('%'))
            
            response += f"🎯 性能分析:\n"
            
            if overall_hit_rate > 70:
                response += f"   • ✅ 性能优秀: {overall_hit_rate:.1f}% 命中率\n"
            elif overall_hit_rate > 50:
                response += f"   • ⚠️ 性能一般: {overall_hit_rate:.1f}% 命中率\n"
            else:
                response += f"   • ❌ 性能较低: {overall_hit_rate:.1f}% 命中率\n"
            
            if memory_hit_rate > 50:
                response += f"   • 🚀 内存缓存有效: {memory_hit_rate:.1f}% 内存命中率\n"
            else:
                response += f"   • 💾 依赖磁盘访问: {memory_hit_rate:.1f}% 内存命中率\n"
            
            # 优化建议
            response += f"\n💡 优化建议:\n"
            if overall_hit_rate < 30:
                response += f"   • 考虑将类似文档一起处理\n"
                response += f"   • 检查是否有太多不重复的唯一文本\n"
            
            if memory_hit_rate < 30 and total_requests > 100:
                response += f"   • 考虑增加内存缓存大小\n"
                response += f"   • 磁盘命中比内存命中慢\n"
            
            if stats['memory_cache_size'] >= stats['max_memory_size'] * 0.9:
                response += f"   • 内存缓存几乎已满\n"
                response += f"   • 如有可用RAM，考虑增加 max_memory_size\n"
        
        log(f"MCP Server: 成功获取缓存统计信息")
        return response
        
    except Exception as e:
        log(f"MCP Server: 获取缓存统计信息时出错: {e}")
        return f"❌ 获取缓存统计信息时出错: {e}"

def clear_embedding_cache_tool() -> str:
    """
    清除嵌入缓存以释放内存和磁盘空间。
    在需要重置缓存或释放资源时使用此功能。
    
    使用场景示例：
    - 系统RAM不足时释放内存
    - 更改嵌入模型后重置缓存
    - 清除不再需要的旧缓存嵌入
    - 解决缓存相关问题
    
    警告：这将删除所有缓存的嵌入，需要重新计算。

    Returns:
        缓存清理操作的确认消息
    """
    log(f"MCP Server: 正在清理嵌入缓存...")
    
    try:
        clear_embedding_cache()
        
        response = "🧹 嵌入缓存清理成功\n\n"
        response += "✅ 已删除所有存储在缓存中的嵌入。\n"
        response += "📝 下一次嵌入将从头开始计算。\n"
        response += "💾 已释放内存和磁盘空间。\n\n"
        response += "⚠️ 注意: 嵌入将在需要时自动重新计算。"
        
        log(f"MCP Server: 嵌入缓存清理成功")
        return response
        
    except Exception as e:
        log(f"MCP Server: 清理缓存时出错: {e}")
        return f"❌ 清理缓存时出错: {e}"

def optimize_vector_database() -> str:
    """
    优化向量数据库以提高搜索性能。
    此工具重新组织内部索引以实现更快的搜索。
    
    使用此工具的情况：
    - 搜索速度缓慢
    - 已添加大量新文档
    - 希望提高系统整体性能
    
    Returns:
        优化过程的信息
    """
    log("MCP Server: 正在优化向量数据库...")
    
    try:
        result = optimize_vector_store()
        
        if result["status"] == "success":
            response = f"✅ 向量数据库优化成功\n\n"
            response += f"📊 优化前统计信息:\n"
            stats_before = result.get("stats_before", {})
            response += f"   • 总文档数: {stats_before.get('total_documents', 'N/A')}\n"
            
            response += f"\n📊 优化后统计信息:\n"
            stats_after = result.get("stats_after", {})
            response += f"   • 总文档数: {stats_after.get('total_documents', 'N/A')}\n"
            
            response += f"\n🚀 优化效果:\n"
            response += f"   • 搜索速度更快\n"
            response += f"   • 结果精度更高\n"
            response += f"   • 索引已优化\n"
            
        else:
            response = f"❌ 优化数据库时出错: {result.get('message', '未知错误')}"
            
        return response
        
    except Exception as e:
        log(f"MCP Server Error: 优化时出错: {e}")
        return f"❌ 优化向量数据库时出错: {str(e)}"

def get_vector_database_stats() -> str:
    """
    获取向量数据库的详细统计信息。
    包括文档、文件类型和配置信息。
    
    使用此工具：
    - 验证数据库状态
    - 分析文档分布
    - 诊断性能问题
    - 规划优化
    
    Returns:
        向量数据库的详细统计信息
    """
    log("MCP Server: 正在获取向量数据库统计信息...")
    
    try:
        stats = get_vector_store_stats()
        
        if "error" in stats:
            return f"❌ 获取统计信息时出错: {stats['error']}"
        
        response = f"📊 向量数据库统计信息\n\n"
        
        response += f"📚 基本信息:\n"
        response += f"   • 文档总数: {stats.get('total_documents', 0)}\n"
        response += f"   • 集合名称: {stats.get('collection_name', 'N/A')}\n"
        response += f"   • 嵌入维度: {stats.get('embedding_dimension', 'N/A')}\n"
        
        # Tipos de archivo
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
        
        # 性能信息
        performance = stats.get('performance', {})
        if performance:
            response += f"\n⚡ 性能信息:\n"
            response += f"   • 索引时间: {performance.get('indexing_time', 'N/A')}\n"
            response += f"   • 索引大小: {performance.get('index_size', 'N/A')}\n"
        
        log(f"MCP Server: 成功获取向量数据库统计信息")
        return response
        
    except Exception as e:
        log(f"MCP Server: 获取向量数据库统计信息时出错: {e}")
        return f"❌ 获取向量数据库统计信息时出错: {str(e)}"

def reindex_vector_database(profile: str = 'auto') -> str:
    """
    使用优化配置重新索引向量数据库。
    此工具使用针对当前大小优化的参数重新创建索引。
    
    Args:
        profile: 配置档案 ('small', 'medium', 'large', 'auto')
                 'auto' 自动检测最佳配置档案
    
    使用此工具的情况：
    - 更改配置档案时
    - 搜索非常缓慢时
    - 希望针对特定数据库大小进行优化时
    - 存在持续性能问题时
    
    ⚠️ 注意: 此过程可能需要一些时间，具体取决于数据库大小。
    
    Returns:
        重新索引过程的信息
    """
    log(f"MCP Server: 正在使用配置档案 '{profile}' 重新索引向量数据库...")
    
    try:
        result = reindex_vector_store(profile=profile)
        
        if result["status"] == "success":
            response = f"✅ 向量数据库重新索引成功\n\n"
            response += f"📊 应用的配置档案: {result.get('profile', 'N/A')}\n"
            response += f"📊 处理的文档数: {result.get('documents_processed', 'N/A')}\n"
            response += f"⏱️ 重新索引时间: {result.get('reindexing_time', 'N/A')}\n"
            
            response += f"\n🚀 重新索引的优势:\n"
            response += f"   • 针对当前大小优化的索引\n"
            response += f"   • 更快更精确的搜索\n"
            response += f"   • 更好的数据分布\n"
            
        else:
            response = f"❌ 重新索引数据库时出错: {result.get('message', '未知错误')}"
            
        return response
        
    except Exception as e:
        log(f"MCP Server: 重新索引向量数据库时出错: {e}")
        return f"❌ 重新索引向量数据库时出错: {str(e)}" 