"""
Widget para previsualizar documentos
Muestra el contenido de un documento con formato y scroll
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from models.document_model import DocumentPreview

class DocumentPreviewWidget:
    """
    Widget para previsualizar el contenido de un documento
    """
    
    def __init__(self, parent, max_preview_length: int = 2000):
        self.parent = parent
        self.max_preview_length = max_preview_length
        self.current_document: Optional[DocumentPreview] = None
        
        # Crear widgets
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del preview"""
        # Frame principal
        self.frame = ttk.LabelFrame(self.parent, text="Vista previa del documento")
        
        # Frame superior con información del documento
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Información del documento
        self.doc_info_label = ttk.Label(info_frame, text="Ningún documento seleccionado")
        self.doc_info_label.pack(side=tk.LEFT)
        
        # Botón para copiar contenido
        self.copy_button = ttk.Button(info_frame, text="Copiar", command=self._copy_content)
        self.copy_button.pack(side=tk.RIGHT)
        self.copy_button.config(state=tk.DISABLED)
        
        # Separador
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        # Área de texto con scroll
        self.text_area = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            state=tk.DISABLED,
            font=("Consolas", 10),
            bg="#0D1117",  # Fondo oscuro
            fg="#56F175"   # Texto verde
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame inferior con estadísticas
        stats_frame = ttk.Frame(self.frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack(side=tk.LEFT)
    
    def show_document(self, document: DocumentPreview):
        """Muestra un documento en el preview"""
        self.current_document = document
        
        # Actualizar información del documento
        info_text = f"📄 {document.original_name} ({document.file_type})"
        if hasattr(document.metadata, 'size_bytes'):
            size_mb = document.metadata.size_bytes / (1024 * 1024)
            info_text += f" - {size_mb:.2f} MB"
        self.doc_info_label.config(text=info_text)
        
        # Mostrar contenido
        content = document.markdown_content
        
        # Limitar contenido si es muy largo
        if len(content) > self.max_preview_length:
            content = content[:self.max_preview_length] + "\n\n[... contenido truncado ...]"
        
        # Actualizar área de texto
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, content)
        self.text_area.config(state=tk.DISABLED)
        
        # Actualizar estadísticas
        stats_text = f"📊 Caracteres: {len(document.markdown_content):,}"
        if hasattr(document.metadata, 'word_count'):
            stats_text += f" | Palabras: {document.metadata.word_count:,}"
        if hasattr(document.metadata, 'processing_method'):
            stats_text += f" | Método: {document.metadata.processing_method}"
        self.stats_label.config(text=stats_text)
        
        # Habilitar botón de copiar
        self.copy_button.config(state=tk.NORMAL)
    
    def clear_preview(self):
        """Limpia el preview"""
        self.current_document = None
        self.doc_info_label.config(text="Ningún documento seleccionado")
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.stats_label.config(text="")
        self.copy_button.config(state=tk.DISABLED)
    
    def _copy_content(self):
        """Copia el contenido al portapapeles"""
        if self.current_document:
            content = self.current_document.markdown_content
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            
            # Mostrar mensaje temporal
            original_text = self.copy_button.cget("text")
            self.copy_button.config(text="¡Copiado!")
            self.parent.after(2000, lambda: self.copy_button.config(text=original_text))
    
    def pack(self, **kwargs):
        """Empaqueta el widget"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Desempaqueta el widget"""
        self.frame.pack_forget() 