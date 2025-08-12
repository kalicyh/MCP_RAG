@echo off
setlocal

:: 定义虚拟环境目录名称
set VENV_DIR=.venv

echo =======================================================
echo  虚拟环境强制清理器 - 批量导入 GUI
echo =======================================================
echo.

echo [1/4] 关闭所有 Python 进程...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
echo      - Python 进程已关闭。

echo.
echo [2/4] 等待文件释放...
timeout /t 3 /nobreak >nul
echo      - 等待完成。

echo.
echo [3/4] 删除现有虚拟环境...
if exist "%VENV_DIR%" (
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "%VENV_DIR%" (
        echo      - 正在尝试强制删除...
        rmdir /s /q "%VENV_DIR%" 2>&1
        if exist "%VENV_DIR%" (
            echo      - 错误：无法删除虚拟环境。
            echo      - 请手动关闭所有终端窗口
            echo      - 或编辑器可能正在使用虚拟环境。
            pause
            exit /b 1
        )
    )
    echo      - 虚拟环境已成功删除。
) else (
    echo      - 未找到可删除的虚拟环境。
)

echo.
echo [4/4] 创建新虚拟环境...
python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo.
        echo 错误：无法创建虚拟环境。
        echo 请确保 Python 已安装并添加到 PATH。
        echo.
        echo 检查 Python 命令：
        echo   python --version
        echo   py --version
        pause
        exit /b 1
    )
)
echo      - 新虚拟环境已成功创建。

echo.
echo =======================================================
echo  强制清理完成！
echo =======================================================
echo.
echo 现在可以运行 run_gui.bat 安装依赖并启动应用。
echo.
pause