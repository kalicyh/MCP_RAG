"""
批量导入 GUI 主控制器
协调应用的所有组件
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
    主控制器，协调应用所有组件
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
        """设置 UI 回调函数"""
        self.ui_callbacks.update(callbacks)
    
    def _start_queue_processors(self):
        """启动队列处理器，用于与 UI 通信"""
        self.root.after(100, self._process_log_queue)
        self.root.after(100, self._process_progress_queue)
        self.root.after(100, self._process_storage_log_queue)
    
    def _process_log_queue(self):
        """处理日志队列"""
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
        """处理进度队列"""
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
        """处理存储日志队列"""
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
        """发送日志消息到队列"""
        self.log_queue.put(message)
    
    def log_storage_message(self, message: str):
        """发送存储日志消息到队列"""
        self.storage_log_queue.put(message)
    
    def update_progress(self, current: int, total: int, current_file: str = ""):
        """发送进度信息到队列"""
        self.progress_queue.put({
            'current': current,
            'total': total,
            'current_file': current_file
        })
    
    def start_processing(self, directory_path: str, save_markdown: bool = True) -> bool:
        """
        开始处理文档
        
        参数：
            directory_path: 要处理的目录路径
            save_markdown: 是否保存为 Markdown
        返回：
            成功启动返回 True
        """
        if self.processing_running:
            self.log_message("⚠️ 处理已在进行中")
            return False
        try:
            # 校验目录
            if not directory_path or not directory_path.strip():
                self.log_message("❌ 未选择目录")
                return False
            # 清空之前的文档
            self.processed_documents.clear()
            # 状态切换
            self.processing_running = True
            self.stop_requested = False
            # 禁用处理按钮
            if self.ui_callbacks['disable_processing_buttons']:
                self.ui_callbacks['disable_processing_buttons']()
            # 更新状态
            if self.ui_callbacks['update_status']:
                self.ui_callbacks['update_status']("正在开始处理...")
            # 启动线程处理
            processing_thread = threading.Thread(
                target=self._process_directory_thread,
                args=(directory_path, save_markdown),
                daemon=True
            )
            processing_thread.start()
            self.log_message("🚀 处理已启动")
            return True
        except Exception as e:
            self.log_message(f"❌ 启动处理时出错: {str(e)}")
            self.processing_running = False
            return False
    
    def _process_directory_thread(self, directory_path: str, save_markdown: bool):
        """处理目录的线程"""
        try:
            # 服务回调
            def progress_callback(current, total, current_file):
                self.update_progress(current, total, current_file)
            def log_callback(message):
                self.log_message(message)
            # 处理目录
            documents = self.document_service.process_directory(
                directory_path=directory_path,
                save_markdown=save_markdown,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            # 保存处理结果
            self.processed_documents = documents
            # 主线程更新界面
            self.root.after(0, self._finish_processing)
        except Exception as e:
            self.log_message(f"❌ 处理过程中出错: {str(e)}")
            self.root.after(0, self._finish_processing)
    
    def _finish_processing(self):
        """处理结束，更新界面"""
        self.processing_running = False
        self.stop_requested = False
        # 启用处理按钮
        if self.ui_callbacks['enable_processing_buttons']:
            self.ui_callbacks['enable_processing_buttons']()
        # 更新状态
        if self.ui_callbacks['update_status']:
            self.ui_callbacks['update_status']("处理完成")
        # 更新文档列表
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        # 更新摘要
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
        # 显示完成消息
        if self.ui_callbacks['show_message']:
            stats = self.document_service.get_processing_statistics()
            message = f"处理完成:\n" \
                     f"✅ {stats['successful']} 成功\n" \
                     f"❌ {stats['failed']} 失败\n" \
                     f"⏭️ {stats['skipped']} 跳过"
            self.ui_callbacks['show_message']("处理完成", message, "info")
        # 如果有统计回调，自动更新
        if hasattr(self, 'ui_callbacks') and 'update_processing_stats' in self.ui_callbacks:
            try:
                self.ui_callbacks['update_processing_stats']()
            except Exception as e:
                print(f"自动更新统计时出错: {e}")
    
    def stop_processing(self):
        """停止正在进行的处理"""
        if not self.processing_running:
            return
        self.stop_requested = True
        self.document_service.stop_processing()
        self.log_message("⏹️ 正在停止处理...")
    
    def start_storage(self, selected_documents: List[DocumentPreview]) -> bool:
        """
        开始存储文档
        
        参数：
            selected_documents: 选中的文档列表
        返回：
            成功启动返回 True
        """
        if self.storage_running:
            self.log_storage_message("⚠️ 存储已在进行中")
            return False
        if not selected_documents:
            self.log_storage_message("❌ 没有选中的文档可存储")
            return False
        try:
            # 状态切换
            self.storage_running = True
            # 禁用存储按钮
            if self.ui_callbacks['disable_storage_buttons']:
                self.ui_callbacks['disable_storage_buttons']()
            # 更新状态
            if self.ui_callbacks['update_status']:
                self.ui_callbacks['update_status']("正在开始存储...")
            # 启动线程存储
            storage_thread = threading.Thread(
                target=self._store_documents_thread,
                args=(selected_documents,),
                daemon=True
            )
            storage_thread.start()
            self.log_storage_message("🚀 存储已启动")
            return True
        except Exception as e:
            self.log_storage_message(f"❌ 启动存储时出错: {str(e)}")
            self.storage_running = False
            return False
    
    def _store_documents_thread(self, selected_documents: List[DocumentPreview]):
        """存储文档的线程"""
        try:
            # 服务回调
            def progress_callback(current, total, current_file):
                if self.ui_callbacks.get('update_storage_progress'):
                    self.ui_callbacks['update_storage_progress'](current, total, current_file)
            def log_callback(message):
                self.log_storage_message(message)
            # 存储文档
            result = self.document_service.store_documents(
                documents=selected_documents,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            # 主线程更新界面
            self.root.after(0, lambda: self._finish_storage(result))
        except Exception as e:
            self.log_storage_message(f"❌ 存储过程中出错: {str(e)}")
            self.root.after(0, lambda: self._finish_storage({
                'status': 'error',
                'message': str(e)
            }))
    
    def _finish_storage(self, result: Dict[str, Any]):
        """存储结束，更新界面"""
        self.storage_running = False
        # 启用存储按钮
        if self.ui_callbacks['enable_storage_buttons']:
            self.ui_callbacks['enable_storage_buttons']()
        # 更新状态
        if self.ui_callbacks['update_status']:
            if result['status'] == 'completed':
                self.ui_callbacks['update_status']("存储完成")
            else:
                self.ui_callbacks['update_status']("存储出错")
        # 显示完成消息
        if self.ui_callbacks['show_message']:
            if result['status'] == 'completed':
                stats = result.get('stats', {})
                message = f"存储完成:\n" \
                         f"✅ {stats.get('successful', 0)} 成功\n" \
                         f"❌ {stats.get('failed', 0)} 失败"
                self.ui_callbacks['show_message']("存储完成", message, "info")
            else:
                self.ui_callbacks['show_message']("存储出错", result['message'], "error")
    
    def stop_storage(self):
        """停止正在进行的存储"""
        if not self.storage_running:
            return
        self.storage_running = False
        self.log_storage_message("⏹️ 正在停止存储...")
    
    def get_processed_documents(self) -> List[DocumentPreview]:
        """获取已处理文档列表"""
        return self.processed_documents.copy()
    
    def get_selected_documents(self) -> List[DocumentPreview]:
        """获取已选中文档列表"""
        return [doc for doc in self.processed_documents if doc.selected.get()]
    
    def select_all_documents(self):
        """全选所有文档"""
        for doc in self.processed_documents:
            doc.selected.set(True)
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
    
    def deselect_all_documents(self):
        """取消全选所有文档"""
        for doc in self.processed_documents:
            doc.selected.set(False)
        if self.ui_callbacks['update_documents_list']:
            self.ui_callbacks['update_documents_list']()
        if self.ui_callbacks['update_summary']:
            self.ui_callbacks['update_summary']()
    
    def filter_documents(self, search_text: str = "", file_type_filter: str = "全部") -> List[DocumentPreview]:
        """根据条件过滤文档"""
        filtered = []
        for doc in self.processed_documents:
            # 按搜索文本过滤
            if search_text and search_text.lower() not in doc.original_name.lower():
                continue
            # 按文件类型过滤
            if file_type_filter != "全部" and doc.file_type != file_type_filter:
                continue
            filtered.append(doc)
        return filtered
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.document_service.get_processing_statistics()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self.document_service.get_cache_statistics()
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        return self.document_service.get_database_statistics()
    
    def clear_cache(self) -> Dict[str, Any]:
        """清空嵌入缓存"""
        result = self.document_service.clear_cache()
        if result['status'] == 'success':
            self.log_message("✅ 缓存清理成功")
        else:
            self.log_message(f"❌ 清理缓存时出错: {result['message']}")
        return result
    
    def export_documents(self, documents: List[DocumentPreview], file_path: str) -> bool:
        """导出文档到 JSON 文件"""
        try:
            import json
            export_data = []
            for doc in documents:
                export_data.append(doc.to_dict())
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            self.log_message(f"✅ 文档已导出到 {file_path}")
            return True
        except Exception as e:
            self.log_message(f"❌ 导出文档时出错: {str(e)}")
            return False
    
    def import_documents(self, file_path: str) -> bool:
        """从 JSON 文件导入文档"""
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
                    self.log_message(f"⚠️ 导入文档时出错: {str(e)}")
            # 添加到现有列表
            self.processed_documents.extend(imported_documents)
            # 更新界面
            if self.ui_callbacks['update_documents_list']:
                self.ui_callbacks['update_documents_list']()
            if self.ui_callbacks['update_summary']:
                self.ui_callbacks['update_summary']()
            self.log_message(f"✅ 成功导入 {len(imported_documents)} 个文档")
            return True
        except Exception as e:
            self.log_message(f"❌ 导入文档时出错: {str(e)}")
            return False
    
    def cleanup(self):
        """清理控制器资源"""
        self.stop_processing()
        self.stop_storage()
        # 清空文档
        self.processed_documents.clear()
        # 清空队列
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
    
    def optimize_database(self) -> Dict[str, Any]:
        print(">>> [控制器] 调用 optimize_database")
        try:
            import bulk_ingest_GUI.rag_core_wrapper as rag_core_wrapper
            result = rag_core_wrapper.optimize_vector_store()
            print(f">>> [控制器] optimize_vector_store 结果: {result}")
            return result
        except Exception as e:
            print(f">>> [控制器] optimize_database 出错: {e}")
            return {"status": "error", "message": f"优化数据库时出错: {str(e)}"}