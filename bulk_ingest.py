import os
import argparse
from datetime import datetime
from rag_core import get_vector_store, add_text_to_knowledge_base, log, load_document_with_fallbacks

# Lista de extensiones de archivo que queremos procesar
SUPPORTED_EXTENSIONS = [
    # Documentos de Office
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".rtf",
    # Documentos OpenDocument
    ".odt", ".odp", ".ods",
    # Formatos web y markup
    ".html", ".htm", ".xml", ".md",
    # Formatos de texto plano
    ".txt", ".csv", ".tsv",
    # Formatos de datos
    ".json", ".yaml", ".yml",
    # Imágenes (requieren OCR)
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
    # Correos electrónicos
    ".eml", ".msg"
]

# Carpeta donde se guardarán las copias en Markdown
CONVERTED_DOCS_DIR = "./converted_docs"

def ensure_converted_docs_directory():
    """Asegura que existe la carpeta para los documentos convertidos."""
    if not os.path.exists(CONVERTED_DOCS_DIR):
        os.makedirs(CONVERTED_DOCS_DIR)
        log(f"Bulk Ingest: Creada carpeta para documentos convertidos: {CONVERTED_DOCS_DIR}")

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
        return md_filepath
    except Exception as e:
        log(f"  Warning: No se pudo guardar copia Markdown: {e}")
        return ""

def process_directory(directory_path: str):
    """
    Recorre un directorio, convierte los archivos soportados a Markdown y los añade a la base de conocimiento.
    También guarda copias en Markdown de cada documento procesado.
    """
    log(f"Starting bulk ingest process for directory: {directory_path}")
    log(f"Configuring vector database...")
    
    # Obtenemos acceso a nuestra base de datos vectorial
    vector_store = get_vector_store()
    
    log(f"Vector database configured.")
    log(f"Initializing enhanced document processor...")
    
    # Contador para estadísticas
    processed_count = 0
    saved_copies_count = 0
    error_count = 0
    skipped_count = 0
    
    # Contar archivos totales para mostrar progreso
    total_files = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                total_files += 1
    
    log(f"Found {total_files} supported files to process.")
    log(f"Starting enhanced processing with Unstructured...\n")
    
    # os.walk nos permite recorrer el directorio y todos sus subdirectorios
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Comprobamos si la extensión del archivo está en nuestra lista de soportadas
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                log(f"[{processed_count + 1}/{total_files}] Processing: {file}")
                
                try:
                    # Usar el sistema mejorado de carga de documentos
                    log(f"   - Loading with enhanced Unstructured system...")
                    markdown_content, metadata = load_document_with_fallbacks(file_path)
                    
                    if not markdown_content or markdown_content.isspace():
                        log(f"   - Warning: Document resulted in empty content. Skipping.")
                        skipped_count += 1
                        continue
                        
                    log(f"   - Converted ({len(markdown_content)} characters)")
                    log(f"   - Processing method: {metadata.get('processing_method', 'unknown')}")
                    
                    # Mostrar información estructural si está disponible
                    if 'structural_info' in metadata:
                        struct_info = metadata['structural_info']
                        log(f"   - Structure: {struct_info['titles_count']} titles, {struct_info['tables_count']} tables, {struct_info['lists_count']} lists")
                    
                    # Guardar copia en Markdown
                    log(f"   - Saving Markdown copy...")
                    md_copy_path = save_markdown_copy(file_path, markdown_content)
                    if md_copy_path:
                        saved_copies_count += 1
                        log(f"   - Copy saved: {md_copy_path}")
                    
                    # Actualizar metadatos con información de la copia
                    metadata['converted_to_md'] = md_copy_path if md_copy_path else "No"
                    
                    # Añadimos el contenido a la base de datos usando nuestra función del núcleo
                    log(f"   - Adding to knowledge base...")
                    add_text_to_knowledge_base(markdown_content, vector_store, metadata)
                    processed_count += 1
                    
                    log(f"   - File '{file}' processed successfully.")
                
                except Exception as e:
                    # Si algo sale mal con un archivo, lo reportamos y continuamos con el siguiente
                    error_count += 1
                    log(f"   - Error processing '{file}': {e}")
            else:
                skipped_count += 1
                log(f"Skipping unsupported file: {file}")

    log(f"\nBulk ingest process completed!")
    log(f"Final Statistics:")
    log(f"   - Successfully processed documents: {processed_count}")
    log(f"   - Markdown copies saved: {saved_copies_count}")
    log(f"   - Errors encountered: {error_count}")
    log(f"   - Skipped files: {skipped_count}")
    log(f"   - Copies folder: {CONVERTED_DOCS_DIR}")
    log(f"   - Database folder: {CONVERTED_DOCS_DIR.replace('converted_docs', 'rag_mcp_db')}")

if __name__ == "__main__":
    # argparse nos permite crear una interfaz de línea de comandos robusta
    parser = argparse.ArgumentParser(description="Procesador masivo de documentos para el sistema RAG.")
    parser.add_argument(
        "--directory",
        type=str,
        required=True,
        help="La ruta al directorio que contiene los documentos a procesar."
    )
    
    args = parser.parse_args()
    
    # Verificamos que el directorio exista
    if not os.path.isdir(args.directory):
        log(f"Error: El directorio '{args.directory}' no existe o no es un directorio válido.")
    else:
        process_directory(args.directory) 