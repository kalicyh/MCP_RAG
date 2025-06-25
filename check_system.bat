@echo off
setlocal

echo =======================================================
echo  Verificador de Sistema - Bulk Ingest GUI
echo =======================================================
echo.

echo [1/4] Verificando version de Python...
echo.

python --version 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
    goto :end
)

py --version 2>&1
if errorlevel 1 (
    echo ❌ py launcher no encontrado
) else (
    echo ✅ py launcher disponible
)

echo.
echo [2/4] Verificando arquitectura del sistema...
echo.

echo Arquitectura del sistema:
echo %PROCESSOR_ARCHITECTURE%

echo.
echo Informacion del procesador:
wmic cpu get name /value | findstr "Name="

echo.
echo [3/4] Verificando GPU y CUDA...
echo.

echo Verificando GPU NVIDIA:
nvidia-smi 2>&1
if errorlevel 1 (
    echo ❌ nvidia-smi no encontrado o no hay GPU NVIDIA
    echo.
    echo Verificando GPU con PowerShell:
    powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object Name, AdapterRAM" 2>&1
) else (
    echo ✅ GPU NVIDIA detectada
)

echo.
echo [4/4] Verificando versiones disponibles de PyTorch...
echo.

echo Intentando instalar PyTorch CPU...
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu 2>&1
if errorlevel 1 (
    echo ❌ No se pudo instalar PyTorch CPU
) else (
    echo ✅ PyTorch CPU instalado correctamente
    echo.
    echo Desinstalando para continuar con la instalacion completa...
    pip uninstall torch -y >nul 2>&1
)

echo.
echo =======================================================
echo  Recomendaciones:
echo =======================================================
echo.
echo 1. Si tienes GPU NVIDIA y CUDA:
echo    - Instala PyTorch con soporte CUDA
echo.
echo 2. Si NO tienes GPU NVIDIA:
echo    - Usa PyTorch CPU (mas lento pero funciona)
echo.
echo 3. Si tu Python es muy antiguo:
echo    - Actualiza a Python 3.11 o superior
echo.
echo 4. Para desarrollo/pruebas:
echo    - PyTorch CPU es suficiente
echo.
pause

:end 