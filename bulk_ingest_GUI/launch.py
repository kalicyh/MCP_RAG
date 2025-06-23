#!/usr/bin/env python3
"""
Script de lanzamiento alternativo para Bulk Ingest GUI
Funciona desde cualquier ubicación
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configura el entorno para la aplicación"""
    # Obtener la ruta del script actual
    script_path = Path(__file__).resolve()
    gui_dir = script_path.parent
    project_root = gui_dir.parent
    
    # Añadir directorios al path
    sys.path.insert(0, str(gui_dir))
    sys.path.insert(0, str(project_root))
    
    # Verificar que rag_core.py existe
    rag_core_path = project_root / "rag_core.py"
    if not rag_core_path.exists():
        print(f"❌ Error: No se encontró rag_core.py en {rag_core_path}")
        return False
    
    print(f"✅ Entorno configurado:")
    print(f"   📁 GUI Directory: {gui_dir}")
    print(f"   📁 Project Root: {project_root}")
    print(f"   🔍 rag_core.py: {rag_core_path.exists()}")
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando Bulk Ingest GUI...")
    
    # Configurar entorno
    if not setup_environment():
        sys.exit(1)
    
    try:
        # Importar módulos
        print("📦 Importando módulos...")
        
        # Importar rag_core primero
        import rag_core
        print("✅ rag_core importado correctamente")
        
        # Importar servicios
        from services.configuration_service import ConfigurationService
        from services.document_service import DocumentService
        print("✅ Servicios importados correctamente")
        
        # Importar controladores
        from controllers.main_controller import MainController
        print("✅ Controladores importados correctamente")
        
        # Importar vistas
        from views.main_view import MainView
        print("✅ Vistas importadas correctamente")
        
        # Importar tkinter
        import tkinter as tk
        print("✅ Tkinter importado correctamente")
        
        # Crear aplicación
        print("🏗️ Creando aplicación...")
        
        # Crear ventana principal
        root = tk.Tk()
        root.title("Bulk Ingest GUI - Sistema RAG Modular")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        
        # Crear servicios
        config_service = ConfigurationService()
        
        # Crear controlador
        controller = MainController(root, config_service)
        
        # Crear vista principal
        main_view = MainView(root, controller)
        
        # Configurar cierre
        def on_closing():
            try:
                controller.cleanup()
                root.destroy()
            except Exception as e:
                print(f"Error durante el cierre: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ Aplicación creada exitosamente")
        print("🎉 Iniciando interfaz gráfica...")
        
        # Ejecutar aplicación
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\n🔧 Soluciones:")
        print("1. Verifica que estés en el directorio correcto")
        print("2. Instala las dependencias: pip install -r requirements.txt")
        print("3. Verifica que rag_core.py esté en el directorio padre")
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 