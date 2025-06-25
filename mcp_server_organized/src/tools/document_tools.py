"""
Herramientas de Documentos para MCP
==================================

Este módulo contiene las herramientas relacionadas con el procesamiento de documentos.
Migradas desde rag_server.py para una arquitectura modular.

NOTA: Estas funciones están diseñadas para ser decoradas con @mcp.tool() en el servidor principal.
"""

import os
import tempfile
import requests
from datetime import datetime
from urllib.parse import urlparse
from rag_core import (
    add_text_to_knowledge_base,
    add_text_to_knowledge_base_enhanced,
    load_document_with_elements
)
from utils.logger import log
from models import DocumentModel, MetadataModel

# Variables globales que deben estar disponibles en el servidor
rag_state = {}
md_converter = None
initialize_rag_func = None
save_processed_copy_func = None

def set_rag_state(state):
    """Establece el estado RAG global."""
    global rag_state
    rag_state = state

def set_md_converter(converter):
    """Establece el conversor MarkItDown global."""
    global md_converter
    md_converter = converter

def set_initialize_rag_func(func):
    """Establece la función de inicialización RAG."""
    global initialize_rag_func
    initialize_rag_func = func

def set_save_processed_copy_func(func):
    """Establece la función de guardar copia procesada."""
    global save_processed_copy_func
    save_processed_copy_func = func

def initialize_rag():
    """Inicializa el sistema RAG."""
    if initialize_rag_func:
        initialize_rag_func()
    elif "initialized" in rag_state:
        return
    # Esta función debe ser implementada en el servidor principal
    pass

