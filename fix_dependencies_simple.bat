@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Reparador Simple de Dependencias - Bulk Ingest GUI
echo =======================================================
echo.

:: Verificar que el entorno virtual existe
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ❌ ERROR: Entorno virtual no encontrado
    echo Por favor, ejecuta install_requirements.bat primero
    pause
    exit /b 1
)

echo ✅ Entorno virtual encontrado: %VENV_DIR%
echo.

:: Activar el entorno virtual
echo Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    echo El entorno virtual puede estar corrupto
    echo Por favor, ejecuta install_requirements.bat para recrearlo
    pause
    exit /b 1
)

echo ✅ Entorno virtual activado
echo.

echo Instalando dependencias criticas...
echo.

:: Instalar dependencias críticas una por una
echo [1/6] FastAPI...
pip install fastapi==0.115.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con FastAPI, intentando sin version especifica...
    pip install fastapi >nul 2>&1
)

echo [2/6] Uvicorn...
pip install uvicorn==0.34.3 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con Uvicorn, intentando sin version especifica...
    pip install uvicorn >nul 2>&1
)

echo [3/6] Rich...
pip install rich==14.0.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con Rich, intentando sin version especifica...
    pip install rich >nul 2>&1
)

echo [4/6] LangChain...
pip install langchain==0.3.26 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con LangChain, intentando sin version especifica...
    pip install langchain >nul 2>&1
)

echo [5/6] ChromaDB...
pip install chromadb==1.0.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con ChromaDB, intentando sin version especifica...
    pip install chromadb >nul 2>&1
)

echo [6/6] Sentence Transformers...
pip install sentence-transformers==2.7.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Error con Sentence Transformers, intentando sin version especifica...
    pip install sentence-transformers >nul 2>&1
)

echo.
echo Verificando instalacion...
echo.

:: Verificar dependencias críticas
python -c "import fastapi; print('✅ FastAPI OK')" 2>&1
python -c "import uvicorn; print('✅ Uvicorn OK')" 2>&1
python -c "import rich; print('✅ Rich OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
python -c "import langchain; print('✅ LangChain OK')" 2>&1
python -c "import chromadb; print('✅ ChromaDB OK')" 2>&1

echo.
echo =======================================================
echo  Reparacion completada
echo =======================================================
echo.
echo Si todas las dependencias muestran "OK", puedes ejecutar:
echo   run_gui.bat
echo.
pause 