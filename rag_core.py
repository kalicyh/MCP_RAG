import os
from dotenv import load_dotenv
import torch
import sys
from tqdm import tqdm
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import unicodedata

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

def fix_duplicated_characters(text: str) -> str:
    """
    Corrige caracteres duplicados que pueden aparecer por problemas de codificación.
    NO toca los números para evitar corregir datos legítimos.
    
    Args:
        text: Texto con posibles caracteres duplicados
    
    Returns:
        Texto con caracteres duplicados corregidos (solo letras y espacios)
    """
    if not text:
        return ""
    
    # Patrones de caracteres duplicados SEGUROS (solo letras y espacios)
    safe_duplicated_patterns = [
        # Letras duplicadas
        ('AA', 'A'), ('BB', 'B'), ('CC', 'C'), ('DD', 'D'), ('EE', 'E'),
        ('FF', 'F'), ('GG', 'G'), ('HH', 'H'), ('II', 'I'), ('JJ', 'J'),
        ('KK', 'K'), ('LL', 'L'), ('MM', 'M'), ('NN', 'N'), ('OO', 'O'),
        ('PP', 'P'), ('QQ', 'Q'), ('RR', 'R'), ('SS', 'S'), ('TT', 'T'),
        ('UU', 'U'), ('VV', 'V'), ('WW', 'W'), ('XX', 'X'), ('YY', 'Y'),
        ('ZZ', 'Z'),
        
        # Letras minúsculas duplicadas
        ('aa', 'a'), ('bb', 'b'), ('cc', 'c'), ('dd', 'd'), ('ee', 'e'),
        ('ff', 'f'), ('gg', 'g'), ('hh', 'h'), ('ii', 'i'), ('jj', 'j'),
        ('kk', 'k'), ('ll', 'l'), ('mm', 'm'), ('nn', 'n'), ('oo', 'o'),
        ('pp', 'p'), ('qq', 'q'), ('rr', 'r'), ('ss', 's'), ('tt', 't'),
        ('uu', 'u'), ('vv', 'v'), ('ww', 'w'), ('xx', 'x'), ('yy', 'y'),
        ('zz', 'z'),
        
        # Espacios duplicados
        ('  ', ' '), ('   ', ' '), ('    ', ' '),
        
        # Puntuación duplicada
        ('..', '.'), ('...', '...'), ('!!', '!'), ('??', '?'),
        (',,', ','), (';;', ';'), ('::', ':'),
    ]
    
    # Aplicar correcciones SEGURAS de patrones duplicados
    for duplicated, corrected in safe_duplicated_patterns:
        text = text.replace(duplicated, corrected)
    
    # Detectar y corregir secuencias largas de caracteres duplicados
    # PERO IGNORAR COMPLETAMENTE LOS NÚMEROS
    import re
    
    # Buscar secuencias de 3 o más caracteres iguales consecutivos
    def fix_long_duplications(match):
        char = match.group(1)
        count = len(match.group(0))
        
        # IGNORAR COMPLETAMENTE LOS NÚMEROS
        if char.isdigit():
            return match.group(0)  # Mantener números tal como están
        else:
            # Para letras y otros caracteres, ser más agresivo
            if count > 2:
                return char
            return match.group(0)
    
    # Aplicar corrección de secuencias largas
    text = re.sub(r'(.)\1{2,}', fix_long_duplications, text)
    
    # Corregir casos específicos de palabras comunes duplicadas
    common_duplicated_words = {
        'CCOOMMPPOONNEENNTTEESS': 'COMPONENTES',
        'DDOOSS': 'DOS',
        'DDEELL': 'DEL',
        'PPAARRA': 'PARA',
        'CCOONN': 'CON',
        'PPRROO': 'PRO',
        'IINNFFOORRMMAACCIIOONN': 'INFORMACION',
        'MMAANNUUAALL': 'MANUAL',
        'RREEPPAARRAACCIIOONN': 'REPARACION',
        'MMAANNTTEENNIIMMIIEENNTTOO': 'MANTENIMIENTO',
    }
    
    for duplicated_word, corrected_word in common_duplicated_words.items():
        text = text.replace(duplicated_word, corrected_word)
    
    return text

