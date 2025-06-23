"""
Bulk Ingest GUI - Sistema Modular Avanzado
==========================================

Sistema de procesamiento y almacenamiento de documentos con arquitectura MVC.
"""

__version__ = "2.0.0"
__author__ = "Sistema RAG Modular"
__description__ = "Sistema de ingesta masiva de documentos con interfaz gráfica avanzada"

# Importar componentes principales
from .main import BulkIngestApp, main

__all__ = ['BulkIngestApp', 'main'] 