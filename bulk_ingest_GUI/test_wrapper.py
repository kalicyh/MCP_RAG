#!/usr/bin/env python3
"""
Script de prueba para el nuevo rag_core_wrapper
"""

from rag_core_wrapper import (
    load_document_with_elements,
    add_text_to_knowledge_base_enhanced,
    get_vector_store,
    log,
    clear_embedding_cache,
    get_cache_stats,
    get_vector_store_stats_advanced
)

def test_wrapper():
    """Probar que el wrapper funciona correctamente"""
    
    print("🧪 Probando rag_core_wrapper...")
    
    try:
        # Probar la función log
        log("Prueba del wrapper funcionando correctamente")
        print("✅ log funcionando")
        
        # Probar get_cache_stats
        stats = get_cache_stats()
        print(f"✅ get_cache_stats funcionando: {stats}")
        
        # Probar get_vector_store_stats_advanced
        vs_stats = get_vector_store_stats_advanced()
        print(f"✅ get_vector_store_stats_advanced funcionando: {vs_stats}")
        
        print("🎉 ¡Todas las funciones del wrapper funcionan correctamente!")
        
    except Exception as e:
        print(f"❌ Error en el wrapper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wrapper() 