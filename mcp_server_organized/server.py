"""
Servidor MCP Organizado - Main Server
=====================================

Este es el servidor principal MCP con arquitectura modular.
Mantiene toda la funcionalidad existente pero con mejor organización.
Ahora incluye soporte para modelos estructurados (DocumentModel y MetadataModel).
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown
from urllib.parse import urlparse

# Añadir el directorio src al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Importaciones de utilidades
from utils.logger import log, log_mcp_server
from utils.config import Config

# Importaciones del núcleo RAG (mantenemos la funcionalidad existente)
from rag_core import (
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

# Importar modelos estructurados
try:
    from models import DocumentModel, MetadataModel
    MODELS_AVAILABLE = True
    log_mcp_server("✅ Modelos estructurados (DocumentModel, MetadataModel) disponibles")
except ImportError as e:
    MODELS_AVAILABLE = False
    log_mcp_server(f"⚠️ Modelos estructurados no disponibles: {e}")

# --- Inicialización del Servidor y Configuración ---
load_dotenv()
mcp = FastMCP(Config.SERVER_NAME)

# El estado ahora incluye información sobre modelos estructurados
rag_state = {
    "models_available": MODELS_AVAILABLE,
    "structured_processing": MODELS_AVAILABLE,
    "document_models": [],  # Lista de DocumentModel procesados
    "metadata_cache": {}    # Cache de MetadataModel por documento
}

# Inicializamos el conversor de MarkItDown una sola vez (para URLs)
md_converter = MarkItDown()

def warm_up_rag_system():
    """
    Precarga los componentes pesados del sistema RAG para evitar demoras
    y conflictos en la primera llamada de una herramienta.
    """
    if "warmed_up" in rag_state:
        return
    
    log_mcp_server("Calentando sistema RAG...")
    log_mcp_server("Precargando modelo de embedding en memoria...")
    
    # Esta llamada fuerza la carga del modelo de embedding
    get_vector_store()
    
    rag_state["warmed_up"] = True
    log_mcp_server("Sistema RAG caliente y listo.")

def ensure_converted_docs_directory():
    """Asegura que existe la carpeta para los documentos convertidos."""
    Config.ensure_directories()
    if not os.path.exists(Config.CONVERTED_DOCS_DIR):
        os.makedirs(Config.CONVERTED_DOCS_DIR)
        log_mcp_server(f"Creada carpeta para documentos convertidos: {Config.CONVERTED_DOCS_DIR}")

def save_processed_copy(file_path: str, processed_content: str, processing_method: str = "unstructured") -> str:
    """
    Guarda una copia del documento procesado en formato Markdown.
    
    Args:
        file_path: Ruta original del archivo
        processed_content: Contenido procesado
        processing_method: Método de procesamiento usado
    
    Returns:
        Ruta del archivo Markdown guardado
    """
    ensure_converted_docs_directory()
    
    # Obtener el nombre del archivo original sin extensión
    original_filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(original_filename)[0]
    
    # Crear el nombre del archivo Markdown con información del método
    md_filename = f"{name_without_ext}_{processing_method}.md"
    md_filepath = os.path.join(Config.CONVERTED_DOCS_DIR, md_filename)
    
    # Guardar el contenido en el archivo Markdown
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        log_mcp_server(f"Copia procesada guardada en: {md_filepath}")
        return md_filepath
    except Exception as e:
        log_mcp_server(f"Advertencia: No se pudo guardar copia procesada: {e}")
        return ""

def initialize_rag():
    """
    Inicializa todos los componentes del sistema RAG usando el núcleo.
    """
    if "initialized" in rag_state:
        return

    log_mcp_server("Inicializando sistema RAG vía núcleo...")
    
    # Obtenemos la base de datos y la cadena QA desde nuestro núcleo
    vector_store = get_vector_store()
    qa_chain = get_qa_chain(vector_store)
    
    rag_state["vector_store"] = vector_store
    rag_state["qa_chain"] = qa_chain
    rag_state["initialized"] = True
    
    # Información sobre el estado de los modelos
    if MODELS_AVAILABLE:
        log_mcp_server("✅ Sistema RAG inicializado con soporte para modelos estructurados")
        log_mcp_server("🧠 DocumentModel y MetadataModel disponibles para procesamiento avanzado")
    else:
        log_mcp_server("⚠️ Sistema RAG inicializado sin modelos estructurados (usando diccionarios)")
    
    log_mcp_server("Sistema RAG inicializado exitosamente.")

# --- Inicialización automática del sistema RAG ---
log_mcp_server("Inicializando sistema RAG automáticamente...")
initialize_rag()
warm_up_rag_system()
log_mcp_server("Sistema RAG inicializado y listo para usar.")

# --- Configurar las herramientas modulares DESPUÉS de inicializar RAG ---
from tools import configure_rag_state, ALL_TOOLS

# Configurar el estado RAG en todos los módulos de herramientas
configure_rag_state(
    rag_state=rag_state, 
    md_converter=md_converter,
    initialize_rag_func=initialize_rag,
    save_processed_copy_func=save_processed_copy
)

# --- Definir las herramientas MCP directamente en el servidor ---
@mcp.tool()
def learn_text(text: str, source_name: str = "manual_input") -> str:
    """
    Adds a new piece of text to the RAG knowledge base for future reference.
    Use this when you want to teach the AI new information that it should remember.
    
    Examples of when to use:
    - Adding facts, definitions, or explanations
    - Storing important information from conversations
    - Saving research findings or notes
    - Adding context about specific topics

    Args:
        text: The text content to be learned and stored in the knowledge base.
        source_name: A descriptive name for the source (e.g., "user_notes", "research_paper", "conversation_summary").
    """
    from tools.document_tools import learn_text as learn_text_logic
    return learn_text_logic(text, source_name)

@mcp.tool()
def learn_document(file_path: str) -> str:
    """
    Reads and processes a document file using advanced Unstructured processing with real semantic chunking, and adds it to the knowledge base.
    Use this when you want to teach the AI from document files with intelligent processing.
    
    Supported file types: PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML, ODT, ODP, ODS, RTF, 
    images (PNG, JPG, TIFF, BMP with OCR), emails (EML, MSG), and more than 25 formats total.
    
    Advanced features:
    - REAL semantic chunking based on document structure (titles, sections, lists)
    - Intelligent document structure preservation (titles, lists, tables)
    - Automatic noise removal (headers, footers, irrelevant content)
    - Structural metadata extraction
    - Robust fallback system for any document type
    - Enhanced context preservation through semantic boundaries
    
    Examples of when to use:
    - Processing research papers or articles with complex layouts
    - Adding content from reports or manuals with tables and lists
    - Importing data from spreadsheets with formatting
    - Converting presentations to searchable knowledge
    - Processing scanned documents with OCR
    
    The document will be intelligently processed with REAL semantic chunking and stored with enhanced metadata.
    A copy of the processed document is saved for verification.

    Args:
        file_path: The absolute or relative path to the document file to process.
    """
    from tools.document_tools import learn_document as learn_document_logic
    return learn_document_logic(file_path)

@mcp.tool()
def learn_from_url(url: str) -> str:
    """
    Procesa contenido de una URL (página web o video de YouTube) y lo añade a la base de conocimientos.
    Use this when you want to teach the AI from web content without downloading files.
    
    Supported URL types:
    - Web pages (HTML content)
    - YouTube videos (transcripts)
    - Any URL that MarkItDown can process
    - Direct file downloads (PDF, DOCX, etc.) - will use enhanced Unstructured processing
    
    Examples of when to use:
    - Adding content from news articles or blog posts
    - Processing YouTube video transcripts
    - Importing information from web pages
    - Converting web content to searchable knowledge
    - Processing documents directly from URLs
    
    The content will be intelligently processed and stored with enhanced metadata.
    A copy of the processed content is saved for verification.

    Args:
        url: The URL of the web page or video to process.
    """
    from tools.document_tools import learn_from_url as learn_from_url_logic
    return learn_from_url_logic(url)

@mcp.tool()
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
    from tools.search_tools import ask_rag as ask_rag_logic
    return ask_rag_logic(query)

@mcp.tool()
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
    from tools.search_tools import ask_rag_filtered as ask_rag_filtered_logic
    return ask_rag_filtered_logic(query, file_type, min_tables, min_titles, processing_method)

@mcp.tool()
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
    from tools.utility_tools import get_knowledge_base_stats as get_knowledge_base_stats_logic
    return get_knowledge_base_stats_logic()

@mcp.tool()
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
    from tools.utility_tools import get_embedding_cache_stats as get_embedding_cache_stats_logic
    return get_embedding_cache_stats_logic()

@mcp.tool()
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
    from tools.utility_tools import clear_embedding_cache_tool as clear_embedding_cache_tool_logic
    return clear_embedding_cache_tool_logic()

@mcp.tool()
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
    from tools.utility_tools import optimize_vector_database as optimize_vector_database_logic
    return optimize_vector_database_logic()

@mcp.tool()
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
    from tools.utility_tools import get_vector_database_stats as get_vector_database_stats_logic
    return get_vector_database_stats_logic()

@mcp.tool()
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
    from tools.utility_tools import reindex_vector_database as reindex_vector_database_logic
    return reindex_vector_database_logic(profile)

# --- Punto de Entrada para Correr el Servidor ---
if __name__ == "__main__":
    log_mcp_server("Iniciando servidor MCP RAG organizado...")
    warm_up_rag_system()  # Calentamos el sistema al arrancar
    mcp.run(transport='stdio') 