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
- **Detección de Alucinaciones**: Previene respuestas falsas cuando no hay información
- **Sugerencias Útiles**: Guía cuando no hay información disponible

**Ejemplos de uso**:
```python
# Buscar información específica
ask_rag("¿Cuál es la temperatura de fusión del titanio?")

# Consultar sobre un documento procesado
ask_rag("¿Qué dice el informe trimestral sobre las ventas?")

# Buscar contexto sobre un tema
ask_rag("¿Qué información tenemos sobre inteligencia artificial?")
```

**Respuesta mejorada de `ask_rag`**:
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

**Manejo de errores mejorado**:
```
🤖 **Respuesta:**

❌ **No se encontró información relevante en la base de conocimientos para responder tu pregunta.**

💡 **Sugerencias:**
• Verifica que hayas cargado documentos relacionados con tu pregunta
• Intenta reformular tu pregunta con términos más específicos
• Usa `get_knowledge_base_stats()` para ver qué información está disponible
• Considera cargar más documentos sobre el tema que te interesa

⚠️ **Nota:** El sistema solo puede responder basándose en la información que ha sido previamente cargada en la base de conocimientos.
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

### 7. `get_embedding_cache_stats()` - **NUEVA**
**Cuándo usar**: Para monitorear el rendimiento del cache de embeddings y optimizar el sistema.

**Información proporcionada**:
- **Total de requests** al cache
- **Hits en memoria** (muy rápidos)
- **Hits en disco** (rápidos, persistentes)
- **Misses** (requieren cálculo nuevo)
- **Tasas de éxito** (porcentajes)
- **Tamaño del cache** en memoria
- **Ubicación** del cache en disco

**Ejemplos de uso**:
```python
# Verificar rendimiento del cache
get_embedding_cache_stats()

# Monitorear antes y después de procesar documentos
stats_before = get_embedding_cache_stats()
learn_document("documento.pdf")
stats_after = get_embedding_cache_stats()
```

**Respuesta de `get_embedding_cache_stats`**:
```
📊 **Estadísticas del Cache de Embeddings**

🔄 **Total de requests:** 150
⚡ **Memory hits:** 45 (30.0%)
💾 **Disk hits:** 85 (56.7%)
❌ **Misses:** 20 (13.3%)
📈 **Overall hit rate:** 86.7%

💾 **Cache en memoria:** 45 embeddings
📁 **Cache en disco:** 130 embeddings
📂 **Ubicación:** ./embedding_cache/

🚀 **Rendimiento:** Cache funcionando de manera óptima
```

### 8. `clear_embedding_cache_tool()` - **NUEVA**
**Cuándo usar**: Para limpiar el cache de embeddings cuando sea necesario.

**Opciones de limpieza**:
- **Limpieza completa**: Elimina cache en memoria y disco
- **Liberación de recursos**: Útil cuando hay problemas de memoria
- **Reinicio limpio**: Para empezar desde cero

**Ejemplos de uso**:
```python
# Limpiar cache cuando hay problemas
clear_embedding_cache_tool()

# Limpiar antes de procesar muchos documentos nuevos
clear_embedding_cache_tool()
learn_document("documento1.pdf")
learn_document("documento2.pdf")
```

**Respuesta de `clear_embedding_cache_tool`**:
```
🧹 **Cache de Embeddings Limpiado**

✅ **Acciones realizadas:**
   • Cache en memoria limpiado
   • Cache en disco limpiado
   • Estadísticas reiniciadas

📊 **Estado actual:**
   • Memory hits: 0
   • Disk hits: 0
   • Misses: 0
   • Total requests: 0

💡 **Nota:** El cache se reconstruirá automáticamente con el uso
```

### 9. `optimize_vector_database()` - **NUEVA**
**Cuándo usar**: Para optimizar la base de datos vectorial y mejorar el rendimiento de búsquedas.

**Información proporcionada**:
- **Optimización de índices**: Reorganiza los índices internos
- **Estadísticas antes/después**: Comparación de rendimiento
- **Documentos procesados**: Número de documentos optimizados
- **Beneficios**: Búsquedas más rápidas y precisas

**Ejemplos de uso**:
```python
# Optimizar cuando las búsquedas son lentas
optimize_vector_database()

# Optimizar después de añadir muchos documentos
learn_document("documento1.pdf")
learn_document("documento2.pdf")
optimize_vector_database()
```

**Respuesta de `optimize_vector_database`**:
```
✅ **Base de datos vectorial optimizada exitosamente**

📊 **Estadísticas antes de la optimización:**
   • Documentos totales: 8,934