def save_processed_copy(file_path: str, processed_content: str, processing_method: str = "unstructured") -> str:
    """Guarda una copia procesada del documento."""
    if save_processed_copy_func:
        return save_processed_copy_func(file_path, processed_content, processing_method)
    return ""

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
    log(f"MCP Server: Procesando texto de {len(text)} caracteres de la fuente: {source_name}")
    initialize_rag()
    
    try:
        # Crear metadatos estructurados usando MetadataModel
        metadata_model = MetadataModel(
            source=source_name,
            input_type="manual_text",
            processed_date=datetime.now(),
            processing_method="manual_input",
            chunking_method="standard",
            chunk_count=1,
            avg_chunk_size=len(text)
        )
        
        # Convertir a diccionario para compatibilidad con el núcleo
        source_metadata = metadata_model.to_dict()
        
        # Usamos la función del núcleo para añadir el texto con metadatos
        add_text_to_knowledge_base(text, rag_state["vector_store"], source_metadata)
        log(f"MCP Server: Texto añadido exitosamente a la base de conocimientos")
        return f"Texto añadido exitosamente a la base de conocimientos. Fragmento: '{text[:70]}...' (Fuente: {source_name})"
    except Exception as e:
        log(f"MCP Server: Error al añadir texto: {e}")
        return f"Error al añadir texto: {e}"

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
    log(f"MCP Server: Iniciando procesamiento avanzado de documento: {file_path}")
    log(f"MCP Server: DEBUG - Ruta recibida: {repr(file_path)}")
    log(f"MCP Server: DEBUG - Verificando existencia de ruta absoluta: {os.path.abspath(file_path)}")
    initialize_rag()  # Asegura que el sistema RAG esté listo
    
    try:
        if not os.path.exists(file_path):
            log(f"MCP Server: Archivo no encontrado en la ruta: {file_path}")
            return f"Error: Archivo no encontrado en '{file_path}'"

        log(f"MCP Server: Procesando documento con sistema Unstructured avanzado...")
        
        # Usar el nuevo sistema de procesamiento con elementos estructurales
        processed_content, raw_metadata, structural_elements = load_document_with_elements(file_path)

        if not processed_content or processed_content.isspace():
            log(f"MCP Server: Advertencia: Documento procesado pero no se pudo extraer contenido: {file_path}")
            return f"Advertencia: El documento '{file_path}' fue procesado, pero no se pudo extraer contenido de texto."

        log(f"MCP Server: Documento procesado exitosamente ({len(processed_content)} caracteres)")
        
        # Crear modelo de documento estructurado
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # Extraer información estructural
        structural_info = raw_metadata.get("structural_info", {})
        titles_count = structural_info.get("titles_count", 0)
        tables_count = structural_info.get("tables_count", 0)
        lists_count = structural_info.get("lists_count", 0)
        total_elements = structural_info.get("total_elements", 0)
        
        # Crear DocumentModel
        document_model = DocumentModel(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            content=processed_content,  # Contenido original (mismo que procesado en este caso)
            processed_content=processed_content,
            processing_method=raw_metadata.get("processing_method", "unstructured_enhanced"),
            processing_date=datetime.now(),
            structural_elements=structural_elements or [],
            total_elements=total_elements,
            titles_count=titles_count,
            tables_count=tables_count,
            lists_count=lists_count,
            chunk_count=0  # Se calculará después del chunking
        )
        
        # Crear MetadataModel
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
        
        # Validar el documento
        if not document_model.is_valid():
            log(f"MCP Server: Error: Documento no válido según el modelo")
            return f"Error: El documento procesado no cumple con los criterios de validez"
        
        log(f"MCP Server: Modelos de documento y metadatos creados exitosamente")
        log(f"MCP Server: Resumen del documento: {document_model.get_summary()}")
        log(f"MCP Server: Resumen de metadatos: {metadata_model.get_summary()}")
        
        # Guardar copia procesada
        log(f"MCP Server: Guardando copia procesada...")
        saved_copy_path = save_processed_copy(file_path, processed_content, document_model.processing_method)
        
        # Añadir contenido a la base de conocimientos con chunking semántico real
        log(f"MCP Server: Añadiendo contenido a la base de conocimientos con metadatos estructurales...")
        
        # Convertir metadatos a diccionario para compatibilidad con el núcleo
        enhanced_metadata = metadata_model.to_dict()
        
        # Usar la función mejorada con elementos estructurales para chunking semántico real
        add_text_to_knowledge_base_enhanced(
            processed_content, 
            rag_state["vector_store"], 
            enhanced_metadata, 
            use_semantic_chunking=True,
            structural_elements=structural_elements
        )
        
        log(f"MCP Server: Proceso completado - Documento procesado con éxito")
        
        # Información sobre el chunking usado
        chunking_info = ""
        if structural_elements and len(structural_elements) > 1:
            chunking_info = f"🧠 **Chunking Semántico Avanzado** con {len(structural_elements)} elementos estructurales"
        elif metadata_model.is_rich_content():
            chunking_info = f"📊 **Chunking Semántico Mejorado** basado en metadatos estructurales"
        else:
            chunking_info = f"📝 **Chunking Tradicional** optimizado"
        
        return f"""✅ **Documento procesado exitosamente**
📄 **Archivo:** {document_model.file_name}
📋 **Tipo:** {document_model.file_type.upper()}
🔧 **Método:** {document_model.processing_method}
{chunking_info}
📊 **Caracteres procesados:** {len(processed_content):,}
📈 **Estructura:** {titles_count} títulos, {tables_count} tablas, {lists_count} listas
💾 **Copia guardada:** {saved_copy_path if saved_copy_path else "No disponible"}
✅ **Validación:** Documento procesado con modelos estructurados"""

    except Exception as e:
        log(f"MCP Server: Error procesando documento '{file_path}': {e}")
        return f"Error procesando documento: {e}"

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
    log(f"MCP Server: Iniciando procesamiento de URL: {url}")
    initialize_rag()
    
    try:
        # Verificar si es una URL de descarga directa de archivo
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1].lower()
        
        # Lista de extensiones que soportan procesamiento mejorado
        enhanced_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', 
                              '.txt', '.html', '.htm', '.csv', '.json', '.xml', '.rtf',
                              '.odt', '.odp', '.ods', '.md', '.yaml', '.yml']
        
        if file_extension in enhanced_extensions:
            log(f"MCP Server: Detectado archivo descargable ({file_extension}), usando procesamiento mejorado...")
            
            # Configurar timeout para la descarga
            timeout_seconds = 30
            
            # Descargar el archivo con timeout
            log(f"MCP Server: Descargando archivo con timeout de {timeout_seconds} segundos...")
            response = requests.get(url, stream=True, timeout=timeout_seconds)
            response.raise_for_status()
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            log(f"MCP Server: Archivo descargado temporalmente en: {temp_file_path}")
            
            try:
                # Usar el procesamiento mejorado con timeout
                log(f"MCP Server: Iniciando procesamiento con Unstructured (puede tomar varios minutos para PDFs grandes)...")
                
                # Para PDFs, usar configuración más rápida para evitar colgadas
                if file_extension == '.pdf':
                    log(f"MCP Server: PDF detectado, usando configuración optimizada para evitar timeouts...")
                    
                    # Opción 1: Intentar con PyPDF2 directamente (más rápido para Cursor)
                    log(f"MCP Server: Intentando con PyPDF2 directo para mayor velocidad...")
                    try:
                        import PyPDF2
                        with open(temp_file_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            processed_content = ""
                            for page_num, page in enumerate(pdf_reader.pages):
                                page_text = page.extract_text()
                                if page_text:
                                    processed_content += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
                            
                            if processed_content.strip():
                                log(f"MCP Server: PyPDF2 directo exitoso, {len(processed_content)} caracteres extraídos")
                                metadata = {
                                    "source": os.path.basename(temp_file_path),
                                    "file_path": temp_file_path,
                                    "file_type": ".pdf",
                                    "processed_date": datetime.now().isoformat(),
                                    "processing_method": "pypdf2_direct",
                                    "structural_info": {
                                        "total_elements": len(pdf_reader.pages),
                                        "titles_count": 0,
                                        "tables_count": 0,
                                        "lists_count": 0,
                                        "narrative_blocks": len(pdf_reader.pages),
                                        "other_elements": 0,
                                        "total_text_length": len(processed_content),
                                        "avg_element_length": len(processed_content) / len(pdf_reader.pages) if pdf_reader.pages else 0
                                    }
                                }
                                log(f"MCP Server: Procesamiento con PyPDF2 directo completado")
                            else:
                                raise Exception("No se pudo extraer contenido con PyPDF2")
                    except Exception as e:
                        log(f"MCP Server: PyPDF2 falló, usando Unstructured: {e}")
                        # Continuar con Unstructured
                        processed_content, metadata, structural_elements = load_document_with_elements(temp_file_path)
                else:
                    # Para otros tipos de archivo, usar Unstructured directamente
                    processed_content, metadata, structural_elements = load_document_with_elements(temp_file_path)
                
                log(f"MCP Server: Archivo descargado y procesado exitosamente ({len(processed_content)} caracteres)")
                
                # Guardar copia procesada
                log(f"MCP Server: Guardando copia procesada...")
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
                    log(f"MCP Server: Copia procesada guardada en: {processed_filepath}")
                except Exception as e:
                    log(f"MCP Server Advertencia: No se pudo guardar copia procesada: {e}")
                    processed_filepath = ""
                
                # Enriquecer metadatos
                enhanced_metadata = metadata.copy()
                enhanced_metadata.update({
                    "source": url,
                    "domain": parsed_url.netloc,
                    "input_type": "url_download",
                    "converted_to_md": processed_filepath if processed_filepath else "No",
                    "server_processed_date": datetime.now().isoformat()
                })
                
                # Usar procesamiento mejorado
                log(f"MCP Server: Añadiendo contenido a la base de conocimientos...")
                add_text_to_knowledge_base_enhanced(
                    processed_content, 
                    rag_state["vector_store"], 
                    enhanced_metadata, 
                    use_semantic_chunking=True,
                    structural_elements=structural_elements if 'structural_elements' in locals() else None
                )
                
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_file_path)
                    log(f"MCP Server: Archivo temporal eliminado: {temp_file_path}")
                except Exception as e:
                    log(f"MCP Server Advertencia: No se pudo eliminar archivo temporal: {e}")
                
                log(f"MCP Server: Proceso completado - URL procesada con éxito")
                
                # Preparar respuesta informativa
                file_name = os.path.basename(parsed_url.path) if parsed_url.path != '/' else parsed_url.netloc
                file_type = metadata.get("file_type", file_extension)
                processing_method = metadata.get("processing_method", "unstructured_enhanced")
                
                return f"""✅ **URL procesada exitosamente**
🌐 **URL:** {url}
📄 **Archivo:** {file_name}
📋 **Tipo:** {file_type.upper()}
🔧 **Método:** {processing_method}
📊 **Caracteres procesados:** {len(processed_content):,}
💾 **Copia guardada:** {processed_filepath if processed_filepath else "No disponible"}"""
                
            except Exception as e:
                # Limpiar archivo temporal en caso de error
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                raise e
        else:
            # Procesar como página web con MarkItDown
            log(f"MCP Server: Procesando como página web con MarkItDown...")
            
            if md_converter is None:
                return "Error: MarkItDown converter no está disponible"
            
            try:
                # Procesar la URL con MarkItDown
                processed_content = md_converter.convert(url)
                
                if not processed_content or processed_content.isspace():
                    log(f"MCP Server: Advertencia: URL procesada pero no se pudo extraer contenido: {url}")
                    return f"Advertencia: La URL '{url}' fue procesada, pero no se pudo extraer contenido de texto."
                
                log(f"MCP Server: URL procesada exitosamente ({len(processed_content)} caracteres)")
                
                # Guardar copia procesada
                log(f"MCP Server: Guardando copia procesada...")
                domain = parsed_url.netloc.replace('.', '_')
                path = parsed_url.path.replace('/', '_').replace('.', '_')
                if not path or path == '_':
                    path = 'homepage'
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{domain}_{path}_{timestamp}_markitdown.md"
                processed_filepath = os.path.join("./data/documents", filename)
                
                try:
                    os.makedirs("./data/documents", exist_ok=True)
                    with open(processed_filepath, 'w', encoding='utf-8') as f:
                        f.write(processed_content)
                    log(f"MCP Server: Copia procesada guardada en: {processed_filepath}")
                except Exception as e:
                    log(f"MCP Server Advertencia: No se pudo guardar copia procesada: {e}")
                    processed_filepath = ""
                
                # Crear metadatos
                metadata = {
                    "source": url,
                    "domain": parsed_url.netloc,
                    "input_type": "url_web",
                    "processed_date": datetime.now().isoformat(),
                    "processing_method": "markitdown",
                    "converted_to_md": processed_filepath if processed_filepath else "No",
                    "server_processed_date": datetime.now().isoformat()
                }
                
                # Añadir contenido a la base de conocimientos
                log(f"MCP Server: Añadiendo contenido a la base de conocimientos...")
                add_text_to_knowledge_base(processed_content, rag_state["vector_store"], metadata)
                
                log(f"MCP Server: Proceso completado - URL procesada con éxito")
                
                # Preparar respuesta informativa
                return f"""✅ **URL procesada exitosamente**
🌐 **URL:** {url}
📋 **Tipo:** PÁGINA WEB
🔧 **Método:** MarkItDown
📊 **Caracteres procesados:** {len(processed_content):,}
💾 **Copia guardada:** {processed_filepath if processed_filepath else "No disponible"}"""
                
            except Exception as e:
                log(f"MCP Server: Error procesando URL '{url}': {e}")
                return f"Error procesando URL: {e}"
                
    except Exception as e:
        log(f"MCP Server: Error procesando URL '{url}': {e}")
        return f"Error procesando URL: {e}" 