def normalize_spanish_characters(text: str) -> str:
    """
    Normaliza caracteres especiales del español que pueden causar problemas de codificación.
    Incluye corrección de caracteres duplicados.
    
    Args:
        text: Texto original con posibles problemas de codificación
    
    Returns:
        Texto con caracteres normalizados
    """
    if not text:
        return ""
    
    # Primero corregir caracteres duplicados
    text = fix_duplicated_characters(text)
    
    # Mapeo de caracteres problemáticos comunes en español
    character_mapping = {
        # Caracteres acentuados mal codificados - casos específicos
        "M´etodo": "Método",
        "An´alisis": "Análisis", 
        "Bisecci´on": "Bisección",
        "Convergencia": "Convergencia",
        "M´etodos": "Métodos",
        "An´alisis": "Análisis",
        
        # Caracteres acentuados mal codificados - patrones generales
        '´': "'",  # Acento agudo mal codificado
        '`': "'",  # Acento grave mal codificado
        
        # Caracteres especiales mal codificados
        'ﬁ': 'fi',  # Ligadura fi
        'ﬂ': 'fl',  # Ligadura fl
        'ﬀ': 'ff',  # Ligadura ff
        'ﬃ': 'ffi', # Ligadura ffi
        'ﬄ': 'ffl', # Ligadura ffl
        
        # Otros caracteres problemáticos
        '…': '...',  # Puntos suspensivos
        '–': '-',    # Guión medio
        '—': '-',    # Guión largo
        '"': '"',    # Comillas tipográficas
        '"': '"',    # Comillas tipográficas
        ''': "'",    # Apóstrofe tipográfico
        ''': "'",    # Apóstrofe tipográfico
        
        # Caracteres de control que pueden aparecer
        '\x00': '',  # Null character
        '\x01': '',  # Start of heading
        '\x02': '',  # Start of text
        '\x03': '',  # End of text
        '\x04': '',  # End of transmission
        '\x05': '',  # Enquiry
        '\x06': '',  # Acknowledge
        '\x07': '',  # Bell
        '\x08': '',  # Backspace
        '\x0b': '',  # Vertical tab
        '\x0c': '',  # Form feed
        '\x0e': '',  # Shift out
        '\x0f': '',
        '\x10': '',  # Data link escape
        '\x11': '',  # Device control 1
        '\x12': '',  # Device control 2
        '\x13': '',  # Device control 3
        '\x14': '',  # Device control 4
        '\x15': '',  # Negative acknowledge
        '\x16': '',  # Synchronous idle
        '\x17': '',  # End of transmission block
        '\x18': '',  # Cancel
        '\x19': '',  # End of medium
        '\x1a': '',  # Substitute
        '\x1b': '',  # Escape
        '\x1c': '',  # File separator
        '\x1d': '',  # Group separator
        '\x1e': '',  # Record separator
        '\x1f': '',  # Unit separator
    }
    
    # Aplicar mapeo de caracteres específicos primero
    for old_char, new_char in character_mapping.items():
        text = text.replace(old_char, new_char)
    
    # Normalizar caracteres Unicode (NFD -> NFC)
    try:
        text = unicodedata.normalize('NFC', text)
    except Exception as e:
        log(f"Core Warning: Error normalizando Unicode: {e}")
    
    # Corregir patrones específicos de acentos mal codificados
    # Patrón: letra + acento mal codificado
    accent_patterns = [
        (r'([aeiouAEIOU])´', r'\1á'),  # a´ -> á
        (r'([aeiouAEIOU])`', r'\1à'),  # a` -> à
    ]
    
    for pattern, replacement in accent_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Corregir casos específicos de ñ mal codificada
    # Casos de ñ con caracteres Unicode combinados
    text = text.replace('ã', 'ñ')  # Corregir ñ mal codificada
    text = text.replace('ĩ', 'ñ')  # Otro caso de ñ mal codificada
    
    # Casos específicos de ñ con caracteres Unicode combinados
    # Estos son casos donde la ñ se representa como n + tilde combinada
    text = text.replace('ñ', 'ñ')  # Normalizar ñ ya correcta
    text = text.replace('ñ', 'ñ')  # n + tilde combinada (U+006E + U+0303)
    text = text.replace('Ñ', 'Ñ')  # N + tilde combinada (U+004E + U+0303)
    
    # Corregir casos específicos de acentos que quedaron mal
    text = text.replace("M'etodo", "Método")
    text = text.replace("An'alisis", "Análisis")
    text = text.replace("Bisecci'on", "Bisección")
    text = text.replace("M'etodos", "Métodos")
    
    # Corregir casos específicos de ñ que quedaron mal
    text = text.replace("espña", "españa")
    text = text.replace("nño", "niño")
    text = text.replace("espãa", "españa")
    text = text.replace("nĩo", "niño")
    
    return text

