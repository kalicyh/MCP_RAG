#!/usr/bin/env python3
"""
Script de inicio para Bulk Ingest GUI
Funciona sin importaciones relativas
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def setup_paths():
    """Configura los paths para las importaciones"""
    # Obtener rutas absolutas
    script_path = Path(__file__).resolve()
    gui_dir = script_path.parent
    project_root = gui_dir.parent
    
    # Añadir al path de Python
    sys.path.insert(0, str(gui_dir))
    sys.path.insert(0, str(project_root))
    
    return gui_dir, project_root

def create_simple_app():
    """Crea una aplicación simple para probar que todo funciona"""
    print("🚀 Creando aplicación simple...")
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Bulk Ingest GUI - Prueba")
    root.geometry("800x600")
    
    # Frame principal
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Título
    title_label = ttk.Label(main_frame, text="Bulk Ingest GUI", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    # Información
    info_text = """
    ✅ Aplicación iniciada correctamente
    
    📁 Directorio GUI: {gui_dir}
    📁 Directorio Proyecto: {project_root}
    🔍 rag_core.py encontrado: {rag_core_exists}
    
    🎯 Próximos pasos:
    1. Probar importación de rag_core.py
    2. Crear servicios y controladores
    3. Implementar interfaz completa
    """.format(
        gui_dir=gui_dir,
        project_root=project_root,
        rag_core_exists=rag_core_path.exists()
    )
    
    info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=20)
    
    # Botón para probar rag_core
    def test_rag_core():
        try:
            import rag_core
            messagebox.showinfo("Éxito", "✅ rag_core.py importado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error importando rag_core: {e}")
    
    test_button = ttk.Button(main_frame, text="Probar rag_core.py", command=test_rag_core)
    test_button.pack(pady=10)
    
    # Botón para cerrar
    def close_app():
        root.destroy()
    
    close_button = ttk.Button(main_frame, text="Cerrar", command=close_app)
    close_button.pack(pady=10)
    
    return root

def main():
    """Función principal"""
    global gui_dir, project_root, rag_core_path
    
    print("🚀 Iniciando Bulk Ingest GUI...")
    
    # Configurar paths
    gui_dir, project_root = setup_paths()
    rag_core_path = project_root / "rag_core.py"
    
    print(f"✅ Entorno configurado:")
    print(f"   📁 GUI Directory: {gui_dir}")
    print(f"   📁 Project Root: {project_root}")
    print(f"   🔍 rag_core.py: {rag_core_path.exists()}")
    
    if not rag_core_path.exists():
        print("❌ Error: No se encontró rag_core.py")
        sys.exit(1)
    
    try:
        # Crear aplicación simple
        root = create_simple_app()
        
        print("✅ Aplicación creada exitosamente")
        print("🎉 Iniciando interfaz gráfica...")
        
        # Ejecutar aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"💥 Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 