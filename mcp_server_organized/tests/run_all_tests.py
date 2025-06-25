#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas unitarias del servidor MCP organizado.
Ejecuta las pruebas de manera organizada y genera un reporte detallado.
"""

import unittest
import sys
import os
from datetime import datetime
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Añadir el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def print_header(title):
    """Imprime un encabezado con formato."""
    console.print(Panel(f"[bold blue]{title}[/bold blue]", title="[cyan]Pruebas Unitarias[/cyan]"))

def run_test_suite():
    """Ejecuta todas las pruebas unitarias."""
    print_header("EJECUTANDO PRUEBAS UNITARIAS DEL SERVIDOR MCP")
    
    # Crear el test loader
    loader = unittest.TestLoader()
    
    # Descubrir y cargar todas las pruebas
    test_suites = []
    test_results = {}
    
    # Lista de archivos de prueba
    test_files = [
        "test_document_tools",
        "test_search_tools", 
        "test_utility_tools"
    ]
    
    print(f"\n[bold magenta]Descubriendo pruebas en {len(test_files)} módulos...[/bold magenta]")
    
    for test_file in test_files:
        try:
            # Importar el módulo de pruebas
            module = __import__(test_file)
            
            # Cargar las pruebas del módulo
            suite = loader.loadTestsFromModule(module)
            test_suites.append(suite)
            
            # Contar pruebas en el módulo
            test_count = suite.countTestCases()
            test_results[test_file] = {
                "suite": suite,
                "count": test_count,
                "status": "loaded"
            }
            
            console.print(f"✅ [green]{test_file}[/green]: {test_count} pruebas cargadas")
            
        except ImportError as e:
            console.print(f"❌ [red]{test_file}[/red]: Error al importar - {e}")
            test_results[test_file] = {
                "suite": None,
                "count": 0,
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            console.print(f"❌ [red]{test_file}[/red]: Error inesperado - {e}")
            test_results[test_file] = {
                "suite": None,
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    # Ejecutar las pruebas
    print(f"\n[bold magenta]Ejecutando {sum(result['count'] for result in test_results.values() if result['status'] == 'loaded')} pruebas...[/bold magenta]")
    
    # Crear runner
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Ejecutar cada suite
    execution_results = {}
    
    for test_file, result in test_results.items():
        if result["status"] == "loaded":
            try:
                console.print(f"\n[bold yellow]Ejecutando: {test_file}[/bold yellow]")
                execution_result = runner.run(result["suite"])
                
                execution_results[test_file] = {
                    "tests_run": execution_result.testsRun,
                    "failures": len(execution_result.failures),
                    "errors": len(execution_result.errors),
                    "skipped": len(execution_result.skipped) if hasattr(execution_result, 'skipped') else 0,
                    "success": execution_result.wasSuccessful()
                }
                
                if execution_result.wasSuccessful():
                    console.print(f"✅ [green]{test_file}[/green]: {execution_result.testsRun} pruebas exitosas")
                else:
                    console.print(f"❌ [red]{test_file}[/red]: {execution_result.testsRun} pruebas, {len(execution_result.failures)} fallos, {len(execution_result.errors)} errores")
                
            except Exception as e:
                console.print(f"❌ [red]{test_file}[/red]: Error durante ejecución - {e}")
                execution_results[test_file] = {
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "success": False,
                    "error": str(e)
                }
        else:
            execution_results[test_file] = {
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
                "success": False,
                "error": result.get("error", "No se pudo cargar")
            }
    
    return test_results, execution_results

def generate_test_report(test_results, execution_results):
    """Genera un reporte detallado de las pruebas."""
    print_header("REPORTE DE PRUEBAS UNITARIAS")
    
    # Calcular estadísticas generales
    total_tests = sum(result["tests_run"] for result in execution_results.values())
    total_failures = sum(result["failures"] for result in execution_results.values())
    total_errors = sum(result["errors"] for result in execution_results.values())
    total_skipped = sum(result["skipped"] for result in execution_results.values())
    successful_modules = sum(1 for result in execution_results.values() if result["success"])
    total_modules = len(execution_results)
    
    # Resumen general
    console.print(Panel(
        f"[bold]Total de módulos:[/bold] [cyan]{total_modules}[/cyan]\n"
        f"[bold]Módulos exitosos:[/bold] [green]{successful_modules}[/green]\n"
        f"[bold]Total de pruebas:[/bold] [cyan]{total_tests}[/cyan]\n"
        f"[bold]Pruebas exitosas:[/bold] [green]{total_tests - total_failures - total_errors}[/green]\n"
        f"[bold]Fallos:[/bold] [red]{total_failures}[/red]\n"
        f"[bold]Errores:[/bold] [red]{total_errors}[/red]\n"
        f"[bold]Omitidas:[/bold] [yellow]{total_skipped}[/yellow]\n"
        f"[bold]Tasa de éxito:[/bold] [bold yellow]{((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0:.1f}%[/bold yellow]",
        title="[bold magenta]Resumen General[/bold magenta]",
        border_style="magenta"
    ))
    
    # Tabla detallada por módulo
    table = Table(title="Resultados por Módulo", show_lines=True, header_style="bold blue")
    table.add_column("MÓDULO", style="cyan", no_wrap=True)
    table.add_column("PRUEBAS", style="white", justify="center")
    table.add_column("EXITOSAS", style="green", justify="center")
    table.add_column("FALLOS", style="red", justify="center")
    table.add_column("ERRORES", style="red", justify="center")
    table.add_column("ESTADO", style="bold")
    
    for module_name, result in execution_results.items():
        successful_tests = result["tests_run"] - result["failures"] - result["errors"]
        
        if result["success"]:
            status = "[green]✅ EXITOSO[/green]"
        elif result["errors"] > 0:
            status = "[red]❌ ERROR[/red]"
        else:
            status = "[yellow]⚠️ FALLOS[/yellow]"
        
        table.add_row(
            module_name,
            str(result["tests_run"]),
            str(successful_tests),
            str(result["failures"]),
            str(result["errors"]),
            status
        )
    
    console.print(table)
    
    # Mostrar módulos por estado
    if successful_modules > 0:
        successful_list = [name for name, result in execution_results.items() if result["success"]]
        console.print(Panel(
            "\n".join(f"[green]• {name}[/green]" for name in successful_list),
            title=f"[bold green]MÓDULOS EXITOSOS ({successful_modules})[/bold green]",
            border_style="green"
        ))
    
    failed_modules = total_modules - successful_modules
    if failed_modules > 0:
        failed_list = [name for name, result in execution_results.items() if not result["success"]]
        console.print(Panel(
            "\n".join(f"[red]• {name}[/red]" for name in failed_list),
            title=f"[bold red]MÓDULOS CON PROBLEMAS ({failed_modules})[/bold red]",
            border_style="red"
        ))
    
    # Estado del sistema
    if successful_modules == total_modules and total_tests > 0:
        console.print(Panel(
            "[bold green]🚀 TODAS LAS PRUEBAS UNITARIAS EXITOSAS[/bold green]\n"
            "• Código modular funcionando correctamente\n"
            "• Funciones individuales validadas\n"
            "• Listo para integración completa",
            title="[green]ESTADO DEL SISTEMA[/green]",
            border_style="green"
        ))
    elif successful_modules >= total_modules * 0.7:
        console.print(Panel(
            "[bold yellow]✅ MAYORÍA DE PRUEBAS UNITARIAS EXITOSAS[/bold yellow]\n"
            "• La mayoría de funciones funcionando correctamente\n"
            "• Revisar módulos con problemas\n"
            "• Sistema funcional con algunas advertencias",
            title="[yellow]ESTADO DEL SISTEMA[/yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold red]⚠️ MÚLTIPLES PRUEBAS UNITARIAS FALLIDAS[/bold red]\n"
            "• Varios módulos con problemas\n"
            "• Requiere revisión y corrección\n"
            "• Sistema no completamente funcional",
            title="[red]ESTADO DEL SISTEMA[/red]",
            border_style="red"
        ))

def save_test_report(test_results, execution_results):
    """Guarda el reporte de pruebas en un archivo."""
    try:
        report_filename = f"unit_tests_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE PRUEBAS UNITARIAS - SERVIDOR MCP ORGANIZADO\n")
            f.write("=" * 70 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Estadísticas generales
            total_tests = sum(result["tests_run"] for result in execution_results.values())
            total_failures = sum(result["failures"] for result in execution_results.values())
            total_errors = sum(result["errors"] for result in execution_results.values())
            successful_modules = sum(1 for result in execution_results.values() if result["success"])
            total_modules = len(execution_results)
            
            f.write(f"RESUMEN GENERAL:\n")
            f.write(f"  Total de módulos: {total_modules}\n")
            f.write(f"  Módulos exitosos: {successful_modules}\n")
            f.write(f"  Total de pruebas: {total_tests}\n")
            f.write(f"  Pruebas exitosas: {total_tests - total_failures - total_errors}\n")
            f.write(f"  Fallos: {total_failures}\n")
            f.write(f"  Errores: {total_errors}\n\n")
            
            # Resultados por módulo
            f.write("RESULTADOS POR MÓDULO:\n")
            f.write("-" * 50 + "\n")
            
            for module_name, result in execution_results.items():
                successful_tests = result["tests_run"] - result["failures"] - result["errors"]
                status = "EXITOSO" if result["success"] else "FALLIDO"
                
                f.write(f"{module_name}:\n")
                f.write(f"  Pruebas: {result['tests_run']}\n")
                f.write(f"  Exitosas: {successful_tests}\n")
                f.write(f"  Fallos: {result['failures']}\n")
                f.write(f"  Errores: {result['errors']}\n")
                f.write(f"  Estado: {status}\n")
                
                if "error" in result:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        console.print(f"📄 [green]Reporte guardado en: {report_filename}[/green]")
        
    except Exception as e:
        console.print(f"⚠️ [yellow]No se pudo guardar el reporte: {e}[/yellow]")

def main():
    """Función principal."""
    console.print("🧪 **PRUEBAS UNITARIAS DEL SERVIDOR MCP ORGANIZADO**")
    console.print("=" * 70)
    console.print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print("=" * 70)
    
    # Ejecutar pruebas
    test_results, execution_results = run_test_suite()
    
    # Generar reporte
    generate_test_report(test_results, execution_results)
    
    # Guardar reporte
    save_test_report(test_results, execution_results)
    
    console.print(f"\n💡 **PRÓXIMOS PASOS:**")
    console.print("   • Revisar pruebas fallidas para correcciones")
    console.print("   • Ejecutar pruebas de integración")
    console.print("   • Validar funcionalidad completa del sistema")
    console.print("   • Documentar casos de uso específicos")

if __name__ == "__main__":
    main() 