def clean_text_for_rag(text: str) -> str:
    """
    Limpia y prepara el texto para mejorar la calidad de las búsquedas RAG.
    Incluye normalización de caracteres especiales del español.
    
    Args:
        text: Texto original a limpiar
    
    Returns:
        Texto limpio y optimizado para RAG
    """
    if not text:
        return ""
    
    # Primero normalizar caracteres especiales del español
    text = normalize_spanish_characters(text)
    
    # Eliminar espacios múltiples y saltos de línea excesivos
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres especiales problemáticos pero mantener puntuación importante y caracteres españoles
    # Mantener: letras, números, espacios, puntuación básica, caracteres acentuados
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'áéíóúÁÉÍÓÚñÑüÜ]', '', text)
    
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
    Incluye normalización de caracteres especiales del español.
    
    Args:
        table_element: Elemento de tabla de Unstructured
    
    Returns:
        Texto formateado de la tabla con caracteres normalizados
    """
    try:
        if hasattr(table_element, 'text'):
            # Normalizar caracteres del texto de la tabla
            normalized_text = normalize_spanish_characters(table_element.text)
            return normalized_text
        elif hasattr(table_element, 'metadata') and 'text_as_html' in table_element.metadata:
            # Si tenemos HTML, extraer el texto
            html_text = table_element.metadata['text_as_html']
            # Limpiar tags HTML básicos
            clean_text = re.sub(r'<[^>]+>', ' ', html_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            # Normalizar caracteres del texto extraído
            normalized_text = normalize_spanish_characters(clean_text)
            return f"Tabla: {normalized_text}"
        else:
            # Normalizar caracteres de la representación en string
            text_representation = str(table_element)
            normalized_text = normalize_spanish_characters(text_representation)
            return normalized_text
    except Exception as e:
        log(f"Core Warning: Error convirtiendo tabla: {e}")
        # Intentar normalizar incluso en caso de error
        try:
            text_representation = str(table_element)
            return normalize_spanish_characters(text_representation)
        except:
            return str(table_element)

def process_unstructured_elements(elements: List[Any]) -> str:
    """
    Procesa elementos de Unstructured de manera inteligente preservando la estructura semántica.
    Incluye normalización de caracteres especiales del español.
    
    Args:
        elements: Lista de elementos extraídos por Unstructured
    
    Returns:
        Texto procesado con estructura preservada y caracteres normalizados
    """
    processed_parts = []
    
    for element in elements:
        element_type = type(element).__name__
        
        if element_type == 'Title':
            # Los títulos van en líneas separadas con formato especial
            if hasattr(element, 'text') and element.text:
                # Normalizar caracteres del título
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(f"\n## {normalized_text}\n")
        elif element_type == 'ListItem':
            # Las listas mantienen su estructura
            if hasattr(element, 'text') and element.text:
                # Normalizar caracteres del elemento de lista
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(f"• {normalized_text}")
        elif element_type == 'Table':
            # Las tablas se convierten a formato legible
            table_text = convert_table_to_text(element)
            if table_text:
                # Normalizar caracteres de la tabla
                normalized_table_text = normalize_spanish_characters(table_text)
                processed_parts.append(f"\n{normalized_table_text}\n")
        elif element_type == 'NarrativeText':
            # El texto narrativo va tal como está
            if hasattr(element, 'text') and element.text:
                # Normalizar caracteres del texto narrativo
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(normalized_text)
        else:
            # Para otros tipos, usar el texto básico
            if hasattr(element, 'text') and element.text:
                # Normalizar caracteres de otros elementos
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(normalized_text)
    
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
    Incluye normalización de caracteres especiales del español.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        Contenido del archivo como texto normalizado
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.docx', '.doc']:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.pptx', '.ppt']:
            from langchain_community.document_loaders import UnstructuredPowerPointLoader
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.xlsx', '.xls']:
            from langchain_community.document_loaders import UnstructuredExcelLoader
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.txt', '.md', '.rtf']:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.html', '.htm']:
            from langchain_community.document_loaders import BSHTMLLoader
            loader = BSHTMLLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension == '.xml':
            from langchain_community.document_loaders import UnstructuredXMLLoader
            loader = UnstructuredXMLLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.csv', '.tsv']:
            from langchain_community.document_loaders import CSVLoader
            loader = CSVLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.json', '.yaml', '.yml']:
            from langchain_community.document_loaders import JSONLoader
            loader = JSONLoader(file_path, jq_schema='.', text_content=False)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            # Para imágenes, intentar con OCR
            try:
                from langchain_community.document_loaders import UnstructuredImageLoader
                loader = UnstructuredImageLoader(file_path)
                documents = loader.load()
                # Normalizar cada documento antes de concatenar
                normalized_contents = []
                for doc in documents:
                    normalized_content = normalize_spanish_characters(doc.page_content)
                    normalized_contents.append(normalized_content)
                return "\n\n".join(normalized_contents)
            except:
                # Si falla, intentar con TextLoader como último recurso
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
                # Normalizar cada documento antes de concatenar
                normalized_contents = []
                for doc in documents:
                    normalized_content = normalize_spanish_characters(doc.page_content)
                    normalized_contents.append(normalized_content)
                return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.eml', '.msg']:
            from langchain_community.document_loaders import UnstructuredEmailLoader
            loader = UnstructuredEmailLoader(file_path)
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        else:
            # Para otros formatos, intentar con TextLoader
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            # Normalizar cada documento antes de concatenar
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
            
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

def flatten_metadata(metadata: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Aplana un diccionario de metadatos anidados para que sea compatible con ChromaDB.
    
    Args:
        metadata: Diccionario de metadatos que puede contener estructuras anidadas
        prefix: Prefijo para las claves aplanadas (usado en recursión)
    
    Returns:
        Diccionario aplanado con solo valores simples (str, int, float, bool)
    """
    flattened = {}
    
    for key, value in metadata.items():
        new_key = f"{prefix}{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursivamente aplanar diccionarios anidados
            nested_flattened = flatten_metadata(value, f"{new_key}_")
            flattened.update(nested_flattened)
        elif isinstance(value, (list, tuple)):
            # Convertir listas y tuplas a string
            flattened[new_key] = str(value)
        elif isinstance(value, (str, int, float, bool)):
            # Valores simples que ChromaDB puede manejar
            flattened[new_key] = value
        else:
            # Cualquier otro tipo se convierte a string
            flattened[new_key] = str(value)
    
    return flattened

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
            # Crear una copia limpia de los metadatos y aplanarlos
            metadata = flatten_metadata(source_metadata)
            
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

