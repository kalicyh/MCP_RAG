"""
Excepciones personalizadas para Bulk Ingest GUI
"""

class BulkIngestError(Exception):
    """Excepción base para errores de Bulk Ingest"""
    pass

class ProcessingError(BulkIngestError):
    """Error durante el procesamiento de documentos"""
    pass

class StorageError(BulkIngestError):
    """Error durante el almacenamiento en base de datos"""
    pass

class ConfigurationError(BulkIngestError):
    """Error en la configuración de la aplicación"""
    pass

class ValidationError(BulkIngestError):
    """Error de validación de datos"""
    pass

class FileProcessingError(ProcessingError):
    """Error específico al procesar un archivo"""
    def __init__(self, file_path: str, original_error: Exception):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Error procesando archivo '{file_path}': {original_error}")

class DirectoryNotFoundError(ValidationError):
    """Error cuando no se encuentra el directorio especificado"""
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        super().__init__(f"Directorio no encontrado: {directory_path}")

class UnsupportedFileTypeError(ValidationError):
    """Error cuando se intenta procesar un tipo de archivo no soportado"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Tipo de archivo no soportado: {file_path}")

class MemoryLimitExceededError(ProcessingError):
    """Error cuando se excede el límite de memoria"""
    def __init__(self, current_usage: int, limit: int):
        self.current_usage = current_usage
        self.limit = limit
        super().__init__(f"Límite de memoria excedido: {current_usage}MB > {limit}MB")

class DatabaseConnectionError(StorageError):
    """Error de conexión con la base de datos"""
    def __init__(self, original_error: Exception):
        self.original_error = original_error
        super().__init__(f"Error de conexión con base de datos: {original_error}")

class ConfigurationLoadError(ConfigurationError):
    """Error al cargar la configuración"""
    def __init__(self, config_file: str, original_error: Exception):
        self.config_file = config_file
        self.original_error = original_error
        super().__init__(f"Error cargando configuración desde '{config_file}': {original_error}")

class ConfigurationSaveError(ConfigurationError):
    """Error al guardar la configuración"""
    def __init__(self, config_file: str, original_error: Exception):
        self.config_file = config_file
        self.original_error = original_error
        super().__init__(f"Error guardando configuración en '{config_file}': {original_error}") 