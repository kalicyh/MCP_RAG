#!/usr/bin/env python3
"""
Script de diagnóstico para rag_core
"""

import sys
import os
from pathlib import Path

def debug_rag_core():
    """Diagnosticar problemas con rag_core"""
    
    print("🔍 Diagnóstico de rag_core...")
    
    # Configurar paths
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    
    print(f"📁 Directorio actual: {current_dir}")
    print(f"📁 Directorio proyecto: {project_root}")
    print(f"📁 Directorio MCP src: {mcp_src_dir}")
    print(f"📁 MCP src existe: {mcp_src_dir.exists()}")
    
    # Verificar archivos
    rag_core_path = mcp_src_dir / "rag_core.py"
    utils_config_path = mcp_src_dir / "utils" / "config.py"
    
    print(f"📄 rag_core.py existe: {rag_core_path.exists()}")
    print(f"📄 utils/config.py existe: {utils_config_path.exists()}")
    
    # Configurar path
    if mcp_src_dir.exists():
        sys.path.insert(0, str(mcp_src_dir))
        print(f"✅ Path configurado: {mcp_src_dir}")
    
    # Probar importación de utils.config
    try:
        # Importar directamente desde el servidor MCP
        import utils.config
        print("✅ utils.config importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando utils.config: {e}")
    
    # Probar importación de rag_core
    try:
        import rag_core
        print("✅ rag_core importado correctamente")
        
        # Probar funciones específicas
        try:
            from rag_core import load_document_with_elements
            print("✅ load_document_with_elements importado")
        except ImportError as e:
            print(f"❌ Error importando load_document_with_elements: {e}")
        
        try:
            from rag_core import log
            print("✅ log importado")
            log("Prueba de diagnóstico")
        except ImportError as e:
            print(f"❌ Error importando log: {e}")
        
    except ImportError as e:
        print(f"❌ Error importando rag_core: {e}")
        print(f"   sys.path: {sys.path[:5]}...")  # Mostrar solo los primeros 5 elementos

if __name__ == "__main__":
    debug_rag_core() 