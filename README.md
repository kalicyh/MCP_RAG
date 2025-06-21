# Servidor RAG Personal con MCP

Este proyecto implementa un servidor compatible con el Protocolo de Contexto de Modelo (MCP) que dota a los clientes de IA (como Cursor, Claude for Desktop, etc.) de una capacidad de Recuperación Aumentada por Generación (RAG). Permite al modelo de lenguaje acceder a una base de conocimiento privada y local, alimentada por tus propios textos y documentos.

## ✨ Características

- **Memoria Persistente para tu IA:** "Enseña" a tu IA nueva información que recordará entre sesiones.
- **🆕 Interfaz Gráfica de Usuario (GUI):** Una aplicación de escritorio intuitiva (`run_gui.bat`) para procesar documentos, previsualizarlos y seleccionarlos antes de añadirlos a la base de conocimiento.
- **Procesamiento de Documentos:** Alimenta la base de conocimiento con archivos `.pdf`, `.docx`, `.pptx`, `.txt`, y más.
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

### 1. Instalación (¡Automática!)

Gracias a los nuevos scripts de arranque, la instalación es increíblemente sencilla.

1.  **Para el Servidor RAG:** Simplemente ejecuta `run_server.bat`.
2.  **Para la Ingesta de Documentos:** Simplemente ejecuta `run_gui.bat`.

La primera vez que ejecutes cualquiera de estos archivos, el script hará todo por ti:
- ✅ Creará un entorno virtual de Python en una carpeta `.venv`.
- ✅ Activará el entorno.
- ✅ Instalará todas las dependencias necesarias desde `requirements.txt`.
- ✅ Lanzará la aplicación.

En ejecuciones posteriores, el script simplemente activará el entorno y lanzará la aplicación directamente.

### 2. Configuración de Ollama (Paso Crítico)

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

**¡Tu sistema RAG está listo para usar!** 🚀

---

## 🛠️ Guía de Uso

### Uso 1: Poblar la Base de Conocimiento con la GUI (Recomendado)

La forma más fácil e intuitiva de añadir documentos es usando la interfaz gráfica.

1.  Haz doble clic en `run_gui.bat`.
2.  La aplicación se iniciará (la primera vez puede tardar mientras instala las dependencias).
3.  Usa el botón "Explorar..." para seleccionar la carpeta con tus documentos.
4.  Haz clic en "Iniciar Procesamiento". Los archivos se convertirán a Markdown en memoria.
5.  Ve a la pestaña "Revisión", selecciona los archivos que quieres guardar y previsualiza su contenido.
6.  Ve a la pestaña "Almacenamiento" y haz clic en "Iniciar Almacenamiento" para guardar los documentos seleccionados en la base de datos.

### Uso 2: Poblar la Base de Conocimiento desde la Línea de Comandos

Si prefieres usar la línea de comandos o necesitas automatizar la ingesta.

1.  Abre una terminal.
2.  Activa el entorno virtual: `.\.venv\Scripts\activate`.
3.  Ejecuta el script `bulk_ingest.py` apuntando a tu carpeta de documentos:
    ```bash
    python bulk_ingest.py --directory "C:\Ruta\A\Tus\Documentos"
    ```

### Uso 3: Configuración del Cliente MCP (Ej. Cursor)

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

### Uso 4: Interactuando con las Herramientas

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

## 🔧 Optimizaciones Implementadas

Esta sección explica cómo funciona el sistema RAG optimizado actualmente, con todas las mejoras técnicas implementadas para obtener las mejores búsquedas y respuestas.

### **A. División Inteligente de Texto**

#### **¿Cómo funciona la división de texto?**

El sistema utiliza `RecursiveCharacterTextSplitter` que divide el texto de manera inteligente, respetando la estructura natural del contenido:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Tamaño máximo de cada fragmento
    chunk_overlap=200,      # Caracteres que se comparten entre fragmentos
    length_function=len,    # Función para medir longitud
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Separadores inteligentes
)
```

#### **Separadores Inteligentes:**

El sistema busca los mejores puntos de división en este orden:
1. **`\n\n`** - Párrafos (mejor opción)
2. **`\n`** - Saltos de línea
3. **`. `** - Final de oraciones
4. **`! `** - Final de exclamaciones
5. **`? `** - Final de preguntas
6. **` `** - Espacios (último recurso)

#### **¿Por qué es importante?**

- **Preserva Contexto**: No corta en medio de una idea
- **Mantiene Coherencia**: Cada fragmento es una unidad lógica
- **Mejora Búsquedas**: Los fragmentos son más relevantes y completos

#### **Ejemplo de División Inteligente:**
```python
# Texto original:
"""
La inteligencia artificial (IA) es una rama de la informática. 
Se enfoca en crear sistemas inteligentes. Estos sistemas pueden 
aprender y tomar decisiones. La IA tiene muchas aplicaciones 
en la vida moderna.
"""

