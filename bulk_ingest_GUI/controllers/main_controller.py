"""
Controlador principal para Bulk Ingest GUI
Coordina todos los componentes de la aplicación
"""

import tkinter as tk
from typing import List, Dict, Any, Optional
import threading
import queue
import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from services.configuration_service import ConfigurationService
from models.document_model import DocumentPreview
from gui_utils.constants import MESSAGES
from gui_utils.exceptions import BulkIngestError


class MainController:
    """
    Controlador principal que coordina todos los componentes de la aplicación
    """
    
    def __init__(self, root: tk.Tk, config_service: ConfigurationService):
        self.root = root
        self.config_service = config_service
        
        # Importar DocumentService de forma diferida para evitar importación circular
        from services.document_service import DocumentService
        self.document_service = DocumentService(config_service)
        
        # Estado de la aplicación
        self.processing_running = False
        self.storage_running = False
        self.stop_requested = False
        
        # Documentos procesados
        self.processed_documents: List[DocumentPreview] = []
        
        # Colas para comunicación entre hilos
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.storage_log_queue = queue.Queue()
        
        # Callbacks para la interfaz
        self.ui_callbacks = {
            'update_progress': None,
            'update_logs': None,
            'update_storage_logs': None,
            'update_status': None,
            'update_documents_list': None,
            'update_summary': None,
            'enable_processing_buttons': None,
            'disable_processing_buttons': None,
            'enable_storage_buttons': None,
            'disable_storage_buttons': None,
            'show_message': None,
            'update_storage_progress': None,
            'update_processing_stats': None
        }
        
        # Iniciar procesamiento de colas
        self._start_queue_processors()
    
    def set_ui_callbacks(self, callbacks: Dict[str, callable]):
        """Establece los callbacks de la interfaz de usuario"""
        self.ui_callbacks.update(callbacks)
    
    def _start_queue_processors(self):
        """Inicia los procesadores de colas para comunicación con la UI"""
        self.root.after(100, self._process_log_queue)
        self.root.after(100, self._process_progress_queue)
        self.root.after(100, self._process_storage_log_queue)
    
    def _process_log_queue(self):
        """Procesa la cola de logs"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                if self.ui_callbacks['update_logs']:
                    self.ui_callbacks['update_logs'](message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_log_queue)
    
    def _process_progress_queue(self):
        """Procesa la cola de progreso"""
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                if self.ui_callbacks['update_progress']:
                    self.ui_callbacks['update_progress'](**progress_data)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_progress_queue)
    
    def _process_storage_log_queue(self):
        """Procesa la cola de logs de almacenamiento"""
        try:
            while True:
                message = self.storage_log_queue.get_nowait()
                if self.ui_callbacks['update_storage_logs']:
                    self.ui_callbacks['update_storage_logs'](message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_storage_log_queue)
    
    def log_message(self, message: str):
        """Envía un mensaje a la cola de logs"""
        self.log_queue.put(message)
    
    def log_storage_message(self, message: str):
        """Envía un mensaje a la cola de logs de almacenamiento"""
        self.storage_log_queue.put(message)
    
    def update_progress(self, current: int, total: int, current_file: str = ""):
        """Envía información de progreso a la cola"""
        self.progress_queue.put({
            'current': current,
            'total': total,
            'current_file': current_file
        })
    
    def start_processing(self, directory_path: str, save_markdown: bool = True) -> bool:
        """
        Inicia el procesamiento de documentos
        
        Args:
            directory_path: Ruta del directorio a procesar
            save_markdown: Si guardar copias en Markdown
            
        Returns:
            True si se inició correctamente
        """
        if self.processing_running:
            self.log_message("⚠️ El procesamiento ya está en curso")
            return False
        
        try:
            # Validar directorio
            if not directory_path or not directory_path.strip():
                self.log_message("❌ No se ha seleccionado un directorio")
                return False
            
            # Limpiar documentos anteriores
            self.processed_documents.clear()
            
            # Cambiar estado
            self.processing_running = True
            self.stop_requested = False
            
            # Deshabilitar botones de procesamiento
            if self.ui_callbacks['disable_processing_buttons']:
                self.ui_callbacks['disable_processing_buttons']()
            
            # Actualizar estado
            if self.ui_callbacks['update_status']:
                self.ui_callbacks['update_status']("Iniciando procesamiento...")
            
            # Iniciar procesamiento en hilo separado
            processing_thread = threading.Thread(
                target=self._process_directory_thread,
                args=(directory_path, save_markdown),
                daemon=True
            )
            processing_thread.start()
            
            self.log_message("🚀 Procesamiento iniciado")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error iniciando procesamiento: {str(e)}")
            self.processing_running = False
            return False
    
    def _process_directory_thread(self, directory_path: str, save_markdown: bool):
        """Hilo para procesar directorio"""
        try:
            # Callbacks para el servicio
            def progress_callback(current, total, current_file):
                self.update_progress(current, total, current_file)
            
            def log_callback(message):
                self.log_message(message)
            
            # Procesar directorio
            documents = self.document_service.process_directory(
                directory_path=directory_path,
                save_markdown=save_markdown,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            # Guardar documentos procesados
            self.processed_documents = documents
            
            # Actualizar interfaz en el hilo principal
            self.root.after(0, self._finish_processing)
            
        except Exception as e:
            self.log_message(f"❌ Error durante el procesamiento: {str(e)}")
            self.root.after(0, self._finish_processing)
    
    def _finish_processing(self):
        """Finaliza el procesamiento y actualiza la interfaz"""
        self.processing_running = False
        self.stop_requested = False
        
        # Habilitar botones de procesamiento
        if self.ui_callbacks['enable_processing_buttons']:
            self.ui_callbacks['enable_processing_buttons']()
        
        # Actualizar estado
        if self.ui_callbacks['update_status']:
            self.ui_callbacks['update_status']("Procesamiento completado")
        
        # Actualizar lista de documentos
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        
        # Actualizar resumen
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
        
        # Mostrar mensaje de finalización
        if self.ui_callbacks['show_message']:
            stats = self.document_service.get_processing_statistics()
            message = f"Procesamiento completado:\n" \
                     f"✅ {stats['successful']} exitosos\n" \
                     f"❌ {stats['failed']} fallidos\n" \
                     f"⏭️ {stats['skipped']} omitidos"
            self.ui_callbacks['show_message']("Procesamiento Completado", message, "info")
        
        # Actualizar estadísticas de procesamiento en el widget de estadísticas si existe el callback
        if hasattr(self, 'ui_callbacks') and 'update_processing_stats' in self.ui_callbacks:
            try:
                self.ui_callbacks['update_processing_stats']()
            except Exception as e:
                print(f"Error actualizando estadísticas automáticamente: {e}")
    
    def stop_processing(self):
        """Detiene el procesamiento en curso"""
        if not self.processing_running:
            return
        
        self.stop_requested = True
        self.document_service.stop_processing()
        self.log_message("⏹️ Deteniendo procesamiento...")
    
    def start_storage(self, selected_documents: List[DocumentPreview]) -> bool:
        """
        Inicia el almacenamiento de documentos
        
        Args:
            selected_documents: Lista de documentos seleccionados para almacenar
            
        Returns:
            True si se inició correctamente
        """
        if self.storage_running:
            self.log_storage_message("⚠️ El almacenamiento ya está en curso")
            return False
        
        if not selected_documents:
            self.log_storage_message("❌ No hay documentos seleccionados para almacenar")
            return False
        
        try:
            # Cambiar estado
            self.storage_running = True
            
            # Deshabilitar botones de almacenamiento
            if self.ui_callbacks['disable_storage_buttons']:
                self.ui_callbacks['disable_storage_buttons']()
            
            # Actualizar estado
            if self.ui_callbacks['update_status']:
                self.ui_callbacks['update_status']("Iniciando almacenamiento...")
            
            # Iniciar almacenamiento en hilo separado
            storage_thread = threading.Thread(
                target=self._store_documents_thread,
                args=(selected_documents,),
                daemon=True
            )
            storage_thread.start()
            
            self.log_storage_message("🚀 Almacenamiento iniciado")
            return True
            
        except Exception as e:
            self.log_storage_message(f"❌ Error iniciando almacenamiento: {str(e)}")
            self.storage_running = False
            return False
    
    def _store_documents_thread(self, selected_documents: List[DocumentPreview]):
        """Hilo para almacenar documentos"""
        try:
            # Callbacks para el servicio
            def progress_callback(current, total, current_file):
                if self.ui_callbacks.get('update_storage_progress'):
                    self.ui_callbacks['update_storage_progress'](current, total, current_file)
            
            def log_callback(message):
                self.log_storage_message(message)
            
            # Almacenar documentos
            result = self.document_service.store_documents(
                documents=selected_documents,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            # Actualizar interfaz en el hilo principal
            self.root.after(0, lambda: self._finish_storage(result))
            
        except Exception as e:
            self.log_storage_message(f"❌ Error durante el almacenamiento: {str(e)}")
            self.root.after(0, lambda: self._finish_storage({
                'status': 'error',
                'message': str(e)
            }))
    
    def _finish_storage(self, result: Dict[str, Any]):
        """Finaliza el almacenamiento y actualiza la interfaz"""
        self.storage_running = False
        
        # Habilitar botones de almacenamiento
        if self.ui_callbacks['enable_storage_buttons']:
            self.ui_callbacks['enable_storage_buttons']()
        
        # Actualizar estado
        if self.ui_callbacks['update_status']:
            if result['status'] == 'completed':
                self.ui_callbacks['update_status']("Almacenamiento completado")
            else:
                self.ui_callbacks['update_status']("Error en almacenamiento")
        
        # Mostrar mensaje de finalización
        if self.ui_callbacks['show_message']:
            if result['status'] == 'completed':
                stats = result.get('stats', {})
                message = f"Almacenamiento completado:\n" \
                         f"✅ {stats.get('successful', 0)} exitosos\n" \
                         f"❌ {stats.get('failed', 0)} fallidos"
                self.ui_callbacks['show_message']("Almacenamiento Completado", message, "info")
            else:
                self.ui_callbacks['show_message']("Error de Almacenamiento", result['message'], "error")
    
    def stop_storage(self):
        """Detiene el almacenamiento en curso"""
        if not self.storage_running:
            return
        
        self.storage_running = False
        self.log_storage_message("⏹️ Deteniendo almacenamiento...")
    
    def get_processed_documents(self) -> List[DocumentPreview]:
        """Obtiene la lista de documentos procesados"""
        return self.processed_documents.copy()
    
    def get_selected_documents(self) -> List[DocumentPreview]:
        """Obtiene la lista de documentos seleccionados"""
        return [doc for doc in self.processed_documents if doc.selected.get()]
    
    def select_all_documents(self):
        """Selecciona todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(True)
        
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
    
    def deselect_all_documents(self):
        """Deselecciona todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(False)
        
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
    
    def filter_documents(self, search_text: str = "", file_type_filter: str = "Todos") -> List[DocumentPreview]:
        """Filtra documentos según criterios"""
        filtered = []
        
        for doc in self.processed_documents:
            # Filtro por texto de búsqueda
            if search_text and search_text.lower() not in doc.original_name.lower():
                continue
            
            # Filtro por tipo de archivo
            if file_type_filter != "Todos" and doc.file_type != file_type_filter:
                continue
            
            filtered.append(doc)
        
        return filtered
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesamiento"""
        return self.document_service.get_processing_statistics()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        return self.document_service.get_cache_statistics()
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        return self.document_service.get_database_statistics()
    
    def clear_cache(self) -> Dict[str, Any]:
        """Limpia el cache de embeddings"""
        result = self.document_service.clear_cache()
        
        if result['status'] == 'success':
            self.log_message("✅ Cache limpiado exitosamente")
        else:
            self.log_message(f"❌ Error limpiando cache: {result['message']}")
        
        return result
    
    def export_documents(self, documents: List[DocumentPreview], file_path: str) -> bool:
        """Exporta documentos a archivo JSON"""
        try:
            import json
            
            export_data = []
            for doc in documents:
                export_data.append(doc.to_dict())
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log_message(f"✅ Documentos exportados a {file_path}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error exportando documentos: {str(e)}")
            return False
    
    def import_documents(self, file_path: str) -> bool:
        """Importa documentos desde archivo JSON"""
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_documents = []
            for item in import_data:
                try:
                    doc = DocumentPreview.from_dict(item)
                    imported_documents.append(doc)
                except Exception as e:
                    self.log_message(f"⚠️ Error importando documento: {str(e)}")
            
            # Añadir a la lista existente
            self.processed_documents.extend(imported_documents)
            
            # Actualizar interfaz
            if self.ui_callbacks['update_documents_list']:
                self.ui_callbacks['update_documents_list']()
            
            if self.ui_callbacks['update_summary']:
                self.ui_callbacks['update_summary']()
            
            self.log_message(f"✅ {len(imported_documents)} documentos importados")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error importando documentos: {str(e)}")
            return False
    
    def cleanup(self):
        """Limpia recursos del controlador"""
        self.stop_processing()
        self.stop_storage()
        
        # Limpiar documentos
        self.processed_documents.clear()
        
        # Limpiar colas
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.storage_log_queue.empty():
            try:
                self.storage_log_queue.get_nowait()
            except queue.Empty:
                break 