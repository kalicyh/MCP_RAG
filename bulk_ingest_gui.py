import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import queue
from markitdown import MarkItDown
from rag_core import get_vector_store, add_text_to_knowledge_base, log

# Lista de extensiones de archivo que queremos procesar
SUPPORTED_EXTENSIONS = [
    ".pdf", ".docx", ".pptx", ".xlsx", ".txt", 
    ".html", ".csv", ".json", ".xml"
]

# Carpeta donde se guardarán las copias en Markdown
CONVERTED_DOCS_DIR = "./converted_docs"

class BulkIngestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Ingest - Sistema RAG")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de control
        self.selected_directory = tk.StringVar()
        self.save_markdown_copies = tk.BooleanVar(value=True)
        self.processing = False
        self.log_queue = queue.Queue()
        
        # Configurar el estilo
        self.setup_styles()
        
        # Crear la interfaz
        self.create_widgets()
        
        # Iniciar el thread para procesar logs
        self.process_log_queue()
    
    def setup_styles(self):
        """Configurar estilos para la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores y estilos
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Info.TLabel', foreground='#3498db')
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="📚 Bulk Ingest - Sistema RAG", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtítulo
        subtitle_label = ttk.Label(main_frame, 
                                 text="Procesa múltiples documentos y añádelos a tu base de conocimiento", 
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 30))
        
        # Sección de selección de directorio
        self.create_directory_section(main_frame, 2)
        
        # Sección de opciones
        self.create_options_section(main_frame, 3)
        
        # Sección de progreso
        self.create_progress_section(main_frame, 4)
        
        # Sección de logs
        self.create_logs_section(main_frame, 5)
        
        # Sección de estadísticas
        self.create_stats_section(main_frame, 6)
        
        # Botones de control
        self.create_control_buttons(main_frame, 7)
    
    def create_directory_section(self, parent, row):
        """Crear sección para seleccionar directorio"""
        # Frame para la sección
        dir_frame = ttk.LabelFrame(parent, text="📁 Directorio de Documentos", padding="10")
        dir_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        dir_frame.columnconfigure(1, weight=1)
        
        # Label
        ttk.Label(dir_frame, text="Selecciona la carpeta con tus documentos:").grid(row=0, column=0, sticky=tk.W)
        
        # Entry para mostrar la ruta
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_directory, state='readonly')
        self.dir_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Botón para seleccionar directorio
        self.browse_btn = ttk.Button(dir_frame, text="📂 Explorar...", command=self.browse_directory)
        self.browse_btn.grid(row=1, column=2, padx=(10, 0), pady=(5, 0))
    
    def create_options_section(self, parent, row):
        """Crear sección de opciones"""
        # Frame para las opciones
        options_frame = ttk.LabelFrame(parent, text="⚙️ Opciones de Procesamiento", padding="10")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Checkbox para guardar copias Markdown
        self.save_copies_cb = ttk.Checkbutton(options_frame, 
                                            text="💾 Guardar copias en formato Markdown", 
                                            variable=self.save_markdown_copies)
        self.save_copies_cb.grid(row=0, column=0, sticky=tk.W)
        
        # Información sobre extensiones soportadas
        extensions_text = f"📄 Extensiones soportadas: {', '.join(SUPPORTED_EXTENSIONS)}"
        ttk.Label(options_frame, text=extensions_text, style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def create_progress_section(self, parent, row):
        """Crear sección de progreso"""
        # Frame para el progreso
        progress_frame = ttk.LabelFrame(parent, text="📊 Progreso", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Label de estado
        self.status_label = ttk.Label(progress_frame, text="Listo para procesar", style='Info.TLabel')
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Label de archivo actual
        self.current_file_label = ttk.Label(progress_frame, text="", style='Subtitle.TLabel')
        self.current_file_label.grid(row=2, column=0, sticky=tk.W, pady=(2, 0))
    
    def create_logs_section(self, parent, row):
        """Crear sección de logs"""
        # Frame para los logs
        logs_frame = ttk.LabelFrame(parent, text="📝 Registro de Actividad", padding="10")
        logs_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Text widget para logs
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=8, wrap=tk.WORD)
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón para limpiar logs
        clear_logs_btn = ttk.Button(logs_frame, text="🗑️ Limpiar", command=self.clear_logs)
        clear_logs_btn.grid(row=1, column=0, pady=(5, 0))
    
    def create_stats_section(self, parent, row):
        """Crear sección de estadísticas"""
        # Frame para estadísticas
        stats_frame = ttk.LabelFrame(parent, text="📈 Estadísticas", padding="10")
        stats_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Variables para estadísticas
        self.stats_vars = {
            'total_files': tk.StringVar(value="0"),
            'processed': tk.StringVar(value="0"),
            'errors': tk.StringVar(value="0"),
            'saved_copies': tk.StringVar(value="0")
        }
        
        # Crear labels de estadísticas
        stats_data = [
            ("📁 Archivos encontrados:", 'total_files'),
            ("✅ Procesados exitosamente:", 'processed'),
            ("❌ Errores:", 'errors'),
            ("💾 Copias guardadas:", 'saved_copies')
        ]
        
        for i, (label_text, var_name) in enumerate(stats_data):
            ttk.Label(stats_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            ttk.Label(stats_frame, textvariable=self.stats_vars[var_name], 
                     font=('Arial', 10, 'bold')).grid(row=i, column=1, sticky=tk.W)
    
    def create_control_buttons(self, parent, row):
        """Crear botones de control"""
        # Frame para botones
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        
        # Botón de procesar
        self.process_btn = ttk.Button(buttons_frame, text="🚀 Iniciar Procesamiento", 
                                     command=self.start_processing)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de detener
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                  command=self.stop_processing, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de salir
        exit_btn = ttk.Button(buttons_frame, text="🚪 Salir", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
    
    def browse_directory(self):
        """Abrir diálogo para seleccionar directorio"""
        directory = filedialog.askdirectory(title="Seleccionar carpeta con documentos")
        if directory:
            self.selected_directory.set(directory)
            self.log_message(f"📁 Directorio seleccionado: {directory}")
    
    def log_message(self, message):
        """Añadir mensaje a la cola de logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_queue.put(formatted_message)
    
    def process_log_queue(self):
        """Procesar mensajes de la cola de logs"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.logs_text.insert(tk.END, message)
                self.logs_text.see(tk.END)
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
    
    def update_stats(self, stats):
        """Actualizar estadísticas"""
        for key, value in stats.items():
            if key in self.stats_vars:
                self.stats_vars[key].set(str(value))
    
    def start_processing(self):
        """Iniciar el procesamiento en un thread separado"""
        if not self.selected_directory.get():
            messagebox.showerror("Error", "Por favor selecciona un directorio primero.")
            return
        
        if not os.path.isdir(self.selected_directory.get()):
            messagebox.showerror("Error", "El directorio seleccionado no existe.")
            return
        
        # Cambiar estado de la interfaz
        self.processing = True
        self.process_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.browse_btn.config(state='disabled')
        
        # Iniciar procesamiento en thread separado
        self.processing_thread = threading.Thread(target=self.process_directory)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """Detener el procesamiento"""
        self.processing = False
        self.log_message("⏹️ Procesamiento detenido por el usuario")
        self.finish_processing()
    
    def finish_processing(self):
        """Finalizar el procesamiento y restaurar interfaz"""
        self.processing = False
        self.process_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.browse_btn.config(state='normal')
        self.status_label.config(text="Procesamiento completado")
        self.current_file_label.config(text="")
    
    def process_directory(self):
        """Procesar el directorio seleccionado"""
        try:
            directory_path = self.selected_directory.get()
            self.log_message(f"🚀 Iniciando procesamiento masivo para: {directory_path}")
            
            # Configurar base de datos vectorial
            self.log_message("⚙️ Configurando base de datos vectorial...")
            vector_store = get_vector_store()
            md_converter = MarkItDown()
            self.log_message("✅ Base de datos configurada")
            
            # Contar archivos totales
            total_files = 0
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                        total_files += 1
            
            self.log_message(f"📁 Encontrados {total_files} archivos soportados")
            
            # Inicializar estadísticas
            stats = {
                'total_files': total_files,
                'processed': 0,
                'errors': 0,
                'saved_copies': 0
            }
            
            # Asegurar directorio de documentos convertidos
            if self.save_markdown_copies.get():
                if not os.path.exists(CONVERTED_DOCS_DIR):
                    os.makedirs(CONVERTED_DOCS_DIR)
                    self.log_message(f"📁 Creada carpeta: {CONVERTED_DOCS_DIR}")
            
            # Procesar archivos
            processed_count = 0
            for root, _, files in os.walk(directory_path):
                if not self.processing:
                    break
                    
                for file in files:
                    if not self.processing:
                        break
                        
                    if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                        file_path = os.path.join(root, file)
                        self.log_message(f"📄 Procesando: {file}")
                        
                        try:
                            # Convertir a Markdown
                            result = md_converter.convert(file_path)
                            markdown_content = result.text_content
                            
                            # Guardar copia si está habilitado
                            md_copy_path = ""
                            if self.save_markdown_copies.get():
                                md_copy_path = self.save_markdown_copy(file_path, markdown_content)
                                if md_copy_path:
                                    stats['saved_copies'] += 1
                                    self.log_message(f"💾 Copia guardada: {os.path.basename(md_copy_path)}")
                            
                            # Crear metadatos
                            source_metadata = {
                                "source": file,
                                "file_path": file_path,
                                "file_type": os.path.splitext(file)[1].lower(),
                                "processed_date": datetime.now().isoformat(),
                                "converted_to_md": md_copy_path if md_copy_path else "No"
                            }
                            
                            # Añadir a la base de conocimiento
                            add_text_to_knowledge_base(markdown_content, vector_store, source_metadata)
                            
                            processed_count += 1
                            stats['processed'] += 1
                            self.log_message(f"✅ {file} procesado exitosamente")
                            
                        except Exception as e:
                            stats['errors'] += 1
                            self.log_message(f"❌ Error procesando {file}: {str(e)}")
                        
                        # Actualizar progreso
                        self.update_progress(processed_count, total_files, file_path)
                        self.update_stats(stats)
            
            if self.processing:
                self.log_message("🎉 ¡Procesamiento completado!")
                self.log_message(f"📊 Resumen final:")
                self.log_message(f"   - Archivos procesados: {stats['processed']}")
                self.log_message(f"   - Copias guardadas: {stats['saved_copies']}")
                self.log_message(f"   - Errores: {stats['errors']}")
                
                messagebox.showinfo("Completado", 
                                  f"Procesamiento completado exitosamente!\n\n"
                                  f"Archivos procesados: {stats['processed']}\n"
                                  f"Copias guardadas: {stats['saved_copies']}\n"
                                  f"Errores: {stats['errors']}")
            
        except Exception as e:
            self.log_message(f"💥 Error general: {str(e)}")
            messagebox.showerror("Error", f"Error durante el procesamiento:\n{str(e)}")
        
        finally:
            # Restaurar interfaz
            self.root.after(0, self.finish_processing)
    
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

def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = BulkIngestGUI(root)
    
    # Centrar la ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Iniciar la aplicación
    root.mainloop()

if __name__ == "__main__":
    main() 