# Fragmentos resultantes:
# Fragmento 1: "La inteligencia artificial (IA) es una rama de la informática. Se enfoca en crear sistemas inteligentes."
# Fragmento 2: "Estos sistemas pueden aprender y tomar decisiones. La IA tiene muchas aplicaciones en la vida moderna."
```

### **B. Motor de Búsqueda Optimizado**

#### **Configuración Actual:**

```python
retriever = vector_store.as_retriever(
    search_type="similarity",  # Búsqueda por similitud semántica
    search_kwargs={
        "k": 5,                # Recupera 5 fragmentos más relevantes
        "score_threshold": 0.7, # Solo documentos con similitud > 70%
        "fetch_k": 10          # Busca 10 documentos y filtra los mejores 5
    }
)
```

#### **¿Cómo funciona la búsqueda?**

1. **Búsqueda Inicial**: Busca 10 documentos candidatos
2. **Cálculo de Similitud**: Calcula qué tan similares son a tu pregunta
3. **Filtrado por Calidad**: Solo mantiene documentos con similitud > 70%
4. **Selección Final**: Toma los 5 mejores fragmentos

#### **Parámetros Explicados:**

- **`k=5`**: Obtienes información de 5 fuentes diferentes para respuestas más completas
- **`score_threshold=0.7`**: Garantiza que solo se use información muy relevante
- **`fetch_k=10`**: Busca más opciones para seleccionar las mejores

### **C. Limpieza Automática de Texto**

#### **¿Qué hace la limpieza?**

Antes de procesar cualquier texto, el sistema lo limpia automáticamente:

```python
def clean_text_for_rag(text: str) -> str:
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Mantener solo caracteres importantes
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']', '', text)
    
    # Normalizar puntuación
    text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
    
    return text.strip()
```

#### **Problemas que resuelve automáticamente:**

1. **Espacios Múltiples**: `"Hola    mundo"` → `"Hola mundo"`
2. **Caracteres Especiales**: `"Texto@#$%^"` → `"Texto"`
3. **Puntuación Inconsistente**: `"Hola . Mundo"` → `"Hola. Mundo"`
4. **Saltos de Línea Excesivos**: Normaliza el formato

#### **Ejemplo de Limpieza:**
```python
# Texto con ruido:
"""
La IA    es muy importante!!!
Tiene muchas aplicaciones@@@
"""

# Después de limpieza automática:
"La IA es muy importante! Tiene muchas aplicaciones"
```

### **D. Respuestas Enriquecidas con Información de Calidad**

#### **¿Qué información incluye cada respuesta?**

El sistema proporciona respuestas completas con:

```
🤖 Respuesta:
[Respuesta generada por IA]

📚 Fuentes de información utilizadas:
   1. documento1.pdf (.pdf) - Procesado: 15/12/2024 14:30
   2. manual_ia.txt (.txt) - Procesado: 15/12/2024 14:25

✅ Alta confianza: Respuesta basada en múltiples fuentes
```

#### **Información Incluida:**

1. **Respuesta Principal**: Generada por el modelo de IA
2. **Fuentes Utilizadas**: Lista de documentos consultados
3. **Tipo de Archivo**: Formato de cada fuente
4. **Fecha de Procesamiento**: Cuándo se añadió a la base de datos
5. **Nivel de Confianza**: Basado en el número de fuentes

#### **Niveles de Confianza:**

- **✅ Alta confianza**: 3 o más fuentes
- **⚠️ Confianza media**: 2 fuentes
- **⚠️ Confianza limitada**: 1 fuente

### **E. Sistema de Logs en Español**

#### **¿Qué información muestran los logs?**

Los logs te permiten seguir todo el proceso en español:

```
MCP Server: Iniciando servidor MCP RAG...
MCP Server: Calentando sistema RAG...
MCP Server: Precargando modelo de embedding en memoria...
Core: Cargando modelo de embedding local: all-MiniLM-L6-v2
Core: Este paso puede tomar unos minutos en la primera ejecución para descargar el modelo.
Core: Usando dispositivo 'cpu' para embeddings.
Core: ¡Modelo cargado exitosamente!
Core: Inicializando base de datos vectorial...
Core: Base de datos vectorial inicializada en './rag_mcp_db'
MCP Server: Sistema RAG caliente y listo.
```

#### **Información que puedes monitorear:**

- **Progreso de Carga**: Cuándo se cargan los modelos
- **Procesamiento de Texto**: Cuántos fragmentos se crean
- **Búsquedas**: Cuántas fuentes se encuentran
- **Errores**: Mensajes claros con sugerencias

### **F. Manejo Inteligente de Errores**

#### **¿Cómo responde el sistema a los errores?**

Cuando algo no funciona correctamente, el sistema proporciona:

```
❌ Error al procesar la pregunta: [Descripción del error]

