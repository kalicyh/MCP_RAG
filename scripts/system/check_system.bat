@echo off
setlocal

echo =======================================================
echo  系统检测工具 - 批量导入GUI
echo =======================================================
echo.

echo [1/4] 检查 Python 版本...
echo.

python --version 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python
    goto :end
)

py --version 2>&1
if errorlevel 1 (
    echo ❌ 未找到 py 启动器
) else (
    echo ✅ py 启动器可用
)

echo.
echo [2/4] 检查系统架构...
echo.

echo 系统架构:
echo %PROCESSOR_ARCHITECTURE%

echo.
echo 处理器信息:
wmic cpu get name /value | findstr "Name="

echo.
echo [3/4] 检查 GPU 和 CUDA...
echo.

echo 检查 NVIDIA GPU:
nvidia-smi 2>&1
if errorlevel 1 (
    echo ❌ 未找到 nvidia-smi 或无 NVIDIA GPU
    echo.
    echo 使用 PowerShell 检查 GPU:
    powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object Name, AdapterRAM" 2>&1
) else (
    echo ✅ 检测到 NVIDIA GPU
)

echo.
echo [4/4] 检查可用的 PyTorch 版本...
echo.

echo 尝试安装 PyTorch CPU 版本...
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu 2>&1
if errorlevel 1 (
    echo ❌ 无法安装 PyTorch CPU 版本
) else (
    echo ✅ PyTorch CPU 安装成功
    echo.
    echo 正在卸载以继续完整安装...
    pip uninstall torch -y >nul 2>&1
)

echo.
echo =======================================================
echo  建议:
echo =======================================================
echo.
echo 1. 如果你有 NVIDIA GPU 和 CUDA:
echo    - 安装支持 CUDA 的 PyTorch
echo.
echo 2. 如果没有 NVIDIA GPU:
echo    - 使用 PyTorch CPU（速度较慢但可用）
echo.
echo 3. 如果你的 Python 版本过旧:
echo    - 请升级到 Python 3.11 或更高版本
echo.
echo 4. 用于开发/测试:
echo    - PyTorch CPU 版本已足够
echo.
pause

:end