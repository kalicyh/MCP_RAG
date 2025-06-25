"""
Paquete de servicios para Bulk Ingest GUI
"""

from .configuration_service import ConfigurationService
from .document_service import DocumentService

__all__ = [
    'ConfigurationService',
    'DocumentService'
] 