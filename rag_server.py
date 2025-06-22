import os
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown
from urllib.parse import urlparse

# --- Importaciones de nuestro núcleo RAG ---
from rag_core import (
    get_vector_store,
    add_text_to_knowledge_base,
    add_text_to_knowledge_base_enhanced,  # Nueva función mejorada
    load_document_with_fallbacks,         # Nueva función de procesamiento con Unstructured
    get_qa_chain,
    search_with_metadata_filters,         # Nueva función de búsqueda con filtros
    create_metadata_filter,               # Nueva función para crear filtros
    get_document_statistics,              # Nueva función para estadísticas
    log  # Importamos nuestra nueva función de log
)

# --- Inicialización del Servidor y Configuración ---
load_dotenv()
mcp = FastMCP("rag_server_knowledge")

# El estado ahora solo guarda los componentes listos para usar
rag_state = {}

# Inicializamos el conversor de MarkItDown una sola vez (para URLs)
md_converter = MarkItDown()

# Carpeta donde se guardarán las copias en Markdown
CONVERTED_DOCS_DIR = "./converted_docs"

def warm_up_rag_system():
    """
    Precarga los componentes pesados del sistema RAG para evitar demoras
    y conflictos en la primera llamada de una herramienta.
    """
    if "warmed_up" in rag_state:
        return
    
    log("MCP Server: Calentando sistema RAG...")
    log("MCP Server: Precargando modelo de embedding en memoria...")
    
    # Esta llamada fuerza la carga del modelo de embedding
    get_vector_store()
    
    rag_state["warmed_up"] = True
    log("MCP Server: Sistema RAG caliente y listo.")

def ensure_converted_docs_directory():
    """Asegura que existe la carpeta para los documentos convertidos."""
    if not os.path.exists(CONVERTED_DOCS_DIR):
        os.makedirs(CONVERTED_DOCS_DIR)
        log(f"MCP Server: Creada carpeta para documentos convertidos: {CONVERTED_DOCS_DIR}")

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
    md_filepath = os.path.join(CONVERTED_DOCS_DIR, md_filename)
    
    # Guardar el contenido en el archivo Markdown
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        log(f"MCP Server: Copia procesada guardada en: {md_filepath}")
        return md_filepath
    except Exception as e:
        log(f"MCP Server Advertencia: No se pudo guardar copia procesada: {e}")
        return ""

def initialize_rag():
    """
    Inicializa todos los componentes del sistema RAG usando el núcleo.
    """
    if "initialized" in rag_state:
        return

    log("MCP Server: Inicializando sistema RAG vía núcleo...")
    
    # Obtenemos la base de datos y la cadena QA desde nuestro núcleo
    vector_store = get_vector_store()
    qa_chain = get_qa_chain(vector_store)
    
    rag_state["vector_store"] = vector_store
    rag_state["qa_chain"] = qa_chain
    rag_state["initialized"] = True
    log("MCP Server: Sistema RAG inicializado exitosamente.")

# --- Implementación de las Herramientas ---

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
    log(f"MCP Server: Procesando texto de {len(text)} caracteres de la fuente: {source_name}")
    initialize_rag()
    
    try:
        # Crear metadatos de fuente
        source_metadata = {
            "source": source_name,
            "input_type": "manual_text",
            "processed_date": datetime.now().isoformat()
        }
        
        # Usamos la función del núcleo para añadir el texto con metadatos
        add_text_to_knowledge_base(text, rag_state["vector_store"], source_metadata)
        log(f"MCP Server: Texto añadido exitosamente a la base de conocimientos")
        return f"Texto añadido exitosamente a la base de conocimientos. Fragmento: '{text[:70]}...' (Fuente: {source_name})"
    except Exception as e:
        log(f"MCP Server: Error al añadir texto: {e}")
        return f"Error al añadir texto: {e}"

