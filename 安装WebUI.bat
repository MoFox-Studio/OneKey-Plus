@echo off
chcp 65001 > nul
title MoFox-Bot WebUI 自动安装程序

echo.
echo ========================================
echo   MoFox-Bot WebUI 自动安装程序
echo ========================================
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 设置 Python 路径（优先使用预置的 Python）
set "PYTHON_CMD=python"

REM 检查预置的 Python
if exist "python_embedded\python.exe" (
    echo [提示] 使用 OneKey-Plus 预置的 Python
    set "PYTHON_CMD=python_embedded\python.exe"
    goto :check_tomlkit
)

REM 检查系统 Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [提示] 使用系统 Python
    goto :check_tomlkit
)

REM 两者都没找到
echo [错误] 未找到 Python！
echo 请确保：
echo   1. OneKey-Plus 目录下的 python_embedded 文件夹完整
echo   2. 或者系统已安装 Python 并添加到 PATH
echo.
pause
exit /b 1

:check_tomlkit
REM 检查 tomlkit 是否已安装
%PYTHON_CMD% -c "import tomlkit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 检测到缺少 tomlkit 库，正在安装...
    %PYTHON_CMD% -m pip install tomlkit
    if %errorlevel% neq 0 (
        echo [错误] tomlkit 安装失败！
        echo 提示：如果使用预置 Python，请确保网络连接正常
        pause
        exit /b 1
    )
    echo [成功] tomlkit 安装完成
    echo.
)

REM 运行安装脚本
echo [运行] 启动 WebUI 安装向导...
echo.
%PYTHON_CMD% scripts\webui_installer.py

REM 脚本结束，不自动关闭窗口（因为脚本内部已有暂停）
