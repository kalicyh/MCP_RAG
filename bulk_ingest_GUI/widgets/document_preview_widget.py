"""
用于预览文档的控件
显示文档内容，支持格式化和滚动
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
import sys
import os
from pathlib import Path

# 配置sys.path用于绝对导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from models.document_model import DocumentPreview

class DocumentPreviewWidget:
    """
    用于预览文档内容的控件
    """
    
    def __init__(self, parent, max_preview_length: int = 2000):
        self.parent = parent
        self.max_preview_length = max_preview_length
        self.current_document: Optional[DocumentPreview] = None
        
        # 创建控件
        self._create_widgets()
    
    def _create_widgets(self):
        """创建预览控件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="文档预览")
        
        # 顶部框架，显示文档信息
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文档信息
        self.doc_info_label = ttk.Label(info_frame, text="未选择任何文档")
        self.doc_info_label.pack(side=tk.LEFT)
        
        # 复制内容按钮
        self.copy_button = ttk.Button(info_frame, text="复制", command=self._copy_content)
        self.copy_button.pack(side=tk.RIGHT)
        self.copy_button.config(state=tk.DISABLED)
        
        # 分隔符
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        # 带滚动条的文本区域
        self.text_area = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            state=tk.DISABLED,
            font=("Consolas", 10),
            bg="#0D1117",  # 深色背景
            fg="#56F175"   # 绿色文字
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 底部框架，显示统计信息
        stats_frame = ttk.Frame(self.frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack(side=tk.LEFT)
    
    def show_document(self, document: DocumentPreview):
        """在预览中显示文档"""
        self.current_document = document
        
        # 更新文档信息
        info_text = f"📄 {document.original_name} ({document.file_type})"
        if hasattr(document.metadata, 'size_bytes'):
            size_mb = document.metadata.size_bytes / (1024 * 1024)
            info_text += f" - {size_mb:.2f} MB"
        self.doc_info_label.config(text=info_text)
        
        # 显示内容
        content = document.markdown_content
        
        # 如果内容过长，进行截断
        if len(content) > self.max_preview_length:
            content = content[:self.max_preview_length] + "\n\n[... 内容已截断 ...]"
        
        # 更新文本区域
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, content)
        self.text_area.config(state=tk.DISABLED)
        
        # 更新统计信息
        stats_text = f"📊 字符数: {len(document.markdown_content):,}"
        if hasattr(document.metadata, 'word_count'):
            stats_text += f" | 单词数: {document.metadata.word_count:,}"
        if hasattr(document.metadata, 'processing_method'):
            stats_text += f" | 方法: {document.metadata.processing_method}"
        self.stats_label.config(text=stats_text)
        
        # 启用复制按钮
        self.copy_button.config(state=tk.NORMAL)
    
    def clear_preview(self):
        """清空预览"""
        self.current_document = None
        self.doc_info_label.config(text="未选择任何文档")
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.stats_label.config(text="")
        self.copy_button.config(state=tk.DISABLED)
    
    def _copy_content(self):
        """将内容复制到剪贴板"""
        if self.current_document:
            content = self.current_document.markdown_content
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            
            # 显示临时消息
            original_text = self.copy_button.cget("text")
            self.copy_button.config(text="已复制！")
            self.parent.after(2000, lambda: self.copy_button.config(text=original_text))
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """取消打包控件"""
        self.frame.pack_forget()