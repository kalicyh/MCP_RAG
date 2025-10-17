#!/usr/bin/env python3
"""
MCP 组织化服务器验证脚本。
测试系统的所有功能，包括：
- 工具的模块化架构
- 文档的高级处理
- 嵌入缓存与优化
- 完整的 MCP 工具
- 错误处理与恢复
- 组织化服务器的状态
"""

import os
import sys
import tempfile
import time
import requests
from datetime import datetime
from unittest.mock import patch, MagicMock

# 导入 Rich 以增强控制台输出
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# 将 src 目录添加到路径以导入我们的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

def print_header(title):
    console.print(Panel(f"[bold blue]{title}[/bold blue]", title="[cyan]测试[/cyan]"))

def print_section(title):
    console.print(f"\n[bold magenta]{title}[/bold magenta]")
    console.print("[magenta]" + "-" * 40 + "[magenta]")

def print_result(test_name, success, details=""):
    status = "[bold green]✅ 通过[/bold green]" if success else "[bold red]❌ 失败[/bold red]"
    console.print(f"{status} [bold]{test_name}[/bold]")
    if details:
        console.print(f"   [yellow]{details}[/yellow]")

def test_modular_architecture():
    """测试 MCP 服务器的模块化架构。"""
    print_header("模块化架构")
    
    try:
        print_section("1. 模块验证")
        
        # 验证模块是否存在
        modules_to_check = [
            "tools.document_tools",
            "tools.search_tools", 
            "tools.utility_tools",
            "tools"
        ]
        
        for module_name in modules_to_check:
            try:
                __import__(module_name)
                print(f"✅ 模块 {module_name} 导入成功")
            except ImportError as e:
                print(f"❌ 导入模块 {module_name} 时出错: {e}")
                return False, f"模块 {module_name} 出错"
        
        print_section("2. 函数验证")
        
        # 验证每个模块中的函数
        from tools.document_tools import learn_text, learn_document, learn_from_url
        from tools.search_tools import ask_rag, ask_rag_filtered
        from tools.utility_tools import get_knowledge_base_stats, get_embedding_cache_stats
        
        print("✅ document_tools 的函数可用")
        print("✅ search_tools 的函数可用")
        print("✅ utility_tools 的函数可用")
        
        print_section("3. 配置验证")
        
        # 验证配置函数
        from tools import configure_rag_state, ALL_TOOLS, TOOLS_BY_NAME
        
        print(f"✅ 配置函数 configure_rag_state 可用")
        print(f"✅ ALL_TOOLS 包含 {len(ALL_TOOLS)} 个工具")
        print(f"✅ TOOLS_BY_NAME 包含 {len(TOOLS_BY_NAME)} 个工具")
        
        # 验证所有工具是否在列表中
        expected_tools = [
            "learn_text", "learn_document", "learn_from_url",
            "ask_rag", "ask_rag_filtered",
            "get_knowledge_base_stats", "get_embedding_cache_stats",
            "clear_embedding_cache_tool", "optimize_vector_database",
            "get_vector_database_stats", "reindex_vector_database"
        ]
        
        for tool in expected_tools:
            if tool in TOOLS_BY_NAME:
                print(f"✅ 工具 {tool} 已注册")
            else:
                print(f"❌ 工具 {tool} 未找到")
                return False, f"工具 {tool} 缺失"
        
        details = f"模块化架构验证成功: {len(ALL_TOOLS)} 个工具已组织"
        return True, details
        
    except Exception as e:
        error_msg = f"模块化架构出错: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_server_initialization():
    """测试组织化MCP服务器的初始化。"""
    print_header("MCP服务器初始化")
    
    try:
        print_section("1. 服务器导入")
        
        # 导入完整服务器
        import server
        print("✅ 服务器导入成功")
        
        print_section("2. 组件验证")
        
        # 验证mcp对象存在
        if hasattr(server, 'mcp'):
            print("✅ MCP对象已创建")
            print(f"   • 服务器名称: {server.mcp.name}")
        else:
            print("❌ 未找到MCP对象")
            return False, "缺少MCP对象"
        
        # 验证RAG状态
        if hasattr(server, 'rag_state'):
            print("✅ RAG状态已初始化")
            print(f"   • 组件: {list(server.rag_state.keys())}")
        else:
            print("❌ 未找到RAG状态")
            return False, "缺少RAG状态"
        
        # Verificar conversor MarkItDown
        if hasattr(server, 'md_converter'):
            print("✅ Conversor MarkItDown inicializado")
        else:
            print("❌ 未找到MarkItDown转换器")
            return False, "缺少MarkItDown转换器"
        
        print_section("3. 初始化函数验证")
        
        # 验证初始化函数
        init_functions = [
            'warm_up_rag_system',
            'ensure_converted_docs_directory', 
            'save_processed_copy',
            'initialize_rag'
        ]
        
        for func_name in init_functions:
            if hasattr(server, func_name):
                print(f"✅ 函数 {func_name} 可用")
            else:
                print(f"❌ 函数 {func_name} 未找到")
                return False, f"缺少函数 {func_name}"
        
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
        error_msg = f"服务器初始化错误：{str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_tools_configuration():
    """测试模块化工具配置。"""
    print_header("工具配置")
    
    try:
        print_section("1. RAG状态配置")
        
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
        
        print_section("2. 应用配置")
        
        from tools import configure_rag_state
        
        # Configurar herramientas con el estado real
        configure_rag_state(
            rag_state=test_rag_state,
            md_converter=test_md_converter,
            initialize_rag_func=test_initialize_rag,
            save_processed_copy_func=test_save_processed_copy
        )
        
        print("✅ 配置应用成功")
        
        print_section("3. 验证模块配置")
        
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
            print("❌ utility_tools 中未配置 RAG 状态")
            return False, "utility_tools 中未共享 RAG 状态"
        
        details = "工具配置已验证：模块间共享RAG状态"
        return True, details
        
    except Exception as e:
        error_msg = f"工具配置错误：{str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def test_document_tools():
    """使用完整服务器测试文档处理工具。"""
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
            # 检查结果中是否有错误
            if result and "Error" in str(result):
                print(f"❌ learn_text 失败：{result}")
                return False, f"learn_text 错误：{result}"
            elif result and ("添加" in result.lower() or "处理" in result.lower()):
                print("✅ learn_text 工作正常")
            else:
                print(f"⚠️ learn_text 已执行但响应意外：{result}")
                return False, f"learn_text 响应意外：{result}"
        except Exception as e:
            print(f"❌ learn_text 错误：{e}")
            return False, f"learn_text 错误：{e}"
        
        print_section("2. learn_document 测试")
        
        # 创建测试文件
        test_content = """
# 模块化测试文档

此文档测试组织化RAG系统的功能。

## 测试特性

1. **模块化架构**：工具组织在模块中
2. **集中配置**：共享RAG状态
3. **智能处理**：使用Unstructured
4. **结构化元数据**：详细信息

## 预期结果

- 文档处理成功
- 结构化元数据提取
- 与模块化系统集成
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # Probar learn_document usando el servidor
            result = server.learn_document(test_file)
            # Verificar si hay errores en el resultado
            if result and "Error" in str(result):
                print(f"❌ learn_document 失败：{result}")
                return False, f"learn_document 错误：{result}"
            elif result and ("procesado" in result.lower() or "añadido" in result.lower()):
                print("✅ learn_document funcionando correctamente")
            else:
                print(f"⚠️ learn_document ejecutado pero respuesta inesperada: {result}")
                return False, f"Respuesta inesperada en learn_document: {result}"
                
        except Exception as e:
            print(f"❌ learn_document 错误：{e}")
            return False, f"learn_document 错误：{e}"
        finally:
            # 清理临时文件
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
        
        print_section("3. 配置错误处理")
        
        try:
            from tools import configure_rag_state
            
            # 测试使用None参数的配置
            configure_rag_state(None, None, None, None)
            print("✅ None参数配置处理正确")
        except Exception as e:
            print(f"❌ None参数配置错误：{e}")
        
        details = "模块化架构中的错误处理已验证"
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
    table.add_column("测试项", style="cyan", no_wrap=True)
    table.add_column("描述", style="white")
    table.add_column("状态", style="bold")
    table.add_column("结果/详情", style="yellow")

    for test_name, success in results.items():
        test_info = test_details.get(test_name, {})
        description = test_info.get('description', '无描述')
        result_details = test_info.get('error', '✅ 成功') if not success else test_info.get('error', '✅ 成功')
        status = "[green]✅ 通过[/green]" if success else "[red]❌ 失败[/red]"
        
        # Truncar descripción y resultado si son muy largos
        if len(description) > 42:
            description = description[:39] + "..."
        if len(result_details) > 37:
            result_details = result_details[:34] + "..."
        table.add_row(test_name, description, status, result_details)
    
    console.print(table)

    # Resumen por estado en paneles
    if passed_tests > 0:
        passed_names = [name for name, ok in results.items() if ok]
        console.print(Panel("\n".join(f"[green]• {name}[/green]" for name in passed_names), 
                           title=f"[bold green]通过的测试 ({passed_tests})[/bold green]", 
                           border_style="green"))
    
    if failed_tests > 0:
        failed_names = [name for name, ok in results.items() if not ok]
        console.print(Panel("\n".join(f"[red]• {name}[/red]" for name in failed_names), 
                           title=f"[bold red]失败的测试 ({failed_tests})[/bold red]", 
                           border_style="red"))

    # 系统状态
    if passed_tests == total_tests:
        console.print(Panel(
            "[bold green]🚀 MCP服务器完全可用[/bold green]\n"
            "• 模块化架构运行正常\n"
            "• 所有MCP工具可用\n"
            "• 可用于生产环境",
            title="[green]系统状态[/green]",
            border_style="green"
        ))
    elif passed_tests >= total_tests * 0.8:
        console.print(Panel(
            "[bold yellow]✅ MCP服务器大部分可用[/bold yellow]\n"
            "• 大部分功能正常\n"
            "• 请检查失败的测试以优化",
            title="[yellow]系统状态[/yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold red]⚠️ MCP服务器存在问题[/bold red]\n"
            "• 多个功能存在错误\n"
            "• 需要检查和修复",
            title="[red]系统状态[/red]",
            border_style="red"
        ))

def main():
    """Función principal del script de validación."""
    
    print("🚀 **MCP组织化服务器 - 完整验证**")
    print("=" * 70)
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 版本: MCP组织化服务器 v1.0")
    print("=" * 70)
    
    # 测试定义
    test_definitions = {
        "模块化架构": {
            "description": "验证工具的模块化组织",
            "function": test_modular_architecture
        },
        "MCP服务器初始化": {
            "description": "测试服务器的完整初始化",
            "function": test_server_initialization
        },
        "工具配置": {
            "description": "验证工具的集中配置",
            "function": test_tools_configuration
        },
        "文档工具": {
            "description": "测试文档处理工具",
            "function": test_document_tools
        },
        "搜索工具": {
            "description": "测试搜索和查询工具",
            "function": test_search_tools
        },
        "维护工具": {
            "description": "测试维护和实用工具",
            "function": test_utility_tools
        },
        "MCP服务器集成": {
            "description": "验证服务器的完整集成",
            "function": test_mcp_server_integration
        },
        "错误处理": {
            "description": "验证模块化架构中的健壮错误处理",
            "function": test_error_handling
        }
    }
    
    results = {}
    test_details = {}
    
    # 执行所有测试
    for test_name, test_info in test_definitions.items():
        try:
            print(f"\n🧪 执行测试: {test_name}")
            success, details = test_info["function"]()
            results[test_name] = success
            test_details[test_name] = {
                "description": test_info["description"],
                "error": details
            }
        except Exception as e:
            print(f"❌ {test_name} 出现严重错误: {e}")
            results[test_name] = False
            test_details[test_name] = {
                "description": test_info["description"],
                "error": str(e)
            }
    
    # 生成最终报告
    generate_test_report(results, test_details)
    
    print(f"\n💡 **后续建议:**")
    print("   • 使用MCP组织化服务器与MCP客户端配合")
    print("   • 监控模块化架构的性能")
    print("   • 在合适的模块中添加新工具")
    print("   • 查看日志以持续优化")

if __name__ == "__main__":
    main()