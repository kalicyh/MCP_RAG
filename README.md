# Servidor RAG Personal con MCP

Este proyecto implementa un servidor compatible con el Protocolo de Contexto de Modelo (MCP) que dota a los clientes de IA (como Cursor, Claude for Desktop, etc.) de una capacidad de Recuperación Aumentada por Generación (RAG). Permite al modelo de lenguaje acceder a una base de conocimiento privada y local, alimentada por tus propios textos y documentos.

## ✨ Características

- **Memoria Persistente para tu IA:** "Enseña" a tu IA nueva información que recordará entre sesiones.
- **🆕 Interfaz Gráfica de Usuario (GUI):** Una aplicación de escritorio intuitiva con sistema de scripts organizados para facilitar la instalación y ejecución.
- **🚀 Procesamiento Avanzado de Documentos:** Alimenta la base de conocimiento con **más de 25 formatos de archivo** incluyendo PDF, DOCX, PPTX, XLSX, imágenes (con OCR), correos electrónicos, y más.
- **🧠 Procesamiento Inteligente con Unstructured:** Sistema de procesamiento de documentos de nivel empresarial que preserva la estructura semántica, elimina ruido automáticamente y maneja formatos complejos.
- **🔄 Sistema de Fallbacks Robusto:** Múltiples estrategias de procesamiento garantizan que cualquier documento sea procesado exitosamente.
- **📊 Metadatos Estructurales:** Información detallada sobre la estructura del documento (títulos, tablas, listas) para mejor rastreabilidad.
- **🔍 Búsquedas Avanzadas con Filtros:** Sistema de filtrado por metadatos para búsquedas más precisas y relevantes.
- **📈 Estadísticas de Base de Conocimientos:** Información detallada sobre el contenido almacenado y su estructura.
- **LLM Local y Privado:** Utiliza modelos de lenguaje locales a través de [Ollama](https://ollama.com/) (ej. Llama 3, Mistral), asegurando que tus datos y preguntas nunca salgan de tu máquina.
- **100% Local y Offline:** Tanto el modelo de lenguaje como los embeddings se ejecutan en tu máquina. Ningún dato sale a internet. Una vez descargados los modelos, funciona sin conexión.
- **Ingesta Masiva:** Scripts dedicados para procesar directorios enteros de documentos y construir la base de conocimiento de manera eficiente.
- **Arquitectura Modular:** La lógica del RAG está separada de los scripts de servidor y de ingesta, facilitando el mantenimiento y la expansión.
- **Copias en Markdown:** Cada documento procesado se guarda automáticamente en formato Markdown para verificación y reutilización.
- **🆕 Metadatos de Fuente:** Rastreabilidad completa de información con atribución de fuentes en cada respuesta.
- **🆕 Optimizado para Agentes de IA:** Descripciones detalladas y manejo de errores inteligente para uso efectivo por agentes de IA.
- **🆕 Sistema de Scripts Organizado:** Estructura modular de scripts que separa instalación, ejecución y diagnóstico.

---

## 🏗️ Arquitectura

El proyecto está organizado en una estructura modular que separa claramente los componentes del servidor MCP y la interfaz gráfica de usuario (GUI). Esta organización facilita el mantenimiento, desarrollo y uso independiente de cada componente.

### **Estructura del Proyecto:**

```
MCP_RAG/
├── 📁 mcp_server_organized/          # Servidor MCP principal
│   ├── 📄 server.py                  # Servidor MCP con herramientas RAG
│   ├── 📄 run_server_organized.bat   # Script para ejecutar el servidor
│   ├── 📁 src/                       # Código fuente del servidor
│   │   ├── 📄 rag_core.py            # Lógica principal del RAG
│   │   ├── 📄 rag_server_bk.py       # Servidor MCP (backup)
│   │   ├── 📁 models/                # Modelos de datos
│   │   ├── 📁 services/              # Servicios del servidor
│   │   ├── 📁 tools/                 # Herramientas MCP
│   │   └── 📁 utils/                 # Utilidades
│   ├── 📁 tests/                     # Pruebas del servidor
│   ├── 📁 data/                      # Datos del servidor
│   │   ├── 📁 documents/             # Documentos procesados
│   │   └── 📁 vector_store/          # Base de datos vectorial
│   └── 📁 embedding_cache/           # Cache de embeddings
│
├── 📁 bulk_ingest_GUI/               # Interfaz gráfica de usuario
│   ├── 📄 main.py                    # Punto de entrada principal
│   ├── 📄 launch.py                  # Lanzador de la aplicación
│   ├── 📄 start_app.py               # Inicialización de la app
│   ├── 📄 rag_core_wrapper.py        # Wrapper para rag_core
│   ├── 📁 views/                     # Vistas de la interfaz
│   │   └── 📄 main_view.py           # Vista principal
│   ├── 📁 controllers/               # Controladores
│   │   └── 📄 main_controller.py     # Controlador principal
│   ├── 📁 services/                  # Servicios de la GUI
│   │   ├── 📄 document_service.py    # Servicio de documentos
│   │   └── 📄 configuration_service.py # Servicio de configuración
│   ├── 📁 models/                    # Modelos de la GUI
│   ├── 📁 widgets/                   # Widgets personalizados
│   ├── 📁 gui_utils/                 # Utilidades de la GUI
│   ├── 📁 data/                      # Datos de la GUI
│   │   ├── 📁 documents/             # Documentos procesados
│   │   └── 📁 vector_store/          # Base de datos vectorial
│   └── 📁 embedding_cache/           # Cache de embeddings
│
├── 📄 start.bat                      # Script principal de arranque
├── 📄 run_gui.bat                    # Script para ejecutar la GUI
├── 📄 install_requirements.bat       # Instalación de dependencias
├── 📄 requirements.txt               # Dependencias del proyecto
├── 📄 README.md                      # Documentación principal
├── 📄 SCRIPTS_README.md              # Guía de scripts
├── 📄 GUI_ADVANCED_README.md         # Guía de la GUI para ingesta de documentos masivo
└── 📄 AGENT_INSTRUCTIONS.md          # Instrucciones para agentes IA
```

### **Componentes Principales:**

#### **1. Servidor MCP (`mcp_server_organized/`)**
- **`server.py`**: Servidor MCP principal que expone las herramientas RAG
- **`src/rag_core.py`**: El corazón del sistema RAG con toda la lógica de procesamiento
- **`src/tools/`**: Herramientas MCP (`learn_text`, `learn_document`, `ask_rag`, etc.)
- **`src/services/`**: Servicios del servidor (configuración, logging, etc.)
- **`src/models/`**: Modelos de datos para el servidor
- **`src/utils/`**: Utilidades compartidas

#### **2. Interfaz Gráfica (`bulk_ingest_GUI/`)**
- **`main.py`**: Punto de entrada principal de la aplicación GUI
- **`views/main_view.py`**: Interfaz de usuario principal con pestañas
- **`controllers/main_controller.py`**: Lógica de control de la interfaz
- **`services/document_service.py`**: Servicio para procesamiento de documentos
- **`services/configuration_service.py`**: Gestión de configuración
- **`widgets/`**: Componentes personalizados de la interfaz
- **`gui_utils/`**: Utilidades específicas de la GUI

#### **3. Scripts de Sistema**
- **`start.bat`**: Script principal que guía al usuario
- **`run_gui.bat`**: Ejecuta directamente la aplicación GUI
- **`install_requirements.bat`**: Instalación completa de dependencias
- **`check_system.bat`**: Diagnóstico del sistema
- **`fix_dependencies.bat`**: Reparación de dependencias

### **Flujo de Datos:**

1. **Ingesta de Documentos**: La GUI procesa documentos usando `rag_core_wrapper.py`
2. **Almacenamiento**: Los documentos se guardan en la base de datos vectorial
3. **Consulta**: El servidor MCP accede a la misma base de datos para responder consultas
4. **Respuesta**: Las herramientas MCP devuelven respuestas con fuentes

### **Separación de Responsabilidades:**

- **Servidor MCP**: Se enfoca en exponer herramientas para clientes de IA
- **GUI**: Se enfoca en la experiencia de usuario para ingesta de documentos
- **RAG Core**: Lógica compartida entre ambos componentes
- **Scripts**: Automatización y gestión del entorno

Esta arquitectura modular permite:
- ✅ Desarrollo independiente de cada componente
- ✅ Reutilización de código entre servidor y GUI
- ✅ Fácil mantenimiento y debugging
- ✅ Escalabilidad para nuevas características
- ✅ Uso independiente del servidor o la GUI

### **Archivos de Documentación:**
- [`AGENT_INSTRUCTIONS.md`](./AGENT_INSTRUCTIONS.md): Guía completa para agentes de IA sobre cómo usar el sistema
- [`GUI_ADVANCED_README.md`](./GUI_ADVANCED_README.md): Guía detallada para la interfaz gráfica para ingesta de documentos masivo
- [`SCRIPTS_README.md`](./SCRIPTS_README.md): Guía completa del sistema de scripts organizados
- [`STORAGE_PROGRESS_README.md`](./STORAGE_PROGRESS_README.md): Documentación del sistema de progreso de almacenamiento
- `test_enhanced_rag.py`: Script de prueba para verificar el funcionamiento del sistema

---

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos para poner en marcha el sistema.

### Prerrequisitos

- **Python 3.10+**
- **Ollama:** Asegúrate de que [Ollama esté instalado](https://ollama.com/) y en ejecución en tu sistema.
- **Tesseract OCR (Opcional):** Para procesar imágenes con texto. Descarga desde [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) o usa `choco install tesseract`.

### 1. Instalación (¡Automática!)

Gracias al sistema de scripts organizados, la instalación es increíblemente sencilla.

#### **Para Usuarios (Recomendado):**
1. **Ejecuta el script principal:** `start.bat`
2. **Selecciona "1"** para instalar dependencias
3. **Espera** a que termine la instalación automática
4. **La aplicación se iniciará** automáticamente

#### **Para Desarrolladores:**
- **Instalación completa:** `install_requirements.bat`
- **Ejecución:** `run_gui.bat`
- **Diagnóstico:** `check_system.bat`

El sistema de scripts hace todo por ti:
- ✅ Crea un entorno virtual de Python en una carpeta `.venv`
- ✅ Activa el entorno automáticamente
- ✅ Instala todas las dependencias necesarias desde `requirements.txt`
- ✅ Detecta automáticamente si tienes GPU NVIDIA y instala PyTorch apropiadamente
- ✅ Instala Unstructured con capacidades avanzadas
- ✅ Lanza la aplicación

En ejecuciones posteriores, el script simplemente activará el entorno y lanzará la aplicación directamente.

### 2. Instalación Manual de Dependencias (Opcional)

Si prefieres instalar las dependencias manualmente o necesitas capacidades específicas:

```bash
# Activar entorno virtual
.\.venv\Scripts\activate

# Instalación completa de Unstructured con todas las capacidades
pip install "unstructured[local-inference,all-docs]"

# Dependencias adicionales para mejor rendimiento
pip install python-docx openpyxl beautifulsoup4 pytesseract
```

### 3. Configuración de Ollama (Paso Crítico)

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

El sistema RAG necesita un modelo de lenguaje para generar respuestas. Se utiliza Ollama por ser gratis:

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

### 4. Verificación Completa del Sistema

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
python -c "import unstructured; print('✅ Unstructured instalado correctamente')"
```

#### Paso 3: Probar el Sistema RAG
```bash
# Ejecutar el script de prueba mejorado
python test_enhanced_rag.py
```

Si todo funciona correctamente, verás:
- ✅ Ollama respondiendo a comandos
- ✅ Todas las dependencias importándose sin errores
- ✅ El sistema RAG procesando preguntas y mostrando fuentes

**¡Tu sistema RAG está listo para usar!** 🚀

---

## 📋 Formatos de Archivo Soportados

El sistema soporta **más de 25 formatos de archivo** con procesamiento optimizado:

### 📄 **Documentos de Office:**
- **PDF** (.pdf) - Con procesamiento de alta resolución
- **Word** (.docx, .doc) - Documentos de Microsoft Word
- **PowerPoint** (.pptx, .ppt) - Presentaciones
- **Excel** (.xlsx, .xls) - Hojas de cálculo
- **RTF** (.rtf) - Formato de texto enriquecido

### 📁 **Documentos OpenDocument:**
- **ODT** (.odt) - Documentos de texto (LibreOffice/OpenOffice)
- **ODP** (.odp) - Presentaciones (LibreOffice/OpenOffice)
- **ODS** (.ods) - Hojas de cálculo (LibreOffice/OpenOffice)

### 🌐 **Formatos Web y Markup:**
- **HTML** (.html, .htm) - Páginas web
- **XML** (.xml) - Datos estructurados
- **Markdown** (.md) - Documentación técnica

### 📝 **Formatos de Texto Plano:**
- **TXT** (.txt) - Texto simple
- **CSV** (.csv) - Datos tabulares
- **TSV** (.tsv) - Datos tabulares separados por tabulaciones

### 📊 **Formatos de Datos:**
- **JSON** (.json) - Datos estructurados
- **YAML** (.yaml, .yml) - Configuraciones y datos

### 🖼️ **Imágenes (con OCR):**
- **PNG** (.png) - Imágenes con texto
- **JPG/JPEG** (.jpg, .jpeg) - Fotografías con texto
- **TIFF** (.tiff) - Imágenes de alta calidad
- **BMP** (.bmp) - Imágenes de mapa de bits

### 📧 **Correos Electrónicos:**
- **EML** (.eml) - Archivos de correo
- **MSG** (.msg) - Mensajes de Outlook

---

## 🛠️ Guía de Uso

### Uso 1: Poblar la Base de Conocimiento con la GUI (Recomendado)

La forma más fácil e intuitiva de añadir documentos es usando la interfaz gráfica.

1. **Ejecuta el script principal:** `start.bat`
2. **Selecciona "1"** para ejecutar la aplicación
3. **La aplicación se iniciará** (la primera vez puede tardar mientras instala las dependencias)
4. **Usa el botón "Explorar..."** para seleccionar la carpeta con tus documentos
5. **Haz clic en "Iniciar Procesamiento"**. Los archivos se procesarán con el sistema avanzado de Unstructured
6. **Ve a la pestaña "Revisión"**, selecciona los archivos que quieres guardar y previsualiza su contenido
7. **Ve a la pestaña "Almacenamiento"** y haz clic en "Iniciar Almacenamiento" para guardar los documentos seleccionados en la base de datos

#### ✨ **GUI para ingesta de documentos masivo con Previsualización y Selección**

Para un control total sobre el proceso de ingesta, hemos añadido una **GUI**. Esta versión te permite **previsualizar** el contenido de cada documento procesado y **seleccionar manualmente** cuáles quieres incluir en la base de conocimiento.

**Características de la GUI:**
- **Procesamiento Inteligente:** Usa Unstructured para limpiar ruido y preservar estructura
- **Previsualización en Tiempo Real:** Ve el contenido procesado antes de almacenar
- **Selección Granular:** Marca/desmarca documentos individualmente
- **Metadatos Estructurales:** Información sobre títulos, tablas, listas en cada documento
- **Sistema de Fallbacks:** Múltiples estrategias garantizan que todo documento se procese
- **Sistema de Progreso:** Seguimiento detallado del proceso de almacenamiento

![Pestaña de Procesamiento de la GUI](src/images/gui_procesamiento.png)

➡️ **Para una guía completa sobre cómo usarla, consulta el [Guia de Carga Masiva](./GUI_ADVANCED_README.md).**

### Uso 2: Poblar la Base de Conocimiento desde la Línea de Comandos

Si prefieres usar la línea de comandos o necesitas automatizar la ingesta.

1. **Abre una terminal**
2. **Activa el entorno virtual:** `.\.venv\Scripts\activate`
3. **Ejecuta el script `bulk_ingest.py`** apuntando a tu carpeta de documentos:
    ```bash
    python bulk_ingest.py --directory "C:\Ruta\A\Tus\Documentos"
    ```

**Características del Procesamiento Mejorado:**
- **Detección Automática de Formato:** El sistema identifica y optimiza el procesamiento según el tipo de archivo
- **Limpieza Inteligente:** Elimina automáticamente cabeceras, pies de página y contenido irrelevante
- **Preservación de Estructura:** Mantiene títulos, listas y tablas organizadas
- **Metadatos Enriquecidos:** Información detallada sobre la estructura de cada documento
- **Logs Detallados:** Información completa sobre el proceso de cada archivo

### Uso 3: Configuración del Cliente MCP (Ej. Cursor)

Para que tu editor de IA pueda usar el servidor, debes configurarlo.

1. **Encuentra el archivo de configuración de servidores MCP de tu editor.** Para Cursor, busca un archivo como `mcp_servers.json` en su directorio de configuración (`%APPDATA%\cursor` en Windows). Si no existe, puedes crearlo.

2. **Añade la siguiente configuración al archivo JSON.**
    
    Este método utiliza el script del servidor MCP (`run_server_organized.bat`) para ejecutar el servidor RAG.

    **¡IMPORTANTE!** Debes reemplazar `"D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG"` con la ruta absoluta real a la carpeta de este proyecto en tu máquina.

    ```json
    {
      "mcpServers": {
        "rag": {
          "command": "D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG\\mcp_server_organized\\run_server_organized.bat",
          "args": [],
          "workingDirectory": "D:\\ruta\\completa\\a\\tu\\proyecto\\MCP_RAG"
        }
      }
    }
    ```

3. **Reinicia tu editor.** Al arrancar, debería detectar y lanzar el servidor MCP, que expondrá las herramientas RAG para uso en el chat.

### Uso 4: Interactuando con las Herramientas

Una vez configurado, puedes usar las herramientas directamente en el chat de tu editor.

#### Herramientas Disponibles:

**1. `learn_text(text, source_name)` - Añadir información textual**
```
@rag learn_text("El punto de fusión del titanio es 1,668 °C.", "material_properties")
```
- **Cuándo usar**: Para añadir hechos, definiciones, notas de conversación, etc.
- **Parámetros**: 
  - `text`: El contenido a almacenar
  - `source_name`: Nombre descriptivo de la fuente (opcional, por defecto "manual_input")

**2. `learn_document(file_path)` - Procesar documentos**
```
@rag learn_document("C:\\Reportes\\informe_q3.pdf")
```
- **Cuándo usar**: Para procesar archivos PDF, DOCX, PPTX, XLSX, TXT, HTML, CSV, JSON, XML, imágenes, correos electrónicos y más de 25 formatos
- **Características Mejoradas**: 
  - **Procesamiento Inteligente**: Usa Unstructured para limpiar ruido y preservar estructura
  - **Sistema de Fallbacks**: Múltiples estrategias garantizan procesamiento exitoso
  - **Metadatos Estructurales**: Información detallada sobre títulos, tablas, listas
  - **Conversión Automática**: Procesamiento optimizado según el tipo de archivo
  - **Copias Guardadas**: Documentos procesados guardados en `./converted_docs/`

**3. `ask_rag(query)` - Consultar información**
```
@rag ask_rag("¿Cuál es el punto de fusión del titanio?")
```
- **Cuándo usar**: Para buscar información previamente almacenada
- **Respuesta incluye**: 
  - Respuesta generada por IA con contexto mejorado
  - 📚 Lista de fuentes utilizadas con metadatos estructurales
  - Información sobre la relevancia de cada fuente

**4. `ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)` - Búsquedas con filtros**
```
@rag ask_rag_filtered("¿Qué tablas de datos tenemos?", file_type=".pdf", min_tables=1)
```
- **Cuándo usar**: Para búsquedas más precisas usando filtros de metadatos
- **Filtros disponibles**:
  - `file_type`: Tipo de archivo (ej. ".pdf", ".docx", ".xlsx")
  - `min_tables`: Mínimo número de tablas en el documento
  - `min_titles`: Mínimo número de títulos en el documento
  - `processing_method`: Método de procesamiento usado
- **Ventajas**: Búsquedas más relevantes y específicas

**5. `get_knowledge_base_stats()` - Estadísticas de la base de conocimientos**
```
@rag get_knowledge_base_stats()
```
- **Cuándo usar**: Para obtener información sobre el contenido almacenado
- **Información proporcionada**:
  - Número total de documentos
  - Distribución por tipo de archivo
  - Estadísticas de estructura (tablas, títulos, listas)
  - Métodos de procesamiento utilizados

#### Ejemplo de Flujo Completo:

```bash
# 1. Añadir información
@rag learn_text("La temperatura de fusión del titanio es 1,668°C.", "material_properties")

# 2. Procesar un documento complejo (ahora con procesamiento mejorado)
@rag learn_document("C:\\Documents\\manual_titanio.pdf")

# 3. Hacer preguntas (con respuestas mejoradas)
@rag ask_rag("¿Cuál es la temperatura de fusión del titanio?")

# 4. Búsqueda filtrada por documentos con tablas
@rag ask_rag_filtered("¿Qué datos tabulares tenemos?", min_tables=1)

# 5. Ver estadísticas de la base de conocimientos
@rag get_knowledge_base_stats()
```

**Respuesta esperada:**
```
La temperatura de fusión del titanio es 1,668°C.

📚 Fuentes de información:
   1. material_properties (manual_input)
   2. manual_titanio.pdf (página 3, sección "Propiedades Físicas")

📊 Estadísticas de búsqueda filtrada:
   • Documentos con tablas encontrados: 3
   • Tipos de archivo: PDF (2), DOCX (1)
   • Total de tablas: 7
```

---

## 🧪 Pruebas y Verificación

### Probar el Sistema

Para verificar que todo funciona correctamente:

```bash
# Probar el sistema RAG mejorado con todas las características
python test_enhanced_rag.py
```

#### **Script de Pruebas Mejorado (`test_enhanced_rag.py`)**

El script de pruebas verifica todas las mejoras implementadas:

**🧪 Pruebas Incluidas:**
- **Procesamiento Mejorado de Documentos**: Verifica el sistema Unstructured con metadatos estructurales
- **Base de Conocimientos Mejorada**: Prueba el chunking mejorado y metadatos enriquecidos
- **Integración del Servidor MCP**: Verifica las herramientas mejoradas del servidor
- **Soporte de Formatos**: Confirma la configuración para más de 25 formatos

**📊 Información de Salida:**
- Estado de cada prueba (✅ PASÓ / ❌ FALLÓ)
- Metadatos estructurales extraídos
- Método de procesamiento utilizado
- Información de fuentes y chunks
- Resumen completo del sistema

### Verificar la Base de Datos

Los documentos procesados se almacenan en:
- **Base de datos vectorial**: `./rag_mcp_db/`
- **Copias procesadas**: `./converted_docs/` (con información del método de procesamiento)

---

## 🤖 Uso por Agentes de IA

El sistema está optimizado para ser utilizado por agentes de IA. Consulta [`AGENT_INSTRUCTIONS.md`](./AGENT_INSTRUCTIONS.md) para:

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

## 🔧 Mejoras Técnicas Implementadas

Esta sección explica las mejoras técnicas avanzadas que han transformado el sistema en una solución de nivel empresarial.

### **A. Procesamiento Inteligente con Unstructured**

#### **¿Qué es Unstructured?**

Unstructured es una librería de procesamiento de documentos que va más allá de la simple extracción de texto. Analiza la **estructura semántica** de los documentos para:

- **Identificar elementos**: Títulos, párrafos, listas, tablas
- **Limpiar ruido**: Eliminar cabeceras, pies de página, elementos irrelevantes
- **Preservar contexto**: Mantener la jerarquía y estructura del documento
- **Manejar formatos complejos**: PDFs escaneados, documentos con tablas, etc.

#### **Configuración Optimizada por Tipo de Archivo:**

```python
UNSTRUCTURED_CONFIGS = {
    '.pdf': {
        'strategy': 'hi_res',        # Alta resolución para PDFs complejos
        'include_metadata': True,    # Incluir metadatos estructurales
        'include_page_breaks': True, # Preservar saltos de página
        'max_partition': 2000,       # Tamaño máximo de partición
        'new_after_n_chars': 1500    # Nuevo elemento después de N caracteres
    },
    '.docx': {
        'strategy': 'fast',          # Procesamiento rápido para documentos de Office
        'include_metadata': True,
        'max_partition': 2000,
        'new_after_n_chars': 1500
    },
    # ... configuraciones para más de 25 formatos
}
```

#### **Procesamiento Inteligente de Elementos:**

```python
def process_unstructured_elements(elements: List[Any]) -> str:
    """Procesa elementos de Unstructured preservando estructura semántica."""
    for element in elements:
        element_type = type(element).__name__
        
        if element_type == 'Title':
            # Los títulos van con formato especial
            processed_parts.append(f"\n## {element.text.strip()}\n")
        elif element_type == 'ListItem':
            # Las listas mantienen su estructura
            processed_parts.append(f"• {element.text.strip()}")
        elif element_type == 'Table':
            # Las tablas se convierten a texto legible
            table_text = convert_table_to_text(element)
            processed_parts.append(f"\n{table_text}\n")
        elif element_type == 'NarrativeText':
            # El texto narrativo va tal como está
            processed_parts.append(element.text.strip())
```

### **B. Sistema de Fallbacks Robusto**

#### **Estrategia de Fallbacks en Cascada:**

El sistema intenta múltiples estrategias en orden de preferencia:

1. **Unstructured con Configuración Óptima**
   - Usa la configuración específica para el tipo de archivo
   - Máxima calidad de procesamiento

2. **Unstructured con Configuración Básica**
   - Estrategia "fast" para compatibilidad
   - Procesamiento más simple pero funcional

3. **Cargadores Específicos de LangChain**
   - Cargadores especializados por tipo de archivo
   - Último recurso para formatos problemáticos

#### **Ejemplo de Fallback en Acción:**

```python
def load_document_with_fallbacks(file_path: str) -> tuple[str, dict]:
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Estrategia 1: Unstructured óptimo
    try:
        config = UNSTRUCTURED_CONFIGS.get(file_extension, DEFAULT_CONFIG)
        elements = partition(filename=file_path, **config)
        processed_text = process_unstructured_elements(elements)
        metadata = extract_structural_metadata(elements, file_path)
        return processed_text, metadata
    except Exception as e:
        log(f"Core Warning: Unstructured óptimo falló: {e}")
    
    # Estrategia 2: Unstructured básico
    try:
        elements = partition(filename=file_path, strategy="fast")
        # ... procesamiento
    except Exception as e:
        log(f"Core Warning: Unstructured básico falló: {e}")
    
    # Estrategia 3: LangChain fallbacks
    try:
        fallback_text = load_with_langchain_fallbacks(file_path)
        # ... procesamiento
    except Exception as e:
        log(f"Core Warning: LangChain fallbacks fallaron: {e}")
    
    return "", {}  # Solo si todas las estrategias fallan
```

### **C. Metadatos Estructurales Enriquecidos**

#### **Información Estructural Capturada:**

```python
def extract_structural_metadata(elements: List[Any], file_path: str) -> Dict[str, Any]:
    structural_info = {
        "total_elements": len(elements),
        "titles_count": sum(1 for e in elements if type(e).__name__ == 'Title'),
        "tables_count": sum(1 for e in elements if type(e).__name__ == 'Table'),
        "lists_count": sum(1 for e in elements if type(e).__name__ == 'ListItem'),
        "narrative_blocks": sum(1 for e in elements if type(e).__name__ == 'NarrativeText'),
        "total_text_length": total_text_length,
        "avg_element_length": total_text_length / len(elements) if elements else 0
    }
    
metadata = {
        "source": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": os.path.splitext(file_path)[1].lower(),
        "processed_date": datetime.now().isoformat(),
        "processing_method": "unstructured_enhanced",
        "structural_info": structural_info
    }
```

#### **Beneficios de los Metadatos Estructurales:**

- **Rastreabilidad**: Sabes exactamente qué parte del documento se usó
- **Calidad**: Información sobre la estructura del contenido
- **Optimización**: Datos para mejorar el procesamiento futuro
- **Debugging**: Información detallada para resolver problemas

### **D. División Inteligente de Texto Mejorada**

#### **Configuración Optimizada:**

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

### **E. Motor de Búsqueda Optimizado**

#### **Configuración Actual:**

```python
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",  # Búsqueda con umbral de similitud
search_kwargs={
        "k": 5,                # Recupera 5 fragmentos más relevantes
        "score_threshold": 0.3, # Umbral de distancia (similitud > 0.7)
    }
)
```

#### **Parámetros Optimizados:**

- **`k=5`**: Obtienes información de 5 fuentes diferentes para respuestas más completas
- **`score_threshold=0.3`**: Garantiza que solo se use información muy relevante (similitud > 70%)
- **Búsqueda por similitud**: Encuentra el contenido más semánticamente similar

### **F. Limpieza Automática de Texto**

#### **Proceso de Limpieza:**

```python
def clean_text_for_rag(text: str) -> str:
    """Limpia y prepara el texto para mejorar la calidad de las búsquedas RAG."""
    if not text:
        return ""
    
    # Eliminar espacios múltiples y saltos de línea excesivos
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres especiales problemáticos pero mantener puntuación importante
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']', '', text)
    
    # Normalizar espacios alrededor de puntuación
    text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
    
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text
```

### **G. Sistema de Filtrado de Metadatos Avanzado**

#### **Funcionalidades de Filtrado:**

El sistema ahora incluye capacidades avanzadas de filtrado que permiten búsquedas más precisas y relevantes:

```python
def create_metadata_filter(file_type: str = None, processing_method: str = None,
                          min_tables: int = None, min_titles: int = None,
                          source_contains: str = None) -> dict:
    """Crea filtros de metadatos para búsquedas más precisas."""
    filters = []
    
    if file_type:
        filters.append({"file_type": file_type})
    if processing_method:
        filters.append({"processing_method": processing_method})
    if min_tables:
        filters.append({"structural_info_tables_count": {"$gte": min_tables}})
    if min_titles:
        filters.append({"structural_info_titles_count": {"$gte": min_titles}})
    if source_contains:
        filters.append({"source": {"$contains": source_contains}})
    
    return {"$and": filters} if len(filters) > 1 else filters[0] if filters else None
