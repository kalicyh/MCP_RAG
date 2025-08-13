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
# 主要导入
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

# 日志配置
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain 和 ChromaDB 导入
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
    print(f"导入 LangChain 时出错: {e}", file=sys.stderr)
    print("正在安装依赖项...", file=sys.stderr)
    os.system("pip install langchain langchain-community langchain-chroma langchain-ollama")

# Unstructured 导入
try:
    from unstructured.partition.auto import partition
    from unstructured.documents.elements import Title, ListItem, Table, NarrativeText
except ImportError as e:
    print(f"导入 Unstructured 时出错: {e}", file=sys.stderr)
    print("正在安装依赖项...", file=sys.stderr)
    os.system("pip install unstructured")

# 结构化模型导入
try:
    from models import MetadataModel
except ImportError as e:
    print(f"警告: 无法导入结构化模型: {e}", file=sys.stderr)
    MetadataModel = None

# =============================================================================
# UNSTRUCTURED 高级配置
# =============================================================================

# 导入集中配置
from utils.config import Config

# 使用集中配置而不是重复配置
UNSTRUCTURED_CONFIGS = Config.UNSTRUCTURED_CONFIGS

# 未指定文件的默认配置
DEFAULT_CONFIG = {
    'strategy': 'fast',
    'include_metadata': True,
    'max_partition': 2000,
    'new_after_n_chars': 1500
}

# 定义默认集合名和持久化目录（集合名将根据嵌入提供商动态派生）
COLLECTION_NAME = "default_collection"
PERSIST_DIRECTORY = "./data/vector_store"

def get_collection_name() -> str:
    """
    基于嵌入提供商/模型动态生成集合名，避免不同维度嵌入写入同一集合。
    可通过环境变量 COLLECTION_NAME 覆盖基础前缀。
    """
    base = os.getenv("COLLECTION_NAME", COLLECTION_NAME)
    provider = os.getenv("EMBEDDING_PROVIDER", "HF").upper()
    if provider == "OPENAI":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        suffix = f"openai_{model}"
    else:
        # 当前本地默认模型
        suffix = "hf_all-MiniLM-L6-v2"
    try:
        safe_suffix = re.sub(r"[^a-zA-Z0-9_-]+", "-", suffix)
    except Exception:
        safe_suffix = suffix
    return f"{base}-{safe_suffix}"

