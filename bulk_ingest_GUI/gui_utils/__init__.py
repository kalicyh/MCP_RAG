"""
Utilidades y herramientas auxiliares
"""

from .constants import *
from .exceptions import *

__all__ = [
    # Constantes
    'SUPPORTED_EXTENSIONS', 'CONVERTED_DOCS_DIR', 'CONFIG_FILE',
    'DEFAULT_WINDOW_SIZE', 'MIN_WINDOW_SIZE', 'COLORS', 'FONT_FAMILY',
    'FONT_SIZES', 'PERFORMANCE_LIMITS', 'CHUNKING_CONFIG', 'STORAGE_CONFIG',
    'MESSAGES', 'is_supported_file', 'get_file_type', 'validate_directory',
    
    # Excepciones
    'BulkIngestError', 'ProcessingError', 'StorageError', 'ConfigurationError',
    'ValidationError', 'FileProcessingError', 'DirectoryNotFoundError',
    'UnsupportedFileTypeError', 'MemoryLimitExceededError', 'DatabaseConnectionError',
    'ConfigurationLoadError', 'ConfigurationSaveError'
] 