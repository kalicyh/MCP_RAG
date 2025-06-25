# MCP Tools Module
"""
Módulo de Herramientas para MCP
==============================

Este módulo contiene todas las herramientas organizadas por categorías:
- document_tools: Herramientas para procesamiento de documentos
- search_tools: Herramientas para búsqueda y consulta
- utility_tools: Herramientas de utilidad y mantenimiento

Todas las funciones están diseñadas para ser decoradas con @mcp.tool() en el servidor principal.
"""

# Importar todas las funciones de cada módulo
from .document_tools import (
    learn_text,
    learn_document,
    learn_from_url,
    set_rag_state as set_doc_rag_state,
    set_md_converter,
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

# Función para configurar el estado RAG en todos los módulos
def configure_rag_state(rag_state, md_converter=None, initialize_rag_func=None, save_processed_copy_func=None):
    """
    Configura el estado RAG en todos los módulos de herramientas.
    
    Args:
        rag_state: El estado RAG global
        md_converter: El conversor MarkItDown (opcional)
        initialize_rag_func: La función de inicialización RAG (opcional)
        save_processed_copy_func: La función de guardar copia procesada (opcional)
    """
    set_doc_rag_state(rag_state)
    set_search_rag_state(rag_state)
    set_utility_rag_state(rag_state)
    
    if md_converter:
        set_md_converter(md_converter)
    
    if initialize_rag_func:
        set_doc_initialize_rag_func(initialize_rag_func)
        set_search_initialize_rag_func(initialize_rag_func)
        set_utility_initialize_rag_func(initialize_rag_func)
    
    if save_processed_copy_func:
        set_save_processed_copy_func(save_processed_copy_func)

# Lista de todas las funciones disponibles para facilitar el registro
ALL_TOOLS = [
    # Document tools
    learn_text,
    learn_document,
    learn_from_url,
    
    # Search tools
    ask_rag,
    ask_rag_filtered,
    
    # Utility tools
    get_knowledge_base_stats,
    get_embedding_cache_stats,
    clear_embedding_cache_tool,
    optimize_vector_database,
    get_vector_database_stats,
    reindex_vector_database
]

# Diccionario para facilitar el registro por nombre
TOOLS_BY_NAME = {
    "learn_text": learn_text,
    "learn_document": learn_document,
    "learn_from_url": learn_from_url,
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
    # Document tools
    "learn_text",
    "learn_document", 
    "learn_from_url",
    "set_md_converter",
    
    # Search tools
    "ask_rag",
    "ask_rag_filtered",
    
    # Utility tools
    "get_knowledge_base_stats",
    "get_embedding_cache_stats",
    "clear_embedding_cache_tool",
    "optimize_vector_database",
    "get_vector_database_stats",
    "reindex_vector_database",
    
    # Configuration
    "configure_rag_state",
    "ALL_TOOLS",
    "TOOLS_BY_NAME"
] 