```

#### **Búsquedas con Filtros:**

```python
def search_with_metadata_filters(vector_store: Chroma, query: str, 
                                metadata_filter: dict = None, k: int = 5) -> List[Any]:
    """Realiza búsquedas con filtros de metadatos para mayor precisión."""
    if metadata_filter:
        # Búsqueda con filtros específicos
        results = vector_store.similarity_search_with_relevance_scores(
            query, k=k, filter=metadata_filter
        )
    else:
        # Búsqueda normal sin filtros
        results = vector_store.similarity_search_with_relevance_scores(query, k=k)
    
    return results
```

#### **Estadísticas de Base de Conocimientos:**

```python
def get_document_statistics(vector_store: Chroma) -> dict:
    """Obtiene estadísticas detalladas sobre la base de conocimientos."""
    all_docs = vector_store.get()
    
    if not all_docs or not all_docs.get('metadatas'):
        return {"total_documents": 0}
    
    metadatas = all_docs['metadatas']
    
    # Análisis por tipo de archivo
    file_types = {}
    processing_methods = {}
    total_tables = 0
    total_titles = 0
    
    for metadata in metadatas:
        file_type = metadata.get("file_type", "unknown")
        processing_method = metadata.get("processing_method", "unknown")
        tables_count = metadata.get("structural_info_tables_count", 0)
        titles_count = metadata.get("structural_info_titles_count", 0)
        
        file_types[file_type] = file_types.get(file_type, 0) + 1
        processing_methods[processing_method] = processing_methods.get(processing_method, 0) + 1
        total_tables += tables_count
        total_titles += titles_count
    
    return {
        "total_documents": len(metadatas),
        "file_types": file_types,
        "processing_methods": processing_methods,
        "total_tables": total_tables,
        "total_titles": total_titles,
        "avg_tables_per_doc": total_tables / len(metadatas) if metadatas else 0,
        "avg_titles_per_doc": total_titles / len(metadatas) if metadatas else 0
    }
