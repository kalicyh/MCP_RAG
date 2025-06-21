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
    get_qa_chain,
    log  # Importamos nuestra nueva función de log
)

# --- Inicialización del Servidor y Configuración ---
load_dotenv()
mcp = FastMCP("rag_server_knowledge")

# El estado ahora solo guarda los componentes listos para usar
rag_state = {}

# Inicializamos el conversor de MarkItDown una sola vez.
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

def save_markdown_copy(file_path: str, markdown_content: str) -> str:
    """
    Guarda una copia del documento convertido en formato Markdown.
    
    Args:
        file_path: Ruta original del archivo
        markdown_content: Contenido convertido a Markdown
    
    Returns:
        Ruta del archivo Markdown guardado
    """
    ensure_converted_docs_directory()
    
    # Obtener el nombre del archivo original sin extensión
    original_filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(original_filename)[0]
    
    # Crear el nombre del archivo Markdown
    md_filename = f"{name_without_ext}.md"
    md_filepath = os.path.join(CONVERTED_DOCS_DIR, md_filename)
    
    # Guardar el contenido en el archivo Markdown
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        log(f"MCP Server: Copia Markdown guardada en: {md_filepath}")
        return md_filepath
    except Exception as e:
        log(f"MCP Server Advertencia: No se pudo guardar copia Markdown: {e}")
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
    Reads and processes a document file, converts it to Markdown, and adds it to the knowledge base.
    Use this when you want to teach the AI from document files like PDFs, Word documents, etc.
    
    Supported file types: PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML
    
    Examples of when to use:
    - Processing research papers or articles
    - Adding content from reports or manuals
    - Importing data from spreadsheets
    - Converting presentations to searchable knowledge
    
    The document will be automatically converted to Markdown format and stored with source tracking.
    A copy of the converted document is saved for verification.

    Args:
        file_path: The absolute or relative path to the document file to process.
    """
    log(f"MCP Server: Iniciando procesamiento de documento: {file_path}")
    log(f"MCP Server: DEBUG - Ruta recibida: {repr(file_path)}")
    log(f"MCP Server: DEBUG - Verificando existencia de ruta absoluta: {os.path.abspath(file_path)}")
    initialize_rag()  # Asegura que el sistema RAG esté listo
    
    try:
        if not os.path.exists(file_path):
            log(f"MCP Server: Archivo no encontrado en la ruta: {file_path}")
            return f"Error: Archivo no encontrado en '{file_path}'"

        log(f"MCP Server: Convirtiendo documento a Markdown...")
        result = md_converter.convert(file_path)
        markdown_content = result.text_content

        if not markdown_content or markdown_content.isspace():
            log(f"MCP Server: Advertencia: Documento procesado pero no se pudo extraer texto: {file_path}")
            return f"Advertencia: El documento '{file_path}' fue procesado, pero no se pudo extraer contenido de texto."

        log(f"MCP Server: Documento convertido exitosamente ({len(markdown_content)} caracteres)")
        
        # Guardar copia en Markdown
        log(f"MCP Server: Guardando copia Markdown...")
        md_copy_path = save_markdown_copy(file_path, markdown_content)
        
        # Reutilizamos la herramienta learn_text que ahora usa el núcleo
        log(f"MCP Server: Añadiendo contenido a la base de conocimientos...")
        
        # Crear metadatos específicos del documento
        doc_metadata = {
            "source": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": os.path.splitext(file_path)[1].lower(),
            "input_type": "document",
            "processed_date": datetime.now().isoformat(),
            "converted_to_md": md_copy_path if md_copy_path else "No"
        }
        
        # Añadir directamente con metadatos en lugar de usar learn_text
        add_text_to_knowledge_base(markdown_content, rag_state["vector_store"], doc_metadata)
        
        # Añadir información sobre la copia guardada
        if md_copy_path:
            log(f"MCP Server: Proceso completado - Copia Markdown guardada")
            return f"Documento añadido exitosamente a la base de conocimientos. Fuente: {os.path.basename(file_path)}\n\nCopia Markdown guardada en: {md_copy_path}"
        else:
            log(f"MCP Server: Proceso completado - No se guardó copia Markdown")
            return f"Documento añadido exitosamente a la base de conocimientos. Fuente: {os.path.basename(file_path)}"

    except Exception as e:
        log(f"MCP Server: Error procesando documento '{file_path}': {e}")
        error_msg = f"Error procesando documento '{file_path}': {e}"
        
        # Proporcionar información más útil para el agente
        if "File not found" in str(e):
            error_msg += "\n\n💡 Consejo: Asegúrate de que la ruta del archivo sea correcta y que el archivo exista."
        elif "UnsupportedFormatException" in str(e):
            error_msg += "\n\n💡 Consejo: Este formato de archivo no es compatible. Formatos soportados: PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML"
        elif "permission" in str(e).lower():
            error_msg += "\n\n💡 Consejo: Verifica si tienes permisos para acceder a este archivo."
        
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
    
    Examples of when to use:
    - Adding content from news articles or blog posts
    - Processing YouTube video transcripts
    - Importing information from web pages
    - Converting web content to searchable knowledge
    
    The content will be automatically converted to Markdown format and stored with source tracking.
    A copy of the converted content is saved for verification.

    Args:
        url: The URL of the web page or video to process.
    """
    log(f"MCP Server: Iniciando procesamiento de URL: {url}")
    initialize_rag()
    
    try:
        log(f"MCP Server: Convirtiendo contenido de URL a Markdown...")
        
        # Usar MarkItDown para procesar la URL directamente
        result = md_converter.convert_url(url)
        markdown_content = result.text_content

        if not markdown_content or markdown_content.isspace():
            log(f"MCP Server: Advertencia: URL procesada pero no se pudo extraer contenido: {url}")
            return f"Advertencia: La URL '{url}' fue procesada, pero no se pudo extraer contenido de texto."

        log(f"MCP Server: Contenido de URL convertido exitosamente ({len(markdown_content)} caracteres)")
        
        # Guardar copia en Markdown
        log(f"MCP Server: Guardando copia Markdown...")
        
        # Crear nombre de archivo basado en la URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('.', '_')
        path = parsed_url.path.replace('/', '_').replace('.', '_')
        if not path or path == '_':
            path = 'homepage'
        
        # Crear nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{path}_{timestamp}.md"
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
            "input_type": "url",
            "processed_date": datetime.now().isoformat(),
            "converted_to_md": md_filepath if md_filepath else "No"
        }
        
        # Añadir directamente con metadatos
        add_text_to_knowledge_base(markdown_content, rag_state["vector_store"], url_metadata)
        
        # Información sobre el proceso completado
        if md_filepath:
            log(f"MCP Server: Proceso completado - Copia Markdown guardada")
            return f"Contenido de URL añadido exitosamente a la base de conocimientos.\n\nURL: {url}\nDominio: {parsed_url.netloc}\n\nCopia Markdown guardada en: {md_filepath}"
        else:
            log(f"MCP Server: Proceso completado - No se guardó copia Markdown")
            return f"Contenido de URL añadido exitosamente a la base de conocimientos.\n\nURL: {url}\nDominio: {parsed_url.netloc}"

    except Exception as e:
        log(f"MCP Server: Error procesando URL '{url}': {e}")
        error_msg = f"Error procesando URL '{url}': {e}"
        
        # Proporcionar información más útil para el agente
        if "404" in str(e) or "Not Found" in str(e):
            error_msg += "\n\n💡 Consejo: La URL no existe o no es accesible. Verifica que la URL sea correcta."
        elif "timeout" in str(e).lower():
            error_msg += "\n\n💡 Consejo: La página tardó demasiado en cargar. Intenta más tarde o verifica tu conexión a internet."
        elif "permission" in str(e).lower() or "403" in str(e):
            error_msg += "\n\n💡 Consejo: No tienes permisos para acceder a esta página. Algunas páginas bloquean el acceso automático."
        elif "youtube" in url.lower() and "transcript" in str(e).lower():
            error_msg += "\n\n💡 Consejo: Este video de YouTube no tiene transcripción disponible o está deshabilitada."
        elif "ssl" in str(e).lower() or "certificate" in str(e).lower():
            error_msg += "\n\n💡 Consejo: Problema con el certificado SSL de la página. Intenta con una URL diferente."
        
        return error_msg

