"""
Logger Module para el Servidor MCP
=================================

Este módulo proporciona funcionalidades de logging mejoradas para el servidor MCP,
utilizando Rich para una salida en consola más atractiva y organizada.
"""

# Importar Rich para mejorar la salida en consola
from rich import print as rich_print
from rich.panel import Panel
from datetime import datetime
import sys

def log(message: str):
    """
    Imprime un mensaje en la consola usando Rich con formato mejorado.
    
    Args:
        message: El mensaje a imprimir
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)

    # Detectar el tipo de mensaje basado en palabras clave
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
    Imprime un mensaje con timestamp y nivel de log.
    
    Args:
        message: El mensaje a imprimir
        level: Nivel del log (INFO, WARNING, ERROR, SUCCESS)
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
    Imprime un mensaje específico del servidor MCP.
    
    Args:
        message: El mensaje a imprimir
    """
    log(f"MCP Server: {message}")

def log_rag_system(message: str):
    """
    Imprime un mensaje específico del sistema RAG.
    
    Args:
        message: El mensaje a imprimir
    """
    log(f"RAG System: {message}")

def log_document_processing(message: str):
    """
    Imprime un mensaje específico del procesamiento de documentos.
    
    Args:
        message: El mensaje a imprimir
    """
    log(f"Document Processing: {message}")

def log_vector_store(message: str):
    """
    Imprime un mensaje específico de la base de datos vectorial.
    
    Args:
        message: El mensaje a imprimir
    """
    log(f"Vector Store: {message}") 