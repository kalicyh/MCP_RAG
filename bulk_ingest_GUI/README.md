# Bulk Ingest GUI - Sistema RAG Modular

## 🚀 Descripción

Bulk Ingest GUI es una aplicación de escritorio moderna para procesar y almacenar documentos en un sistema RAG (Retrieval-Augmented Generation) modular. Utiliza `rag_core.py` como núcleo del sistema, proporcionando todas las funcionalidades avanzadas de procesamiento, chunking semántico, cache de embeddings y almacenamiento vectorial.

## 🏗️ Arquitectura

La aplicación sigue el patrón **MVC + Services** con una estructura modular:

```
bulk_ingest_GUI/
├── controllers/          # Controladores (lógica de aplicación)
│   └── main_controller.py
├── models/              # Modelos de datos
│   └── document_model.py
├── services/            # Servicios (lógica de negocio)
│   ├── configuration_service.py
│   └── document_service.py
├── views/               # Vistas (interfaz gráfica)
│   └── main_view.py
├── widgets/             # Widgets personalizados
│   ├── document_preview_widget.py
│   └── statistics_widget.py
├── utils/               # Utilidades y constantes
│   ├── constants.py
│   └── exceptions.py
├── main.py              # Punto de entrada principal
└── run_gui.py           # Script de lanzamiento
```

## 🔧 Características

### ✅ Funcionalidades Principales
- **Procesamiento de documentos**: Soporta múltiples formatos (PDF, DOCX, TXT, etc.)
- **Chunking semántico avanzado**: Usa elementos estructurales para mejor calidad
- **Cache de embeddings**: Optimización de rendimiento con cache en memoria y disco
- **Almacenamiento vectorial**: Integración completa con ChromaDB
- **Interfaz moderna**: GUI intuitiva con Tkinter

### ✅ Funcionalidades Avanzadas
- **Previsualización de documentos**: Widget para ver contenido antes de almacenar
- **Estadísticas detalladas**: Información sobre procesamiento, cache y base de datos
- **Filtros y búsqueda**: Encuentra documentos rápidamente
- **Exportar/Importar**: Guarda y carga listas de documentos
- **Procesamiento por lotes**: Manejo eficiente de grandes volúmenes

## 🚀 Instalación y Uso

### Requisitos
- Python 3.8+
- Dependencias de `rag_core.py`
- Tkinter (incluido con Python)

### Instalación
```bash
# Clonar el repositorio
git clone <repository-url>
cd MCP_RAG

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la GUI
python bulk_ingest_GUI/run_gui.py
```

### Uso Básico
1. **Seleccionar directorio**: Haz clic en "Examinar" y selecciona la carpeta con documentos
2. **Procesar**: Haz clic en "Procesar" para extraer contenido de los documentos
3. **Revisar**: Usa los filtros y previsualización para revisar los documentos
4. **Seleccionar**: Marca los documentos que quieres almacenar
5. **Almacenar**: Haz clic en "Almacenar seleccionados" para guardar en la base vectorial

## 🔄 Flujo de Datos

```
1. Usuario selecciona directorio
   ↓
2. MainView llama a MainController
   ↓
3. MainController usa DocumentService
   ↓
4. DocumentService llama a rag_core.py
   ↓
5. rag_core.py procesa con Unstructured
   ↓
6. DocumentService almacena con ChromaDB
   ↓
7. UI se actualiza con resultados
```

## 🎯 Integración con rag_core.py

La aplicación utiliza `rag_core.py` como núcleo, aprovechando todas sus optimizaciones:

- **`load_document_with_elements()`**: Carga documentos con elementos estructurales
- **`add_text_to_knowledge_base_enhanced()`**: Almacenamiento con chunking semántico
- **`get_vector_store()`**: Configuración optimizada de ChromaDB
- **`get_cache_stats()`**: Estadísticas del cache de embeddings
- **`clear_embedding_cache()`**: Gestión del cache

## 📊 Widgets Disponibles

### DocumentPreviewWidget
- Muestra contenido de documentos con formato
- Estadísticas de tamaño y palabras
- Botón para copiar contenido
- Scroll automático para documentos largos

### StatisticsWidget
- **Pestaña Procesamiento**: Estadísticas de documentos procesados
- **Pestaña Cache**: Información del cache de embeddings
- **Pestaña Base de Datos**: Estado de la base vectorial
- Botones para actualizar y optimizar

## 🔧 Configuración

La aplicación usa `ConfigurationService` para gestionar configuraciones:

```python
# Ejemplo de configuración
config = {
    'ui.window_size': '1200x800',
    'processing.max_preview_length': 2000,
    'processing.batch_size': 10,
    'storage.use_semantic_chunking': True
}
```

## 🐛 Solución de Problemas

### Error de importación
```bash
# Asegúrate de estar en el directorio correcto
cd MCP_RAG
python bulk_ingest_GUI/run_gui.py
```

### Error de dependencias
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

### Error de permisos
```bash
# En Windows, ejecutar como administrador si es necesario
# En Linux/Mac, verificar permisos de escritura
```

## 🚀 Próximas Mejoras

- [ ] Soporte para más formatos de archivo
- [ ] Interfaz de consulta RAG integrada
- [ ] Configuración avanzada de chunking
- [ ] Exportación a diferentes formatos
- [ ] Integración con APIs externas
- [ ] Modo oscuro/claro
- [ ] Atajos de teclado
- [ ] Logs detallados en archivo

## 📝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la misma licencia que el proyecto principal.

## 🤝 Soporte

Para soporte y preguntas:
- Revisa la documentación de `rag_core.py`
- Abre un issue en el repositorio
- Consulta los logs de la aplicación para más detalles 