"""
Constantes y configuración centralizada para Bulk Ingest GUI
"""

import os
from pathlib import Path

APP_NAME = "Bulk Ingest GUI"
VERSION = "1.0.0"

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS
# =============================================================================

# Extensiones de archivo soportadas
SUPPORTED_EXTENSIONS = [
    # Documentos de Office
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".rtf",
    # Documentos OpenDocument
    ".odt", ".odp", ".ods",
    # Formatos web y markup
    ".html", ".htm", ".xml", ".md",
    # Formatos de texto plano
    ".txt", ".csv", ".tsv",
    # Formatos de datos
    ".json", ".yaml", ".yml",
    # Imágenes (requieren OCR)
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
    # Correos electrónicos
    ".eml", ".msg"
]

# Directorios
# Usar directorios del servidor MCP organizado
current_dir = Path(__file__).parent.parent.resolve()
project_root = current_dir.parent.resolve()
mcp_server_dir = project_root / "mcp_server_organized"

CONVERTED_DOCS_DIR = str(mcp_server_dir / "data" / "documents")
EMBEDDING_CACHE_DIR = str(mcp_server_dir / "embedding_cache")
VECTOR_STORE_DIR = str(mcp_server_dir / "data" / "vector_store")
CONFIG_FILE = "bulk_ingest_config.json"

# =============================================================================
# CONFIGURACIÓN DE LA INTERFAZ
# =============================================================================

# Geometría de ventana
DEFAULT_WINDOW_SIZE = "1100x850"
MIN_WINDOW_SIZE = (900, 700)

# Colores del tema "Terminal Refinada"
COLORS = {
    'BG_COLOR': "#0D1117",           # Negro azulado (GitHub Dark)
    'FG_COLOR': "#56F175",           # Verde CRT
    'SELECT_BG': "#56F175",          # Verde para selección
    'SELECT_FG': "#0D1117",          # Negro para texto seleccionado
    'TROUGH_COLOR': "#161B22",       # Fondo de barra de progreso
    'BORDER_COLOR': "#30363D",       # Borde gris oscuro
    'HIGHLIGHT_BORDER': "#56F175",   # Borde verde para hover
    'WARNING_COLOR': "#F1E056",      # Amarillo para advertencias
    'ERROR_COLOR': "#F85149",        # Rojo para errores
}

# Fuentes
FONT_FAMILY = "Consolas"
FONT_SIZES = {
    'title': 16,
    'subtitle': 11,
    'normal': 10,
    'small': 9
}

# =============================================================================
# CONFIGURACIÓN DE RENDIMIENTO
# =============================================================================

# Límites de memoria y rendimiento
PERFORMANCE_LIMITS = {
    'max_preview_length': 50000,     # Caracteres para previsualización
    'batch_size': 10,                # Documentos por lote
    'memory_limit': 100 * 1024 * 1024,  # 100MB límite de memoria
    'max_log_lines': 1000,           # Líneas máximas en logs
    'update_interval': 100,          # ms entre actualizaciones de UI
}

# =============================================================================
# CONFIGURACIÓN DE PROCESAMIENTO
# =============================================================================

# Configuración de chunking
CHUNKING_CONFIG = {
    'default_chunk_size': 1000,
    'default_overlap': 200,
    'semantic_chunking': True,
}

# Configuración de almacenamiento
STORAGE_CONFIG = {
    'confirm_required': True,
    'batch_processing': True,
    'progress_update_interval': 0.5,  # segundos
}

# =============================================================================
# MENSAJES Y TEXTOS
# =============================================================================

MESSAGES = {
    'processing': {
        'start': "🚀 Iniciando procesamiento...",
        'complete': "✅ Procesamiento completado",
        'error': "❌ Error durante el procesamiento",
        'stopped': "⏹️ Procesamiento detenido",
    },
    'storage': {
        'start': "💾 Iniciando almacenamiento...",
        'complete': "🎉 Almacenamiento completado",
        'error': "❌ Error durante el almacenamiento",
        'stopped': "⏹️ Almacenamiento detenido",
    },
    'ui': {
        'ready': "Listo para procesar",
        'select_directory': "Por favor selecciona un directorio",
        'no_documents': "No hay documentos para procesar",
        'confirm_storage': "Por favor confirma el almacenamiento",
    }
}

# =============================================================================
# VALIDACIONES
# =============================================================================

def is_supported_file(filename: str) -> bool:
    """Verificar si un archivo tiene una extensión soportada"""
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)

def get_file_type(filename: str) -> str:
    """Obtener el tipo de archivo basado en la extensión"""
    return os.path.splitext(filename)[1].lower()

def validate_directory(path: str) -> bool:
    """Validar que un directorio existe y es accesible"""
    return os.path.isdir(path) and os.access(path, os.R_OK) 