@mcp.tool()
def ask_rag(query: str) -> str:
    """
    Searches the knowledge base and generates an AI-powered answer based on stored information.
    Use this when you need to retrieve specific information that has been previously stored.
    
    Examples of when to use:
    - Looking up facts, definitions, or explanations that were previously added
    - Finding information from processed documents
    - Retrieving context about specific topics
    - Getting answers based on stored research or notes
    
    The response will include the answer plus a list of sources used to generate it.
    If no relevant information is found, the AI will indicate this clearly.

    Args:
        query: The specific question or information request to search for in the knowledge base.
    """
    log(f"MCP Server: Procesando pregunta: '{query[:50]}{'...' if len(query) > 50 else ''}'")
    initialize_rag()

    try:
        log(f"MCP Server: Buscando información relevante en la base de conocimientos...")
        qa_chain = rag_state["qa_chain"]
        response = qa_chain.invoke({"query": query})
        
        # Obtener la respuesta principal
        answer = response.get("result", "No se pudo obtener una respuesta.")
        
        # Verificar si se encontró información relevante
        source_documents = response.get("source_documents", [])
        
        if not source_documents:
            return "❌ **No se encontró información relevante** en la base de conocimientos para responder a tu pregunta.\n\n💡 **Sugerencias:**\n- Verifica que hayas añadido documentos o texto relacionado con este tema\n- Intenta reformular tu pregunta con palabras diferentes\n- Usa la herramienta `learn_text` o `learn_document` para añadir información sobre este tema"
        
        # Construir respuesta mejorada con información de fuentes
        enhanced_answer = f"🤖 **Respuesta:**\n{answer}\n\n"
        
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
                
                # Añadir fecha de procesamiento
                processed_date = metadata.get("processed_date")
                if processed_date:
                    try:
                        date_obj = datetime.fromisoformat(processed_date.replace('Z', '+00:00'))
                        readable_date = date_obj.strftime("%d/%m/%Y %H:%M")
                        source_info += f"\n      - **Procesado:** {readable_date}"
                    except:
                        pass
                
                # Añadir un fragmento del contenido relevante
                content_snippet = doc.page_content.strip().replace('\n', ' ')
                source_info += f"\n      - **Fragmento Relevante:**\n        > _{content_snippet[:150]}{'...' if len(content_snippet) > 150 else ''}_"
                
                enhanced_answer += source_info + "\n\n"
        
        # Añadir información sobre la calidad de la respuesta
        num_sources = len(source_documents)
        if num_sources >= 3:
            enhanced_answer += "\n✅ **Alta confianza:** Respuesta basada en múltiples fuentes"
        elif num_sources == 2:
            enhanced_answer += "\n⚠️ **Confianza media:** Respuesta basada en 2 fuentes"
        else:
            enhanced_answer += "\n⚠️ **Confianza limitada:** Respuesta basada en 1 fuente"
        
        log(f"MCP Server: Respuesta generada exitosamente con {len(source_documents)} fuentes")
        return enhanced_answer
        
    except Exception as e:
        log(f"MCP Server: Error procesando pregunta: {e}")
        return f"❌ **Error al procesar la pregunta:** {e}\n\n💡 **Sugerencias:**\n- Verifica que el sistema RAG esté correctamente inicializado\n- Intenta reformular tu pregunta\n- Si el problema persiste, reinicia el servidor"

# --- Punto de Entrada para Correr el Servidor ---
if __name__ == "__main__":
    log("Iniciando servidor MCP RAG...")
    warm_up_rag_system()  # Calentamos el sistema al arrancar
    mcp.run(transport='stdio') 