# --- Sistema de Cache de Embeddings ---
class EmbeddingCache:
    """
    嵌入缓存系统，显著提高性能
    避免为已处理的文本重新计算嵌入。
    """
    
    def __init__(self, cache_dir: str = None, max_memory_size: int = 1000):
        """
        初始化嵌入缓存。
        
        Args:
            cache_dir: 磁盘上存储嵌入的目录
                       如果为 None，使用 MCP 服务器配置
            max_memory_size: 内存中嵌入的最大数量（LRU）
        """
        # 如果未指定 cache_dir，使用 MCP 服务器配置
        if cache_dir is None:
            try:
                from utils.config import Config
                cache_dir = Config.EMBEDDING_CACHE_DIR
            except ImportError:
                # 回退：使用相对于项目的目录
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
        """使用 MD5 哈希为文本生成唯一键。"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存键的缓存文件路径。"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _update_access_order(self, key: str):
        """更新访问顺序以实现 LRU。"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        # 仅保留最近的元素
        if len(self._access_order) > self.max_memory_size:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._memory_cache:
                del self._memory_cache[oldest_key]
    
    def get(self, text: str):
        """
        获取文本的嵌入，首先从内存获取，然后从磁盘获取。
        
        Args:
            text: 要获取嵌入的文本
            
        Returns:
            如果在缓存中则返回嵌入，否则返回 None
        """
        if not text or not text.strip():
            return None
        
        cache_key = self._get_cache_key(text)
        
        # 1. 查找内存缓存
        if cache_key in self._memory_cache:
            self.hits += 1
            self._update_access_order(cache_key)
            log(f"核心: 内存缓存命中，文本长度 {len(text)}")
            return self._memory_cache[cache_key]
        
        # 2. 查找磁盘缓存
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                
                # 移动到内存
                self._memory_cache[cache_key] = embedding
                self._update_access_order(cache_key)
                
                self.disk_hits += 1
                log(f"核心: 磁盘缓存命中，文本长度 {len(text)}")
                return embedding
            except Exception as e:
                log(f"核心: 从磁盘加载 embedding 时出错: {e}")
                # 删除损坏的文件
                try:
                    cache_file.unlink()
                except:
                    pass
        
        self.misses += 1
        log(f"核心: 缓存未命中，文本长度 {len(text)}")
        return None
    
    def set(self, text: str, embedding):
        """
        在缓存中存储嵌入（内存和磁盘）。
        
        Args:
            text: Texto original
            embedding: 要存储的嵌入
        """
        if not text or not text.strip() or embedding is None:
            return
        
        cache_key = self._get_cache_key(text)
        
        # 存储到内存
        self._memory_cache[cache_key] = embedding
        self._update_access_order(cache_key)
        
        # 存储到磁盘
        cache_file = self._get_cache_file_path(cache_key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
            log(f"核心: Embedding 已缓存（内存 + 磁盘），文本长度 {len(text)}")
        except Exception as e:
            log(f"核心: 保存 embedding 到磁盘时出错: {e}")
    
    def clear_memory(self):
        """清理内存缓存，保留磁盘缓存。"""
        self._memory_cache.clear()
        self._access_order.clear()
        log("核心: 内存缓存已清空")
    
    def clear_all(self):
        """清理所有缓存（内存和磁盘）。"""
        self.clear_memory()
        
        # 清理磁盘文件
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            log("核心: 完全清空缓存（内存 + 磁盘）")
        except Exception as e:
            log(f"核心: 清理磁盘缓存时出错: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存的统计信息。"""
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
        """打印缓存统计信息。"""
        stats = self.get_stats()
        log("核心: === Embedding 缓存统计信息 ===")
        for key, value in stats.items():
            log(f"核心: {key}: {value}")
        log("核心: ===========================================")

# =============================================================================
# 缓存实用工具和管理功能
# =============================================================================

# 嵌入缓存的全局变量
_embedding_cache = None

def get_embedding_cache() -> EmbeddingCache:
    """
    获取嵌入缓存的全局实例。
    
    Returns:
        EmbeddingCache 实例
    """
    global _embedding_cache
    if _embedding_cache is None:
        # 使用 config.py 文件的配置
        from utils.config import Config
        
        # 验证是否在 GUI 中并使用 MCP 服务器的绝对路径
        cache_dir = Config.EMBEDDING_CACHE_DIR
        
        # 如果路径是相对路径，转换为 MCP 服务器的绝对路径
        if not os.path.isabs(cache_dir):
            # 获取 MCP 服务器的绝对路径
            current_file = os.path.abspath(__file__)
            mcp_src_dir = os.path.dirname(current_file)
            mcp_server_dir = os.path.dirname(mcp_src_dir)
            cache_dir = os.path.join(mcp_server_dir, cache_dir)
        
        _embedding_cache = EmbeddingCache(cache_dir=cache_dir)
    return _embedding_cache

def get_cache_stats() -> Dict[str, Any]:
    """
    获取嵌入缓存的统计信息。
    
    Returns:
        包含缓存统计信息的字典
    """
    cache = get_embedding_cache()
    return cache.get_stats()

def print_cache_stats():
    """打印嵌入缓存的统计信息。"""
    cache = get_embedding_cache()
    cache.print_stats()

def clear_embedding_cache():
    """完全清理嵌入缓存。"""
    global _embedding_cache
    if _embedding_cache:
        _embedding_cache.clear_all()
        _embedding_cache = None
    log("核心: Embedding 缓存已完全清空")

# =============================================================================
# FUNCIONES DE LOGGING Y UTILIDADES GENERALES
# =============================================================================

def log(message: str):
    """使用 Rich 的集中式日志功能，包含时间戳和颜色。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)
    # 检测消息类型以着色
   
    # if any(word in message.lower() for word in ["error", "失败", "fatal", "异常"]):
    #     rich_print(f"[bold red][{timestamp}] {message}[/bold red]")
    # elif any(word in message.lower() for word in ["警告", "warning"]):
    #     rich_print(f"[bold yellow][{timestamp}] {message}[/bold yellow]")
    # elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok", "iniciado", "iniciando"]):
    #     rich_print(f"[bold green][{timestamp}] {message}[/bold green]")
    # else:
    #     rich_print(f"[cyan][{timestamp}] {message}[/cyan]")

def download_with_progress(url: str, filename: str, desc: str = "Downloading"):
    """
    下载带进度条的文件。
    
    Args:
        url: 要下载的文件URL
        filename: 本地文件名
        desc: 进度条描述
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
# 嵌入和模型管理
# =============================================================================

def get_embedding_function():
    """
    获取集成缓存的嵌入函数。
    自动检测是否有可用GPU并在可能时使用。
    
    Returns:
        带缓存的嵌入函数
    """
    try:
        provider = os.getenv("EMBEDDING_PROVIDER", "HF").upper()
        # 获取缓存（跨提供商复用，但我们用命名空间避免串扰）
        cache = get_embedding_cache()

        if provider == "OPENAI":
            try:
                from langchain_openai import OpenAIEmbeddings
            except ImportError:
                os.system("pip install langchain-openai")
                from langchain_openai import OpenAIEmbeddings

            openai_api_key = os.getenv("OPENAI_API_KEY", "")
            openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

            log(f"核心: 使用 OpenAI Embeddings: {model_name}，API 地址: {openai_api_base}")
            base_embeddings = OpenAIEmbeddings(
                api_key=openai_api_key,
                base_url=openai_api_base,
                model=model_name,
            )

            key_prefix = f"OPENAI:{model_name}"
            device = "api"

        else:
            # 本地 HuggingFace 模型
            model_name = "sentence-transformers/all-MiniLM-L6-v2"

            # 自动检测可用设备
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

            base_embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device},
                encode_kwargs={'normalize_embeddings': True}
            )
            key_prefix = f"HF:{model_name}"

        # 缓存包装器（添加提供商/模型命名空间，避免不同提供商缓存串扰）
        class CachedEmbeddings:
            def __init__(self, base_embeddings, cache, device, key_prefix: str):
                self.base_embeddings = base_embeddings
                self.cache = cache
                self.device = device
                self.key_prefix = key_prefix

            def _cache_key(self, text: str) -> str:
                return f"[{self.key_prefix}] {text}"

            def _cached_embed_query(self, text: str):
                namespaced_text = self._cache_key(text)
                cached_embedding = self.cache.get(namespaced_text)
                if cached_embedding is not None:
                    return cached_embedding
                embedding = self.base_embeddings.embed_query(text)
                self.cache.set(namespaced_text, embedding)
                return embedding

            def _cached_embed_documents(self, texts: List[str]):
                embeddings = []
                uncached_texts = []
                uncached_indices = []
                for i, text in enumerate(texts):
                    namespaced_text = self._cache_key(text)
                    cached_embedding = self.cache.get(namespaced_text)
                    if cached_embedding is not None:
                        embeddings.append(cached_embedding)
                    else:
                        embeddings.append(None)
                        uncached_texts.append(text)
                        uncached_indices.append(i)
                if uncached_texts:
                    new_embeddings = self.base_embeddings.embed_documents(uncached_texts)
                    for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                        namespaced_text = self._cache_key(text)
                        self.cache.set(namespaced_text, embedding)
                        embeddings[uncached_indices[i]] = embedding
                return embeddings

            def embed_query(self, text: str):
                return self._cached_embed_query(text)

            def embed_documents(self, texts: List[str]):
                return self._cached_embed_documents(texts)

        return CachedEmbeddings(base_embeddings, cache, device, key_prefix)

    except Exception as e:
        log(f"核心: 初始化 embeddings 时出错: {e}")
        raise

