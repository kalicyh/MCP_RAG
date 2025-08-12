"""
MCP 服务器日志模块
=================

此模块为 MCP 服务器提供增强的日志功能，
使用 Rich 获得更具吸引力和组织性的控制台输出。
"""

# 导入 Rich 以改善控制台输出
from rich import print as rich_print
from rich.panel import Panel
from datetime import datetime
import sys

def log(message: str):
    """
    使用 Rich 以改进的格式在控制台打印消息。
    
    参数：
        message: 要打印的消息
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)

    # 基于关键词检测消息类型
    #if any(word in message.lower() for word in ["error", "falló", "fatal", "excepción", "failed"]):
    #    rich_print(Panel(f"{message}", title="[red]Error[/red]", style="bold red"))
    #elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok", "success"]):
    #    rich_print(f"[bold green]{message}[/bold green]")
    #elif any(word in message.lower() for word in ["advertencia", "warning", "cuidado"]):
    #    rich_print(f"[bold yellow]{message}[/bold yellow]")
    #elif any(word in message.lower() for word in ["info", "información", "debug"]):
    #    rich_print(f"[bold blue]{message}[/bold blue]")
    #else:
    #    rich_print(message)

def log_with_timestamp(message: str, level: str = "INFO"):
    """
    打印带时间戳和日志级别的消息。
    
    参数：
        message: 要打印的消息
        level: 日志级别（INFO, WARNING, ERROR, SUCCESS）
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)

    #if level.upper() == "ERROR":
    #    rich_print(Panel(f"[{timestamp}] {message}", title="[red]ERROR[/red]", style="bold red"))
    #elif level.upper() == "WARNING":
    #    rich_print(f"[bold yellow][{timestamp}] WARNING: {message}[/bold yellow]")
    #elif level.upper() == "SUCCESS":
    #    rich_print(f"[bold green][{timestamp}] SUCCESS: {message}[/bold green]")
    #else:
    #    rich_print(f"[bold blue][{timestamp}] INFO: {message}[/bold blue]")

def log_mcp_server(message: str):
    """
    打印 MCP 服务器特定的消息。
    
    参数：
        message: 要打印的消息
    """
    log(f"MCP服务器: {message}")

def log_rag_system(message: str):
    """
    打印 RAG 系统特定的消息。
    
    参数：
        message: 要打印的消息
    """
    log(f"RAG系统: {message}")

def log_document_processing(message: str):
    """
    打印文档处理特定的消息。
    
    参数：
        message: 要打印的消息
    """
    log(f"文档处理: {message}")

def log_vector_store(message: str):
    """
    打印向量数据库特定的消息。
    
    参数：
        message: 要打印的消息
    """
    log(f"向量存储: {message}") 