# pre_download_model.py
import sys
from sentence_transformers import SentenceTransformer

def log(message: str):
    """Imprime un mensaje en la consola."""
    print(message, file=sys.stderr, flush=True)

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