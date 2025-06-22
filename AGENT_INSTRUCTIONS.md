# Instrucciones para Agentes de IA - Sistema RAG Mejorado

## 🎯 Propósito del Sistema

Este sistema RAG (Retrieval-Augmented Generation) **mejorado** permite a los agentes de IA:
- **Almacenar información** de forma persistente con procesamiento inteligente
- **Consultar conocimiento** previamente guardado con metadatos estructurales
- **Rastrear fuentes** de información con detalles completos
- **Procesar documentos** automáticamente con más de 25 formatos
- **Preservar estructura** semántica de documentos (títulos, tablas, listas)
- **Eliminar ruido** automáticamente (cabeceras, pies de página, contenido irrelevante)
- **🔍 Realizar búsquedas filtradas** por metadatos para mayor precisión
- **📊 Obtener estadísticas** detalladas de la base de conocimientos

## 🚀 Nuevas Características del Sistema Mejorado

### **🧠 Procesamiento Inteligente con Unstructured**
- **Preservación de Estructura**: Mantiene títulos, listas, tablas organizadas
- **Limpieza Automática**: Elimina cabeceras, pies de página y contenido irrelevante
- **Metadatos Estructurales**: Información detallada sobre la estructura del documento
- **Sistema de Fallbacks**: Múltiples estrategias garantizan procesamiento exitoso

### **📋 Soporte Expandido de Formatos**
**Más de 25 formatos soportados:**
- **Documentos de Office**: PDF, DOCX, PPTX, XLSX, RTF
- **OpenDocument**: ODT, ODP, ODS
- **Web y Markup**: HTML, XML, Markdown
- **Texto y Datos**: TXT, CSV, TSV, JSON, YAML
- **Imágenes con OCR**: PNG, JPG, TIFF, BMP
- **Correos Electrónicos**: EML, MSG

### **🎯 Chunking Semántico Inteligente**
- **División Natural**: Respeta la estructura del documento
- **Overlap Inteligente**: Mantiene continuidad entre fragmentos
- **Contexto Preservado**: No corta en medio de ideas

### **🔍 Búsquedas Avanzadas con Filtros**
- **Filtrado por Tipo de Archivo**: Buscar solo en PDFs, DOCX, etc.
- **Filtrado por Estructura**: Documentos con tablas, títulos específicos
- **Filtrado por Método de Procesamiento**: Unstructured vs MarkItDown
- **Filtros Combinados**: Múltiples criterios simultáneos

### **📈 Estadísticas de Base de Conocimientos**
- **Análisis de Contenido**: Distribución por tipo de archivo
- **Métricas Estructurales**: Total de tablas, títulos, listas
- **Información de Procesamiento**: Métodos utilizados
- **Insights Automáticos**: Promedios y tendencias

## 🛠️ Herramientas Disponibles

### 1. `learn_text(text, source_name)`
**Cuándo usar**: Para añadir información textual que el agente debe recordar.

**Ejemplos de uso**:
```python
# Añadir definiciones importantes
learn_text("La inteligencia artificial es la simulación de procesos de inteligencia humana por máquinas.", "ai_definitions")

# Guardar notas de conversación
learn_text("El usuario mencionó que trabaja en el sector financiero y necesita análisis de datos.", "conversation_notes")

# Almacenar hechos específicos
learn_text("La temperatura de fusión del titanio es 1,668°C.", "material_properties")
```

### 2. `learn_document(file_path)` - **MEJORADO**
**Cuándo usar**: Para procesar y almacenar contenido de archivos con procesamiento inteligente.

**Nuevas capacidades**:
- **Procesamiento Inteligente**: Usa Unstructured para preservar estructura
- **Metadatos Estructurales**: Información sobre títulos, tablas, listas
- **Sistema de Fallbacks**: Múltiples estrategias de procesamiento
- **Soporte Amplio**: Más de 25 formatos de archivo