def get_qa_chain(vector_store: Chroma, metadata_filter: dict = None) -> RetrievalQA:
    """
    Crea y retorna la cadena de Pregunta/Respuesta usando un LLM local.
    
    Args:
        vector_store: La base de datos vectorial
        metadata_filter: Diccionario con filtros de metadatos (ej: {"file_type": ".pdf", "processing_method": "unstructured_enhanced"})
    """
    log(f"Core: Inicializando modelo de lenguaje local (Ollama)...")
    llm = ChatOllama(model="llama3", temperature=0)
    log(f"Core: Configurando cadena RAG con recuperación de fuentes mejorada...")
    
    # Configurar parámetros de búsqueda
    search_kwargs = {
        "k": 5,  # Aumentar a 5 fragmentos para más contexto
        "score_threshold": 0.1,  # Umbral más bajo para obtener resultados
    }
    
    # Añadir filtros de metadatos si se proporcionan
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"Core: Aplicando filtros de metadatos: {metadata_filter}")
    
    # Configurar el retriever con parámetros optimizados para mejor recuperación
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",  # Cambiado para soportar filtrado por score
        search_kwargs=search_kwargs
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

def search_with_metadata_filters(vector_store: Chroma, query: str, metadata_filter: dict = None, k: int = 5) -> List[Any]:
    """
    Realiza una búsqueda con filtros de metadatos opcionales.
    
    Args:
        vector_store: La base de datos vectorial
        query: La consulta de búsqueda
        metadata_filter: Diccionario con filtros de metadatos
        k: Número de resultados a retornar
    
    Returns:
        Lista de documentos que coinciden con la consulta y filtros
    """
    log(f"Core: Realizando búsqueda con filtros de metadatos...")
    
    # Configurar parámetros de búsqueda
    search_kwargs = {
        "k": k,
        "score_threshold": 0.1,  # Umbral más bajo para obtener resultados
    }
    
    # Añadir filtros si se proporcionan
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"Core: Filtros aplicados: {metadata_filter}")
    
    # Realizar búsqueda
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs
    )
    
    results = retriever.get_relevant_documents(query)
    log(f"Core: Búsqueda completada - {len(results)} resultados encontrados")
    
    return results

