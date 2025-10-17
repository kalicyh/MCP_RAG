"""
MCP 服务器元数据模型
===================

此模块定义了 RAG 系统中元数据的数据结构。
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class MetadataModel:
    """
    用于表示文档元数据的数据模型。
    """
    
    # 基本信息
    source: str
    input_type: str
    processed_date: datetime = field(default_factory=datetime.now)
    
    # 文件信息
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    
    # 处理信息
    processing_method: str = "未知"
    processing_duration: Optional[float] = None
    
    # Información estructural
    structural_info: Dict[str, Any] = field(default_factory=dict)
    total_elements: int = 0
    titles_count: int = 0
    tables_count: int = 0
    lists_count: int = 0
    narrative_blocks: int = 0
    other_elements: int = 0
    # 新增字段，兼容所有元数据
    word_count: Optional[int] = None
    size_bytes: Optional[int] = None
    
    # Información de chunking
    chunking_method: str = "standard"
    chunk_count: int = 0
    avg_chunk_size: float = 0.0
    
    # Información de embeddings
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None
    
    # Metadatos adicionales
    additional_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Campos adicionales para compatibilidad con el sistema existente
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    domain: Optional[str] = None
    server_processed_date: Optional[datetime] = None
    
    # Campos de información estructural detallada
    structural_info_total_text_length: Optional[int] = None
    structural_info_total_elements: Optional[int] = None
    structural_info_titles_count: Optional[int] = None
    structural_info_tables_count: Optional[int] = None
    structural_info_lists_count: Optional[int] = None
    structural_info_narrative_blocks: Optional[int] = None
    structural_info_other_elements: Optional[int] = None
    
    # Campos adicionales para compatibilidad completa
    structural_info_avg_element_length: Optional[float] = None
    converted_to_md: Optional[bool] = None
    
    def __post_init__(self):
        """Inicialización post-construcción del dataclass."""
        # Calcular información estructural si no está presente
        if not self.structural_info:
            self.structural_info = {
                'total_elements': self.total_elements,
                'titles_count': self.titles_count,
                'tables_count': self.tables_count,
                'lists_count': self.lists_count,
                'narrative_blocks': self.narrative_blocks,
                'other_elements': self.other_elements
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Diccionario con todos los metadatos
        """
        return {
            'source': self.source,
            'input_type': self.input_type,
            'processed_date': self.processed_date.isoformat(),
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'processing_method': self.processing_method,
            'processing_duration': self.processing_duration,
            'structural_info': self.structural_info,
            'total_elements': self.total_elements,
            'titles_count': self.titles_count,
            'tables_count': self.tables_count,
            'lists_count': self.lists_count,
            'narrative_blocks': self.narrative_blocks,
            'other_elements': self.other_elements,
            'chunking_method': self.chunking_method,
            'chunk_count': self.chunk_count,
            'avg_chunk_size': self.avg_chunk_size,
            'embedding_model': self.embedding_model,
            'embedding_dimension': self.embedding_dimension,
            'additional_metadata': self.additional_metadata,
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks,
            'domain': self.domain,
            'server_processed_date': self.server_processed_date,
            'structural_info_total_text_length': self.structural_info_total_text_length,
            'structural_info_total_elements': self.structural_info_total_elements,
            'structural_info_titles_count': self.structural_info_titles_count,
            'structural_info_tables_count': self.structural_info_tables_count,
            'structural_info_lists_count': self.structural_info_lists_count,
            'structural_info_narrative_blocks': self.structural_info_narrative_blocks,
            'structural_info_other_elements': self.structural_info_other_elements,
            'structural_info_avg_element_length': self.structural_info_avg_element_length,
            'converted_to_md': self.converted_to_md
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataModel':
        """
        Crea un MetadataModel desde un diccionario.
        
        Args:
            data: Diccionario con los metadatos
            
        Returns:
            Instancia de MetadataModel
        """
        # Asegurar que los campos requeridos estén presentes
        if 'source' not in data:
            data['source'] = data.get('file_path', 'unknown')
        if 'input_type' not in data:
            data['input_type'] = 'unknown'
        
        # Convertir la fecha de string a datetime
        if 'processed_date' in data and isinstance(data['processed_date'], str):
            try:
                data['processed_date'] = datetime.fromisoformat(data['processed_date'])
            except ValueError:
                data['processed_date'] = datetime.now()
        
        # Convertir la fecha del servidor si existe
        if 'server_processed_date' in data and isinstance(data['server_processed_date'], str):
            try:
                data['server_processed_date'] = datetime.fromisoformat(data['server_processed_date'])
            except ValueError:
                data['server_processed_date'] = None
        
        return cls(**data)
    
    def update_structural_info(self, elements: List[Any]):
        """
        Actualiza la información estructural basada en elementos de Unstructured.
        
        Args:
            elements: Lista de elementos de Unstructured
        """
        from unstructured.documents.elements import Title, ListItem, Table, NarrativeText
        
        self.total_elements = len(elements)
        self.titles_count = sum(1 for elem in elements if isinstance(elem, Title))
        self.tables_count = sum(1 for elem in elements if isinstance(elem, Table))
        self.lists_count = sum(1 for elem in elements if isinstance(elem, ListItem))
        self.narrative_blocks = sum(1 for elem in elements if isinstance(elem, NarrativeText))
        self.other_elements = self.total_elements - self.titles_count - self.tables_count - self.lists_count - self.narrative_blocks
        
        # Actualizar structural_info
        self.structural_info = {
            'total_elements': self.total_elements,
            'titles_count': self.titles_count,
            'tables_count': self.tables_count,
            'lists_count': self.lists_count,
            'narrative_blocks': self.narrative_blocks,
            'other_elements': self.other_elements
        }
    
    def get_summary(self) -> str:
        """
        Obtiene un resumen de los metadatos.
        
        Returns:
            Resumen de los metadatos
        """
        return f"Fuente: {self.source} - Método: {self.processing_method} - Elementos: {self.total_elements} - Chunks: {self.chunk_count}"
    
    def is_rich_content(self) -> bool:
        """
        Verifica si el contenido es rico en estructura.
        
        Returns:
            True si el contenido tiene buena estructura
        """
        return (
            self.titles_count > 0 or
            self.tables_count > 0 or
            self.lists_count > 0 or
            self.narrative_blocks > 2
        ) 