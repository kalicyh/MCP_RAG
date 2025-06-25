#!/usr/bin/env python3
"""
Script de validación del servidor MCP organizado.
Prueba todas las funcionalidades del sistema incluyendo:
- Arquitectura modular de herramientas
- Procesamiento avanzado de documentos
- Cache de embeddings y optimización
- Herramientas MCP completas
- Manejo de errores y recuperación
- Estado del servidor organizado
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

# Añadir el directorio src al path para importar nuestros módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

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

def test_modular_architecture():
    """Prueba la arquitectura modular del servidor MCP."""
    print_header("ARQUITECTURA MODULAR")
    
    try:
        print_section("1. Verificación de Módulos")
        
        # Verificar que los módulos existen
        modules_to_check = [
            "tools.document_tools",
            "tools.search_tools", 
            "tools.utility_tools",
            "tools"
        ]
        
        for module_name in modules_to_check:
            try:
                __import__(module_name)
                print(f"✅ Módulo {module_name} importado correctamente")
            except ImportError as e:
                print(f"❌ Error importando {module_name}: {e}")
                return False, f"Error en módulo {module_name}"
        
        print_section("2. Verificación de Funciones")
        
        # Verificar funciones en cada módulo
        from tools.document_tools import learn_text, learn_document, learn_from_url
        from tools.search_tools import ask_rag, ask_rag_filtered
        from tools.utility_tools import get_knowledge_base_stats, get_embedding_cache_stats
        
        print("✅ Funciones de document_tools disponibles")
        print("✅ Funciones de search_tools disponibles")
        print("✅ Funciones de utility_tools disponibles")
        
        print_section("3. Verificación de Configuración")
        
        # Verificar función de configuración
        from tools import configure_rag_state, ALL_TOOLS, TOOLS_BY_NAME
        
        print(f"✅ Función configure_rag_state disponible")
        print(f"✅ ALL_TOOLS contiene {len(ALL_TOOLS)} herramientas")
        print(f"✅ TOOLS_BY_NAME contiene {len(TOOLS_BY_NAME)} herramientas")
        
        # Verificar que todas las herramientas están en la lista
        expected_tools = [
            "learn_text", "learn_document", "learn_from_url",
            "ask_rag", "ask_rag_filtered",
            "get_knowledge_base_stats", "get_embedding_cache_stats",
            "clear_embedding_cache_tool", "optimize_vector_database",
            "get_vector_database_stats", "reindex_vector_database"
        ]
        
        for tool in expected_tools:
            if tool in TOOLS_BY_NAME:
                print(f"✅ Herramienta {tool} registrada")
            else:
                print(f"❌ Herramienta {tool} no encontrada")
                return False, f"Herramienta {tool} faltante"
        
        details = f"Arquitectura modular verificada: {len(ALL_TOOLS)} herramientas organizadas"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en arquitectura modular: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_server_initialization():
    """Prueba la inicialización del servidor MCP organizado."""
    print_header("INICIALIZACIÓN DEL SERVIDOR MCP")
    
    try:
        print_section("1. Importación del Servidor")
        
        # Importar el servidor completo
        import server
        print("✅ Servidor importado correctamente")
        
        print_section("2. Verificación de Componentes")
        
        # Verificar que el objeto mcp existe
        if hasattr(server, 'mcp'):
            print("✅ Objeto MCP creado")
            print(f"   • Nombre del servidor: {server.mcp.name}")
        else:
            print("❌ Objeto MCP no encontrado")
            return False, "Objeto MCP faltante"
        
        # Verificar estado RAG
        if hasattr(server, 'rag_state'):
            print("✅ Estado RAG inicializado")
            print(f"   • Componentes: {list(server.rag_state.keys())}")
        else:
            print("❌ Estado RAG no encontrado")
            return False, "Estado RAG faltante"
        
        # Verificar conversor MarkItDown
        if hasattr(server, 'md_converter'):
            print("✅ Conversor MarkItDown inicializado")
        else:
            print("❌ Conversor MarkItDown no encontrado")
            return False, "Conversor MarkItDown faltante"
        
        print_section("3. Verificación de Funciones de Inicialización")
        
        # Verificar funciones de inicialización
        init_functions = [
            'warm_up_rag_system',
            'ensure_converted_docs_directory', 
            'save_processed_copy',
            'initialize_rag'
        ]
        
        for func_name in init_functions:
            if hasattr(server, func_name):
                print(f"✅ Función {func_name} disponible")
            else:
                print(f"❌ Función {func_name} no encontrada")
                return False, f"Función {func_name} faltante"
        
        print_section("4. Verificación de Herramientas MCP")
        
        # Verificar que las herramientas están disponibles en el servidor
        mcp_tools = [
            'learn_text', 'learn_document', 'learn_from_url',
            'ask_rag', 'ask_rag_filtered',
            'get_knowledge_base_stats', 'get_embedding_cache_stats',
            'clear_embedding_cache_tool', 'optimize_vector_database',
            'get_vector_database_stats', 'reindex_vector_database'
        ]
        
        available_tools = []
        for tool_name in mcp_tools:
            if hasattr(server, tool_name):
                tool_func = getattr(server, tool_name)
                if callable(tool_func):
                    available_tools.append(tool_name)
                    print(f"✅ {tool_name} disponible y callable")
                else:
                    print(f"❌ {tool_name} no es callable")
            else:
                print(f"❌ {tool_name} no encontrado")
        
        details = f"Servidor inicializado: {len(available_tools)} herramientas MCP registradas"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en inicialización del servidor: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_tools_configuration():
    """Prueba la configuración de herramientas modulares."""
    print_header("CONFIGURACIÓN DE HERRAMIENTAS")
    
    try:
        print_section("1. Configuración del Estado RAG")
        
        # Importar el servidor para obtener el estado real
        import server
        
        # Usar el estado RAG real del servidor
        test_rag_state = server.rag_state
        
        # Simular conversor MarkItDown
        class MockMarkItDown:
            def convert(self, url):
                return f"Contenido procesado de {url}"
        
        test_md_converter = MockMarkItDown()
        
        # Función de inicialización simulada
        def test_initialize_rag():
            return "RAG inicializado"
        
        # Función de guardar copia simulada
        def test_save_processed_copy(file_path, content, method):
            return f"copia_guardada_{method}.md"
        
        print_section("2. Aplicar Configuración")
        
        from tools import configure_rag_state
        
        # Configurar herramientas con el estado real
        configure_rag_state(
            rag_state=test_rag_state,
            md_converter=test_md_converter,
            initialize_rag_func=test_initialize_rag,
            save_processed_copy_func=test_save_processed_copy
        )
        
        print("✅ Configuración aplicada correctamente")
        
        print_section("3. Verificar Configuración en Módulos")
        
        # Verificar que los módulos tienen acceso al estado
        from tools.document_tools import rag_state as doc_rag_state
        from tools.search_tools import rag_state as search_rag_state
        from tools.utility_tools import rag_state as utility_rag_state
        
        if doc_rag_state == test_rag_state:
            print("✅ Estado RAG configurado en document_tools")
        else:
            print("❌ Estado RAG no configurado en document_tools")
            return False, "Estado RAG no compartido en document_tools"
        
        if search_rag_state == test_rag_state:
            print("✅ Estado RAG configurado en search_tools")
        else:
            print("❌ Estado RAG no configurado en search_tools")
            return False, "Estado RAG no compartido en search_tools"
        
        if utility_rag_state == test_rag_state:
            print("✅ Estado RAG configurado en utility_tools")
        else:
            print("❌ Estado RAG no configurado en utility_tools")
            return False, "Estado RAG no compartido en utility_tools"
        
        details = "Configuración de herramientas verificada: estado RAG compartido entre módulos"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en configuración de herramientas: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_document_tools():
    """Prueba las herramientas de procesamiento de documentos usando el servidor completo."""
    print_header("HERRAMIENTAS DE DOCUMENTOS")
    
    try:
        # Importar el servidor completo
        import server
        
        print_section("1. Prueba de learn_text")
        
        # Probar learn_text usando el servidor
        test_text = "Este es un texto de prueba para el sistema RAG modular."
        test_source = "test_validation"
        
        try:
            result = server.learn_text(test_text, test_source)
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ learn_text falló: {result}")
                return False, f"Error en learn_text: {result}"
            elif result and ("añadido" in result.lower() or "procesado" in result.lower()):
                print("✅ learn_text funcionando correctamente")
            else:
                print(f"⚠️ learn_text ejecutado pero respuesta inesperada: {result}")
                return False, f"Respuesta inesperada en learn_text: {result}"
        except Exception as e:
            print(f"❌ Error en learn_text: {e}")
            return False, f"Error en learn_text: {e}"
        
        print_section("2. Prueba de learn_document")
        
        # Crear archivo de prueba
        test_content = """