def create_simple_metadata_filter(file_type: str = None, processing_method: str = None, 
                                 min_tables: int = None, min_titles: int = None) -> dict:
    """
    Crea un filtro de metadatos simple compatible con ChromaDB.
    Esta versión maneja mejor los filtros múltiples.
    
    Args:
        file_type: Tipo de archivo (ej: ".pdf", ".docx")
        processing_method: Método de procesamiento (ej: "unstructured_enhanced")
        min_tables: Mínimo número de tablas en el documento
        min_titles: Mínimo número de títulos en el documento
    
    Returns:
        Diccionario con filtros de metadatos compatibles con ChromaDB
    """
    # ChromaDB requiere un formato específico para filtros múltiples
    # Usar operador $and para combinar múltiples condiciones
    
    conditions = []
    
    # Añadir filtros simples
    if file_type:
        conditions.append({"file_type": file_type})
    
    if processing_method:
        conditions.append({"processing_method": processing_method})
    
    # Añadir filtros numéricos - usar los nombres correctos de metadatos aplanados
    if min_tables is not None:
        conditions.append({"structural_info_tables_count": {"$gte": min_tables}})
    
    if min_titles is not None:
        conditions.append({"structural_info_titles_count": {"$gte": min_titles}})
    
    # Retornar el filtro apropiado
    if len(conditions) == 0:
        return {}
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}

def create_metadata_filter(file_type: str = None, processing_method: str = None, 
                          min_tables: int = None, min_titles: int = None,
                          source_contains: str = None) -> dict:
    """
    Crea un filtro de metadatos para búsquedas específicas.
    
    Args:
        file_type: Tipo de archivo (ej: ".pdf", ".docx")
        processing_method: Método de procesamiento (ej: "unstructured_enhanced")
        min_tables: Mínimo número de tablas en el documento
        min_titles: Mínimo número de títulos en el documento
        source_contains: Texto que debe contener el nombre de la fuente
    
    Returns:
        Diccionario con filtros de metadatos compatibles con ChromaDB
    """
    # Usar la versión mejorada
    return create_simple_metadata_filter(file_type, processing_method, min_tables, min_titles)

def get_document_statistics(vector_store: Chroma) -> dict:
    """
    Obtiene estadísticas sobre los documentos en la base de datos.
    
    Args:
        vector_store: La base de datos vectorial
    
    Returns:
        Diccionario con estadísticas de la base de datos
    """
    log(f"Core: Obteniendo estadísticas de la base de datos...")
    
    try:
        # Obtener todos los documentos para análisis
        all_docs = vector_store.get()
        
        if not all_docs or not all_docs['documents']:
            return {"total_documents": 0, "message": "Base de datos vacía"}
        
        documents = all_docs['documents']
        metadatas = all_docs.get('metadatas', [])
        
        stats = {
            "total_documents": len(documents),
            "file_types": {},
            "processing_methods": {},
            "structural_stats": {
                "documents_with_tables": 0,
                "documents_with_lists": 0,
                "documents_with_titles": 0,
                "avg_tables_per_doc": 0,
                "avg_titles_per_doc": 0,
                "avg_lists_per_doc": 0
            }
        }
        
        total_tables = 0
        total_titles = 0
        total_lists = 0
        
        for metadata in metadatas:
            # Contar tipos de archivo
            file_type = metadata.get("file_type", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            
            # Contar métodos de procesamiento
            processing_method = metadata.get("processing_method", "unknown")
            stats["processing_methods"][processing_method] = stats["processing_methods"].get(processing_method, 0) + 1
            
            # Estadísticas estructurales
            tables_count = metadata.get("structural_info_tables_count", 0)
            titles_count = metadata.get("structural_info_titles_count", 0)
            lists_count = metadata.get("structural_info_lists_count", 0)
            
            if tables_count > 0:
                stats["structural_stats"]["documents_with_tables"] += 1
                total_tables += tables_count
            
            if titles_count > 0:
                stats["structural_stats"]["documents_with_titles"] += 1
                total_titles += titles_count
            
            if lists_count > 0:
                stats["structural_stats"]["documents_with_lists"] += 1
                total_lists += lists_count
        
        # Calcular promedios
        if stats["total_documents"] > 0:
            stats["structural_stats"]["avg_tables_per_doc"] = total_tables / stats["total_documents"]
            stats["structural_stats"]["avg_titles_per_doc"] = total_titles / stats["total_documents"]
            stats["structural_stats"]["avg_lists_per_doc"] = total_lists / stats["total_documents"]
        
        log(f"Core: Estadísticas obtenidas - {stats['total_documents']} documentos")
        return stats
        
    except Exception as e:
        log(f"Core Error: Error obteniendo estadísticas: {e}")
        return {"error": str(e)} 