📊 **Estadísticas después de la optimización:**
   • Documentos totales: 8,934

🚀 **Beneficios:**
   • Búsquedas más rápidas
   • Mejor precisión en resultados
   • Índices optimizados
```

### 10. `get_vector_database_stats()` - **NUEVA**
**Cuándo usar**: Para obtener estadísticas detalladas de la base de datos vectorial.

**Información proporcionada**:
- **Total de documentos** almacenados
- **Distribución por tipo de archivo** (PDF, DOCX, etc.)
- **Métodos de procesamiento** utilizados
- **Perfil recomendado** basado en el tamaño
- **Dimensión de embeddings**

**Ejemplos de uso**:
```python
# Verificar el estado de la base de datos
get_vector_database_stats()

# Analizar distribución de documentos
stats = get_vector_database_stats()
# Luego usar ask_rag_filtered con filtros apropiados
```

**Respuesta de `get_vector_database_stats`**:
```
📊 **Estadísticas de la Base de Datos Vectorial**

📚 **Información General:**
   • Total de documentos: 8,934
   • Nombre de colección: mcp_rag_collection
   • Dimensión de embeddings: 768

📄 **Distribución por tipo de archivo:**
   • .pdf: 5,093 documentos
   • .xlsx: 2,642 documentos
   • .docx: 396 documentos
   • .txt: 502 documentos

🔧 **Métodos de procesamiento:**
   • unstructured_enhanced: 8,500 documentos
   • markitdown: 434 documentos

🎯 **Perfil recomendado:** medium
```

### 11. `reindex_vector_database(profile)` - **NUEVA**
**Cuándo usar**: Para reindexar la base de datos con una configuración optimizada.

**Parámetros**:
- **`profile`**: Perfil de configuración ('small', 'medium', 'large', 'auto')

**Ejemplos de uso**:
```python
# Reindexar con perfil automático
reindex_vector_database('auto')

# Reindexar con perfil específico para bases grandes
reindex_vector_database('large')

# Reindexar cuando hay problemas de rendimiento
reindex_vector_database('medium')
```

**Respuesta de `reindex_vector_database`**:
```
✅ **Base de datos vectorial reindexada exitosamente**

📊 **Información del proceso:**
   • Perfil aplicado: medium
   • Documentos procesados: 8,934

🚀 **Beneficios del reindexado:**
   • Índices optimizados para el tamaño actual
   • Búsquedas más rápidas y precisas
   • Mejor uso de memoria
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
10. **Monitorear el cache** usando `get_embedding_cache_stats()` para optimizar rendimiento
11. **Limpiar cache** cuando sea necesario usando `clear_embedding_cache_tool()`
12. **Aprovechar la persistencia** del cache en disco entre sesiones
13. **Optimizar la base vectorial** usando `optimize_vector_database()` cuando las búsquedas sean lentas
14. **Monitorear estadísticas** de la base vectorial con `get_vector_database_stats()`
15. **Reindexar cuando sea necesario** usando `reindex_vector_database()` para mejorar rendimiento

### Manejo de Errores Mejorado
- **Archivo no encontrado**: Verificar la ruta del archivo
- **Formato no soportado**: El sistema soporta más de 25 formatos
- **Error de OCR**: Instalar Tesseract para procesar imágenes con texto
- **Error de Unstructured**: Verificar instalación: `pip install 'unstructured[local-inference,all-docs]'`
- **Sin información**: Asegurarse de que se haya cargado información relevante
- **Filtros sin resultados**: Usar filtros menos restrictivos o verificar estadísticas
- **Error en filtros**: Verificar formato de parámetros de filtrado
- **Cache corrupto**: Usar `clear_embedding_cache_tool()` para limpiar
- **Baja tasa de aciertos**: Revisar patrones de consulta y optimizar

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

## Herramientas Disponibles

### 🔍 **Búsqueda y Consulta**
- `search_documents`: Busca documentos en la base de conocimiento
- `ask_rag`: Realiza consultas RAG con el modelo de lenguaje
- `ask_rag_filtered`: Consultas RAG con filtros de metadatos

### 📊 **Gestión de Base de Datos**
- `get_document_statistics`: Obtiene estadísticas detalladas de la base
- `get_vector_store_stats`: Estadísticas básicas de la base vectorial
- `get_vector_store_stats_advanced`: **NUEVO** - Estadísticas avanzadas con información de escalabilidad

