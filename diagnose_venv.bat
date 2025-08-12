@echo off
setlocal
:: 定义虚拟环境目录名称
set VENV_DIR=.venv

echo =======================================================
echo  虚拟环境诊断工具 - 批量导入GUI
echo =======================================================
echo.

echo [1/5] 检查目录是否存在...
if exist "%VENV_DIR%" (
    echo ✅ .venv 目录存在
) else (
    echo ❌ .venv 目录不存在
    goto :create_new
)

echo.
echo [2/5] 检查虚拟环境结构...
echo.
:: 检查关键文件和目录
set MISSING_FILES=0
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ✅ Scripts\activate.bat 存在
) else (
    echo ❌ Scripts\activate.bat 不存在
    set /a MISSING_FILES+=1
)
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo ✅ Scripts\python.exe 存在
) else (
    echo ❌ Scripts\python.exe 不存在
    set /a MISSING_FILES+=1
)
if exist "%VENV_DIR%\Lib\site-packages" (
    echo ✅ Lib\site-packages 存在
) else (
    echo ❌ Lib\site-packages 不存在
    set /a MISSING_FILES+=1
)
if exist "%VENV_DIR%\pyvenv.cfg" (
    echo ✅ pyvenv.cfg 存在
) else (
    echo ❌ pyvenv.cfg 不存在
    set /a MISSING_FILES+=1
)

echo.
echo [3/5] 检查访问权限...
echo.
:: 尝试访问文件
if exist "%VENV_DIR%\Scripts\activate.bat" (
    type "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
    if errorlevel 1 (
        echo ❌ 无法读取 Scripts\activate.bat（权限问题）
        set /a MISSING_FILES+=1
    ) else (
        echo ✅ 可以读取 Scripts\activate.bat
    )
)

echo.
echo [4/5] 检查目录内容...
echo.
echo .venv 目录内容:
dir "%VENV_DIR%" /b 2>&1

echo.
echo .venv\Scripts 目录内容（如存在）:
if exist "%VENV_DIR%\Scripts" (
    dir "%VENV_DIR%\Scripts" /b 2>&1
) else (
    echo ❌ Scripts 目录不存在
)

echo.
echo [5/5] 诊断总结...
echo.
if %MISSING_FILES% GTR 0 (
    echo ❌ 发现 %MISSING_FILES% 个缺失或不可访问的文件/目录
    echo.
    echo 虚拟环境已损坏或不完整。
    echo 建议删除并重新创建。
    echo.
    echo 是否删除损坏的虚拟环境？（Y/N）
    set /p choice=
    if /i "%choice%"=="Y" (
        echo.
        echo 正在删除损坏的虚拟环境...
        rmdir /s /q "%VENV_DIR%" 2>&1
        if exist "%VENV_DIR%" (
            echo ❌ 删除失败。请使用 force_clean_venv.bat
        ) else (
            echo ✅ 虚拟环境已删除
            goto :create_new
        )
    )
) else (
    echo ✅ 虚拟环境状态良好
    echo.
    echo 问题可能出在 run_gui.bat 的检测脚本
    echo 正在检查具体条件...
    echo.
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        echo ✅ 条件 'exist "%VENV_DIR%\Scripts\activate.bat"' 为真
        echo 脚本不应尝试创建新环境
    ) else (
        echo ❌ 条件 'exist "%VENV_DIR%\Scripts\activate.bat"' 为假
        echo 脚本应尝试创建新环境
    )
)

goto :end

:create_new
echo.
echo =======================================================
echo  正在创建新虚拟环境...
echo =======================================================
echo.
python -m venv %VENV_DIR% >nul 2>&1
if errorlevel 1 (
    py -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo ❌ 错误：无法创建虚拟环境
        echo 请运行 check_python.bat 检查安装
    ) else (
        echo ✅ 使用 'py' 创建新虚拟环境成功
    )
) else (
    echo ✅ 使用 'python' 创建新虚拟环境成功
)

:end
echo.
echo =======================================================
echo  诊断完成
echo =======================================================
echo.
pause