import time
import sys
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

try:
    log("--- Iniciando prueba de carga de modelo ---")
    log("Importando SentenceTransformer...")
    from sentence_transformers import SentenceTransformer
    log("Importación exitosa.")

    MODEL_NAME = "all-MiniLM-L6-v2"
    
    log(f"Intentando cargar el modelo '{MODEL_NAME}' a la memoria...")
    log("Esto debería tardar solo unos segundos si el modelo está cacheado.")
    
    start_time = time.time()
    # Esta es la línea que se está bloqueando en el servidor RAG
    model = SentenceTransformer(MODEL_NAME, device='cpu')
    end_time = time.time()
    
    log("\n" + "-"*20 + " ¡ÉXITO! " + "-"*20)
    log(f"✅ Modelo cargado exitosamente en {end_time - start_time:.2f} segundos.")
    log(f"El objeto del modelo es: {model}")
    log("Esto confirma que la librería y el modelo en caché funcionan correctamente.")

except Exception as e:
    log(f"\n" + "-"*20 + " ¡ERROR! " + "-"*20)
    log(f"❌ Falló la carga del modelo: {e}")
    import traceback
    traceback.print_exc() 