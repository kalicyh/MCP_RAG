"""
MCP 服务器配置模块
=================================

此模块处理 MCP 服务器的所有配置，
包括路径、Unstructured 配置和系统参数。
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# 加载环境变量
load_dotenv()

class Config:
    """
    MCP 服务器的集中配置类。
    """
    
    # 服务器配置
    SERVER_NAME = "ragmcp"
    SERVER_VERSION = "1.0.0"
    
    # 数据路径
    CONVERTED_DOCS_DIR = "./data/documents"
    VECTOR_STORE_DIR = "./data/vector_store"
    EMBEDDING_CACHE_DIR = "./embedding_cache"
    
    # 模型配置
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DEVICE = "cpu"
    
    # 分块配置
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    # 缓存配置
    MAX_CACHE_SIZE = 1000
    
    # 针对不同文档类型的优化配置
    UNSTRUCTURED_CONFIGS = {
        # Office 文档
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
        
        # OpenDocument 文档
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
        
        # Web 和标记格式
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
        
        # 纯文本格式
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
        
        # 数据格式
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
        
        # 图像（需要 OCR）
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
        
        # 电子邮件
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
    
    @classmethod
    def get_unstructured_config(cls, file_extension: str) -> Dict[str, Any]:
        """
        获取特定文件类型的 Unstructured 配置。
        
        Args:
            file_extension: 文件扩展名（例如：'.pdf'）
            
        Returns:
            文件类型的 Unstructured 配置
        """
        return cls.UNSTRUCTURED_CONFIGS.get(file_extension.lower(), {
            'strategy': 'fast',
            'include_metadata': True,
            'max_partition': 2000,
            'new_after_n_chars': 1500
        })
    
    @classmethod
    def ensure_directories(cls):
        """
        确保所有必要的目录都存在。
        """
        directories = [
            cls.CONVERTED_DOCS_DIR,
            cls.VECTOR_STORE_DIR,
            cls.EMBEDDING_CACHE_DIR
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def get_env_var(cls, key: str, default: str = None) -> str:
        """
        获取环境变量并提供默认值。
        
        Args:
            key: 环境变量名称
            default: 如果不存在的默认值
            
        Returns:
            环境变量的值或默认值
        """
        return os.getenv(key, default) 