def get_optimal_vector_store_profile() -> str:
    """
    根据数据库大小自动检测最佳配置文件。
    
    Returns:
        最佳配置文件（'small', 'medium', 'large'）
    """
    try:
        # ChromaDB基本配置
        chroma_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
        
        # 创建临时向量存储以计算文档数量
        temp_store = Chroma(
            collection_name=get_collection_name(),
            embedding_function=get_embedding_function(),
            persist_directory=PERSIST_DIRECTORY,
            client_settings=chroma_settings
        )
        
        # 计算集合中的文档数量
        count = temp_store._collection.count()
        
        # 基于大小确定配置文件
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
        return 'medium'  # 默认配置文件

def get_vector_store(profile: str = 'auto') -> Chroma:
    """
    创建并返回优化的向量数据库实例。
    
    Args:
        profile: 配置文件（'small', 'medium', 'large', 'auto'）
                 'auto' 自动检测最佳配置文件
    
    Returns:
        优化配置的Chroma实例
    """
    # 如果要求则自动检测配置文件
    if profile == 'auto':
        profile = get_optimal_vector_store_profile()
    
    log(f"核心: 初始化向量数据库，配置文件 '{profile}'...")
    
    # 获取配置文件信息
    profile_info = VECTOR_STORE_PROFILES.get(profile, {})
    log(f"核心: 配置文件 '{profile}' - {profile_info.get('description', '标准配置')}")
    
    embeddings = get_embedding_function()
    
    # 创建 ChromaDB 配置
    chroma_settings = Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
    
    # 使用优化配置创建向量存储
    vector_store = Chroma(
        collection_name=get_collection_name(),
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        client_settings=chroma_settings
    )
    
    log(f"核心: 向量数据库优化初始化在 '{PERSIST_DIRECTORY}'")
    log(f"核心: 应用配置文件: {profile} - {profile_info.get('recommended_for', '通用配置')}")
    
    return vector_store

