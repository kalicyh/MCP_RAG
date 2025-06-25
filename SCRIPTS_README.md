# Scripts de Bulk Ingest GUI

Esta carpeta contiene scripts organizados para facilitar la instalación y ejecución de la aplicación Bulk Ingest GUI.

## 📁 Estructura de Scripts

### **Scripts Principales**

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `start.bat` | **Script principal** - Guía interactiva | **Siempre usar este primero** |
| `install_requirements.bat` | Instala todas las dependencias | Primera vez o problemas |
| `run_gui.bat` | Ejecuta la aplicación | Después de instalar |

### **Scripts de Diagnóstico**

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `check_system.bat` | Verifica Python, GPU, CUDA | Problemas de instalación |
| `diagnose_venv.bat` | Diagnostica el entorno virtual | Problemas con .venv |
| `force_clean_venv.bat` | Limpia forzadamente el entorno | Entorno corrupto |

### **Scripts Especializados**

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `install_pytorch.bat` | Instala PyTorch específicamente | Solo problemas con PyTorch |

## 🚀 Guía de Uso

### **Primera Vez (Recomendado)**

1. **Ejecuta el script principal:**
   ```bash
   start.bat
   ```

2. **Selecciona "1" para instalar dependencias**

3. **Espera a que termine la instalación**

4. **La aplicación se iniciará automáticamente**

### **Uso Diario**

1. **Ejecuta el script principal:**
   ```bash
   start.bat
   ```

2. **Selecciona "1" para ejecutar la aplicación**

### **Si Hay Problemas**

#### **Problema: Entorno virtual corrupto**
```bash
force_clean_venv.bat
```

#### **Problema: Dependencias faltantes**
```bash
install_requirements.bat
```

#### **Problema: PyTorch no funciona**
```bash
install_pytorch.bat
```

#### **Problema: No sé qué pasa**
```bash
check_system.bat
```

## 🔧 Separación de Responsabilidades

### **install_requirements.bat**
- ✅ Verifica el sistema (Python, GPU)
- ✅ Limpia entorno virtual corrupto
- ✅ Crea nuevo entorno virtual
- ✅ Instala PyTorch (CPU o CUDA según hardware)
- ✅ Instala todas las dependencias
- ✅ Verifica la instalación

### **run_gui.bat**
- ✅ Verifica que el entorno virtual existe
- ✅ Activa el entorno virtual
- ✅ Ejecuta la aplicación
- ✅ Maneja errores de ejecución

### **start.bat**
- ✅ Detecta si necesita instalación
- ✅ Guía al usuario con opciones claras
- ✅ Coordina los otros scripts
- ✅ Maneja casos de primera vez vs uso diario

## 📋 Flujo de Trabajo

```
start.bat
    ↓
¿Necesita instalación?
    ↓
SÍ → install_requirements.bat → run_gui.bat
    ↓
NO → run_gui.bat
```

## 🛠️ Ventajas de Esta Estructura

### **Para Usuarios**
- ✅ **Simplicidad**: Solo ejecutar `start.bat`
- ✅ **Intuitivo**: Menús claros y opciones explicadas
- ✅ **Robusto**: Maneja errores automáticamente
- ✅ **Flexible**: Opciones para diferentes situaciones

### **Para Desarrolladores**
- ✅ **Mantenible**: Cada script tiene una responsabilidad
- ✅ **Debuggeable**: Fácil identificar dónde falla
- ✅ **Extensible**: Fácil agregar nuevas funcionalidades
- ✅ **Reutilizable**: Scripts pueden usarse independientemente

## 🚨 Solución de Problemas

### **Error: "Entorno virtual no encontrado"**
```bash
start.bat
# Selecciona "1" para instalar dependencias
```

### **Error: "No se pudo activar el entorno virtual"**
```bash
force_clean_venv.bat
start.bat
```

### **Error: "PyTorch no encontrado"**
```bash
install_pytorch.bat
```

### **Error: "Python no encontrado"**
1. Instala Python desde https://www.python.org/downloads/
2. Marca "Add Python to PATH" durante la instalación
3. Reinicia la terminal
4. Ejecuta `start.bat`

## 📝 Notas Importantes

- **Siempre usa `start.bat`** como punto de entrada
- **No ejecutes scripts directamente** a menos que sepas lo que haces
- **Si algo falla**, usa los scripts de diagnóstico
- **Para reinstalar**, usa la opción "Reinstalar dependencias" en `start.bat`

## 🔄 Actualizaciones

Para actualizar el sistema:
1. Ejecuta `start.bat`
2. Selecciona "Reinstalar dependencias"
3. Esto limpiará y reinstalará todo automáticamente 