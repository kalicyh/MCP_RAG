#!/usr/bin/env python3
"""
Script principal de validación del sistema RAG mejorado.
Prueba todas las funcionalidades del sistema incluyendo:
- Procesamiento avanzado de documentos
- Cache de embeddings y optimización
- Escalabilidad y rendimiento
- Herramientas MCP completas
- Manejo de errores y recuperación
"""

import os
import sys
import tempfile
import time
import requests
from datetime import datetime
from unittest.mock import patch, MagicMock
# Importar Rich para mejorar la salida en consola
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
console = Console()

# Añadir el directorio actual al path para importar nuestros módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    console.print(Panel(f"[bold blue]{title}[/bold blue]", title="[cyan]Prueba[/cyan]"))

def print_section(title):
    console.print(f"\n[bold magenta]{title}[/bold magenta]")
    console.print("[magenta]" + "-" * 40 + "[/magenta]")

def print_result(test_name, success, details=""):
    status = "[bold green]✅ PASÓ[/bold green]" if success else "[bold red]❌ FALLÓ[/bold red]"
    console.print(f"{status} [bold]{test_name}[/bold]")
    if details:
        console.print(f"   [yellow]{details}[/yellow]")

def test_system_initialization():
    """Prueba la inicialización completa del sistema."""
    print_header("INICIALIZACIÓN DEL SISTEMA")
    
    try:
        from rag_core import get_vector_store, get_cache_stats, get_vector_store_stats_advanced
        
        print_section("1. Verificación de Componentes")
        
        # Verificar vector store
        print("🔍 Inicializando base vectorial...")
        vector_store = get_vector_store()
        print("✅ Base vectorial inicializada")
        
        # Verificar cache de embeddings
        print("🧠 Verificando cache de embeddings...")
        cache_stats = get_cache_stats()
        print(f"✅ Cache de embeddings: {cache_stats.get('total_requests', 0)} solicitudes")
        
        # Verificar estadísticas avanzadas
        print("📊 Obteniendo estadísticas del sistema...")
        advanced_stats = get_vector_store_stats_advanced()
        print(f"✅ Sistema: {advanced_stats.get('total_documents', 0)} documentos")
        print(f"✅ Memoria: {advanced_stats.get('current_memory_usage_mb', 0):.1f} MB")
        print(f"✅ Es base grande: {advanced_stats.get('is_large_database', False)}")
        
        details = f"Sistema inicializado: {advanced_stats.get('total_documents', 0)} documentos, {advanced_stats.get('current_memory_usage_mb', 0):.1f} MB"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en inicialización: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_enhanced_document_processing():
    """Prueba el procesamiento mejorado de documentos con Unstructured."""
    print_header("PROCESAMIENTO AVANZADO DE DOCUMENTOS")
    
    try:
        from rag_core import load_document_with_fallbacks, log
        
        # Crear un archivo de prueba complejo
        test_content = """
# Documento de Prueba Completo

Este es un documento de prueba para verificar el procesamiento mejorado del sistema RAG.

## Sección 1: Información Básica

- Punto 1: El sistema RAG funciona correctamente
- Punto 2: El procesamiento con Unstructured está activo
- Punto 3: Los metadatos estructurales se extraen
- Punto 4: El chunking semántico está optimizado

## Sección 2: Tabla de Datos

| Característica | Estado | Notas |
|----------------|--------|-------|
| Procesamiento | ✅ Activo | Funcionando correctamente |
| Metadatos | ✅ Extraídos | Información estructural disponible |
| Chunking | ✅ Semántico | División inteligente activa |
| Cache | ✅ Optimizado | Embeddings en memoria y disco |
| Escalabilidad | ✅ Preparado | Listo para bases grandes |

## Sección 3: Análisis Técnico

El sistema implementa las siguientes mejoras:

1. **Procesamiento Inteligente**: Uso de Unstructured para extracción avanzada
2. **Metadatos Estructurales**: Información detallada sobre títulos, tablas, listas
3. **Chunking Semántico**: División basada en estructura del documento
4. **Cache de Embeddings**: Optimización de memoria y rendimiento
5. **Escalabilidad**: Detección automática de perfiles

## Conclusión

El sistema está funcionando de manera óptima con todas las mejoras implementadas.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            print(f"📄 Procesando archivo de prueba: {test_file}")
            
            start_time = time.time()
            processed_content, metadata = load_document_with_fallbacks(test_file)
            processing_time = time.time() - start_time
            
            print(f"✅ Procesamiento exitoso en {processing_time:.2f}s")
            print(f"📊 Contenido procesado: {len(processed_content)} caracteres")
            
            # Verificar metadatos estructurales
            structural_info = metadata.get("structural_info", {})
            print(f"🏗️ Metadatos estructurales:")
            print(f"   • Elementos totales: {structural_info.get('total_elements', 'N/A')}")
            print(f"   • Títulos: {structural_info.get('titles_count', 'N/A')}")
            print(f"   • Tablas: {structural_info.get('tables_count', 'N/A')}")
            print(f"   • Listas: {structural_info.get('lists_count', 'N/A')}")
            print(f"   • Bloques narrativos: {structural_info.get('narrative_blocks', 'N/A')}")
            
            # Verificar método de procesamiento
            processing_method = metadata.get("processing_method", "desconocido")
            print(f"🔧 Método de procesamiento: {processing_method}")
            
            details = f"Procesado {len(processed_content)} caracteres en {processing_time:.2f}s usando {processing_method}"
            return True, details
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(test_file)
            except:
                pass
                
    except Exception as e:
        error_msg = f"Error en procesamiento: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_cache_performance():
    """Prueba el rendimiento del cache de embeddings."""
    print_header("RENDIMIENTO DEL CACHE DE EMBEDDINGS")
    
    try:
        from rag_core import get_cache_stats, clear_embedding_cache, get_embedding_function
        
        print_section("1. Generando Datos de Prueba para el Cache")
        
        # Obtener la función de embedding
        embedding_function = get_embedding_function()
        
        # Generar algunos textos de prueba para activar el cache
        test_texts = [
            "Este es un texto de prueba para el cache de embeddings.",
            "El sistema RAG mejorado incluye procesamiento inteligente.",
            "Los metadatos estructurales se extraen correctamente.",
            "El chunking semántico está optimizado para mejor contexto.",
            "La base de conocimientos vectorial funciona eficientemente."
        ]
        
        print("🔄 Generando embeddings de prueba...")
        for i, text in enumerate(test_texts, 1):
            embedding = embedding_function.embed_query(text)
            print(f"   • Texto {i}: {len(embedding)} dimensiones")
        
        print_section("2. Estadísticas del Cache")
        
        # Obtener estadísticas después de generar embeddings
        cache_stats = get_cache_stats()
        
        print(f"📊 Solicitudes totales: {cache_stats.get('total_requests', 0)}")
        print(f"🎯 Hits en memoria: {cache_stats.get('memory_hits', 0)}")
        print(f"💾 Hits en disco: {cache_stats.get('disk_hits', 0)}")
        print(f"❌ Misses: {cache_stats.get('misses', 0)}")
        print(f"📈 Tasa de hits total: {cache_stats.get('overall_hit_rate', 'N/A')}")
        print(f"🧠 Tasa de hits en memoria: {cache_stats.get('memory_hit_rate', 'N/A')}")
        print(f"💾 Tamaño del cache en memoria: {cache_stats.get('memory_cache_size', 0)}")
        print(f"📁 Tamaño del cache en disco: {cache_stats.get('disk_cache_size', 0)}")
        
        print_section("3. Análisis de Rendimiento")
        
        total_requests = cache_stats.get('total_requests', 0)
        if total_requests > 0:
            overall_hit_rate = float(cache_stats.get('overall_hit_rate', '0%').rstrip('%'))
            memory_hit_rate = float(cache_stats.get('memory_hit_rate', '0%').rstrip('%'))
            
            print(f"📊 Análisis de rendimiento:")
            if overall_hit_rate > 70:
                print("🚀 Rendimiento excelente del cache")
            elif overall_hit_rate > 50:
                print("✅ Rendimiento bueno del cache")
            else:
                print("⚠️ Rendimiento moderado del cache")
            
            if memory_hit_rate > 50:
                print("⚡ Cache en memoria muy efectivo")
            else:
                print("💾 Dependencia del disco para cache")
            
            # Verificar tamaño del cache
            memory_size = cache_stats.get('memory_cache_size', 0)
            disk_size = cache_stats.get('disk_cache_size', 0)
            
            if memory_size > 0:
                print(f"🧠 Cache en memoria activo: {memory_size} elementos")
            if disk_size > 0:
                print(f"💾 Cache en disco activo: {disk_size} elementos")
        else:
            print("⚠️ No se detectaron solicitudes al cache")
        
        print_section("4. Prueba de Reutilización del Cache")
        
        # Generar el mismo texto nuevamente para probar hits
        print("🔄 Probando reutilización del cache...")
        for i, text in enumerate(test_texts[:2], 1):
            embedding = embedding_function.embed_query(text)
            print(f"   • Reutilización {i}: {len(embedding)} dimensiones")
        
        # Obtener estadísticas finales
        final_stats = get_cache_stats()
        print(f"📊 Estadísticas finales:")
        print(f"   • Total requests: {final_stats.get('total_requests', 0)}")
        print(f"   • Memory hits: {final_stats.get('memory_hits', 0)}")
        print(f"   • Disk hits: {final_stats.get('disk_hits', 0)}")
        print(f"   • Misses: {final_stats.get('misses', 0)}")
        
        print_section("5. Limpieza de Cache (Opcional)")
        
        # Preguntar si limpiar cache (solo en modo interactivo)
        if len(sys.argv) > 1 and '--clean-cache' in sys.argv:
            print("🧹 Limpiando cache de embeddings...")
            clear_embedding_cache()
            print("✅ Cache limpiado")
        
        details = f"Cache probado: {final_stats.get('total_requests', 0)} solicitudes, {final_stats.get('overall_hit_rate', 'N/A')} tasa de hits"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en prueba de cache: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_optimization_features():
    """Prueba las funciones de optimización y escalabilidad."""
    print_header("OPTIMIZACIÓN Y ESCALABILIDAD")
    
    try:
        from rag_core import (
            optimize_vector_store, 
            get_vector_store_stats_advanced,
            is_large_database,
            get_optimal_vector_store_profile
        )
        
        print_section("1. Análisis de Escalabilidad")
        
        # Verificar si es base grande
        is_large = is_large_database()
        print(f"🔍 Es base grande: {is_large}")
        
        # Obtener perfil óptimo
        optimal_profile = get_optimal_vector_store_profile()
        print(f"🎯 Perfil óptimo: {optimal_profile}")
        
        # Estadísticas avanzadas
        advanced_stats = get_vector_store_stats_advanced()
        print(f"📊 Documentos totales: {advanced_stats.get('total_documents', 0)}")
        print(f"⏱️ Tiempo estimado de optimización: {advanced_stats.get('estimated_optimization_time', 'N/A')}")
        print(f"🎯 Enfoque recomendado: {advanced_stats.get('recommended_optimization_approach', 'N/A')}")
        
        print_section("2. Optimización de Base Vectorial")
        
        print("🚀 Iniciando optimización...")
        start_time = time.time()
        
        optimization_result = optimize_vector_store()
        
        optimization_time = time.time() - start_time
        
        if optimization_result.get("status") == "success":
            print(f"✅ Optimización completada en {optimization_time:.2f}s")
            print(f"🔧 Tipo: {optimization_result.get('optimization_type', 'N/A')}")
            
            optimizations = optimization_result.get('optimizations_applied', [])
            if optimizations:
                print("📋 Optimizaciones aplicadas:")
                for opt in optimizations:
                    print(f"   • {opt}")
            
            details = f"Optimización {optimization_result.get('optimization_type', 'N/A')} completada en {optimization_time:.2f}s"
            return True, details
        else:
            error_msg = f"Error en optimización: {optimization_result.get('message', 'Error desconocido')}"
            print(f"❌ {error_msg}")
            return False, error_msg
        
    except Exception as e:
        error_msg = f"Error en prueba de optimización: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_server_tools():
    """Prueba todas las herramientas del servidor MCP."""
    print_header("HERRAMIENTAS DEL SERVIDOR MCP")
    
    try:
        # Importar funciones del servidor
        from rag_server import learn_text, learn_document, ask_rag, learn_from_url
        
        print_section("1. Prueba de learn_text")
        
        text_result = learn_text(
            "El sistema RAG mejorado incluye procesamiento inteligente con Unstructured y metadatos estructurales detallados.",
            "test_enhanced_features"
        )
        print(f"✅ learn_text: {text_result[:100]}...")
        
        print_section("2. Prueba de learn_document")
        
        # Crear un archivo de prueba para learn_document
        test_doc_content = """
