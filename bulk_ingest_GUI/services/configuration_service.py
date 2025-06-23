"""
Servicio de configuración para Bulk Ingest GUI
Gestiona la configuración de la aplicación
"""

import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

import json
from typing import Dict, Any, Optional

from utils.constants import CONFIG_FILE, DEFAULT_WINDOW_SIZE, PERFORMANCE_LIMITS
from utils.exceptions import ConfigurationLoadError, ConfigurationSaveError


class ConfigurationService:
    """
    Servicio para gestionar la configuración de la aplicación
    """
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self._get_default_config()
        self.load_configuration()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto"""
        return {
            'ui': {
                'window_size': DEFAULT_WINDOW_SIZE,
                'save_markdown': True,
                'last_directory': '',
                'theme': 'terminal_refined'
            },
            'performance': {
                'max_preview_length': PERFORMANCE_LIMITS['max_preview_length'],
                'batch_size': PERFORMANCE_LIMITS['batch_size'],
                'memory_limit': PERFORMANCE_LIMITS['memory_limit'],
                'max_log_lines': PERFORMANCE_LIMITS['max_log_lines'],
                'update_interval': PERFORMANCE_LIMITS['update_interval']
            },
            'processing': {
                'semantic_chunking': True,
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'save_converted_files': True
            },
            'storage': {
                'confirm_required': True,
                'batch_processing': True,
                'progress_update_interval': 0.5
            },
            'recent_files': [],
            'version': '2.0'
        }
    
    def load_configuration(self) -> bool:
        """
        Cargar configuración desde archivo
        
        Returns:
            True si se cargó exitosamente, False si se usó configuración por defecto
        """
        try:
            if not os.path.exists(self.config_file):
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Fusionar configuración cargada con la por defecto
            self._merge_config(loaded_config)
            return True
            
        except Exception as e:
            raise ConfigurationLoadError(self.config_file, e)
    
    def save_configuration(self) -> bool:
        """
        Guardar configuración actual
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise ConfigurationSaveError(self.config_file, e)
    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """Fusionar configuración cargada con la por defecto"""
        for section, values in loaded_config.items():
            if section in self.config:
                if isinstance(values, dict) and isinstance(self.config[section], dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración usando notación de puntos
        
        Args:
            key: Clave en formato 'seccion.subclave'
            default: Valor por defecto si no se encuentra
            
        Returns:
            Valor de configuración
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Establecer valor de configuración usando notación de puntos
        
        Args:
            key: Clave en formato 'seccion.subclave'
            value: Valor a establecer
        """
        keys = key.split('.')
        config = self.config
        
        # Navegar hasta la sección padre
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Establecer el valor
        config[keys[-1]] = value
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Obtener configuración de UI"""
        return self.config.get('ui', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Obtener configuración de rendimiento"""
        return self.config.get('performance', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Obtener configuración de procesamiento"""
        return self.config.get('processing', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Obtener configuración de almacenamiento"""
        return self.config.get('storage', {})
    
    def add_recent_file(self, file_path: str):
        """Añadir archivo a la lista de recientes"""
        recent_files = self.config.get('recent_files', [])
        
        # Remover si ya existe
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Añadir al inicio
        recent_files.insert(0, file_path)
        
        # Mantener solo los últimos 10
        self.config['recent_files'] = recent_files[:10]
    
    def get_recent_files(self) -> list:
        """Obtener lista de archivos recientes"""
        return self.config.get('recent_files', [])
    
    def clear_recent_files(self):
        """Limpiar lista de archivos recientes"""
        self.config['recent_files'] = []
    
    def reset_to_defaults(self):
        """Restablecer configuración por defecto"""
        self.config = self._get_default_config()
    
    def export_config(self, file_path: str) -> bool:
        """
        Exportar configuración a archivo
        
        Args:
            file_path: Ruta del archivo de destino
            
        Returns:
            True si se exportó exitosamente
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise ConfigurationSaveError(file_path, e)
    
    def import_config(self, file_path: str) -> bool:
        """
        Importar configuración desde archivo
        
        Args:
            file_path: Ruta del archivo de origen
            
        Returns:
            True si se importó exitosamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            self._merge_config(imported_config)
            return True
            
        except Exception as e:
            raise ConfigurationLoadError(file_path, e)
    
    def validate_config(self) -> bool:
        """
        Validar que la configuración es correcta
        
        Returns:
            True si la configuración es válida
        """
        try:
            # Verificar secciones requeridas
            required_sections = ['ui', 'performance', 'processing', 'storage']
            for section in required_sections:
                if section not in self.config:
                    return False
            
            # Verificar valores mínimos
            if self.get('performance.max_preview_length', 0) < 1000:
                return False
            
            if self.get('performance.batch_size', 0) < 1:
                return False
            
            return True
            
        except Exception:
            return False 