💡 Sugerencias:
- Verifica que el sistema RAG esté correctamente inicializado
- Intenta reformular tu pregunta
- Si el problema persiste, reinicia el servidor
```

#### **Tipos de errores que maneja:**

- **Archivos no encontrados**: Sugiere verificar rutas
- **Formatos no soportados**: Lista formatos compatibles
- **Problemas de permisos**: Guía para verificar acceso
- **Sistema no inicializado**: Instrucciones de reinicio

## **¿Cómo Funciona el Sistema Optimizado?**

### **1. Proceso de Búsqueda Completo:**

1. **Recepción de Pregunta**: El sistema recibe tu consulta
2. **Limpieza Automática**: Limpia la pregunta si es necesario
3. **Búsqueda Semántica**: Encuentra documentos relevantes
4. **Filtrado por Calidad**: Solo usa información muy similar
5. **Generación de Respuesta**: Crea respuesta basada en múltiples fuentes
6. **Información de Fuentes**: Proporciona lista completa de referencias

### **2. Características de Calidad:**

- **Alta Precisión**: Solo documentos con >70% de similitud
- **Contexto Completo**: 5 fragmentos de información
- **Trazabilidad**: Sabes exactamente de dónde viene cada información
- **Confianza Medible**: Nivel de confianza basado en fuentes

### **3. Experiencia de Usuario:**

- **Respuestas Completas**: Información detallada y bien estructurada
- **Fuentes Claras**: Sabes qué documentos se consultaron
- **Errores Útiles**: Mensajes claros con sugerencias
- **Monitoreo Fácil**: Logs en español para seguir el proceso

## **Ejemplo de Funcionamiento Completo**

**Pregunta**: "¿Cuáles son las aplicaciones de machine learning en medicina?"

**Proceso Interno:**
1. Sistema busca documentos sobre "machine learning" y "medicina"
2. Encuentra 3 documentos relevantes con similitud >70%
3. Genera respuesta combinando información de las 3 fuentes
4. Proporciona lista completa de fuentes utilizadas

**Respuesta Final:**
```
🤖 Respuesta:
Machine learning tiene múltiples aplicaciones en medicina, incluyendo diagnóstico por imágenes, análisis de datos médicos, descubrimiento de fármacos y medicina personalizada. Los algoritmos pueden analizar radiografías, resonancias magnéticas y otros estudios médicos para detectar enfermedades con alta precisión.

📚 Fuentes de información utilizadas:
   1. aplicaciones_ml.pdf (.pdf) - Procesado: 15/12/2024 14:30
   2. medicina_digital.txt (.txt) - Procesado: 15/12/2024 14:25
   3. ia_salud.docx (.docx) - Procesado: 15/12/2024 14:20

✅ Alta confianza: Respuesta basada en múltiples fuentes
```

## **Consejos para Obtener Mejores Resultados**

### **1. Añade Información Variada:**
```python
# Ejemplo de uso
learn_text("La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana.", "definicion_ia")
```

### **2. Usa Preguntas Específicas:**
- ❌ "¿Qué es la IA?"
- ✅ "¿Cuáles son las principales aplicaciones de la inteligencia artificial en la medicina?"

### **3. Verifica las Fuentes:**
- Siempre revisa la información de fuentes en las respuestas
- Usa múltiples documentos sobre el mismo tema para mayor confianza

### **4. Monitoreo del Sistema:**
- Los logs te mostrarán cuántos fragmentos se procesan
- Verás información sobre la calidad de las búsquedas
- Podrás identificar si necesitas ajustar parámetros

---

## 🧠 Entendiendo los Embeddings

Esta sección explica qué son los embeddings y por qué son fundamentales para el funcionamiento del sistema RAG.

### **🤖 ¿Qué son los Embeddings?**

#### **Definición Simple:**
Los **embeddings** son como "traductores" que convierten texto en números que las computadoras pueden entender y comparar. Es como crear un "código postal" para cada palabra o frase.

#### **Analogía Práctica:**
Imagina que tienes una biblioteca con miles de libros. Para encontrar libros similares, podrías:
- **Sin embeddings**: Leer cada libro completo (muy lento)
- **Con embeddings**: Usar un código que describe el contenido (muy rápido)

### **🔢 ¿Cómo Funcionan los Embeddings?**

#### **Proceso de Conversión:**
```python
# Texto original (humano entiende)
"La inteligencia artificial es fascinante"

# Embedding (computadora entiende)
[0.234, -0.567, 0.891, 0.123, -0.456, ...]  # Vector de 384 números
```

#### **¿Por qué Números?**
- **Comparación rápida**: Las computadoras pueden comparar números muy rápido
- **Similitud matemática**: Textos similares tienen números similares
- **Búsqueda eficiente**: Encuentra información relevante en milisegundos

### **🎯 ¿Cómo Se Usan en tu Sistema RAG?**

#### **1. Proceso de Almacenamiento:**
```python
# Cuando añades texto al sistema:
texto = "Machine learning es un tipo de IA"
embedding = modelo_embedding.convertir_a_vector(texto)
# Resultado: [0.1, 0.5, -0.3, 0.8, ...]

# Se guarda en la base de datos vectorial
base_datos.guardar(texto, embedding)
```

#### **2. Proceso de Búsqueda:**
```python
# Cuando haces una pregunta:
pregunta = "¿Qué es machine learning?"
embedding_pregunta = modelo_embedding.convertir_a_vector(pregunta)
# Resultado: [0.12, 0.48, -0.25, 0.82, ...]