```

#### **Casos de Uso de Filtrado:**

1. **Búsqueda por Tipo de Archivo:**
   ```python
   # Solo buscar en PDFs
   pdf_filter = create_metadata_filter(file_type=".pdf")
   results = search_with_metadata_filters(vector_store, "datos", pdf_filter)
   ```

2. **Búsqueda por Estructura:**
   ```python
   # Solo documentos con tablas
   tables_filter = create_metadata_filter(min_tables=1)
   results = search_with_metadata_filters(vector_store, "datos tabulares", tables_filter)
   ```

3. **Búsqueda por Método de Procesamiento:**
   ```python
   # Solo documentos procesados con Unstructured
   unstructured_filter = create_metadata_filter(processing_method="unstructured_enhanced")
   results = search_with_metadata_filters(vector_store, "contenido", unstructured_filter)
   ```

4. **Filtros Combinados:**
   ```python
   # PDFs con tablas procesados con Unstructured
   complex_filter = create_metadata_filter(
       file_type=".pdf", 
       min_tables=1, 
       processing_method="unstructured_enhanced"
   )
   results = search_with_metadata_filters(vector_store, "datos", complex_filter)
   ```

### **H. Herramientas MCP Mejoradas**

#### **Nuevas Herramientas Disponibles:**

1. **`ask_rag_filtered`**: Búsquedas con filtros de metadatos
2. **`get_knowledge_base_stats`**: Estadísticas detalladas de la base de conocimientos

#### **Integración con Agentes de IA:**

Las nuevas herramientas están optimizadas para uso por agentes de IA con:
- **Descripciones detalladas** de parámetros y casos de uso
- **Ejemplos específicos** de cada herramienta
- **Manejo de errores inteligente** con sugerencias útiles
- **Respuestas estructuradas** con información de metadatos

---
