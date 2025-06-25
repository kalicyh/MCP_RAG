"""
Herramientas de Búsqueda para MCP
===============================

Este módulo contiene las herramientas relacionadas con la búsqueda y consulta en la base de conocimientos.
Migradas desde rag_server.py para una arquitectura modular.

NOTA: Estas funciones están diseñadas para ser decoradas con @mcp.tool() en el servidor principal.
"""

from rag_core import (
    get_qa_chain,
    create_metadata_filter
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

def process_document_metadata(metadata: dict) -> dict:
    """
    Procesa metadatos de documentos usando MetadataModel si está disponible.
    
    Args:
        metadata: Diccionario de metadatos del documento
        
    Returns:
        Diccionario con información procesada del documento
    """
    if not metadata:
        return {"source": "Fuente desconocida"}
    
    # Si MetadataModel está disponible, intentar crear un modelo estructurado
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
            log(f"MCP Server Warning: Error procesando metadatos con MetadataModel: {e}")
    
    # Fallback a procesamiento directo de diccionario
    return {
        "source": metadata.get("source", "Fuente desconocida"),
        "file_path": metadata.get("file_path"),
        "file_type": metadata.get("file_type"),
        "processing_method": metadata.get("processing_method"),
        "structural_info": metadata.get("structural_info", {}),
        "titles_count": metadata.get("structural_titles_count", 0),
        "tables_count": metadata.get("structural_tables_count", 0),
        "lists_count": metadata.get("structural_lists_count", 0),
        "total_elements": metadata.get("structural_total_elements", 0),
        "is_rich_content": False,  # No podemos determinar esto sin el modelo
        "chunking_method": metadata.get("chunking_method", "unknown"),
        "avg_chunk_size": metadata.get("avg_chunk_size", 0)
    }

def ask_rag(query: str) -> str:
    """
    Asks a question to the RAG knowledge base and returns an answer based on the stored information.
    Use this when you want to get information from the knowledge base that has been previously learned.
    
    Examples of when to use:
    - Asking about specific topics or concepts
    - Requesting explanations or definitions
    - Seeking information from processed documents
    - Getting answers based on learned text or documents
    
    The system will search through all stored information and provide the most relevant answer.

    Args:
        query: The question or query to ask the knowledge base.
    """
    log(f"MCP Server: Procesando pregunta: {query}")
    initialize_rag()
    
    try:
        # Usar la cadena QA estándar (sin filtros)
        qa_chain = get_qa_chain(rag_state["vector_store"])
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])
        
        # Verificar si realmente tenemos información relevante
        if not source_documents:
            # No hay fuentes - el LLM probablemente está alucinando
            enhanced_answer = f"🤖 **Respuesta:**\n\n❌ **No se encontró información relevante en la base de conocimientos para responder tu pregunta.**\n\n"
            enhanced_answer += "💡 **Sugerencias:**\n"
            enhanced_answer += "• Verifica que hayas cargado documentos relacionados con tu pregunta\n"
            enhanced_answer += "• Intenta reformular tu pregunta con términos más específicos\n"
            enhanced_answer += "• Usa `get_knowledge_base_stats()` para ver qué información está disponible\n"
            enhanced_answer += "• Considera cargar más documentos sobre el tema que te interesa\n\n"
            enhanced_answer += "⚠️ **Nota:** El sistema solo puede responder basándose en la información que ha sido previamente cargada en la base de conocimientos."
            
            log(f"MCP Server: No se encontraron fuentes relevantes para la pregunta")
            return enhanced_answer
        
        # Verificar si la respuesta parece ser una alucinación
        # Si no hay fuentes pero hay respuesta, es probable una alucinación
        if len(source_documents) == 0 and answer.strip():
            enhanced_answer = f"🤖 **Respuesta:**\n\n❌ **No se encontró información específica en la base de conocimientos para responder tu pregunta.**\n\n"
            enhanced_answer += "💡 **Sugerencias:**\n"
            enhanced_answer += "• Verifica que hayas cargado documentos relacionados con tu pregunta\n"
            enhanced_answer += "• Intenta reformular tu pregunta con términos más específicos\n"
            enhanced_answer += "• Usa `get_knowledge_base_stats()` para ver qué información está disponible\n\n"
            enhanced_answer += "⚠️ **Nota:** El sistema solo puede responder basándose en la información que ha sido previamente cargada en la base de conocimientos."
            
            log(f"MCP Server: Respuesta detectada como posible alucinación (sin fuentes)")
            return enhanced_answer
        
        # Si tenemos fuentes, construir respuesta normal
        enhanced_answer = f"🤖 **Respuesta:**\n\n{answer}\n"
        
        # Añadir información de fuentes con más detalles usando modelos estructurados
        if source_documents:
            enhanced_answer += "📚 **Fuentes de información utilizadas:**\n\n"
            for i, doc in enumerate(source_documents, 1):
                raw_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                
                # Procesar metadatos usando modelos estructurados
                doc_info = process_document_metadata(raw_metadata)
                
                # --- Mejoramos la información de la fuente ---
                source_info = f"   {i}. **{doc_info['source']}**"
                
                # Añadir ruta completa si es un documento
                if doc_info['file_path']:
                    source_info += f"\n      - **Ruta:** `{doc_info['file_path']}`"
                
                # Añadir tipo de archivo si está disponible
                if doc_info['file_type']:
                    source_info += f"\n      - **Tipo:** {doc_info['file_type'].upper()}"
                
                # Añadir método de procesamiento si está disponible
                if doc_info['processing_method']:
                    method_display = doc_info['processing_method'].replace('_', ' ').title()
                    source_info += f"\n      - **Procesamiento:** {method_display}"
                
                # Añadir información estructural usando datos del modelo
                if doc_info['total_elements'] > 0:
                    source_info += f"\n      - **Estructura:** {doc_info['total_elements']} elementos"
                    
                    structural_details = []
                    if doc_info['titles_count'] > 0:
                        structural_details.append(f"{doc_info['titles_count']} títulos")
                    if doc_info['tables_count'] > 0:
                        structural_details.append(f"{doc_info['tables_count']} tablas")
                    if doc_info['lists_count'] > 0:
                        structural_details.append(f"{doc_info['lists_count']} listas")
                    
                    if structural_details:
                        source_info += f" ({', '.join(structural_details)})"
                
                # Añadir información de chunking si está disponible
                if doc_info['chunking_method'] and doc_info['chunking_method'] != "unknown":
                    chunking_display = doc_info['chunking_method'].replace('_', ' ').title()
                    source_info += f"\n      - **Chunking:** {chunking_display}"
                
                # Añadir indicador de contenido rico si está disponible
                if doc_info.get('is_rich_content', False):
                    source_info += f"\n      - **Calidad:** Contenido rico en estructura"
                
                enhanced_answer += source_info + "\n\n"
        
        # Añadir información sobre la calidad de la respuesta
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ **Alta confianza:** Respuesta basada en múltiples fuentes"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ **Confianza media:** Respuesta basada en 2 fuentes"
        else:
            enhanced_answer += "\n⚠️ **Confianza limitada:** Respuesta basada en 1 fuente"
        
        # Añadir información sobre el procesamiento usando modelos estructurados
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
            enhanced_answer += f"\n🧠 **Procesamiento inteligente:** {len(enhanced_docs)} fuentes procesadas con Unstructured (preservación de estructura)"
        
        if rich_content_docs:
            enhanced_answer += f"\n📊 **Contenido estructurado:** {len(rich_content_docs)} fuentes con estructura rica (títulos, tablas, listas)"
        
        log(f"MCP Server: Respuesta generada exitosamente con {len(source_documents)} fuentes")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP Server: Error procesando pregunta: {e}")
        return f"❌ **Error al procesar la pregunta:** {e}\n\n💡 **Sugerencias:**\n- Verifica que el sistema RAG esté correctamente inicializado\n- Intenta reformular tu pregunta\n- Si el problema persiste, reinicia el servidor"