# El sistema busca textos con embeddings similares
resultados = base_datos.buscar_similares(embedding_pregunta)
```

### **🧮 ¿Cómo Se Calcula la Similitud?**

#### **Cálculo de Distancia:**
```python
# Ejemplo simplificado:
embedding_1 = [0.1, 0.5, -0.3, 0.8]
embedding_2 = [0.12, 0.48, -0.25, 0.82]

# Distancia = qué tan diferentes son
distancia = calcular_distancia(embedding_1, embedding_2)
# Resultado: 0.05 (muy similar)

# Similitud = 1 - distancia
similitud = 1 - 0.05 = 0.95 (95% similar)
```

#### **Interpretación de Similitud:**
- **0.9 - 1.0**: Muy similar (excelente coincidencia)
- **0.7 - 0.9**: Similar (buena coincidencia) ← **Tu sistema usa 0.7 como mínimo**
- **0.5 - 0.7**: Moderadamente similar
- **0.0 - 0.5**: Poco similar

### **🔧 ¿Qué Modelo de Embedding Usa tu Sistema?**

#### **Modelo Actual:**
```python
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
```

#### **Características del Modelo:**
- **Tamaño**: ~90MB (pequeño y eficiente)
- **Dimensiones**: 384 números por texto
- **Idiomas**: Multilingüe (español e inglés)
- **Velocidad**: Muy rápido
- **Calidad**: Excelente para búsquedas

#### **¿Por qué Este Modelo?**
- **Eficiente**: No necesita mucha memoria
- **Rápido**: Procesa texto en milisegundos
- **Preciso**: Encuentra información muy relevante
- **Local**: Funciona sin internet

### **📊 Ejemplo Práctico en tu Sistema**

#### **Escenario: Buscar información sobre "machine learning"**

**Paso 1: Procesar Documentos**
```python
# Documento 1
texto_1 = "Machine learning es una rama de la IA"
embedding_1 = [0.1, 0.5, -0.3, 0.8, ...]  # 384 números

# Documento 2  
texto_2 = "Los algoritmos de ML pueden aprender"
embedding_2 = [0.12, 0.48, -0.25, 0.82, ...]  # 384 números

# Documento 3
texto_3 = "El clima hoy está soleado"
embedding_3 = [-0.8, 0.2, 0.9, -0.1, ...]  # 384 números
```

**Paso 2: Hacer Pregunta**
```python
pregunta = "¿Qué es machine learning?"
embedding_pregunta = [0.11, 0.49, -0.28, 0.81, ...]
```

**Paso 3: Calcular Similitudes**
```python
similitud_1 = calcular_similitud(embedding_pregunta, embedding_1)  # 0.95
similitud_2 = calcular_similitud(embedding_pregunta, embedding_2)  # 0.92
similitud_3 = calcular_similitud(embedding_pregunta, embedding_3)  # 0.15
```

**Paso 4: Seleccionar Resultados**
```python
# Solo documentos con similitud > 0.7 (70%)
resultados = [
    (texto_1, 0.95),  # Muy relevante
    (texto_2, 0.92)   # Muy relevante
    # texto_3 se descarta (0.15 < 0.7)
]
```

### **⚡ Ventajas de los Embeddings**

#### **1. Búsqueda Semántica:**
```python
# Encuentra información incluso con palabras diferentes
pregunta = "¿Qué es ML?"
# Encuentra: "Machine learning es una rama de la IA"
# Aunque "ML" y "Machine learning" son diferentes
```

#### **2. Velocidad:**
- **Sin embeddings**: Leer todos los documentos (muy lento)
- **Con embeddings**: Comparar números (muy rápido)

#### **3. Precisión:**
- **Búsqueda por palabras**: "IA" no encuentra "inteligencia artificial"
- **Búsqueda semántica**: "IA" encuentra "inteligencia artificial"

#### **4. Escalabilidad:**
- **Miles de documentos**: Procesamiento en segundos
- **Millones de documentos**: Procesamiento en minutos

### **🔍 ¿Cómo Se Configuran en tu Sistema?**

#### **En `rag_core.py`:**
```python
def get_embedding_function():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}  # o 'cuda' si tienes GPU
    )
    return embeddings
```

#### **Parámetros Importantes:**
- **`model_name`**: Qué modelo usar
- **`device`**: CPU o GPU
- **`chunk_size`**: Tamaño de fragmentos (1000 caracteres)
- **`chunk_overlap`**: Superposición entre fragmentos (200 caracteres)

### **📈 ¿Cómo Mejorar los Embeddings?**

#### **1. Calidad del Texto:**
```python
# ✅ Texto limpio y bien estructurado
"Machine learning es una rama de la inteligencia artificial que permite a las computadoras aprender sin ser programadas explícitamente."

