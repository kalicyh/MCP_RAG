"""
Bulk Ingest GUI 的配置服务
使用 MCP 服务器的配置管理应用配置
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

from gui_utils.constants import DEFAULT_WINDOW_SIZE, PERFORMANCE_LIMITS
from gui_utils.exceptions import ConfigurationLoadError, ConfigurationSaveError


class ConfigurationService:
    """
    用于管理应用配置的服务
    使用 MCP 服务器的配置以保持一致性
    """
    
    def __init__(self, config_file: str = None):
        # 如果可用，使用 MCP 服务器的配置
        try:
            # 配置 sys.path 以便从 MCP 服务器导入
            mcp_src_dir = project_root / "mcp_server_organized" / "src"
            if str(mcp_src_dir) not in sys.path:
                sys.path.insert(0, str(mcp_src_dir))
            
            from utils.config import Config
            # 配置文件路径设为 MCP 服务器目录下
            mcp_server_dir = project_root / "mcp_server_organized"
            self.config_file = str(mcp_server_dir / "bulk_ingest_config.json")
            print(f"✅ ConfigurationService: 使用 MCP 服务器配置: {self.config_file}")
        except ImportError as e:
            # 回退：使用本地配置
            if config_file is None:
                config_file = "bulk_ingest_config.json"
            self.config_file = config_file
            print(f"⚠️ ConfigurationService: 使用本地配置: {self.config_file}")
            print(f"   导入错误: {e}")
        
        self.config = self._get_default_config()
        self.load_configuration()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
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
        从文件加载配置
        
        返回：
            成功加载返回 True，使用默认配置返回 False
        """
        try:
            if not os.path.exists(self.config_file):
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # 合并加载的配置与默认配置
            self._merge_config(loaded_config)
            return True
            
        except Exception as e:
            raise ConfigurationLoadError(self.config_file, e)
    
    def save_configuration(self) -> bool:
        """
        保存当前配置到文件
        
        返回：
            成功保存返回 True
        """
        try:
            # 如果目录不存在则创建（使用 Path 更好管理）
            config_path = Path(self.config_file)
            config_dir = config_path.parent
            
            if config_dir and not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ ConfigurationService: 已创建目录: {config_dir}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise ConfigurationSaveError(self.config_file, e)
    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """合并加载的配置与默认配置"""
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
        使用点号分隔获取配置值
        
        参数：
            key: 例如 'section.subkey' 的键
            default: 未找到时的默认值
        返回：
            配置值
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
        使用点号分隔设置配置值
        
        参数：
            key: 例如 'section.subkey' 的键
            value: 要设置的值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取 UI 配置"""
        return self.config.get('ui', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.config.get('performance', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理配置"""
        return self.config.get('processing', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return self.config.get('storage', {})
    
    def add_recent_file(self, file_path: str):
        """将文件添加到最近文件列表"""
        recent_files = self.config.get('recent_files', [])
        
        # 如果已存在则移除
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到开头
        recent_files.insert(0, file_path)
        
        # 只保留最近 10 个
        self.config['recent_files'] = recent_files[:10]
    
    def get_recent_files(self) -> list:
        """获取最近文件列表"""
        return self.config.get('recent_files', [])
    
    def clear_recent_files(self):
        """清空最近文件列表"""
        self.config['recent_files'] = []
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = self._get_default_config()
    
    def export_config(self, file_path: str) -> bool:
        """
        导出配置到文件
        
        参数：
            file_path: 目标文件路径
        返回：
            成功导出返回 True
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise ConfigurationSaveError(file_path, e)
    
    def import_config(self, file_path: str) -> bool:
        """
        从文件导入配置
        
        参数：
            file_path: 源文件路径
        返回：
            成功导入返回 True
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
        校验配置是否正确
        
        返回：
            配置有效返回 True
        """
        try:
            # 检查必需的部分
            required_sections = ['ui', 'performance', 'processing', 'storage']
            for section in required_sections:
                if section not in self.config:
                    return False
            
            # 检查最小值
            if self.get('performance.max_preview_length', 0) < 1000:
                return False
            
            if self.get('performance.batch_size', 0) < 1:
                return False
            
            return True
            
        except Exception:
            return False