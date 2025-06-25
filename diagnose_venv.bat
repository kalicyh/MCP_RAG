@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Diagnostico del Entorno Virtual - Bulk Ingest GUI
echo =======================================================
echo.

echo [1/5] Verificando existencia del directorio...
if exist "%VENV_DIR%" (
    echo ✅ Directorio .venv existe
) else (
    echo ❌ Directorio .venv NO existe
    goto :create_new
)

echo.
echo [2/5] Verificando estructura del entorno virtual...
echo.

:: Verificar archivos y directorios críticos
set MISSING_FILES=0

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ✅ Scripts\activate.bat existe
) else (
    echo ❌ Scripts\activate.bat NO existe
    set /a MISSING_FILES+=1
)

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo ✅ Scripts\python.exe existe
) else (
    echo ❌ Scripts\python.exe NO existe
    set /a MISSING_FILES+=1
)

if exist "%VENV_DIR%\Lib\site-packages" (
    echo ✅ Lib\site-packages existe
) else (
    echo ❌ Lib\site-packages NO existe
    set /a MISSING_FILES+=1
)

if exist "%VENV_DIR%\pyvenv.cfg" (
    echo ✅ pyvenv.cfg existe
) else (
    echo ❌ pyvenv.cfg NO existe
    set /a MISSING_FILES+=1
)

echo.
echo [3/5] Verificando permisos de acceso...
echo.

:: Intentar acceder a los archivos
if exist "%VENV_DIR%\Scripts\activate.bat" (
    type "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
    if errorlevel 1 (
        echo ❌ No se puede leer Scripts\activate.bat (problema de permisos)
        set /a MISSING_FILES+=1
    ) else (
        echo ✅ Se puede leer Scripts\activate.bat
    )
)

echo.
echo [4/5] Verificando contenido del directorio...
echo.

echo Contenido del directorio .venv:
dir "%VENV_DIR%" /b 2>&1

echo.
echo Contenido del directorio .venv\Scripts (si existe):
if exist "%VENV_DIR%\Scripts" (
    dir "%VENV_DIR%\Scripts" /b 2>&1
) else (
    echo ❌ Directorio Scripts no existe
)

echo.
echo [5/5] Resumen del diagnostico...
echo.

if %MISSING_FILES% GTR 0 (
    echo ❌ Se encontraron %MISSING_FILES% archivos/directorios faltantes o inaccesibles
    echo.
    echo El entorno virtual esta corrupto o incompleto.
    echo Se recomienda eliminarlo y crear uno nuevo.
    echo.
    echo ¿Deseas eliminar el entorno virtual corrupto? (S/N)
    set /p choice=
    if /i "%choice%"=="S" (
        echo.
        echo Eliminando entorno virtual corrupto...
        rmdir /s /q "%VENV_DIR%" 2>&1
        if exist "%VENV_DIR%" (
            echo ❌ No se pudo eliminar. Usa force_clean_venv.bat
        ) else (
            echo ✅ Entorno virtual eliminado
            goto :create_new
        )
    )
) else (
    echo ✅ El entorno virtual parece estar en buen estado
    echo.
    echo El problema puede estar en la verificacion del script run_gui.bat
    echo Verificando la condicion exacta...
    echo.
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        echo ✅ La condicion 'exist "%VENV_DIR%\Scripts\activate.bat"' es VERDADERA
        echo El script NO deberia intentar crear un nuevo entorno
    ) else (
        echo ❌ La condicion 'exist "%VENV_DIR%\Scripts\activate.bat"' es FALSA
        echo El script SI deberia intentar crear un nuevo entorno
    )
)

goto :end

:create_new
echo.
echo =======================================================
echo  Creando nuevo entorno virtual...
echo =======================================================
echo.

python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo ❌ ERROR: No se pudo crear el entorno virtual
        echo Ejecuta check_python.bat para verificar la instalacion
    ) else (
        echo ✅ Nuevo entorno virtual creado con 'py'
    )
) else (
    echo ✅ Nuevo entorno virtual creado con 'python'
)

:end
echo.
echo =======================================================
echo  Diagnostico completado
echo =======================================================
echo.
pause 