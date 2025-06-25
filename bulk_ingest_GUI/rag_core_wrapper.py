"""
Wrapper para rag_core que maneja las importaciones correctamente
para la integración con Bulk Ingest GUI

Este wrapper asegura que la GUI use la misma base de datos que el servidor MCP
para mantener consistencia de datos entre ambos componentes.
"""

import sys
import os
from pathlib import Path

def setup_rag_core_environment():
    """Configura el entorno para que rag_core funcione correctamente"""
    
    # Obtener rutas
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    
    # Configurar sys.path para que rag_core pueda importar utils.config
    if mcp_src_dir.exists():
        # Añadir el directorio src del servidor MCP al path
        if str(mcp_src_dir) not in sys.path:
            sys.path.insert(0, str(mcp_src_dir))
        
        # También añadir el directorio padre para importaciones relativas
        mcp_parent = mcp_src_dir.parent
        if str(mcp_parent) not in sys.path:
            sys.path.insert(0, str(mcp_parent))
        
        print(f"✅ Entorno configurado para rag_core: {mcp_src_dir}")
        return True
    else:
        print(f"❌ No se encontró el directorio del servidor MCP: {mcp_src_dir}")
        return False

def import_rag_core_functions():
    """Importa las funciones necesarias de rag_core"""
    
    if not setup_rag_core_environment():
        raise ImportError("No se pudo configurar el entorno para rag_core")
    
    try:
        # Guardar el path actual
        original_path = sys.path.copy()
        
        # Configurar el path específicamente para rag_core
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent.resolve()
        mcp_src_dir = project_root / "mcp_server_organized" / "src"
        
        # Limpiar y configurar el path temporalmente
        temp_path = [str(mcp_src_dir), str(mcp_src_dir.parent)]
        temp_path.extend(original_path)
        sys.path = temp_path
        
        # Cambiar al directorio del servidor MCP temporalmente
        original_cwd = os.getcwd()
        os.chdir(mcp_src_dir)
        
        try:
            # Importar configuración del servidor MCP
            from utils.config import Config
            
            # Configurar variables de entorno para usar la misma base de datos
            os.environ['RAG_DATA_DIR'] = str(project_root / "mcp_server_organized" / "data")
            os.environ['RAG_VECTOR_STORE_DIR'] = str(project_root / "mcp_server_organized" / "data" / "vector_store")
            os.environ['RAG_EMBEDDING_CACHE_DIR'] = str(project_root / "mcp_server_organized" / "embedding_cache")
            
            # NO llamar a Config.ensure_directories() desde la GUI
            # Los directorios ya deben existir en el servidor MCP
            # Config.ensure_directories()
            
            # Intentar importar desde la estructura modular
            from rag_core import (
                load_document_with_elements,
                add_text_to_knowledge_base_enhanced,
                get_vector_store,
                log,
                clear_embedding_cache,
                get_cache_stats,
                get_vector_store_stats_advanced
            )
            
            print("✅ Funciones de rag_core importadas desde estructura modular")
            print(f"✅ Usando base de datos del servidor MCP: {Config.VECTOR_STORE_DIR}")
            return {
                'load_document_with_elements': load_document_with_elements,
                'add_text_to_knowledge_base_enhanced': add_text_to_knowledge_base_enhanced,
                'get_vector_store': get_vector_store,
                'log': log,
                'clear_embedding_cache': clear_embedding_cache,
                'get_cache_stats': get_cache_stats,
                'get_vector_store_stats_advanced': get_vector_store_stats_advanced
            }
        finally:
            # Restaurar el directorio de trabajo original
            os.chdir(original_cwd)
            # Restaurar el path original
            sys.path = original_path
            
    except ImportError as e:
        print(f"❌ Error importando desde estructura modular: {e}")
        
        # Fallback: intentar importar desde rag_core.py original
        try:
            from rag_core import (
                load_document_with_elements,
                add_text_to_knowledge_base_enhanced,
                get_vector_store,
                log,
                clear_embedding_cache,
                get_cache_stats,
                get_vector_store_stats_advanced
            )
            print("✅ Funciones de rag_core importadas desde estructura original")
            return {
                'load_document_with_elements': load_document_with_elements,
                'add_text_to_knowledge_base_enhanced': add_text_to_knowledge_base_enhanced,
                'get_vector_store': get_vector_store,
                'log': log,
                'clear_embedding_cache': clear_embedding_cache,
                'get_cache_stats': get_cache_stats,
                'get_vector_store_stats_advanced': get_vector_store_stats_advanced
            }
        except ImportError as e2:
            print(f"❌ Error importando desde estructura original: {e2}")
            raise ImportError(f"No se pudo importar rag_core: {e2}")

# Variables globales para las funciones
_rag_functions = None
_import_attempted = False

def get_rag_functions():
    """Obtiene las funciones de rag_core, importándolas si es necesario"""
    global _rag_functions, _import_attempted
    
    if _rag_functions is not None:
        return _rag_functions
    
    if _import_attempted:
        raise ImportError("rag_core no está disponible")
    
    _import_attempted = True
    
    try:
        _rag_functions = import_rag_core_functions()
        return _rag_functions
    except ImportError as e:
        print(f"❌ Error importando rag_core: {e}")
        raise

# Funciones wrapper que importan dinámicamente
def load_document_with_elements(*args, **kwargs):
    """Wrapper para load_document_with_elements"""
    functions = get_rag_functions()
    return functions['load_document_with_elements'](*args, **kwargs)

def add_text_to_knowledge_base_enhanced(*args, **kwargs):
    """Wrapper para add_text_to_knowledge_base_enhanced"""
    functions = get_rag_functions()
    return functions['add_text_to_knowledge_base_enhanced'](*args, **kwargs)

def get_vector_store(*args, **kwargs):
    """Wrapper para get_vector_store - Usa la misma base de datos que el servidor MCP"""
    functions = get_rag_functions()
    return functions['get_vector_store'](*args, **kwargs)

def log(*args, **kwargs):
    """Wrapper para log"""
    functions = get_rag_functions()
    return functions['log'](*args, **kwargs)

def clear_embedding_cache(*args, **kwargs):
    """Wrapper para clear_embedding_cache"""
    functions = get_rag_functions()
    return functions['clear_embedding_cache'](*args, **kwargs)

def get_cache_stats(*args, **kwargs):
    """Wrapper para get_cache_stats"""
    functions = get_rag_functions()
    return functions['get_cache_stats'](*args, **kwargs)

def get_vector_store_stats_advanced(*args, **kwargs):
    """Wrapper para get_vector_store_stats_advanced"""
    functions = get_rag_functions()
    return functions['get_vector_store_stats_advanced'](*args, **kwargs)

def optimize_vector_store(*args, **kwargs):
    print(">>> [Wrapper] Llamando a optimize_vector_store")
    if not setup_rag_core_environment():
        raise ImportError("No se pudo configurar el entorno para rag_core")
    try:
        import importlib
        rag_core = importlib.import_module("rag_core")
        result = rag_core.optimize_vector_store(*args, **kwargs)
        print(f">>> [Wrapper] Resultado de optimize_vector_store: {result}")
        return result
    except Exception as e:
        print(f"❌ Error llamando a optimize_vector_store: {e}")
        return {"status": "error", "message": str(e)} 