### ⚡ **Optimización y Rendimiento**
- `optimize_vector_store`: Optimiza la base vectorial (detecta automáticamente si es base grande)
- `reindex_vector_store`: Reindexa la base con nuevo perfil
- `optimize_vector_store_large`: **NUEVO** - Optimización incremental para bases muy grandes
- `reindex_vector_store_large`: **NUEVO** - Reindexado incremental para bases muy grandes

### 🧠 **Cache de Embeddings**
- `get_cache_stats`: Estadísticas del cache de embeddings
- `print_cache_stats`: Imprime estadísticas del cache
- `clear_embedding_cache`: Limpia el cache de embeddings

### 🔧 **Configuración y Perfiles**
- `get_optimal_vector_store_profile`: Detecta el perfil óptimo automáticamente
- `get_vector_store`: Obtiene la base vectorial con perfil optimizado

## Características de Escalabilidad

### **Detección Automática de Tamaño**
El sistema detecta automáticamente si la base de datos es "grande" (>10,000 documentos) y aplica optimizaciones especiales:

- **Bases pequeñas/medianas** (<10,000 docs): Optimización estándar
- **Bases grandes** (>10,000 docs): Optimización incremental con checkpoints

### **Optimización Incremental para Bases Grandes**
- **Procesamiento por lotes**: Batches de 2,000 documentos
- **Checkpoints automáticos**: Cada 5,000 documentos
- **Monitoreo de memoria**: Control de uso de RAM
- **Recuperación automática**: Reanudación desde checkpoint en caso de error
- **Almacenamiento temporal**: Datos guardados en disco durante proceso

### **Estimaciones de Rendimiento**
El sistema proporciona estimaciones basadas en el tamaño:
- **<1,000 docs**: 1-5 minutos
- **1,000-10,000 docs**: 5-15 minutos  
- **10,000-50,000 docs**: 15-45 minutos
- **50,000-100,000 docs**: 45-90 minutos
- **>100,000 docs**: 2-4 horas

## Mejores Prácticas

### **Para Bases Pequeñas/Medianas**
1. Usar optimización estándar
2. Cache de embeddings mejora rendimiento
3. Reindexado ocasional para mantenimiento

### **Para Bases Grandes**
1. Optimización incremental automática
2. Monitorear uso de memoria
3. Checkpoints frecuentes
4. Considerar particionamiento de datos
5. Usar almacenamiento SSD

### **Configuraciones Recomendadas**
- **Umbral de base grande**: 10,000 documentos
- **Batch incremental**: 2,000 documentos
- **Checkpoint cada**: 5,000 documentos
- **Límite de memoria**: 2,048 MB

## Manejo de Errores Mejorado

### **Detección de Falta de Información**
- El sistema detecta cuando no hay información relevante
- Proporciona mensajes claros al usuario
- Evita respuestas falsas o inventadas

### **Recuperación de Errores**
- Errores de batch: Reducción automática del tamaño
- Errores de memoria: Limpieza automática y pausa
- Errores de proceso: Recuperación desde checkpoint

## Ejemplos de Uso

### **Consulta Simple**
```python
# Consulta básica
result = ask_rag("¿Qué es la inteligencia artificial?")
```

### **Consulta con Filtros**
```python
# Consulta filtrada por tipo de archivo
filter_metadata = {"file_type": ".pdf"}
result = ask_rag_filtered("Explica machine learning", filter_metadata)
```

### **Optimización Automática**
```python
# El sistema detecta automáticamente el tamaño y usa el método apropiado
result = optimize_vector_store()
```

### **Estadísticas Avanzadas**
```python
# Obtener información completa de escalabilidad
stats = get_vector_store_stats_advanced()
print(f"Es base grande: {stats['is_large_database']}")
print(f"Tiempo estimado: {stats['estimated_optimization_time']}")
```

## Notas Importantes

1. **Detección Automática**: Las funciones detectan automáticamente si es necesario usar optimización incremental
2. **Monitoreo de Memoria**: Requiere `psutil` instalado para funcionar completamente
3. **Checkpoints**: Se guardan automáticamente en `./temp_reindex/`
4. **Recuperación**: Los errores en bases grandes son recuperables desde el último checkpoint
5. **Rendimiento**: Las estimaciones son aproximadas y pueden variar según el hardware

## Troubleshooting

### **Error de Memoria**
- El sistema reduce automáticamente el tamaño de batch
- Limpia memoria y continúa el proceso
- Considerar aumentar RAM si es frecuente

### **Error de Batch**
- Reducción automática del tamaño de batch
- Procesamiento en sub-batches más pequeños
- Logs detallados para debugging

### **Error de Checkpoint**
- Verificar espacio en disco
- Limpiar directorio temporal si es necesario
- Reanudar desde el último checkpoint válido 