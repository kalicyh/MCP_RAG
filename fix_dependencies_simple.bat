@echo off
setlocal

:: 检查虚拟环境是否存在
set VENV_DIR=.venv

echo =======================================================
echo  简易依赖修复器 - 批量导入 GUI
echo =======================================================
echo.

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

echo ✅ 虚拟环境已激活
echo.

echo 正在安装关键依赖...
echo.

:: 逐个安装关键依赖
echo [1/6] FastAPI...
pip install fastapi==0.115.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FastAPI 安装失败，尝试无版本...
    pip install fastapi >nul 2>&1
)

echo [2/6] Uvicorn...
pip install uvicorn==0.34.3 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Uvicorn 安装失败，尝试无版本...
    pip install uvicorn >nul 2>&1
)

echo [3/6] Rich...
pip install rich==14.0.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Rich 安装失败，尝试无版本...
    pip install rich >nul 2>&1
)

echo [4/6] LangChain...
pip install langchain==0.3.26 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ LangChain 安装失败，尝试无版本...
    pip install langchain >nul 2>&1
)

echo [5/6] ChromaDB...
pip install chromadb==1.0.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ ChromaDB 安装失败，尝试无版本...
    pip install chromadb >nul 2>&1
)

echo [6/6] Sentence Transformers...
pip install sentence-transformers==2.7.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Sentence Transformers 安装失败，尝试无版本...
    pip install sentence-transformers >nul 2>&1
)

echo.
echo 正在验证安装...
echo.

:: 验证关键依赖
python -c "import fastapi; print('✅ FastAPI OK')" 2>&1
python -c "import uvicorn; print('✅ Uvicorn OK')" 2>&1
python -c "import rich; print('✅ Rich OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
python -c "import langchain; print('✅ LangChain OK')" 2>&1
python -c "import chromadb; print('✅ ChromaDB OK')" 2>&1

echo.
echo =======================================================
echo  修复完成
echo =======================================================
echo.
echo 如果所有依赖都显示 "OK"，可运行：
echo   run_gui.bat
echo.
pause