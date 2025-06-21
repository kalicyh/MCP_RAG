import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown

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
    
    log("MCP Server: Warming up RAG system...")
    log("MCP Server: Pre-loading embedding model into memory...")
    
    # Esta llamada fuerza la carga del modelo de embedding
    get_vector_store()
    
    rag_state["warmed_up"] = True
    log("MCP Server: RAG system is warm and ready.")

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
        log(f"MCP Server Warning: No se pudo guardar copia Markdown: {e}")
        return ""

def initialize_rag():
    """
    Inicializa todos los componentes del sistema RAG usando el núcleo.
    """
    if "initialized" in rag_state:
        return

    log("MCP Server: Initializing RAG system via core...")
    
    # Obtenemos la base de datos y la cadena QA desde nuestro núcleo
    vector_store = get_vector_store()
    qa_chain = get_qa_chain(vector_store)
    
    rag_state["vector_store"] = vector_store
    rag_state["qa_chain"] = qa_chain
    rag_state["initialized"] = True
    log("MCP Server: RAG system initialized successfully.")

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
    log(f"MCP Server: Processing text of {len(text)} characters from source: {source_name}")
    initialize_rag()
    
    try:
        # Crear metadatos de fuente
        source_metadata = {
            "source": source_name,
            "input_type": "manual_text",
            "processed_date": "2025-06-21"
        }
        
        # Usamos la función del núcleo para añadir el texto con metadatos
        add_text_to_knowledge_base(text, rag_state["vector_store"], source_metadata)
        log(f"MCP Server: Text added successfully to the knowledge base")
        return f"Text successfully added to knowledge base. Fragment: '{text[:70]}...' (Source: {source_name})"
    except Exception as e:
        log(f"MCP Server: Error adding text: {e}")
        return f"Error adding text: {e}"

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
    log(f"MCP Server: Starting document processing: {file_path}")
    log(f"MCP Server: DEBUG - Raw path received: {repr(file_path)}")
    log(f"MCP Server: DEBUG - Checking existence for absolute path: {os.path.abspath(file_path)}")
    initialize_rag()  # Asegura que el sistema RAG esté listo
    
    try:
        if not os.path.exists(file_path):
            log(f"MCP Server: File not found at path: {file_path}")
            return f"Error: File not found at '{file_path}'"

        log(f"MCP Server: Converting document to Markdown...")
        result = md_converter.convert(file_path)
        markdown_content = result.text_content

        if not markdown_content or markdown_content.isspace():
            log(f"MCP Server: Warning: Document processed but no text could be extracted: {file_path}")
            return f"Warning: Document '{file_path}' was processed, but no text content could be extracted."

        log(f"MCP Server: Document converted successfully ({len(markdown_content)} characters)")
        
        # Guardar copia en Markdown
        log(f"MCP Server: Saving Markdown copy...")
        md_copy_path = save_markdown_copy(file_path, markdown_content)
        
        # Reutilizamos la herramienta learn_text que ahora usa el núcleo
        log(f"MCP Server: Adding content to the knowledge base...")
        
        # Crear metadatos específicos del documento
        doc_metadata = {
            "source": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": os.path.splitext(file_path)[1].lower(),
            "input_type": "document",
            "processed_date": "2025-06-21",
            "converted_to_md": md_copy_path if md_copy_path else "No"
        }
        
        # Añadir directamente con metadatos en lugar de usar learn_text
        add_text_to_knowledge_base(markdown_content, rag_state["vector_store"], doc_metadata)
        
        # Añadir información sobre la copia guardada
        if md_copy_path:
            log(f"MCP Server: Process completed - Markdown copy saved")
            return f"Document successfully added to knowledge base. Source: {os.path.basename(file_path)}\n\nMarkdown copy saved at: {md_copy_path}"
        else:
            log(f"MCP Server: Process completed - No Markdown copy saved")
            return f"Document successfully added to knowledge base. Source: {os.path.basename(file_path)}"

    except Exception as e:
        log(f"MCP Server: Error processing document '{file_path}': {e}")
        error_msg = f"Error processing document '{file_path}': {e}"
        
        # Proporcionar información más útil para el agente
        if "File not found" in str(e):
            error_msg += "\n\n💡 Tip: Make sure the file path is correct and the file exists."
        elif "UnsupportedFormatException" in str(e):
            error_msg += "\n\n💡 Tip: This file format is not supported. Supported formats: PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML"
        elif "permission" in str(e).lower():
            error_msg += "\n\n💡 Tip: Check if you have permission to access this file."
        
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
    log(f"MCP Server: Processing question: '{query[:50]}{'...' if len(query) > 50 else ''}'")
    initialize_rag()

    try:
        log(f"MCP Server: Searching for relevant information in the knowledge base...")
        qa_chain = rag_state["qa_chain"]
        response = qa_chain.invoke({"query": query})
        
        # Obtener la respuesta principal
        answer = response.get("result", "Could not get an answer.")
        
        # Añadir información de fuentes si está disponible
        sources_info = ""
        if "source_documents" in response and response["source_documents"]:
            sources_info = "\n\n📚 Fuentes de información:\n"
            for i, doc in enumerate(response["source_documents"], 1):
                source_name = doc.metadata.get("source", "Unknown") if hasattr(doc, 'metadata') and doc.metadata else "Unknown"
                sources_info += f"   {i}. {source_name}\n"
        
        log(f"MCP Server: Answer generated successfully")
        return answer + sources_info
    except Exception as e:
        log(f"MCP Server: Error processing question: {e}")
        return f"Error processing the question: {e}"

# --- Punto de Entrada para Correr el Servidor ---
if __name__ == "__main__":
    log("Starting RAG MCP server...")
    warm_up_rag_system()  # Calentamos el sistema al arrancar
    mcp.run(transport='stdio') 