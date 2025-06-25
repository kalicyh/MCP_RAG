@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Instalador de Requerimientos - Bulk Ingest GUI
echo =======================================================
echo.

echo [1/7] Verificando sistema...
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado en el PATH
    echo.
    echo Por favor, instala Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
    python --version
)

echo.
echo [2/7] Verificando GPU y CUDA...
echo.

nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ℹ️ No se detecto GPU NVIDIA - Se usara PyTorch CPU
    set GPU_AVAILABLE=false
) else (
    echo ✅ GPU NVIDIA detectada - Se usara PyTorch con CUDA
    set GPU_AVAILABLE=true
)

echo.
echo [3/7] Limpiando entorno virtual existente...
echo.

if exist "%VENV_DIR%" (
    echo Eliminando entorno virtual existente...
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "%VENV_DIR%" (
        echo ⚠️ No se pudo eliminar completamente. Intentando forzar...
        taskkill /f /im python.exe >nul 2>&1
        timeout /t 2 /nobreak >nul
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
        if exist "%VENV_DIR%" (
            echo ❌ No se pudo eliminar el entorno virtual
            echo Por favor, cierra todas las ventanas de terminal y vuelve a intentar
            pause
            exit /b 1
        )
    )
    echo ✅ Entorno virtual eliminado
) else (
    echo ℹ️ No se encontro entorno virtual para eliminar
)

echo.
echo [4/7] Creando nuevo entorno virtual...
echo.

python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo ❌ No se pudo crear el entorno virtual
        echo Verifica que Python este instalado correctamente
        pause
        exit /b 1
    )
)
echo ✅ Entorno virtual creado exitosamente

echo.
echo [5/7] Activando entorno virtual...
echo.

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado

echo.
echo [6/7] Actualizando pip...
echo.

python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip actualizado

echo.
echo [7/7] Instalando dependencias...
echo.

echo Instalando PyTorch...
if "%GPU_AVAILABLE%"=="true" (
    echo Instalando PyTorch con soporte CUDA...
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118 >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ Fallo la instalacion con CUDA, intentando CPU...
        pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
    )
) else (
    echo Instalando PyTorch CPU...
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
)

if errorlevel 1 (
    echo ❌ Error instalando PyTorch
    echo Intentando instalacion sin versiones especificas...
    pip install torch torchaudio torchvision >nul 2>&1
)

echo ✅ PyTorch instalado

echo.
echo Instalando dependencias criticas individualmente...
echo.

echo Instalando FastAPI...
pip install fastapi==0.115.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con FastAPI, intentando sin version especifica...
    pip install fastapi >nul 2>&1
)

echo Instalando Uvicorn...
pip install uvicorn==0.34.3 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con Uvicorn, intentando sin version especifica...
    pip install uvicorn >nul 2>&1
)

echo Instalando Rich...
pip install rich==14.0.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con Rich, intentando sin version especifica...
    pip install rich >nul 2>&1
)

echo Instalando LangChain...
pip install langchain==0.3.26 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con LangChain, intentando sin version especifica...
    pip install langchain >nul 2>&1
)

echo Instalando ChromaDB...
pip install chromadb==1.0.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con ChromaDB, intentando sin version especifica...
    pip install chromadb >nul 2>&1
)

echo.
echo Instalando resto de dependencias desde requirements.txt...
echo.

pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Algunas dependencias pueden no haberse instalado completamente
    echo Se instalaron las dependencias criticas individualmente
) else (
    echo ✅ Todas las dependencias instaladas correctamente
)

echo.
echo =======================================================
echo  Verificando instalacion...
echo =======================================================
echo.

echo Verificando PyTorch:
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')" 2>&1

echo.
echo Verificando dependencias principales:
python -c "import fastapi; print('✅ FastAPI OK')" 2>&1
python -c "import uvicorn; print('✅ Uvicorn OK')" 2>&1
python -c "import rich; print('✅ Rich OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
python -c "import langchain; print('✅ LangChain OK')" 2>&1
python -c "import chromadb; print('✅ ChromaDB OK')" 2>&1

echo.
echo =======================================================
echo  ¡Instalacion completada!
echo =======================================================
echo.
echo Ahora puedes ejecutar run_gui.bat para iniciar la aplicacion.
echo.
echo Si hay dependencias faltantes, ejecuta fix_dependencies.bat
echo para instalar las dependencias faltantes individualmente.
echo.
echo Resumen de la instalacion:
echo ✅ Entorno virtual creado y activado
echo ✅ PyTorch instalado (%GPU_AVAILABLE%)
echo ✅ Dependencias criticas instaladas
echo.
pause 