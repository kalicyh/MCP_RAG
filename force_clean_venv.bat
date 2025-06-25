@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Limpiador Forzado de Entorno Virtual - Bulk Ingest GUI
echo =======================================================
echo.

echo [1/4] Cerrando procesos de Python activos...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
echo      - Procesos de Python cerrados.

echo.
echo [2/4] Esperando que se liberen los archivos...
timeout /t 3 /nobreak >nul
echo      - Espera completada.

echo.
echo [3/4] Eliminando entorno virtual existente...
if exist "%VENV_DIR%" (
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "%VENV_DIR%" (
        echo      - Intentando eliminación forzada...
        rmdir /s /q "%VENV_DIR%" 2>&1
        if exist "%VENV_DIR%" (
            echo      - ERROR: No se pudo eliminar el entorno virtual.
            echo      - Por favor, cierra manualmente cualquier ventana de terminal
            echo      - o editor que pueda estar usando el entorno virtual.
            pause
            exit /b 1
        )
    )
    echo      - Entorno virtual eliminado exitosamente.
) else (
    echo      - No se encontró entorno virtual para eliminar.
)

echo.
echo [4/4] Creando nuevo entorno virtual...
python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudo crear el entorno virtual.
        echo Por favor, asegurate de que Python este instalado y anadido al PATH.
        echo.
        echo Comandos para verificar Python:
        echo   python --version
        echo   py --version
        pause
        exit /b 1
    )
)
echo      - Nuevo entorno virtual creado exitosamente.

echo.
echo =======================================================
echo  Limpieza forzada completada exitosamente!
echo =======================================================
echo.
echo Ahora puedes ejecutar run_gui.bat para instalar las dependencias
echo y iniciar la aplicacion.
echo.
pause 