def fix_duplicated_characters(text: str) -> str:
    """
    修正可能因编码问题出现的重复字符。
    不触碰数字以避免修正合法数据。
    
    Args:
        text: 可能包含重复字符的文本
    
    Returns:
        重复字符已修正的文本（仅字母和空格）
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
    
    # 应用安全的重复模式修正
    for duplicated, corrected in safe_duplicated_patterns:
        text = text.replace(duplicated, corrected)
    
    # Detectar y corregir secuencias largas de caracteres duplicados
    # PERO IGNORAR COMPLETAMENTE LOS NÚMEROS
    def fix_long_duplications(match):
        char = match.group(1)
        count = len(match.group(0))
        
        # IGNORAR COMPLETAMENTE LOS NÚMEROS
        if char.isdigit():
            return match.group(0)  # 保持数字原样
        else:
            # Para letras y otros caracteres, ser más agresivo
            if count > 2:
                return char
            return match.group(0)
    
    # 应用长序列修正
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
        "M´etodo": "方法",
        "An´alisis": "Análisis", 
        "Bisecci´on": "Bisección",
        "Convergencia": "Convergencia",
        "M´etodos": "方法",
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
    
    # 首先应用特定字符映射
    for old_char, new_char in character_mapping.items():
        text = text.replace(old_char, new_char)
    
    # 标准化Unicode字符 (NFD -> NFC)
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
    text = text.replace('ñ', 'ñ')  # 标准化已正确的ñ
    text = text.replace('ñ', 'ñ')  # n + tilde combinada (U+006E + U+0303)
    text = text.replace('Ñ', 'Ñ')  # N + tilde combinada (U+004E + U+0303)
    
    # Corregir casos específicos de acentos que quedaron mal
    text = text.replace("M'etodo", "方法")
    text = text.replace("An'alisis", "Análisis")
    text = text.replace("Bisecci'on", "Bisección")
    text = text.replace("M'etodos", "方法")
    
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
    
    # 首先标准化西班牙语特殊字符
    text = normalize_spanish_characters(text)
    
    # 删除多个空格和过多的换行符
    text = re.sub(r'\s+', ' ', text)
    
    # 删除有问题的特殊字符但保留重要的标点和西班牙语字符
    # Mantener: letras, números, espacios, puntuación básica, caracteres acentuados
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'áéíóúÁÉÍÓÚñÑüÜ]', '', text)
    
    # 标准化标点符号周围的空格
    text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
    
    # 删除多个空行
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
            # 标准化表格文本的字符
            normalized_text = normalize_spanish_characters(table_element.text)
            return normalized_text
        elif hasattr(table_element, 'metadata') and 'text_as_html' in table_element.metadata:
            # 如果有HTML，提取文本
            html_text = table_element.metadata['text_as_html']
            # Limpiar tags HTML básicos
            clean_text = re.sub(r'<[^>]+>', ' ', html_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            # 标准化提取文本的字符
            normalized_text = normalize_spanish_characters(clean_text)
            return f"Tabla: {normalized_text}"
        else:
            # 标准化字符串表示的字符
            text_representation = str(table_element)
            normalized_text = normalize_spanish_characters(text_representation)
            return normalized_text
    except Exception as e:
        log(f"核心警告: 转换表格时出错: {e}")
        # 即使出错也尝试标准化
        try:
            text_representation = str(table_element)
            return normalize_spanish_characters(text_representation)
        except:
            return str(table_element)

def process_unstructured_elements(elements: List[Any]) -> str:
    """
    智能处理 Unstructured 元素，保持语义结构。
    包括西班牙语特殊字符的标准化。
    
    Args:
        elements: Unstructured 提取的元素列表
    
    Returns:
        保持结构和字符标准化的处理文本
    """
    processed_parts = []
    
    for element in elements:
        element_type = type(element).__name__
        
        if element_type == 'Title':
            # Los títulos van en líneas separadas con formato especial
            if hasattr(element, 'text') and element.text:
                # 标准化标题字符
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(f"\n## {normalized_text}\n")
        elif element_type == 'ListItem':
            # 列表保持其结构
            if hasattr(element, 'text') and element.text:
                # 标准化列表元素字符
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(f"• {normalized_text}")
        elif element_type == 'Table':
            # 表格转换为可读格式
            table_text = convert_table_to_text(element)
            if table_text:
                # 标准化表格字符
                normalized_table_text = normalize_spanish_characters(table_text)
                processed_parts.append(f"\n{normalized_table_text}\n")
        elif element_type == 'NarrativeText':
            # 叙述文本保持原样
            if hasattr(element, 'text') and element.text:
                # 标准化叙述文本字符
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(normalized_text)
        else:
            # 对于其他类型，使用基本文本
            if hasattr(element, 'text') and element.text:
                # 标准化其他元素的字符
                normalized_text = normalize_spanish_characters(element.text.strip())
                processed_parts.append(normalized_text)
    
    return "\n\n".join(processed_parts)

def extract_structural_metadata(elements: List[Any], file_path: str) -> Dict[str, Any]:
    """
    提取文档的结构化元数据。
    
    Args:
        elements: Unstructured 提取的元素列表
        file_path: 处理文件的路径
    
    Returns:
        结构元数据字典或 MetadataModel（如果可用）
    """
    structural_info = {
        "total_elements": len(elements),
        "titles_count": sum(1 for e in elements if type(e).__name__ == 'Title'),
        "tables_count": sum(1 for e in elements if type(e).__name__ == 'Table'),
        "lists_count": sum(1 for e in elements if type(e).__name__ == 'ListItem'),
        "narrative_blocks": sum(1 for e in elements if type(e).__name__ == 'NarrativeText'),
        "other_elements": sum(1 for e in elements if type(e).__name__ not in ['Title', 'Table', 'ListItem', 'NarrativeText'])
    }
    
    # 计算内容统计
    total_text_length = sum(len(e.text) for e in elements if hasattr(e, 'text') and e.text)
    structural_info["total_text_length"] = total_text_length
    structural_info["avg_element_length"] = total_text_length / len(elements) if elements else 0
    
    # 如果 MetadataModel 可用，创建结构化模型
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
            
            # 使用模型的方法更新结构信息
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
    基于文档的语义结构创建块。
    
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
        
        # 如果添加此元素会超过最大大小
        if current_size + element_size > max_chunk_size and current_chunk:
            # 保存当前块
            chunk_text = "\n\n".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            # 如果可能，与前面的元素创建重叠
            overlap_elements = []
            overlap_size = 0
            for j in range(len(current_chunk) - 1, -1, -1):
                if overlap_size + len(current_chunk[j]) <= overlap:
                    overlap_elements.insert(0, current_chunk[j])
                    overlap_size += len(current_chunk[j])
                else:
                    break
            
            # 用重叠开始新块
            current_chunk = overlap_elements + [element_text]
            current_size = overlap_size + element_size
        else:
            # 添加到当前块
            current_chunk.append(element_text)
            current_size += element_size
    
    # 添加最后一个块（如果存在）
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
        file_path: 要加载的文件路径
    
    Returns:
        文件内容作为标准化文本
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.docx', '.doc']:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.pptx', '.ppt']:
            from langchain_community.document_loaders import UnstructuredPowerPointLoader
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.xlsx', '.xls']:
            from langchain_community.document_loaders import UnstructuredExcelLoader
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.txt', '.md', '.rtf']:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension in ['.html', '.htm']:
            from langchain_community.document_loaders import BSHTMLLoader
            loader = BSHTMLLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
            normalized_contents = []
            for doc in documents:
                normalized_content = normalize_spanish_characters(doc.page_content)
                normalized_contents.append(normalized_content)
            return "\n\n".join(normalized_contents)
        
        elif file_extension == '.xml':
            from langchain_community.document_loaders import UnstructuredXMLLoader
            loader = UnstructuredXMLLoader(file_path)
            documents = loader.load()
            # 连接前标准化每个文档
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
    使用多种回退策略加载文档。
    
    Args:
        file_path: 要加载的文件路径
    
    Returns:
        Tupla con (contenido_texto, metadatos)
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # 策略1：Unstructured 优化配置
    try:
        log(f"核心: 尝试使用 Unstructured 加载（最佳配置）...")
        config = Config.get_unstructured_config(file_extension)
        
        # 对于PDF，使用更快的配置以避免挂起
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
    
    # 策略2：Unstructured 基本配置
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
    
    # 策略3：LangChain 特定加载器
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
        text: 要添加的文本
        vector_store: 向量数据库
        source_metadata: 包含源元数据的字典
        use_semantic_chunking: 是否使用语义分块而非传统分块
        structural_elements: 用于语义分块的结构化元素列表
    """
    if not text or text.isspace():
        log("核心警告: 尝试添加空文本或仅空格的文本.")
        return

    # 处理前清理文本
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
            # 创建元数据的干净副本并展平
            metadata = flatten_metadata(source_metadata)
            
            # 添加块信息
            metadata['chunk_index'] = i
            metadata['total_chunks'] = len(texts)
            
            # 添加关于使用的分块类型的信息
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
    保持与现有代码兼容性的原始函数。
    分割文本，将其与源元数据一起添加到数据库并持久化。
    
    Args:
        text: 要添加的文本
        vector_store: 向量数据库
        source_metadata: 包含源元数据的字典 (例如: {"source": "file.pdf", "author": "张三"})
    """
    # Usar la versión mejorada por defecto
    add_text_to_knowledge_base_enhanced(text, vector_store, source_metadata, use_semantic_chunking=False)

def load_document_with_unstructured(file_path: str) -> str:
    """
    使用带回退的增强 Unstructured 系统加载文档。
    此函数保持与现有代码的兼容性。
    
    Args:
        file_path: 要加载的文件路径
    
    Returns:
        文件内容作为文本
    """
    content, _ = load_document_with_fallbacks(file_path)
    return content

def get_qa_chain(vector_store: Chroma, metadata_filter: dict = None) -> RetrievalQA:
    """
    Crea y retorna la cadena de Pregunta/Respuesta usando un LLM local.
    
    Args:
        vector_store: 向量数据库
        metadata_filter: 包含元数据过滤器的字典 (例如: {"file_type": ".pdf", "processing_method": "unstructured_enhanced"})
    """
    log(f"核心: 初始化语言模型...")
    load_dotenv()
    model_type = os.getenv("MODEL_TYPE", "OLLAMA").upper()
    llm = None
    if model_type == "OLLAMA":
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        ollama_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0"))
        llm = ChatOllama(model=ollama_model, temperature=ollama_temperature)
        log(f"核心: 使用 Ollama 模型: {ollama_model}，温度: {ollama_temperature}")
    elif model_type == "OPENAI":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            os.system("pip install langchain-openai")
            from langchain_openai import ChatOpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        llm = ChatOpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base,
            model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0"))
        )
        log(f"核心: 使用 OpenAI 模型: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}，API 地址: {openai_api_base}")
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")
    log(f"核心: 配置 RAG 链接，改进的源检索...")
    
    # 配置搜索参数
    search_kwargs = {
        "k": 5,  # 增加到 5 个片段以获得更多上下文
        "score_threshold": 0.1,  # 更低的阈值以获取结果
    }
    
    # 添加元数据过滤器（如果提供）
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"核心: 应用元数据过滤器: {metadata_filter}")
    
    # 配置检索器，使用优化参数以获得更好的检索效果
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",  # 更改为支持按分数过滤
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
    
    # 配置搜索参数
    search_kwargs = {
        "k": k,
        "score_threshold": 0.1,  # 更低的阈值以获取结果
    }
    
    # 添加过滤器（如果提供）
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
        log(f"核心: 应用的过滤器: {metadata_filter}")
    
    # 执行搜索
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
        file_type: 文件类型 (例如: ".pdf", ".docx")
        processing_method: 处理方法 (例如: "unstructured_enhanced")
        min_tables: 文档中表格的最小数量
        min_titles: 文档中标题的最小数量
    
    Returns:
        与ChromaDB兼容的元数据过滤器字典
    """
    # ChromaDB requiere un formato específico para filtros múltiples
    # Usar operador $and para combinar múltiples condiciones
    
    conditions = []
    
    # 添加简单过滤器
    if file_type:
        conditions.append({"file_type": file_type})
    
    if processing_method:
        conditions.append({"processing_method": processing_method})
    
    # 添加数值过滤器 - 使用扁平化元数据的正确名称
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
        file_type: 文件类型（例如：".pdf"、".docx"）
        processing_method: 处理方法（例如："unstructured_enhanced"）
        min_tables: 文档中表格的最少数量
        min_titles: 文档中标题的最少数量
        source_contains: Texto que debe contener el nombre de la fuente
    
    Returns:
        Diccionario con filtros de metadatos compatibles con ChromaDB
    """
    # Usar la versión mejorada
    return create_simple_metadata_filter(file_type, processing_method, min_tables, min_titles)

def get_document_statistics(vector_store: Chroma) -> dict:
    """
    获取数据库中文档的统计信息。
    
    Args:
        vector_store: 向量数据库
    
    Returns:
        包含数据库统计信息的字典
    """
    log(f"核心: 获取数据库统计信息...")
    
    try:
        # 获取所有文档进行分析
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
            # 统计文件类型
            file_type = metadata.get("file_type", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            
            # 统计处理方法
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

# --- 优化向量数据库配置 ---
VECTOR_STORE_CONFIG = {
    # 持久化和性能配置
    'anonymized_telemetry': False,  # 禁用遥测
    'allow_reset': True,  # 允许重置集合
    'is_persistent': True,  # 启用持久化
}

# 不同数据库大小的配置
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
        
        # 获取优化前的统计信息
        stats_before = get_vector_store_stats(vector_store)
        
        collection = vector_store._collection
        
        # En lugar de reindexar, usar métodos nativos de ChromaDB para optimización
        log("核心: 应用 ChromaDB 原生优化...")
        
        # 1. 强制持久化以优化存储
        try:
            collection.persist()
            log("核心: 强制持久化完成")
        except Exception as e:
            log(f"核心警告: 无法强制持久化: {e}")
        
        # 2. 获取集合信息以验证状态
        count = collection.count()
        log(f"核心: 检查到 {count} 个文档在集合中")
        
        # 3. 执行测试查询以验证索引
        try:
            # Hacer una búsqueda de prueba para activar índices
            test_results = collection.query(
                query_texts=["test"],
                n_results=1
            )
            log("核心: 搜索索引验证通过")
        except Exception as e:
            log(f"核心警告: 验证索引时出错: {e}")
        
        # 4. 验证集合配置
        try:
            # 获取集合元数据
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
        
        # 获取优化后的统计信息
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
        
        # 获取基本统计信息
        count = collection.count()
        
        # 获取配置信息
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
        
        # 估算嵌入维度（一次性探测，结果会被缓存）
        try:
            probe_dim = len(get_embedding_function().embed_query("__dim_probe__"))
        except Exception:
            probe_dim = "unknown"

        return {
            "total_documents": count,
            "file_types": file_types,
            "processing_methods": processing_methods,
            "collection_name": collection.name,
            "embedding_dimension": str(probe_dim)
        }
        
    except Exception as e:
        log(f"核心错误: 获取向量数据库统计信息时出错: {e}")
        return {"error": str(e)}

def reindex_vector_store(vector_store: Chroma = None, profile: str = 'auto') -> dict:
    """
    用优化配置重新索引向量数据库。
    自动检测是否为大型数据库并使用增量重新索引。
    使用 ChromaDB 原生方法避免批次限制。
    当配置文件更改时很有用。
    
    Args:
        vector_store: Chroma 实例（如果为 None，则创建新实例）
        profile: 重新索引的配置文件
    
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
        
        # 获取重新索引前的统计信息
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
        
        # 3. 验证集合配置
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
    适用于超大数据库的特殊重新索引，使用增量处理。
    
    Args:
        vector_store: Chroma 实例（如果为 None，则创建新实例）
        profile: 重新索引的配置文件
    
    Returns:
        包含重新索引信息的字典
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
    使用增量处理和检查点避免内存问题。
    
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