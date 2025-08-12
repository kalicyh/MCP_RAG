"""
Vista principal de la aplicación Bulk Ingest GUI
Muestra la interfaz gráfica y se conecta con el MainController
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Dict, Any
import sys
import os
from pathlib import Path
import queue
import tkinter.ttk as ttk_plus

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from controllers.main_controller import MainController
from widgets.document_preview_widget import DocumentPreviewWidget
from widgets.statistics_widget import StatisticsWidget

class MainView:
    """
    Vista principal de la aplicación Bulk Ingest GUI
    """
    def __init__(self, root: tk.Tk, controller: MainController):
        self.root = root
        self.controller = controller
        
        # Configurar la ventana principal
        self.root.title("批量导入高级版 - 模块化RAG系统")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        # Variables de estado
        self.selected_directory = tk.StringVar()
        self.save_markdown = tk.BooleanVar(value=True)
        self.search_text = tk.StringVar()
        self.file_type_filter = tk.StringVar(value="Todos")
        
        # Colas para logging seguro entre hilos
        self.log_queue = queue.Queue()
        self.storage_log_queue = queue.Queue()
        
        # Configurar estilos y crear widgets
        self.setup_styles()
        self.create_widgets()
        
        # Conectar callbacks de la UI al controlador
        self._register_callbacks()
        
        # Iniciar procesamiento de colas de logs
        self.process_log_queue()
        self.process_storage_log_queue()
        
        # Configurar limpieza automática
        self.setup_cleanup()
    
    def setup_styles(self):
        """Configurar estilos para la interfaz con tema 'Terminal Refinada'."""
        
        # --- Paleta de colores "Terminal Refinada" ---
        BG_COLOR = "#0D1117"       # Negro azulado, como terminales modernas (GitHub Dark)
        FG_COLOR = "#56F175"       # Verde CRT, sutil y legible
        SELECT_BG = "#56F175"      # Verde para fondos de selección
        SELECT_FG = "#0D1117"      # Negro para texto seleccionado
        TROUGH_COLOR = "#161B22"    # Fondo de la barra de progreso
        BORDER_COLOR = "#30363D"   # Borde gris oscuro, muy sutil
        HIGHLIGHT_BORDER = "#56F175" # Borde verde para cuando el mouse pasa por encima
        FONT_FAMILY = "Consolas"   # Fuente ideal para consolas
        
        self.root.configure(bg=BG_COLOR)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Configuración general de widgets ---
        style.configure('.',
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        fieldbackground=BG_COLOR,
                        bordercolor=BORDER_COLOR)
        
        # --- Estilos específicos ---
        style.configure('TFrame', background=BG_COLOR)
        style.configure('Title.TLabel', font=(FONT_FAMILY, 16, 'bold'), foreground=FG_COLOR, background=BG_COLOR)
        style.configure('Subtitle.TLabel', font=(FONT_FAMILY, 11), foreground=FG_COLOR, background=BG_COLOR)
        style.configure('Info.TLabel', foreground="#56F175", background=BG_COLOR)
        style.configure('Warning.TLabel', foreground="#F1E056", background=BG_COLOR) # Amarillo
        
        # Estilo para los LabelFrame
        style.configure('TLabelFrame', background=BG_COLOR, bordercolor=BORDER_COLOR, borderwidth=1)
        style.configure('TLabelFrame.Label', foreground=FG_COLOR, background=BG_COLOR, font=(FONT_FAMILY, 11, 'bold'))
        
        # Estilo para los botones
        style.map('TButton',
                  background=[('active', '#161B22')],
                  foreground=[('active', FG_COLOR)],
                  bordercolor=[('active', HIGHLIGHT_BORDER)])
        style.configure('TButton',
                        font=(FONT_FAMILY, 11, 'bold'),
                        foreground=FG_COLOR,
                        background=BG_COLOR,
                        borderwidth=1,
                        relief="solid",
                        padding=[10, 5])
        
        # Estilo para las pestañas (Notebook)
        style.configure('TNotebook', background=BG_COLOR, borderwidth=1, bordercolor=BORDER_COLOR)
        style.configure('TNotebook.Tab',
                        background=[BG_COLOR],
                        foreground=[FG_COLOR],
                        font=(FONT_FAMILY, 11, 'bold'),
                        padding=[10, 5],
                        relief="solid",
                        borderwidth=1)
        style.map('TNotebook.Tab',
                  background=[('selected', '#161B22'), ('active', '#21262D')],
                  bordercolor=[('selected', HIGHLIGHT_BORDER), ('active', BORDER_COLOR)])
        
        # Estilo para la barra de progreso
        style.configure('green.Horizontal.TProgressbar',
                        troughcolor=TROUGH_COLOR,
                        background=FG_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=FG_COLOR,
                        darkcolor=FG_COLOR)
                        
        # Estilo para los campos de texto
        style.configure('TEntry', foreground=FG_COLOR, insertcolor=FG_COLOR, borderwidth=1, relief="solid")
        style.map('TEntry', fieldbackground=[('readonly', TROUGH_COLOR)])

        # Estilo para Checkbuttons
        style.configure('TCheckbutton',
                        indicatorforeground=FG_COLOR,
                        indicatorbackground=BG_COLOR,
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        font=(FONT_FAMILY, 11))
        style.map('TCheckbutton',
                  indicatorbackground=[('selected', FG_COLOR), ('active', BG_COLOR)],
                  indicatorforeground=[('selected', BG_COLOR), ('active', FG_COLOR)])
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal con notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Configuración y Procesamiento
        self.create_processing_tab()
        
        # Pestaña 2: Revisión y Selección
        self.create_review_tab()
        
        # Pestaña 3: Almacenamiento Final
        self.create_storage_tab()
        
        # Vincular evento de cambio de pestaña
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Manejar cambio de pestaña"""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        # Si se cambia a la pestaña de almacenamiento (índice 2), actualizar resumen
        if tab_index == 2:  # Pestaña de almacenamiento
            self._update_summary()
        # Si se cambia a la pestaña de revisión (índice 1), actualizar estadísticas de procesamiento
        if tab_index == 1 and hasattr(self, 'stats_widget'):
            stats = self.controller.get_processing_statistics()
            self.stats_widget.update_processing_stats(stats)
        # Si se cambia a la pestaña de Cache (índice 1 en el widget de estadísticas)
        if hasattr(self, 'stats_widget'):
            stats_tab = self.stats_widget.notebook.index(self.stats_widget.notebook.select())
            if stats_tab == 1:  # Cache
                cache_stats = self.controller.get_cache_statistics()
                self.stats_widget.update_cache_stats(cache_stats)
            elif stats_tab == 2:  # Base de Datos
                db_stats = self.controller.get_database_statistics()
                self.stats_widget.update_database_stats(db_stats)
        # También actualizar al cambiar de pestaña dentro del widget de estadísticas
        if hasattr(self, 'stats_widget'):
            def on_stats_tab_changed(event):
                stats_tab = self.stats_widget.notebook.index(self.stats_widget.notebook.select())
                if stats_tab == 1:
                    cache_stats = self.controller.get_cache_statistics()
                    self.stats_widget.update_cache_stats(cache_stats)
                elif stats_tab == 2:
                    db_stats = self.controller.get_database_statistics()
                    self.stats_widget.update_database_stats(db_stats)
            self.stats_widget.notebook.bind('<<NotebookTabChanged>>', on_stats_tab_changed)
    
    def create_processing_tab(self):
        """Crear pestaña de procesamiento"""
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="📁 处理")
        
        # Sección de directorio
        self.create_directory_section(processing_frame)
        
        # Sección de opciones
        self.create_options_section(processing_frame)
        
        # Sección de progreso
        self.create_progress_section(processing_frame)
        
        # Sección de logs
        self.create_logs_section(processing_frame)
        
        # Botones de control
        self.create_control_buttons(processing_frame)
        
        # Sección de resumen
        self.create_summary_section(processing_frame)
    
    def create_review_tab(self):
        """Crear pestaña de revisión"""
        review_frame = ttk.Frame(self.notebook)
        self.notebook.add(review_frame, text="📋 审核")
        
        # Frame superior para filtros y controles
        top_frame = ttk.Frame(review_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filtros
        filter_frame = ttk.LabelFrame(top_frame, text="过滤器")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._update_documents_list())
        search_entry_tooltip = ttk.Label(filter_frame, text="🔍 输入文件名的一部分以过滤列表。", foreground="#56F175", background="#0D1117")
        search_entry_tooltip.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="类型:").pack(side=tk.LEFT, padx=10)
        file_types = ["Todos", ".pdf", ".docx", ".txt", ".md", ".xlsx", ".pptx"]
        file_type_menu = ttk.OptionMenu(filter_frame, self.file_type_filter, "Todos", *file_types, 
                                       command=lambda _: self._update_documents_list())
        file_type_menu.pack(side=tk.LEFT, padx=5)
        file_type_tooltip = ttk.Label(filter_frame, text="📂 按文件扩展名过滤。", foreground="#56F175", background="#0D1117")
        file_type_tooltip.pack(side=tk.LEFT, padx=5)
        
        # Botones de selección
        ttk.Button(filter_frame, text="全选", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="全不选", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        selection_help = ttk.Label(filter_frame, text="您可以选择一个或多个文档进行预览或存储。", foreground="#56F175", background="#0D1117")
        selection_help.pack(side=tk.LEFT, padx=10)
        
        # Frame principal con lista y preview
        main_frame = ttk.Frame(review_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lista de documentos (izquierda)
        list_frame = ttk.LabelFrame(main_frame, text="已处理文档")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.docs_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=20)
        self.docs_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        docs_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.docs_listbox.yview)
        docs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_listbox.config(yscrollcommand=docs_scrollbar.set)
        
        # Vincular eventos de selección
        self.docs_listbox.bind('<<ListboxSelect>>', self._on_document_select)
        
        # Preview de documento (derecha)
        preview_frame = ttk.LabelFrame(main_frame, text="预览")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Crear widget de preview
        self.preview_widget = DocumentPreviewWidget(preview_frame)
        self.preview_widget.pack(fill=tk.BOTH, expand=True)
        
        # Frame inferior solo con estadísticas (sin navegación)
        bottom_frame = ttk.Frame(review_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Widget de estadísticas
        # self.stats_widget = StatisticsWidget(bottom_frame)
        # self.stats_widget.pack(side=tk.RIGHT)
        
        # Conectar callbacks del widget de estadísticas con el controlador
        # stats_callbacks = {
        #     'update_processing_stats': self._update_processing_stats_from_controller,
        #     'update_cache_stats': self._update_cache_stats_from_controller,
        #     'update_database_stats': self._update_database_stats_from_controller,
        #     'clear_cache': self._clear_cache_from_controller,
        #     'optimize_database': self._optimize_database_from_controller
        # }
        # self.stats_widget.set_callbacks(stats_callbacks)
    
    def create_storage_tab(self):
        """Crear pestaña de almacenamiento"""
        storage_frame = ttk.Frame(self.notebook)
        self.notebook.add(storage_frame, text="💾 存储")
        
        # Opciones de almacenamiento
        self.create_storage_options(storage_frame)
        
        # Botones de almacenamiento
        self.create_storage_buttons(storage_frame)
        
        # Progreso de almacenamiento
        self.create_storage_progress_section(storage_frame)
        
        # Logs de almacenamiento
        self.create_storage_logs(storage_frame)
        
        # Resumen final
        self.create_final_summary_section(storage_frame)
    
    def create_directory_section(self, parent):
        """Crear sección de selección de directorio"""
        dir_frame = ttk.LabelFrame(parent, text="📁 文档目录")
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="路径:").pack(side=tk.LEFT, padx=5)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_directory, width=60)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览", command=self._browse_directory).pack(side=tk.LEFT, padx=5)
    
    def create_options_section(self, parent):
        """Crear sección de opciones"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ 处理选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(options_frame, text="保存Markdown副本", 
                       variable=self.save_markdown).pack(side=tk.LEFT, padx=10)
    
    def create_progress_section(self, parent):
        """Crear sección de progreso"""
        progress_frame = ttk.LabelFrame(parent, text="📊 处理进度")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, style='green.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="进度: 0/0")
        self.progress_label.pack(side=tk.LEFT, padx=10)
    
    def create_logs_section(self, parent_frame):
        """Crear sección de logs"""
        log_frame = ttk.LabelFrame(parent_frame, text="📝 处理日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame para botones de control de logs
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(log_control_frame, text="清除日志", 
                  command=self._clear_logs).pack(side=tk.LEFT, padx=2)
        
        # Frame para área de texto y scrollbar
        text_scroll_frame = ttk.Frame(log_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de texto para logs
        self.log_text = tk.Text(text_scroll_frame, height=8, state=tk.DISABLED, 
                               bg="#0D1117", fg="#56F175", font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs
        log_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
    
    def create_control_buttons(self, parent):
        """Crear botones de control"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.process_button = ttk.Button(button_frame, text="🚀 开始处理", 
                                        command=self._start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", 
                                     command=self._stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🧹 清理", command=self._clear_documents).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 转到审核", command=self._go_to_review).pack(side=tk.RIGHT, padx=5)
    
    def create_summary_section(self, parent):
        """Crear sección de resumen"""
        summary_frame = ttk.LabelFrame(parent, text="📈 处理摘要")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_label = ttk.Label(summary_frame, text="摘要: 已处理 0 个文档")
        self.summary_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def create_storage_options(self, parent):
        """Crear opciones de almacenamiento"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ 存储选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="选择要存储到知识库的文档。").pack(padx=10, pady=5)
    
    def create_storage_buttons(self, parent):
        """Crear botones de almacenamiento"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.store_button = ttk.Button(button_frame, text="💾 存储所选文档", 
                                      command=self._start_storage)
        self.store_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📤 导出列表", command=self._export_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 导入列表", command=self._import_documents).pack(side=tk.LEFT, padx=5)
    
    def create_storage_progress_section(self, parent):
        """Crear sección de progreso de almacenamiento"""
        progress_frame = ttk.LabelFrame(parent, text="📊 存储进度")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.storage_progress_var = tk.DoubleVar()
        self.storage_progress_bar = ttk.Progressbar(progress_frame, variable=self.storage_progress_var, 
                                                   maximum=100, style='green.Horizontal.TProgressbar')
        self.storage_progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.storage_progress_label = ttk.Label(progress_frame, text="进度: 0/0")
        self.storage_progress_label.pack(side=tk.LEFT, padx=10)
    
    def create_storage_logs(self, parent_frame):
        """Crear logs de almacenamiento"""
        log_frame = ttk.LabelFrame(parent_frame, text="📝 存储日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame interno para área de texto y scrollbar
        text_scroll_frame = ttk.Frame(log_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de texto para logs de almacenamiento
        self.storage_log_text = tk.Text(text_scroll_frame, height=6, state=tk.DISABLED, 
                                       bg="#0D1117", fg="#56F175", font=("Consolas", 9))
        self.storage_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs de almacenamiento
        storage_log_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.storage_log_text.yview)
        storage_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.storage_log_text.config(yscrollcommand=storage_log_scrollbar.set)
    
    def create_final_summary_section(self, parent):
        """Crear sección de resumen final"""
        summary_frame = ttk.LabelFrame(parent, text="📈 最终摘要")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.final_summary_label = ttk.Label(summary_frame, text="摘要: 已准备存储 0 个文档")
        self.final_summary_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def _register_callbacks(self):
        """Registra los callbacks de la UI en el controlador"""
        callbacks = {
            'update_progress': self._update_progress,
            'update_logs': self._update_logs,
            'update_storage_logs': self._update_storage_logs,
            'update_status': self._update_status,
            'update_documents_list': self._update_documents_list,
            'update_summary': self._update_summary,
            'enable_processing_buttons': self._enable_processing_buttons,
            'disable_processing_buttons': self._disable_processing_buttons,
            'enable_storage_buttons': self._enable_storage_buttons,
            'disable_storage_buttons': self._disable_storage_buttons,
            'show_message': self._show_message,
            'update_storage_progress': self._update_storage_progress
        }
        self.controller.set_ui_callbacks(callbacks)
    
    # Métodos de interacción con la UI y el controlador
    def _browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
    
    def _start_processing(self):
        self.controller.start_processing(self.selected_directory.get(), self.save_markdown.get())
    
    def _stop_processing(self):
        self.controller.stop_processing()
    
    def _clear_documents(self):
        self.controller.cleanup()
        self._update_documents_list()
        self._update_summary()
        self.preview_widget.clear_preview()
    
    def _go_to_review(self):
        self.notebook.select(1)  # Cambiar a pestaña de revisión
    
    def _select_all(self):
        self.controller.select_all_documents()
        self._update_documents_list()
    
    def _deselect_all(self):
        self.controller.deselect_all_documents()
        self._update_documents_list()
    
    def _start_storage(self):
        # Usar la selección lógica, no solo la visual
        selected_docs = self.controller.get_selected_documents()
        self.controller.start_storage(selected_docs)
    
    def _export_documents(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            docs = self.controller.get_processed_documents()
            self.controller.export_documents(docs, file_path)
    
    def _import_documents(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.controller.import_documents(file_path)
            self._update_documents_list()
    
    def _on_document_select(self, event):
        """Al hacer clic, alterna la selección para almacenamiento y previsualiza el documento"""
        selection = self.docs_listbox.curselection()
        if not hasattr(self, 'filtered_docs'):
            self.filtered_docs = self.controller.get_processed_documents()
        all_docs = self.controller.get_processed_documents()
        if selection:
            for idx in selection:
                if idx < len(self.filtered_docs):
                    doc = self.filtered_docs[idx]
                    # Buscar el objeto real en la lista completa y actualizarlo
                    for real_doc in all_docs:
                        if real_doc.file_path == doc.file_path:
                            real_doc.selected.set(not real_doc.selected.get())
                            # Previsualizar el documento seleccionado
                            self.preview_widget.show_document(real_doc)
                            break
            self._update_documents_list()
    
    def _clear_logs(self):
        """Limpiar logs de procesamiento"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    # Métodos de actualización de la UI (llamados por el controlador)
    def _update_progress(self, current, total, current_file=""):
        percent = (current / total * 100) if total > 0 else 0
        self.progress_var.set(percent)
        self.progress_label.config(text=f"进度: {current}/{total} - {current_file}")
        self.root.update_idletasks()
    
    def _update_logs(self, message):
        self.log_queue.put(message)
    
    def _update_storage_logs(self, message):
        self.storage_log_queue.put(message)
    
    def _update_status(self, status):
        # Actualizar estado de la interfaz según el status
        pass
    
    def _update_documents_list(self):
        """Actualizar la lista de documentos con filtros de búsqueda y tipo"""
        self.docs_listbox.delete(0, tk.END)
        # Obtener filtros
        search = self.search_text.get().strip()
        file_type = self.file_type_filter.get()
        # Usar el método de filtrado del controlador
        filtered_docs = self.controller.filter_documents(search_text=search, file_type_filter=file_type)
        self.filtered_docs = filtered_docs  # Guardar para selección
        for doc in filtered_docs:
            status = "✅" if doc.selected.get() else "⭕"
            display_text = f"{status} {doc.original_name} ({doc.file_type}) - {doc.size_kb:.1f}KB"
            self.docs_listbox.insert(tk.END, display_text)
        if not filtered_docs:
            self.docs_listbox.insert(tk.END, "没有符合筛选条件的文档。")
    
    def _update_summary(self):
        """Actualizar resumen de documentos"""
        documents = self.controller.get_processed_documents()
        total_size = sum(doc.size_kb for doc in documents)
        total_words = sum(doc.metadata.word_count for doc in documents)
        
        summary_text = f"摘要: {len(documents)} 个文档已处理 - {total_size:.1f}KB - {total_words:,} 个词"
        self.summary_label.config(text=summary_text)
        
        # Actualizar también el resumen final
        final_summary_text = f"摘要: {len(documents)} 个文档已准备存储"
        self.final_summary_label.config(text=final_summary_text)
    
    def _enable_processing_buttons(self):
        self.process_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def _disable_processing_buttons(self):
        self.process_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
    
    def _enable_storage_buttons(self):
        self.store_button.config(state=tk.NORMAL)
    
    def _disable_storage_buttons(self):
        self.store_button.config(state=tk.DISABLED)
    
    def _show_message(self, title, message, msg_type="info"):
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _update_storage_progress(self, current, total, current_file=""):
        percent = (current / total * 100) if total > 0 else 0
        self.storage_progress_var.set(percent)
        self.storage_progress_label.config(text=f"进度: {current}/{total} - {current_file}")
        self.root.update_idletasks()
    
    def process_log_queue(self):
        """Procesar cola de logs de procesamiento"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
    
    def process_storage_log_queue(self):
        """Procesar cola de logs de almacenamiento"""
        try:
            while True:
                message = self.storage_log_queue.get_nowait()
                self.storage_log_text.config(state=tk.NORMAL)
                self.storage_log_text.insert(tk.END, message + "\n")
                self.storage_log_text.see(tk.END)
                self.storage_log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_storage_log_queue)
    
    def setup_cleanup(self):
        """Configurar limpieza automática"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """Manejar cierre de la aplicación"""
        self.controller.cleanup()
        self.root.destroy()
    
    # Métodos de callback para el widget de estadísticas
    def _update_processing_stats_from_controller(self):
        """Actualiza estadísticas de procesamiento desde el controlador"""
        try:
            stats = self.controller.get_processing_statistics()
            self.stats_widget.update_processing_stats(stats)
        except Exception as e:
            print(f"更新处理统计信息时出错: {e}")
    
    def _update_cache_stats_from_controller(self):
        """Actualiza estadísticas de cache desde el controlador"""
        try:
            stats = self.controller.get_cache_statistics()
            self.stats_widget.update_cache_stats(stats)
        except Exception as e:
            print(f"更新缓存统计信息时出错: {e}")
    
    def _update_database_stats_from_controller(self):
        print(">>> [GUI] 更新按钮已按下")
        try:
            stats = self.controller.get_database_statistics()
            print(f">>> [GUI] 统计信息已更新: {stats}")
            self.stats_widget.update_database_stats(stats)
        except Exception as e:
            print(f"更新数据库统计信息时出错: {e}")
    
    def _clear_cache_from_controller(self):
        """Limpia cache desde el controlador"""
        try:
            result = self.controller.clear_cache()
            if result['status'] == 'success':
                # Actualizar estadísticas de cache después de limpiar
                self._update_cache_stats_from_controller()
        except Exception as e:
            print(f"清理缓存时出错: {e}")
    
    def _optimize_database_from_controller(self):
        print(">>> [GUI] 优化按钮已按下")
        try:
            result = self.controller.optimize_database()
            print(f">>> [GUI] 优化结果: {result}")
            self._update_database_stats_from_controller()
            msg = result.get('message', 'Optimización completada')
            status = result.get('status', 'success')
            if hasattr(self, 'ui_callbacks') and 'show_message' in self.ui_callbacks:
                tipo = 'info' if status == 'success' else 'error'
                self.ui_callbacks['show_message']("Optimización", msg, tipo)
        except Exception as e:
            print(f"优化数据库时出错: {e}")