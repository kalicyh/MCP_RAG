@echo off
setlocal

:: 定义虚拟环境目录名称
set VENV_DIR=.venv

echo =======================================================
echo  应用启动器 - 批量导入 GUI
echo =======================================================
echo.

:: 1. 检查虚拟环境是否存在
echo [1/3] 检查虚拟环境...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo.
    echo ❌ 错误：未找到虚拟环境
    echo.
    echo 虚拟环境不存在或已损坏。
    echo 请先运行 install_requirements.bat 创建并安装所有依赖。
    echo.
    pause
    exit /b 1
) else (
    echo ✅ 虚拟环境已找到
)

:: 2. 激活虚拟环境
echo.
echo [2/3] 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ❌ 错误：无法激活虚拟环境
    echo.
    echo 虚拟环境可能已损坏。
    echo 请运行 install_requirements.bat 重新创建。
    echo.
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

:: 3. 启动应用
echo.
echo [3/3] 正在启动应用...
echo =======================================================
echo.

python bulk_ingest_GUI/run_gui.py

echo.
echo =======================================================
echo 应用已关闭。
echo =======================================================
echo.
echo 如有错误，请检查：
echo 1. 所有依赖已安装（install_requirements.bat）
echo 2. 虚拟环境已正确激活
echo 3. 没有其他进程占用相关文件
echo.
pause 
pause