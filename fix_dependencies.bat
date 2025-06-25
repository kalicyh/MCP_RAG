@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  Reparador de Dependencias - Bulk Ingest GUI
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

echo ✅ Entorno virtual activado: %VIRTUAL_ENV%
echo.

echo [1/5] Instalando dependencias web (FastAPI, Uvicorn)...
echo.

echo Instalando FastAPI...
pip install fastapi==0.115.13
if errorlevel 1 (
    echo ❌ Error instalando FastAPI
    echo Intentando sin version especifica...
    pip install fastapi
)

echo.
echo Instalando Uvicorn...
pip install uvicorn==0.34.3
if errorlevel 1 (
    echo ❌ Error instalando Uvicorn
    echo Intentando sin version especifica...
    pip install uvicorn
)

echo.
echo [2/5] Instalando dependencias de interfaz (Rich, Tkinter)...
echo.

echo Instalando Rich...
pip install rich==14.0.0
if errorlevel 1 (
    echo ❌ Error instalando Rich
    echo Intentando sin version especifica...
    pip install rich
)

echo.
echo Verificando Tkinter (incluido con Python)...
python -c "import tkinter; print('✅ Tkinter disponible')" 2>&1
if errorlevel 1 (
    echo ❌ Tkinter no disponible
    echo Esto puede requerir reinstalar Python con Tkinter
)

echo.
echo [3/5] Instalando dependencias de procesamiento de documentos...
echo.

echo Instalando LangChain...
pip install langchain==0.3.26
if errorlevel 1 (
    echo ❌ Error instalando LangChain
    echo Intentando sin version especifica...
    pip install langchain
)

echo.
echo Instalando ChromaDB...
pip install chromadb==1.0.13
if errorlevel 1 (
    echo ❌ Error instalando ChromaDB
    echo Intentando sin version especifica...
    pip install chromadb
)

echo.
echo Instalando Sentence Transformers...
pip install sentence-transformers==2.7.0
if errorlevel 1 (
    echo ❌ Error instalando Sentence Transformers
    echo Intentando sin version especifica...
    pip install sentence-transformers
)

echo.
echo [4/5] Instalando dependencias de archivos...
echo.

echo Instalando Unstructured...
pip install unstructured==0.17.2
if errorlevel 1 (
    echo ❌ Error instalando Unstructured
    echo Intentando sin version especifica...
    pip install unstructured
)

echo.
echo Instalando PyPDF...
pip install pypdf==5.6.0
if errorlevel 1 (
    echo ❌ Error instalando PyPDF
    echo Intentando sin version especifica...
    pip install pypdf
)

echo.
echo [5/5] Verificando instalacion...
echo.

echo Verificando dependencias criticas:
echo.

python -c "import fastapi; print('✅ FastAPI OK')" 2>&1
python -c "import uvicorn; print('✅ Uvicorn OK')" 2>&1
python -c "import rich; print('✅ Rich OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
python -c "import langchain; print('✅ LangChain OK')" 2>&1
python -c "import chromadb; print('✅ ChromaDB OK')" 2>&1
python -c "import sentence_transformers; print('✅ Sentence Transformers OK')" 2>&1
python -c "import unstructured; print('✅ Unstructured OK')" 2>&1
python -c "import pypdf; print('✅ PyPDF OK')" 2>&1

echo.
echo =======================================================
echo  Reparacion completada
echo =======================================================
echo.
echo Si todas las dependencias muestran "OK", puedes ejecutar:
echo   run_gui.bat
echo.
echo Si hay errores, intenta:
echo   1. Reinstalar Python con todas las opciones
echo   2. Ejecutar install_requirements.bat nuevamente
echo   3. Verificar la conexion a internet
echo.
pause 