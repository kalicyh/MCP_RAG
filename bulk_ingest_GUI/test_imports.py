#!/usr/bin/env python3
"""
Script de prueba para verificar importaciones de Bulk Ingest GUI
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Probar todas las importaciones necesarias"""
    
    # Configurar paths
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    
    # Cambiar al directorio de la GUI
    os.chdir(current_dir)
    
    # Configurar sys.path
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(project_root))
    if mcp_src_dir.exists():
        sys.path.insert(0, str(mcp_src_dir))
    
    print("🧪 Probando importaciones...")
    
    # Probar importaciones de la GUI
    try:
        from services.configuration_service import ConfigurationService
        print("✅ ConfigurationService importado")
    except Exception as e:
        print(f"❌ Error importando ConfigurationService: {e}")
        return False
    
    try:
        from services.document_service import DocumentService
        print("✅ DocumentService importado")
    except Exception as e:
        print(f"❌ Error importando DocumentService: {e}")
        return False
    
    try:
        from controllers.main_controller import MainController
        print("✅ MainController importado")
    except Exception as e:
        print(f"❌ Error importando MainController: {e}")
        return False
    
    try:
        from views.main_view import MainView
        print("✅ MainView importado")
    except Exception as e:
        print(f"❌ Error importando MainView: {e}")
        return False
    
    try:
        from models.document_model import DocumentPreview
        print("✅ DocumentPreview importado")
    except Exception as e:
        print(f"❌ Error importando DocumentPreview: {e}")
        return False
    
    # Probar importación del núcleo RAG
    try:
        from mcp_server_organized.src.rag_core import log
        print("✅ Núcleo RAG importado desde estructura modular")
    except Exception as e:
        try:
            from rag_core import log
            print("✅ Núcleo RAG importado desde estructura original")
        except Exception as e2:
            print(f"❌ Error importando núcleo RAG: {e2}")
            return False
    
    # Probar Tkinter
    try:
        import tkinter as tk
        print("✅ Tkinter importado")
    except Exception as e:
        print(f"❌ Error importando Tkinter: {e}")
        return False
    
    print("🎉 Todas las importaciones funcionan correctamente!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 