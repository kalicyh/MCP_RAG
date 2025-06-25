"""
Document Model para el Servidor MCP
==================================

Este módulo define las estructuras de datos para documentos
y metadatos en el sistema RAG.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class DocumentModel:
    """
    Modelo de datos para representar un documento procesado.
    """
    
    # Información básica del documento
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    
    # Contenido procesado
    content: str
    processed_content: str
    
    # Metadatos
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Información de procesamiento
    processing_method: str = "unknown"
    processing_date: datetime = field(default_factory=datetime.now)
    
    # Información estructural
    structural_elements: List[Any] = field(default_factory=list)
    total_elements: int = 0
    titles_count: int = 0
    tables_count: int = 0
    lists_count: int = 0
    
    # Información de chunking
    chunks: List[str] = field(default_factory=list)
    chunk_count: int = 0
    
    def __post_init__(self):
        """Inicialización post-construcción del dataclass."""
        if not self.file_name:
            self.file_name = self.file_path.split('/')[-1] if '/' in self.file_path else self.file_path.split('\\')[-1]
        
        if not self.file_type:
            self.file_type = self.file_name.split('.')[-1].lower() if '.' in self.file_name else "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Diccionario con todos los datos del documento
        """
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'content': self.content,
            'processed_content': self.processed_content,
            'metadata': self.metadata,
            'processing_method': self.processing_method,
            'processing_date': self.processing_date.isoformat(),
            'structural_elements': len(self.structural_elements),
            'total_elements': self.total_elements,
            'titles_count': self.titles_count,
            'tables_count': self.tables_count,
            'lists_count': self.lists_count,
            'chunk_count': self.chunk_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentModel':
        """
        Crea un DocumentModel desde un diccionario.
        
        Args:
            data: Diccionario con los datos del documento
            
        Returns:
            Instancia de DocumentModel
        """
        # Convertir la fecha de string a datetime
        if 'processing_date' in data and isinstance(data['processing_date'], str):
            data['processing_date'] = datetime.fromisoformat(data['processing_date'])
        
        return cls(**data)
    
    def get_summary(self) -> str:
        """
        Obtiene un resumen del documento.
        
        Returns:
            Resumen del documento
        """
        return f"Documento: {self.file_name} ({self.file_type.upper()}) - {len(self.processed_content)} caracteres - {self.chunk_count} chunks"
    
    def is_valid(self) -> bool:
        """
        Verifica si el documento es válido.
        
        Returns:
            True si el documento es válido
        """
        return (
            bool(self.file_path) and
            bool(self.file_name) and
            bool(self.processed_content) and
            len(self.processed_content.strip()) > 0
        ) 