#!/usr/bin/env python3
"""
Script para mostrar el estado de las herramientas del servidor MCP.
Este script proporciona una vista rápida y visual del estado de todas las herramientas MCP.
"""

import os
import sys
import time
import tempfile
from datetime import datetime

# Importar Rich para mejorar la salida en consola
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def print_header(title):
    """Imprime un encabezado con formato."""
    console.print(Panel(f"[bold blue]{title}[/bold blue]", title="[cyan]Estado MCP[/cyan]"))

def print_section(title):
    """Imprime una sección con formato."""
    console.print(f"\n[bold magenta]{title}[/bold magenta]")
    console.print("[magenta]" + "-" * 40 + "[/magenta]")

def test_mcp_tools():
    """Prueba y muestra el estado de todas las herramientas MCP."""
    print_header("ESTADO DE HERRAMIENTAS MCP")
    
    try:
        # Importar funciones del servidor
        from rag_server import (
            learn_text, learn_document, ask_rag, learn_from_url,
            ask_rag_filtered, get_knowledge_base_stats, get_embedding_cache_stats,
            clear_embedding_cache_tool, optimize_vector_database,
            get_vector_database_stats, reindex_vector_database
        )
        
        # Definir información de herramientas
        tools_info = {
            "learn_text": {
                "description": "Añade texto manual a la base de conocimientos",
                "test_data": {
                    "text": "Prueba del sistema MCP mejorado con procesamiento inteligente.",
                    "source_name": "mcp_test"
                }
            },
            "learn_document": {
                "description": "Procesa documentos con Unstructured avanzado",
                "test_data": {
                    "file_path": None  # Se creará temporalmente
                }
            },
            "learn_from_url": {
                "description": "Procesa contenido de URLs y páginas web",
                "test_data": {
                    "url": "https://httpbin.org/html"
                }
            },
            "ask_rag": {
                "description": "Hace preguntas a la base de conocimientos",
                "test_data": {
                    "query": "¿Qué es el sistema RAG?"
                }
            },
            "ask_rag_filtered": {
                "description": "Preguntas con filtros de metadatos",
                "test_data": {
                    "query": "¿Qué información hay disponible?",
                    "file_type": ".txt"
                }
            },
            "get_knowledge_base_stats": {
                "description": "Obtiene estadísticas de la base de conocimientos",
                "test_data": {}
            },
            "get_embedding_cache_stats": {
                "description": "Obtiene estadísticas del cache de embeddings",
                "test_data": {}
            },
            "clear_embedding_cache_tool": {
                "description": "Limpia el cache de embeddings",
                "test_data": {}
            },
            "optimize_vector_database": {
                "description": "Optimiza la base de datos vectorial",
                "test_data": {}
            },
            "get_vector_database_stats": {
                "description": "Obtiene estadísticas de la base de datos vectorial",
                "test_data": {}
            },
            "reindex_vector_database": {
                "description": "Reindexa la base de datos vectorial",
                "test_data": {
                    "profile": "auto"
                }
            }
        }
        
        # Mapeo de funciones
        tools_functions = {
            "learn_text": learn_text,
            "learn_document": learn_document,
            "learn_from_url": learn_from_url,
            "ask_rag": ask_rag,
            "ask_rag_filtered": ask_rag_filtered,
            "get_knowledge_base_stats": get_knowledge_base_stats,
            "get_embedding_cache_stats": get_embedding_cache_stats,
            "clear_embedding_cache_tool": clear_embedding_cache_tool,
            "optimize_vector_database": optimize_vector_database,
            "get_vector_database_stats": get_vector_database_stats,
            "reindex_vector_database": reindex_vector_database
        }
        
        # Crear archivo temporal para learn_document
        test_doc_content = """
# Documento de Prueba MCP

Este documento prueba el estado de las herramientas MCP.

## Funcionalidades

- Procesamiento de documentos
- Búsqueda inteligente
- Gestión de cache
- Optimización de base de datos

## Estado

El sistema está funcionando correctamente.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_doc_content)
            test_file = f.name
        
        try:
            # Tabla de resultados
            results_table = Table(title="Estado de Herramientas MCP", show_lines=True, header_style="bold blue")
            results_table.add_column("HERRAMIENTA", style="cyan", no_wrap=True)
            results_table.add_column("DESCRIPCIÓN", style="white")
            results_table.add_column("ESTADO", style="bold")
            results_table.add_column("TIEMPO", style="yellow")
            results_table.add_column("RESULTADO", style="green")
            
            results = {}
            
            # Probar cada herramienta con barra de progreso
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Probando herramientas MCP...", total=len(tools_info))
                
                for tool_name, tool_info in tools_info.items():
                    progress.update(task, description=f"Probando {tool_name}...")
                    
                    # Actualizar datos de prueba si es necesario
                    if tool_name == "learn_document":
                        tool_info["test_data"]["file_path"] = test_file
                    
                    # Obtener la función
                    tool_function = tools_functions.get(tool_name)
                    
                    if tool_function is None:
                        status = "❌ NO DISPONIBLE"
                        execution_time = "N/A"
                        result_preview = "Función no encontrada"
                        results[tool_name] = False
                    else:
                        try:
                            # Ejecutar la herramienta
                            start_time = time.time()
                            
                            if tool_name == "learn_text":
                                result = tool_function(
                                    tool_info["test_data"]["text"],
                                    tool_info["test_data"]["source_name"]
                                )
                            elif tool_name == "learn_document":
                                result = tool_function(tool_info["test_data"]["file_path"])
                            elif tool_name == "learn_from_url":
                                result = tool_function(tool_info["test_data"]["url"])
                            elif tool_name == "ask_rag":
                                result = tool_function(tool_info["test_data"]["query"])
                            elif tool_name == "ask_rag_filtered":
                                result = tool_function(
                                    tool_info["test_data"]["query"],
                                    tool_info["test_data"]["file_type"]
                                )
                            elif tool_name == "reindex_vector_database":
                                result = tool_function(tool_info["test_data"]["profile"])
                            else:
                                # Herramientas sin parámetros
                                result = tool_function()
                            
                            execution_time = time.time() - start_time
                            
                            # Analizar resultado
                            if result and len(str(result)) > 0:
                                if "Error" in str(result) or "error" in str(result).lower():
                                    status = "⚠️ CON ADVERTENCIAS"
                                    results[tool_name] = False
                                else:
                                    status = "✅ FUNCIONANDO"
                                    results[tool_name] = True
                            else:
                                status = "⚠️ SIN RESPUESTA"
                                results[tool_name] = False
                            
                            # Mostrar resultado resumido
                            result_preview = str(result)[:30] + "..." if len(str(result)) > 30 else str(result)
                            
                        except Exception as e:
                            status = "❌ ERROR"
                            execution_time = "N/A"
                            result_preview = f"Error: {str(e)[:25]}..."
                            results[tool_name] = False
                    
                    # Añadir a la tabla
                    results_table.add_row(
                        tool_name,
                        tool_info["description"],
                        status,
                        f"{execution_time:.2f}s" if execution_time != "N/A" else "N/A",
                        result_preview
                    )
                    
                    progress.advance(task)
        
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(test_file)
            except:
                pass
        
        # Mostrar tabla de resultados
        console.print(results_table)
        
        # Resumen final
        total_tools = len(results)
        working_tools = sum(1 for success in results.values() if success)
        error_tools = total_tools - working_tools
        
        console.print(Panel(
            f"[bold]Total de herramientas:[/bold] [cyan]{total_tools}[/cyan]\n"
            f"[bold]Funcionando correctamente:[/bold] [green]{working_tools}[/green]\n"
            f"[bold]Con problemas:[/bold] [red]{error_tools}[/red]\n"
            f"[bold]Tasa de éxito:[/bold] [bold yellow]{(working_tools/total_tools)*100:.1f}%[/bold yellow]",
            title="[bold magenta]Resumen del Estado MCP[/bold magenta]",
            border_style="magenta"
        ))
        
        # Mostrar herramientas por estado
        if working_tools > 0:
            working_list = [name for name, ok in results.items() if ok]
            console.print(Panel(
                "\n".join(f"[green]• {name}[/green]" for name in working_list),
                title=f"[bold green]HERRAMIENTAS FUNCIONANDO ({working_tools})[/bold green]",
                border_style="green"
            ))
        
        if error_tools > 0:
            error_list = [name for name, ok in results.items() if not ok]
            console.print(Panel(
                "\n".join(f"[red]• {name}[/red]" for name in error_list),
                title=f"[bold red]HERRAMIENTAS CON PROBLEMAS ({error_tools})[/bold red]",
                border_style="red"
            ))
        
        return True, f"Herramientas MCP verificadas: {working_tools}/{total_tools} funcionando"
        
    except Exception as e:
        error_msg = f"Error verificando herramientas MCP: {str(e)}"
        console.print(f"[red]❌ {error_msg}[/red]")
        return False, error_msg

def main():
    """Función principal."""
    console.print("🔧 **VERIFICACIÓN RÁPIDA DE HERRAMIENTAS MCP**")
    console.print("=" * 60)
    console.print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print("=" * 60)
    
    success, details = test_mcp_tools()
    
    if success:
        console.print(f"\n[green]✅ Verificación completada: {details}[/green]")
    else:
        console.print(f"\n[red]❌ Verificación fallida: {details}[/red]")
    
    console.print("\n💡 **Para más detalles, ejecuta:** `python test_system_validation.py`")

if __name__ == "__main__":
    main() 