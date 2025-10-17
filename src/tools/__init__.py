# MCP Tools Module
"""
MCP工具模块
===========

该模块包含按类别组织的所有工具：
- document_tools: 文档处理工具
- search_tools: 搜索和查询工具  
- utility_tools: 实用工具和维护工具

所有函数都设计为在主服务器中使用@mcp.tool()装饰器。
"""

# Importar todas las funciones de cada módulo
from .document_tools import (
    learn_text,
    learn_document,
    set_rag_state as set_doc_rag_state,
    set_initialize_rag_func as set_doc_initialize_rag_func,
    set_save_processed_copy_func
)

from .search_tools import (
    ask_rag,
    ask_rag_filtered,
    set_rag_state as set_search_rag_state,
    set_initialize_rag_func as set_search_initialize_rag_func
)

from .utility_tools import (
    get_knowledge_base_stats,
    get_embedding_cache_stats,
    clear_embedding_cache_tool,
    optimize_vector_database,
    get_vector_database_stats,
    reindex_vector_database,
    set_rag_state as set_utility_rag_state,
    set_initialize_rag_func as set_utility_initialize_rag_func
)

# 配置所有工具模块中RAG状态的函数
def configure_rag_state(rag_state, initialize_rag_func=None, save_processed_copy_func=None):
    """
    在所有工具模块中配置RAG状态。
    
    Args:
        rag_state: 全局RAG状态
        initialize_rag_func: RAG初始化函数（可选）
        save_processed_copy_func: 保存处理副本函数（可选）
    """
    set_doc_rag_state(rag_state)
    set_search_rag_state(rag_state)
    set_utility_rag_state(rag_state)
    
    
    if initialize_rag_func:
        set_doc_initialize_rag_func(initialize_rag_func)
        set_search_initialize_rag_func(initialize_rag_func)
        set_utility_initialize_rag_func(initialize_rag_func)
    
    if save_processed_copy_func:
        set_save_processed_copy_func(save_processed_copy_func)

# 所有可用工具的列表，便于注册
ALL_TOOLS = [
    # 文档工具
    learn_text,
    learn_document,
    
    # 搜索工具
    ask_rag,
    ask_rag_filtered,
    
    # 实用工具
    get_knowledge_base_stats,
    get_embedding_cache_stats,
    clear_embedding_cache_tool,
    optimize_vector_database,
    get_vector_database_stats,
    reindex_vector_database
]

# 按名称注册的字典
TOOLS_BY_NAME = {
    "learn_text": learn_text,
    "learn_document": learn_document,
    "ask_rag": ask_rag,
    "ask_rag_filtered": ask_rag_filtered,
    "get_knowledge_base_stats": get_knowledge_base_stats,
    "get_embedding_cache_stats": get_embedding_cache_stats,
    "clear_embedding_cache_tool": clear_embedding_cache_tool,
    "optimize_vector_database": optimize_vector_database,
    "get_vector_database_stats": get_vector_database_stats,
    "reindex_vector_database": reindex_vector_database
}

__all__ = [
    # 文档工具
    "learn_text",
    "learn_document", 
    
    # 搜索工具
    "ask_rag",
    "ask_rag_filtered",
    
    # 实用工具
    "get_knowledge_base_stats",
    "get_embedding_cache_stats",
    "clear_embedding_cache_tool",
    "optimize_vector_database",
    "get_vector_database_stats",
    "reindex_vector_database",
    
    # 配置
    "configure_rag_state",
    "ALL_TOOLS",
    "TOOLS_BY_NAME"
] 