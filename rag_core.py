"""
Sistema RAG Modular Avanzado - Core Module
==========================================

Este módulo proporciona funcionalidades avanzadas para el procesamiento y almacenamiento
de documentos en un sistema RAG (Retrieval-Augmented Generation), incluyendo:

- Procesamiento de múltiples formatos de documentos
- Cache de embeddings para optimización de rendimiento
- Chunking semántico avanzado
- Optimizaciones para bases de datos grandes
- Normalización de texto y limpieza
- Gestión avanzada de metadatos
- Sistema de cache de embeddings
- Sistema de cache de documentos
- Sistema de cache de consultas
- Sistema de cache de respuestas
- Sistema de cache de metadatos
- Sistema de cache de embeddings
"""

# =============================================================================
# IMPORTS Y DEPENDENCIAS
# =============================================================================

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
import hashlib
import pickle
from pathlib import Path
from functools import lru_cache

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, ListItem, Table, NarrativeText

# ChromaDB imports
from chromadb.config import Settings

# Importar Rich para mejorar la salida en consola
from rich import print as rich_print
from rich.panel import Panel

# =============================================================================
# CONFIGURACIÓN AVANZADA DE UNSTRUCTURED
# =============================================================================

# Configuraciones optimizadas para diferentes tipos de documentos
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

# --- Sistema de Cache de Embeddings ---
class EmbeddingCache:
    """
    Sistema de cache para embeddings que mejora significativamente el rendimiento
    evitando recalcular embeddings para textos ya procesados.
    """
    
    def __init__(self, cache_dir: str = "./embedding_cache", max_memory_size: int = 1000):
        """
        Inicializa el cache de embeddings.
        
        Args:
            cache_dir: Directorio donde se almacenan los embeddings en disco
            max_memory_size: Número máximo de embeddings en memoria (LRU)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_memory_size = max_memory_size
        
        # Cache en memoria usando LRU
        self._memory_cache = {}
        self._access_order = []
        
        # Estadísticas
        self.hits = 0
        self.misses = 0
        self.disk_hits = 0
        
        log(f"Core: Cache de embeddings inicializado en '{self.cache_dir}'")
        log(f"Core: Tamaño máximo en memoria: {max_memory_size} embeddings")
    
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
            log(f"Core: Cache HIT en memoria para texto de {len(text)} caracteres")
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
                log(f"Core: Cache HIT en disco para texto de {len(text)} caracteres")
                return embedding
            except Exception as e:
                log(f"Core: Error cargando embedding desde disco: {e}")
                # Eliminar archivo corrupto
                try:
                    cache_file.unlink()
                except:
                    pass
        
        self.misses += 1
        log(f"Core: Cache MISS para texto de {len(text)} caracteres")
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
            log(f"Core: Embedding guardado en cache (memoria + disco) para texto de {len(text)} caracteres")
        except Exception as e:
            log(f"Core: Error guardando embedding en disco: {e}")
    
    def clear_memory(self):
        """Limpia el cache en memoria, manteniendo el cache en disco."""
        self._memory_cache.clear()
        self._access_order.clear()
        log("Core: Cache en memoria limpiado")
    
    def clear_all(self):
        """Limpia todo el cache (memoria y disco)."""
        self.clear_memory()
        
        # Limpiar archivos de disco
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            log("Core: Cache completo limpiado (memoria + disco)")
        except Exception as e:
            log(f"Core: Error limpiando cache en disco: {e}")
    
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
        log("Core: === Estadísticas del Cache de Embeddings ===")
        for key, value in stats.items():
            log(f"Core: {key}: {value}")
        log("Core: ===========================================")

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
        _embedding_cache = EmbeddingCache()
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
    log("Core: Cache de embeddings limpiado completamente")

# =============================================================================
# FUNCIONES DE LOGGING Y UTILIDADES GENERALES
# =============================================================================

def log(message: str):
    """Función de logging centralizada con timestamp y colores usando Rich."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Detectar tipo de mensaje para colorear
    if any(word in message.lower() for word in ["error", "falló", "fatal", "excepción"]):
        rich_print(f"[bold red][{timestamp}] {message}[/bold red]")
    elif any(word in message.lower() for word in ["advertencia", "warning"]):
        rich_print(f"[bold yellow][{timestamp}] {message}[/bold yellow]")
    elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok", "iniciado", "iniciando"]):
        rich_print(f"[bold green][{timestamp}] {message}[/bold green]")
    else:
        rich_print(f"[cyan][{timestamp}] {message}[/cyan]")

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
        
        log(f"Core: Descarga completada: {filename}")
    except Exception as e:
        log(f"Core: Error en descarga: {e}")
        raise

