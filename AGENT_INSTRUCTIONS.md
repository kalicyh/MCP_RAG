# Instrucciones para Agentes de IA - Sistema RAG Mejorado

## 🎯 Propósito del Sistema

Este sistema RAG (Retrieval-Augmented Generation) **mejorado** permite a los agentes de IA:
- **Almacenar información** de forma persistente con procesamiento inteligente
- **Consultar conocimiento** previamente guardado con metadatos estructurales
- **Rastrear fuentes** de información con detalles completos
- **Procesar documentos** automáticamente con más de 25 formatos
- **Preservar estructura** semántica de documentos (títulos, tablas, listas)
- **Eliminar ruido** automáticamente (cabeceras, pies de página, contenido irrelevante)

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

### Paso 2: Consultar Información
```python
# Hacer preguntas sobre la información cargada
respuesta = ask_rag("¿Cuál es la información importante?")
```

### Paso 3: Verificar Fuentes Mejoradas
- Las respuestas incluyen metadatos estructurales detallados
- Información sobre método de procesamiento
- Nivel de confianza de la respuesta

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

### Mejores Prácticas
1. **Usar nombres descriptivos** para las fuentes
2. **Verificar las rutas** de archivos antes de procesarlos
3. **Revisar las fuentes** en las respuestas para validar información
4. **Procesar documentos** antes de hacer preguntas sobre ellos
5. **Aprovechar metadatos estructurales** para entender mejor el contenido
6. **Usar chunking semántico** para documentos con estructura compleja

### Manejo de Errores Mejorado
- **Archivo no encontrado**: Verificar la ruta del archivo
- **Formato no soportado**: El sistema soporta más de 25 formatos
- **Error de OCR**: Instalar Tesseract para procesar imágenes con texto
- **Error de Unstructured**: Verificar instalación: `pip install 'unstructured[local-inference,all-docs]'`
- **Sin información**: Asegurarse de que se haya cargado información relevante

## 📝 Ejemplos de Casos de Uso Mejorados

### Caso 1: Investigación Académica con Documentos Complejos
```python
# 1. Cargar papers de investigación con estructura compleja
learn_document("paper_ai_ethics.pdf")  # Preserva títulos, tablas, referencias
learn_document("survey_machine_learning.docx")  # Mantiene formato y estructura

# 2. Consultar información específica con contexto estructural
ask_rag("¿Cuáles son los principales desafíos éticos de la IA según los papers?")
```

### Caso 2: Análisis de Datos con Hojas de Cálculo
```python
# 1. Cargar datos y reportes con formato preservado
learn_document("datos_ventas.xlsx")  # Procesa tablas y datos estructurados
learn_document("reporte_analisis.pdf")  # Mantiene gráficos y tablas

# 2. Hacer consultas específicas sobre datos estructurados
ask_rag("¿Cuáles fueron las ventas del Q3 según la tabla de datos?")
```

### Caso 3: Asistente Personal con Documentos Escaneados
```python
# 1. Almacenar información personal y documentos escaneados
learn_text("Mi dirección es 123 Calle Principal", "personal_info")
learn_document("documento_identidad_escaneado.png")  # OCR automático

# 2. Consultar cuando sea necesario
ask_rag("¿Cuál es mi información de contacto?")
```

### Caso 4: Investigación Web con Descarga de Archivos
```python
# 1. Procesar contenido web y descargar documentos
learn_from_url("https://example.com/articulo")  # Página web
learn_from_url("https://example.com/informe.pdf")  # Descarga y procesa PDF

# 2. Consultar información combinada
ask_rag("¿Qué información tenemos sobre el tema desde las fuentes web?")
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

### **Niveles de Confianza**
- **Alta confianza**: Respuesta basada en 3+ fuentes
- **Confianza media**: Respuesta basada en 2 fuentes
- **Confianza limitada**: Respuesta basada en 1 fuente

### **Métodos de Procesamiento**
- **unstructured_enhanced**: Procesamiento inteligente con preservación de estructura
- **markitdown**: Procesamiento web tradicional
- **langchain_fallback**: Cargadores específicos de LangChain 