**Ejemplos de uso**:
```python
# Procesar un informe con estructura compleja
learn_document("C:/Documents/informe_trimestral.pdf")

# Añadir un manual técnico con tablas y listas
learn_document("D:/Manuals/manual_usuario.docx")

# Importar datos de una hoja de cálculo
learn_document("E:/Data/datos_ventas.xlsx")

# Procesar imágenes con texto (requiere OCR)
learn_document("F:/Scans/documento_escaneado.png")

# Procesar correos electrónicos
learn_document("G:/Emails/importante.msg")
```

**Respuesta mejorada de `learn_document`**:
```
✅ **Documento procesado exitosamente**
📄 **Archivo:** informe_trimestral.pdf
📋 **Tipo:** PDF
🔧 **Método:** Unstructured Enhanced

📊 **Estructura del documento:**
   • Elementos totales: 15
   • Títulos: 3
   • Tablas: 2
   • Listas: 4
   • Bloques narrativos: 6

💾 **Copia guardada:** ./converted_docs/informe_trimestral_unstructured_enhanced.md
📚 **Estado:** Añadido a la base de conocimientos con chunking semántico
```

### 3. `learn_from_url(url)` - **MEJORADO**
**Cuándo usar**: Para procesar contenido web o descargar y procesar archivos directamente desde URLs.

**Nuevas capacidades**:
- **Detección Automática**: Identifica archivos descargables vs páginas web
- **Procesamiento Mejorado**: Usa Unstructured para archivos descargados
- **MarkItDown para Web**: Mantiene procesamiento web tradicional
- **Metadatos Enriquecidos**: Información del dominio y método de procesamiento

**Ejemplos de uso**:
```python
# Descargar y procesar un PDF desde una URL
learn_from_url("https://example.com/informe.pdf")

# Procesar una página web
learn_from_url("https://example.com/articulo")

# Descargar y procesar un documento de Word
learn_from_url("https://example.com/manual.docx")
```

### 4. `ask_rag(query)` - **MEJORADO**
**Cuándo usar**: Para consultar información previamente almacenada con información detallada de fuentes.

**Nuevas capacidades**:
- **Metadatos Estructurales**: Información sobre estructura de documentos
- **Información de Chunks**: Número de fragmento y total
- **Método de Procesamiento**: Tipo de procesamiento usado
- **Información de Confianza**: Nivel de confianza basado en número de fuentes

**Ejemplos de uso**:
```python
# Buscar información específica
ask_rag("¿Cuál es la temperatura de fusión del titanio?")

# Consultar sobre un documento procesado
ask_rag("¿Qué dice el informe trimestral sobre las ventas?")

# Buscar contexto sobre un tema
ask_rag("¿Qué información tenemos sobre inteligencia artificial?")
```

### 5. `ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)` - **NUEVA**
**Cuándo usar**: Para realizar búsquedas más precisas y específicas usando filtros de metadatos.

**Capacidades de filtrado**:
- **`file_type`**: Filtrar por tipo de archivo (ej. ".pdf", ".docx", ".xlsx")
- **`min_tables`**: Solo documentos con mínimo número de tablas
- **`min_titles`**: Solo documentos con mínimo número de títulos
- **`processing_method`**: Filtrar por método de procesamiento usado

**Ejemplos de uso**:
```python
# Buscar solo en documentos PDF
ask_rag_filtered("¿Qué información tenemos sobre ventas?", file_type=".pdf")

# Buscar documentos con tablas de datos
ask_rag_filtered("¿Qué datos tabulares tenemos?", min_tables=1)

# Buscar en documentos procesados con Unstructured
ask_rag_filtered("¿Qué contenido tenemos?", processing_method="unstructured_enhanced")

# Combinar múltiples filtros
ask_rag_filtered("¿Qué reportes PDF con tablas tenemos?", file_type=".pdf", min_tables=1)
```

**Respuesta de `ask_rag_filtered`**:
```
🤖 **Respuesta filtrada:**
Se encontraron 3 documentos PDF con tablas que contienen información sobre ventas.

📚 **Fuentes filtradas utilizadas:**
   1. **reporte_ventas_q1.pdf** (PDF, 2 tablas)
   2. **datos_ventas_2024.pdf** (PDF, 1 tabla)
   3. **analisis_ventas.pdf** (PDF, 3 tablas)

✅ **Filtros aplicados:** Tipo de archivo: PDF, Mínimo tablas: 1
📊 **Resultados:** 3 de 15 documentos totales
```