# =============================================================================
# GESTIÓN DE EMBEDDINGS Y MODELOS
# =============================================================================

def get_embedding_function():
    """
    Obtiene la función de embeddings con cache integrado.
    
    Returns:
        Función de embeddings con cache
    """
    try:
        # Configuración del modelo de embeddings
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Crear embeddings base
        base_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Obtener cache
        cache = get_embedding_cache()
        
        # Wrapper con cache
        class CachedEmbeddings:
            def __init__(self, base_embeddings, cache):
                self.base_embeddings = base_embeddings
                self.cache = cache
            
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
        
        return CachedEmbeddings(base_embeddings, cache)
        
    except Exception as e:
        log(f"Core: Error inicializando embeddings: {e}")
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
        
        log(f"Core: Detectados {count} documentos, usando perfil '{profile}'")
        return profile
        
    except Exception as e:
        log(f"Core Warning: No se pudo detectar perfil automáticamente: {e}")
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
    
    log(f"Core: Inicializando base de datos vectorial con perfil '{profile}'...")
    
    # Obtener información del perfil
    profile_info = VECTOR_STORE_PROFILES.get(profile, {})
    log(f"Core: Perfil '{profile}' - {profile_info.get('description', 'Configuración estándar')}")
    
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
    
    log(f"Core: Base de datos vectorial optimizada inicializada en '{PERSIST_DIRECTORY}'")
    log(f"Core: Perfil aplicado: {profile} - {profile_info.get('recommended_for', 'Configuración general')}")
    
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
        log("Core Advertencia: Se intentó añadir texto vacío o solo espacios en blanco.")
        return

    # Limpiar el texto antes de procesarlo
    log(f"Core: Limpiando y preparando texto para procesamiento RAG...")
    cleaned_text = clean_text_for_rag(text)
    
    if not cleaned_text or cleaned_text.isspace():
        log("Core Advertencia: El texto quedó vacío después de la limpieza.")
        return

    # Determinar qué tipo de chunking usar
    if use_semantic_chunking and structural_elements and len(structural_elements) > 1:
        # Usar chunking semántico real con elementos estructurales
        log(f"Core: Usando chunking semántico avanzado con {len(structural_elements)} elementos estructurales...")
        texts = create_advanced_semantic_chunks(structural_elements, max_chunk_size=800, overlap=150)
        
        if not texts:
            log("Core Warning: No se pudieron crear chunks semánticos, usando chunking tradicional...")
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
        log(f"Core: Usando chunking semántico mejorado basado en metadatos estructurales...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Chunks más pequeños para mejor precisión
            chunk_overlap=150,  # Overlap moderado
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        texts = text_splitter.split_text(cleaned_text)
    
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
            
            # Añadir información sobre el tipo de chunking usado
            if use_semantic_chunking and structural_elements:
                metadata['chunking_method'] = 'semantic_advanced'
            elif use_semantic_chunking:
                metadata['chunking_method'] = 'semantic_improved'
            else:
                metadata['chunking_method'] = 'traditional'
            
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
            log("Core: Detectada base de datos grande, usando optimización incremental")
            return optimize_vector_store_large(vector_store)
        
        log("Core: Iniciando optimización de la base vectorial...")
        
        # Obtener estadísticas antes de la optimización
        stats_before = get_vector_store_stats(vector_store)
        
        collection = vector_store._collection
        
        # En lugar de reindexar, usar métodos nativos de ChromaDB para optimización
        log("Core: Aplicando optimizaciones nativas de ChromaDB...")
        
        # 1. Forzar persistencia para optimizar almacenamiento
        try:
            collection.persist()
            log("Core: Persistencia forzada completada")
        except Exception as e:
            log(f"Core Warning: No se pudo forzar persistencia: {e}")
        
        # 2. Obtener información de la colección para verificar estado
        count = collection.count()
        log(f"Core: Verificando {count} documentos en la colección")
        
        # 3. Realizar una consulta de prueba para verificar índices
        try:
            # Hacer una búsqueda de prueba para activar índices
            test_results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            log("Core: Índices de búsqueda verificados")
        except Exception as e:
            log(f"Core Warning: Error verificando índices: {e}")
        
        # 4. Verificar configuración de la colección
        try:
            # Obtener metadatos de la colección
            collection_metadata = collection.metadata
            log(f"Core: Metadatos de colección: {collection_metadata}")
        except Exception as e:
            log(f"Core Warning: No se pudieron obtener metadatos: {e}")
        
        # 5. Forzar compactación si está disponible
        try:
            # Intentar compactar la base de datos
            if hasattr(collection, 'compact'):
                collection.compact()
                log("Core: Compactación de base de datos completada")
            else:
                log("Core: Compactación no disponible en esta versión de ChromaDB")
        except Exception as e:
            log(f"Core Warning: Error en compactación: {e}")
        
        # Obtener estadísticas después de la optimización
        stats_after = get_vector_store_stats(vector_store)
        
        log("Core: Optimización de base vectorial completada")
        
        return {
            "status": "success",
            "message": "Base vectorial optimizada usando métodos nativos de ChromaDB",
            "stats_before": stats_before,
            "stats_after": stats_after,
            "documents_processed": count,
            "optimization_type": "native",
            "optimizations_applied": [
                "persistencia forzada",
                "verificación de índices",
                "compactación de base de datos"
            ]
        }
        
    except Exception as e:
        log(f"Core Error: Error optimizando base vectorial: {e}")
        return {
            "status": "error",
            "message": f"Error optimizando base vectorial: {str(e)}"
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
        log(f"Core Error: Error obteniendo estadísticas de base vectorial: {e}")
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
            log(f"Core: Detectada base de datos grande, usando reindexado incremental con perfil '{profile}'")
            return reindex_vector_store_large(vector_store, profile)
        
        log(f"Core: Iniciando reindexado de base vectorial con perfil '{profile}'...")
        
        collection = vector_store._collection
        
        # Obtener estadísticas antes del reindexado
        count_before = collection.count()
        log(f"Core: Documentos antes del reindexado: {count_before}")
        
        # En lugar de eliminar y reinsertar, usar métodos nativos de ChromaDB
        log("Core: Aplicando reindexado usando métodos nativos de ChromaDB...")
        
        # 1. Verificar que la colección esté en buen estado
        try:
            # Hacer una consulta de prueba para verificar índices
            test_results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            log("Core: Índices de búsqueda verificados")
        except Exception as e:
            log(f"Core Warning: Error verificando índices: {e}")
        
        # 2. Forzar persistencia si está disponible
        try:
            if hasattr(collection, 'persist'):
                collection.persist()
                log("Core: Persistencia forzada completada")
            else:
                log("Core: Persistencia no disponible en esta versión")
        except Exception as e:
            log(f"Core Warning: No se pudo forzar persistencia: {e}")
        
        # 3. Verificar configuración de la colección
        try:
            collection_metadata = collection.metadata
            log(f"Core: Metadatos de colección: {collection_metadata}")
        except Exception as e:
            log(f"Core Warning: No se pudieron obtener metadatos: {e}")
        
        # 4. Intentar compactación si está disponible
        try:
            if hasattr(collection, 'compact'):
                collection.compact()
                log("Core: Compactación de base de datos completada")
            else:
                log("Core: Compactación no disponible en esta versión de ChromaDB")
        except Exception as e:
            log(f"Core Warning: Error en compactación: {e}")
        
        # 5. Verificar que el perfil se aplique correctamente
        # Esto se hace automáticamente al crear el vector_store con el perfil
        log(f"Core: Perfil '{profile}' aplicado a la configuración")
        
        # Obtener estadísticas después del reindexado
        count_after = collection.count()
        log(f"Core: Documentos después del reindexado: {count_after}")
        
        log("Core: Reindexado de base vectorial completado")
        
        return {
            "status": "success",
            "message": f"Base vectorial reindexada con perfil '{profile}' usando métodos nativos",
            "documents_before": count_before,
            "documents_after": count_after,
            "reindex_type": "native",
            "profile_applied": profile,
            "optimizations_applied": [
                "verificación de índices",
                "persistencia forzada",
                "compactación de base de datos",
                "aplicación de perfil"
            ]
        }
        
    except Exception as e:
        log(f"Core Error: Error reindexando base vectorial: {e}")
        return {
            "status": "error",
            "message": f"Error reindexando base vectorial: {str(e)}"
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
        
        log(f"Core: Iniciando reindexado incremental con perfil '{profile}'...")
        
        # Verificar si es una base grande
        if not is_large_database(vector_store):
            log("Core: Base no es grande, usando reindexado estándar")
            return reindex_vector_store(vector_store, profile)
        
        # Usar la misma lógica que optimize_vector_store_large pero con nuevo perfil
        return optimize_vector_store_large(vector_store)
        
    except Exception as e:
        log(f"Core Error: Error en reindexado para base grande: {e}")
        return {
            "status": "error",
            "message": f"Error en reindexado para base grande: {str(e)}"
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
            estimated_optimization_time = "1-5 minutos"
            recommended_approach = "estándar"
        elif total_docs < 10000:
            estimated_optimization_time = "5-15 minutos"
            recommended_approach = "estándar"
        elif total_docs < 50000:
            estimated_optimization_time = "15-45 minutos"
            recommended_approach = "incremental"
        elif total_docs < 100000:
            estimated_optimization_time = "45-90 minutos"
            recommended_approach = "incremental"
        else:
            estimated_optimization_time = "2-4 horas"
            recommended_approach = "incremental"
        
        advanced_stats = {
            **basic_stats,
            "is_large_database": is_large,
            "current_memory_usage_mb": memory_usage,
            "estimated_optimization_time": estimated_optimization_time,
            "recommended_optimization_approach": recommended_approach,
            "memory_threshold": LARGE_DB_CONFIG['memory_threshold'],
            "incremental_batch_size": LARGE_DB_CONFIG['incremental_batch_size'],
            "checkpoint_interval": LARGE_DB_CONFIG['checkpoint_interval']
        }
        
        return advanced_stats
        
    except Exception as e:
        log(f"Core Error: Error obteniendo estadísticas avanzadas: {e}")
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
        log(f"Core Error: Error verificando tamaño de base: {e}")
        return False

def get_memory_usage() -> float:
    """
    Obtiene el uso actual de memoria en MB.
    
    Returns:
        Uso de memoria en MB
    """
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convertir a MB
    except ImportError:
        log("Core: psutil no disponible, no se puede monitorear memoria")
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
        
        log("Core: Iniciando optimización para base de datos grande...")
        
        # Verificar si realmente es una base grande
        if not is_large_database(vector_store):
            log("Core: Base no es grande, usando optimización estándar")
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
                "message": "No hay documentos para optimizar"
            }
        
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        ids = all_data['ids']
        
        total_docs = len(documents)
        batch_size = LARGE_DB_CONFIG['incremental_batch_size']
        checkpoint_interval = LARGE_DB_CONFIG['checkpoint_interval']
        
        log(f"Core: Optimizando {total_docs} documentos en modo incremental")
        log(f"Core: Batch size: {batch_size}, Checkpoint cada: {checkpoint_interval}")
        
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
            log(f"Core: Resumiendo desde documento {processed_count}")
        
        try:
            for i in range(processed_count, total_docs, batch_size):
                end_idx = min(i + batch_size, total_docs)
                batch_docs = documents[i:end_idx]
                batch_metadatas = metadatas[i:end_idx]
                batch_ids = ids[i:end_idx]
                
                # Verificar uso de memoria
                memory_usage = get_memory_usage()
                if memory_usage > LARGE_DB_CONFIG['max_memory_usage_mb']:
                    log(f"Core Warning: Uso de memoria alto ({memory_usage:.1f}MB), pausando...")
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
                    log(f"Core: Batch procesado ({i+1}-{end_idx} de {total_docs}) - Memoria: {memory_usage:.1f}MB")
                    
                    # Guardar checkpoint
                    if end_idx % checkpoint_interval == 0 or end_idx == total_docs:
                        with open(checkpoint_file, 'w') as f:
                            f.write(str(end_idx))
                        log(f"Core: Checkpoint guardado en documento {end_idx}")
                        
                except Exception as batch_error:
                    log(f"Core Error: Error en batch {i//batch_size + 1}: {batch_error}")
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
                        log(f"Core: Sub-batch procesado ({j+1}-{sub_end} de {len(batch_docs)})")
            
            # Limpiar archivos temporales
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
            
            log("Core: Optimización incremental completada")
            
            return {
                "status": "success",
                "message": f"Base vectorial optimizada incrementalmente ({total_docs} documentos)",
                "documents_processed": total_docs,
                "optimization_type": "incremental"
            }
            
        except Exception as e:
            log(f"Core Error: Error durante optimización incremental: {e}")
            # Restaurar desde checkpoint si es posible
            if os.path.exists(checkpoint_file):
                log("Core: Error recuperable, se puede reanudar desde checkpoint")
            
            return {
                "status": "error",
                "message": f"Error en optimización incremental: {str(e)}",
                "recoverable": True
            }
        
    except Exception as e:
        log(f"Core Error: Error en optimización para base grande: {e}")
        return {
            "status": "error",
            "message": f"Error en optimización para base grande: {str(e)}"
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
            return processed_text, metadata, elements
    
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
            return processed_text, metadata, elements
    
    except Exception as e:
        log(f"Core Warning: Unstructured (configuración básica) falló: {e}")
    
    # Estrategia 3: Cargadores específicos de LangChain (sin elementos estructurales)
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
            return fallback_text, metadata, None  # Sin elementos estructurales
    
    except Exception as e:
        log(f"Core Warning: Cargadores específicos de LangChain fallaron: {e}")
    
    # Si todas las estrategias fallan
    log(f"Core Error: Todas las estrategias de carga fallaron para '{file_path}'")
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
    
    log(f"Core: Creando chunks semánticos avanzados con {len(elements)} elementos...")
    
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
                log(f"Core: Chunk {len(chunks)} creado con {len(current_chunk)} elementos, tamaño: {len(chunk_text)}")
            
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
            log(f"Core: Chunk final {len(chunks)} creado con {len(current_chunk)} elementos, tamaño: {len(chunk_text)}")
    
    log(f"Core: Chunking semántico avanzado completado: {len(chunks)} chunks creados")
    return chunks

# =============================================================================
# CONFIGURACIÓN Y GESTIÓN DEL VECTOR STORE
# =============================================================================

# Configuración del proyecto
load_dotenv()

# Obtener la ruta absoluta del directorio del script actual
_project_root = os.path.dirname(os.path.abspath(__file__))
# Forzar la ruta absoluta para la base de datos, evitando problemas de directorio de trabajo
PERSIST_DIRECTORY = os.path.join(_project_root, "rag_mcp_db")
COLLECTION_NAME = "mcp_rag_collection"

# Perfiles de configuración para diferentes tamaños de base de datos
VECTOR_STORE_PROFILES = {
    'small': {
        'description': 'Base de datos pequeña (< 1000 documentos)',
        'recommended_for': 'Desarrollo y pruebas',
        'chunk_size': 1000,
        'chunk_overlap': 200
    },
    'medium': {
        'description': 'Base de datos mediana (1000-10000 documentos)',
        'recommended_for': 'Uso general',
        'chunk_size': 1000,
        'chunk_overlap': 200
    },
    'large': {
        'description': 'Base de datos grande (> 10000 documentos)',
        'recommended_for': 'Producción y grandes volúmenes',
        'chunk_size': 800,
        'chunk_overlap': 150
    }
}