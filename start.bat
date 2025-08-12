@echo off
setlocal

echo =======================================================
echo  批量导入 GUI - 启动助手
echo =======================================================
echo.

:: 检查虚拟环境是否存在且完整
set VENV_DIR=.venv
set NEEDS_INSTALL=false

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    set NEEDS_INSTALL=true
) else (
    :: 检查是否已安装 PyTorch
    call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
    python -c "import torch" >nul 2>&1
    if errorlevel 1 (
        set NEEDS_INSTALL=true
    )
)

if "%NEEDS_INSTALL%"=="true" (
    echo 🛠️ 检测到首次运行或安装不完整
    echo.
    echo 运行应用前需要安装依赖。
    echo.
    echo 请选择操作：
    echo.
    echo 1. 安装依赖（首次运行推荐）
    echo 2. 仅运行应用（已安装依赖时）
    echo 3. 检查系统
    echo 4. 修复依赖（安装失败时）
    echo 5. 退出
    echo.
    set /p choice="请选择一个选项 (1-5): "
    
    if "%choice%"=="1" (
        echo.
        echo 正在安装依赖...
        call install_requirements.bat
        if errorlevel 1 (
            echo.
            echo ❌ 安装失败，请检查上方错误。
            pause
            exit /b 1
        )
        echo.
        echo ✅ 安装完成，正在启动应用...
        timeout /t 2 /nobreak >nul
        call run_gui.bat
        
    ) else if "%choice%"=="2" (
        echo.
        echo 正在尝试运行应用...
        call run_gui.bat
        
    ) else if "%choice%"=="3" (
        echo.
        echo 正在检查系统...
        call check_system.bat
        
    ) else if "%choice%"=="4" (
        echo.
        echo 正在修复依赖...
        call fix_dependencies_simple.bat
        
    ) else if "%choice%"=="5" (
        echo.
        echo 已退出...
        exit /b 0
        
    ) else (
        echo.
        echo 无效选项，已退出...
        pause
        exit /b 1
    )
    
) else (
    echo ✅ 系统已准备好运行
    echo.
    echo 虚拟环境已存在且依赖已安装。
    echo.
    echo 请选择操作：
    echo.
    echo 1. 运行应用
    echo 2. 重新安装依赖
    echo 3. 检查系统
    echo 4. 修复依赖
    echo 5. 退出
    echo.
    set /p choice="请选择一个选项 (1-5): "
    
    if "%choice%"=="1" (
        echo.
        echo 正在启动应用...
        call run_gui.bat
        
    ) else if "%choice%"=="2" (
        echo.
        echo 正在重新安装依赖...
        call install_requirements.bat
        if errorlevel 1 (
            echo.
            echo ❌ 重新安装失败。
            pause
            exit /b 1
        )
        echo.
        echo ✅ 重新安装完成，正在启动应用...
        timeout /t 2 /nobreak >nul
        call run_gui.bat
        
    ) else if "%choice%"=="3" (
        echo.
        echo 正在检查系统...
        call check_system.bat
        
    ) else if "%choice%"=="4" (
        echo.
        echo 正在修复依赖...
        call fix_dependencies_simple.bat
        
    ) else if "%choice%"=="5" (
        echo.
        echo 已退出...
        exit /b 0
        
    ) else (
        echo.
        echo 无效选项，已退出...
        pause
        exit /b 1
    )
)