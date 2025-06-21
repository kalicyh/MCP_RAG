import os
from dotenv import load_dotenv
import torch
import sys
from tqdm import tqdm
import requests

from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
# CAMBIO: Quitamos OpenAI, importamos el wrapper para embeddings locales
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter

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
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def get_embedding_function():
    """
    Retorna la función de embeddings a usar. Ahora, un modelo local.
    Detecta automáticamente si hay una GPU disponible para usarla.
    """
    log(f"Core: Loading local embedding model: {EMBEDDING_MODEL_NAME}")
    log("Core: This step might take a few minutes on the first run to download the model.")
    log("Core: If the model is already downloaded, it will load quickly from the cache.")
    
    # Detectar si hay una GPU disponible y asignar el dispositivo correspondiente
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    log(f"Core: Using device '{device}' for embeddings.")
    
    # Configurar el modelo con progreso de descarga
    model_kwargs = {'device': device}
    
    # Intentar cargar el modelo con progreso visible
    try:
        log("Core: Attempting to load model (download will show progress if needed)...")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs=model_kwargs
        )
        log("Core: Model loaded successfully!")
        return embeddings
    except Exception as e:
        log(f"Core: Error loading model: {e}")
        log("Core: This might be a download issue. Please check your internet connection.")
        raise

def get_vector_store() -> Chroma:
    """Crea y retorna una instancia de la base de datos vectorial."""
    log(f"Core: Initializing vector database...")
    embeddings = get_embedding_function()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    log(f"Core: Vector database initialized at '{PERSIST_DIRECTORY}'")
    return vector_store

def add_text_to_knowledge_base(text: str, vector_store: Chroma, source_metadata: dict = None):
    """
    Divide el texto, lo añade a la base de datos con metadatos de fuente y lo persiste.
    
    Args:
        text: El texto a añadir
        vector_store: La base de datos vectorial
        source_metadata: Diccionario con metadatos de la fuente (ej: {"source": "archivo.pdf", "author": "Juan Pérez"})
    """
    if not text or text.isspace():
        log("Core Warning: Attempted to add empty or whitespace-only text.")
        return

    log(f"Core: Splitting text into chunks...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(text)
    log(f"Core: Text split into {len(texts)} chunks")
    
    # Preparar metadatos para cada chunk
    if source_metadata:
        metadatas = [source_metadata.copy() for _ in texts]
        log(f"Core: Adding source metadata: {source_metadata}")
    else:
        metadatas = None
    
    log(f"Core: Generating embeddings and adding to the database...")
    if metadatas:
        vector_store.add_texts(texts, metadatas=metadatas)
    else:
        vector_store.add_texts(texts)
    vector_store.persist()
    log(f"Core: {len(texts)} chunks added and persisted to the knowledge base")

def get_qa_chain(vector_store: Chroma) -> RetrievalQA:
    """Crea y retorna la cadena de Pregunta/Respuesta usando un LLM local."""
    log(f"Core: Initializing local language model (Ollama)...")
    llm = ChatOllama(model="llama3", temperature=0)
    log(f"Core: Configuring RAG chain with source retrieval...")
    
    # Configurar el retriever para incluir metadatos
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # Obtener los 3 fragmentos más relevantes
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True  # Incluir documentos fuente
    )
    log(f"Core: RAG chain configured successfully with source tracking")
    return qa_chain 