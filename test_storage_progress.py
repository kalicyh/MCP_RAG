#!/usr/bin/env python3
"""
Script de prueba para la barra de progreso de almacenamiento
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random

class TestStorageProgressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Test - Barra de Progreso de Almacenamiento")
        self.root.geometry("800x600")
        
        # Variables de control
        self.storage_running = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de prueba"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🧪 Test - Barra de Progreso de Almacenamiento", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Sección de configuración
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuración de Prueba", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Número de documentos
        ttk.Label(config_frame, text="Número de documentos a simular:").pack(anchor=tk.W)
        self.doc_count_var = tk.StringVar(value="10")
        doc_count_entry = ttk.Entry(config_frame, textvariable=self.doc_count_var, width=10)
        doc_count_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Tiempo por documento
        ttk.Label(config_frame, text="Tiempo por documento (segundos):").pack(anchor=tk.W, pady=(10, 0))
        self.doc_time_var = tk.StringVar(value="1.0")
        doc_time_entry = ttk.Entry(config_frame, textvariable=self.doc_time_var, width=10)
        doc_time_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Sección de progreso
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progreso de Almacenamiento", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label de estado
        self.status_label = ttk.Label(progress_frame, text="Listo para almacenar", 
                                     font=('Arial', 10, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        # Label de archivo actual
        self.current_file_label = ttk.Label(progress_frame, text="", 
                                           font=('Arial', 9))
        self.current_file_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Botón de detener
        self.stop_btn = ttk.Button(progress_frame, text="⏹️ Detener Almacenamiento", 
                                  command=self.stop_storage, state='disabled')
        self.stop_btn.pack(anchor=tk.W, pady=(5, 0))
        
        # Sección de logs
        logs_frame = ttk.LabelFrame(main_frame, text="📝 Logs de Almacenamiento", padding="10")
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Text widget para logs
        self.logs_text = tk.Text(logs_frame, height=10, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs
        scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.config(yscrollcommand=scrollbar.set)
        
        # Botones de control
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack()
        
        self.start_btn = ttk.Button(buttons_frame, text="🚀 Iniciar Almacenamiento", 
                                   command=self.start_storage)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(buttons_frame, text="🗑️ Limpiar Logs", 
                              command=self.clear_logs)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = ttk.Button(buttons_frame, text="🚪 Salir", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
    
    def log_message(self, message):
        """Añadir mensaje a los logs"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, formatted_message)
        self.logs_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, current, total, current_file=""):
        """Actualizar la barra de progreso"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_bar['value'] = progress
            self.status_label.config(text=f"Almacenando... {current}/{total} ({progress:.1f}%)")
        
        if current_file:
            self.current_file_label.config(text=f"Documento actual: {current_file}")
        
        self.root.update_idletasks()
    
    def start_storage(self):
        """Iniciar almacenamiento simulado"""
        try:
            doc_count = int(self.doc_count_var.get())
            doc_time = float(self.doc_time_var.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")
            return
        
        if doc_count <= 0 or doc_time <= 0:
            messagebox.showerror("Error", "Los valores deben ser mayores que 0.")
            return
        
        # Cambiar estado de la interfaz
        self.storage_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_bar['value'] = 0
        self.status_label.config(text="Preparando almacenamiento...")
        self.current_file_label.config(text="")
        
        # Iniciar almacenamiento en thread separado
        self.storage_thread = threading.Thread(target=self.perform_storage, 
                                             args=(doc_count, doc_time))
        self.storage_thread.daemon = True
        self.storage_thread.start()
    
    def stop_storage(self):
        """Detener el almacenamiento"""
        self.storage_running = False
        self.status_label.config(text="Deteniendo almacenamiento...")
        self.stop_btn.config(state='disabled')
        self.log_message("⏹️ Almacenamiento detenido por el usuario")
    
    def perform_storage(self, doc_count, doc_time):
        """Realizar almacenamiento simulado"""
        try:
            self.log_message("🚀 Iniciando almacenamiento simulado...")
            self.log_message(f"📊 Configuración: {doc_count} documentos, {doc_time}s por documento")
            
            # Simular configuración de base de datos
            self.log_message("⚙️ Configurando base de datos vectorial...")
            time.sleep(1)  # Simular tiempo de configuración
            self.log_message("✅ Base de datos configurada")
            
            # Nombres de documentos simulados
            doc_names = [
                "documento1.pdf", "documento2.docx", "documento3.txt", "documento4.xlsx",
                "documento5.pdf", "documento6.docx", "documento7.txt", "documento8.xlsx",
                "documento9.pdf", "documento10.docx", "documento11.txt", "documento12.xlsx",
                "documento13.pdf", "documento14.docx", "documento15.txt"
            ]
            
            # Procesar cada documento
            for i in range(doc_count):
                # Verificar si se debe detener
                if not self.storage_running:
                    self.log_message("⏹️ Almacenamiento detenido por el usuario")
                    break
                
                # Obtener nombre del documento
                doc_name = doc_names[i % len(doc_names)]
                
                # Actualizar progreso
                self.root.after(0, lambda c=i+1, t=doc_count, f=doc_name: 
                              self.update_progress(c, t, f))
                
                self.log_message(f"📄 Procesando {i+1}/{doc_count}: {doc_name}")
                
                # Simular procesamiento del documento
                time.sleep(doc_time)
                
                # Simular éxito o error ocasional
                if random.random() < 0.1:  # 10% de probabilidad de error
                    self.log_message(f"❌ Error simulado procesando {doc_name}")
                else:
                    self.log_message(f"✅ {doc_name} almacenado exitosamente")
            
            # Completar progreso solo si no se detuvo
            if self.storage_running:
                # Completar progreso
                self.root.after(0, lambda: self.update_progress(doc_count, doc_count))
                self.root.after(0, lambda: self.status_label.config(text="¡Almacenamiento completado!"))
                self.root.after(0, lambda: self.current_file_label.config(text=""))
                
                self.log_message("🎉 ¡Almacenamiento completado!")
                self.log_message(f"📊 Total de documentos procesados: {doc_count}")
                
                messagebox.showinfo("Completado", 
                                  f"¡Almacenamiento simulado completado!\n\n"
                                  f"Documentos procesados: {doc_count}")
            else:
                # Almacenamiento detenido
                self.root.after(0, lambda: self.status_label.config(text="Almacenamiento detenido"))
                self.root.after(0, lambda: self.current_file_label.config(text=""))
            
        except Exception as e:
            self.log_message(f"💥 Error general: {str(e)}")
            self.root.after(0, lambda: self.status_label.config(text="Error durante el almacenamiento"))
            messagebox.showerror("Error", f"Error durante el almacenamiento:\n{str(e)}")
        
        finally:
            # Restaurar interfaz
            self.storage_running = False
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
    
    def clear_logs(self):
        """Limpiar los logs"""
        self.logs_text.delete(1.0, tk.END)

def main():
    """Función principal"""
    root = tk.Tk()
    app = TestStorageProgressGUI(root)
    
    # Centrar la ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 