# ❌ Texto con ruido
"ML is AI stuff that makes computers learn stuff without programming them explicitly."
```

#### **2. Tamaño de Fragmentos:**
- **Muy pequeños**: Pierden contexto
- **Muy grandes**: Menos precisos
- **Óptimo**: 1000 caracteres con 200 de overlap

#### **3. Modelo de Embedding:**
- **Modelos más grandes**: Mejor calidad, más lento
- **Modelos más pequeños**: Más rápido, calidad aceptable
- **Tu modelo**: Balance perfecto

### **🎯 Resumen: ¿Por qué son Importantes?**

#### **Sin Embeddings:**
- Búsquedas lentas
- Resultados imprecisos
- No entiende sinónimos
- Escalabilidad limitada

#### **Con Embeddings:**
- Búsquedas instantáneas
- Resultados muy precisos
- Entiende significado
- Escalable a millones de documentos

**Los embeddings son el "cerebro" que hace que tu sistema RAG sea inteligente y rápido. Convierten el texto en un lenguaje que las computadoras pueden entender y comparar eficientemente, permitiendo búsquedas semánticas precisas en milisegundos.**

---

## ⚠️ Limitaciones y Elección del Modelo de Embedding

Esta sección detalla por qué se eligió el modelo `all-mpnet-base-v2`, sus ventajas y sus limitaciones en comparación con otras alternativas.

### **🎯 ¿Por qué `all-mpnet-base-v2`? Un excelente punto medio**

Este modelo fue seleccionado por ofrecer el mejor **equilibrio entre rendimiento y calidad** para una ejecución local.

- **Ventajas:**
    - **Alta Calidad:** Ofrece una comprensión semántica significativamente mejor que modelos más pequeños (como `all-MiniLM-L6-v2`). Es muy bueno capturando matices y relaciones complejas en el texto.
    - **Buen Rendimiento:** Aunque es más grande que los modelos "mini", sigue siendo lo suficientemente rápido para ejecutarse en CPUs modernas sin tiempos de espera frustrantes.
    - **Muy Popular:** Es uno de los modelos de `sentence-transformers` más usados y mejor valorados, lo que garantiza un buen soporte y rendimiento probado.

- **Desventajas:**
    - **Uso de Recursos:** Requiere más RAM y espacio en disco (420MB) que los modelos pequeños.
    - **No es el mejor:** Modelos comerciales de vanguardia (como los de OpenAI o Cohere) o modelos locales mucho más grandes (de varios Gigabytes) pueden ofrecer una precisión aún mayor, pero a costa de no poder ejecutarse localmente o requerir hardware muy potente.

### **⚖️ Comparativa de Modelos**

| Modelo | Tamaño | Dimensiones | Calidad Semántica | Requisitos | Ideal para... |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`all-mpnet-base-v2` (Tu modelo)** | **~420MB** | **768** | **Alta** | **Moderados (CPU/GPU)** | **El mejor balance para uso local y de alta calidad.** |
| `all-MiniLM-L6-v2` | ~90MB | 384 | Media | Bajos (CPU) | Sistemas con muy pocos recursos o donde la velocidad es más importante que la precisión. |
| `text-embedding-3-large` (OpenAI) | N/A (API) | 3072 | Muy Alta | Conexión a Internet, API Key | Proyectos comerciales que necesitan la máxima precisión y no tienen problemas de privacidad/coste. |


En resumen, `all-mpnet-base-v2` es la elección perfecta para este proyecto: un sistema RAG local, privado y de alto rendimiento que no requiere hardware de servidor.

---

## ⚠️ Limitaciones del Modelo de Embedding

Esta sección detalla las limitaciones y desventajas del modelo `all-MiniLM-L6-v2` que usa tu sistema, para que puedas tomar decisiones informadas y optimizar su uso.

### **🔍 Limitaciones de Tamaño y Complejidad**

#### **Modelo Pequeño:**
- **Tamaño**: Solo 90MB (muy pequeño)
- **Dimensiones**: 384 números (limitado)
- **¿Problema?** Menos capacidad para capturar matices complejos

#### **Comparación con Modelos Más Grandes:**
```python
# Tu modelo actual:
all-MiniLM-L6-v2: 90MB, 384 dimensiones

# Modelos más potentes:
sentence-transformers/all-mpnet-base-v2: 420MB, 768 dimensiones
text-embedding-ada-002: 1.5GB, 1536 dimensiones
```

### **🧠 Limitaciones en Comprensión Semántica**

#### **Contexto Limitado:**
- **Longitud máxima**: ~512 tokens por fragmento
- **¿Problema?** Puede perder contexto en textos largos o complejos

#### **Ejemplo de Limitación:**
```python
# Texto complejo que puede ser problemático:
texto_complejo = """
La inteligencia artificial, específicamente el machine learning supervisado, 
utiliza algoritmos como redes neuronales convolucionales para procesar 
imágenes médicas y detectar anomalías en radiografías de tórax, 
permitiendo diagnósticos más precisos y tempranos.
"""

