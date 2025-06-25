"""
Script de prueba para verificar la integración entre la GUI y el servidor MCP
Verifica que ambos componentes usen la misma base de datos
"""

import sys
import os
from pathlib import Path

# Configurar paths
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
mcp_src_dir = project_root / "mcp_server_organized" / "src"

# Añadir el directorio del servidor MCP al path
if str(mcp_src_dir) not in sys.path:
    sys.path.insert(0, str(mcp_src_dir))

def test_server_integration():
    """Prueba que la GUI use la misma base de datos que el servidor MCP"""
    
    print("🧪 Probando integración entre GUI y servidor MCP...")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración del servidor MCP
        print("\n1. Verificando configuración del servidor MCP...")
        from utils.config import Config
        
        print(f"   ✅ Configuración cargada desde: {mcp_src_dir}")
        print(f"   📁 Directorio de datos: {Config.CONVERTED_DOCS_DIR}")
        print(f"   📊 Base vectorial: {Config.VECTOR_STORE_DIR}")
        print(f"   🧠 Cache de embeddings: {Config.EMBEDDING_CACHE_DIR}")
        
        # 2. Verificar que los directorios existan
        print("\n2. Verificando directorios del servidor MCP...")
        Config.ensure_directories()
        print("   ✅ Directorios del servidor MCP creados/verificados")
        
        # 3. Verificar que rag_core funcione desde la GUI
        print("\n3. Verificando rag_core desde la GUI...")
        import bulk_ingest_GUI.rag_core_wrapper as rag_wrapper
        
        # Probar importación
        functions = rag_wrapper.get_rag_functions()
        print("   ✅ Funciones de rag_core importadas correctamente")
        
        # 4. Verificar que ambos usen la misma base de datos
        print("\n4. Verificando consistencia de base de datos...")
        
        # Obtener base de datos desde el servidor MCP
        from rag_core import get_vector_store
        server_vector_store = get_vector_store()
        print("   ✅ Base de datos del servidor MCP obtenida")
        
        # Obtener base de datos desde la GUI
        gui_vector_store = rag_wrapper.get_vector_store()
        print("   ✅ Base de datos de la GUI obtenida")
        
        # Verificar que sean la misma instancia
        if server_vector_store == gui_vector_store:
            print("   ✅ Ambos componentes usan la misma base de datos")
        else:
            print("   ❌ Los componentes usan bases de datos diferentes")
            return False
        
        # 5. Verificar configuración de directorios
        print("\n5. Verificando configuración de directorios...")
        
        # Verificar que la GUI use los directorios del servidor
        from bulk_ingest_GUI.gui_utils.constants import CONVERTED_DOCS_DIR, VECTOR_STORE_DIR, EMBEDDING_CACHE_DIR
        
        expected_docs_dir = str(project_root / "mcp_server_organized" / "data" / "documents")
        expected_vector_dir = str(project_root / "mcp_server_organized" / "data" / "vector_store")
        expected_cache_dir = str(project_root / "mcp_server_organized" / "embedding_cache")
        
        if CONVERTED_DOCS_DIR == expected_docs_dir:
            print("   ✅ GUI usa directorio de documentos del servidor")
        else:
            print(f"   ❌ GUI usa directorio incorrecto: {CONVERTED_DOCS_DIR}")
            print(f"      Esperado: {expected_docs_dir}")
            return False
        
        if VECTOR_STORE_DIR == expected_vector_dir:
            print("   ✅ GUI usa directorio de base vectorial del servidor")
        else:
            print(f"   ❌ GUI usa directorio incorrecto: {VECTOR_STORE_DIR}")
            print(f"      Esperado: {expected_vector_dir}")
            return False
        
        if EMBEDDING_CACHE_DIR == expected_cache_dir:
            print("   ✅ GUI usa directorio de cache del servidor")
        else:
            print(f"   ❌ GUI usa directorio incorrecto: {EMBEDDING_CACHE_DIR}")
            print(f"      Esperado: {expected_cache_dir}")
            return False
        
        # 6. Verificar que el servicio de documentos funcione
        print("\n6. Verificando servicio de documentos...")
        from bulk_ingest_GUI.services.document_service import DocumentService
        from bulk_ingest_GUI.services.configuration_service import ConfigurationService
        
        config_service = ConfigurationService()
        doc_service = DocumentService(config_service)
        print("   ✅ Servicio de documentos inicializado correctamente")
        
        # 7. Verificar estadísticas de base de datos
        print("\n7. Verificando estadísticas de base de datos...")
        
        # Desde el servidor
        from rag_core import get_vector_store_stats
        server_stats = get_vector_store_stats(server_vector_store)
        print(f"   📊 Estadísticas del servidor: {server_stats.get('total_documents', 0)} documentos")
        
        # Desde la GUI
        gui_stats = doc_service.get_database_statistics()
        if 'error' not in gui_stats:
            print(f"   📊 Estadísticas de la GUI: {gui_stats.get('total_documents', 0)} documentos")
            
            # Verificar que las estadísticas coincidan
            if server_stats.get('total_documents') == gui_stats.get('total_documents'):
                print("   ✅ Estadísticas coinciden entre servidor y GUI")
            else:
                print("   ❌ Estadísticas no coinciden entre servidor y GUI")
                return False
        else:
            print(f"   ❌ Error obteniendo estadísticas de la GUI: {gui_stats['error']}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ¡Todas las pruebas pasaron! La GUI está correctamente integrada con el servidor MCP")
        print("✅ Ambos componentes usan la misma base de datos")
        print("✅ Los directorios están configurados correctamente")
        print("✅ Las estadísticas coinciden entre ambos componentes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_integration()
    sys.exit(0 if success else 1) 