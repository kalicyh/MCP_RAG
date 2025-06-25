@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Ejecutor de Aplicacion - Bulk Ingest GUI
echo =======================================================
echo.

:: 1. Verificar si el entorno virtual existe
echo [1/3] Verificando entorno virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo.
    echo ❌ ERROR: Entorno virtual no encontrado
    echo.
    echo El entorno virtual no existe o esta corrupto.
    echo Por favor, ejecuta primero install_requirements.bat
    echo para crear e instalar todas las dependencias.
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Entorno virtual encontrado
)

:: 2. Activar el entorno virtual
echo.
echo [2/3] Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo activar el entorno virtual
    echo.
    echo El entorno virtual puede estar corrupto.
    echo Por favor, ejecuta install_requirements.bat para recrearlo.
    echo.
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado

:: 3. Ejecutar la aplicación
echo.
echo [3/3] Iniciando la aplicacion...
echo =======================================================
echo.

python bulk_ingest_GUI/run_gui.py

echo.
echo =======================================================
echo La aplicacion se ha cerrado.
echo =======================================================
echo.
echo Si hubo un error, verifica que:
echo 1. Todas las dependencias esten instaladas (install_requirements.bat)
echo 2. El entorno virtual este activado correctamente
echo 3. No haya otros procesos usando los archivos
echo.
pause 
pause 