# El modelo puede no capturar completamente la relación entre:
# - "redes neuronales convolucionales" 
# - "procesar imágenes médicas"
# - "detectar anomalías"
```

### **🌍 Limitaciones en Idiomas**

#### **Soporte Multilingüe Básico:**
- **Idiomas principales**: Inglés y español
- **¿Problema?** Rendimiento desigual en otros idiomas
- **Calidad variable**: Mejor en inglés que en español

#### **Ejemplo de Problema:**
```python
# En inglés (excelente):
"machine learning" → [0.1, 0.5, -0.3, ...]

# En español (bueno, pero no óptimo):
"aprendizaje automático" → [0.08, 0.48, -0.25, ...]

# En otros idiomas (limitado):
"apprentissage automatique" → [0.05, 0.45, -0.2, ...]
```

### **🔬 Limitaciones en Dominios Específicos**

#### **Conocimiento General vs Especializado:**
- **Entrenado en**: Texto general de internet
- **¿Problema?** Puede no entender bien terminología técnica específica

#### **Ejemplos de Dominios Problemáticos:**
```python
# Terminología médica especializada:
"adenocarcinoma pulmonar de células pequeñas" 
# Puede no capturar bien la relación con "cáncer de pulmón"

# Terminología legal:
"res judicata" 
# Puede no entender que es "cosa juzgada"

# Terminología técnica muy específica:
"microservicios con arquitectura hexagonal"
# Puede perder matices técnicos específicos
```

### **🔗 Limitaciones en Comprensión de Relaciones**

#### **Relaciones Complejas:**
- **Relaciones simples**: Excelente (sinónimos, antónimos)
- **Relaciones complejas**: Limitado (causalidad, implicación)

#### **Ejemplo de Limitación:**
```python
# Relación simple (funciona bien):
"coche" ↔ "automóvil"  # Sinónimos

# Relación compleja (puede fallar):
"Si llueve, el suelo se moja" 
# Puede no capturar bien la relación causal
```

### **📝 Sensibilidad al Formato del Texto**

#### **Dependencia del Formato:**
- **Texto limpio**: Excelente rendimiento
- **Texto con ruido**: Rendimiento degradado

#### **Ejemplos Problemáticos:**
```python
# ✅ Texto limpio (funciona bien):
"La inteligencia artificial es una rama de la informática."

# ❌ Texto con ruido (puede fallar):
"La IA es una rama de la info... muy importante!!!"
"La inteligencia artificial (IA) es una rama de la informática."
```

### **🎯 Limitaciones en Tareas Específicas**

#### **Búsqueda de Información vs Otras Tareas:**
- **Búsqueda semántica**: Excelente
- **Clasificación de texto**: Limitado
- **Análisis de sentimientos**: No optimizado
- **Extracción de entidades**: Básico

### **📈 Limitaciones de Escalabilidad**

#### **Rendimiento con Grandes Volúmenes:**
- **Miles de documentos**: Excelente
- **Millones de documentos**: Puede ser lento
- **¿Por qué?** Comparación secuencial de vectores

## **🔄 Estrategias para Mitigar Limitaciones**

### **1. Optimizar el Texto de Entrada:**
```python
# ✅ Mejorar calidad del texto:
texto_limpio = clean_text_for_rag(texto_original)

# ✅ Usar fragmentos apropiados:
chunk_size = 1000  # Tamaño óptimo para este modelo
chunk_overlap = 200  # Mantener contexto
```

### **2. Ajustar Parámetros de Búsqueda:**
```python
# Para compensar limitaciones:
search_kwargs = {
    "k": 5,                # Más fragmentos para mejor cobertura
    "score_threshold": 0.7, # Umbral alto para precisión
    "fetch_k": 10          # Buscar más candidatos
}
```

### **3. Mejorar la Estructura de Datos:**
```python
# ✅ Documentos bien estructurados:
"Machine learning es una rama de la inteligencia artificial que permite a las computadoras aprender sin ser programadas explícitamente."

