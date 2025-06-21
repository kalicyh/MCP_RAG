@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Asistente de Arranque - Bulk Ingest GUI
echo =======================================================
echo.

:: 1. Comprobar si el entorno virtual existe
echo [1/4] Verificando entorno virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo      - Entorno no encontrado. Creando uno nuevo...
    
    :: Intenta crear el entorno con 'python', si falla, prueba con 'py'
    python -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        py -m venv %VENV_DIR% >nul 2>&1
        if errorlevel 1 (
            echo.
            echo ERROR: No se pudo crear el entorno virtual.
            echo Por favor, asegurate de que Python este instalado y anadido al PATH.
            pause
            exit /b 1
        )
    )
    echo      - Entorno virtual creado en la carpeta '%VENV_DIR%'.
) else (
    echo      - Entorno virtual encontrado.
)

:: 2. Activar el entorno virtual
echo.
echo [2/4] Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
echo      - Entorno activado.

:: 3. Instalar/actualizar dependencias
echo.
echo [3/4] Instalando/actualizando dependencias desde requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo      - Dependencias instaladas correctamente.

:: 4. Iniciar la aplicacion
echo.
echo [4/4] Iniciando la aplicacion...
echo =======================================================
echo.
python bulk_ingest_gui.py

echo.
echo La aplicacion se ha cerrado. Pulsa cualquier tecla para salir.
pause 