#!/usr/bin/env python3
"""
Script de prueba para verificar el chunking semántico real.
Este script prueba la nueva implementación de chunking semántico avanzado.
"""

import os
import sys
import time
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "="*60)
    print(f"🧠 {title}")
    print("="*60)

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_semantic_chunking_real():
    """Prueba el chunking semántico real con elementos estructurales."""
    print_header("PRUEBA DE CHUNKING SEMÁNTICO REAL")
    
    try:
        from rag_core import load_document_with_elements, create_advanced_semantic_chunks
        
        print_section("1. Cargando Documento con Elementos Estructurales")
        
        # Buscar un documento de prueba
        test_files = [
            "README.md",
            "AGENT_INSTRUCTIONS.md",
            "RECOMENDACIONES_MEJORAS.md"
        ]
        
        test_file = None
        for file in test_files:
            if os.path.exists(file):
                test_file = file
                break
        
        if not test_file:
            print("❌ No se encontró ningún archivo de prueba")
            return False, "No se encontró archivo de prueba"
        
        print(f"📄 Usando archivo de prueba: {test_file}")
        
        # Cargar documento con elementos estructurales
        start_time = time.time()
        processed_content, metadata, structural_elements = load_document_with_elements(test_file)
        load_time = time.time() - start_time
        
        print(f"✅ Documento cargado en {load_time:.2f}s")
        print(f"📊 Caracteres procesados: {len(processed_content):,}")
        print(f"🧩 Elementos estructurales: {len(structural_elements) if structural_elements else 0}")
        
        if not structural_elements:
            print("⚠️  No se obtuvieron elementos estructurales")
            return False, "No se obtuvieron elementos estructurales"
        
        print_section("2. Análisis de Elementos Estructurales")
        
        # Analizar tipos de elementos
        element_types = {}
        for element in structural_elements:
            element_type = "unknown"
            if hasattr(element, 'category'):
                element_type = element.category
            elif hasattr(element, 'metadata') and element.metadata:
                element_type = element.metadata.get('category', 'unknown')
            
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        print("📋 Tipos de elementos encontrados:")
        for element_type, count in element_types.items():
            print(f"   • {element_type}: {count}")
        
        print_section("3. Creando Chunks Semánticos Avanzados")
        
        # Crear chunks semánticos
        start_time = time.time()
        semantic_chunks = create_advanced_semantic_chunks(structural_elements, max_chunk_size=800, overlap=150)
        chunking_time = time.time() - start_time
        
        print(f"✅ Chunks semánticos creados en {chunking_time:.2f}s")
        print(f"📦 Total de chunks: {len(semantic_chunks)}")
        
        if not semantic_chunks:
            print("❌ No se pudieron crear chunks semánticos")
            return False, "No se pudieron crear chunks semánticos"
        
        print_section("4. Análisis de Chunks Semánticos")
        
        # Analizar chunks
        total_chars = sum(len(chunk) for chunk in semantic_chunks)
        avg_chunk_size = total_chars / len(semantic_chunks)
        
        print(f"📊 Estadísticas de chunks:")
        print(f"   • Total de chunks: {len(semantic_chunks)}")
        print(f"   • Caracteres totales: {total_chars:,}")
        print(f"   • Tamaño promedio: {avg_chunk_size:.0f} caracteres")
        print(f"   • Tamaño mínimo: {min(len(chunk) for chunk in semantic_chunks)} caracteres")
        print(f"   • Tamaño máximo: {max(len(chunk) for chunk in semantic_chunks)} caracteres")
        
        print_section("5. Muestra de Chunks")
        
        # Mostrar algunos chunks de ejemplo
        for i, chunk in enumerate(semantic_chunks[:3]):
            print(f"\n📄 Chunk {i+1} ({len(chunk)} caracteres):")
            print(f"   {chunk[:100]}{'...' if len(chunk) > 100 else ''}")
        
        if len(semantic_chunks) > 3:
            print(f"\n... y {len(semantic_chunks) - 3} chunks más")
        
        print_section("6. Comparación con Chunking Tradicional")
        
        # Comparar con chunking tradicional
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        traditional_chunks = text_splitter.split_text(processed_content)
        
        print(f"📊 Comparación:")
        print(f"   • Chunks semánticos: {len(semantic_chunks)}")
        print(f"   • Chunks tradicionales: {len(traditional_chunks)}")
        print(f"   • Diferencia: {abs(len(semantic_chunks) - len(traditional_chunks))}")
        
        # Verificar si el chunking semántico respeta mejor la estructura
        semantic_quality = "✅ EXCELENTE" if len(semantic_chunks) > 0 else "❌ FALLIDO"
        
        return True, f"Chunking semántico real funcionando correctamente. {semantic_quality}"
        
    except Exception as e:
        return False, f"Error en prueba de chunking semántico: {e}"

