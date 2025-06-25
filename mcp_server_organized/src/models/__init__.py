# MCP Models Module
"""
Módulo de modelos de datos del servidor MCP.
Contiene las estructuras de datos y modelos principales.
"""

from .document_model import DocumentModel
from .metadata_model import MetadataModel

__all__ = [
    'DocumentModel',
    'MetadataModel'
] 