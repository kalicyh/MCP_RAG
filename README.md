# Servidor RAG Personal con MCP

Este proyecto implementa un servidor compatible con el Protocolo de Contexto de Modelo (MCP) que dota a los clientes de IA (como Cursor, Claude for Desktop, etc.) de una capacidad de Recuperación Aumentada por Generación (RAG). Permite al modelo de lenguaje acceder a una base de conocimiento privada y local, alimentada por tus propios textos y documentos.

## ✨ Características

- **Memoria Persistente para tu IA:** "Enseña" a tu IA nueva información que recordará entre sesiones.
- **Procesamiento de Documentos:** Alimenta la base de conocimiento con archivos `.pdf`, `.docx`, `.pptx`, `.txt`, y más, gracias a la integración con [Microsoft MarkItDown](https://github.com/microsoft/markitdown).
- **LLM Local y Privado:** Utiliza modelos de lenguaje locales a través de [Ollama](https://ollama.com/) (ej. Llama 3, Mistral), asegurando que tus datos y preguntas nunca salgan de tu máquina.
- **100% Local y Offline:** Tanto el modelo de lenguaje como los embeddings se ejecutan en tu máquina. Ningún dato sale a internet. Una vez descargados los modelos, funciona sin conexión.
- **Ingesta Masiva:** Un script dedicado para procesar directorios enteros de documentos y construir la base de conocimiento de manera eficiente.
- **Arquitectura Modular:** La lógica del RAG está separada de los scripts de servidor y de ingesta, facilitando el mantenimiento y la expansión.
- **Copias en Markdown:** Cada documento procesado se guarda automáticamente en formato Markdown para verificación y reutilización.
- **🆕 Metadatos de Fuente:** Rastreabilidad completa de información con atribución de fuentes en cada respuesta.
- **🆕 Optimizado para Agentes de IA:** Descripciones detalladas y manejo de errores inteligente para uso efectivo por agentes de IA.

---

## 🏗️ Arquitectura

El proyecto está dividido en tres componentes principales:

1.  `rag_core.py`: El corazón del sistema. Contiene toda la lógica reutilizable para manejar la base de datos vectorial (ChromaDB), procesar texto y crear la cadena de preguntas y respuestas con LangChain. **Incluye soporte para metadatos de fuente.**
2.  `rag_server.py`: El servidor MCP. Expone las herramientas (`learn_text`, `learn_document`, `ask_rag`) que el cliente de IA puede invocar. Se comunica a través de `stdio`. **Optimizado con descripciones detalladas para agentes de IA.**
3.  `bulk_ingest.py`: Un script de línea de comandos para procesar una carpeta llena de documentos y añadirlos a la base de conocimiento de forma masiva. **Incluye metadatos de fuente automáticos.**

### Archivos de Documentación:
- `AGENT_INSTRUCTIONS.md`: Guía completa para agentes de IA sobre cómo usar el sistema
- `test_rag.py`: Script de prueba para verificar el funcionamiento del sistema

---

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos para poner en marcha el sistema.

### Prerrequisitos

- **Python 3.10+**
- **Ollama:** Asegúrate de que [Ollama esté instalado](https://ollama.com/) y en ejecución en tu sistema.

### 0. Configuración de Ollama (Paso Crítico)

Ollama es necesario para que el sistema RAG funcione, ya que proporciona el modelo de lenguaje local que genera las respuestas.

#### Instalación de Ollama

**Windows:**
1. Descarga Ollama desde [ollama.com](https://ollama.com/)
2. Ejecuta el instalador y sigue las instrucciones
3. Ollama se ejecutará automáticamente como servicio

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Verificar Instalación

```bash
# Verificar que Ollama está funcionando
ollama --version

# Verificar que el servicio está ejecutándose
ollama list
```

#### Descargar Modelos de Lenguaje

El sistema RAG necesita un modelo de lenguaje para generar respuestas. Recomendamos:

```bash
# Modelo recomendado (equilibrio entre velocidad y calidad)
ollama pull llama3

# Alternativas más rápidas
ollama pull phi3
ollama pull mistral

# Alternativa más potente (requiere más recursos)
ollama pull llama3.1:8b
```

#### Configurar el Modelo en el Sistema

Una vez descargado el modelo, asegúrate de que `rag_core.py` use el modelo correcto:

```python
# En rag_core.py, línea ~100, verifica que use tu modelo:
llm = ChatOllama(model="llama3", temperature=0)
```

**Nota:** Si descargaste un modelo diferente, cambia `"llama3"` por el nombre de tu modelo.

#### Probar Ollama

```bash
# Probar que el modelo funciona
ollama run llama3 "Hola, ¿cómo estás?"
```

Si ves una respuesta generada, Ollama está funcionando correctamente.

#### Solución de Problemas Comunes

**Error: "Ollama is not running"**
```bash
# Iniciar Ollama manualmente
ollama serve
```

**Error: "Model not found"**
```bash
# Verificar modelos disponibles
ollama list

# Descargar el modelo si no está
ollama pull llama3
```

**Error: "Out of memory"**
- Usa un modelo más pequeño: `ollama pull phi3`
- Cierra otras aplicaciones que consuman mucha RAM
- Considera aumentar la memoria virtual en Windows

### 1. Configuración del Entorno

```bash
# 1. Clona este repositorio (si estuviera en GitHub) o usa los archivos existentes.
# cd RAG_MCP_Project

# 2. Crea un entorno virtual de Python
python -m venv .venv

# 3. Activa el entorno virtual
# En Windows:
.venv\\Scripts\\activate
# En macOS/Linux:
# source .venv/bin/activate
```

### 2. Instalación de Dependencias

Una vez que el entorno virtual esté activado, instala todas las librerías necesarias.

#### Opción A: Instalación Completa (Recomendada)
```bash
pip install -r requirements.txt
```

#### Opción B: Instalación Mínima (Para pruebas rápidas)
```bash
pip install -r requirements-minimal.txt
```

#### Opción C: Instalación de Desarrollo (Para contribuir al proyecto)
```bash
pip install -r requirements-dev.txt
```

**Nota:** La instalación completa incluye todas las dependencias necesarias. La instalación mínima omite algunas utilidades opcionales pero mantiene la funcionalidad core. La instalación de desarrollo incluye herramientas de testing y desarrollo.

### 2. Verificación Completa del Sistema

Antes de continuar, vamos a verificar que todo esté funcionando correctamente:

#### Paso 1: Verificar Ollama
```bash
# Verificar que Ollama está ejecutándose
ollama list

# Probar el modelo
ollama run llama3 "Test de funcionamiento"
```

#### Paso 2: Verificar Dependencias de Python
```bash
# Verificar que todas las dependencias están instaladas
python -c "import mcp; print('✅ MCP instalado correctamente')"
python -c "import langchain; print('✅ LangChain instalado correctamente')"
python -c "import chromadb; print('✅ ChromaDB instalado correctamente')"
```

#### Paso 3: Probar el Sistema RAG
```bash
# Ejecutar el script de prueba
python test_rag.py
```

Si todo funciona correctamente, verás:
- ✅ Ollama respondiendo a comandos
- ✅ Todas las dependencias importándose sin errores
- ✅ El sistema RAG procesando preguntas y mostrando fuentes

### 3. Descarga del Modelo Local

**Nota:** Si ya descargaste el modelo en el paso 0, puedes saltar esta sección.

Abre una terminal y descarga el modelo de lenguaje que usará Ollama para generar las respuestas.

```bash
# Modelo recomendado para el sistema RAG
ollama pull llama3
```

**Alternativas de modelos:**

| Modelo | Tamaño | Velocidad | Calidad | Uso Recomendado |
|--------|--------|-----------|---------|-----------------|
| `llama3` | ~4GB | Media | Alta | ✅ **Recomendado** |
| `phi3` | ~2GB | Rápida | Buena | Para recursos limitados |
| `mistral` | ~4GB | Media | Alta | Alternativa a llama3 |
| `llama3.1:8b` | ~5GB | Lenta | Muy alta | Para máxima calidad |

**Nota:** La primera vez que ejecutes el servidor o el script de ingesta, el modelo de *embedding* (`all-MiniLM-L6-v2`, unos 90MB) se descargará automáticamente. Esto solo ocurre una vez.

**Verificar descarga:**
```bash
# Verificar que el modelo está disponible
ollama list

# Probar el modelo
ollama run llama3 "Hola, ¿puedes ayudarme con el sistema RAG?"
```

### 4. Configurar el Modelo en el Código

Si descargaste un modelo diferente a `llama3`, necesitas actualizar la configuración:

#### Opción 1: Descargar el Modelo de Embedding (Recomendado la primera vez)
Para evitar esperas la primera vez que se usa el servidor, puedes pre-descargar el modelo de embedding con este comando. Verás una barra de progreso:
```bash
python pre_download_model.py
```

#### Opción 2: Cambiar en rag_core.py
```python
# Abrir rag_core.py y buscar la línea ~100
# Cambiar esta línea:
llm = ChatOllama(model="llama3", temperature=0)

# Por tu modelo, por ejemplo:
llm = ChatOllama(model="phi3", temperature=0)
```

#### Opción 3: Usar Variable de Entorno (Recomendado)
Crea un archivo `.env` en la raíz del proyecto:

```bash
# Crear archivo .env
echo "OLLAMA_MODEL=llama3" > .env
```

Y modifica `rag_core.py` para usar la variable de entorno:

```python
import os
from dotenv import load_dotenv

load_dotenv()
model_name = os.getenv("OLLAMA_MODEL", "llama3")  # Por defecto llama3
llm = ChatOllama(model=model_name, temperature=0)
```

**Ventajas de usar variable de entorno:**
- Fácil cambio de modelo sin modificar código
- Configuración específica por entorno
- No se modifica el código fuente

---

## ✅ Resumen de Configuración

Para verificar que todo está listo, ejecuta esta secuencia de comandos:

```bash
# 1. Verificar Ollama
ollama list
ollama run llama3 "Test"

# 2. Verificar dependencias
python -c "import mcp, langchain, chromadb; print('✅ Todas las dependencias OK')"

# 3. Probar el sistema completo
python test_rag.py
```

**Si todo funciona correctamente, verás:**
- ✅ Lista de modelos de Ollama
- ✅ Respuesta del modelo de prueba
- ✅ Todas las dependencias importándose
- ✅ Sistema RAG procesando preguntas con fuentes

**¡Tu sistema RAG está listo para usar!** 🚀

---

## 🛠️ Guía de Uso

### Uso 1: Poblar la Base de Conocimiento (Ingesta Masiva)

Para añadir una gran cantidad de documentos de una sola vez, usa el script `bulk_ingest.py`.

1.  Crea una carpeta en tu ordenador (ej. `C:\MisDocumentos`).
2.  Copia todos los documentos que quieres que la IA aprenda en esa carpeta.
3.  Ejecuta el siguiente comando en la terminal (con el entorno virtual activado):

```bash
python bulk_ingest.py --directory "C:\MisDocumentos"
```

El script recorrerá todos los archivos soportados, los convertirá y los añadirá a la base de datos vectorial en la carpeta `./rag_mcp_db`.

### Uso 2: Configuración del Cliente MCP (Ej. Cursor)

Para que tu editor de IA pueda usar el servidor, debes configurarlo.

1.  **Encuentra el archivo de configuración de servidores MCP de tu editor.** Para Cursor, busca un archivo como `mcp_servers.json` en su directorio de configuración (`%APPDATA%\cursor` en Windows). Si no existe, puedes crearlo.

2.  **Añade la siguiente configuración al archivo JSON.**
    
    Este método utiliza un script de arranque (`run_server.bat`) para asegurar que la codificación de caracteres sea UTF-8, previniendo errores en Windows.

    **¡IMPORTANTE!** Debes reemplazar `"D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG"` con la ruta absoluta real a la carpeta de este proyecto en tu máquina.

    ```json
    {
      "mcpServers": {
        "rag_server_knowledge": {
          "command": "D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG\\run_server.bat",
          "args": [],
          "workingDirectory": "D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG"
        }
      }
    }
    ```

3.  **Reinicia tu editor.** Al arrancar, debería detectar y lanzar tu `run_server.bat`, que a su vez ejecutará `rag_server.py` en segundo plano con el entorno correcto.

### Uso 3: Interactuando con las Herramientas

Una vez configurado, puedes usar las herramientas directamente en el chat de tu editor.

#### Herramientas Disponibles:

**1. `learn_text(text, source_name)` - Añadir información textual**
```
@rag_server_knowledge learn_text("El punto de fusión del titanio es 1,668 °C.", "material_properties")
```
- **Cuándo usar**: Para añadir hechos, definiciones, notas de conversación, etc.
- **Parámetros**: 
  - `text`: El contenido a almacenar
  - `source_name`: Nombre descriptivo de la fuente (opcional, por defecto "manual_input")

**2. `learn_document(file_path)` - Procesar documentos**
```
@rag_server_knowledge learn_document("C:\\Reportes\\informe_q3.pdf")
```
- **Cuándo usar**: Para procesar archivos PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML
- **Características**: 
  - Conversión automática a Markdown
  - Copia guardada en `./converted_docs/`
  - Metadatos de fuente automáticos

**3. `ask_rag(query)` - Consultar información**
```
@rag_server_knowledge ask_rag("¿Cuál es el punto de fusión del titanio?")
```
- **Cuándo usar**: Para buscar información previamente almacenada
- **Respuesta incluye**: 
  - Respuesta generada por IA
  - 📚 Lista de fuentes utilizadas

#### Ejemplo de Flujo Completo:

```bash
# 1. Añadir información
@rag_server_knowledge learn_text("La temperatura de fusión del titanio es 1,668°C.", "material_properties")

# 2. Procesar un documento
@rag_server_knowledge learn_document("C:\\Documents\\manual_titanio.pdf")

# 3. Hacer preguntas
@rag_server_knowledge ask_rag("¿Cuál es la temperatura de fusión del titanio?")
```

**Respuesta esperada:**
```
La temperatura de fusión del titanio es 1,668°C.

📚 Fuentes de información:
   1. material_properties
   2. manual_titanio.pdf
```

---

## 🧪 Pruebas y Verificación

### Probar el Sistema

Para verificar que todo funciona correctamente:

```bash
# Probar el sistema RAG con metadatos de fuente
python test_rag.py
```

Este script realizará pruebas automáticas y mostrará las fuentes de información utilizadas.

### Verificar la Base de Datos

Los documentos procesados se almacenan en:
- **Base de datos vectorial**: `./rag_mcp_db/`
- **Copias Markdown**: `./converted_docs/`

---

## 🤖 Uso por Agentes de IA

El sistema está optimizado para ser utilizado por agentes de IA. Consulta `AGENT_INSTRUCTIONS.md` para:

- Guías detalladas de uso
- Ejemplos de casos de uso
- Mejores prácticas
- Manejo de errores
- Consideraciones importantes

### Características para Agentes:

- **Descripciones detalladas** de cada herramienta
- **Ejemplos de uso** claros y específicos
- **Manejo de errores inteligente** con sugerencias útiles
- **Metadatos de fuente** para rastreabilidad completa
- **Respuestas estructuradas** con información de fuentes

---

## 📂 Estructura del Proyecto

```
/
├── .venv/                  # Entorno virtual de Python
├── rag_mcp_db/             # Base de datos vectorial (se crea al usarla)
├── converted_docs/          # Copias en Markdown de documentos procesados
├── bulk_ingest.py          # Script para la ingesta masiva de documentos
├── rag_core.py             # Lógica central y reutilizable del sistema RAG
├── rag_server.py           # El servidor MCP (lanzado por run_server.bat)
├── run_server.bat          # Script de arranque para el servidor en Windows
├── requirements.txt        # Dependencias completas (recomendado)
├── requirements-minimal.txt # Dependencias mínimas para pruebas rápidas
├── requirements-dev.txt    # Dependencias de desarrollo
├── pre_download_model.py   # Script para pre-descargar el modelo de embedding
├── test_rag.py             # Script de prueba del sistema RAG
├── AGENT_INSTRUCTIONS.md   # Guía para agentes de IA
├── proyecto_alpha.txt      # Archivo de ejemplo
└── README.md               # Este archivo
```