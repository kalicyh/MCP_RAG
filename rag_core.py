import os
from dotenv import load_dotenv
import torch
import sys
from tqdm import tqdm
import requests
import re

from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
# CAMBIO: Quitamos OpenAI, importamos el wrapper para embeddings locales
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
EMBEDDING_MODEL_NAME = "paraphrase-MiniLM-L3-v2"

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

def add_text_to_knowledge_base(text: str, vector_store: Chroma, source_metadata: dict = None):
    """
    Divide el texto, lo añade a la base de datos con metadatos de fuente y lo persiste.
    
    Args:
        text: El texto a añadir
        vector_store: La base de datos vectorial
        source_metadata: Diccionario con metadatos de la fuente (ej: {"source": "archivo.pdf", "author": "Juan Pérez"})
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

    log(f"Core: Dividiendo texto en fragmentos usando divisor inteligente...")
    # Usar RecursiveCharacterTextSplitter para una división más inteligente
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,  # Aumentar overlap para mejor contexto
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Separadores inteligentes
    )
    texts = text_splitter.split_text(cleaned_text)
    log(f"Core: Texto dividido en {len(texts)} fragmentos")
    
    # Preparar metadatos para cada chunk
    if source_metadata:
        metadatas = [source_metadata.copy() for _ in texts]
        log(f"Core: Añadiendo metadatos de fuente: {source_metadata}")
    else:
        metadatas = None
    
    log(f"Core: Generando embeddings y añadiendo a la base de datos...")
    if metadatas:
        vector_store.add_texts(texts, metadatas=metadatas)
    else:
        vector_store.add_texts(texts)
    vector_store.persist()
    log(f"Core: {len(texts)} fragmentos añadidos y guardados en la base de conocimientos")

def get_qa_chain(vector_store: Chroma) -> RetrievalQA:
    """Crea y retorna la cadena de Pregunta/Respuesta usando un LLM local."""
    log(f"Core: Inicializando modelo de lenguaje local (Ollama)...")
    llm = ChatOllama(model="llama3", temperature=0)
    log(f"Core: Configurando cadena RAG con recuperación de fuentes mejorada...")
    
    # Configurar el retriever con parámetros optimizados para mejor recuperación
    retriever = vector_store.as_retriever(
        search_type="similarity",  # Tipo de búsqueda por similitud
        search_kwargs={
            "k": 5,  # Aumentar a 5 fragmentos para más contexto
            "score_threshold": 0.6,  # Solo documentos con similitud > 70%
            "fetch_k": 10  # Buscar 10 documentos y luego filtrar los mejores 5
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