def ask_rag_filtered(query: str, file_type: str = None, min_tables: int = None, min_titles: int = None, processing_method: str = None) -> str:
    """
    Asks a question to the RAG knowledge base with specific filters to focus the search.
    Use this when you want to get information from specific types of documents or documents with certain characteristics.
    
    Examples of when to use:
    - Searching only in PDF documents: file_type=".pdf"
    - Looking for documents with tables: min_tables=1
    - Finding well-structured documents: min_titles=5
    - Searching in enhanced processed documents: processing_method="unstructured_enhanced"
    
    This provides more targeted and relevant results by filtering the search scope.

    Args:
        query: The question or query to ask the knowledge base.
        file_type: Filter by file type (e.g., ".pdf", ".docx", ".txt")
        min_tables: Minimum number of tables the document must have
        min_titles: Minimum number of titles the document must have
        processing_method: Filter by processing method (e.g., "unstructured_enhanced", "markitdown")
    """
    log(f"MCP Server: Procesando pregunta con filtros: {query}")
    log(f"MCP Server: Filtros aplicados - Tipo: {file_type}, Tablas: {min_tables}, Títulos: {min_titles}, Método: {processing_method}")
    initialize_rag()
    
    try:
        # Crear filtros de metadatos
        metadata_filter = create_metadata_filter(
            file_type=file_type,
            processing_method=processing_method,
            min_tables=min_tables,
            min_titles=min_titles
        )
        
        # Usar la cadena QA con filtros
        qa_chain = get_qa_chain(rag_state["vector_store"], metadata_filter)
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "")
        source_documents = response.get("source_documents", [])
        
        # Verificar si realmente tenemos información relevante con los filtros
        if not source_documents:
            # No hay fuentes que cumplan con los filtros
            enhanced_answer = f"🔍 **Respuesta (con filtros aplicados):**\n\n❌ **No se encontró información relevante en la base de conocimientos que cumpla con los filtros especificados.**\n\n"
            
            # Mostrar filtros aplicados
            if metadata_filter:
                enhanced_answer += "📋 **Filtros aplicados:**\n"
                for key, value in metadata_filter.items():
                    if key == "file_type":
                        enhanced_answer += f"   • Tipo de archivo: {value}\n"
                    elif key == "processing_method":
                        enhanced_answer += f"   • Método de procesamiento: {value.replace('_', ' ').title()}\n"
                    elif key == "structural_tables_count":
                        enhanced_answer += f"   • Mínimo de tablas: {value['$gte']}\n"
                    elif key == "structural_titles_count":
                        enhanced_answer += f"   • Mínimo de títulos: {value['$gte']}\n"
                    else:
                        enhanced_answer += f"   • {key}: {value}\n"
            
            enhanced_answer += "\n💡 **Sugerencias:**\n"
            enhanced_answer += "• Intenta relajar los filtros para obtener más resultados\n"
            enhanced_answer += "• Verifica que tengas documentos que cumplan con los criterios especificados\n"
            enhanced_answer += "• Usa `get_knowledge_base_stats()` para ver qué tipos de documentos están disponibles\n"
            enhanced_answer += "• Considera cargar más documentos que cumplan con los filtros\n\n"
            enhanced_answer += "⚠️ **Nota:** Los filtros pueden ser muy restrictivos. Intenta con filtros más amplios si no obtienes resultados."
            
            log(f"MCP Server: No se encontraron fuentes que cumplan con los filtros especificados")
            return enhanced_answer
        
        # Si tenemos fuentes, construir respuesta normal
        enhanced_answer = f"🔍 **Respuesta (con filtros aplicados):**\n\n{answer}\n"
        
        # Mostrar filtros aplicados
        if metadata_filter:
            enhanced_answer += "\n📋 **Filtros aplicados:**\n"
            for key, value in metadata_filter.items():
                if key == "file_type":
                    enhanced_answer += f"   • Tipo de archivo: {value}\n"
                elif key == "processing_method":
                    enhanced_answer += f"   • Método de procesamiento: {value.replace('_', ' ').title()}\n"
                elif key == "structural_tables_count":
                    enhanced_answer += f"   • Mínimo de tablas: {value['$gte']}\n"
                elif key == "structural_titles_count":
                    enhanced_answer += f"   • Mínimo de títulos: {value['$gte']}\n"
                else:
                    enhanced_answer += f"   • {key}: {value}\n"
        
        # Añadir información de fuentes
        if source_documents:
            enhanced_answer += "\n📚 **Fuentes de información utilizadas:**\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "Fuente desconocida")
                
                source_info = f"   {i}. **{source_name}**"
                
                # Añadir información adicional de la fuente
                file_path = metadata.get("file_path")
                if file_path:
                    source_info += f"\n      - **Ruta:** `{file_path}`"
                
                file_type = metadata.get("file_type")
                if file_type:
                    source_info += f"\n      - **Tipo:** {file_type.upper()}"
                
                processing_method = metadata.get("processing_method")
                if processing_method:
                    method_display = processing_method.replace('_', ' ').title()
                    source_info += f"\n      - **Procesamiento:** {method_display}"
                
                # Añadir información estructural
                structural_info = metadata.get("structural_info")
                if structural_info:
                    source_info += f"\n      - **Estructura:** {structural_info.get('total_elements', 'N/A')} elementos"
                    titles_count = structural_info.get('titles_count', 0)
                    tables_count = structural_info.get('tables_count', 0)
                    lists_count = structural_info.get('lists_count', 0)
                    if titles_count > 0 or tables_count > 0 or lists_count > 0:
                        structure_details = []
                        if titles_count > 0:
                            structure_details.append(f"{titles_count} títulos")
                        if tables_count > 0:
                            structure_details.append(f"{tables_count} tablas")
                        if lists_count > 0:
                            structure_details.append(f"{lists_count} listas")
                        source_info += f" ({', '.join(structure_details)})"
                
                enhanced_answer += source_info + "\n\n"
        
        # Añadir información sobre la calidad de la respuesta
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ **Alta confianza:** Respuesta basada en múltiples fuentes filtradas"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ **Confianza media:** Respuesta basada en 2 fuentes filtradas"
        else:
            enhanced_answer += "\n⚠️ **Confianza limitada:** Respuesta basada en 1 fuente filtrada"
        
        log(f"MCP Server: Respuesta filtrada generada exitosamente con {len(source_documents)} fuentes")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP Server: Error procesando pregunta filtrada: {e}")
        return f"❌ **Error al procesar la pregunta filtrada:** {e}\n\n💡 **Sugerencias:**\n- Verifica que el sistema RAG esté correctamente inicializado\n- Intenta con filtros menos restrictivos\n- Si el problema persiste, reinicia el servidor" 