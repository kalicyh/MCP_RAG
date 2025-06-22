import os
from dotenv import load_dotenv
import torch
import sys
from tqdm import tqdm
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
# CAMBIO: Quitamos OpenAI, importamos el wrapper para embeddings locales
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, ListItem, Table, NarrativeText

# --- Configuración Avanzada de Unstructured ---
UNSTRUCTURED_CONFIGS = {
    # Documentos de Office
    '.pdf': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'include_page_breaks': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.docx': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.doc': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.pptx': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.ppt': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.xlsx': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.xls': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.rtf': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Documentos OpenDocument
    '.odt': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.odp': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.ods': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Formatos web y markup
    '.html': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.htm': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.xml': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.md': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Formatos de texto plano
    '.txt': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.csv': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.tsv': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Formatos de datos
    '.json': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.yaml': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.yml': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Imágenes (requieren OCR)
    '.png': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.jpg': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.jpeg': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.tiff': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.bmp': {
        'strategy': 'hi_res',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    
    # Correos electrónicos
    '.eml': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    '.msg': {
        'strategy': 'fast',
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    }
}

# Configuración por defecto para archivos no especificados
DEFAULT_CONFIG = {
    'strategy': 'fast',
    'include_metadata': True,
    'max_partition': 2000,
    'new_after_n_chars': 1500
}

# --- Utilidad de Logging ---
def log(message: str):
    """Imprime un mensaje en stderr para que aparezca en los logs del cliente MCP."""
    print(message, file=sys.stderr, flush=True)

# --- Utilidad de Progreso de Descarga ---
def download_with_progress(url: str, filename: str, desc: str = "Downloading"):
    """Descarga un archivo mostrando una barra de progreso."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=desc,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        file=sys.stderr  # Enviamos a stderr para que aparezca en los logs
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

# --- Configuración ---
load_dotenv()

# Obtenemos la ruta absoluta del directorio del script actual
_project_root = os.path.dirname(os.path.abspath(__file__))
# Forzamos la ruta absoluta para la base de datos, evitando problemas de directorio de trabajo
PERSIST_DIRECTORY = os.path.join(_project_root, "rag_mcp_db")

COLLECTION_NAME = "mcp_rag_collection"
# Definimos el modelo de embedding que usaremos localmente
# Modelos más potentes (requieren más recursos):
# "all-mpnet-base-v2"      # 420MB, mejor calidad
# "text-embedding-ada-002" # 1.5GB, máxima calidad

# Modelos más rápidos:
# "all-MiniLM-L6-v2"       # Tu modelo actual
# "paraphrase-MiniLM-L3-v2" # Aún más rápido
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"

def get_embedding_function():
    """
    Retorna la función de embeddings a usar. Ahora, un modelo local.
    Detecta automáticamente si hay una GPU disponible para usarla.
    """
    log(f"Core: Cargando modelo de embedding local: {EMBEDDING_MODEL_NAME}")
    log("Core: Este paso puede tomar unos minutos en la primera ejecución para descargar el modelo.")
    log("Core: Si el modelo ya está descargado, se cargará rápidamente desde la caché.")
    
    # Detectar si hay una GPU disponible y asignar el dispositivo correspondiente
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    log(f"Core: Usando dispositivo '{device}' para embeddings.")
    
    # Configurar el modelo con progreso de descarga
    model_kwargs = {'device': device}
    
    # Intentar cargar el modelo con progreso visible
    try:
        log("Core: Intentando cargar modelo (se mostrará progreso de descarga si es necesario)...")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs=model_kwargs
        )
        log("Core: ¡Modelo cargado exitosamente!")
        return embeddings
    except Exception as e:
        log(f"Core: Error al cargar modelo: {e}")
        log("Core: Esto podría ser un problema de descarga. Por favor verifica tu conexión a internet.")
        raise

def get_vector_store() -> Chroma:
    """Crea y retorna una instancia de la base de datos vectorial."""
    log(f"Core: Inicializando base de datos vectorial...")
    embeddings = get_embedding_function()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    log(f"Core: Base de datos vectorial inicializada en '{PERSIST_DIRECTORY}'")
    return vector_store

def clean_text_for_rag(text: str) -> str:
    """
    Limpia y prepara el texto para mejorar la calidad de las búsquedas RAG.
    
    Args:
        text: Texto original a limpiar
    
    Returns:
        Texto limpio y optimizado para RAG
    """
    if not text:
        return ""
    
    # Eliminar espacios múltiples y saltos de línea excesivos
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres especiales problemáticos pero mantener puntuación importante
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']', '', text)
    
    # Normalizar espacios alrededor de puntuación
    text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
    
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text

def convert_table_to_text(table_element) -> str:
    """
    Convierte un elemento de tabla a texto legible.
    
    Args:
        table_element: Elemento de tabla de Unstructured
    
    Returns:
        Texto formateado de la tabla
    """
    try:
        if hasattr(table_element, 'text'):
            return table_element.text
        elif hasattr(table_element, 'metadata') and 'text_as_html' in table_element.metadata:
            # Si tenemos HTML, extraer el texto
            html_text = table_element.metadata['text_as_html']
            # Limpiar tags HTML básicos
            clean_text = re.sub(r'<[^>]+>', ' ', html_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return f"Tabla: {clean_text}"
        else:
            return str(table_element)
    except Exception as e:
        log(f"Core Warning: Error convirtiendo tabla: {e}")
        return str(table_element)

def process_unstructured_elements(elements: List[Any]) -> str:
    """
    Procesa elementos de Unstructured de manera inteligente preservando la estructura semántica.
    
    Args:
        elements: Lista de elementos extraídos por Unstructured
    
    Returns:
        Texto procesado con estructura preservada
    """
    processed_parts = []
    
    for element in elements:
        element_type = type(element).__name__
        
        if element_type == 'Title':
            # Los títulos van en líneas separadas con formato especial
            if hasattr(element, 'text') and element.text:
                processed_parts.append(f"\n## {element.text.strip()}\n")
        elif element_type == 'ListItem':
            # Las listas mantienen su estructura
            if hasattr(element, 'text') and element.text:
                processed_parts.append(f"• {element.text.strip()}")
        elif element_type == 'Table':
            # Las tablas se convierten a formato legible
            table_text = convert_table_to_text(element)
            if table_text:
                processed_parts.append(f"\n{table_text}\n")
        elif element_type == 'NarrativeText':
            # El texto narrativo va tal como está
            if hasattr(element, 'text') and element.text:
                processed_parts.append(element.text.strip())
        else:
            # Para otros tipos, usar el texto básico
            if hasattr(element, 'text') and element.text:
                processed_parts.append(element.text.strip())
    
    return "\n\n".join(processed_parts)

def extract_structural_metadata(elements: List[Any], file_path: str) -> Dict[str, Any]:
    """
    Extrae metadatos estructurales del documento.
    
    Args:
        elements: Lista de elementos extraídos por Unstructured
        file_path: Ruta del archivo procesado
    
    Returns:
        Diccionario con metadatos estructurales
    """
    structural_info = {
        "total_elements": len(elements),
        "titles_count": sum(1 for e in elements if type(e).__name__ == 'Title'),
        "tables_count": sum(1 for e in elements if type(e).__name__ == 'Table'),
        "lists_count": sum(1 for e in elements if type(e).__name__ == 'ListItem'),
        "narrative_blocks": sum(1 for e in elements if type(e).__name__ == 'NarrativeText'),
        "other_elements": sum(1 for e in elements if type(e).__name__ not in ['Title', 'Table', 'ListItem', 'NarrativeText'])
    }
    
    # Calcular estadísticas de contenido
    total_text_length = sum(len(e.text) for e in elements if hasattr(e, 'text') and e.text)
    structural_info["total_text_length"] = total_text_length
    structural_info["avg_element_length"] = total_text_length / len(elements) if elements else 0
    
    metadata = {
        "source": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": os.path.splitext(file_path)[1].lower(),
        "processed_date": datetime.now().isoformat(),
        "processing_method": "unstructured_enhanced",
        "structural_info": structural_info
    }
    
    return metadata

def create_semantic_chunks(elements: List[Any], max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Crea chunks basados en la estructura semántica del documento.
    
    Args:
        elements: Lista de elementos extraídos por Unstructured
        max_chunk_size: Tamaño máximo de cada chunk
        overlap: Superposición entre chunks
    
    Returns:
        Lista de chunks semánticos
    """
    chunks = []
    current_chunk = []
    current_size = 0
    
    for i, element in enumerate(elements):
        element_text = element.text if hasattr(element, 'text') else str(element)
        element_size = len(element_text)
        
        # Si añadir este elemento excedería el tamaño máximo
        if current_size + element_size > max_chunk_size and current_chunk:
            # Guardar el chunk actual
            chunk_text = "\n\n".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            # Crear overlap con elementos anteriores si es posible
            overlap_elements = []
            overlap_size = 0
            for j in range(len(current_chunk) - 1, -1, -1):
                if overlap_size + len(current_chunk[j]) <= overlap:
                    overlap_elements.insert(0, current_chunk[j])
                    overlap_size += len(current_chunk[j])
                else:
                    break
            
            # Iniciar nuevo chunk con overlap
            current_chunk = overlap_elements + [element_text]
            current_size = overlap_size + element_size
        else:
            # Añadir al chunk actual
            current_chunk.append(element_text)
            current_size += element_size
    
    # Añadir el último chunk si existe
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        if chunk_text.strip():
            chunks.append(chunk_text)
    
    return chunks

def load_with_langchain_fallbacks(file_path: str) -> str:
    """
    Sistema de fallback usando cargadores específicos de LangChain.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        Contenido del archivo como texto
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.docx', '.doc']:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.pptx', '.ppt']:
            from langchain_community.document_loaders import UnstructuredPowerPointLoader
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.xlsx', '.xls']:
            from langchain_community.document_loaders import UnstructuredExcelLoader
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.txt', '.md', '.rtf']:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.html', '.htm']:
            from langchain_community.document_loaders import BSHTMLLoader
            loader = BSHTMLLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension == '.xml':
            from langchain_community.document_loaders import UnstructuredXMLLoader
            loader = UnstructuredXMLLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.csv', '.tsv']:
            from langchain_community.document_loaders import CSVLoader
            loader = CSVLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.json', '.yaml', '.yml']:
            from langchain_community.document_loaders import JSONLoader
            loader = JSONLoader(file_path, jq_schema='.', text_content=False)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            # Para imágenes, intentar con OCR
            try:
                from langchain_community.document_loaders import UnstructuredImageLoader
                loader = UnstructuredImageLoader(file_path)
                documents = loader.load()
                return "\n\n".join([doc.page_content for doc in documents])
            except:
                # Si falla, intentar con TextLoader como último recurso
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
                return "\n\n".join([doc.page_content for doc in documents])
        
        elif file_extension in ['.eml', '.msg']:
            from langchain_community.document_loaders import UnstructuredEmailLoader
            loader = UnstructuredEmailLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        
        else:
            # Para otros formatos, intentar con TextLoader
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
            
    except Exception as e:
        log(f"Core Warning: Fallback de LangChain falló: {e}")
        return ""

def load_document_with_fallbacks(file_path: str) -> tuple[str, dict]:
    """
    Carga documento con múltiples estrategias de fallback.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        Tupla con (contenido_texto, metadatos)
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Estrategia 1: Unstructured con configuración óptima
    try:
        log(f"Core: Intentando carga con Unstructured (configuración óptima)...")
        config = UNSTRUCTURED_CONFIGS.get(file_extension, DEFAULT_CONFIG)
        
        # Para PDFs, usar configuración más rápida para evitar colgadas
        if file_extension == '.pdf':
            log(f"Core: PDF detectado, usando configuración rápida para evitar timeouts...")
            config = config.copy()
            config['strategy'] = 'fast'
            config['max_partition'] = 1000
            config['new_after_n_chars'] = 800
        
        elements = partition(filename=file_path, **config)
        
        # Procesar elementos de manera inteligente
        processed_text = process_unstructured_elements(elements)
        
        # Extraer metadatos estructurales
        metadata = extract_structural_metadata(elements, file_path)
        
        if processed_text and not processed_text.isspace():
            log(f"Core: Carga exitosa con Unstructured (configuración óptima)")
            return processed_text, metadata
    
    except Exception as e:
        log(f"Core Warning: Unstructured (configuración óptima) falló: {e}")
    
    # Estrategia 2: Unstructured con configuración básica
    try:
        log(f"Core: Intentando carga con Unstructured (configuración básica)...")
        elements = partition(filename=file_path, strategy="fast", max_partition=1000)
        processed_text = process_unstructured_elements(elements)
        metadata = extract_structural_metadata(elements, file_path)
        
        if processed_text and not processed_text.isspace():
            log(f"Core: Carga exitosa con Unstructured (configuración básica)")
            return processed_text, metadata
    
    except Exception as e:
        log(f"Core Warning: Unstructured (configuración básica) falló: {e}")
    
    # Estrategia 3: Cargadores específicos de LangChain
    try:
        log(f"Core: Intentando carga con cargadores específicos de LangChain...")
        fallback_text = load_with_langchain_fallbacks(file_path)
        
        if fallback_text and not fallback_text.isspace():
            metadata = {
                "source": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": file_extension,
                "processed_date": datetime.now().isoformat(),
                "processing_method": "langchain_fallback",
                "structural_info": {
                    "total_elements": 1,
                    "titles_count": 0,
                    "tables_count": 0,
                    "lists_count": 0,
                    "narrative_blocks": 1,
                    "other_elements": 0,
                    "total_text_length": len(fallback_text),
                    "avg_element_length": len(fallback_text)
                }
            }
            log(f"Core: Carga exitosa con cargadores específicos de LangChain")
            return fallback_text, metadata
    
    except Exception as e:
        log(f"Core Warning: Cargadores específicos de LangChain fallaron: {e}")
    
    # Si todas las estrategias fallan
    log(f"Core Error: Todas las estrategias de carga fallaron para '{file_path}'")
    return "", {}

def add_text_to_knowledge_base_enhanced(text: str, vector_store: Chroma, source_metadata: dict = None, use_semantic_chunking: bool = True):
    """
    Versión mejorada que soporta chunking semántico y metadatos estructurales.
    
    Args:
        text: El texto a añadir
        vector_store: La base de datos vectorial
        source_metadata: Diccionario con metadatos de la fuente
        use_semantic_chunking: Si usar chunking semántico en lugar del tradicional
    """
    if not text or text.isspace():
        log("Core Advertencia: Se intentó añadir texto vacío o solo espacios en blanco.")
        return

    # Limpiar el texto antes de procesarlo
    log(f"Core: Limpiando y preparando texto para procesamiento RAG...")
    cleaned_text = clean_text_for_rag(text)
    
    if not cleaned_text or cleaned_text.isspace():
        log("Core Advertencia: El texto quedó vacío después de la limpieza.")
        return

    if use_semantic_chunking and source_metadata and 'structural_info' in source_metadata:
        # Usar chunking semántico si tenemos información estructural
        log(f"Core: Usando chunking semántico basado en estructura del documento...")
        # Para chunking semántico, necesitaríamos los elementos originales
        # Por ahora, usamos el chunking tradicional pero con parámetros optimizados
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Chunks más pequeños para mejor precisión
            chunk_overlap=150,  # Overlap moderado
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    else:
        # Usar chunking tradicional mejorado
        log(f"Core: Usando chunking tradicional mejorado...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
            chunk_overlap=200,
        length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    texts = text_splitter.split_text(cleaned_text)
    log(f"Core: Texto dividido en {len(texts)} fragmentos")
    
    # Preparar metadatos para cada chunk
    if source_metadata:
        metadatas = []
        for i in range(len(texts)):
            # Crear una copia limpia de los metadatos
            metadata = {}
            
            # Copiar metadatos básicos
            for key, value in source_metadata.items():
                if key != 'structural_info':
                    metadata[key] = value
            
            # Convertir structural_info a metadatos planos
            if 'structural_info' in source_metadata:
                structural_info = source_metadata['structural_info']
                if isinstance(structural_info, dict):
                    for struct_key, struct_value in structural_info.items():
                        # Convertir a string si es necesario para ChromaDB
                        if isinstance(struct_value, (int, float, bool)):
                            metadata[f'structural_{struct_key}'] = struct_value
                        else:
                            metadata[f'structural_{struct_key}'] = str(struct_value)
            
            # Añadir información del chunk
            metadata['chunk_index'] = i
            metadata['total_chunks'] = len(texts)
            
            metadatas.append(metadata)
        
        log(f"Core: Añadiendo metadatos de fuente: {source_metadata.get('source', 'unknown')}")
    else:
        metadatas = None
    
    log(f"Core: Generando embeddings y añadiendo a la base de datos...")
    if metadatas:
        vector_store.add_texts(texts, metadatas=metadatas)
    else:
        vector_store.add_texts(texts)
    vector_store.persist()
    log(f"Core: {len(texts)} fragmentos añadidos y guardados en la base de conocimientos")

def add_text_to_knowledge_base(text: str, vector_store: Chroma, source_metadata: dict = None):
    """
    Función original para mantener compatibilidad con código existente.
    Divide el texto, lo añade a la base de datos con metadatos de fuente y lo persiste.
    
    Args:
        text: El texto a añadir
        vector_store: La base de datos vectorial
        source_metadata: Diccionario con metadatos de la fuente (ej: {"source": "archivo.pdf", "author": "Juan Pérez"})
    """
    # Usar la versión mejorada por defecto
    add_text_to_knowledge_base_enhanced(text, vector_store, source_metadata, use_semantic_chunking=False)

def load_document_with_unstructured(file_path: str) -> str:
    """
    Carga un documento usando el sistema mejorado de Unstructured con fallbacks.
    Esta función mantiene compatibilidad con el código existente.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        Contenido del archivo como texto
    """
    content, _ = load_document_with_fallbacks(file_path)
    return content

def get_qa_chain(vector_store: Chroma) -> RetrievalQA:
    """Crea y retorna la cadena de Pregunta/Respuesta usando un LLM local."""
    log(f"Core: Inicializando modelo de lenguaje local (Ollama)...")
    llm = ChatOllama(model="llama3", temperature=0)
    log(f"Core: Configurando cadena RAG con recuperación de fuentes mejorada...")
    
    # Configurar el retriever con parámetros optimizados para mejor recuperación
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",  # Cambiado para soportar filtrado por score
        search_kwargs={
            "k": 5,  # Aumentar a 5 fragmentos para más contexto
            "score_threshold": 0.3,  # Umbral de distancia. Similitud > 0.7 = Distancia < 0.3
        }
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,  # Incluir documentos fuente
        chain_type_kwargs={
            "verbose": False  # Reducir verbosidad en producción
        }
    )
    log(f"Core: Cadena RAG configurada exitosamente con seguimiento de fuentes mejorado")
    return qa_chain 