### 6. `get_knowledge_base_stats()` - **NUEVA**
**Cuándo usar**: Para obtener información detallada sobre el contenido almacenado en la base de conocimientos.

**Información proporcionada**:
- **Total de documentos** almacenados
- **Distribución por tipo de archivo** (PDF, DOCX, etc.)
- **Estadísticas estructurales** (total de tablas, títulos, listas)
- **Métodos de procesamiento** utilizados
- **Promedios** por documento

**Ejemplos de uso**:
```python
# Obtener estadísticas generales
get_knowledge_base_stats()

# Usar antes de búsquedas filtradas para entender el contenido
stats = get_knowledge_base_stats()
# Luego usar ask_rag_filtered con filtros apropiados
```

**Respuesta de `get_knowledge_base_stats`**:
```
📊 **Estadísticas de la Base de Conocimientos**

📄 **Documentos totales:** 25
📋 **Distribución por tipo:**
   • PDF: 12 documentos (48%)
   • DOCX: 8 documentos (32%)
   • XLSX: 3 documentos (12%)
   • TXT: 2 documentos (8%)

🏗️ **Estructura del contenido:**
   • Total de tablas: 47
   • Total de títulos: 156
   • Total de listas: 89
   • Promedio tablas por documento: 1.9
   • Promedio títulos por documento: 6.2

🔧 **Métodos de procesamiento:**
   • Unstructured Enhanced: 20 documentos (80%)
   • MarkItDown: 3 documentos (12%)
   • LangChain Fallback: 2 documentos (8%)

📈 **Insights:**
   • 76% de documentos contienen tablas
   • 92% procesados con método avanzado
   • Contenido rico en estructura semántica
```

## 🔄 Flujo de Trabajo Recomendado

### Paso 1: Cargar Información
```python
# Opción A: Texto directo
learn_text("Información importante...", "mi_fuente")

# Opción B: Documento con procesamiento mejorado
learn_document("ruta/al/documento.pdf")

# Opción C: Contenido web o archivo desde URL
learn_from_url("https://example.com/documento.pdf")
```

### Paso 2: Explorar el Contenido
```python
# Obtener estadísticas para entender qué tenemos
get_knowledge_base_stats()
```

### Paso 3: Consultar Información
```python
# Búsqueda general
respuesta = ask_rag("¿Cuál es la información importante?")

# Búsqueda filtrada para mayor precisión
respuesta_filtrada = ask_rag_filtered("¿Qué datos tenemos?", file_type=".pdf", min_tables=1)
```

### Paso 4: Verificar Fuentes Mejoradas
- Las respuestas incluyen metadatos estructurales detallados
- Información sobre método de procesamiento
- Nivel de confianza de la respuesta
- Filtros aplicados (en búsquedas filtradas)

## 📊 Ejemplo de Respuesta Mejorada de `ask_rag`

```
🤖 **Respuesta:**
El punto de fusión del titanio es 1,668 °C. Esta propiedad lo hace ideal para aplicaciones aeroespaciales donde se requieren materiales resistentes a altas temperaturas.

📚 **Fuentes de información utilizadas:**

   1. **material_properties**
      - **Tipo:** MANUAL_INPUT
      - **Procesamiento:** Manual Text
      - **Procesado:** 21/06/2025 17:30
      - **Fragmento:** 1 de 1
      - **Fragmento Relevante:**
        > _La temperatura de fusión del titanio es 1,668°C._

   2. **datasheet_titanium.pdf**
      - **Ruta:** `D:\Docs\datasheet_titanium.pdf`
      - **Tipo:** PDF
      - **Procesamiento:** Unstructured Enhanced
      - **Estructura:** 12 elementos (2 títulos, 1 tabla, 3 listas)
      - **Fragmento:** 3 de 5
      - **Procesado:** 21/06/2025 17:32
      - **Fragmento Relevante:**
        > _...el titanio puro tiene un punto de fusión de 1,668 grados Celsius, lo que lo hace ideal para aplicaciones aeroespaciales..._

✅ **Alta confianza:** Respuesta basada en múltiples fuentes
🧠 **Procesamiento inteligente:** 1 fuentes procesadas con Unstructured (preservación de estructura)
```

