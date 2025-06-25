#!/usr/bin/env python3
"""
Script de lanzamiento para Bulk Ingest GUI
Ejecuta la aplicación desde cualquier ubicación
Configurado para la nueva estructura modular del servidor MCP
"""

import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()

# Cambiar al directorio de la GUI para que las importaciones relativas funcionen
os.chdir(current_dir)

# Añadir directorios al path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

# Configurar path para el servidor MCP ANTES de cualquier importación
mcp_src_dir = project_root / "mcp_server_organized" / "src"
if mcp_src_dir.exists():
    sys.path.insert(0, str(mcp_src_dir))
    print(f"✅ Path del servidor MCP configurado: {mcp_src_dir}")

# Verificar que el núcleo RAG esté disponible en la nueva estructura
rag_core_found = False
rag_core_path = None

# Buscar en la nueva estructura modular
modular_rag_core = project_root / "mcp_server_organized" / "src" / "rag_core.py"
if modular_rag_core.exists():
    rag_core_found = True
    rag_core_path = modular_rag_core
    print(f"✅ Núcleo RAG encontrado en estructura modular: {rag_core_path}")
else:
    # Fallback: buscar en la estructura original
    original_rag_core = project_root / "rag_core.py"
    if original_rag_core.exists():
        rag_core_found = True
        rag_core_path = original_rag_core
        print(f"⚠️ Núcleo RAG encontrado en estructura original: {rag_core_path}")
    else:
        print("❌ Error: No se encontró el núcleo RAG")
        print(f"Buscando en:")
        print(f"  - Estructura modular: {modular_rag_core}")
        print(f"  - Estructura original: {original_rag_core}")
        sys.exit(1)

def main():
    """Función principal de lanzamiento"""
    try:
        print("🚀 Iniciando Bulk Ingest GUI...")
        print(f"📁 Directorio actual: {os.getcwd()}")
        print(f"📁 Directorio padre: {project_root}")
        print(f"🔍 Núcleo RAG: {rag_core_path}")
        
        # Importar y ejecutar la aplicación de forma más directa
        print("📦 Importando módulos...")
        
        # Importar módulos uno por uno para identificar el problema
        print("  - Importando main...")
        import main
        
        print("  - Ejecutando main.main()...")
        main.main()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas:")
        print("pip install -r requirements.txt")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 