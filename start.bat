@echo off
setlocal

echo =======================================================
echo  Bulk Ingest GUI - Asistente de Inicio
echo =======================================================
echo.

:: Verificar si el entorno virtual existe y está completo
set VENV_DIR=.venv
set NEEDS_INSTALL=false

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    set NEEDS_INSTALL=true
) else (
    :: Verificar si PyTorch está instalado
    call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
    python -c "import torch" >nul 2>&1
    if errorlevel 1 (
        set NEEDS_INSTALL=true
    )
)

if "%NEEDS_INSTALL%"=="true" (
    echo 🔧 Primera vez o instalacion incompleta detectada
    echo.
    echo Se requiere instalar las dependencias antes de ejecutar la aplicacion.
    echo.
    echo ¿Que deseas hacer?
    echo.
    echo 1. Instalar dependencias (recomendado para primera vez)
    echo 2. Solo ejecutar la aplicacion (si ya esta instalado)
    echo 3. Verificar el sistema
    echo 4. Reparar dependencias (si la instalacion fallo)
    echo 5. Salir
    echo.
    set /p choice="Selecciona una opcion (1-5): "
    
    if "%choice%"=="1" (
        echo.
        echo Iniciando instalacion de dependencias...
        call install_requirements.bat
        if errorlevel 1 (
            echo.
            echo ❌ La instalacion fallo. Revisa los errores arriba.
            pause
            exit /b 1
        )
        echo.
        echo ✅ Instalacion completada. Iniciando aplicacion...
        timeout /t 2 /nobreak >nul
        call run_gui.bat
        
    ) else if "%choice%"=="2" (
        echo.
        echo Intentando ejecutar la aplicacion...
        call run_gui.bat
        
    ) else if "%choice%"=="3" (
        echo.
        echo Verificando el sistema...
        call check_system.bat
        
    ) else if "%choice%"=="4" (
        echo.
        echo Reparando dependencias...
        call fix_dependencies_simple.bat
        
    ) else if "%choice%"=="5" (
        echo.
        echo Saliendo...
        exit /b 0
        
    ) else (
        echo.
        echo Opcion invalida. Saliendo...
        pause
        exit /b 1
    )
    
) else (
    echo ✅ Sistema listo para ejecutar
    echo.
    echo El entorno virtual existe y las dependencias estan instaladas.
    echo.
    echo ¿Que deseas hacer?
    echo.
    echo 1. Ejecutar la aplicacion
    echo 2. Reinstalar dependencias
    echo 3. Verificar el sistema
    echo 4. Reparar dependencias
    echo 5. Salir
    echo.
    set /p choice="Selecciona una opcion (1-5): "
    
    if "%choice%"=="1" (
        echo.
        echo Iniciando aplicacion...
        call run_gui.bat
        
    ) else if "%choice%"=="2" (
        echo.
        echo Reinstalando dependencias...
        call install_requirements.bat
        if errorlevel 1 (
            echo.
            echo ❌ La reinstalacion fallo.
            pause
            exit /b 1
        )
        echo.
        echo ✅ Reinstalacion completada. Iniciando aplicacion...
        timeout /t 2 /nobreak >nul
        call run_gui.bat
        
    ) else if "%choice%"=="3" (
        echo.
        echo Verificando el sistema...
        call check_system.bat
        
    ) else if "%choice%"=="4" (
        echo.
        echo Reparando dependencias...
        call fix_dependencies_simple.bat
        
    ) else if "%choice%"=="5" (
        echo.
        echo Saliendo...
        exit /b 0
        
    ) else (
        echo.
        echo Opcion invalida. Saliendo...
        pause
        exit /b 1
    )
) 