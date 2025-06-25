"""
Servicio de documentos para Bulk Ingest GUI
Integra con la nueva estructura modular del servidor MCP

Este servicio usa la misma base de datos que el servidor MCP para mantener
consistencia de datos entre la GUI y el servidor.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading
import queue
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

# Importar el wrapper de rag_core que maneja la configuración del servidor MCP
import bulk_ingest_GUI.rag_core_wrapper as rag_core_wrapper

from models.document_model import DocumentPreview, DocumentMetadata
from gui_utils.constants import SUPPORTED_EXTENSIONS, is_supported_file
from gui_utils.exceptions import (
    ProcessingError, FileProcessingError, DirectoryNotFoundError,
    UnsupportedFileTypeError, ValidationError
)


class DocumentService:
    """
    Servicio para manejo de documentos que integra con rag_core.py
    Usa la misma base de datos que el servidor MCP para consistencia
    """
    
    def __init__(self, config_service):
        self.config_service = config_service
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.stop_processing = False
        
        # Estadísticas de procesamiento
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
        
        # Verificar que rag_core esté disponible
        try:
            rag_core_wrapper.get_rag_functions()
            print("✅ DocumentService: rag_core configurado correctamente")
        except ImportError as e:
            print(f"❌ DocumentService: Error configurando rag_core: {e}")
            raise
    
    def process_directory(self, directory_path: str, save_markdown: bool = True, 
                         progress_callback=None, log_callback=None) -> List[DocumentPreview]:
        """
        Procesa todos los documentos en un directorio
        
        Args:
            directory_path: Ruta del directorio a procesar
            save_markdown: Si guardar copias en Markdown
            progress_callback: Función para reportar progreso
            log_callback: Función para reportar logs
            
        Returns:
            Lista de documentos procesados
        """
        if not os.path.isdir(directory_path):
            raise DirectoryNotFoundError(directory_path)
        
        # Limpiar estadísticas
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
        
        # Encontrar todos los archivos soportados
        files_to_process = self._find_supported_files(directory_path)
        
        if not files_to_process:
            if log_callback:
                log_callback("No se encontraron archivos soportados en el directorio")
            return []
        
        if log_callback:
            log_callback(f"Encontrados {len(files_to_process)} archivos para procesar")
        
        # Procesar archivos
        processed_documents = []
        
        for i, file_path in enumerate(files_to_process):
            if self.stop_processing:
                if log_callback:
                    log_callback("Procesamiento detenido por el usuario")
                break
            
            try:
                # Reportar progreso
                if progress_callback:
                    progress_callback(i + 1, len(files_to_process), os.path.basename(file_path))
                
                # Procesar documento
                document = self._process_single_file(file_path, save_markdown, log_callback)
                
                if document:
                    processed_documents.append(document)
                    self.stats['successful'] += 1
                    self.stats['total_size'] += document.metadata.size_bytes
                else:
                    self.stats['skipped'] += 1
                
                self.stats['total_processed'] += 1
                
            except Exception as e:
                self.stats['failed'] += 1
                self.stats['total_processed'] += 1
                if log_callback:
                    log_callback(f"Error procesando {os.path.basename(file_path)}: {str(e)}")
        
        if log_callback:
            log_callback(f"Procesamiento completado: {self.stats['successful']} exitosos, "
                        f"{self.stats['failed']} fallidos, {self.stats['skipped']} omitidos")
        
        return processed_documents
    
    def _find_supported_files(self, directory_path: str) -> List[str]:
        """Encuentra todos los archivos soportados en un directorio"""
        supported_files = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_supported_file(file):
                    supported_files.append(file_path)
        
        return supported_files
    
    def _process_single_file(self, file_path: str, save_markdown: bool, 
                           log_callback=None) -> Optional[DocumentPreview]:
        """
        Procesa un archivo individual usando rag_core.py
        
        Args:
            file_path: Ruta del archivo a procesar
            save_markdown: Si guardar copia en Markdown
            log_callback: Función para reportar logs
            
        Returns:
            DocumentPreview si se procesó exitosamente, None si se omitió
        """
        try:
            if log_callback:
                log_callback(f"Procesando: {os.path.basename(file_path)}")
            
            # Usar rag_core para cargar el documento con elementos estructurales
            markdown_content, metadata, structural_elements = rag_core_wrapper.load_document_with_elements(file_path)
            
            if not markdown_content or markdown_content.isspace():
                if log_callback:
                    log_callback(f"Documento vacío: {os.path.basename(file_path)}")
                return None
            
            # Crear metadatos mejorados
            enhanced_metadata = self._create_enhanced_metadata(file_path, metadata, markdown_content)
            
            # Guardar copia en Markdown si se solicita
            if save_markdown:
                md_path = self._save_markdown_copy(file_path, markdown_content)
                if md_path:
                    enhanced_metadata['converted_to_md'] = md_path
            
            # Crear documento
            document = DocumentPreview(
                file_path=file_path,
                markdown_content=markdown_content,
                file_type=os.path.splitext(file_path)[1].lower(),
                original_name=os.path.basename(file_path),
                metadata=enhanced_metadata,
                structural_elements=structural_elements
            )
            
            # Validar documento
            document.validate()
            
            if log_callback:
                log_callback(f"✅ {os.path.basename(file_path)} procesado ({len(markdown_content)} caracteres)")
            
            return document
            
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error procesando {os.path.basename(file_path)}: {str(e)}")
            raise FileProcessingError(file_path, e)
    
    def _create_enhanced_metadata(self, file_path: str, original_metadata: Dict[str, Any], 
                                content: str) -> Dict[str, Any]:
        """Crea metadatos mejorados para el documento"""
        enhanced_metadata = original_metadata.copy() if original_metadata else {}
        
        # Añadir información adicional
        enhanced_metadata.update({
            'file_path': file_path,
            'original_name': os.path.basename(file_path),
            'file_type': os.path.splitext(file_path)[1].lower(),
            'processed_date': datetime.now().isoformat(),
            'size_bytes': len(content.encode('utf-8')),
            'word_count': len(content.split()),
            'character_count': len(content),
            'processing_service': 'document_service_v2'
        })
        
        return enhanced_metadata
    
    def _save_markdown_copy(self, file_path: str, content: str) -> Optional[str]:
        """Guarda una copia del documento en formato Markdown usando la configuración del servidor MCP"""
        try:
            # Obtener la configuración del servidor MCP
            current_dir = Path(__file__).parent.resolve()
            project_root = current_dir.parent.parent.resolve()
            mcp_data_dir = project_root / "mcp_server_organized" / "data" / "documents"
            
            # Crear directorio si no existe
            mcp_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre del archivo Markdown
            original_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(original_name)[0]
            md_filename = f"{name_without_ext}.md"
            md_filepath = mcp_data_dir / md_filename
            
            # Guardar archivo
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(md_filepath)
            
        except Exception as e:
            rag_core_wrapper.log(f"Error guardando copia Markdown: {e}")
            return None
    
    def store_documents(self, documents: List[DocumentPreview], 
                       progress_callback=None, log_callback=None) -> Dict[str, Any]:
        """
        Almacena documentos en la base de datos usando rag_core.py
        
        Args:
            documents: Lista de documentos a almacenar
            progress_callback: Función para reportar progreso
            log_callback: Función para reportar logs
            
        Returns:
            Diccionario con resultados del almacenamiento
        """
        if not documents:
            return {'status': 'no_documents', 'message': 'No hay documentos para almacenar'}
        
        try:
            if log_callback:
                log_callback("🚀 Iniciando almacenamiento en base de datos...")
            
            # Configurar base de datos vectorial usando rag_core
            if log_callback:
                log_callback("⚙️ Configurando base de datos vectorial...")
            
            vector_store = rag_core_wrapper.get_vector_store()
            
            if log_callback:
                log_callback("✅ Base de datos configurada")
            
            # Estadísticas de almacenamiento
            storage_stats = {
                'total_documents': len(documents),
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            # Procesar cada documento
            for i, document in enumerate(documents):
                if progress_callback:
                    progress_callback(i + 1, len(documents), document.original_name)
                
                try:
                    # Crear metadatos para almacenamiento
                    source_metadata = {
                        "source": document.original_name,
                        "file_path": document.file_path,
                        "file_type": document.file_type,
                        "processed_date": datetime.now().isoformat(),
                        "converted_to_md": "Yes" if hasattr(document.metadata, 'converted_to_md') else "No",
                        "size_bytes": document.metadata.size_bytes,
                        "word_count": document.metadata.word_count,
                        "processing_method": document.metadata.processing_method
                    }
                    
                    # Añadir información estructural si está disponible
                    if hasattr(document.metadata, 'structural_info'):
                        source_metadata['structural_info'] = document.metadata.structural_info
                    
                    # Usar rag_core para almacenar con chunking semántico
                    rag_core_wrapper.add_text_to_knowledge_base_enhanced(
                        document.markdown_content,
                        vector_store,
                        source_metadata,
                        use_semantic_chunking=True,
                        structural_elements=document.structural_elements
                    )
                    
                    storage_stats['successful'] += 1
                    
                    if log_callback:
                        log_callback(f"✅ {document.original_name} almacenado exitosamente")
                    
                except Exception as e:
                    storage_stats['failed'] += 1
                    error_msg = f"Error almacenando {document.original_name}: {str(e)}"
                    storage_stats['errors'].append(error_msg)
                    
                    if log_callback:
                        log_callback(f"❌ {error_msg}")
            
            # Resultado final
            if log_callback:
                log_callback(f"🎉 Almacenamiento completado: {storage_stats['successful']} exitosos, "
                           f"{storage_stats['failed']} fallidos")
            
            return {
                'status': 'completed',
                'stats': storage_stats,
                'message': f"Almacenamiento completado: {storage_stats['successful']} documentos"
            }
            
        except Exception as e:
            error_msg = f"Error general durante el almacenamiento: {str(e)}"
            if log_callback:
                log_callback(f"💥 {error_msg}")
            
            return {
                'status': 'error',
                'message': error_msg,
                'stats': storage_stats
            }
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache de embeddings usando rag_core"""
        try:
            return rag_core_wrapper.get_cache_stats()
        except Exception as e:
            return {'error': str(e)}
    
    def clear_cache(self):
        """Limpia el cache de embeddings usando rag_core"""
        try:
            rag_core_wrapper.clear_embedding_cache()
            return {'status': 'success', 'message': 'Cache limpiado exitosamente'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error limpiando cache: {str(e)}'}
    
    def validate_document(self, document: DocumentPreview) -> bool:
        """Valida un documento usando las reglas del servicio"""
        try:
            return document.validate()
        except Exception:
            return False
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesamiento"""
        return self.stats.copy()
    
    def stop_processing(self):
        """Detiene el procesamiento en curso"""
        self.stop_processing = True
    
    def reset_statistics(self):
        """Reinicia las estadísticas de procesamiento"""
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas avanzadas de la base de datos usando rag_core"""
        try:
            return rag_core_wrapper.get_vector_store_stats_advanced()
        except Exception as e:
            return {'error': str(e)} 