"""
Config Module para el Servidor MCP
=================================

Este módulo maneja toda la configuración del servidor MCP,
incluyendo rutas, configuraciones de Unstructured, y parámetros del sistema.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno
load_dotenv()

class Config:
    """
    Clase de configuración centralizada para el servidor MCP.
    """
    
    # Configuración del servidor
    SERVER_NAME = "ragmcp"
    SERVER_VERSION = "1.0.0"
    
    # Rutas de datos
    CONVERTED_DOCS_DIR = "./data/documents"
    VECTOR_STORE_DIR = "./data/vector_store"
    EMBEDDING_CACHE_DIR = "./embedding_cache"
    
    # Configuración de modelos
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DEVICE = "cpu"
    
    # Configuración de chunking
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    # Configuración de cache
    MAX_CACHE_SIZE = 1000
    
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
    
    @classmethod
    def get_unstructured_config(cls, file_extension: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de Unstructured para un tipo de archivo específico.
        
        Args:
            file_extension: Extensión del archivo (ej: '.pdf')
            
        Returns:
            Configuración de Unstructured para el tipo de archivo
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
        Asegura que todos los directorios necesarios existan.
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
        Obtiene una variable de entorno con valor por defecto.
        
        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la variable de entorno o el valor por defecto
        """
        return os.getenv(key, default) 