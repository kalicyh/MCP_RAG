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

# Importar Rich para mejorar la salida en consola
from rich import print
from rich.panel import Panel


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
    
    print(f"[bold green]✅ Entorno configurado para {APP_NAME} v{VERSION}[/bold green]")


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
                print(Panel(f"[bold red]Error durante el cierre: {e}[/bold red]", title="[red]Error[/red]"))
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        return root, controller, main_view
        
    except Exception as e:
        print(Panel(f"[bold red]❌ Error creando la aplicación: {e}[/bold red]", title="[red]Error[/red]"))
        raise


def main():
    """Función principal que lanza la aplicación"""
    try:
        print(Panel(f"[bold blue]🚀 Iniciando {APP_NAME} v{VERSION}[/bold blue]", title="[cyan]Inicio[/cyan]"))
        print("[cyan]" + "=" * 50 + "[/cyan]")
        
        # Configurar entorno
        setup_environment()
        
        # Crear aplicación
        root, controller, main_view = create_application()
        
        print("[bold green]✅ Aplicación creada exitosamente[/bold green]")
        print("[bold magenta]📋 Funcionalidades disponibles:[/bold magenta]")
        print("[yellow]   • Procesamiento de documentos con rag_core.py[/yellow]")
        print("[yellow]   • Chunking semántico avanzado[/yellow]")
        print("[yellow]   • Cache de embeddings optimizado[/yellow]")
        print("[yellow]   • Almacenamiento en base vectorial[/yellow]")
        print("[yellow]   • Exportar/importar listas de documentos[/yellow]")
        print("[yellow]   • Filtros y búsqueda[/yellow]")
        print("[cyan]" + "=" * 50 + "[/cyan]")
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        print(Panel(f"[bold red]💥 Error fatal en la aplicación: {e}[/bold red]", title="[red]Error Fatal[/red]"))
        print("[red]Detalles del error:[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 