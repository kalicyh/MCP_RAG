#!/usr/bin/env python3
"""
Script de lanzamiento para Bulk Ingest GUI
Ejecuta la aplicación desde cualquier ubicación
"""

import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

# Verificar que rag_core.py esté disponible
rag_core_path = project_root / "rag_core.py"
if not rag_core_path.exists():
    print("❌ Error: No se encontró rag_core.py en el directorio padre")
    print(f"Buscando en: {rag_core_path}")
    sys.exit(1)

def main():
    """Función principal de lanzamiento"""
    try:
        print("🚀 Iniciando Bulk Ingest GUI...")
        print(f"📁 Directorio actual: {current_dir}")
        print(f"📁 Directorio padre: {project_root}")
        print(f"🔍 rag_core.py encontrado: {rag_core_path.exists()}")
        
        # Importar y ejecutar la aplicación
        from main import main as run_app
        run_app()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 