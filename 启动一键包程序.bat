@echo off
CHCP 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo      MaiBot-Plus 一键启动程序
echo ========================================
echo.

REM 检测是否在压缩包内运行
set "CURRENT_PATH=%~dp0"
echo %CURRENT_PATH% | findstr /i "temp" >nul && set "IN_ARCHIVE=1" || set "IN_ARCHIVE=0"
echo %CURRENT_PATH% | findstr /i "tmp" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "rar$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "zip$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "7z$" >nul && set "IN_ARCHIVE=1"

if "%IN_ARCHIVE%"=="1" (
    echo ❌ 检测到在压缩包中运行！
    echo.
    echo 请先解压缩文件到本地目录再运行此脚本
    echo.
    pause >nul
    exit /b 1
)

REM 保存当前目录
set "CURRENT_DIR=%CD%"
cd /d "%~dp0"

echo 启动 MaiBot-Plus 管理程序...
echo ========================================

REM 启动onekey.py
python_embedded\python.exe onekey.py

REM 如果程序异常退出，显示错误信息
if !errorlevel! neq 0 (
    echo.
    echo ========================================
    echo 程序异常退出，错误代码：!errorlevel!
    echo ========================================
)

echo.
echo 按任意键退出...
pause >nul

@echo off
CHCP 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo      MaiBot-Plus 一键启动程序
echo ========================================
echo.

REM 检测是否在压缩包内运行
set "CURRENT_PATH=%~dp0"
echo %CURRENT_PATH% | findstr /i "temp" >nul && set "IN_ARCHIVE=1" || set "IN_ARCHIVE=0"
echo %CURRENT_PATH% | findstr /i "tmp" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "rar$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "zip$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "7z$" >nul && set "IN_ARCHIVE=1"

if "%IN_ARCHIVE%"=="1" (
    echo ❌ 检测到在压缩包中运行！
    echo.
    echo 请先解压缩文件到本地目录再运行此脚本
    echo.
    pause >nul
    exit /b 1
)

REM 保存当前目录
set "CURRENT_DIR=%CD%"
cd /d "%~dp0"

REM 检查虚拟环境和依赖标记
set "VENV_PATH=%~dp0.venv"
set "PYTHON_PATH=%VENV_PATH%\Scripts\python.exe"
set "DEPS_CHECK_FILE=%~dp0.deps_installed"

echo 检查运行环境...

if not exist "%PYTHON_PATH%" (
    echo ❌ 虚拟环境未找到！
    echo.
    echo 请先运行 "首次启动点我.bat" 初始化环境
    echo.
    pause
    exit /b 1
)

if not exist "%DEPS_CHECK_FILE%" (
    echo ❌ 依赖未安装！
    echo.
    echo 请先运行 "首次启动点我.bat" 安装依赖
    echo.
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.
echo 启动 MaiBot-Plus 管理程序...
echo ========================================

REM 启动onekey.py
"%PYTHON_PATH%" onekey.py

REM 如果程序异常退出，显示错误信息
if !errorlevel! neq 0 (
    echo.
    echo ========================================
    echo 程序异常退出，错误代码：!errorlevel!
    echo.
    echo 如果遇到依赖问题，请重新运行：
    echo    "首次启动点我.bat"
    echo ========================================
)

echo.
echo 按任意键退出...
pause >nul
