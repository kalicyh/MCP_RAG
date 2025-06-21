# Instrucciones para Agentes de IA - Sistema RAG

## 🎯 Propósito del Sistema

Este sistema RAG (Retrieval-Augmented Generation) permite a los agentes de IA:
- **Almacenar información** de forma persistente
- **Consultar conocimiento** previamente guardado
- **Rastrear fuentes** de información
- **Procesar documentos** automáticamente

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

### 2. `learn_document(file_path)`
**Cuándo usar**: Para procesar y almacenar contenido de archivos.

**Ejemplos de uso**:
```python
# Procesar un informe
learn_document("C:/Documents/informe_trimestral.pdf")

# Añadir un manual técnico
learn_document("D:/Manuals/manual_usuario.docx")

# Importar datos de una hoja de cálculo
learn_document("E:/Data/datos_ventas.xlsx")
```

### 3. `ask_rag(query)`
**Cuándo usar**: Para consultar información previamente almacenada.

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

# Opción B: Documento
learn_document("ruta/al/documento.pdf")
```

### Paso 2: Consultar Información
```python
# Hacer preguntas sobre la información cargada
respuesta = ask_rag("¿Cuál es la información importante?")
```

### Paso 3: Verificar Fuentes
- Las respuestas incluyen las fuentes utilizadas
- Siempre verificar la credibilidad de las fuentes
- Usar múltiples fuentes cuando sea posible

## ⚠️ Consideraciones Importantes

### Limitaciones
- **Alcance**: Solo puede acceder a información previamente almacenada
- **Formato**: Los documentos se convierten automáticamente a Markdown
- **Tamaño**: Los archivos muy grandes pueden tardar en procesarse

### Mejores Prácticas
1. **Usar nombres descriptivos** para las fuentes
2. **Verificar las rutas** de archivos antes de procesarlos
3. **Revisar las fuentes** en las respuestas
4. **Procesar documentos** antes de hacer preguntas sobre ellos

### Manejo de Errores
- **Archivo no encontrado**: Verificar la ruta del archivo
- **Formato no soportado**: Usar solo formatos compatibles
- **Sin información**: Asegurarse de que se haya cargado información relevante

## 📝 Ejemplos de Casos de Uso

### Caso 1: Investigación Académica
```python
# 1. Cargar papers de investigación
learn_document("paper_ai_ethics.pdf")
learn_document("survey_machine_learning.docx")

# 2. Consultar información específica
ask_rag("¿Cuáles son los principales desafíos éticos de la IA?")
```

### Caso 2: Análisis de Datos
```python
# 1. Cargar datos y reportes
learn_document("datos_ventas.xlsx")
learn_document("reporte_analisis.pdf")

# 2. Hacer consultas específicas
ask_rag("¿Cuáles fueron las ventas del Q3?")
```

### Caso 3: Asistente Personal
```python
# 1. Almacenar información personal
learn_text("Mi dirección es 123 Calle Principal", "personal_info")
learn_text("Mi número de teléfono es 555-0123", "personal_info")

# 2. Consultar cuando sea necesario
ask_rag("¿Cuál es mi dirección?")
```

## 🎯 Consejos para Agentes

1. **Sé específico** en las consultas para obtener mejores resultados
2. **Usa fuentes descriptivas** para facilitar el rastreo
3. **Verifica siempre** las fuentes en las respuestas
4. **Procesa documentos** antes de consultar sobre ellos
5. **Maneja errores** de forma elegante y proporciona sugerencias útiles 