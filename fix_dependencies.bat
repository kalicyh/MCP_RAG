@echo off
setlocal

:: Define el nombre del directorio para el entorno virtual
set VENV_DIR=.venv

echo =======================================================
echo  依赖修复工具 - 批量导入GUI
echo =======================================================
echo.

:: 检查虚拟环境是否存在
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ❌ 错误：未找到虚拟环境
    echo 请先运行 install_requirements.bat
    pause
    exit /b 1
)

echo ✅ 虚拟环境已找到: %VENV_DIR%
echo.

:: 激活虚拟环境
echo 正在激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ 错误：无法激活虚拟环境
    echo 虚拟环境可能已损坏
    echo 请运行 install_requirements.bat 重新创建
    pause
    exit /b 1
)

echo ✅ 虚拟环境已激活: %VIRTUAL_ENV%
echo.

echo [1/5] 安装 Web 依赖 (FastAPI, Uvicorn)...
echo.

echo 正在安装 FastAPI...
pip install fastapi==0.115.13
if errorlevel 1 (
    echo ❌ 安装 FastAPI 失败
    echo 尝试不指定版本...
    pip install fastapi
)

echo.
echo 正在安装 Uvicorn...
pip install uvicorn==0.34.3
if errorlevel 1 (
    echo ❌ 安装 Uvicorn 失败
    echo 尝试不指定版本...
    pip install uvicorn
)

echo.
echo [2/5] 安装界面依赖 (Rich, Tkinter)...
echo.

echo 正在安装 Rich...
pip install rich==14.0.0
if errorlevel 1 (
    echo ❌ 安装 Rich 失败
    echo 尝试不指定版本...
    pip install rich
)

echo.
echo 检查 Tkinter（Python自带）...
python -c "import tkinter; print('✅ Tkinter 可用')" 2>&1
if errorlevel 1 (
    echo ❌ Tkinter 不可用
    echo 可能需要重新安装带 Tkinter 的 Python
)

echo.
echo [3/5] 安装文档处理依赖...
echo.

echo 正在安装 LangChain...
pip install langchain==0.3.26
if errorlevel 1 (
    echo ❌ 安装 LangChain 失败
    echo 尝试不指定版本...
    pip install langchain
)

echo.
echo 正在安装 ChromaDB...
pip install chromadb==1.0.13
if errorlevel 1 (
    echo ❌ 安装 ChromaDB 失败
    echo 尝试不指定版本...
    pip install chromadb
)

echo.
echo 正在安装 Sentence Transformers...
pip install sentence-transformers==2.7.0
if errorlevel 1 (
    echo ❌ 安装 Sentence Transformers 失败
    echo 尝试不指定版本...
    pip install sentence-transformers
)

echo.
echo [4/5] 安装文件依赖...
echo.

echo 正在安装 Unstructured...
pip install unstructured==0.17.2
if errorlevel 1 (
    echo ❌ 安装 Unstructured 失败
    echo 尝试不指定版本...
    pip install unstructured
)

echo.
echo 正在安装 PyPDF...
pip install pypdf==5.6.0
if errorlevel 1 (
    echo ❌ 安装 PyPDF 失败
    echo 尝试不指定版本...
    pip install pypdf
)

echo.
echo [5/5] 检查安装情况...
echo.

echo 检查关键依赖:
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
echo  修复完成
echo =======================================================
echo.
echo 如果所有依赖都显示 "OK"，可直接运行:
echo   run_gui.bat
echo.
echo 如果有错误，请尝试:
echo   1. 重新安装带全部选项的 Python
echo   2. 再次运行 install_requirements.bat
echo   3. 检查网络连接
echo.
pause 