## ⚠️ Consideraciones Importantes

### Limitaciones
- **Alcance**: Solo puede acceder a información previamente almacenada
- **OCR**: Para imágenes con texto, requiere Tesseract OCR instalado
- **Tamaño**: Los archivos muy grandes pueden tardar en procesarse
- **Formato**: Algunos formatos muy específicos pueden requerir dependencias adicionales
- **Filtros**: Los filtros muy restrictivos pueden no devolver resultados

### Mejores Prácticas
1. **Usar nombres descriptivos** para las fuentes
2. **Verificar las rutas** de archivos antes de procesarlos
3. **Revisar las fuentes** en las respuestas para validar información
4. **Procesar documentos** antes de hacer preguntas sobre ellos
5. **Aprovechar metadatos estructurales** para entender mejor el contenido
6. **Usar chunking semántico** para documentos con estructura compleja
7. **Explorar estadísticas** antes de hacer búsquedas filtradas
8. **Combinar filtros** para búsquedas más precisas
9. **Verificar resultados** de búsquedas filtradas para confirmar relevancia

### Manejo de Errores Mejorado
- **Archivo no encontrado**: Verificar la ruta del archivo
- **Formato no soportado**: El sistema soporta más de 25 formatos
- **Error de OCR**: Instalar Tesseract para procesar imágenes con texto
- **Error de Unstructured**: Verificar instalación: `pip install 'unstructured[local-inference,all-docs]'`
- **Sin información**: Asegurarse de que se haya cargado información relevante
- **Filtros sin resultados**: Usar filtros menos restrictivos o verificar estadísticas
- **Error en filtros**: Verificar formato de parámetros de filtrado

## 📝 Ejemplos de Casos de Uso Mejorados

### Caso 1: Investigación Académica con Documentos Complejos
```python
# 1. Cargar papers de investigación con estructura compleja
learn_document("paper_ai_ethics.pdf")  # Preserva títulos, tablas, referencias
learn_document("survey_machine_learning.docx")  # Mantiene formato y estructura

# 2. Explorar el contenido cargado
get_knowledge_base_stats()

# 3. Consultar información específica con filtros
ask_rag_filtered("¿Cuáles son los principales desafíos éticos de la IA?", file_type=".pdf", min_titles=3)
```

### Caso 2: Análisis de Datos con Hojas de Cálculo
```python
# 1. Cargar datos y reportes con formato preservado
learn_document("datos_ventas.xlsx")  # Procesa tablas y datos estructurados
learn_document("reporte_analisis.pdf")  # Mantiene gráficos y tablas

# 2. Buscar específicamente datos tabulares
ask_rag_filtered("¿Cuáles fueron las ventas del Q3?", min_tables=1)

# 3. Verificar qué tipos de datos tenemos
get_knowledge_base_stats()
```

### Caso 3: Asistente Personal con Documentos Escaneados
```python
# 1. Almacenar información personal y documentos escaneados
learn_text("Mi dirección es 123 Calle Principal", "personal_info")
learn_document("documento_identidad_escaneado.png")  # OCR automático

# 2. Consultar cuando sea necesario
ask_rag("¿Cuál es mi información de contacto?")

# 3. Verificar documentos procesados con OCR
ask_rag_filtered("¿Qué documentos escaneados tenemos?", processing_method="unstructured_enhanced")
```

### Caso 4: Investigación Web con Descarga de Archivos
```python
# 1. Procesar contenido web y descargar documentos
learn_from_url("https://example.com/articulo")  # Página web
learn_from_url("https://example.com/informe.pdf")  # Descarga y procesa PDF

# 2. Explorar contenido web vs documentos
get_knowledge_base_stats()

# 3. Consultar información combinada con filtros
ask_rag_filtered("¿Qué información tenemos sobre el tema?", file_type=".pdf")
ask_rag_filtered("¿Qué contenido web tenemos?", processing_method="markitdown")
```