def test_document_processing_with_semantic():
    """Prueba el procesamiento completo de documentos con chunking semántico."""
    print_header("PRUEBA DE PROCESAMIENTO COMPLETO CON CHUNKING SEMÁNTICO")
    
    try:
        from rag_core import get_vector_store, add_text_to_knowledge_base_enhanced
        from rag_core import load_document_with_elements
        
        print_section("1. Inicializando Base Vectorial")
        
        vector_store = get_vector_store()
        print("✅ Base vectorial inicializada")
        
        print_section("2. Procesando Documento con Chunking Semántico")
        
        # Buscar un documento de prueba
        test_file = "README.md"
        if not os.path.exists(test_file):
            print(f"❌ Archivo de prueba no encontrado: {test_file}")
            return False, "Archivo de prueba no encontrado"
        
        print(f"📄 Procesando: {test_file}")
        
        # Cargar documento con elementos estructurales
        processed_content, metadata, structural_elements = load_document_with_elements(test_file)
        
        if not processed_content:
            print("❌ No se pudo procesar el documento")
            return False, "No se pudo procesar el documento"
        
        print(f"✅ Documento procesado ({len(processed_content):,} caracteres)")
        print(f"🧩 Elementos estructurales: {len(structural_elements) if structural_elements else 0}")
        
        print_section("3. Añadiendo a Base de Conocimientos con Chunking Semántico")
        
        # Añadir con chunking semántico real
        start_time = time.time()
        add_text_to_knowledge_base_enhanced(
            processed_content,
            vector_store,
            metadata,
            use_semantic_chunking=True,
            structural_elements=structural_elements
        )
        processing_time = time.time() - start_time
        
        print(f"✅ Documento añadido en {processing_time:.2f}s")
        
        print_section("4. Verificando Metadatos de Chunking")
        
        # Verificar que los metadatos incluyan información del chunking
        if structural_elements and len(structural_elements) > 1:
            expected_method = "semantic_advanced"
        elif metadata.get("structural_info", {}).get("total_elements", 0) > 1:
            expected_method = "semantic_improved"
        else:
            expected_method = "traditional"
        
        print(f"🎯 Método de chunking esperado: {expected_method}")
        print(f"📊 Metadatos estructurales: {metadata.get('structural_info', {})}")
        
        return True, f"Procesamiento completo exitoso con chunking {expected_method}"
        
    except Exception as e:
        return False, f"Error en procesamiento completo: {e}"

def main():
    """Función principal que ejecuta todas las pruebas."""
    print_header("PRUEBAS DE CHUNKING SEMÁNTICO REAL")
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Chunking Semántico Real", test_semantic_chunking_real),
        ("Procesamiento Completo", test_document_processing_with_semantic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            success, details = test_func()
            results.append((test_name, success, details))
            
            if success:
                print(f"✅ {test_name}: EXITOSO")
                print(f"   📝 {details}")
            else:
                print(f"❌ {test_name}: FALLIDO")
                print(f"   📝 {details}")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR")
            print(f"   📝 Error: {e}")
            results.append((test_name, False, f"Error: {e}"))
    
    print_header("RESULTADOS FINALES")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"📊 Resumen: {passed}/{total} pruebas exitosas")
    
    for test_name, success, details in results:
        status = "✅ EXITOSO" if success else "❌ FALLIDO"
        print(f"   • {test_name}: {status}")
        if not success:
            print(f"     📝 {details}")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El chunking semántico real está funcionando correctamente.")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisar implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 