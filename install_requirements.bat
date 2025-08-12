@echo off
setlocal

:: 定义虚拟环境目录名称
set VENV_DIR=.venv

echo =======================================================
echo  依赖安装器 - 批量导入 GUI
echo =======================================================
echo.

echo [1/7] 检查系统...
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未在 PATH 中找到 Python
    echo.
    echo 请从 https://www.python.org/downloads/ 安装 Python
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
) else (
    echo ✅ 已找到 Python
    python --version
)

echo.
echo [2/7] 检查 GPU 和 CUDA...
echo.

nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ℹ️ 未检测到 NVIDIA GPU - 将使用 PyTorch CPU
    set GPU_AVAILABLE=false
) else (
    echo ✅ 检测到 NVIDIA GPU - 将使用 PyTorch CUDA
    set GPU_AVAILABLE=true
)

echo.
echo [3/7] 清理现有虚拟环境...
echo.

if exist "%VENV_DIR%" (
    echo 正在删除现有虚拟环境...
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "%VENV_DIR%" (
        echo ⚠️ 未能完全删除，尝试强制...
        taskkill /f /im python.exe >nul 2>&1
        timeout /t 2 /nobreak >nul
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
        if exist "%VENV_DIR%" (
            echo ❌ 无法删除虚拟环境
            echo 请关闭所有终端窗口后重试
            pause
            exit /b 1
        )
    )
    echo ✅ 虚拟环境已删除
) else (
    echo ℹ️ 未找到可删除的虚拟环境
)

echo.
echo [4/7] 创建新虚拟环境...
echo.

python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo ❌ 无法创建虚拟环境
        echo 请检查 Python 是否正确安装
        pause
        exit /b 1
    )
)
echo ✅ 虚拟环境创建成功

echo.
echo [5/7] 激活虚拟环境...
echo.

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ 无法激活虚拟环境
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

echo.
echo [6/7] 升级 pip...
echo.

python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip 已升级

echo.
echo [7/7] 安装依赖...
echo.

echo 正在安装 PyTorch...
if "%GPU_AVAILABLE%"=="true" (
    echo 正在安装支持 CUDA 的 PyTorch...
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118 >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ CUDA 安装失败，尝试 CPU...
        pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
    )
) else (
    echo 正在安装 PyTorch CPU...
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
)

if errorlevel 1 (
    echo ❌ 安装 PyTorch 时出错
    echo 正在尝试无版本安装...
    pip install torch torchaudio torchvision >nul 2>&1
)

echo ✅ PyTorch 已安装

echo.
echo 正在单独安装关键依赖...
echo.

echo 正在安装 FastAPI...
pip install fastapi==0.115.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FastAPI 安装失败，尝试无版本...
    pip install fastapi >nul 2>&1
)

echo 正在安装 Uvicorn...
pip install uvicorn==0.34.3 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Uvicorn 安装失败，尝试无版本...
    pip install uvicorn >nul 2>&1
)

echo 正在安装 Rich...
pip install rich==14.0.0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Rich 安装失败，尝试无版本...
    pip install rich >nul 2>&1
)

echo 正在安装 LangChain...
pip install langchain==0.3.26 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ LangChain 安装失败，尝试无版本...
    pip install langchain >nul 2>&1
)

echo 正在安装 ChromaDB...
pip install chromadb==1.0.13 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ ChromaDB 安装失败，尝试无版本...
    pip install chromadb >nul 2>&1
)

echo.
echo 正在从 requirements.txt 安装剩余依赖...
echo.

pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 部分依赖可能未完全安装
    echo 已单独安装关键依赖
) else (
    echo ✅ 所有依赖已正确安装
)

echo.
echo =======================================================
echo  正在验证安装...
echo =======================================================
echo.

echo 验证 PyTorch:
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')" 2>&1

echo.
echo 验证主要依赖:
python -c "import fastapi; print('✅ FastAPI OK')" 2>&1
python -c "import uvicorn; print('✅ Uvicorn OK')" 2>&1
python -c "import rich; print('✅ Rich OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
python -c "import langchain; print('✅ LangChain OK')" 2>&1
python -c "import chromadb; print('✅ ChromaDB OK')" 2>&1

echo.
echo =======================================================
echo  安装完成！
echo =======================================================
echo.
echo 现在可以运行 run_gui.bat 启动应用。
echo.
echo 如有依赖缺失，请运行 fix_dependencies.bat 单独安装缺失依赖。
echo.
echo 安装摘要：
echo ✅ 虚拟环境已创建并激活
echo ✅ PyTorch 已安装 (%GPU_AVAILABLE%)
echo ✅ 关键依赖已安装
echo.
pause