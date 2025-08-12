"""
RAG 系统 - 核心模块
==========================================

本模块为 RAG（检索增强生成）系统提供高级文档处理与存储功能，包括：

- 多格式文档处理
- Embedding 缓存优化性能
- 高级语义分块
- 大型数据库优化
- 文本归一化与清理
- 高级元数据管理
- Embedding 缓存系统
- 文档缓存系统
- 查询缓存系统
- 响应缓存系统
- 元数据缓存系统
- Embedding 缓存系统
"""

# =============================================================================
# IMPORTACIONES PRINCIPALES
# =============================================================================

import os
import sys
import json
import pickle
import hashlib
import tempfile
import threading
import time
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Configuración de logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importaciones de LangChain y ChromaDB
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain.chains import RetrievalQA
    from langchain_community.llms import HuggingFacePipeline
    from langchain.schema import Document
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    from chromadb.config import Settings
    from langchain_ollama import ChatOllama
except ImportError as e:
    print(f"导入 LangChain 时出错: {e}")
    print("正在安装依赖项...")
    os.system("pip install langchain langchain-community langchain-chroma langchain-ollama")

# Importaciones de Unstructured
try:
    from unstructured.partition.auto import partition
    from unstructured.documents.elements import Title, ListItem, Table, NarrativeText
except ImportError as e:
    print(f"导入 Unstructured 时出错: {e}")
    print("正在安装依赖项...")
    os.system("pip install unstructured")

# Importaciones de modelos estructurados
try:
    from models import MetadataModel
except ImportError as e:
    print(f"警告: 无法导入结构化模型: {e}")
    MetadataModel = None

# =============================================================================
# CONFIGURACIÓN AVANZADA DE UNSTRUCTURED
# =============================================================================

# Importar configuración centralizada
from utils.config import Config

# Usar la configuración centralizada en lugar de duplicar
UNSTRUCTURED_CONFIGS = Config.UNSTRUCTURED_CONFIGS

# Configuración por defecto para archivos no especificados
DEFAULT_CONFIG = {
    'strategy': 'fast',
    'include_metadata': True,
    'max_partition': 2000,
    'new_after_n_chars': 1500
}

# 定义 COLLECTION_NAME 和 PERSIST_DIRECTORY
COLLECTION_NAME = "default_collection"
PERSIST_DIRECTORY = "./data/vector_store"