@mcp.tool()
def learn_document(file_path: str) -> str:
    """
    Reads and processes a document file using advanced Unstructured processing, and adds it to the knowledge base.
    Use this when you want to teach the AI from document files with intelligent processing.
    
    Supported file types: PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML, ODT, ODP, ODS, RTF, 
    images (PNG, JPG, TIFF, BMP with OCR), emails (EML, MSG), and more than 25 formats total.
    
    Advanced features:
    - Intelligent document structure preservation (titles, lists, tables)
    - Automatic noise removal (headers, footers, irrelevant content)
    - Semantic chunking for better context
    - Robust fallback system for any document type
    - Structural metadata extraction
    
    Examples of when to use:
    - Processing research papers or articles with complex layouts
    - Adding content from reports or manuals with tables and lists
    - Importing data from spreadsheets with formatting
    - Converting presentations to searchable knowledge
    - Processing scanned documents with OCR
    
    The document will be intelligently processed and stored with enhanced metadata.
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
        
        # Usar el nuevo sistema de procesamiento con Unstructured y fallbacks
        processed_content, metadata = load_document_with_fallbacks(file_path)

        if not processed_content or processed_content.isspace():
            log(f"MCP Server: Advertencia: Documento procesado pero no se pudo extraer contenido: {file_path}")
            return f"Advertencia: El documento '{file_path}' fue procesado, pero no se pudo extraer contenido de texto."

        log(f"MCP Server: Documento procesado exitosamente ({len(processed_content)} caracteres)")
        
        # Guardar copia procesada
        log(f"MCP Server: Guardando copia procesada...")
        processing_method = metadata.get("processing_method", "unstructured_enhanced")
        processed_copy_path = save_processed_copy(file_path, processed_content, processing_method)
        
        # Añadir contenido a la base de conocimientos con metadatos estructurales
        log(f"MCP Server: Añadiendo contenido a la base de conocimientos con metadatos estructurales...")
        
        # Enriquecer metadatos con información del servidor
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            "input_type": "document",
            "converted_to_md": processed_copy_path if processed_copy_path else "No",
            "server_processed_date": datetime.now().isoformat()
        })
        
        # Usar la función mejorada que soporta chunking semántico
        add_text_to_knowledge_base_enhanced(
            processed_content, 
            rag_state["vector_store"], 
            enhanced_metadata, 
            use_semantic_chunking=True
        )
        
        # Construir respuesta informativa
        file_type = enhanced_metadata.get("file_type", "desconocido")
        structural_info = enhanced_metadata.get("structural_info", {})
        
        response_parts = [
            f"✅ **Documento procesado exitosamente**",
            f"📄 **Archivo:** {os.path.basename(file_path)}",
            f"📋 **Tipo:** {file_type.upper()}",
            f"🔧 **Método:** {processing_method.replace('_', ' ').title()}"
        ]
        
        # Añadir información estructural si está disponible
        if structural_info:
            response_parts.extend([
                f"📊 **Estructura del documento:**",
                f"   • Elementos totales: {structural_info.get('total_elements', 'N/A')}",
                f"   • Títulos: {structural_info.get('titles_count', 'N/A')}",
                f"   • Tablas: {structural_info.get('tables_count', 'N/A')}",
                f"   • Listas: {structural_info.get('lists_count', 'N/A')}",
                f"   • Bloques narrativos: {structural_info.get('narrative_blocks', 'N/A')}"
            ])
        
        # Añadir información sobre la copia guardada
        if processed_copy_path:
            response_parts.append(f"💾 **Copia guardada:** {processed_copy_path}")
        
        response_parts.append(f"📚 **Estado:** Añadido a la base de conocimientos con chunking semántico")
        
        log(f"MCP Server: Proceso completado - Documento procesado con éxito")
        return "\n".join(response_parts)

    except Exception as e:
        log(f"MCP Server: Error procesando documento '{file_path}': {e}")
        error_msg = f"❌ **Error procesando documento '{file_path}':** {e}"
        
        # Proporcionar información más útil para el agente
        if "File not found" in str(e):
            error_msg += "\n\n💡 **Consejo:** Asegúrate de que la ruta del archivo sea correcta y que el archivo exista."
        elif "UnsupportedFormatException" in str(e):
            error_msg += "\n\n💡 **Consejo:** Este formato de archivo no es compatible. El sistema soporta más de 25 formatos incluyendo PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML, imágenes con OCR, y más."
        elif "permission" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Verifica si tienes permisos para acceder a este archivo."
        elif "tesseract" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Para procesar imágenes con texto, instala Tesseract OCR: `choco install tesseract` (Windows) o desde GitHub."
        elif "unstructured" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Verifica que Unstructured esté instalado correctamente: `pip install 'unstructured[local-inference,all-docs]'`"
        
        return error_msg

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
            
            # Crear nombre de archivo temporal
            import tempfile
            import requests
            import signal
            
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
                                # Si PyPDF2 no extrae texto, intentar con Unstructured
                                log(f"MCP Server: PyPDF2 no extrajo texto, intentando con Unstructured...")
                                raise Exception("PyPDF2 no extrajo texto")
                    except Exception as e:
                        log(f"MCP Server: PyPDF2 directo falló: {e}")
                        log(f"MCP Server: Intentando con Unstructured con timeout...")
                        
                        # Opción 2: Unstructured con timeout (fallback)
                        # Usar threading con timeout para evitar colgadas
                        import threading
                        import time
                        
                        elements = None
                        processing_error = None
                        
                        def process_pdf():
                            nonlocal elements, processing_error
                            try:
                                from rag_core import partition
                                log(f"MCP Server: Iniciando partición del PDF con strategy='fast'...")
                                log(f"MCP Server: Procesando archivo: {os.path.basename(temp_file_path)}")
                                elements = partition(filename=temp_file_path, strategy="fast", max_partition=1000)
                                log(f"MCP Server: Partición completada, {len(elements)} elementos extraídos")
                            except Exception as e:
                                processing_error = e
                                log(f"MCP Server: Error en partición: {e}")
                        
                        # Ejecutar procesamiento en hilo separado con timeout
                        thread = threading.Thread(target=process_pdf)
                        thread.daemon = True
                        thread.start()
                        
                        # Esperar máximo 30 segundos para el procesamiento
                        timeout_seconds = 30  # Reducido de 60 a 30 segundos para Cursor
                        
                        # Logs de progreso durante la espera
                        log(f"MCP Server: Esperando procesamiento (timeout: {timeout_seconds}s)...")
                        
                        # Esperar con logs de progreso cada 10 segundos
                        for i in range(0, timeout_seconds, 10):
                            thread.join(10)  # Esperar 10 segundos
                            if not thread.is_alive():
                                break
                            log(f"MCP Server: Procesamiento en progreso... ({i+10}/{timeout_seconds}s)")
                        
                        # Verificar si terminó o si necesitamos esperar más
                        if thread.is_alive():
                            remaining_time = timeout_seconds - (timeout_seconds // 10) * 10
                            if remaining_time > 0:
                                thread.join(remaining_time)
                        
                        if thread.is_alive():
                            log(f"MCP Server: Timeout en procesamiento de PDF después de {timeout_seconds} segundos")
                            # Intentar con configuración mínima
                            log(f"MCP Server: Intentando con configuración mínima...")
                            try:
                                from rag_core import partition
                                elements = partition(filename=temp_file_path, strategy="fast", max_partition=500)
                                log(f"MCP Server: Partición mínima completada, {len(elements)} elementos extraídos")
                            except Exception as e:
                                log(f"MCP Server: Error en partición mínima: {e}")
                                return f"❌ **Error de timeout:** El procesamiento del PDF tardó demasiado.\n\n💡 **Consejos:**\n- El PDF puede ser muy grande o complejo\n- Intenta con un PDF más pequeño\n- Verifica que el archivo no esté corrupto"
                        
                        if processing_error:
                            log(f"MCP Server: Error en procesamiento: {processing_error}")
                            return f"❌ **Error procesando PDF:** {processing_error}\n\n💡 **Consejos:**\n- El archivo puede estar corrupto\n- Intenta con un PDF diferente\n- Verifica que el archivo sea accesible"
                        
                        if not elements:
                            log(f"MCP Server: No se pudieron extraer elementos del PDF")
                            # Intentar con PyPDF2 como fallback
                            log(f"MCP Server: Intentando con PyPDF2 como fallback...")
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
                                        log(f"MCP Server: PyPDF2 fallback exitoso, {len(processed_content)} caracteres extraídos")
                                        metadata = {
                                            "source": os.path.basename(temp_file_path),
                                            "file_path": temp_file_path,
                                            "file_type": ".pdf",
                                            "processed_date": datetime.now().isoformat(),
                                            "processing_method": "pypdf2_fallback",
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
                                    else:
                                        return f"❌ **Error:** No se pudo extraer texto del PDF con ningún método.\n\n💡 **Consejos:**\n- El PDF puede estar escaneado (solo imágenes)\n- El archivo puede estar corrupto\n- Intenta con un PDF diferente"
                            except ImportError:
                                log(f"MCP Server: PyPDF2 no disponible")
                                return f"❌ **Error:** No se pudieron extraer elementos del PDF.\n\n💡 **Consejos:**\n- El archivo puede estar vacío o corrupto\n- Intenta con un PDF diferente"
                            except Exception as e:
                                log(f"MCP Server: Error en PyPDF2 fallback: {e}")
                                return f"❌ **Error:** No se pudieron extraer elementos del PDF.\n\n💡 **Consejos:**\n- El archivo puede estar vacío o corrupto\n- Intenta con un PDF diferente"
                        else:
                            log(f"MCP Server: Procesando elementos extraídos...")
                            from rag_core import process_unstructured_elements, extract_structural_metadata
                            processed_content = process_unstructured_elements(elements)
                            log(f"MCP Server: Elementos procesados, {len(processed_content)} caracteres extraídos")
                            
                            metadata = extract_structural_metadata(elements, temp_file_path)
                            metadata["processing_method"] = "unstructured_fast_pdf"
                            log(f"MCP Server: Metadatos estructurales extraídos")
                else:
                    # Para otros formatos, usar el procesamiento normal
                    processed_content, metadata = load_document_with_fallbacks(temp_file_path)
                
                if not processed_content or processed_content.isspace():
                    log(f"MCP Server: Advertencia: Archivo descargado pero no se pudo extraer contenido: {url}")
                    return f"Advertencia: El archivo de la URL '{url}' fue descargado, pero no se pudo extraer contenido de texto."
                
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
                processed_filepath = os.path.join(CONVERTED_DOCS_DIR, filename)
                
                try:
                    ensure_converted_docs_directory()
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
                    use_semantic_chunking=True
                )
                
                # Construir respuesta informativa
                structural_info = enhanced_metadata.get("structural_info", {})
                
                response_parts = [
                    f"✅ **Archivo descargado y procesado exitosamente**",
                    f"🌐 **URL:** {url}",
                    f"📄 **Archivo:** {os.path.basename(parsed_url.path)}",
                    f"📋 **Tipo:** {file_extension.upper()}",
                    f"🔧 **Método:** {processing_method.replace('_', ' ').title()}"
                ]
                
                # Añadir información estructural si está disponible
                if structural_info:
                    response_parts.extend([
                        f"📊 **Estructura del documento:**",
                        f"   • Elementos totales: {structural_info.get('total_elements', 'N/A')}",
                        f"   • Títulos: {structural_info.get('titles_count', 'N/A')}",
                        f"   • Tablas: {structural_info.get('tables_count', 'N/A')}",
                        f"   • Listas: {structural_info.get('lists_count', 'N/A')}",
                        f"   • Bloques narrativos: {structural_info.get('narrative_blocks', 'N/A')}"
                    ])
                
                if processed_filepath:
                    response_parts.append(f"💾 **Copia guardada:** {processed_filepath}")
                
                response_parts.append(f"📚 **Estado:** Añadido a la base de conocimientos con chunking semántico")
                
                log(f"MCP Server: Procesamiento de URL completado exitosamente")
                return "\n".join(response_parts)
                
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_file_path)
                    log(f"MCP Server: Archivo temporal eliminado: {temp_file_path}")
                except Exception as e:
                    log(f"MCP Server Advertencia: No se pudo eliminar archivo temporal: {e}")
        
        else:
            # Procesamiento tradicional para páginas web
            log(f"MCP Server: Procesando contenido web con MarkItDown...")
            
            # Usar MarkItDown para procesar la URL directamente con timeout
            try:
                result = md_converter.convert_url(url)
                markdown_content = result.text_content
            except Exception as e:
                log(f"MCP Server: Error con MarkItDown, intentando descarga directa: {e}")
                # Fallback: intentar descarga directa
                import requests
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                markdown_content = response.text

            if not markdown_content or markdown_content.isspace():
                log(f"MCP Server: Advertencia: URL procesada pero no se pudo extraer contenido: {url}")
                return f"Advertencia: La URL '{url}' fue procesada, pero no se pudo extraer contenido de texto."

            log(f"MCP Server: Contenido de URL convertido exitosamente ({len(markdown_content)} caracteres)")
            
            # Guardar copia en Markdown
            log(f"MCP Server: Guardando copia Markdown...")
            
            # Crear nombre de archivo basado en la URL
            domain = parsed_url.netloc.replace('.', '_')
            path = parsed_url.path.replace('/', '_').replace('.', '_')
            if not path or path == '_':
                path = 'homepage'
            
            # Crear nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{path}_{timestamp}_markitdown.md"
            md_filepath = os.path.join(CONVERTED_DOCS_DIR, filename)
            
            # Guardar el contenido
            try:
                ensure_converted_docs_directory()
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                log(f"MCP Server: Copia Markdown guardada en: {md_filepath}")
            except Exception as e:
                log(f"MCP Server Advertencia: No se pudo guardar copia Markdown: {e}")
                md_filepath = ""
            
            # Añadir contenido a la base de conocimientos
            log(f"MCP Server: Añadiendo contenido a la base de conocimientos...")
            
            # Crear metadatos específicos de la URL
            url_metadata = {
                "source": url,
                "domain": parsed_url.netloc,
                "input_type": "url_web",
                "processed_date": datetime.now().isoformat(),
                "processing_method": "markitdown",
                "converted_to_md": md_filepath if md_filepath else "No"
            }
            
            # Añadir directamente con metadatos
            add_text_to_knowledge_base(markdown_content, rag_state["vector_store"], url_metadata)
            
            # Información sobre el proceso completado
            response_parts = [
                f"✅ **Contenido web procesado exitosamente**",
                f"🌐 **URL:** {url}",
                f"🌍 **Dominio:** {parsed_url.netloc}",
                f"🔧 **Método:** MarkItDown"
            ]
            
            if md_filepath:
                response_parts.append(f"💾 **Copia guardada:** {md_filepath}")
            
            response_parts.append(f"📚 **Estado:** Añadido a la base de conocimientos")
            
            log(f"MCP Server: Procesamiento de URL completado exitosamente")
            return "\n".join(response_parts)

    except requests.exceptions.Timeout:
        log(f"MCP Server: Timeout al procesar URL: {url}")
        return f"❌ **Error de timeout:** La URL '{url}' tardó demasiado en responder.\n\n💡 **Consejos:**\n- Verifica tu conexión a internet\n- Intenta más tarde\n- La URL puede estar temporalmente lenta"
    
    except requests.exceptions.ConnectionError:
        log(f"MCP Server: Error de conexión al procesar URL: {url}")
        return f"❌ **Error de conexión:** No se pudo conectar a la URL '{url}'.\n\n💡 **Consejos:**\n- Verifica tu conexión a internet\n- La URL puede no estar disponible\n- Intenta más tarde"
    
    except Exception as e:
        log(f"MCP Server: Error procesando URL '{url}': {e}")
        error_msg = f"❌ **Error procesando URL '{url}':** {e}"
        
        # Proporcionar información más útil para el agente
        if "404" in str(e) or "Not Found" in str(e):
            error_msg += "\n\n💡 **Consejo:** La URL no existe o no es accesible. Verifica que la URL sea correcta."
        elif "timeout" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** La página tardó demasiado en cargar. Intenta más tarde o verifica tu conexión a internet."
        elif "permission" in str(e).lower() or "403" in str(e):
            error_msg += "\n\n💡 **Consejo:** No tienes permisos para acceder a esta página. Algunas páginas bloquean el acceso automático."
        elif "youtube" in url.lower() and "transcript" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Este video de YouTube no tiene transcripción disponible o está deshabilitada."
        elif "ssl" in str(e).lower() or "certificate" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Problema con el certificado SSL de la página. Intenta con una URL diferente."
        elif "download" in str(e).lower() or "connection" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Error al descargar el archivo. Verifica que la URL sea accesible y el archivo exista."
        elif "unstructured" in str(e).lower():
            error_msg += "\n\n💡 **Consejo:** Error en el procesamiento del documento. El archivo puede estar corrupto o ser muy grande."
        
        return error_msg

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
    log(f"MCP Server: Procesando pregunta: {query}")
    initialize_rag()
    
    try:
        # Usar la cadena QA estándar (sin filtros)
        qa_chain = get_qa_chain(rag_state["vector_store"])
        response = qa_chain.invoke({"query": query})
        
        answer = response.get("result", "No se encontró información relevante para responder tu pregunta.")
        source_documents = response.get("source_documents", [])
        
        # Construir respuesta mejorada con información de fuentes
        enhanced_answer = f"🤖 **Respuesta:**\n\n{answer}\n"
        
        # Añadir información de fuentes con más detalles
        if source_documents:
            enhanced_answer += "📚 **Fuentes de información utilizadas:**\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "Fuente desconocida")
                
                # --- Mejoramos la información de la fuente ---
                source_info = f"   {i}. **{source_name}**"
                
                # Añadir ruta completa si es un documento
                file_path = metadata.get("file_path")
                if file_path:
                    source_info += f"\n      - **Ruta:** `{file_path}`"
                
                # Añadir tipo de archivo si está disponible
                file_type = metadata.get("file_type")
                if file_type:
                    source_info += f"\n      - **Tipo:** {file_type.upper()}"
                
                # Añadir método de procesamiento si está disponible
                processing_method = metadata.get("processing_method")
                if processing_method:
                    method_display = processing_method.replace('_', ' ').title()
                    source_info += f"\n      - **Procesamiento:** {method_display}"
                
                # Añadir información estructural si está disponible
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
                
                # Reconstruir información estructural desde metadatos planos
                structural_elements = []
                titles_count = metadata.get("structural_titles_count", 0)
                tables_count = metadata.get("structural_tables_count", 0)
                lists_count = metadata.get("structural_lists_count", 0)
                total_elements = metadata.get("structural_total_elements", 0)
                
                if total_elements > 0:
                    structural_details = []
                    if titles_count > 0:
                        structural_details.append(f"{titles_count} títulos")
                    if tables_count > 0:
                        structural_details.append(f"{tables_count} tablas")
                    if lists_count > 0:
                        structural_details.append(f"{lists_count} listas")
                    
                    if structural_details:
                        source_info += f"\n      - **Estructura:** {', '.join(structural_details)}"
                
                enhanced_answer += source_info + "\n\n"
        else:
            enhanced_answer += "\n⚠️ **No se encontraron fuentes específicas para esta respuesta.**\n"
        
        # Añadir información sobre la calidad de la respuesta
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ **Alta confianza:** Respuesta basada en múltiples fuentes"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ **Confianza media:** Respuesta basada en 2 fuentes"
        else:
            enhanced_answer += "\n⚠️ **Confianza limitada:** Respuesta basada en 1 fuente"
        
        # Añadir información sobre el procesamiento si hay documentos con metadatos estructurales
        enhanced_docs = [doc for doc in source_documents if hasattr(doc, 'metadata') and doc.metadata.get("processing_method") == "unstructured_enhanced"]
        if enhanced_docs:
            enhanced_answer += f"\n🧠 **Procesamiento inteligente:** {len(enhanced_docs)} fuentes procesadas con Unstructured (preservación de estructura)"
        
        log(f"MCP Server: Respuesta generada exitosamente con {len(source_documents)} fuentes")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP Server: Error procesando pregunta: {e}")
        return f"❌ **Error al procesar la pregunta:** {e}\n\n💡 **Sugerencias:**\n- Verifica que el sistema RAG esté correctamente inicializado\n- Intenta reformular tu pregunta\n- Si el problema persiste, reinicia el servidor"

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
        
        answer = response.get("result", "No se encontró información relevante con los filtros especificados.")
        source_documents = response.get("source_documents", [])
        
        # Construir respuesta mejorada
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
        
        # Añadir información de fuentes
        if source_documents:
            enhanced_answer += f"\n📚 **Fuentes encontradas ({len(source_documents)}):**\n\n"
            for i, doc in enumerate(source_documents, 1):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "Fuente desconocida")
                
                source_info = f"   {i}. **{source_name}**"
                
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
        else:
            enhanced_answer += "\n⚠️ **No se encontraron documentos que cumplan con los filtros especificados.**\n"
        
        # Información sobre la búsqueda filtrada
        enhanced_answer += f"\n🎯 **Búsqueda filtrada:** Los resultados se limitaron a documentos que cumplen con los criterios especificados."
        
        log(f"MCP Server: Respuesta filtrada generada exitosamente con {len(source_documents)} fuentes")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP Server: Error procesando pregunta filtrada: {e}")
        return f"❌ **Error al procesar la pregunta filtrada:** {e}"

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
    log(f"MCP Server: Obteniendo estadísticas de la base de conocimientos...")
    initialize_rag()
    
    try:
        stats = get_document_statistics(rag_state["vector_store"])
        
        if "error" in stats:
            return f"❌ **Error obteniendo estadísticas:** {stats['error']}"
        
        if stats.get("total_documents", 0) == 0:
            return "📊 **Base de conocimientos vacía**\n\nNo hay documentos almacenados en la base de conocimientos."
        
        # Construir respuesta detallada
        response = f"📊 **Estadísticas de la Base de Conocimientos**\n\n"
        response += f"📚 **Total de documentos:** {stats['total_documents']}\n\n"
        
        # Tipos de archivo
        if stats["file_types"]:
            response += "📄 **Tipos de archivo:**\n"
            for file_type, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total_documents"]) * 100
                response += f"   • {file_type.upper()}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Métodos de procesamiento
        if stats["processing_methods"]:
            response += "🔧 **Métodos de procesamiento:**\n"
            for method, count in sorted(stats["processing_methods"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total_documents"]) * 100
                method_display = method.replace('_', ' ').title()
                response += f"   • {method_display}: {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Estadísticas estructurales
        structural = stats["structural_stats"]
        response += "🏗️ **Información estructural:**\n"
        response += f"   • Documentos con tablas: {structural['documents_with_tables']}\n"
        response += f"   • Documentos con títulos: {structural['documents_with_titles']}\n"
        response += f"   • Documentos con listas: {structural['documents_with_lists']}\n"
        response += f"   • Promedio de tablas por documento: {structural['avg_tables_per_doc']:.1f}\n"
        response += f"   • Promedio de títulos por documento: {structural['avg_titles_per_doc']:.1f}\n"
        response += f"   • Promedio de listas por documento: {structural['avg_lists_per_doc']:.1f}\n\n"
        
        # Sugerencias de búsqueda
        response += "💡 **Sugerencias de búsqueda:**\n"
        if structural['documents_with_tables'] > 0:
            response += f"   • Usa `ask_rag_filtered` con `min_tables=1` para buscar información en documentos con tablas\n"
        if structural['documents_with_titles'] > 5:
            response += f"   • Usa `ask_rag_filtered` con `min_titles=5` para buscar en documentos bien estructurados\n"
        if ".pdf" in stats["file_types"]:
            response += f"   • Usa `ask_rag_filtered` con `file_type=\".pdf\"` para buscar solo en documentos PDF\n"
        
        log(f"MCP Server: Estadísticas obtenidas exitosamente")
        return response
        
    except Exception as e:
        log(f"MCP Server: Error obteniendo estadísticas: {e}")
        return f"❌ **Error obteniendo estadísticas:** {e}"

# --- Punto de Entrada para Correr el Servidor ---
if __name__ == "__main__":
    log("Iniciando servidor MCP RAG...")
    warm_up_rag_system()  # Calentamos el sistema al arrancar
    mcp.run(transport='stdio') 