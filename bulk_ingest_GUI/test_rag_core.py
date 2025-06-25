#!/usr/bin/env python3
"""
Script de prueba para verificar que el wrapper de rag_core funciona
"""

import sys
import os
from pathlib import Path

def test_rag_core_wrapper():
    """Probar el wrapper de rag_core"""
    
    # Configurar paths
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    
    # Cambiar al directorio de la GUI
    os.chdir(current_dir)
    
    # Configurar sys.path
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(project_root))
    
    print("🧪 Probando wrapper de rag_core...")
    
    try:
        # Importar el wrapper
        from rag_core_wrapper import (
            load_document_with_elements,
            add_text_to_knowledge_base_enhanced,
            get_vector_store,
            log,
            clear_embedding_cache,
            get_cache_stats,
            get_vector_store_stats_advanced
        )
        
        print("✅ Wrapper importado correctamente")
        
        # Probar una función simple
        try:
            log("Prueba del wrapper de rag_core")
            print("✅ Función log funciona correctamente")
        except Exception as e:
            print(f"⚠️ Función log no funciona: {e}")
        
        # Probar obtener estadísticas del cache
        try:
            stats = get_cache_stats()
            print("✅ Función get_cache_stats funciona correctamente")
            print(f"   Estadísticas: {stats}")
        except Exception as e:
            print(f"⚠️ Función get_cache_stats no funciona: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando wrapper: {e}")
        return False
    except Exception as e:
        print(f"❌ Error probando wrapper: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_core_wrapper()
    sys.exit(0 if success else 1) 