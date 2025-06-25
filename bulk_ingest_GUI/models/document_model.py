"""
Modelo de documento para Bulk Ingest GUI
"""

import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from gui_utils.constants import get_file_type, is_supported_file
import tkinter as tk
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from gui_utils.exceptions import UnsupportedFileTypeError, ValidationError


@dataclass
class DocumentMetadata:
    """Metadatos de un documento"""
    source: str
    file_path: str
    file_type: str
    processed_date: str
    processing_method: str
    structural_info: Dict[str, Any] = field(default_factory=dict)
    converted_to_md: Optional[str] = None
    size_bytes: int = 0
    word_count: int = 0
    processing_time: float = 0.0
    # Permitir kwargs extra para ignorar campos inesperados
    extra_kwargs: Dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        # Eliminar cualquier campo inesperado de los atributos
        for k in list(self.extra_kwargs.keys()):
            if hasattr(self, k):
                setattr(self, k, self.extra_kwargs.pop(k))

    def to_dict(self) -> Dict[str, Any]:
        """Convertir metadatos a diccionario"""
        base = {
            'source': self.source,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'processed_date': self.processed_date,
            'processing_method': self.processing_method,
            'structural_info': self.structural_info,
            'converted_to_md': self.converted_to_md,
            'size_bytes': self.size_bytes,
            'word_count': self.word_count,
            'processing_time': self.processing_time
        }
        base.update(self.extra_kwargs)
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        # Separar los campos conocidos y los extra
        known_fields = {f.name for f in cls.__dataclass_fields__.values() if f.name != 'extra_kwargs'}
        init_args = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(**init_args, extra_kwargs=extra)


class DocumentPreview:
    """
    Modelo de documento con funcionalidades de previsualización
    """
    
    def __init__(self, 
                 file_path: str, 
                 markdown_content: str, 
                 file_type: str = None, 
                 original_name: str = None, 
                 metadata: Dict[str, Any] = None,
                 structural_elements: List[Any] = None):
        """
        Inicializar documento
        
        Args:
            file_path: Ruta completa del archivo
            markdown_content: Contenido convertido a Markdown
            file_type: Tipo de archivo (se infiere si no se proporciona)
            original_name: Nombre original del archivo
            metadata: Metadatos del documento
            structural_elements: Elementos estructurales para chunking semántico
        """
        self.file_path = file_path
        self.markdown_content = markdown_content
        self.structural_elements = structural_elements or []
        
        # Validar y establecer tipo de archivo
        if file_type:
            self.file_type = file_type
        else:
            self.file_type = get_file_type(file_path)
        
        # Validar que el tipo de archivo es soportado
        if not is_supported_file(file_path):
            raise UnsupportedFileTypeError(file_path)
        
        # Establecer nombre original
        if original_name:
            self.original_name = original_name
        else:
            self.original_name = os.path.basename(file_path)
        
        # Crear metadatos
        if metadata:
            self.metadata = DocumentMetadata.from_dict(metadata)
        else:
            self.metadata = self._create_default_metadata()
        
        # Variables de UI
        self.selected = tk.BooleanVar(value=True)
        self.preview_visible = False
        
        # Calcular estadísticas
        self._calculate_statistics()
    
    def _create_default_metadata(self) -> DocumentMetadata:
        """Crear metadatos por defecto"""
        return DocumentMetadata(
            source=self.original_name,
            file_path=self.file_path,
            file_type=self.file_type,
            processed_date=datetime.now().isoformat(),
            processing_method="unstructured_enhanced",
            size_bytes=len(self.markdown_content.encode('utf-8')),
            word_count=len(self.markdown_content.split())
        )
    
    def _calculate_statistics(self):
        """Calcular estadísticas del documento"""
        self.metadata.size_bytes = len(self.markdown_content.encode('utf-8'))
        self.metadata.word_count = len(self.markdown_content.split())
    
    @property
    def size_kb(self) -> float:
        """Tamaño en KB"""
        return self.metadata.size_bytes / 1024
    
    @property
    def size_mb(self) -> float:
        """Tamaño en MB"""
        return self.metadata.size_bytes / (1024 * 1024)
    
    @property
    def is_large_document(self) -> bool:
        """Verificar si es un documento grande"""
        return self.metadata.size_bytes > 1024 * 1024  # > 1MB
    
    @property
    def has_structural_elements(self) -> bool:
        """Verificar si tiene elementos estructurales"""
        return len(self.structural_elements) > 0
    
    def get_preview_content(self, max_length: int = 50000) -> str:
        """Obtener contenido para previsualización"""
        if len(self.markdown_content) <= max_length:
            return self.markdown_content
        
        return (self.markdown_content[:max_length] + 
                "\n\n... [CONTENIDO TRUNCADO PARA PREVISUALIZACIÓN] ...")
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen del documento"""
        return {
            'name': self.original_name,
            'type': self.file_type,
            'size_kb': round(self.size_kb, 2),
            'word_count': self.metadata.word_count,
            'selected': self.selected.get(),
            'has_structural_elements': self.has_structural_elements,
            'processing_method': self.metadata.processing_method
        }
    
    def validate(self) -> bool:
        """Validar que el documento es válido"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.file_path):
                raise ValidationError(f"Archivo no encontrado: {self.file_path}")
            
            # Verificar que tiene contenido
            if not self.markdown_content or self.markdown_content.isspace():
                raise ValidationError(f"Documento vacío: {self.original_name}")
            
            # Verificar tipo de archivo
            if not is_supported_file(self.file_path):
                raise UnsupportedFileTypeError(self.file_path)
            
            return True
            
        except Exception as e:
            raise ValidationError(f"Error validando documento '{self.original_name}': {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir documento a diccionario para serialización"""
        return {
            'file_path': self.file_path,
            'markdown_content': self.markdown_content,
            'file_type': self.file_type,
            'original_name': self.original_name,
            'metadata': self.metadata.to_dict(),
            'selected': self.selected.get()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentPreview':
        """Crear documento desde diccionario"""
        doc = cls(
            file_path=data['file_path'],
            markdown_content=data['markdown_content'],
            file_type=data.get('file_type'),
            original_name=data.get('original_name'),
            metadata=data.get('metadata')
        )
        doc.selected.set(data.get('selected', True))
        return doc
    
    def __str__(self) -> str:
        return f"DocumentPreview({self.original_name}, {self.file_type}, {self.size_kb:.1f}KB)"
    
    def __repr__(self) -> str:
        return self.__str__() 