### Caso 5: Gestión de Documentos Empresariales
```python
# 1. Cargar diferentes tipos de documentos empresariales
learn_document("manual_empleados.docx")
learn_document("reporte_financiero.pdf")
learn_document("datos_ventas.xlsx")

# 2. Obtener estadísticas del contenido
get_knowledge_base_stats()

# 3. Búsquedas específicas por tipo de contenido
# Solo manuales y guías
ask_rag_filtered("¿Qué procedimientos tenemos?", file_type=".docx")

# Solo reportes con datos
ask_rag_filtered("¿Qué datos financieros tenemos?", min_tables=1)

# Solo documentos procesados con método avanzado
ask_rag_filtered("¿Qué contenido de alta calidad tenemos?", processing_method="unstructured_enhanced")
```

## 🎯 Consejos para Agentes Mejorados

1. **Aprovecha la estructura**: Los documentos mantienen títulos, tablas y listas
2. **Usa metadatos estructurales**: Para entender mejor el contenido de las fuentes
3. **Verifica el método de procesamiento**: Unstructured vs MarkItDown
4. **Confía en el chunking semántico**: Mejor contexto en las respuestas
5. **Revisa la confianza**: Respuestas con múltiples fuentes son más confiables
6. **Usa formatos soportados**: Más de 25 formatos disponibles
7. **Maneja errores específicos**: Cada tipo de error tiene consejos útiles
8. **Aprovecha OCR**: Para procesar imágenes con texto
9. **Usa URLs inteligentemente**: El sistema detecta automáticamente archivos vs páginas web
10. **Valida con fuentes**: Siempre revisa la información de fuentes en las respuestas
11. **Explora estadísticas**: Usa `get_knowledge_base_stats()` para entender el contenido
12. **Aplica filtros estratégicamente**: Para búsquedas más precisas y relevantes
13. **Combina filtros**: Usa múltiples criterios para búsquedas muy específicas
14. **Verifica resultados de filtros**: Confirma que los filtros devuelven información relevante
15. **Optimiza consultas**: Usa filtros para reducir ruido en las respuestas

## 🔧 Información Técnica para Agentes

### **Procesamiento de Documentos**
- **Unstructured Enhanced**: Para la mayoría de formatos con preservación de estructura
- **MarkItDown**: Para páginas web y contenido HTML
- **Fallbacks**: Múltiples estrategias garantizan procesamiento exitoso

### **Metadatos Estructurales**
- **total_elements**: Número total de elementos en el documento
- **titles_count**: Número de títulos identificados
- **tables_count**: Número de tablas extraídas
- **lists_count**: Número de listas identificadas
- **narrative_blocks**: Bloques de texto narrativo

### **Sistema de Filtrado**
- **Filtros de tipo de archivo**: `.pdf`, `.docx`, `.xlsx`, etc.
- **Filtros estructurales**: `min_tables`, `min_titles`
- **Filtros de procesamiento**: `unstructured_enhanced`, `markitdown`
- **Filtros combinados**: Múltiples criterios simultáneos

### **Niveles de Confianza**
- **Alta confianza**: Respuesta basada en 3+ fuentes
- **Confianza media**: Respuesta basada en 2 fuentes
- **Confianza limitada**: Respuesta basada en 1 fuente

### **Métodos de Procesamiento**
- **unstructured_enhanced**: Procesamiento inteligente con preservación de estructura
- **markitdown**: Procesamiento web tradicional
- **langchain_fallback**: Cargadores específicos de LangChain

### **Estadísticas de Base de Conocimientos**
- **Distribución por tipo**: Porcentaje de cada formato de archivo
- **Métricas estructurales**: Totales y promedios de elementos
- **Métodos de procesamiento**: Distribución de estrategias utilizadas
- **Insights automáticos**: Análisis de calidad del contenido 