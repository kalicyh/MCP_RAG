"""
Herramientas de Utilidad para MCP
===============================

Este módulo contiene herramientas de utilidad y mantenimiento.
Migradas desde rag_server.py para una arquitectura modular.

NOTA: Estas funciones están diseñadas para ser decoradas con @mcp.tool() en el servidor principal.
"""

from rag_core import (
    get_document_statistics,
    get_cache_stats,
    clear_embedding_cache,
    optimize_vector_store,
    get_vector_store_stats,
    reindex_vector_store
)
from utils.logger import log

# Importar modelos estructurados
try:
    from models import MetadataModel
except ImportError as e:
    print(f"Advertencia: No se pudieron importar los modelos estructurados: {e}")
    MetadataModel = None

# Variables globales que deben estar disponibles en el servidor
rag_state = {}
initialize_rag_func = None

def set_rag_state(state):
    """Establece el estado RAG global."""
    global rag_state
    rag_state = state

def set_initialize_rag_func(func):
    """Establece la función de inicialización RAG."""
    global initialize_rag_func
    initialize_rag_func = func

def initialize_rag():
    """Inicializa el sistema RAG."""
    if initialize_rag_func:
        initialize_rag_func()
    elif "initialized" in rag_state:
        return
    # Esta función debe ser implementada en el servidor principal
    pass

def analyze_documents_with_models(vector_store) -> dict:
    """
    Analiza documentos usando modelos estructurados para obtener información más detallada.
    
    Args:
        vector_store: La base de datos vectorial
        
    Returns:
        Diccionario con análisis detallado usando modelos
    """
    if MetadataModel is None:
        return {"error": "MetadataModel no disponible"}
    
    try:
        # Obtener todos los documentos
        all_docs = vector_store.get()
        
        if not all_docs or not all_docs['documents']:
            return {"total_documents": 0, "message": "Base de datos vacía"}
        
        documents = all_docs['documents']
        metadatas = all_docs.get('metadatas', [])
        
        # Convertir a modelos estructurados
        metadata_models = []
        for metadata in metadatas:
            if metadata:
                try:
                    metadata_model = MetadataModel.from_dict(metadata)
                    metadata_models.append(metadata_model)
                except Exception as e:
                    log(f"MCP Server Warning: Error convirtiendo metadatos a modelo: {e}")
        
        # Análisis usando modelos estructurados
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
            # Tipos de archivo
            file_type = model.file_type or "unknown"
            analysis["file_types"][file_type] = analysis["file_types"].get(file_type, 0) + 1
            
            # Métodos de procesamiento
            processing_method = model.processing_method or "unknown"
            analysis["processing_methods"][processing_method] = analysis["processing_methods"].get(processing_method, 0) + 1
            
            # Métodos de chunking
            chunking_method = model.chunking_method or "unknown"
            analysis["chunking_methods"][chunking_method] = analysis["chunking_methods"].get(chunking_method, 0) + 1
            
            # Calidad del contenido
            if model.is_rich_content():
                analysis["content_quality"]["rich_content"] += 1
            elif model.total_elements > 1:
                analysis["content_quality"]["standard_content"] += 1
            else:
                analysis["content_quality"]["poor_content"] += 1
            
            # Análisis estructural
            if model.tables_count > 0:
                analysis["structural_analysis"]["documents_with_tables"] += 1
                total_tables += model.tables_count
            
            if model.titles_count > 0:
                analysis["structural_analysis"]["documents_with_titles"] += 1
                total_titles += model.titles_count
            
            if model.lists_count > 0:
                analysis["structural_analysis"]["documents_with_lists"] += 1
                total_lists += model.lists_count
            
            # Tamaño de chunks
            if model.avg_chunk_size > 0:
                total_chunk_sizes += model.avg_chunk_size
            
            # Calidad de procesamiento
            if processing_method == "unstructured_enhanced":
                analysis["processing_quality"]["unstructured_enhanced"] += 1
            elif processing_method == "manual_input":
                analysis["processing_quality"]["manual_input"] += 1
            elif processing_method == "markitdown":
                analysis["processing_quality"]["markitdown"] += 1
            else:
                analysis["processing_quality"]["other"] += 1
        
        # Calcular promedios
        if len(metadata_models) > 0:
            analysis["structural_analysis"]["avg_tables_per_doc"] = total_tables / len(metadata_models)
            analysis["structural_analysis"]["avg_titles_per_doc"] = total_titles / len(metadata_models)
            analysis["structural_analysis"]["avg_lists_per_doc"] = total_lists / len(metadata_models)
            analysis["structural_analysis"]["avg_chunk_size"] = total_chunk_sizes / len(metadata_models)
        
        return analysis
        
    except Exception as e:
        log(f"MCP Server Error: Error en análisis con modelos: {e}")
        return {"error": str(e)}

