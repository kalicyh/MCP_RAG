# 📁 Carpeta `tests/` - Pruebas Unitarias del Servidor MCP

## 🎯 **¿Para qué sirve esta carpeta?**

La carpeta `tests/` es una **convención estándar** en proyectos Python para organizar las **pruebas unitarias y de integración**. Su propósito es:

### 🔍 **Objetivos principales:**

1. **Pruebas Unitarias**: Probar funciones individuales de forma aislada
2. **Pruebas de Integración**: Verificar que los módulos trabajen juntos correctamente
3. **Pruebas de Regresión**: Asegurar que cambios no rompan funcionalidad existente
4. **Documentación Viva**: Las pruebas sirven como documentación del comportamiento esperado

### 🔄 **Diferencias con otros scripts de prueba:**

| Tipo de Prueba | Archivo | Propósito |
|----------------|---------|-----------|
| **Validación de Sistema** | `test_mcp_server_validation.py` | Pruebas de **sistema completo** y **validación de arquitectura** |
| **Pruebas Unitarias** | `tests/` | Pruebas **unitarias específicas** y **casos de uso detallados** |

## 📋 **Contenido de la carpeta:**

```
tests/
├── __init__.py                    # Hace de tests un paquete Python
├── test_document_tools.py         # Pruebas para herramientas de documentos
├── test_search_tools.py           # Pruebas para herramientas de búsqueda
├── test_utility_tools.py          # Pruebas para herramientas de utilidad
├── run_all_tests.py              # Script para ejecutar todas las pruebas
└── README.md                     # Este archivo
```

## 🧪 **Archivos de prueba disponibles:**

### 1. **`test_document_tools.py`**
Prueba las funciones de procesamiento de documentos:
- ✅ `learn_text()` - Añadir texto manual
- ✅ `learn_document()` - Procesar archivos
- ✅ `learn_from_url()` - Procesar URLs
- ✅ Manejo de errores y casos edge
- ✅ Configuración de estado RAG

### 2. **`test_search_tools.py`**
Prueba las funciones de búsqueda y consulta:
- ✅ `ask_rag()` - Preguntas básicas
- ✅ `ask_rag_filtered()` - Preguntas con filtros
- ✅ Configuración de retriever y QA chain
- ✅ Manejo de errores de vector store
- ✅ Documentos fuente en respuestas

### 3. **`test_utility_tools.py`**
Prueba las funciones de mantenimiento y utilidad:
- ✅ `get_knowledge_base_stats()` - Estadísticas de la base
- ✅ `get_embedding_cache_stats()` - Estadísticas del cache
- ✅ `clear_embedding_cache_tool()` - Limpiar cache
- ✅ `optimize_vector_database()` - Optimizar BD
- ✅ `get_vector_database_stats()` - Estadísticas de BD
- ✅ `reindex_vector_database()` - Reindexar BD

## 🚀 **Cómo ejecutar las pruebas:**

### **Opción 1: Ejecutar todas las pruebas**
```bash
# Desde la carpeta mcp_server_organized
python tests/run_all_tests.py
```

### **Opción 2: Ejecutar pruebas específicas**
```bash
# Pruebas de herramientas de documentos
python -m unittest tests.test_document_tools

# Pruebas de herramientas de búsqueda
python -m unittest tests.test_search_tools

# Pruebas de herramientas de utilidad
python -m unittest tests.test_utility_tools
```

### **Opción 3: Ejecutar con más detalle**
```bash
# Con verbosidad aumentada
python -m unittest tests.test_document_tools -v

# Ejecutar una clase específica
python -m unittest tests.test_document_tools.TestDocumentTools -v

# Ejecutar un método específico
python -m unittest tests.test_document_tools.TestDocumentTools.test_learn_text_basic -v
```

## 📊 **Tipos de pruebas incluidas:**

### **Pruebas Básicas**
- ✅ Funcionamiento normal de las funciones
- ✅ Parámetros válidos
- ✅ Respuestas esperadas

### **Pruebas de Error**
- ✅ Parámetros inválidos
- ✅ Estado RAG no inicializado
- ✅ Fallos de vector store
- ✅ Errores de configuración

### **Pruebas de Configuración**
- ✅ Configuración de estado RAG
- ✅ Persistencia de configuración
- ✅ Compartir estado entre módulos

### **Pruebas de Integración**
- ✅ Flujos de trabajo completos
- ✅ Interacción entre módulos
- ✅ Datos realistas

### **Pruebas de Casos Edge**
- ✅ Vector store vacío
- ✅ Vector store grande
- ✅ Parámetros extremos

## 🔧 **Características técnicas:**

### **Mocks y Simulación**
- 🔄 Uso de `unittest.mock` para simular dependencias
- 🔄 Vector store simulado para pruebas aisladas
- 🔄 QA chain simulada para respuestas controladas
- 🔄 Cache de embeddings simulado

### **Configuración Automática**
- 🔄 `setUp()` automático para cada prueba
- 🔄 Limpieza automática de archivos temporales
- 🔄 Restauración de estado después de cada prueba

### **Reportes Detallados**
- 📊 Estadísticas por módulo
- 📊 Tasa de éxito general
- 📊 Identificación de problemas específicos
- 📊 Guardado automático de reportes

## 📈 **Beneficios de las pruebas unitarias:**

### **Para el Desarrollo**
- 🚀 **Detección temprana de errores**
- 🚀 **Refactoring seguro**
- 🚀 **Documentación del comportamiento**
- 🚀 **Confianza en el código**

### **Para el Mantenimiento**
- 🔧 **Identificación rápida de regresiones**
- 🔧 **Validación de cambios**
- 🔧 **Base sólida para mejoras**
- 🔧 **Reducción de bugs en producción**

### **Para el Equipo**
- 👥 **Entendimiento compartido del código**
- 👥 **Onboarding más fácil**
- 👥 **Estándares de calidad**
- 👥 **Colaboración mejorada**

## 🎯 **Cuándo usar estas pruebas:**

### **Durante el Desarrollo**
- ✅ Antes de hacer commit
- ✅ Al añadir nuevas funcionalidades
- ✅ Al refactorizar código existente
- ✅ Al corregir bugs

### **En CI/CD**
- ✅ En cada pull request
- ✅ Antes de cada release
- ✅ En builds automatizados
- ✅ Para validación de calidad

### **Para Validación**
- ✅ Verificar que el código funciona
- ✅ Asegurar que no se rompió nada
- ✅ Validar casos edge
- ✅ Confirmar comportamiento esperado

## 💡 **Próximos pasos:**

1. **Ejecutar las pruebas** para verificar el estado actual
2. **Revisar pruebas fallidas** y corregir problemas
3. **Añadir nuevas pruebas** para funcionalidades adicionales
4. **Integrar en CI/CD** para automatización
5. **Documentar casos de uso** específicos

## 🔗 **Relación con otros archivos:**

- **`test_mcp_server_validation.py`**: Pruebas de sistema completo
- **`src/tools/`**: Código fuente que se está probando
- **`server.py`**: Servidor MCP principal
- **`requirements.txt`**: Dependencias necesarias

---

**¡Las pruebas unitarias son la base de un código robusto y mantenible!** 🧪✨ 