# ✅ Metadatos descriptivos:
metadata = {
    "domain": "tecnología",
    "language": "español",
    "complexity": "intermedio"
}
```

### **4. Considerar Modelos Alternativos (Futuro):**

#### **Para Mejor Calidad:**
```python
# Modelos más potentes (requieren más recursos):
"all-mpnet-base-v2"      # 420MB, mejor calidad
"text-embedding-ada-002" # 1.5GB, máxima calidad
```

#### **Para Mejor Velocidad:**
```python
# Modelos más rápidos:
"all-MiniLM-L6-v2"       # Tu modelo actual
"paraphrase-MiniLM-L3-v2" # Aún más rápido
```

## **⚖️ Resumen: Ventajas vs Desventajas**

### **Desventajas:**
- ❌ Comprensión semántica limitada
- ❌ Contexto limitado en textos largos
- ❌ Rendimiento variable en idiomas
- ❌ Limitado en dominios especializados
- ❌ Sensible al formato del texto
- ❌ Relaciones complejas limitadas

### **Ventajas (que compensan):**
- ✅ Muy rápido y eficiente
- ✅ Poco uso de memoria
- ✅ Funciona sin internet
- ✅ Excelente para búsquedas básicas
- ✅ Balance calidad/velocidad
- ✅ Fácil de implementar

## **🎯 Recomendaciones para tu Caso de Uso**

### **Para tu Sistema Actual:**
1. **Mantén el modelo actual** - Es un buen balance
2. **Optimiza el texto de entrada** - Limpia y estructura bien
3. **Ajusta parámetros** - Usa más fragmentos si es necesario
4. **Monitorea resultados** - Verifica calidad de respuestas

### **Para Considerar en el Futuro:**
1. **Si necesitas mejor calidad**: Cambiar a modelo más grande
2. **Si necesitas más velocidad**: Usar modelo más pequeño
3. **Si tienes GPU**: Habilitar aceleración por hardware
4. **Si tienes muchos documentos**: Considerar indexación avanzada

### **Señales de que Necesitas un Modelo Mejor:**
- Respuestas inconsistentes en tu dominio
- No encuentra información que sabes que existe
- Problemas con terminología técnica específica
- Necesitas mayor precisión en relaciones complejas

---

## ⚡ Consideraciones para Funcionamiento Óptimo

Esta sección detalla las consideraciones técnicas y mejores prácticas para obtener el máximo rendimiento de tu sistema RAG.

### **🔧 Requisitos del Sistema**

#### **Memoria RAM:**
- **Mínimo recomendado**: 8GB RAM
- **Óptimo**: 16GB RAM o más
- **¿Por qué es importante?** Los modelos de embedding y el LLM necesitan memoria para funcionar eficientemente

#### **Almacenamiento:**
- **Espacio libre**: Al menos 10GB disponibles
- **Velocidad**: SSD preferiblemente (más rápido que HDD)
- **¿Para qué?** Modelos, base de datos vectorial y documentos procesados

#### **CPU/GPU:**
- **CPU**: Mínimo 4 núcleos, recomendado 8+ núcleos
- **GPU**: Opcional pero mejora significativamente el rendimiento
- **¿Por qué?** Los embeddings y el procesamiento de texto son intensivos

### **🤖 Configuración de Ollama**

#### **Modelos Recomendados:**
```bash
# Modelos por rendimiento:
ollama pull llama3        # Equilibrio velocidad/calidad
ollama pull phi3          # Más rápido, menos recursos
ollama pull mistral       # Buena calidad, moderado uso de recursos
```

#### **Configuración de Memoria:**
```bash
# En Windows, ajustar memoria virtual:
# Panel de Control > Sistema > Configuración avanzada > Rendimiento > Configuración
# Memoria virtual: Al menos 16GB
```

#### **Verificar Funcionamiento:**
```bash
# Probar que Ollama funciona correctamente
ollama list
ollama run llama3 "Test de funcionamiento"
```

### **📄 Calidad de los Datos de Entrada**

#### **Documentos Bien Estructurados:**
- **Formato consistente**: Usa el mismo formato en todos los documentos
- **Contenido relevante**: Solo añade información útil para tus consultas
- **Tamaño apropiado**: Documentos entre 1-50 páginas funcionan mejor

#### **Ejemplos de Buena Práctica:**
```python
# ✅ Documentos bien estructurados
learn_text("La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana. Se divide en machine learning, procesamiento de lenguaje natural y visión por computadora.", "definicion_ia_completa")

# ❌ Información fragmentada
learn_text("IA", "definicion_corta")
learn_text("es", "definicion_fragmentada")
```

### **✂️ Estrategia de División de Texto**

#### **Tamaño de Fragmentos Actual:**
- **Fragmentos**: 1000 caracteres con 200 de overlap
- **Para documentos técnicos**: Puedes aumentar a 1500 caracteres
- **Para conversaciones**: Puedes reducir a 800 caracteres

#### **Separadores Inteligentes:**
El sistema ya usa separadores óptimos, pero puedes ajustar según tu contenido:
```python
# Para documentos técnicos con muchas listas:
separators=["\n\n", "\n", ". ", "• ", "- ", " ", ""]

# Para documentos narrativos:
separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
```

### **🔍 Configuración de Búsqueda**

#### **Parámetros Actuales (Optimizados):**
```python
search_kwargs={
    "k": 5,                # 5 fragmentos - buen balance
    "score_threshold": 0.7, # 70% similitud - alta precisión
    "fetch_k": 10          # 10 candidatos - buena selección
}
```

#### **Ajustes según Necesidades:**
- **Para respuestas más completas**: Aumentar `k` a 7-8
- **Para mayor precisión**: Aumentar `score_threshold` a 0.8
- **Para búsquedas más amplias**: Reducir `score_threshold` a 0.6

### **🗄️ Gestión de la Base de Datos**

#### **Mantenimiento Regular:**
```bash
# Verificar tamaño de la base de datos
ls -la rag_mcp_db/

