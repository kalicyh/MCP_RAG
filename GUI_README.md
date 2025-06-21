# 📚 Bulk Ingest GUI - Interfaz Visual

## ¿Qué es esta aplicación?

Esta es una **interfaz gráfica amigable** para el proceso de **bulk_ingest** que te permite procesar múltiples documentos de manera visual, sin necesidad de usar la línea de comandos.

## 🚀 Características Principales

### ✨ Interfaz Intuitiva
- **Selección visual de carpetas** con explorador de archivos
- **Barra de progreso** en tiempo real
- **Estadísticas visuales** del procesamiento
- **Registro de actividad** con timestamps

### 📊 Funcionalidades
- **Procesamiento masivo** de documentos
- **Conversión automática** a Markdown
- **Guardado de copias** (opcional)
- **Manejo de errores** amigable
- **Pausa/Reanudación** del proceso

### 📄 Formatos Soportados
- PDF (.pdf)
- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- Texto (.txt)
- HTML (.html)
- CSV (.csv)
- JSON (.json)
- XML (.xml)

## 🛠️ Instalación y Uso

### Requisitos Previos
1. Tener Python instalado
2. Tener todas las dependencias del proyecto instaladas
3. Tener configurado el modelo de embeddings

### Ejecutar la Aplicación

#### Opción 1: Usando el archivo batch (Windows)
```bash
# Simplemente haz doble clic en:
run_gui.bat
```

#### Opción 2: Desde la línea de comandos
```bash
python bulk_ingest_gui.py
```

## 📖 Guía de Uso

### Paso 1: Seleccionar Directorio
1. Haz clic en **"📂 Explorar..."**
2. Navega hasta la carpeta que contiene tus documentos
3. Selecciona la carpeta y haz clic en **"Seleccionar carpeta"**

### Paso 2: Configurar Opciones
- ✅ **Guardar copias Markdown**: Marca esta opción si quieres guardar copias de los documentos convertidos
- 📄 **Extensiones soportadas**: Se muestran automáticamente

### Paso 3: Iniciar Procesamiento
1. Haz clic en **"🚀 Iniciar Procesamiento"**
2. Observa el progreso en tiempo real:
   - Barra de progreso
   - Archivo actual siendo procesado
   - Estadísticas actualizadas
   - Logs detallados

### Paso 4: Monitorear el Proceso
- **📊 Progreso**: Ve el avance en tiempo real
- **📝 Registro**: Observa todos los detalles del procesamiento
- **📈 Estadísticas**: Revisa los números finales

### Paso 5: Resultados
- Los documentos se añaden automáticamente a tu base de conocimiento
- Las copias Markdown se guardan en `./converted_docs/` (si está habilitado)
- Se muestra un resumen final con estadísticas

## 🎯 Ventajas sobre la Línea de Comandos

### ✅ Facilidad de Uso
- **No necesitas recordar comandos**
- **Interfaz visual intuitiva**
- **Selección de carpetas con explorador**

### 📊 Mejor Control
- **Progreso visual en tiempo real**
- **Puedes detener el proceso en cualquier momento**
- **Estadísticas detalladas**

### 🛡️ Mejor Manejo de Errores
- **Mensajes de error claros**
- **Continuación automática** si un archivo falla
- **Logs detallados** para debugging

### ⚙️ Configuración Fácil
- **Opciones configurables** con checkboxes
- **Información clara** sobre formatos soportados
- **Configuración persistente** durante la sesión

## 🔧 Solución de Problemas

### Error: "No se pudo importar tkinter"
```bash
# En Ubuntu/Debian:
sudo apt-get install python3-tk

# En CentOS/RHEL:
sudo yum install tkinter

# En Windows: tkinter viene incluido con Python
```

### Error: "Directorio no existe"
- Verifica que la ruta sea correcta
- Asegúrate de que tengas permisos de lectura en esa carpeta

### Error: "No se pudo procesar archivo"
- Revisa que el archivo no esté corrupto
- Verifica que el formato esté soportado
- Revisa los logs para más detalles

### La aplicación se cuelga
- Usa el botón **"⏹️ Detener"** para parar el proceso
- Cierra la aplicación y vuelve a abrirla
- Verifica que no haya otros procesos usando los mismos archivos

## 📁 Estructura de Archivos

```
MCP_RAG/
├── bulk_ingest_gui.py      # Aplicación GUI principal
├── run_gui.bat            # Lanzador para Windows
├── GUI_README.md          # Esta documentación
├── bulk_ingest.py         # Versión de línea de comandos
├── converted_docs/        # Copias Markdown (si está habilitado)
└── rag_mcp_db/           # Base de datos vectorial
```

## 🎓 Conceptos Importantes

### ¿Qué es Bulk Ingest?
Es el proceso de **procesar múltiples documentos** de una vez y añadirlos a tu base de conocimiento para que el sistema RAG pueda responder preguntas sobre ellos.

### ¿Qué hace la conversión a Markdown?
Convierte documentos de diferentes formatos (PDF, Word, etc.) a **texto plano estructurado** que es más fácil de procesar y buscar.

### ¿Por qué guardar copias?
Las copias Markdown te permiten:
- **Verificar** que la conversión fue correcta
- **Revisar** el contenido procesado
- **Tener un respaldo** del contenido original

## 🚀 Próximas Mejoras

- [ ] **Drag & Drop** de archivos
- [ ] **Filtros** por tipo de archivo
- [ ] **Configuración** de opciones avanzadas
- [ ] **Historial** de procesamientos
- [ ] **Exportar** estadísticas
- [ ] **Tema oscuro** opcional

## 💡 Consejos de Uso

1. **Organiza tus documentos** en carpetas por tema o proyecto
2. **Revisa los logs** si algo no funciona como esperabas
3. **Usa el botón de detener** si necesitas pausar el proceso
4. **Guarda copias Markdown** para verificar la conversión
5. **Procesa en lotes pequeños** si tienes muchos archivos grandes

¡Disfruta usando tu nueva interfaz visual para bulk_ingest! 🎉 