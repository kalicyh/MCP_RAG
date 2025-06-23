"""
Archivo principal de la aplicación Bulk Ingest GUI
Lanza la aplicación y conecta todos los componentes
"""

import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

import tkinter as tk
from services.configuration_service import ConfigurationService
from controllers.main_controller import MainController
from views.main_view import MainView
from utils.constants import APP_NAME, VERSION
from utils.exceptions import BulkIngestError


def setup_environment():
    """Configura el entorno de la aplicación"""
    # Crear directorios necesarios si no existen
    directories = [
        "converted_docs",
        "embedding_cache",
        "rag_mcp_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print(f"✅ Entorno configurado para {APP_NAME} v{VERSION}")


def create_application():
    """Crea y configura la aplicación principal"""
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Configurar la ventana
        root.title(f"{APP_NAME} v{VERSION}")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        
        # Configurar icono si existe
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                root.iconbitmap(icon_path)
            except:
                pass  # Ignorar si no se puede cargar el icono
        
        # Crear servicios
        config_service = ConfigurationService()
        
        # Crear controlador
        controller = MainController(root, config_service)
        
        # Crear vista principal
        main_view = MainView(root, controller)
        
        # Configurar cierre de ventana
        def on_closing():
            try:
                controller.cleanup()
                root.destroy()
            except Exception as e:
                print(f"Error durante el cierre: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        return root, controller, main_view
        
    except Exception as e:
        print(f"❌ Error creando la aplicación: {e}")
        raise


def main():
    """Función principal que lanza la aplicación"""
    try:
        print(f"🚀 Iniciando {APP_NAME} v{VERSION}")
        print("=" * 50)
        
        # Configurar entorno
        setup_environment()
        
        # Crear aplicación
        root, controller, main_view = create_application()
        
        print("✅ Aplicación creada exitosamente")
        print("📋 Funcionalidades disponibles:")
        print("   • Procesamiento de documentos con rag_core.py")
        print("   • Chunking semántico avanzado")
        print("   • Cache de embeddings optimizado")
        print("   • Almacenamiento en base vectorial")
        print("   • Exportar/importar listas de documentos")
        print("   • Filtros y búsqueda")
        print("=" * 50)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        print(f"💥 Error fatal en la aplicación: {e}")
        print("Detalles del error:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 