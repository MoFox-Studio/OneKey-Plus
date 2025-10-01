@echo off
chcp 65001 >nul
setlocal

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"

REM 设置Python可执行文件路径
set "PYTHON_EXECUTABLE=%SCRIPT_DIR%python_embedded\python.exe"

REM 设置更新脚本路径
set "UPDATE_SCRIPT=%SCRIPT_DIR%update.py"

REM 检查Python解释器是否存在
if not exist "%PYTHON_EXECUTABLE%" (
    echo.
    echo [ERROR] 未找到内置Python环境: %PYTHON_EXECUTABLE%
    echo.
    echo 请确保 "python_embedded" 文件夹与此脚本位于同一目录中。
    echo.
    pause
    exit /b 1
)

REM 检查更新脚本是否存在
if not exist "%UPDATE_SCRIPT%" (
    echo.
    echo [ERROR] 未找到更新脚本: %UPDATE_SCRIPT%
    echo.
    pause
    exit /b 1
)

REM 执行更新脚本
echo.
echo [INFO] 正在启动一键更新程序...
echo.
"%PYTHON_EXECUTABLE%" "%UPDATE_SCRIPT%"

endlocal