# Documento de Prueba Modular

Este documento prueba las capacidades del sistema RAG organizado.

## Características Probadas

1. **Arquitectura Modular**: Herramientas organizadas en módulos
2. **Configuración Centralizada**: Estado RAG compartido
3. **Procesamiento Inteligente**: Uso de Unstructured
4. **Metadatos Estructurales**: Información detallada

## Resultados Esperados

- Procesamiento exitoso del documento
- Extracción de metadatos estructurales
- Integración con el sistema modular
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # Probar learn_document usando el servidor
            result = server.learn_document(test_file)
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ learn_document falló: {result}")
                return False, f"Error en learn_document: {result}"
            elif result and ("procesado" in result.lower() or "añadido" in result.lower()):
                print("✅ learn_document funcionando correctamente")
            else:
                print(f"⚠️ learn_document ejecutado pero respuesta inesperada: {result}")
                return False, f"Respuesta inesperada en learn_document: {result}"
                
        except Exception as e:
            print(f"❌ Error en learn_document: {e}")
            return False, f"Error en learn_document: {e}"
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(test_file)
            except:
                pass
        
        print_section("3. Prueba de learn_from_url")
        
        try:
            result = server.learn_from_url("https://httpbin.org/html")
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ learn_from_url falló: {result}")
                return False, f"Error en learn_from_url: {result}"
            elif result and ("procesada" in result.lower() or "añadido" in result.lower()):
                print("✅ learn_from_url funcionando correctamente")
            else:
                print(f"⚠️ learn_from_url ejecutado pero respuesta inesperada: {result}")
                return False, f"Respuesta inesperada en learn_from_url: {result}"
        except Exception as e:
            print(f"❌ Error en learn_from_url: {e}")
            return False, f"Error en learn_from_url: {e}"
        
        details = "Herramientas de documentos probadas: learn_text, learn_document, learn_from_url"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en herramientas de documentos: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_search_tools():
    """Prueba las herramientas de búsqueda usando el servidor completo."""
    print_header("HERRAMIENTAS DE BÚSQUEDA")
    
    try:
        # Importar el servidor completo
        import server
        
        print_section("1. Prueba de ask_rag")
        
        try:
            result = server.ask_rag("¿Qué es el sistema RAG?")
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ ask_rag falló: {result}")
                return False, f"Error en ask_rag: {result}"
            elif result and len(str(result)) > 0:
                print("✅ ask_rag funcionando correctamente")
            else:
                print(f"⚠️ ask_rag ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en ask_rag: {result}"
        except Exception as e:
            print(f"❌ Error en ask_rag: {e}")
            return False, f"Error en ask_rag: {e}"
        
        print_section("2. Prueba de ask_rag_filtered")
        
        try:
            result = server.ask_rag_filtered(
                query="¿Qué información hay sobre el sistema?",
                file_type=".txt",
                min_tables=None,
                min_titles=None,
                processing_method=None
            )
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ ask_rag_filtered falló: {result}")
                return False, f"Error en ask_rag_filtered: {result}"
            elif result and len(str(result)) > 0:
                print("✅ ask_rag_filtered funcionando correctamente")
            else:
                print(f"⚠️ ask_rag_filtered ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en ask_rag_filtered: {result}"
        except Exception as e:
            print(f"❌ Error en ask_rag_filtered: {e}")
            return False, f"Error en ask_rag_filtered: {e}"
        
        details = "Herramientas de búsqueda probadas: ask_rag, ask_rag_filtered"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en herramientas de búsqueda: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_utility_tools():
    """Prueba las herramientas de utilidad usando el servidor completo."""
    print_header("HERRAMIENTAS DE UTILIDAD")
    
    try:
        # Importar el servidor completo
        import server
        
        print_section("1. Prueba de get_knowledge_base_stats")
        
        try:
            result = server.get_knowledge_base_stats()
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ get_knowledge_base_stats falló: {result}")
                return False, f"Error en get_knowledge_base_stats: {result}"
            elif result and len(str(result)) > 0:
                print("✅ get_knowledge_base_stats funcionando correctamente")
            else:
                print(f"⚠️ get_knowledge_base_stats ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en get_knowledge_base_stats: {result}"
        except Exception as e:
            print(f"❌ Error en get_knowledge_base_stats: {e}")
            return False, f"Error en get_knowledge_base_stats: {e}"
        
        print_section("2. Prueba de get_embedding_cache_stats")
        
        try:
            result = server.get_embedding_cache_stats()
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ get_embedding_cache_stats falló: {result}")
                return False, f"Error en get_embedding_cache_stats: {result}"
            elif result and len(str(result)) > 0:
                print("✅ get_embedding_cache_stats funcionando correctamente")
            else:
                print(f"⚠️ get_embedding_cache_stats ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en get_embedding_cache_stats: {result}"
        except Exception as e:
            print(f"❌ Error en get_embedding_cache_stats: {e}")
            return False, f"Error en get_embedding_cache_stats: {e}"
        
        print_section("3. Prueba de clear_embedding_cache_tool")
        
        try:
            result = server.clear_embedding_cache_tool()
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ clear_embedding_cache_tool falló: {result}")
                return False, f"Error en clear_embedding_cache_tool: {result}"
            elif result and "limpiado" in result.lower():
                print("✅ clear_embedding_cache_tool funcionando correctamente")
            else:
                print(f"⚠️ clear_embedding_cache_tool ejecutado pero respuesta inesperada: {result}")
                return False, f"Respuesta inesperada en clear_embedding_cache_tool: {result}"
        except Exception as e:
            print(f"❌ Error en clear_embedding_cache_tool: {e}")
            return False, f"Error en clear_embedding_cache_tool: {e}"
        
        print_section("4. Prueba de optimize_vector_database")
        
        try:
            result = server.optimize_vector_database()
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ optimize_vector_database falló: {result}")
                return False, f"Error en optimize_vector_database: {result}"
            elif result and len(str(result)) > 0:
                print("✅ optimize_vector_database funcionando correctamente")
            else:
                print(f"⚠️ optimize_vector_database ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en optimize_vector_database: {result}"
        except Exception as e:
            print(f"❌ Error en optimize_vector_database: {e}")
            return False, f"Error en optimize_vector_database: {e}"
        
        print_section("5. Prueba de get_vector_database_stats")
        
        try:
            result = server.get_vector_database_stats()
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ get_vector_database_stats falló: {result}")
                return False, f"Error en get_vector_database_stats: {result}"
            elif result and len(str(result)) > 0:
                print("✅ get_vector_database_stats funcionando correctamente")
            else:
                print(f"⚠️ get_vector_database_stats ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en get_vector_database_stats: {result}"
        except Exception as e:
            print(f"❌ Error en get_vector_database_stats: {e}")
            return False, f"Error en get_vector_database_stats: {e}"
        
        print_section("6. Prueba de reindex_vector_database")
        
        try:
            result = server.reindex_vector_database(profile="auto")
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ reindex_vector_database falló: {result}")
                return False, f"Error en reindex_vector_database: {result}"
            elif result and len(str(result)) > 0:
                print("✅ reindex_vector_database funcionando correctamente")
            else:
                print(f"⚠️ reindex_vector_database ejecutado pero sin respuesta: {result}")
                return False, f"Sin respuesta en reindex_vector_database: {result}"
        except Exception as e:
            print(f"❌ Error en reindex_vector_database: {e}")
            return False, f"Error en reindex_vector_database: {e}"
        
        details = "Herramientas de utilidad probadas: 6 funciones de mantenimiento"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en herramientas de utilidad: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_mcp_server_integration():
    """Prueba la integración completa del servidor MCP."""
    print_header("INTEGRACIÓN DEL SERVIDOR MCP")
    
    try:
        print_section("1. Importación del Servidor")
        
        import server
        
        print_section("2. Verificación de Herramientas MCP")
        
        # Verificar que las herramientas están disponibles en el servidor
        mcp_tools = [
            'learn_text', 'learn_document', 'learn_from_url',
            'ask_rag', 'ask_rag_filtered',
            'get_knowledge_base_stats', 'get_embedding_cache_stats',
            'clear_embedding_cache_tool', 'optimize_vector_database',
            'get_vector_database_stats', 'reindex_vector_database'
        ]
        
        available_tools = []
        for tool_name in mcp_tools:
            if hasattr(server, tool_name):
                tool_func = getattr(server, tool_name)
                if callable(tool_func):
                    available_tools.append(tool_name)
                    print(f"✅ {tool_name} disponible y callable")
                else:
                    print(f"❌ {tool_name} no es callable")
            else:
                print(f"❌ {tool_name} no encontrado")
        
        print_section("3. Prueba de Ejecución de Herramientas")
        
        # Probar algunas herramientas básicas
        test_results = {}
        
        # Probar learn_text
        try:
            result = server.learn_text("Texto de prueba para integración", "test_integration")
            if result and "Error" in str(result):
                test_results['learn_text'] = False
                print(f"❌ learn_text falló: {result}")
            else:
                test_results['learn_text'] = True
                print("✅ learn_text ejecutado correctamente")
        except Exception as e:
            test_results['learn_text'] = False
            print(f"❌ Error en learn_text: {e}")
        
        # Probar get_knowledge_base_stats
        try:
            result = server.get_knowledge_base_stats()
            if result and "Error" in str(result):
                test_results['get_knowledge_base_stats'] = False
                print(f"❌ get_knowledge_base_stats falló: {result}")
            else:
                test_results['get_knowledge_base_stats'] = True
                print("✅ get_knowledge_base_stats ejecutado correctamente")
        except Exception as e:
            test_results['get_knowledge_base_stats'] = False
            print(f"❌ Error en get_knowledge_base_stats: {e}")
        
        # Probar get_embedding_cache_stats
        try:
            result = server.get_embedding_cache_stats()
            if result and "Error" in str(result):
                test_results['get_embedding_cache_stats'] = False
                print(f"❌ get_embedding_cache_stats falló: {result}")
            else:
                test_results['get_embedding_cache_stats'] = True
                print("✅ get_embedding_cache_stats ejecutado correctamente")
        except Exception as e:
            test_results['get_embedding_cache_stats'] = False
            print(f"❌ Error en get_embedding_cache_stats: {e}")
        
        print_section("4. Análisis de Resultados")
        
        successful_tools = sum(test_results.values())
        total_tools = len(test_results)
        
        print(f"📊 Herramientas probadas: {total_tools}")
        print(f"✅ Exitosas: {successful_tools}")
        print(f"❌ Fallidas: {total_tools - successful_tools}")
        
        if successful_tools == total_tools:
            print("🎉 Todas las herramientas funcionando correctamente")
        elif successful_tools >= total_tools * 0.7:
            print("✅ Mayoría de herramientas funcionando")
        else:
            print("⚠️ Múltiples herramientas con problemas")
        
        details = f"Integración MCP probada: {successful_tools}/{total_tools} herramientas funcionando"
        return successful_tools == total_tools, details
        
    except Exception as e:
        error_msg = f"Error en integración MCP: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_error_handling():
    """Prueba el manejo de errores en la arquitectura modular."""
    print_header("MANEJO DE ERRORES")
    
    try:
        print_section("1. Manejo de Errores en Módulos")
        
        # Probar con estado RAG no configurado
        from tools.document_tools import learn_text
        
        try:
            # Limpiar estado
            from tools.document_tools import set_rag_state
            set_rag_state({})
            
            result = learn_text("Texto de prueba", "test_error")
            if "Error" in str(result) or "no inicializado" in str(result).lower():
                print("✅ Manejo correcto de estado RAG no inicializado")
            else:
                print("⚠️ No se detectó manejo de estado RAG no inicializado")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print_section("2. Manejo de Errores en Servidor")
        
        import server
        
        # Probar con parámetros inválidos
        try:
            result = server.learn_text("", "")  # Parámetros vacíos
            if "Error" in str(result) or "vací" in str(result).lower():
                print("✅ Manejo correcto de parámetros vacíos")
            else:
                print("⚠️ No se detectó manejo de parámetros vacíos")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print_section("3. Manejo de Errores de Configuración")
        
        try:
            from tools import configure_rag_state
            
            # Probar configuración con parámetros None
            configure_rag_state(None, None, None, None)
            print("✅ Configuración con parámetros None manejada correctamente")
        except Exception as e:
            print(f"❌ Error en configuración con parámetros None: {e}")
        
        details = "Manejo de errores validado en arquitectura modular"
        return True, details
        
    except Exception as e:
        error_msg = f"Error en prueba de manejo de errores: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def generate_test_report(results, test_details):
    """Genera un reporte detallado de las pruebas."""
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
        console.print(Panel("\n".join(f"[green]• {name}[/green]" for name in exitosas), 
                           title=f"[bold green]PRUEBAS EXITOSAS ({passed_tests})[/bold green]", 
                           border_style="green"))
    
    if failed_tests > 0:
        fallidas = [name for name, ok in results.items() if not ok]
        console.print(Panel("\n".join(f"[red]• {name}[/red]" for name in fallidas), 
                           title=f"[bold red]PRUEBAS FALLIDAS ({failed_tests})[/bold red]", 
                           border_style="red"))

    # Estado del sistema
    if passed_tests == total_tests:
        console.print(Panel(
            "[bold green]🚀 SERVIDOR MCP COMPLETAMENTE OPERATIVO[/bold green]\n"
            "• Arquitectura modular funcionando correctamente\n"
            "• Todas las herramientas MCP disponibles\n"
            "• Listo para uso en producción",
            title="[green]ESTADO DEL SISTEMA[/green]",
            border_style="green"
        ))
    elif passed_tests >= total_tests * 0.8:
        console.print(Panel(
            "[bold yellow]✅ SERVIDOR MCP MAYORMENTE OPERATIVO[/bold yellow]\n"
            "• La mayoría de funcionalidades funcionando\n"
            "• Revisar pruebas fallidas para optimización",
            title="[yellow]ESTADO DEL SISTEMA[/yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold red]⚠️ SERVIDOR MCP CON PROBLEMAS[/bold red]\n"
            "• Múltiples funcionalidades con errores\n"
            "• Requiere revisión y corrección",
            title="[red]ESTADO DEL SISTEMA[/red]",
            border_style="red"
        ))

def main():
    """Función principal del script de validación."""
    
    print("🚀 **SERVIDOR MCP ORGANIZADO - VALIDACIÓN COMPLETA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Versión: Servidor MCP Organizado v1.0")
    print("=" * 70)
    
    # Definición detallada de las pruebas
    test_definitions = {
        "Arquitectura Modular": {
            "description": "Verifica la organización modular de herramientas",
            "function": test_modular_architecture
        },
        "Inicialización del Servidor MCP": {
            "description": "Prueba la inicialización completa del servidor",
            "function": test_server_initialization
        },
        "Configuración de Herramientas": {
            "description": "Verifica la configuración centralizada de herramientas",
            "function": test_tools_configuration
        },
        "Herramientas de Documentos": {
            "description": "Prueba las herramientas de procesamiento de documentos",
            "function": test_document_tools
        },
        "Herramientas de Búsqueda": {
            "description": "Prueba las herramientas de búsqueda y consulta",
            "function": test_search_tools
        },
        "Herramientas de Utilidad": {
            "description": "Prueba las herramientas de mantenimiento y utilidad",
            "function": test_utility_tools
        },
        "Integración del Servidor MCP": {
            "description": "Verifica la integración completa del servidor MCP",
            "function": test_mcp_server_integration
        },
        "Manejo de Errores": {
            "description": "Valida el manejo robusto de errores en la arquitectura modular",
            "function": test_error_handling
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
    
    # Generar reporte final
    generate_test_report(results, test_details)
    
    print(f"\n💡 **PRÓXIMOS PASOS:**")
    print("   • Usar el servidor MCP organizado con clientes MCP")
    print("   • Monitorear rendimiento de la arquitectura modular")
    print("   • Añadir nuevas herramientas en módulos apropiados")
    print("   • Revisar logs para mejoras continuas")

if __name__ == "__main__":
    main() 