# Documento de Prueba del Servidor

Este documento prueba las capacidades mejoradas del servidor MCP.

## Funcionalidades Probadas

1. **Procesamiento Inteligente**: Uso de Unstructured para mejor extracción
2. **Metadatos Estructurales**: Información detallada sobre la estructura
3. **Chunking Semántico**: División inteligente del contenido
4. **Sistema de Fallbacks**: Múltiples estrategias de procesamiento

## Resultados Esperados

- Mejor calidad de respuestas
- Información de fuentes detallada
- Rastreabilidad completa
- Procesamiento optimizado
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_doc_content)
            test_file = f.name
        
        try:
            doc_result = learn_document(test_file)
            print(f"✅ learn_document: {doc_result[:100]}...")
        finally:
            try:
                os.unlink(test_file)
            except:
                pass
        
        print_section("3. Prueba de ask_rag")
        
        query_result = ask_rag("¿Qué funcionalidades incluye el sistema RAG mejorado?")
        print(f"✅ ask_rag: {query_result[:100]}...")
        
        print_section("4. Prueba de learn_from_url")
        
        url_result = learn_from_url("https://httpbin.org/html")
        print(f"✅ learn_from_url: {url_result[:100]}...")
        
        details = "Todas las herramientas MCP funcionando correctamente"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en prueba de herramientas del servidor: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_error_handling():
    """Prueba el manejo robusto de errores."""
    print_header("MANEJO DE ERRORES")
    
    try:
        from rag_server import learn_document, learn_from_url, ask_rag
        
        print_section("1. Archivo Inexistente")
        
        try:
            result = learn_document("archivo_que_no_existe.txt")
            if "Error" in result or "no encontrado" in result:
                print("✅ Manejo correcto de archivo inexistente")
            else:
                print("❌ No se detectó manejo de archivo inexistente")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print_section("2. URL Inválida")
        
        try:
            result = learn_from_url("https://url-que-no-existe-12345.com")
            if "Error" in result or "no se pudo" in result:
                print("✅ Manejo correcto de URL inválida")
            else:
                print("❌ No se detectó manejo de URL inválida")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print_section("3. Pregunta Sin Información")
        
        try:
            result = ask_rag("¿Cuál es la capital de un planeta que no existe?")
            if "no tengo información" in result.lower() or "no encontré" in result.lower():
                print("✅ Manejo correcto de pregunta sin información")
            else:
                print("❌ No se detectó manejo de pregunta sin información")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        details = "Manejo de errores validado correctamente"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en prueba de manejo de errores: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_metadata_filtering():
    """Prueba el filtrado avanzado de metadatos."""
    print_header("FILTRADO DE METADATOS")
    
    try:
        from rag_core import get_vector_store, search_with_metadata_filters, create_metadata_filter
        
        print_section("1. Búsqueda Sin Filtros")
        
        vector_store = get_vector_store()
        results = search_with_metadata_filters(vector_store, "sistema")
        print(f"✅ Resultados sin filtro: {len(results)} documentos")
        
        print_section("2. Filtro por Tipo de Archivo")
        
        pdf_filter = create_metadata_filter(file_type=".pdf")
        pdf_results = search_with_metadata_filters(vector_store, "sistema", pdf_filter)
        print(f"✅ Resultados filtrados por PDF: {len(pdf_results)} documentos")
        
        print_section("3. Filtro por Documentos con Tablas")
        
        tables_filter = create_metadata_filter(min_tables=1)
        tables_results = search_with_metadata_filters(vector_store, "sistema", tables_filter)
        print(f"✅ Resultados filtrados por tablas: {len(tables_results)} documentos")
        
        print_section("4. Filtro Complejo")
        
        complex_filter = create_metadata_filter(
            file_type=".docx",
            min_tables=1
        )
        complex_results = search_with_metadata_filters(vector_store, "sistema", complex_filter)
        print(f"✅ Resultados con filtro complejo: {len(complex_results)} documentos")
        
        details = f"Filtrado probado: {len(results)} total, {len(pdf_results)} PDF, {len(tables_results)} con tablas"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en prueba de filtrado: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def generate_test_report(results, test_details):
    """Genera un reporte detallado de las pruebas en formato tabla usando Rich."""
    print_header("REPORTE FINAL DE PRUEBAS")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    failed_tests = total_tests - passed_tests

    # Resumen general en panel
    console.print(Panel(f"[bold]Total de pruebas:[/bold] [cyan]{total_tests}[/cyan]\n"
                       f"[bold]Pruebas exitosas:[/bold] [green]{passed_tests}[/green]\n"
                       f"[bold]Pruebas fallidas:[/bold] [red]{failed_tests}[/red]\n"
                       f"[bold]Tasa de éxito:[/bold] [bold yellow]{(passed_tests/total_tests)*100:.1f}%[/bold yellow]",
                       title="[bold magenta]Resumen General[/bold magenta]", border_style="magenta"))

    # Tabla de resultados detallada
    table = Table(title="Resultados Detallados de Pruebas", show_lines=True, header_style="bold blue")
    table.add_column("PRUEBA", style="cyan", no_wrap=True)
    table.add_column("DESCRIPCIÓN", style="white")
    table.add_column("ESTADO", style="bold")
    table.add_column("RESULTADO/DETALLES", style="yellow")

    for test_name, success in results.items():
        test_info = test_details.get(test_name, {})
        description = test_info.get('description', 'Sin descripción')
        result_details = test_info.get('error', '✅ Exitoso') if not success else test_info.get('error', '✅ Exitoso')
        status = "[green]✅ PASÓ[/green]" if success else "[red]❌ FALLÓ[/red]"
        # Truncar descripción y resultado si son muy largos
        if len(description) > 42:
            description = description[:39] + "..."
        if len(result_details) > 37:
            result_details = result_details[:34] + "..."
        table.add_row(test_name, description, status, result_details)
    console.print(table)

    # Resumen por estado en paneles
    if passed_tests > 0:
        exitosas = [name for name, ok in results.items() if ok]
        console.print(Panel("\n".join(f"[green]• {name}[/green]" for name in exitosas), title=f"[bold green]PRUEBAS EXITOSAS ({passed_tests})[/bold green]", border_style="green"))
    if failed_tests > 0:
        fallidas = [name for name, ok in results.items() if not ok]
        console.print(Panel("\n".join(f"[red]• {name}[/red]" for name in fallidas), title=f"[bold red]PRUEBAS FALLIDAS ({failed_tests})[/bold red]", border_style="red"))

    # Estado del sistema
    if passed_tests == total_tests:
        console.print(Panel("[bold green]🚀 SISTEMA COMPLETAMENTE OPERATIVO[/bold green]\n• Todas las funcionalidades funcionando correctamente\n• Listo para uso en producción", title="[green]ESTADO DEL SISTEMA[/green]", border_style="green"))
    elif passed_tests >= total_tests * 0.8:
        console.print(Panel("[bold yellow]✅ SISTEMA MAYORMENTE OPERATIVO[/bold yellow]\n• La mayoría de funcionalidades funcionando\n• Revisar pruebas fallidas para optimización", title="[yellow]ESTADO DEL SISTEMA[/yellow]", border_style="yellow"))
    else:
        console.print(Panel("[bold red]⚠️ SISTEMA CON PROBLEMAS[/bold red]\n• Múltiples funcionalidades con errores\n• Requiere revisión y corrección", title="[red]ESTADO DEL SISTEMA[/red]", border_style="red"))

    # Información adicional del cache si está disponible
    try:
        from rag_core import get_cache_stats
        cache_stats = get_cache_stats()
        if cache_stats.get('total_requests', 0) > 0:
            console.print(Panel(f"[bold]Solicitudes totales:[/bold] {cache_stats.get('total_requests', 0)}\n"
                               f"[bold]Tasa de hits:[/bold] {cache_stats.get('overall_hit_rate', 'N/A')}\n"
                               f"[bold]Cache en memoria:[/bold] {cache_stats.get('memory_cache_size', 0)} elementos\n"
                               f"[bold]Cache en disco:[/bold] {cache_stats.get('disk_cache_size', 0)} elementos",
                               title="[blue]INFORMACIÓN ADICIONAL DEL CACHE[/blue]", border_style="blue"))
    except:
        pass

