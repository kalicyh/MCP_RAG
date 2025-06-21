import time
import sys

def log(message: str):
    """Imprime un mensaje en la consola."""
    print(message, file=sys.stdout, flush=True)

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