# Limpiar archivos temporales si es necesario
rm -rf rag_mcp_db/*.tmp
```

#### **Backup de Datos:**
```bash
# Crear copia de seguridad
cp -r rag_mcp_db/ rag_mcp_db_backup_$(date +%Y%m%d)
```

### **💡 Optimización de Consultas**

#### **Preguntas Efectivas:**
```python
# ✅ Preguntas específicas y claras
ask_rag("¿Cuáles son las principales aplicaciones de machine learning en el diagnóstico médico?")

# ❌ Preguntas muy generales
ask_rag("¿Qué es la IA?")
```

#### **Uso de Palabras Clave:**
- **Incluye términos técnicos** específicos de tu dominio
- **Usa sinónimos** para conceptos importantes
- **Sé específico** en lo que buscas

### **📊 Monitoreo del Rendimiento**

#### **Logs Importantes a Revisar:**
```
Core: Texto dividido en X fragmentos
Core: X fragmentos añadidos y guardados en la base de conocimientos
MCP Server: Respuesta generada exitosamente con X fuentes
```

#### **Indicadores de Rendimiento:**
- **Tiempo de respuesta**: Debería ser < 5 segundos
- **Número de fuentes**: 3+ fuentes = alta confianza
- **Calidad de respuestas**: Información relevante y completa

### **🔒 Consideraciones de Seguridad**

#### **Datos Sensibles:**
- **No incluyas información personal** en la base de conocimientos
- **Revisa documentos** antes de procesarlos
- **Usa fuentes confiables** para la información

#### **Acceso al Sistema:**
- **Mantén actualizado** el entorno virtual
- **Revisa logs** regularmente
- **Monitorea uso de recursos**

### **⚙️ Optimización de Flujo de Trabajo**

#### **Proceso Recomendado:**
1. **Preparar documentos**: Limpiar y estructurar contenido
2. **Procesar en lotes**: Usar `bulk_ingest.py` para muchos documentos
3. **Verificar calidad**: Revisar respuestas de prueba
4. **Ajustar parámetros**: Si es necesario, modificar configuración
5. **Monitorear uso**: Revisar logs y rendimiento

#### **Herramientas de Verificación:**
```bash
# Probar el sistema completo
python test_rag.py

# Verificar que Ollama funciona
ollama run llama3 "Test"

# Verificar dependencias
python -c "import mcp, langchain, chromadb; print('✅ Todo OK')"
```

## **🚀 Checklist para Funcionamiento Óptimo**

### **Antes de Usar:**
- [ ] Ollama instalado y funcionando
- [ ] Modelo de lenguaje descargado
- [ ] Suficiente memoria RAM disponible
- [ ] Espacio en disco suficiente
- [ ] Entorno virtual activado

### **Durante el Uso:**
- [ ] Documentos bien estructurados
- [ ] Preguntas específicas y claras
- [ ] Monitoreo de logs
- [ ] Verificación de fuentes en respuestas
- [ ] Backup regular de datos

### **Mantenimiento:**
- [ ] Revisar logs semanalmente
- [ ] Verificar rendimiento
- [ ] Limpiar archivos temporales
- [ ] Actualizar dependencias si es necesario
- [ ] Backup de base de datos

## **⚠️ Problemas Comunes y Soluciones**

### **Respuestas Lentas:**
- **Causa**: Modelo muy grande o poca RAM
- **Solución**: Usar modelo más pequeño (phi3) o aumentar RAM

### **Respuestas Pobres:**
- **Causa**: Poca información en la base de datos
- **Solución**: Añadir más documentos relevantes

### **Errores de Memoria:**
- **Causa**: Documentos muy grandes o muchos fragmentos
- **Solución**: Reducir tamaño de fragmentos o procesar en lotes

### **Búsquedas Sin Resultados:**
- **Causa**: Umbral de similitud muy alto
- **Solución**: Reducir `score_threshold` a 0.6

### **Modelo No Encontrado:**
- **Causa**: Modelo no descargado o nombre incorrecto
- **Solución**: Verificar con `ollama list` y descargar si es necesario

### **Errores de Conexión:**
- **Causa**: Ollama no está ejecutándose
- **Solución**: Iniciar Ollama con `ollama serve`

---

## 📂 Estructura del Proyecto

```
/
├── .venv/                  # Entorno virtual de Python (creado automáticamente)
├── rag_mcp_db/             # Base de datos vectorial (se crea al usarla)
├── converted_docs/         # Copias en Markdown de documentos procesados
├── bulk_ingest.py          # Script para la ingesta masiva desde línea de comandos
├── bulk_ingest_gui.py      # Script de la Interfaz Gráfica de Usuario
├── rag_core.py             # Lógica central y reutilizable del sistema RAG
├── rag_server.py           # El servidor MCP (lanzado por run_server.bat)
├── run_gui.bat             # Script de arranque para la interfaz gráfica
├── run_server.bat          # Script de arranque para el servidor en Windows
├── requirements.txt        # Todas las dependencias del proyecto
├── pre_download_model.py   # Script para pre-descargar el modelo de embedding
├── test_rag.py             # Script de prueba del sistema RAG
├── AGENT_INSTRUCTIONS.md   # Guía para agentes de IA
└── README.md               # Este archivo
```