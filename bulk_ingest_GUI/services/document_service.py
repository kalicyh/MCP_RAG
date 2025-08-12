"""
文档服务用于 Bulk Ingest GUI
与 MCP 服务器的新模块化结构集成

此服务使用与 MCP 服务器相同的数据库，以保持 GUI 和服务器之间的数据一致性。
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
    用于处理文档的服务，与 rag_core.py 集成
    使用与 MCP 服务器相同的数据库以保持一致性
    """
    
    def __init__(self, config_service):
        self.config_service = config_service
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.stop_processing = False
        
        # 处理统计数据
        self.stats = {
            'total_processed': 0,  # 总处理数
            'successful': 0,       # 成功数
            'failed': 0,           # 失败数
            'skipped': 0,          # 跳过数
            'total_size': 0        # 总大小
        }
        
        # 验证 rag_core 是否可用
        try:
            rag_core_wrapper.get_rag_functions()
            print("✅ DocumentService: rag_core 配置成功")
        except ImportError as e:
            print(f"❌ DocumentService: 配置 rag_core 时出错: {e}")
            raise
    
    def process_directory(self, directory_path: str, save_markdown: bool = True, 
                         progress_callback=None, log_callback=None) -> List[DocumentPreview]:
        """
        处理目录中的所有文档
        
        参数：
            directory_path: 要处理的目录路径
            save_markdown: 是否保存为 Markdown 格式
            progress_callback: 用于报告进度的回调函数
            log_callback: 用于报告日志的回调函数
            
        返回：
            处理的文档列表
        """
        if not os.path.isdir(directory_path):
            raise DirectoryNotFoundError(directory_path)
        
        # 清空统计数据
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
        
        # 查找所有支持的文件
        files_to_process = self._find_supported_files(directory_path)
        
        if not files_to_process:
            if log_callback:
                log_callback("未在目录中找到支持的文件")
            return []
        
        if log_callback:
            log_callback(f"找到 {len(files_to_process)} 个文件待处理")
        
        # 处理文件
        processed_documents = []
        
        for i, file_path in enumerate(files_to_process):
            if self.stop_processing:
                if log_callback:
                    log_callback("用户停止了处理")
                break
            
            try:
                # 报告进度
                if progress_callback:
                    progress_callback(i + 1, len(files_to_process), os.path.basename(file_path))
                
                # 处理单个文档
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
                    log_callback(f"处理 {os.path.basename(file_path)} 时出错: {str(e)}")
        
        if log_callback:
            log_callback(f"处理完成: {self.stats['successful']} 成功, "
                        f"{self.stats['failed']} 失败, {self.stats['skipped']} 跳过")
        
        return processed_documents
    
    def _find_supported_files(self, directory_path: str) -> List[str]:
        """查找目录中所有支持的文件"""
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
        使用 rag_core.py 处理单个文件
        
        参数：
            file_path: 要处理的文件路径
            save_markdown: 是否保存为 Markdown 格式
            log_callback: 用于报告日志的回调函数
            
        返回：
            如果成功处理，返回 DocumentPreview；如果跳过，返回 None
        """
        try:
            if log_callback:
                log_callback(f"正在处理: {os.path.basename(file_path)}")
            
            # 使用 rag_core 加载带有结构化元素的文档
            markdown_content, metadata, structural_elements = rag_core_wrapper.load_document_with_elements(file_path)
            
            if not markdown_content or markdown_content.isspace():
                if log_callback:
                    log_callback(f"文档为空: {os.path.basename(file_path)}")
                return None
            
            # 创建增强的元数据
            enhanced_metadata = self._create_enhanced_metadata(file_path, metadata, markdown_content)
            
            # 如果需要，保存为 Markdown 格式
            if save_markdown:
                md_path = self._save_markdown_copy(file_path, markdown_content)
                if md_path:
                    enhanced_metadata['converted_to_md'] = md_path
            
            # 创建文档
            document = DocumentPreview(
                file_path=file_path,
                markdown_content=markdown_content,
                file_type=os.path.splitext(file_path)[1].lower(),
                original_name=os.path.basename(file_path),
                metadata=enhanced_metadata,
                structural_elements=structural_elements
            )
            
            # 验证文档
            document.validate()
            
            if log_callback:
                log_callback(f"✅ {os.path.basename(file_path)} 处理成功 ({len(markdown_content)} 字符)")
            
            return document
            
        except Exception as e:
            if log_callback:
                log_callback(f"❌ 处理 {os.path.basename(file_path)} 时出错: {str(e)}")
            raise FileProcessingError(file_path, e)
    
    def _create_enhanced_metadata(self, file_path: str, original_metadata: Dict[str, Any], 
                                content: str) -> Dict[str, Any]:
        """创建文档的增强元数据"""
        enhanced_metadata = original_metadata.copy() if original_metadata else {}
        
        # 添加额外信息
        enhanced_metadata.update({
            'file_path': file_path,  # 文件路径
            'original_name': os.path.basename(file_path),  # 原始文件名
            'file_type': os.path.splitext(file_path)[1].lower(),  # 文件类型
            'processed_date': datetime.now().isoformat(),  # 处理日期
            'size_bytes': len(content.encode('utf-8')),  # 文件大小（字节）
            'word_count': len(content.split()),  # 单词数
            'character_count': len(content),  # 字符数
            'processing_service': 'document_service_v2'  # 处理服务名称
        })
        
        return enhanced_metadata
    
    def _save_markdown_copy(self, file_path: str, content: str) -> Optional[str]:
        """使用 MCP 服务器配置保存文档的 Markdown 副本"""
        try:
            # 获取 MCP 服务器的配置
            current_dir = Path(__file__).parent.resolve()
            project_root = current_dir.parent.parent.resolve()
            mcp_data_dir = project_root / "mcp_server_organized" / "data" / "documents"
            
            # 如果目录不存在，则创建
            mcp_data_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成 Markdown 文件名
            original_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(original_name)[0]
            md_filename = f"{name_without_ext}.md"
            md_filepath = mcp_data_dir / md_filename
            
            # 保存文件
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(md_filepath)
            
        except Exception as e:
            rag_core_wrapper.log(f"保存 Markdown 副本时出错: {e}")
            return None
    
    def store_documents(self, documents: List[DocumentPreview], 
                       progress_callback=None, log_callback=None) -> Dict[str, Any]:
        """存储文档到数据库中，使用 rag_core.py"""
        if not documents:
            return {'status': 'no_documents', 'message': '没有文档可存储'}
        
        try:
            if log_callback:
                log_callback("🚀 开始将文档存储到数据库...")
            
            # 配置向量数据库，使用 rag_core
            if log_callback:
                log_callback("⚙️ 正在配置向量数据库...")
            
            vector_store = rag_core_wrapper.get_vector_store()
            
            if log_callback:
                log_callback("✅ 向量数据库配置成功")
            
            # 存储统计数据
            storage_stats = {
                'total_documents': len(documents),
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            # 处理每个文档
            for i, document in enumerate(documents):
                if progress_callback:
                    progress_callback(i + 1, len(documents), document.original_name)
                
                try:
                    # 创建存储元数据
                    source_metadata = {
                        "source": document.original_name,  # 来源文件名
                        "file_path": document.file_path,  # 文件路径
                        "file_type": document.file_type,  # 文件类型
                        "processed_date": datetime.now().isoformat(),  # 处理日期
                        "converted_to_md": "是" if hasattr(document.metadata, 'converted_to_md') else "否",  # 是否转换为 Markdown
                        "size_bytes": document.metadata.size_bytes,  # 文件大小
                        "word_count": document.metadata.word_count,  # 单词数
                        "processing_method": document.metadata.processing_method  # 处理方法
                    }
                    
                    # 如果有结构化信息，添加到元数据中
                    if hasattr(document.metadata, 'structural_info'):
                        source_metadata['structural_info'] = document.metadata.structural_info
                    
                    # 使用 rag_core 进行语义分块存储
                    rag_core_wrapper.add_text_to_knowledge_base_enhanced(
                        document.markdown_content,
                        vector_store,
                        source_metadata,
                        use_semantic_chunking=True,
                        structural_elements=document.structural_elements
                    )
                    
                    storage_stats['successful'] += 1
                    
                    if log_callback:
                        log_callback(f"✅ {document.original_name} 成功存储")
                    
                except Exception as e:
                    storage_stats['failed'] += 1
                    error_msg = f"存储 {document.original_name} 时出错: {str(e)}"
                    storage_stats['errors'].append(error_msg)
                    
                    if log_callback:
                        log_callback(f"❌ {error_msg}")
            
            # 最终结果
            if log_callback:
                log_callback(f"🎉 存储完成: {storage_stats['successful']} 成功, "
                           f"{storage_stats['failed']} 失败")
            
            return {
                'status': 'completed',
                'stats': storage_stats,
                'message': f"存储完成: {storage_stats['successful']} 个文档"
            }
            
        except Exception as e:
            error_msg = f"存储过程中发生一般性错误: {str(e)}"
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
        """Reinicia las统计数据处理"""
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