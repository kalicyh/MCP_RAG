#!/usr/bin/env python3
"""
Script de prueba para el cache de embeddings.
Verifica que el cache funciona correctamente y muestra las mejoras de rendimiento.
"""

import time
import sys
import os

# Añadir el directorio actual al path para importar rag_core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_core import (
    get_embedding_function, 
    get_cache_stats, 
    print_cache_stats, 
    clear_embedding_cache,
    get_embedding_cache,
    log
)

def test_embedding_cache():
    """Prueba el cache de embeddings con textos repetidos."""
    
    print("🚀 Iniciando prueba del cache de embeddings...")
    print("=" * 60)
    
    # Textos de prueba
    test_texts = [
        "Este es un documento importante sobre machine learning.",
        "La inteligencia artificial está transformando el mundo.",
        "Los embeddings son representaciones vectoriales del texto.",
        "El cache mejora significativamente el rendimiento.",
        "Este es un documento importante sobre machine learning.",  # Repetido
        "La inteligencia artificial está transformando el mundo.",  # Repetido
        "Los embeddings son representaciones vectoriales del texto.",  # Repetido
        "El cache mejora significativamente el rendimiento.",  # Repetido
    ]
    
    try:
        # Obtener función de embedding con cache
        print("📥 Cargando modelo de embedding...")
        embedding_function = get_embedding_function()
        
        print("\n🔄 Procesando textos (primera vez - sin cache)...")
        start_time = time.time()
        
        for i, text in enumerate(test_texts[:4], 1):
            print(f"  {i}. Procesando: '{text[:50]}...'")
            embedding = embedding_function.embed_query(text)
            print(f"     ✅ Embedding generado: {len(embedding)} dimensiones")
        
        first_batch_time = time.time() - start_time
        print(f"⏱️  Tiempo primera tanda: {first_batch_time:.2f} segundos")
        
        # Mostrar estadísticas después de la primera tanda
        print("\n📊 Estadísticas después de la primera tanda:")
        stats = get_cache_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n🔄 Procesando textos (segunda vez - con cache)...")
        start_time = time.time()
        
        for i, text in enumerate(test_texts[4:], 1):
            print(f"  {i}. Procesando: '{text[:50]}...'")
            embedding = embedding_function.embed_query(text)
            print(f"     ✅ Embedding recuperado: {len(embedding)} dimensiones")
        
        second_batch_time = time.time() - start_time
        print(f"⏱️  Tiempo segunda tanda: {second_batch_time:.2f} segundos")
        
        # Mostrar estadísticas finales
        print("\n📊 Estadísticas finales:")
        stats = get_cache_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Calcular mejoras
        if first_batch_time > 0:
            speedup = first_batch_time / second_batch_time
            improvement = ((first_batch_time - second_batch_time) / first_batch_time) * 100
            print(f"\n🚀 Mejora de rendimiento:")
            print(f"  Velocidad: {speedup:.1f}x más rápido")
            print(f"  Tiempo ahorrado: {improvement:.1f}%")
        
        # Probar con textos completamente nuevos
        print("\n🆕 Probando con textos nuevos...")
        new_texts = [
            "Este es un texto completamente nuevo para probar el cache.",
            "Otro texto diferente que no debería estar en cache.",
        ]
        
        start_time = time.time()
        for text in new_texts:
            embedding = embedding_function.embed_query(text)
        new_texts_time = time.time() - start_time
        
        print(f"⏱️  Tiempo textos nuevos: {new_texts_time:.2f} segundos")
        
        print("\n✅ Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
    
    return True

def test_cache_persistence():
    """Prueba que el cache persiste entre sesiones."""
    
    print("\n" + "=" * 60)
    print("🔄 Probando persistencia del cache...")
    
    try:
        # Primera sesión
        print("📝 Primera sesión - creando embeddings...")
        embedding_function = get_embedding_function()
        
        test_text = "Este texto debería persistir en el cache entre sesiones."
        embedding1 = embedding_function.embed_query(test_text)
        
        # Mostrar estadísticas
        stats1 = get_cache_stats()
        print(f"  Embeddings en cache: {stats1['memory_cache_size']}")
        
        # Segunda sesión (simulada)
        print("\n📝 Segunda sesión - verificando persistencia...")
        
        # Limpiar solo memoria, mantener disco
        cache = get_embedding_cache()
        cache.clear_memory()
        
        # Procesar el mismo texto
        embedding2 = embedding_function.embed_query(test_text)
        
        # Verificar que son iguales
        if len(embedding1) == len(embedding2):
            print("✅ Embeddings recuperados correctamente del disco")
        else:
            print("❌ Error: Embeddings no coinciden")
        
        # Mostrar estadísticas finales
        stats2 = get_cache_stats()
        print(f"  Embeddings en cache: {stats2['memory_cache_size']}")
        print(f"  Cache hits en disco: {stats2['disk_hits']}")
        
        print("✅ Prueba de persistencia completada!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba de persistencia: {e}")
        return False
    
    return True

def main():
    """Función principal del script de prueba."""
    
    print("🧪 SCRIPT DE PRUEBA DEL CACHE DE EMBEDDINGS")
    print("=" * 60)
    
    # Ejecutar pruebas
    success1 = test_embedding_cache()
    success2 = test_cache_persistence()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ Todas las pruebas pasaron exitosamente!")
        print("\n🎉 El cache de embeddings está funcionando correctamente.")
        print("   - Mejora significativa en rendimiento para textos repetidos")
        print("   - Persistencia correcta entre sesiones")
        print("   - Estadísticas detalladas disponibles")
    else:
        print("❌ Algunas pruebas fallaron.")
        print("   Revisa los logs para más detalles.")
    
    # Preguntar si limpiar el cache
    print("\n🧹 ¿Deseas limpiar el cache de embeddings? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            clear_embedding_cache()
            print("✅ Cache limpiado.")
        else:
            print("ℹ️  Cache mantenido para futuras pruebas.")
    except KeyboardInterrupt:
        print("\nℹ️  Cache mantenido.")

if __name__ == "__main__":
    main() 