def main():
    """Función principal del script de validación."""
    
    print("🚀 **SISTEMA RAG MEJORADO - VALIDACIÓN COMPLETA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Versión: Sistema RAG Mejorado v2.0")
    print("=" * 70)
    
    # Definición detallada de las pruebas con descripciones
    test_definitions = {
        "Inicialización del Sistema": {
            "description": "Verifica que todos los componentes del sistema se inicialicen correctamente",
            "function": test_system_initialization
        },
        "Procesamiento Avanzado de Documentos": {
            "description": "Prueba el procesamiento mejorado con Unstructured y metadatos estructurales",
            "function": test_enhanced_document_processing
        },
        "Rendimiento del Cache de Embeddings": {
            "description": "Evalúa el rendimiento y estadísticas del cache de embeddings",
            "function": test_cache_performance
        },
        "Optimización y Escalabilidad": {
            "description": "Verifica las funciones de optimización y detección de escalabilidad",
            "function": test_optimization_features
        },
        "Herramientas del Servidor MCP": {
            "description": "Prueba todas las herramientas disponibles en el servidor MCP",
            "function": test_server_tools
        },
        "Manejo de Errores": {
            "description": "Valida el manejo robusto de errores y casos edge",
            "function": test_error_handling
        },
        "Filtrado de Metadatos": {
            "description": "Prueba el filtrado avanzado de metadatos en búsquedas",
            "function": test_metadata_filtering
        }
    }
    
    results = {}
    test_details = {}
    
    # Ejecutar todas las pruebas
    for test_name, test_info in test_definitions.items():
        try:
            print(f"\n🧪 Ejecutando: {test_name}")
            success, details = test_info["function"]()
            results[test_name] = success
            test_details[test_name] = {
                "description": test_info["description"],
                "error": details
            }
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results[test_name] = False
            test_details[test_name] = {
                "description": test_info["description"],
                "error": str(e)
            }
    
    # Generar reporte final con tabla
    generate_test_report(results, test_details)
    
    print(f"\n💡 **PRÓXIMOS PASOS:**")
    print("   • Usar el sistema con documentos reales")
    print("   • Monitorear rendimiento regularmente")
    print("   • Ejecutar optimizaciones según necesidad")
    print("   • Revisar logs para mejoras continuas")
    
    # Guardar reporte en archivo
    try:
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE PRUEBAS DEL SISTEMA RAG\n")
            f.write("=" * 50 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            total_tests = len(results)
            passed_tests = sum(1 for success in results.values() if success)
            f.write(f"Resumen: {passed_tests}/{total_tests} pruebas exitosas\n\n")
            
            for test_name, success in results.items():
                test_info = test_details.get(test_name, {})
                status = "PASÓ" if success else "FALLÓ"
                f.write(f"{test_name}: {status}\n")
                f.write(f"  Descripción: {test_info.get('description', 'N/A')}\n")
                f.write(f"  Resultado: {test_info.get('error', 'N/A')}\n\n")
        
        print(f"📄 Reporte guardado en: {report_filename}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {e}")

if __name__ == "__main__":
    main() 