def get_knowledge_base_stats() -> str:
    """
    Gets comprehensive statistics about the knowledge base, including document types, processing methods, and structural information.
    Use this to understand what information is available in your knowledge base and how it was processed.
    
    Examples of when to use:
    - Checking how many documents are in the knowledge base
    - Understanding the distribution of file types
    - Seeing which processing methods were used
    - Analyzing the structural complexity of stored documents
    
    This helps you make informed decisions about what to search for and how to filter your queries.

    Returns:
        Detailed statistics about the knowledge base contents.
    """
    log(f"MCP Server: Obteniendo estadísticas de la base de conocimientos...")
    initialize_rag()
    
    try:
        # Obtener estadísticas básicas
        basic_stats = get_document_statistics(rag_state["vector_store"])
        
        if "error" in basic_stats:
            return f"❌ **Error obteniendo estadísticas:** {basic_stats['error']}"
        
        if basic_stats.get("total_documents", 0) == 0:
            return "📊 **Base de conocimientos vacía**\n\nNo hay documentos almacenados en la base de conocimientos."
        
        # Obtener análisis con modelos estructurados
        model_analysis = analyze_documents_with_models(rag_state["vector_store"])
        
        # Construir respuesta detallada
        response = f"📊 **Estadísticas de la Base de Conocimientos**\n\n"
        response += f"📚 **Total de documentos:** {basic_stats['total_documents']}\n"
        
        # Información sobre modelos estructurados si está disponible
        if "error" not in model_analysis and model_analysis.get("structured_models", 0) > 0:
            response += f"🧠 **Documentos con modelos estructurados:** {model_analysis['structured_models']}\n"
            response += f"📈 **Análisis avanzado disponible:** ✅\n"
        else:
            response += f"📈 **Análisis avanzado disponible:** ❌ (usando análisis básico)\n"
        
        response += "\n"
        
        # Tipos de archivo
        if basic_stats["file_types"]:
            response += "📄 **Tipos de archivo:**\n"
            for file_type, count in sorted(basic_stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / basic_stats["total_documents"]) * 100
                response += f"   • {file_type.upper()}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Métodos de procesamiento
        if basic_stats["processing_methods"]:
            response += "🔧 **Métodos de procesamiento:**\n"
            for method, count in sorted(basic_stats["processing_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / basic_stats["total_documents"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Métodos de chunking (solo si hay análisis con modelos)
        if "error" not in model_analysis and model_analysis.get("chunking_methods"):
            response += "🧩 **Métodos de chunking:**\n"
            for method, count in sorted(model_analysis["chunking_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / model_analysis["structured_models"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Calidad del contenido (solo si hay análisis con modelos)
        if "error" not in model_analysis and model_analysis.get("content_quality"):
            response += "📊 **Calidad del contenido:**\n"
            quality = model_analysis["content_quality"]
            total_analyzed = quality["rich_content"] + quality["standard_content"] + quality["poor_content"]
            
            if total_analyzed > 0:
                rich_pct = (quality["rich_content"] / total_analyzed) * 100
                standard_pct = (quality["standard_content"] / total_analyzed) * 100
                poor_pct = (quality["poor_content"] / total_analyzed) * 100
                
                response += f"   • 🟢 Contenido rico en estructura: {quality['rich_content']} ({rich_pct:.1f}%)\n"
                response += f"   • 🟡 Contenido estándar: {quality['standard_content']} ({standard_pct:.1f}%)\n"
                response += f"   • 🔴 Contenido básico: {quality['poor_content']} ({poor_pct:.1f}%)\n"
            response += "\n"
        
        # Estadísticas estructurales
        structural = basic_stats["structural_stats"]
        response += "🏗️ **Información estructural:**\n"
        response += f"   • Documentos con tablas: {structural['documents_with_tables']}\n"
        response += f"   • Documentos con títulos: {structural['documents_with_titles']}\n"
        response += f"   • Documentos con listas: {structural['documents_with_lists']}\n"
        response += f"   • Promedio de tablas por documento: {structural['avg_tables_per_doc']:.1f}\n"
        response += f"   • Promedio de títulos por documento: {structural['avg_titles_per_doc']:.1f}\n"
        response += f"   • Promedio de listas por documento: {structural['avg_lists_per_doc']:.1f}\n"
        
        # Información adicional de modelos si está disponible
        if "error" not in model_analysis and model_analysis.get("structural_analysis"):
            model_structural = model_analysis["structural_analysis"]
            response += f"   • Tamaño promedio de chunks: {model_structural['avg_chunk_size']:.0f} caracteres\n"
        
        response += "\n"
        
        # Sugerencias de búsqueda mejoradas
        response += "💡 **Sugerencias de búsqueda:**\n"
        if structural['documents_with_tables'] > 0:
            response += f"   • Usa `ask_rag_filtered` con `min_tables=1` para buscar información en documentos con tablas\n"
        if structural['documents_with_titles'] > 5:
            response += f"   • Usa `ask_rag_filtered` con `min_titles=5` para buscar en documentos bien estructurados\n"
        if ".pdf" in basic_stats["file_types"]:
            response += f"   • Usa `ask_rag_filtered` con `file_type=\".pdf\"` para buscar solo en documentos PDF\n"
        
        # Sugerencias adicionales basadas en análisis de modelos
        if "error" not in model_analysis:
            if model_analysis["content_quality"]["rich_content"] > 0:
                response += f"   • Tienes {model_analysis['content_quality']['rich_content']} documentos con estructura rica - aprovecha el chunking semántico\n"
            if model_analysis["processing_quality"]["unstructured_enhanced"] > 0:
                response += f"   • {model_analysis['processing_quality']['unstructured_enhanced']} documentos procesados con Unstructured mejorado\n"
        
        log(f"MCP Server: Estadísticas obtenidas exitosamente")
        return response
        
    except Exception as e:
        log(f"MCP Server: Error obteniendo estadísticas: {e}")
        return f"❌ **Error obteniendo estadísticas:** {e}"

def get_embedding_cache_stats() -> str:
    """
    Gets detailed statistics about the embedding cache performance.
    Use this to monitor cache efficiency and understand how the system is performing.
    
    Examples of when to use:
    - Checking cache hit rates to see if the system is working efficiently
    - Monitoring memory usage of the cache
    - Understanding how often embeddings are being reused
    - Debugging performance issues
    
    This helps you optimize the system and understand its behavior.

    Returns:
        Detailed statistics about the embedding cache performance.
    """
    log(f"MCP Server: Obteniendo estadísticas del cache de embeddings...")
    
    try:
        stats = get_cache_stats()
        
        if not stats:
            return "📊 **Cache de embeddings no disponible**\n\nEl cache de embeddings no está inicializado."
        
        # Construir respuesta detallada
        response = f"📊 **Estadísticas del Cache de Embeddings**\n\n"
        
        # Métricas principales
        response += f"🔄 **Actividad del cache:**\n"
        response += f"   • Total de solicitudes: {stats['total_requests']}\n"
        response += f"   • Hits en memoria: {stats['memory_hits']}\n"
        response += f"   • Hits en disco: {stats['disk_hits']}\n"
        response += f"   • Misses (no encontrados): {stats['misses']}\n\n"
        
        # Tasas de éxito
        response += f"📈 **Tasas de éxito:**\n"
        response += f"   • Tasa de hits en memoria: {stats['memory_hit_rate']}\n"
        response += f"   • Tasa de hits en disco: {stats['disk_hit_rate']}\n"
        response += f"   • Tasa de hits total: {stats['overall_hit_rate']}\n\n"
        
        # Uso de memoria
        response += f"💾 **Uso de memoria:**\n"
        response += f"   • Embeddings en memoria: {stats['memory_cache_size']}\n"
        response += f"   • Tamaño máximo: {stats['max_memory_size']}\n"
        response += f"   • Directorio de cache: {stats['cache_directory']}\n\n"
        
        # Análisis de rendimiento
        total_requests = stats['total_requests']
        if total_requests > 0:
            memory_hit_rate = float(stats['memory_hit_rate'].rstrip('%'))
            overall_hit_rate = float(stats['overall_hit_rate'].rstrip('%'))
            
            response += f"🎯 **Análisis de rendimiento:**\n"
            
            if overall_hit_rate > 70:
                response += f"   • ✅ Excelente rendimiento: {overall_hit_rate:.1f}% de hits\n"
            elif overall_hit_rate > 50:
                response += f"   • ⚠️ Rendimiento moderado: {overall_hit_rate:.1f}% de hits\n"
            else:
                response += f"   • ❌ Rendimiento bajo: {overall_hit_rate:.1f}% de hits\n"
            
            if memory_hit_rate > 50:
                response += f"   • 🚀 Cache en memoria efectivo: {memory_hit_rate:.1f}% de hits en memoria\n"
            else:
                response += f"   • 💾 Dependencia del disco: {memory_hit_rate:.1f}% de hits en memoria\n"
            
            # Sugerencias de optimización
            response += f"\n💡 **Sugerencias de optimización:**\n"
            if overall_hit_rate < 30:
                response += f"   • Considera procesar documentos similares juntos\n"
                response += f"   • Revisa si hay muchos textos únicos que no se repiten\n"
            
            if memory_hit_rate < 30 and total_requests > 100:
                response += f"   • Considera aumentar el tamaño del cache en memoria\n"
                response += f"   • Los hits en disco son más lentos que en memoria\n"
            
            if stats['memory_cache_size'] >= stats['max_memory_size'] * 0.9:
                response += f"   • El cache en memoria está casi lleno\n"
                response += f"   • Considera aumentar max_memory_size si tienes RAM disponible\n"
        
        log(f"MCP Server: Estadísticas del cache obtenidas exitosamente")
        return response
        
    except Exception as e:
        log(f"MCP Server: Error obteniendo estadísticas del cache: {e}")
        return f"❌ **Error obteniendo estadísticas del cache:** {e}"

def clear_embedding_cache_tool() -> str:
    """
    Clears the embedding cache to free up memory and disk space.
    Use this when you want to reset the cache or free up resources.
    
    Examples of when to use:
    - Freeing up memory when the system is running low on RAM
    - Resetting the cache after making changes to the embedding model
    - Clearing old cached embeddings that are no longer needed
    - Troubleshooting cache-related issues
    
    Warning: This will remove all cached embeddings and they will need to be recalculated.

    Returns:
        Confirmation message about the cache clearing operation.
    """
    log(f"MCP Server: Limpiando cache de embeddings...")
    
    try:
        clear_embedding_cache()
        
        response = "🧹 **Cache de embeddings limpiado exitosamente**\n\n"
        response += "✅ Se han eliminado todos los embeddings almacenados en cache.\n"
        response += "📝 Los próximos embeddings se calcularán desde cero.\n"
        response += "💾 Se ha liberado memoria y espacio en disco.\n\n"
        response += "⚠️ **Nota:** Los embeddings se recalcularán automáticamente cuando sea necesario."
        
        log(f"MCP Server: Cache de embeddings limpiado exitosamente")
        return response
        
    except Exception as e:
        log(f"MCP Server: Error limpiando cache: {e}")
        return f"❌ **Error limpiando cache:** {e}"

def optimize_vector_database() -> str:
    """
    Optimiza la base de datos vectorial para mejorar el rendimiento de búsquedas.
    Esta herramienta reorganiza los índices internos para búsquedas más rápidas.
    
    Use esta herramienta cuando:
    - Las búsquedas son lentas
    - Se han añadido muchos documentos nuevos
    - Quieres mejorar el rendimiento general del sistema
    
    Returns:
        Información sobre el proceso de optimización
    """
    log("MCP Server: Optimizando base de datos vectorial...")
    
    try:
        result = optimize_vector_store()
        
        if result["status"] == "success":
            response = f"✅ **Base de datos vectorial optimizada exitosamente**\n\n"
            response += f"📊 **Estadísticas antes de la optimización:**\n"
            stats_before = result.get("stats_before", {})
            response += f"   • Documentos totales: {stats_before.get('total_documents', 'N/A')}\n"
            
            response += f"\n📊 **Estadísticas después de la optimización:**\n"
            stats_after = result.get("stats_after", {})
            response += f"   • Documentos totales: {stats_after.get('total_documents', 'N/A')}\n"
            
            response += f"\n🚀 **Beneficios:**\n"
            response += f"   • Búsquedas más rápidas\n"
            response += f"   • Mejor precisión en resultados\n"
            response += f"   • Índices optimizados\n"
            
        else:
            response = f"❌ **Error optimizando base de datos:** {result.get('message', 'Error desconocido')}"
            
        return response
        
    except Exception as e:
        log(f"MCP Server Error: Error en optimización: {e}")
        return f"❌ **Error optimizando base de datos vectorial:** {str(e)}"

def get_vector_database_stats() -> str:
    """
    Obtiene estadísticas detalladas de la base de datos vectorial.
    Incluye información sobre documentos, tipos de archivo y configuración.
    
    Use esta herramienta para:
    - Verificar el estado de la base de datos
    - Analizar la distribución de documentos
    - Diagnosticar problemas de rendimiento
    - Planificar optimizaciones
    
    Returns:
        Estadísticas detalladas de la base de datos vectorial
    """
    log("MCP Server: Obteniendo estadísticas de base de datos vectorial...")
    
    try:
        stats = get_vector_store_stats()
        
        if "error" in stats:
            return f"❌ **Error obteniendo estadísticas:** {stats['error']}"
        
        response = f"📊 **Estadísticas de la Base de Datos Vectorial**\n\n"
        
        response += f"📚 **Información General:**\n"
        response += f"   • Total de documentos: {stats.get('total_documents', 0)}\n"
        response += f"   • Nombre de colección: {stats.get('collection_name', 'N/A')}\n"
        response += f"   • Dimensión de embeddings: {stats.get('embedding_dimension', 'N/A')}\n"
        
        # Tipos de archivo
        file_types = stats.get('file_types', {})
        if file_types:
            response += f"\n📄 **Distribución por tipo de archivo:**\n"
            for file_type, count in file_types.items():
                response += f"   • {file_type}: {count} documentos\n"
        
        # Métodos de procesamiento
        processing_methods = stats.get('processing_methods', {})
        if processing_methods:
            response += f"\n🔧 **Métodos de procesamiento:**\n"
            for method, count in processing_methods.items():
                response += f"   • {method}: {count} documentos\n"
        
        # Información de rendimiento
        performance = stats.get('performance', {})
        if performance:
            response += f"\n⚡ **Información de rendimiento:**\n"
            response += f"   • Tiempo de indexación: {performance.get('indexing_time', 'N/A')}\n"
            response += f"   • Tamaño de índice: {performance.get('index_size', 'N/A')}\n"
        
        log(f"MCP Server: Estadísticas de base de datos vectorial obtenidas exitosamente")
        return response
        
    except Exception as e:
        log(f"MCP Server: Error obteniendo estadísticas de base de datos vectorial: {e}")
        return f"❌ **Error obteniendo estadísticas de base de datos vectorial:** {str(e)}"

def reindex_vector_database(profile: str = 'auto') -> str:
    """
    Reindexa la base de datos vectorial con una configuración optimizada.
    Esta herramienta recrea los índices con parámetros optimizados para el tamaño actual.
    
    Args:
        profile: Perfil de configuración ('small', 'medium', 'large', 'auto')
                 'auto' detecta automáticamente el perfil óptimo
    
    Use esta herramienta cuando:
    - Cambias el perfil de configuración
    - Las búsquedas son muy lentas
    - Quieres optimizar para un tamaño específico de base de datos
    - Hay problemas de rendimiento persistentes
    
    ⚠️ **Nota:** Este proceso puede tomar tiempo dependiendo del tamaño de la base de datos.
    
    Returns:
        Información sobre el proceso de reindexado
    """
    log(f"MCP Server: Reindexando base de datos vectorial con perfil '{profile}'...")
    
    try:
        result = reindex_vector_store(profile=profile)
        
        if result["status"] == "success":
            response = f"✅ **Base de datos vectorial reindexada exitosamente**\n\n"
            response += f"📊 **Perfil aplicado:** {result.get('profile', 'N/A')}\n"
            response += f"📊 **Documentos procesados:** {result.get('documents_processed', 'N/A')}\n"
            response += f"⏱️ **Tiempo de reindexado:** {result.get('reindexing_time', 'N/A')}\n"
            
            response += f"\n🚀 **Beneficios del reindexado:**\n"
            response += f"   • Índices optimizados para el tamaño actual\n"
            response += f"   • Búsquedas más rápidas y precisas\n"
            response += f"   • Mejor distribución de datos\n"
            
        else:
            response = f"❌ **Error reindexando base de datos:** {result.get('message', 'Error desconocido')}"
            
        return response
        
    except Exception as e:
        log(f"MCP Server: Error reindexando base de datos vectorial: {e}")
        return f"❌ **Error reindexando base de datos vectorial:** {str(e)}" 