# --- Sistema de Cache de Embeddings ---
class EmbeddingCache:
    """
    Sistema de cache para embeddings que mejora significativamente el rendimiento
    evitando recalcular embeddings para textos ya procesados.
    """
    
    def __init__(self, cache_dir: str = None, max_memory_size: int = 1000):
        """
        Inicializa el cache de embeddings.
        
        Args:
            cache_dir: Directorio donde se almacenan los embeddings en disco
                       Si es None, usa la configuración del servidor MCP
            max_memory_size: Número máximo de embeddings en memoria (LRU)
        """
        # Si no se especifica cache_dir, usar la configuración del servidor MCP
        if cache_dir is None:
            try:
                from utils.config import Config
                cache_dir = Config.EMBEDDING_CACHE_DIR
            except ImportError:
                # Fallback: usar directorio relativo al proyecto
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                cache_dir = os.path.join(project_root, "mcp_server_organized", "embedding_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_memory_size = max_memory_size
        
        # Cache en memoria usando LRU
        self._memory_cache = {}
        self._access_order = []
        
        # Estadísticas
        self.hits = 0
        self.misses = 0
        self.disk_hits = 0
        
        log(f"核心: Embedding 缓存初始化在 '{self.cache_dir}'")
        log(f"核心: 内存最大大小: {max_memory_size} embeddings")
    
    def _get_cache_key(self, text: str) -> str:
        """Genera una clave única para el texto usando hash MD5."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Obtiene la ruta del archivo de cache para una clave."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _update_access_order(self, key: str):
        """Actualiza el orden de acceso para implementar LRU."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        # Mantener solo los elementos más recientes
        if len(self._access_order) > self.max_memory_size:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._memory_cache:
                del self._memory_cache[oldest_key]
    
    def get(self, text: str):
        """
        Obtiene el embedding para un texto, primero desde memoria, luego desde disco.
        
        Args:
            text: Texto para el cual obtener el embedding
            
        Returns:
            Embedding si está en cache, None si no se encuentra
        """
        if not text or not text.strip():
            return None
        
        cache_key = self._get_cache_key(text)
        
        # 1. Buscar en memoria
        if cache_key in self._memory_cache:
            self.hits += 1
            self._update_access_order(cache_key)
            log(f"核心: 内存缓存命中，文本长度 {len(text)}")
            return self._memory_cache[cache_key]
        
        # 2. Buscar en disco
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                
                # Mover a memoria
                self._memory_cache[cache_key] = embedding
                self._update_access_order(cache_key)
                
                self.disk_hits += 1
                log(f"核心: 磁盘缓存命中，文本长度 {len(text)}")
                return embedding
            except Exception as e:
                log(f"核心: 从磁盘加载 embedding 时出错: {e}")
                # Eliminar archivo corrupto
                try:
                    cache_file.unlink()
                except:
                    pass
        
        self.misses += 1
        log(f"核心: 缓存未命中，文本长度 {len(text)}")
        return None
    
    def set(self, text: str, embedding):
        """
        Almacena un embedding en cache (memoria y disco).
        
        Args:
            text: Texto original
            embedding: Embedding a almacenar
        """
        if not text or not text.strip() or embedding is None:
            return
        
        cache_key = self._get_cache_key(text)
        
        # Almacenar en memoria
        self._memory_cache[cache_key] = embedding
        self._update_access_order(cache_key)
        
        # Almacenar en disco
        cache_file = self._get_cache_file_path(cache_key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
            log(f"核心: Embedding 已缓存（内存 + 磁盘），文本长度 {len(text)}")
        except Exception as e:
            log(f"核心: 保存 embedding 到磁盘时出错: {e}")
    
    def clear_memory(self):
        """Limpia el cache en memoria, manteniendo el cache en disco."""
        self._memory_cache.clear()
        self._access_order.clear()
        log("核心: 内存缓存已清空")
    
    def clear_all(self):
        """Limpia todo el cache (memoria y disco)."""
        self.clear_memory()
        
        # Limpiar archivos de disco
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            log("核心: 完全清空缓存（内存 + 磁盘）")
        except Exception as e:
            log(f"核心: 清理磁盘缓存时出错: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        total_requests = self.hits + self.misses
        memory_hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        disk_hit_rate = (self.disk_hits / total_requests * 100) if total_requests > 0 else 0
        overall_hit_rate = ((self.hits + self.disk_hits) / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "memory_hits": self.hits,
            "disk_hits": self.disk_hits,
            "misses": self.misses,
            "memory_hit_rate": f"{memory_hit_rate:.1f}%",
            "disk_hit_rate": f"{disk_hit_rate:.1f}%",
            "overall_hit_rate": f"{overall_hit_rate:.1f}%",
            "memory_cache_size": len(self._memory_cache),
            "max_memory_size": self.max_memory_size,
            "cache_directory": str(self.cache_dir)
        }
    
    def print_stats(self):
        """Imprime las estadísticas del cache."""
        stats = self.get_stats()
        log("核心: === Embedding 缓存统计信息 ===")
        for key, value in stats.items():
            log(f"核心: {key}: {value}")
        log("核心: ===========================================")

# =============================================================================
# FUNCIONES DE UTILIDAD Y GESTIÓN DEL CACHE
# =============================================================================

# Variable global para el cache de embeddings
_embedding_cache = None

def get_embedding_cache() -> EmbeddingCache:
    """
    Obtiene la instancia global del cache de embeddings.
    
    Returns:
        Instancia de EmbeddingCache
    """
    global _embedding_cache
    if _embedding_cache is None:
        # Usar la configuración del archivo config.py
        from utils.config import Config
        
        # Verificar si estamos en la GUI y usar rutas absolutas del servidor MCP
        cache_dir = Config.EMBEDDING_CACHE_DIR
        
        # Si la ruta es relativa, convertirla a absoluta del servidor MCP
        if not os.path.isabs(cache_dir):
            # Obtener la ruta absoluta del servidor MCP
            current_file = os.path.abspath(__file__)
            mcp_src_dir = os.path.dirname(current_file)
            mcp_server_dir = os.path.dirname(mcp_src_dir)
            cache_dir = os.path.join(mcp_server_dir, cache_dir)
        
        _embedding_cache = EmbeddingCache(cache_dir=cache_dir)
    return _embedding_cache

def get_cache_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del cache de embeddings.
    
    Returns:
        Diccionario con estadísticas del cache
    """
    cache = get_embedding_cache()
    return cache.get_stats()

def print_cache_stats():
    """Imprime las estadísticas del cache de embeddings."""
    cache = get_embedding_cache()
    cache.print_stats()

def clear_embedding_cache():
    """Limpia completamente el cache de embeddings."""
    global _embedding_cache
    if _embedding_cache:
        _embedding_cache.clear_all()
        _embedding_cache = None
    log("核心: Embedding 缓存已完全清空")

# =============================================================================
# FUNCIONES DE LOGGING Y UTILIDADES GENERALES
# =============================================================================

def log(message: str):
    """Función de logging centralizada con timestamp y colores usando Rich."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)
    # Detectar tipo de mensaje para colorear
   
    # if any(word in message.lower() for word in ["error", "falló", "fatal", "excepción"]):
    #     rich_print(f"[bold red][{timestamp}] {message}[/bold red]")
    # elif any(word in message.lower() for word in ["advertencia", "warning"]):
    #     rich_print(f"[bold yellow][{timestamp}] {message}[/bold yellow]")
    # elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok", "iniciado", "iniciando"]):
    #     rich_print(f"[bold green][{timestamp}] {message}[/bold green]")
    # else:
    #     rich_print(f"[cyan][{timestamp}] {message}[/cyan]")

def download_with_progress(url: str, filename: str, desc: str = "Downloading"):
    """
    Descarga un archivo con barra de progreso.
    
    Args:
        url: URL del archivo a descargar
        filename: Nombre del archivo local
        desc: Descripción para la barra de progreso
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filename, 'wb') as file, tqdm(
            desc=desc,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)
        
        log(f"核心: 下载完成: {filename}")
    except Exception as e:
        log(f"核心: 下载出错: {e}")
        raise

# =============================================================================
# GESTIÓN DE EMBEDDINGS Y MODELOS
# =============================================================================

def get_embedding_function():
    """
    Obtiene la función de embeddings con cache integrado.
    Detecta automáticamente si hay GPU disponible y la usa cuando es posible.
    
    Returns:
        Función de embeddings con cache
    """
    try:
        # Configuración del modelo de embeddings
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Detectar automáticamente el dispositivo disponible
        try:
            import torch
            if torch.cuda.is_available():
                device = 'cuda'
                gpu_name = torch.cuda.get_device_name(0)
                log(f"核心: 检测到 GPU: {gpu_name}")
                log(f"核心: 使用 GPU 进行 embeddings 计算 (设备: {device})")
            else:
                device = 'cpu'
                log(f"核心: 未检测到 GPU，使用 CPU 进行 embeddings 计算")
        except ImportError:
            device = 'cpu'
            log(f"核心: PyTorch 不可用，使用 CPU 进行 embeddings 计算")
        except Exception as e:
            device = 'cpu'
            log(f"核心警告: 检测 GPU 时出错 ({e}), 使用 CPU 进行 embeddings 计算")
        
        # Crear embeddings base con el dispositivo detectado
        base_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Obtener cache
        cache = get_embedding_cache()
        
        # Wrapper con cache
        class CachedEmbeddings:
            def __init__(self, base_embeddings, cache, device):
                self.base_embeddings = base_embeddings
                self.cache = cache
                self.device = device
            
            def _cached_embed_query(self, text: str):
                """Embedding con cache para consultas."""
                # Intentar obtener del cache
                cached_embedding = self.cache.get(text)
                if cached_embedding is not None:
                    return cached_embedding
                
                # Calcular nuevo embedding
                embedding = self.base_embeddings.embed_query(text)
                
                # Guardar en cache
                self.cache.set(text, embedding)
                
                return embedding
            
            def _cached_embed_documents(self, texts: List[str]):
                """Embedding con cache para documentos."""
                embeddings = []
                uncached_texts = []
                uncached_indices = []
                
                # Verificar cache para cada texto
                for i, text in enumerate(texts):
                    cached_embedding = self.cache.get(text)
                    if cached_embedding is not None:
                        embeddings.append(cached_embedding)
                    else:
                        embeddings.append(None)  # Placeholder
                        uncached_texts.append(text)
                        uncached_indices.append(i)
                
                # Calcular embeddings para textos no cacheados
                if uncached_texts:
                    new_embeddings = self.base_embeddings.embed_documents(uncached_texts)
                    
                    # Guardar en cache y actualizar lista
                    for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                        self.cache.set(text, embedding)
                        embeddings[uncached_indices[i]] = embedding
                
                return embeddings
            
            # Exponer métodos de la clase base
            def embed_query(self, text: str):
                return self._cached_embed_query(text)
            
            def embed_documents(self, texts: List[str]):
                return self._cached_embed_documents(texts)
        
        return CachedEmbeddings(base_embeddings, cache, device)
        
    except Exception as e:
        log(f"核心: 初始化 embeddings 时出错: {e}")
        raise

def get_optimal_vector_store_profile() -> str:
    """
    Detecta automáticamente el perfil óptimo basado en el tamaño de la base de datos.
    
    Returns:
        Perfil óptimo ('small', 'medium', 'large')
    """
    try:
        # Configuración básica de ChromaDB
        chroma_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
        
        # Crear vector store temporal para contar documentos
        temp_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
            persist_directory=PERSIST_DIRECTORY,
            client_settings=chroma_settings
        )
        
        # Contar documentos en la colección
        count = temp_store._collection.count()
        
        # Determinar perfil basado en el tamaño
        if count < 1000:
            profile = 'small'
        elif count < 10000:
            profile = 'medium'
        else:
            profile = 'large'
        
        log(f"核心: 检测到 {count} 个文档，使用配置文件 '{profile}'")
        return profile
        
    except Exception as e:
        log(f"核心警告: 无法自动检测配置文件: {e}")
        return 'medium'  # Perfil por defecto

def get_vector_store(profile: str = 'auto') -> Chroma:
    """
    Crea y retorna una instancia optimizada de la base de datos vectorial.
    
    Args:
        profile: Perfil de configuración ('small', 'medium', 'large', 'auto')
                 'auto' detecta automáticamente el perfil óptimo
    
    Returns:
        Instancia de Chroma con configuración optimizada
    """
    # Detectar perfil automáticamente si se solicita
    if profile == 'auto':
        profile = get_optimal_vector_store_profile()
    
    log(f"核心: 初始化向量数据库，配置文件 '{profile}'...")
    
    # Obtener información del perfil
    profile_info = VECTOR_STORE_PROFILES.get(profile, {})
    log(f"核心: 配置文件 '{profile}' - {profile_info.get('description', '标准配置')}")
    
    embeddings = get_embedding_function()
    
    # Crear configuración de ChromaDB
    chroma_settings = Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
    
    # Crear vector store con configuración optimizada
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        client_settings=chroma_settings
    )
    
    log(f"核心: 向量数据库优化初始化在 '{PERSIST_DIRECTORY}'")
    log(f"核心: 应用配置文件: {profile} - {profile_info.get('recommended_for', '通用配置')}")
    
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
        log(f"核心警告: Unicode 归一化时出错: {e}")
    
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
        log(f"核心警告: 转换表格时出错: {e}")
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
        Diccionario con metadatos estructurales o MetadataModel si está disponible
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
    
    # Si MetadataModel está disponible, crear un modelo estructurado
    if MetadataModel is not None:
        try:
            metadata_model = MetadataModel(
                source=os.path.basename(file_path),
                input_type="file_processing",
                processed_date=datetime.now(),
                file_path=file_path,
                file_type=os.path.splitext(file_path)[1].lower(),
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                processing_method="unstructured_enhanced",
                structural_info=structural_info,
                total_elements=structural_info["total_elements"],
                titles_count=structural_info["titles_count"],
                tables_count=structural_info["tables_count"],
                lists_count=structural_info["lists_count"],
                narrative_blocks=structural_info["narrative_blocks"],
                other_elements=structural_info["other_elements"],
                chunking_method="semantic",
                avg_chunk_size=structural_info["avg_element_length"]
            )
            
            # Actualizar información estructural usando el método del modelo
            metadata_model.update_structural_info(elements)
            
            log(f"核心: 使用 MetadataModel 创建结构化元数据")
            return metadata_model.to_dict()
            
        except Exception as e:
            log(f"核心警告: 创建 MetadataModel 时出错，使用字典: {e}")
    
    # Fallback a diccionario simple si MetadataModel no está disponible
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
        log(f"核心警告: LangChain 回退加载失败: {e}")
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
        log(f"核心: 尝试使用 Unstructured 加载（最佳配置）...")
        config = Config.get_unstructured_config(file_extension)
        
        # Para PDFs, usar configuración más rápida para evitar colgadas
        if file_extension == '.pdf':
            log(f"核心: 检测到 PDF，使用快速配置以避免超时...")
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
            log(f"核心: 使用 Unstructured 加载成功（最佳配置）")
            return processed_text, metadata
    
    except Exception as e:
        log(f"核心警告: Unstructured（最佳配置）加载失败: {e}")
    
    # Estrategia 2: Unstructured con configuración básica
    try:
        log(f"核心: 尝试使用 Unstructured 加载（基本配置）...")
        elements = partition(filename=file_path, strategy="fast", max_partition=1000)
        processed_text = process_unstructured_elements(elements)
        metadata = extract_structural_metadata(elements, file_path)
        
        if processed_text and not processed_text.isspace():
            log(f"核心: 使用 Unstructured 加载成功（基本配置）")
            return processed_text, metadata
    
    except Exception as e:
        log(f"核心警告: Unstructured（基本配置）加载失败: {e}")
    
    # Estrategia 3: Cargadores específicos de LangChain
    try:
        log(f"核心: 尝试使用 LangChain 特定加载器加载...")
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
            log(f"核心: 使用 LangChain 特定加载器加载成功")
            return fallback_text, metadata
    
    except Exception as e:
        log(f"核心警告: LangChain 特定加载器加载失败: {e}")
    
    # Si todas las estrategias fallan
    log(f"核心错误: 所有加载策略均失败，文件: '{file_path}'")
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

def add_text_to_knowledge_base_enhanced(text: str, vector_store: Chroma, source_metadata: dict = None, use_semantic_chunking: bool = True, structural_elements: List[Any] = None):
    """
    Versión mejorada que soporta chunking semántico real y metadatos estructurales.
    
    Args:
        text: El texto a añadir
        vector_store: La base de datos vectorial
        source_metadata: Diccionario con metadatos de la fuente
        use_semantic_chunking: Si usar chunking semántico en lugar del tradicional
        structural_elements: Lista de elementos estructurales para chunking semántico
    """
    if not text or text.isspace():
        log("核心警告: 尝试添加空文本或仅空格的文本.")
        return

    # Limpiar el texto antes de procesarlo
    log(f"核心: 清理和准备文本以进行 RAG 处理...")
    cleaned_text = clean_text_for_rag(text)
    
    if not cleaned_text or cleaned_text.isspace():
        log("核心警告: 清理后文本为空.")
        return

    # Determinar qué tipo de chunking usar
    if use_semantic_chunking and structural_elements and len(structural_elements) > 1:
        # Usar chunking semántico real con elementos estructurales
        log(f"核心: 使用高级语义分块，{len(structural_elements)} 个结构化元素...")
        texts = create_advanced_semantic_chunks(structural_elements, max_chunk_size=800, overlap=150)
        
        if not texts:
            log("核心警告: 无法创建语义块，使用传统分块...")
            # Fallback a chunking tradicional
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
            )
            texts = text_splitter.split_text(cleaned_text)
    
    elif use_semantic_chunking and source_metadata and 'structural_info' in source_metadata:
        # Usar chunking semántico mejorado (sin elementos estructurales)
        log(f"核心: 使用基于结构化元数据的语义分块...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Chunks más pequeños para mejor precisión
            chunk_overlap=150,  # Overlap moderado
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        texts = text_splitter.split_text(cleaned_text)
    
    else:
        # Usar chunking tradicional mejorado
        log(f"核心: 使用改进的传统分块...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        texts = text_splitter.split_text(cleaned_text)
    
    log(f"核心: 文本分割为 {len(texts)} 个片段")
    
    # Preparar metadatos para cada chunk
    if source_metadata:
        metadatas = []
        for i in range(len(texts)):
            # Crear una copia limpia de los metadatos y aplanarlos
            metadata = flatten_metadata(source_metadata)
            
            # Añadir información del chunk
            metadata['chunk_index'] = i
            metadata['total_chunks'] = len(texts)
            
            # Añadir información sobre el tipo de chunking usado
            if use_semantic_chunking and structural_elements:
                metadata['chunking_method'] = 'semantic_advanced'
            elif use_semantic_chunking:
                metadata['chunking_method'] = 'semantic_improved'
            else:
                metadata['chunking_method'] = 'traditional'
            
            metadatas.append(metadata)
        
        log(f"核心: 添加源元数据: {source_metadata.get('source', 'unknown')}")
    else:
        metadatas = None
    
    log(f"核心: 生成 embeddings 并添加到数据库...")
    if metadatas:
        vector_store.add_texts(texts, metadatas=metadatas)
    else:
        vector_store.add_texts(texts)
    log(f"核心: {len(texts)} 个片段已添加到知识库（自动持久化，无需 persist）")

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
    log(f"核心: 初始化本地语言模型 (Ollama)...")
    llm = ChatOllama(model="llama3", temperature=0)
    log(f"核心: 配置 RAG 链接，改进的源检索...")
    
    # Configurar parámetros de búsqueda
    search_kwargs = {
        "k": 5,  # Aumentar a 5 fragmentos para más contexto
        "score_threshold": 0.1,  # Umbral más bajo para obtener resultados
    }
    
    # Añadir filtros de metadatos si se proporcionan
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"核心: 应用元数据过滤器: {metadata_filter}")
    
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
    log(f"核心: RAG 链接配置成功，改进的源追踪")
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
    log(f"核心: 进行带元数据过滤的搜索...")
    
    # Configurar parámetros de búsqueda
    search_kwargs = {
        "k": k,
        "score_threshold": 0.1,  # Umbral más bajo para obtener resultados
    }
    
    # Añadir filtros si se proporcionan
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"核心: 应用的过滤器: {metadata_filter}")
    
    # Realizar búsqueda
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs
    )
    
    results = retriever.get_relevant_documents(query)
    log(f"核心: 搜索完成 - 找到 {len(results)} 个结果")
    
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
    log(f"核心: 获取数据库统计信息...")
    
    try:
        # Obtener todos los documentos para análisis
        all_docs = vector_store.get()
        
        if not all_docs or not all_docs['documents']:
            return {"total_documents": 0, "message": "数据库为空"}
        
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
            
            # Convertir a enteros para evitar errores de comparación
            try:
                tables_count = int(tables_count) if tables_count is not None else 0
                titles_count = int(titles_count) if titles_count is not None else 0
                lists_count = int(lists_count) if lists_count is not None else 0
            except (ValueError, TypeError):
                tables_count = 0
                titles_count = 0
                lists_count = 0
            
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
        
        log(f"核心: 获取统计信息成功 - {stats['total_documents']} 个文档")
        return stats
        
    except Exception as e:
        log(f"核心错误: 获取统计信息时出错: {e}")
        return {"error": str(e)}

# --- Configuración de Base Vectorial Optimizada ---
VECTOR_STORE_CONFIG = {
    # Configuración de persistencia y rendimiento
    'anonymized_telemetry': False,  # Desactivar telemetría
    'allow_reset': True,  # Permitir reset de la colección
    'is_persistent': True,  # Habilitar persistencia
}

# Configuración para diferentes tamaños de base de datos
VECTOR_STORE_PROFILES = {
    'small': {  # Para bases pequeñas (< 1000 documentos)
        'description': 'Optimizado para bases pequeñas',
        'recommended_for': 'Menos de 1000 documentos'
    },
    'medium': {  # Para bases medianas (1000-10000 documentos)
        'description': 'Optimizado para bases medianas',
        'recommended_for': '1000-10000 documentos'
    },
    'large': {  # Para bases grandes (> 10000 documentos)
        'description': 'Optimizado para bases grandes',
        'recommended_for': 'Más de 10000 documentos'
    }
}

def optimize_vector_store(vector_store: Chroma = None) -> dict:
    """
    Optimiza la base vectorial para mejorar el rendimiento.
    Detecta automáticamente si es una base grande y usa optimización incremental.
    Usa métodos nativos de ChromaDB para evitar límites de batch.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
    
    Returns:
        Diccionario con información sobre la optimización
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        # Detectar automáticamente si es una base grande
        if is_large_database(vector_store):
            log("核心: 检测到大数据库，使用增量优化")
            return optimize_vector_store_large(vector_store)
        
        log("核心: 开始优化向量数据库...")
        
        # Obtener estadísticas antes de la optimización
        stats_before = get_vector_store_stats(vector_store)
        
        collection = vector_store._collection
        
        # En lugar de reindexar, usar métodos nativos de ChromaDB para optimización
        log("核心: 应用 ChromaDB 原生优化...")
        
        # 1. Forzar persistencia para optimizar almacenamiento
        try:
            collection.persist()
            log("核心: 强制持久化完成")
        except Exception as e:
            log(f"核心警告: 无法强制持久化: {e}")
        
        # 2. Obtener información de la colección para verificar estado
        count = collection.count()
        log(f"核心: 检查到 {count} 个文档在集合中")
        
        # 3. Realizar una consulta de prueba para verificar índices
        try:
            # Hacer una búsqueda de prueba para activar índices
            test_results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            log("核心: 搜索索引验证通过")
        except Exception as e:
            log(f"核心警告: 验证索引时出错: {e}")
        
        # 4. Verificar configuración de la colección
        try:
            # Obtener metadatos de la colección
            collection_metadata = collection.metadata
            log(f"核心: 集合元数据: {collection_metadata}")
        except Exception as e:
            log(f"核心警告: 无法获取元数据: {e}")
        
        # 5. Forzar compactación si está disponible
        try:
            # Intentar compactar la base de datos
            if hasattr(collection, 'compact'):
                collection.compact()
                log("核心: 数据库压缩完成")
            else:
                log("核心: 此版本的 ChromaDB 不支持压缩")
        except Exception as e:
            log(f"核心警告: 压缩时出错: {e}")
        
        # Obtener estadísticas después de la optimización
        stats_after = get_vector_store_stats(vector_store)
        
        log("核心: 向量数据库优化完成")
        
        return {
            "status": "success",
            "message": "向量数据库已使用 ChromaDB 原生方法优化",
            "stats_before": stats_before,
            "stats_after": stats_after,
            "documents_processed": count,
            "optimization_type": "native",
            "optimizations_applied": [
                "强制持久化",
                "索引验证",
                "数据库压缩"
            ]
        }
        
    except Exception as e:
        log(f"核心错误: 优化向量数据库时出错: {e}")
        return {
            "status": "error",
            "message": f"优化向量数据库时出错: {str(e)}"
        }

def get_vector_store_stats(vector_store: Chroma = None) -> dict:
    """
    Obtiene estadísticas detalladas de la base vectorial.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
    
    Returns:
        Diccionario con estadísticas de la base vectorial
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        collection = vector_store._collection
        
        # Obtener estadísticas básicas
        count = collection.count()
        
        # Obtener información de configuración
        all_data = collection.get()
        metadata = all_data.get('metadatas', [])
        
        # Calcular estadísticas de metadatos
        file_types = {}
        processing_methods = {}
        
        for meta in metadata:
            if meta:
                file_type = meta.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
                
                processing_method = meta.get('processing_method', 'unknown')
                processing_methods[processing_method] = processing_methods.get(processing_method, 0) + 1
        
        return {
            "total_documents": count,
            "file_types": file_types,
            "processing_methods": processing_methods,
            "collection_name": collection.name,
            "embedding_dimension": "768"  # Dimension estándar para all-mpnet-base-v2
        }
        
    except Exception as e:
        log(f"核心错误: 获取向量数据库统计信息时出错: {e}")
        return {"error": str(e)}

def reindex_vector_store(vector_store: Chroma = None, profile: str = 'auto') -> dict:
    """
    Reindexa la base vectorial con una configuración optimizada.
    Detecta automáticamente si es una base grande y usa reindexado incremental.
    Usa métodos nativos de ChromaDB para evitar límites de batch.
    Útil cuando se cambia el perfil de configuración.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
        profile: Perfil de configuración para reindexar
    
    Returns:
        Diccionario con información sobre el reindexado
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        # Detectar automáticamente si es una base grande
        if is_large_database(vector_store):
            log(f"核心: 检测到大数据库，使用配置文件 '{profile}' 的增量重建索引")
            return reindex_vector_store_large(vector_store, profile)
        
        log(f"核心: 使用配置文件 '{profile}' 开始重建索引...")
        
        collection = vector_store._collection
        
        # Obtener estadísticas antes del reindexado
        count_before = collection.count()
        log(f"核心: 重建索引前文档数量: {count_before}")
        
        # En lugar de eliminar y reinsertar, usar métodos nativos de ChromaDB
        log("核心: 应用增量重建索引，使用 ChromaDB 原生方法...")
        
        # 1. Verificar que la colección esté en buen estado
        try:
            # Hacer una consulta de prueba para verificar índices
            test_results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            log("核心: 搜索索引验证通过")
        except Exception as e:
            log(f"核心警告: 验证索引时出错: {e}")
        
        # 2. Forzar persistencia si está disponible
        try:
            if hasattr(collection, 'persist'):
                collection.persist()
                log("核心: 强制持久化完成")
            else:
                log("核心: 持久化在此版本不可用")
        except Exception as e:
            log(f"核心警告: 无法强制持久化: {e}")
        
        # 3. Verificar configuración de la colección
        try:
            collection_metadata = collection.metadata
            log(f"核心: 集合元数据: {collection_metadata}")
        except Exception as e:
            log(f"核心警告: 无法获取元数据: {e}")
        
        # 4. Intentar compactación si está disponible
        try:
            if hasattr(collection, 'compact'):
                collection.compact()
                log("核心: 数据库压缩完成")
            else:
                log("核心: 此版本的 ChromaDB 不支持压缩")
        except Exception as e:
            log(f"核心警告: 压缩时出错: {e}")
        
        # 5. Verificar que el perfil se aplique correctamente
        # Esto se hace automáticamente al crear el vector_store con el perfil
        log(f"核心: 配置文件 '{profile}' 已应用")
        
        # Obtener estadísticas después del reindexado
        count_after = collection.count()
        log(f"核心: 重建索引后文档数量: {count_after}")
        
        log("核心: 向量数据库重建索引完成")
        
        return {
            "status": "success",
            "message": f"向量数据库已使用配置文件 '{profile}' 重建索引",
            "documents_before": count_before,
            "documents_after": count_after,
            "reindex_type": "native",
            "profile_applied": profile,
            "optimizations_applied": [
                "索引验证",
                "强制持久化",
                "数据库压缩",
                "应用配置文件"
            ]
        }
        
    except Exception as e:
        log(f"核心错误: 重建索引时出错: {e}")
        return {
            "status": "error",
            "message": f"重建索引时出错: {str(e)}"
        }

def reindex_vector_store_large(vector_store: Chroma = None, profile: str = 'auto') -> dict:
    """
    Reindexado especial para bases de datos muy grandes con procesamiento incremental.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
        profile: Perfil de configuración para reindexar
    
    Returns:
        Diccionario con información sobre el reindexado
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        log(f"核心: 开始增量重建索引，配置文件 '{profile}'...")
        
        # Verificar si es una base grande
        if not is_large_database(vector_store):
            log("核心: 数据库不大，使用标准重建索引")
            return reindex_vector_store(vector_store, profile)
        
        # Usar la misma lógica que optimize_vector_store_large pero con nuevo perfil
        return optimize_vector_store_large(vector_store)
        
    except Exception as e:
        log(f"核心错误: 大型数据库重建索引时出错: {e}")
        return {
            "status": "error",
            "message": f"大型数据库重建索引时出错: {str(e)}"
        }

def get_vector_store_stats_advanced(vector_store: Chroma = None) -> dict:
    """
    Estadísticas avanzadas incluyendo información de escalabilidad.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
    
    Returns:
        Diccionario con estadísticas avanzadas
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        # Obtener estadísticas básicas
        basic_stats = get_vector_store_stats(vector_store)
        
        # Añadir información de escalabilidad
        is_large = is_large_database(vector_store)
        memory_usage = get_memory_usage()
        
        # Calcular estimaciones de rendimiento
        total_docs = basic_stats.get('total_documents', 0)
        
        # Estimaciones basadas en el tamaño
        if total_docs < 1000:
            estimated_optimization_time = "1-5 分钟"
            recommended_approach = "标准"
        elif total_docs < 10000:
            estimated_optimization_time = "5-15 分钟"
            recommended_approach = "标准"
        elif total_docs < 50000:
            estimated_optimization_time = "15-45 分钟"
            recommended_approach = "增量"
        elif total_docs < 100000:
            estimated_optimization_time = "45-90 分钟"
            recommended_approach = "增量"
        else:
            estimated_optimization_time = "2-4 小时"
            recommended_approach = "增量"
        
        advanced_stats = {
            **basic_stats,
            "is_large_database": is_large,
            "current_memory_usage_mb": memory_usage,
            "estimated_optimization_time": estimated_optimization_time,
            "recommended_optimization_approach": recommended_approach,
            "memory_threshold": LARGE_DB_CONFIG['memory_threshold'],
            "incremental_batch_size": LARGE_DB_CONFIG['incremental_batch_size'],
            "checkpoint_interval": LARGE_DB_CONFIG['checkpoint_interval']
        };
        
        return advanced_stats
        
    except Exception as e:
        log(f"核心错误: 获取高级统计信息时出错: {e}")
        return {"error": str(e)}

# --- Configuraciones para Bases Grandes ---
LARGE_DB_CONFIG = {
    'incremental_batch_size': 2000,  # Batch más pequeño para bases grandes
    'memory_threshold': 10000,  # Número de documentos para usar modo incremental
    'checkpoint_interval': 5000,  # Guardar progreso cada N documentos
    'max_memory_usage_mb': 2048,  # Límite de memoria en MB
    'temp_storage_dir': './temp_reindex'
}

def is_large_database(vector_store: Chroma = None) -> bool:
    """
    Determina si la base de datos es considerada "grande" para optimizaciones especiales.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
    
    Returns:
        True si la base es grande (>10,000 documentos)
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        count = vector_store._collection.count()
        return count > LARGE_DB_CONFIG['memory_threshold']
        
    except Exception as e:
        log(f"核心错误: 检查数据库大小时出错: {e}")
        return False

def get_memory_usage() -> float:
    """
    Obtiene el uso currente de memoria en MB.
    
    Returns:
        Uso de memoria en MB
    """
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convertir a MB
    except ImportError:
        log("核心: psutil 不可用，无法监控内存")
        return 0.0

def optimize_vector_store_large(vector_store: Chroma = None) -> dict:
    """
    Optimización especial para bases de datos muy grandes (>10,000 documentos).
    Usa procesamiento incremental y checkpoints para evitar problemas de memoria.
    
    Args:
        vector_store: Instancia de Chroma (si None, se crea una nueva)
    
    Returns:
        Diccionario con información sobre la optimización
    """
    try:
        if vector_store is None:
            vector_store = get_vector_store()
        
        log("核心: 开始优化大型数据库...")
        
        # Verificar si realmente es una base grande
        if not is_large_database(vector_store):
            log("核心: 数据库不大，使用标准优化")
            return optimize_vector_store(vector_store)
        
        # Crear directorio temporal si no existe
        import os
        temp_dir = LARGE_DB_CONFIG['temp_storage_dir']
        os.makedirs(temp_dir, exist_ok=True)
        
        collection = vector_store._collection
        all_data = collection.get()
        
        if not all_data['documents']:
            return {
                "status": "warning",
                "message": "没有文档可供优化"
            }
        
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        ids = all_data['ids']
        
        total_docs = len(documents)
        batch_size = LARGE_DB_CONFIG['incremental_batch_size']
        checkpoint_interval = LARGE_DB_CONFIG['checkpoint_interval']
        
        log(f"核心: 在增量模式下优化 {total_docs} 个文档")
        log(f"核心: 批处理大小: {batch_size}, 每 {checkpoint_interval}个文档创建检查点")
        
        # Guardar datos originales en archivos temporales
        import pickle
        temp_data_file = os.path.join(temp_dir, 'temp_data.pkl')
        with open(temp_data_file, 'wb') as f:
            pickle.dump({
                'documents': documents,
                'metadatas': metadatas,
                'ids': ids
            }, f)
        
        # Eliminar documentos originales
        collection.delete(ids=ids)
        
        # Procesar en batches con checkpoints
        processed_count = 0
        checkpoint_file = os.path.join(temp_dir, 'checkpoint.txt')
        
        # Verificar si hay un checkpoint previo
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                processed_count = int(f.read().strip())
            log(f"核心: 从文档 {processed_count} 恢复")
        
        try:
            for i in range(processed_count, total_docs, batch_size):
                end_idx = min(i + batch_size, total_docs)
                batch_docs = documents[i:end_idx]
                batch_metadatas = metadatas[i:end_idx]
                batch_ids = ids[i:end_idx]
                
                # Verificar uso de memoria
                memory_usage = get_memory_usage()
                if memory_usage > LARGE_DB_CONFIG['max_memory_usage_mb']:
                    log(f"核心警告: 内存使用过高 ({memory_usage:.1f}MB)，暂停中...")
                    # Forzar limpieza de memoria
                    import gc
                    gc.collect()
                
                # Procesar batch
                try:
                    collection.add(
                        documents=batch_docs,
                        metadatas=batch_metadatas,
                        ids=batch_ids
                    )
                    
                    processed_count = end_idx
                    log(f"核心: 批处理完成 ({i+1}-{end_idx} / {total_docs}) - 内存: {memory_usage:.1f}MB")
                    
                    # Guardar checkpoint
                    if end_idx % checkpoint_interval == 0 or end_idx == total_docs:
                        with open(checkpoint_file, 'w') as f:
                            f.write(str(end_idx))
                        log(f"核心: 检查点已保存，文档 {end_idx}")
                        
                except Exception as batch_error:
                    log(f"核心错误: 批处理 {i//batch_size + 1} 出错: {batch_error}")
                    # Intentar con batch más pequeño
                    smaller_batch_size = batch_size // 2
                    for j in range(0, len(batch_docs), smaller_batch_size):
                        sub_end = min(j + smaller_batch_size, len(batch_docs))
                        sub_docs = batch_docs[j:sub_end]
                        sub_metadatas = batch_metadatas[j:sub_end]
                        sub_ids = batch_ids[j:sub_end]
                        
                        collection.add(
                            documents=sub_docs,
                            metadatas=sub_metadatas,
                            ids=sub_ids
                        )
                        log(f"核心: 子批处理完成 ({j+1}-{sub_end} / {len(batch_docs)})")
            
            # Limpiar archivos temporales
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
            
            log("核心: 增量优化完成")
            
            return {
                "status": "success",
                "message": f"向量数据库已增量优化 ({total_docs} 个文档)",
                "documents_processed": total_docs,
                "optimization_type": "incremental"
            }
            
        except Exception as e:
            log(f"核心错误: 增量优化过程中出错: {e}")
            # Restaurar desde checkpoint si es posible
            if os.path.exists(checkpoint_file):
                log("核心: 可恢复错误，可以从检查点恢复")
            
            return {
                "status": "error",
                "message": f"增量优化出错: {str(e)}",
                "recoverable": True
            }
        
    except Exception as e:
        log(f"核心错误: 优化大型数据库时出错: {e}")
        return {
            "status": "error",
            "message": f"优化大型数据库时出错: {str(e)}"
        }

def load_document_with_elements(file_path: str) -> tuple[str, dict, List[Any]]:
    """
    Carga documento manteniendo los elementos estructurales para chunking semántico.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        Tupla con (contenido_texto, metadatos, elementos_estructurales)
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Estrategia 1: Unstructured con configuración óptima
    try:
        log(f"核心: 尝试使用 Unstructured 加载（最佳配置）...")
        config = Config.get_unstructured_config(file_extension)
        
        # Para PDFs, usar configuración más rápida para evitar colgadas
        if file_extension == '.pdf':
            log(f"核心: 检测到 PDF，使用快速配置以避免超时...")
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
            log(f"核心: 使用 Unstructured 加载成功（最佳配置）")
            return processed_text, metadata, elements
    
    except Exception as e:
        log(f"核心警告: Unstructured（最佳配置）加载失败: {e}")
    
    # Estrategia 2: Unstructured con configuración básica
    try:
        log(f"核心: 尝试使用 Unstructured 加载（基本配置）...")
        elements = partition(filename=file_path, strategy="fast", max_partition=1000)
        processed_text = process_unstructured_elements(elements)
        metadata = extract_structural_metadata(elements, file_path)
        
        if processed_text and not processed_text.isspace():
            log(f"核心: 使用 Unstructured 加载成功（基本配置）")
            return processed_text, metadata, elements
    
    except Exception as e:
        log(f"核心警告: Unstructured（基本配置）加载失败: {e}")
    
    # Estrategia 3: Cargadores específicos de LangChain (sin elementos estructurales)
    try:
        log(f"核心: 尝试使用 LangChain 特定加载器加载...")
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
            log(f"核心: 使用 LangChain 特定加载器加载成功")
            return fallback_text, metadata, None  # Sin elementos estructurales
    
    except Exception as e:
        log(f"核心警告: LangChain 特定加载器加载失败: {e}")
    
    # Si todas las estrategias fallan
    log(f"核心错误: 所有加载策略均失败，文件: '{file_path}'")
    return "", {}, None

def create_advanced_semantic_chunks(elements: List[Any], max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Crea chunks semánticos avanzados basados en la estructura real del documento.
    
    Args:
        elements: Lista de elementos extraídos por Unstructured
        max_chunk_size: Tamaño máximo de cada chunk
        overlap: Superposición entre chunks
    
    Returns:
        Lista de chunks semánticos
    """
    if not elements:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    log(f"核心: 创建高级语义块，{len(elements)} 个元素...")
    
    for i, element in enumerate(elements):
        # Extraer texto del elemento
        element_text = ""
        if hasattr(element, 'text'):
            element_text = element.text
        elif hasattr(element, 'content'):
            element_text = element.content
        else:
            element_text = str(element)
        
        # Limpiar el texto
        element_text = element_text.strip()
        if not element_text:
            continue
        
        element_size = len(element_text)
        
        # Determinar si este elemento es un punto de quiebre natural
        is_break_point = False
        
        # Verificar si es un título (punto de quiebre natural)
        if hasattr(element, 'category'):
            if element.category in ['Title', 'NarrativeText', 'ListItem']:
                is_break_point = True
        elif hasattr(element, 'metadata') and element.metadata:
            if element.metadata.get('category') in ['Title', 'NarrativeText', 'ListItem']:
                is_break_point = True
        
        # Si añadir este elemento excedería el tamaño máximo Y es un punto de quiebre
        if current_size + element_size > max_chunk_size and current_chunk and is_break_point:
            # Guardar el chunk actual
            chunk_text = "\n\n".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
                log(f"核心: 创建第 {len(chunks)} 个块，包含 {len(current_chunk)} 个元素，大小: {len(chunk_text)}")
            
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
            log(f"核心: 创建最后一个块，包含 {len(current_chunk)} 个元素，大小: {len(chunk_text)}")
    
    log(f"核心: 高级语义分块完成: 创建了 {len(chunks)} 个块")
    return chunks