import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import queue
from rag_core import get_vector_store, add_text_to_knowledge_base_enhanced, log, load_document_with_elements

# Lista de extensiones de archivo que queremos procesar
SUPPORTED_EXTENSIONS = [
    # Documentos de Office
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".rtf",
    # Documentos OpenDocument
    ".odt", ".odp", ".ods",
    # Formatos web y markup
    ".html", ".htm", ".xml", ".md",
    # Formatos de texto plano
    ".txt", ".csv", ".tsv",
    # Formatos de datos
    ".json", ".yaml", ".yml",
    # Imágenes (requieren OCR)
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
    # Correos electrónicos
    ".eml", ".msg"
]

# Carpeta donde se guardarán las copias en Markdown
CONVERTED_DOCS_DIR = "./converted_docs"

class DocumentPreview:
    """Clase para manejar la previsualización de documentos"""
    def __init__(self, file_path, markdown_content, file_type, original_name, metadata=None):
        self.file_path = file_path
        self.markdown_content = markdown_content
        self.file_type = file_type
        self.original_name = original_name
        self.metadata = metadata or {}
        self.selected = tk.BooleanVar(value=True)  # Por defecto seleccionado
        self.preview_visible = False

class BulkIngestAdvancedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Ingest Avanzado")

        # --- Geometría de la ventana ---
        self.root.geometry("1100x850") 
        self.root.minsize(900, 700)

        # --- Variables de estado (DEBEN INICIALIZARSE ANTES DE CREAR WIDGETS) ---
        self.selected_directory = tk.StringVar()
        self.save_markdown = tk.BooleanVar(value=True)
        self.processing_running = False
        self.stop_requested = False
        self.storage_running = False
        self.stop_storage_requested = False

        # Colas para logging seguro entre hilos
        self.log_queue = queue.Queue()
        self.storage_log_queue = queue.Queue()
        
        # Lista de documentos procesados
        self.processed_documents = [] # Almacena tuplas (path, markdown_content, size)
        self.documents_to_store = {} # Diccionario {path: BooleanVar}
        
        # --- Configuración e inicialización de la UI ---
        self.setup_styles()
        self.create_widgets()

        # Iniciar el procesamiento de colas de logs
        self.process_log_queue()
        self.process_storage_log_queue()
    
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
            self.update_summary()
    
    def create_processing_tab(self):
        """Crear pestaña de procesamiento"""
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="📁 Procesamiento")
        
        # Frame principal
        main_frame = ttk.Frame(processing_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="📚 Bulk Ingest Avanzado - Procesamiento", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Subtítulo
        subtitle_label = ttk.Label(main_frame, 
                                 text="Procesa documentos y previsualiza su conversión a Markdown", 
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # Sección de selección de directorio
        self.create_directory_section(main_frame)
        
        # Sección de opciones
        self.create_options_section(main_frame)
        
        # Sección de progreso
        self.create_progress_section(main_frame)
        
        # Sección de logs
        self.create_logs_section(main_frame)
        
        # Botones de control
        self.create_control_buttons(main_frame)
    
    def create_review_tab(self):
        """Crear pestaña de revisión"""
        review_frame = ttk.Frame(self.notebook)
        self.notebook.add(review_frame, text="👀 Revisión")
        
        # Frame principal
        main_frame = ttk.Frame(review_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="👀 Revisión de Documentos", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame para lista de documentos y previsualización
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo: Lista de documentos
        left_panel = ttk.LabelFrame(content_frame, text="📋 Documentos Procesados", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Lista de documentos
        self.documents_listbox = tk.Listbox(left_panel, selectmode=tk.SINGLE, bg="#1a1a1a", fg="#33ff33", selectbackground="#33ff33", selectforeground="#000000", borderwidth=0, highlightthickness=1, highlightbackground="#33ff33")
        self.documents_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.documents_listbox.bind('<<ListboxSelect>>', self.on_document_select)
        
        # Botones para la lista
        list_buttons_frame = ttk.Frame(left_panel)
        list_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(list_buttons_frame, text="✅ Seleccionar Todos", 
                  command=self.select_all_documents).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_buttons_frame, text="❌ Deseleccionar Todos", 
                  command=self.deselect_all_documents).pack(side=tk.LEFT)
        
        # Panel derecho: Previsualización
        right_panel = ttk.LabelFrame(content_frame, text="📄 Previsualización Markdown", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Información del documento
        self.doc_info_frame = ttk.Frame(right_panel)
        self.doc_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.doc_name_label = ttk.Label(self.doc_info_frame, text="", style='Info.TLabel')
        self.doc_name_label.pack(anchor=tk.W)
        
        self.doc_type_label = ttk.Label(self.doc_info_frame, text="", style='Subtitle.TLabel')
        self.doc_type_label.pack(anchor=tk.W)
        
        self.doc_size_label = ttk.Label(self.doc_info_frame, text="", style='Subtitle.TLabel')
        self.doc_size_label.pack(anchor=tk.W)
        
        # Checkbox para seleccionar documento
        self.doc_select_var = tk.BooleanVar(value=True)
        self.doc_select_cb = ttk.Checkbutton(right_panel, text="✅ Incluir en base de datos", 
                                           variable=self.doc_select_var, 
                                           command=self.on_document_selection_change)
        self.doc_select_cb.pack(anchor=tk.W, pady=(0, 10))
        
        # Área de previsualización
        preview_frame = ttk.Frame(right_panel)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, 
                                                     font=('Courier New', 9), bg="#1a1a1a", fg="#33ff33", insertbackground="#33ff33", selectbackground="#33ff33", selectforeground="#000000", borderwidth=0, highlightthickness=1, highlightbackground="#33ff33")
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de navegación
        nav_frame = ttk.Frame(right_panel)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(nav_frame, text="⬅️ Anterior", 
                  command=self.previous_document).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="➡️ Siguiente", 
                  command=self.next_document).pack(side=tk.LEFT)
        
        # Contador de documentos
        self.doc_counter_label = ttk.Label(nav_frame, text="", style='Info.TLabel')
        self.doc_counter_label.pack(side=tk.RIGHT)
    
    def create_storage_tab(self):
        """Crear pestaña de almacenamiento final"""
        storage_frame = ttk.Frame(self.notebook)
        self.notebook.add(storage_frame, text="💾 Almacenamiento")
        
        # Frame principal
        main_frame = ttk.Frame(storage_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="💾 Almacenamiento Final", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Resumen de selección
        self.create_summary_section(main_frame)
        
        # Opciones de almacenamiento
        self.create_storage_options(main_frame)
        
        # Progreso de almacenamiento
        self.create_storage_progress_section(main_frame)
        
        # Botones de acción
        self.create_storage_buttons(main_frame)
        
        # Logs de almacenamiento
        self.create_storage_logs(main_frame)
    
    def create_directory_section(self, parent):
        """Crear sección para seleccionar directorio"""
        dir_frame = ttk.LabelFrame(parent, text="📁 Directorio de Documentos", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label
        ttk.Label(dir_frame, text="Selecciona la carpeta con tus documentos:").pack(anchor=tk.W)
        
        # Frame para entry y botón
        entry_frame = ttk.Frame(dir_frame)
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Entry para mostrar la ruta
        self.dir_entry = ttk.Entry(entry_frame, textvariable=self.selected_directory, state='readonly')
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botón para seleccionar directorio
        self.browse_btn = ttk.Button(entry_frame, text="📂 Explorar...", command=self.browse_directory)
        self.browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_options_section(self, parent):
        """Crear sección de opciones"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Opciones de Procesamiento", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkbox para guardar copias Markdown
        self.save_copies_cb = ttk.Checkbutton(options_frame, 
                                            text="💾 Guardar copias en formato Markdown", 
                                            variable=self.save_markdown)
        self.save_copies_cb.pack(anchor=tk.W)
        
        # Información sobre extensiones soportadas
        extensions_text = f"📄 Extensiones soportadas: {', '.join(SUPPORTED_EXTENSIONS)}"
        ttk.Label(options_frame, text=extensions_text, style='Info.TLabel').pack(anchor=tk.W, pady=(5, 0))
    
    def create_progress_section(self, parent):
        """Crear sección de progreso"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progreso", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', style='green.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label de estado
        self.status_label = ttk.Label(progress_frame, text="Listo para procesar", style='Info.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # Label de archivo actual
        self.current_file_label = ttk.Label(progress_frame, text="", style='Subtitle.TLabel')
        self.current_file_label.pack(anchor=tk.W, pady=(2, 0))
    
    def create_logs_section(self, parent_frame):
        """Crea la sección de registro de actividad en la pestaña de procesamiento."""
        main_frame = ttk.Frame(parent_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Título ---
        title_label = ttk.Label(main_frame, text="Registro de Actividad", style='TLabelFrame.Label')
        title_label.pack(anchor='w', padx=20, pady=(10, 0))

        # --- Contenedor para el registro de actividad ---
        # Se cambia LabelFrame por Frame para un look de consola sin título
        logs_frame = ttk.Frame(main_frame, style='TFrame')
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10), padx=20)
        
        # --- Área de texto para logs ---
        self.logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, height=10, 
                                                   background="#0D1117", foreground="#56F175", 
                                                   font=("Consolas", 10),
                                                   borderwidth=1, relief="solid",
                                                   padx=10, pady=10)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        self.logs_text.insert(tk.END, "> Listo para procesar...\n")
        self.logs_text.configure(state='disabled')

    def create_control_buttons(self, parent):
        """Crear botones de control"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=(0, 20))
        
        # Botón de procesar
        self.process_btn = ttk.Button(buttons_frame, text="🚀 Iniciar Procesamiento", 
                                     command=self.start_processing)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de detener
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                  command=self.stop_processing, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para ir a revisión
        self.review_btn = ttk.Button(buttons_frame, text="👀 Ir a Revisión", 
                                    command=self.go_to_review, state='disabled')
        self.review_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de salir
        exit_btn = ttk.Button(buttons_frame, text="🚪 Salir", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
    
    def create_summary_section(self, parent):
        """Crear sección de resumen"""
        summary_frame = ttk.LabelFrame(parent, text="📊 Resumen de Selección", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Variables para el resumen
        self.summary_vars = {
            'total_processed': tk.StringVar(value="0"),
            'selected_for_storage': tk.StringVar(value="0"),
            'not_selected': tk.StringVar(value="0"),
            'total_size': tk.StringVar(value="0 KB"),
            'selected_size': tk.StringVar(value="0 KB")
        }
        
        # Crear labels de resumen
        summary_data = [
            ("📁 Total procesados:", 'total_processed'),
            ("✅ Seleccionados para almacenar:", 'selected_for_storage'),
            ("❌ No seleccionados:", 'not_selected'),
            ("📏 Tamaño total:", 'total_size'),
            ("📏 Tamaño seleccionado:", 'selected_size')
        ]
        
        for i, (label_text, var_name) in enumerate(summary_data):
            frame = ttk.Frame(summary_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label_text).pack(side=tk.LEFT)
            ttk.Label(frame, textvariable=self.summary_vars[var_name], 
                     font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Añadir información adicional
        info_frame = ttk.Frame(summary_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(info_frame, text="💡 El resumen se actualiza automáticamente al cambiar de pestaña", 
                 style='Info.TLabel').pack(anchor=tk.W)
    
    def create_storage_options(self, parent):
        """Crear opciones de almacenamiento"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Opciones de Almacenamiento", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkbox para confirmar almacenamiento
        self.confirm_storage = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="🔒 Confirmar almacenamiento en base de datos", 
                       variable=self.confirm_storage).pack(anchor=tk.W)
        
        # Información adicional
        ttk.Label(options_frame, 
                 text="⚠️ Solo los documentos seleccionados serán añadidos a la base de conocimiento", 
                 style='Warning.TLabel').pack(anchor=tk.W, pady=(5, 0))
    
    def create_storage_buttons(self, parent):
        """Crear botones de almacenamiento"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=(0, 20))
        
        # Botón de almacenar
        self.store_btn = ttk.Button(buttons_frame, text="💾 Almacenar Seleccionados", 
                                   command=self.store_selected_documents, state='disabled')
        self.store_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de actualizar resumen
        refresh_btn = ttk.Button(buttons_frame, text="🔄 Actualizar Resumen", 
                                command=self.update_summary)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de volver a revisión
        ttk.Button(buttons_frame, text="👀 Volver a Revisión", 
                  command=self.go_to_review_tab).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de salir
        exit_btn = ttk.Button(buttons_frame, text="🚪 Salir", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
    
    def create_storage_logs(self, parent_frame):
        """Crea la sección de logs en la pestaña de almacenamiento."""
        # --- Título ---
        title_label = ttk.Label(parent_frame, text="Registro de Actividad de Almacenamiento", style='TLabelFrame.Label')
        title_label.pack(anchor='w', padx=20, pady=(10, 0))

        # --- Contenedor para el registro de actividad ---
        logs_frame = ttk.Frame(parent_frame, style='TFrame')
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10), padx=20)
        
        self.storage_logs_text = scrolledtext.ScrolledText(
            logs_frame, wrap=tk.WORD, height=10,
            background="#0D1117", foreground="#56F175",
            font=("Consolas", 10),
            borderwidth=1, relief="solid", padx=10, pady=10)
        
        self.storage_logs_text.pack(fill=tk.BOTH, expand=True)
        self.storage_logs_text.insert(tk.END, "> Esperando para guardar archivos en la base de datos...\n")
        self.storage_logs_text.configure(state='disabled')
    
    def create_storage_progress_section(self, parent):
        """Crear sección de progreso de almacenamiento"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progreso de Almacenamiento", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Barra de progreso
        self.storage_progress_bar = ttk.Progressbar(progress_frame, mode='determinate', style='green.Horizontal.TProgressbar')
        self.storage_progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label de estado
        self.storage_status_label = ttk.Label(progress_frame, text="Listo para almacenar", style='Info.TLabel')
        self.storage_status_label.pack(anchor=tk.W)
        
        # Label de archivo actual
        self.storage_current_file_label = ttk.Label(progress_frame, text="", style='Subtitle.TLabel')
        self.storage_current_file_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Botón de detener almacenamiento
        self.stop_storage_btn = ttk.Button(progress_frame, text="⏹️ Detener Almacenamiento", 
                                          command=self.stop_storage, state='disabled')
        self.stop_storage_btn.pack(anchor=tk.W, pady=(5, 0))
    
    def browse_directory(self):
        """Abrir diálogo para seleccionar directorio"""
        directory = filedialog.askdirectory(title="Seleccionar carpeta con documentos")
        if directory:
            self.selected_directory.set(directory)
            self.log_message(f"📁 Directorio seleccionado: {directory}")
    
    def log_message(self, message):
        """Añadir mensaje a la cola de logs con formato de consola."""
        # Formato de consola simple con un prompt '>'
        formatted_message = f"> {message}\n"
        self.log_queue.put(formatted_message)
    
    def process_log_queue(self):
        """Procesa los mensajes de la cola de logs."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.logs_text.configure(state='normal')
                self.logs_text.insert(tk.END, message)
                self.logs_text.see(tk.END)
                self.logs_text.configure(state='disabled')
                self.logs_text.update_idletasks()
        except queue.Empty:
            pass
        finally:
            # Programar la siguiente verificación
            self.root.after(100, self.process_log_queue)
    
    def clear_logs(self):
        """Limpiar el área de logs"""
        self.logs_text.delete(1.0, tk.END)
    
    def update_progress(self, current, total, current_file=""):
        """Actualizar la barra de progreso y estado"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_bar['value'] = progress
            self.status_label.config(text=f"Procesando... {current}/{total} ({progress:.1f}%)")
        
        if current_file:
            self.current_file_label.config(text=f"Archivo actual: {os.path.basename(current_file)}")
        
        self.root.update_idletasks()
    
    def start_processing(self):
        """Iniciar el procesamiento de documentos en un hilo separado."""
        if not self.selected_directory.get():
            messagebox.showerror("Error", "Por favor selecciona un directorio primero.")
            return
        
        if not os.path.isdir(self.selected_directory.get()):
            messagebox.showerror("Error", "El directorio seleccionado no existe.")
            return
        
        # Limpiar documentos anteriores
        self.processed_documents.clear()
        
        # Cambiar estado de la interfaz
        self.processing_running = True
        self.stop_requested = False
        self.process_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.browse_btn.config(state='disabled')
        self.review_btn.config(state='disabled')
        
        # Iniciar procesamiento en thread separado
        self.processing_thread = threading.Thread(target=self.process_directory, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        """Detener el procesamiento"""
        self.processing_running = False
        self.stop_requested = True
        self.log_message("Proceso de ingesta detenido por el usuario.")
        self.finish_processing()
    
    def finish_processing(self):
        """Finalizar el procesamiento y restaurar interfaz"""
        self.processing_running = False
        self.stop_requested = False
        self.process_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.browse_btn.config(state='normal')
        self.status_label.config(text="Procesamiento completado")
        self.current_file_label.config(text="")
        
        # Habilitar botón de revisión si hay documentos
        if self.processed_documents:
            self.review_btn.config(state='normal')
            self.update_documents_list()
            # Actualizar resumen después del procesamiento
            self.update_summary()
    
    def process_directory(self):
        """Recorre un directorio, convierte archivos a Markdown y los prepara para revisión."""
        try:
            directory_path = self.selected_directory.get()
            self.log_message(f"Iniciando procesamiento para el directorio: {directory_path}")
            
            # Contar archivos totales para la barra de progreso
            total_files = 0
            file_paths = []
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                        total_files += 1
                        file_paths.append(os.path.join(root, file))
            
            self.log_message(f"Se encontraron {total_files} archivos compatibles.")
            
            processed_count = 0
            for file_path in file_paths:
                if self.stop_requested:
                    break
                
                original_filename = os.path.basename(file_path)
                processed_count += 1
                self.log_message(f"[{processed_count}/{total_files}] Procesando: {original_filename}")
                self.update_progress(processed_count, total_files, original_filename)
                
                try:
                    # Usar el sistema mejorado de Unstructured con elementos estructurales
                    self.log_message(f"   - Cargando con sistema mejorado de Unstructured...")
                    markdown_content, metadata, structural_elements = load_document_with_elements(file_path)
                    
                    if not markdown_content or markdown_content.isspace():
                        self.log_message(f"   - Advertencia: El documento resultó vacío tras el procesamiento. Omitiendo.")
                        continue
                        
                    self.log_message(f"   - Convertido ({len(markdown_content)} caracteres)")
                    self.log_message(f"   - Método de procesamiento: {metadata.get('processing_method', 'unknown')}")
                    
                    # Mostrar información estructural si está disponible
                    if 'structural_info' in metadata:
                        struct_info = metadata['structural_info']
                        self.log_message(f"   - Estructura: {struct_info['titles_count']} títulos, {struct_info['tables_count']} tablas, {struct_info['lists_count']} listas")
                    
                    # Mostrar información de elementos estructurales
                    if structural_elements:
                        self.log_message(f"   - Elementos estructurales: {len(structural_elements)} elementos para chunking semántico")
                    
                    # Guardar copia en Markdown si la opción está seleccionada
                    if self.save_markdown.get():
                        self.log_message(f"   - Guardando copia Markdown...")
                        md_copy_path = self.save_markdown_copy(file_path, markdown_content)
                        if md_copy_path:
                            metadata['converted_to_md'] = md_copy_path
                            self.log_message(f"   - Copia guardada: {os.path.basename(md_copy_path)}")

                    file_type = os.path.splitext(original_filename)[1]
                    
                    # Guardar el resultado en la lista para la pestaña de revisión
                    preview = DocumentPreview(file_path, markdown_content, file_type, original_filename, metadata)
                    # Añadir elementos estructurales al preview
                    preview.structural_elements = structural_elements
                    self.processed_documents.append(preview)
                    
                except Exception as e:
                    self.log_message(f"   - Error procesando '{original_filename}': {e}")

        except Exception as e:
            self.log_message(f"Error inesperado durante el procesamiento: {e}")
        finally:
            if not self.stop_requested:
                self.finish_processing()
    
    def save_markdown_copy(self, file_path: str, markdown_content: str) -> str:
        """Guardar copia en Markdown"""
        try:
            original_filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(original_filename)[0]
            md_filename = f"{name_without_ext}.md"
            md_filepath = os.path.join(CONVERTED_DOCS_DIR, md_filename)
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return md_filepath
        except Exception as e:
            self.log_message(f"⚠️ No se pudo guardar copia Markdown: {e}")
            return ""
    
    def update_documents_list(self):
        """Actualizar la lista de documentos"""
        self.documents_listbox.delete(0, tk.END)
        for doc in self.processed_documents:
            status = "✅" if doc.selected.get() else "❌"
            self.documents_listbox.insert(tk.END, f"{status} {doc.original_name}")
        
        # Seleccionar el primer documento si existe
        if self.processed_documents:
            self.documents_listbox.selection_set(0)
            self.current_preview_index = 0
            self.update_preview()
    
    def on_document_select(self, event):
        """Manejar selección de documento en la lista"""
        selection = self.documents_listbox.curselection()
        if selection:
            self.current_preview_index = selection[0]
            self.update_preview()
    
    def update_preview(self):
        """Actualizar la previsualización del documento actual"""
        if not self.processed_documents or self.current_preview_index >= len(self.processed_documents):
            return
        
        doc = self.processed_documents[self.current_preview_index]
        
        # Actualizar información del documento
        self.doc_name_label.config(text=f"📄 {doc.original_name}")
        self.doc_type_label.config(text=f"📁 Tipo: {doc.file_type}")
        self.doc_size_label.config(text=f"📏 Tamaño: {len(doc.markdown_content)} caracteres")
        
        # Actualizar checkbox de selección
        self.doc_select_var.set(doc.selected.get())
        
        # Actualizar previsualización
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, doc.markdown_content)
        
        # Actualizar contador
        self.doc_counter_label.config(text=f"{self.current_preview_index + 1} de {len(self.processed_documents)}")
    
    def on_document_selection_change(self):
        """Manejar cambio en la selección del documento"""
        if not self.processed_documents or self.current_preview_index >= len(self.processed_documents):
            return
        
        doc = self.processed_documents[self.current_preview_index]
        doc.selected.set(self.doc_select_var.get())
        
        # Actualizar lista
        self.update_documents_list()
        self.update_summary()
    
    def select_all_documents(self):
        """Seleccionar todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(True)
        self.update_documents_list()
        self.update_summary()
        if self.processed_documents:
            self.update_preview()
    
    def deselect_all_documents(self):
        """Deseleccionar todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(False)
        self.update_documents_list()
        self.update_summary()
        if self.processed_documents:
            self.update_preview()
    
    def previous_document(self):
        """Ir al documento anterior"""
        if self.processed_documents and self.current_preview_index > 0:
            self.current_preview_index -= 1
            self.documents_listbox.selection_clear(0, tk.END)
            self.documents_listbox.selection_set(self.current_preview_index)
            self.update_preview()
    
    def next_document(self):
        """Ir al siguiente documento"""
        if self.processed_documents and self.current_preview_index < len(self.processed_documents) - 1:
            self.current_preview_index += 1
            self.documents_listbox.selection_clear(0, tk.END)
            self.documents_listbox.selection_set(self.current_preview_index)
            self.update_preview()
    
    def update_summary(self):
        """Actualizar resumen de selección"""
        try:
            total = len(self.processed_documents)
            selected = sum(1 for doc in self.processed_documents if doc.selected.get())
            not_selected = total - selected
            
            # Calcular tamaños
            total_size = sum(len(doc.markdown_content) for doc in self.processed_documents)
            selected_size = sum(len(doc.markdown_content) for doc in self.processed_documents if doc.selected.get())
            
            # Convertir a KB para mejor legibilidad
            total_size_kb = total_size / 1024
            selected_size_kb = selected_size / 1024
            
            # Actualizar variables del resumen
            self.summary_vars['total_processed'].set(str(total))
            self.summary_vars['selected_for_storage'].set(str(selected))
            self.summary_vars['not_selected'].set(str(not_selected))
            self.summary_vars['total_size'].set(f"{total_size_kb:.1f} KB")
            self.summary_vars['selected_size'].set(f"{selected_size_kb:.1f} KB")
            
            # Habilitar botón de almacenamiento si hay documentos seleccionados
            if selected > 0:
                self.store_btn.config(state='normal')
            else:
                self.store_btn.config(state='disabled')
            
            # Log de debugging
            print(f"📊 Resumen actualizado: Total={total}, Seleccionados={selected}, No seleccionados={not_selected}")
            print(f"📏 Tamaños: Total={total_size_kb:.1f}KB, Seleccionado={selected_size_kb:.1f}KB")
            
        except Exception as e:
            print(f"❌ Error actualizando resumen: {e}")
            # En caso de error, establecer valores por defecto
            self.summary_vars['total_processed'].set("0")
            self.summary_vars['selected_for_storage'].set("0")
            self.summary_vars['not_selected'].set("0")
            self.summary_vars['total_size'].set("0 KB")
            self.summary_vars['selected_size'].set("0 KB")
            self.store_btn.config(state='disabled')
    
    def go_to_review(self):
        """Ir a la pestaña de revisión"""
        self.notebook.select(1)  # Índice 1 es la pestaña de revisión
    
    def go_to_review_tab(self):
        """Ir a la pestaña de revisión desde almacenamiento"""
        self.notebook.select(1)
    
    def store_selected_documents(self):
        """Almacenar documentos seleccionados en la base de datos"""
        if not self.confirm_storage.get():
            messagebox.showwarning("Confirmación Requerida", 
                                 "Por favor marca la casilla de confirmación para continuar.")
            return
        
        selected_docs = [doc for doc in self.processed_documents if doc.selected.get()]
        if not selected_docs:
            messagebox.showwarning("Sin Documentos", 
                                 "No hay documentos seleccionados para almacenar.")
            return
        
        # Cambiar a pestaña de almacenamiento
        self.notebook.select(2)
        
        # Cambiar estado de la interfaz
        self.storage_running = True
        self.stop_storage_requested = False
        self.store_btn.config(state='disabled')
        self.stop_storage_btn.config(state='normal')
        self.storage_progress_bar['value'] = 0
        self.storage_status_label.config(text="Preparando almacenamiento...")
        self.storage_current_file_label.config(text="")
        
        # Iniciar almacenamiento en thread separado
        self.storage_thread = threading.Thread(target=self.perform_storage, args=(selected_docs,))
        self.storage_thread.daemon = True
        self.storage_thread.start()
    
    def perform_storage(self, selected_docs):
        """Realizar el almacenamiento de documentos seleccionados"""
        try:
            self.log_storage_message("🚀 Iniciando almacenamiento en base de datos...")
            
            # Configurar base de datos vectorial
            self.log_storage_message("⚙️ Configurando base de datos vectorial...")
            vector_store = get_vector_store()
            self.log_storage_message("✅ Base de datos configurada")
            
            # Procesar cada documento seleccionado
            for i, doc in enumerate(selected_docs):
                # Verificar si se debe detener
                if not self.storage_running:
                    self.log_storage_message("⏹️ Almacenamiento detenido por el usuario")
                    break
                
                self.log_storage_message(f"📄 Procesando {i+1}/{len(selected_docs)}: {doc.original_name}")
                
                try:
                    # Crear metadatos
                    source_metadata = {
                        "source": doc.original_name,
                        "file_path": doc.file_path,
                        "file_type": doc.file_type,
                        "processed_date": datetime.now().isoformat(),
                        "converted_to_md": "Yes"
                    }
                    
                    # Añadir a la base de conocimiento con chunking semántico real
                    add_text_to_knowledge_base_enhanced(
                        doc.markdown_content, 
                        vector_store, 
                        source_metadata,
                        use_semantic_chunking=True,
                        structural_elements=getattr(doc, 'structural_elements', None)
                    )
                    
                    self.log_storage_message(f"✅ {doc.original_name} almacenado exitosamente")
                    
                except Exception as e:
                    self.log_storage_message(f"❌ Error almacenando {doc.original_name}: {str(e)}")

                # Actualizar progreso DESPUÉS de procesar el documento
                self.root.after(0, lambda c=i+1, t=len(selected_docs), f=doc.file_path: 
                              self.update_storage_progress(c, t, f))
            
            # Completar progreso solo si no se detuvo
            if self.storage_running:
                # El progreso ya está al 100%, solo actualizamos el estado
                self.root.after(0, lambda: self.storage_status_label.config(text="¡Almacenamiento completado!"))
                self.root.after(0, lambda: self.storage_current_file_label.config(text=""))
                
                self.log_storage_message("🎉 ¡Almacenamiento completado!")
                self.log_storage_message(f"📊 Total de documentos almacenados: {len(selected_docs)}")
                
                messagebox.showinfo("Completado", 
                                  f"¡Almacenamiento completado exitosamente!\n\n"
                                  f"Documentos almacenados: {len(selected_docs)}")
            else:
                # Almacenamiento detenido
                self.root.after(0, lambda: self.storage_status_label.config(text="Almacenamiento detenido"))
                self.root.after(0, lambda: self.storage_current_file_label.config(text=""))
            
        except Exception as e:
            self.log_storage_message(f"💥 Error general: {str(e)}")
            self.root.after(0, lambda: self.storage_status_label.config(text="Error durante el almacenamiento"))
            messagebox.showerror("Error", f"Error durante el almacenamiento:\n{str(e)}")
        
        finally:
            # Restaurar interfaz
            self.storage_running = False
            self.root.after(0, lambda: self.store_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_storage_btn.config(state='disabled'))
    
    def log_storage_message(self, message):
        """Añadir mensaje a la cola de logs de almacenamiento con formato de consola."""
        # Formato de consola simple con un prompt '>'
        formatted_message = f"> {message}\n"
        self.storage_log_queue.put(formatted_message)

    def process_storage_log_queue(self):
        """Procesa los mensajes de la cola de logs de almacenamiento."""
        try:
            while True:
                message = self.storage_log_queue.get_nowait()
                self.storage_logs_text.configure(state='normal')
                self.storage_logs_text.insert(tk.END, message)
                self.storage_logs_text.see(tk.END)
                self.storage_logs_text.configure(state='disabled')
                self.storage_logs_text.update_idletasks()
        except queue.Empty:
            pass
        finally:
            # Programar la siguiente verificación
            self.root.after(100, self.process_storage_log_queue)

    def update_storage_progress(self, current, total, current_file=""):
        """Actualizar la barra de progreso de almacenamiento"""
        if total > 0:
            progress = (current / total) * 100
            self.storage_progress_bar['value'] = progress
            self.storage_status_label.config(text=f"Almacenando... {current}/{total} ({progress:.1f}%)")
        
        if current_file:
            self.storage_current_file_label.config(text=f"Documento actual: {os.path.basename(current_file)}")
        
        self.root.update_idletasks()

    def stop_storage(self):
        """Detener el almacenamiento"""
        self.storage_running = False
        self.stop_storage_requested = True
        self.storage_status_label.config(text="Deteniendo almacenamiento...")
        self.stop_storage_btn.config(state='disabled')
        self.log_storage_message("⏹️ Almacenamiento detenido por el usuario")
        
        # El thread se detendrá automáticamente en la siguiente iteración
    
def main():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = BulkIngestAdvancedGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 