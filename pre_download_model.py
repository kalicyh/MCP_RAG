# pre_download_model.py
import sys
from sentence_transformers import SentenceTransformer
# Importar Rich para mejorar la salida en consola
from rich import print as rich_print
from rich.panel import Panel

def log(message: str):
    """Imprime un mensaje en la consola usando Rich."""
    if any(word in message.lower() for word in ["error", "falló", "fatal", "excepción"]):
        rich_print(Panel(f"{message}", title="[red]Error[/red]", style="bold red"))
    elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok"]):
        rich_print(f"[bold green]{message}[/bold green]")
    else:
        rich_print(message)

# El modelo de embedding que usa nuestro sistema
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def download_embedding_model():
    """
    Descarga y cachea el modelo de embedding de HuggingFace.
    Esto es útil para la primera ejecución, para que el usuario vea el progreso.
    """
    log(f"Iniciando la descarga del modelo de embedding: {EMBEDDING_MODEL_NAME}")
    log("Esto puede tardar varios minutos dependiendo de tu conexión a internet.")
    log("La descarga se guardará en la caché de HuggingFace para futuras ejecuciones.")
    log("-" * 60)

    try:
        # Al instanciar SentenceTransformer, se descarga y cachea el modelo.
        # El progreso de la descarga se debería mostrar automáticamente en la consola.
        SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
        
        log("-" * 60)
        log("✅ ¡Modelo de embedding descargado y cacheado exitosamente!")
        log("Ahora el servidor RAG se iniciará mucho más rápido.")

    except Exception as e:
        log(f"\n❌ Error durante la descarga del modelo: {e}")
        log("Por favor, verifica tu conexión a internet e inténtalo de nuevo.")
        log("Si el problema persiste, puede ser un problema con los servidores de HuggingFace o un firewall.")

if __name__ == "__main__":
    download_embedding_model() 