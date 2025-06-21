#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del resumen de selección
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class TestSummaryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Test - Resumen de Selección")
        self.root.geometry("600x400")
        
        # Simular documentos procesados
        self.processed_documents = []
        self.create_test_documents()
        
        # Variables del resumen
        self.summary_vars = {
            'total_processed': tk.StringVar(value="0"),
            'selected_for_storage': tk.StringVar(value="0"),
            'not_selected': tk.StringVar(value="0"),
            'total_size': tk.StringVar(value="0 KB"),
            'selected_size': tk.StringVar(value="0 KB")
        }
        
        self.create_widgets()
        self.update_summary()
    
    def create_test_documents(self):
        """Crear documentos de prueba"""
        test_docs = [
            ("documento1.pdf", "Contenido del primer documento con bastante texto para probar el cálculo de tamaño."),
            ("documento2.docx", "Segundo documento con contenido diferente y más largo para verificar el resumen."),
            ("documento3.txt", "Tercer documento más corto."),
            ("documento4.pdf", "Cuarto documento con contenido extenso para probar el cálculo de tamaños en KB."),
            ("documento5.xlsx", "Quinto documento con datos tabulares convertidos a texto.")
        ]
        
        for name, content in test_docs:
            doc = type('Document', (), {
                'original_name': name,
                'markdown_content': content,
                'selected': tk.BooleanVar(value=True)
            })()
            self.processed_documents.append(doc)
    
    def create_widgets(self):
        """Crear widgets de prueba"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🧪 Test - Resumen de Selección", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Sección de resumen
        summary_frame = ttk.LabelFrame(main_frame, text="📊 Resumen de Selección", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
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
        
        # Lista de documentos de prueba
        docs_frame = ttk.LabelFrame(main_frame, text="📋 Documentos de Prueba", padding="10")
        docs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Lista
        self.documents_listbox = tk.Listbox(docs_frame)
        self.documents_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.update_documents_list()
        
        # Botones de control
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack()
        
        ttk.Button(buttons_frame, text="✅ Seleccionar Todos", 
                  command=self.select_all_documents).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Deseleccionar Todos", 
                  command=self.deselect_all_documents).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🔄 Actualizar Resumen", 
                  command=self.update_summary).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🎲 Cambiar Aleatorio", 
                  command=self.random_selection).pack(side=tk.LEFT)
    
    def update_documents_list(self):
        """Actualizar la lista de documentos"""
        self.documents_listbox.delete(0, tk.END)
        for doc in self.processed_documents:
            status = "✅" if doc.selected.get() else "❌"
            self.documents_listbox.insert(tk.END, f"{status} {doc.original_name}")
    
    def select_all_documents(self):
        """Seleccionar todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(True)
        self.update_documents_list()
        self.update_summary()
    
    def deselect_all_documents(self):
        """Deseleccionar todos los documentos"""
        for doc in self.processed_documents:
            doc.selected.set(False)
        self.update_documents_list()
        self.update_summary()
    
    def random_selection(self):
        """Cambiar selección aleatoriamente"""
        import random
        for doc in self.processed_documents:
            doc.selected.set(random.choice([True, False]))
        self.update_documents_list()
        self.update_summary()
    
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

def main():
    """Función principal"""
    root = tk.Tk()
    app = TestSummaryGUI(root)
    
    # Centrar la ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 