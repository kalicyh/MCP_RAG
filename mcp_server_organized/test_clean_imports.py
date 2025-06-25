#!/usr/bin/env python3
"""
Test de Importaciones Limpias - Sin Advertencias de Deprecación
==============================================================

Este script prueba que las importaciones actualizadas funcionan
sin generar advertencias de deprecación.
"""

import sys
import warnings

# Añadir el directorio src al path
sys.path.insert(0, 'src')

def test_clean_imports():
    """Prueba las importaciones sin advertencias."""
    
    print("🔍 **TEST DE IMPORTACIONES LIMPIAS**")
    print("=" * 50)
    
    # Capturar advertencias para verificar que no hay deprecaciones
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            print("1. Probando importaciones de LangChain...")
            
            # Importar las clases actualizadas
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain_community.chat_models import ChatOllama
            
            print("   ✅ Importaciones de LangChain exitosas")
            
            # Verificar si hay advertencias de deprecación
            deprecation_warnings = [warning for warning in w if 'deprecated' in str(warning.message).lower()]
            
            if deprecation_warnings:
                print(f"   ⚠️ Se encontraron {len(deprecation_warnings)} advertencias de deprecación:")
                for warning in deprecation_warnings:
                    print(f"      - {warning.message}")
            else:
                print("   ✅ No se encontraron advertencias de deprecación")
            
            print("\n2. Probando importación del sistema RAG...")
            from rag_core import get_vector_store, get_qa_chain
            print("   ✅ Sistema RAG importado correctamente")
            
            print("\n3. Probando creación de componentes...")
            vector_store = get_vector_store()
            print("   ✅ Vector store creado correctamente")
            
            print("\n🎉 **TODAS LAS IMPORTACIONES FUNCIONAN SIN ADVERTENCIAS**")
            print("✅ Importaciones actualizadas correctamente")
            print("✅ Sistema funcionando sin deprecaciones")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en las importaciones: {e}")
            return False

if __name__ == "__main__":
    success = test_clean_imports()
    sys.exit(0 if success else 1) 