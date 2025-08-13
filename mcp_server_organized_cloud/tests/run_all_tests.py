#!/usr/bin/env python3
"""
MCP组织化服务器单元测试脚本。
有序执行所有单元测试并生成详细报告。
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

# 添加 src 目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def print_header(title):
    """打印格式化标题。"""
    console.print(Panel(f"[bold blue]{title}[/bold blue]", title="[cyan]单元测试[/cyan]"))

def run_test_suite():
    """执行所有单元测试。"""
    print_header("正在执行MCP组织化服务器单元测试")
    
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 发现并加载所有测试
    test_suites = []
    test_results = {}
    
    # 测试文件列表
    test_files = [
        "test_document_tools",
        "test_search_tools", 
        "test_utility_tools"
    ]
    
    print(f"\n[bold magenta]正在发现 {len(test_files)} 个模块中的测试...[/bold magenta]")
    
    for test_file in test_files:
        try:
            # 导入测试模块
            module = __import__(test_file)
            
            # 加载模块中的测试
            suite = loader.loadTestsFromModule(module)
            test_suites.append(suite)
            
            # 统计模块中的测试数量
            test_count = suite.countTestCases()
            test_results[test_file] = {
                "suite": suite,
                "count": test_count,
                "status": "loaded"
            }
            
            console.print(f"✅ [green]{test_file}[/green]: 加载了 {test_count} 个测试")
            
        except ImportError as e:
            console.print(f"❌ [red]{test_file}[/red]: 导入出错 - {e}")
            test_results[test_file] = {
                "suite": None,
                "count": 0,
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            console.print(f"❌ [red]{test_file}[/red]: 未知错误 - {e}")
            test_results[test_file] = {
                "suite": None,
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    # 执行测试
    print(f"\n[bold magenta]正在执行 {sum(result['count'] for result in test_results.values() if result['status'] == 'loaded')} 个测试...[/bold magenta]")
    
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
                    console.print(f"✅ [green]{test_file}[/green]: {execution_result.testsRun} 个测试全部通过")
                else:
                    console.print(f"❌ [red]{test_file}[/red]: {execution_result.testsRun} 个测试，{len(execution_result.failures)} 失败，{len(execution_result.errors)} 错误")
                
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
    """生成详细测试报告。"""
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
        f"[bold]模块总数:[/bold] [cyan]{total_modules}[/cyan]\n"
        f"[bold]成功模块:[/bold] [green]{successful_modules}[/green]\n"
        f"[bold]测试总数:[/bold] [cyan]{total_tests}[/cyan]\n"
        f"[bold]成功测试:[/bold] [green]{total_tests - total_failures - total_errors}[/green]\n"
        f"[bold]失败:[/bold] [red]{total_failures}[/red]\n"
        f"[bold]错误:[/bold] [red]{total_errors}[/red]\n"
        f"[bold]跳过:[/bold] [yellow]{total_skipped}[/yellow]\n"
        f"[bold]成功率:[/bold] [bold yellow]{((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0:.1f}%[/bold yellow]",
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
            status = "[green]✅ 成功[/green]"
        elif result["errors"] > 0:
            status = "[red]❌ 错误[/red]"
        else:
            status = "[yellow]⚠️ 失败[/yellow]"
        
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
            "[bold green]🚀 所有单元测试均成功[/bold green]\n"
            "• 模块化代码运行正常\n"
            "• 各功能已验证\n"
            "• 可进行完整集成",
            title="[green]系统状态[/green]",
            border_style="green"
        ))
    elif successful_modules >= total_modules * 0.7:
        console.print(Panel(
            "[bold yellow]✅ 大部分单元测试成功[/bold yellow]\n"
            "• 大部分功能正常运行\n"
            "• 请检查有问题的模块\n"
            "• 系统功能正常，有一些警告",
            title="[yellow]系统状态[/yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold red]⚠️ 多个单元测试失败[/bold red]\n"
            "• 多个模块存在问题\n"
            "• 需要检查和修正\n"
            "• 系统功能不完全",
            title="[red]系统状态[/red]",
            border_style="red"
        ))

def save_test_report(test_results, execution_results):
    """将测试报告保存到文件。"""
    try:
        report_filename = f"unit_tests_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("MCP组织化服务器单元测试报告\n")
            f.write("=" * 70 + "\n")
            f.write(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Estadísticas generales
            total_tests = sum(result["tests_run"] for result in execution_results.values())
            total_failures = sum(result["failures"] for result in execution_results.values())
            total_errors = sum(result["errors"] for result in execution_results.values())
            successful_modules = sum(1 for result in execution_results.values() if result["success"])
            total_modules = len(execution_results)
            
            f.write(f"总览:\n")
            f.write(f"  Total de módulos: {total_modules}\n")
            f.write(f"  Módulos exitosos: {successful_modules}\n")
            f.write(f"  Total de pruebas: {total_tests}\n")
            f.write(f"  Pruebas exitosas: {total_tests - total_failures - total_errors}\n")
            f.write(f"  Fallos: {total_failures}\n")
            f.write(f"  Errores: {total_errors}\n\n")
            
            # Resultados por módulo
            f.write("各模块结果:\n")
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
    console.print("   • 验证系统完整功能")
    console.print("   • Documentar casos de uso específicos")

if __name__ == "__main__":
    main() 