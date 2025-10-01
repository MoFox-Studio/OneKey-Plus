@echo off
CHCP 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================
echo       MaiBot-Plus 首次启动配置
echo ========================================
echo.
echo 本程序将为您完成以下操作：
echo   • 创建Python虚拟环境
echo   • 安装所有必要的依赖包
echo   • 初始化运行环境
echo.
echo  首次运行可能需要几分钟时间，请耐心等待
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
    echo 检测到在压缩包中运行！
    echo.
    echo 请先解压缩文件到本地目录再运行此脚本
    echo 直接在压缩包中运行会导致程序异常
    echo.
    echo 按任意键退出，请解压后重新运行
    pause >nul
    exit /b 1
)

REM 删除旧的依赖安装标记文件（如果存在）
if exist ".deps_installed" (
    del ".deps_installed"
    echo 已清理旧的安装标记
)

echo 步骤1：检查Python环境...

REM 检查系统Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo 错误：未找到Python！
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo 下载地址：https://www.python.org/
    echo.
    echo 安装时请勾选"Add Python to PATH"选项
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ 找到Python %PYTHON_VERSION%

echo.
echo 步骤2：创建虚拟环境...

REM 删除现有虚拟环境（如果存在）
if exist ".venv" (
    echo  删除现有虚拟环境...
    rmdir /s /q ".venv" >nul 2>&1
)

REM 创建新的虚拟环境
echo 创建新的虚拟环境...
python -m venv .venv
if !errorlevel! neq 0 (
    echo ❌ 虚拟环境创建失败！
    echo.
    echo 可能的原因：
    echo - Python版本过低（需要3.8+）
    echo - 磁盘空间不足
    echo - 权限不足
    echo.
    echo 建议：尝试以管理员身份运行此脚本
    pause
    exit /b 1
)

echo ✅ 虚拟环境创建成功

REM 检查虚拟环境
set "VENV_PATH=%~dp0.venv"
set "PYTHON_PATH=%VENV_PATH%\Scripts\python.exe"
set "PIP_PATH=%VENV_PATH%\Scripts\pip.exe"

if not exist "%PYTHON_PATH%" (
    echo ❌ 虚拟环境验证失败！
    pause
    exit /b 1
)

echo.
echo 步骤3：安装依赖包...
echo.

set "SUCCESS_COUNT=0"
set "TOTAL_COUNT=0"

for %%d in (Bot Adapter Matcha-Adapter) do (
    if exist "%%d\requirements.txt" (
        set /a TOTAL_COUNT+=1
        echo 正在安装 %%d 的依赖包...
        
        REM 显示requirements.txt内容预览
        echo    依赖文件：%%d\requirements.txt
        
        "%PIP_PATH%" install -r "%%d\requirements.txt" --no-cache-dir --disable-pip-version-check
        if !errorlevel! equ 0 (
            echo ✅ %%d 依赖包安装完成
            set /a SUCCESS_COUNT+=1
        ) else (
            echo ❌ %%d 依赖包安装失败
            echo    请检查网络连接或依赖包是否存在问题
        )
        echo.
    ) else (
        echo  未找到 %%d\requirements.txt，跳过
    )
)

echo 安装总结：
echo    成功：%SUCCESS_COUNT%/%TOTAL_COUNT% 个模块
echo.

if %SUCCESS_COUNT% LSS %TOTAL_COUNT% (
    echo  部分依赖安装失败，但可以继续使用
    echo    如遇到问题，请重新运行此脚本
) else (
    echo ✅ 所有依赖安装完成！
)

REM 创建安装完成标记
echo Environment initialized on %date% %time% > ".deps_installed"
echo Python: %PYTHON_VERSION% >> ".deps_installed"
echo Modules: %SUCCESS_COUNT%/%TOTAL_COUNT% >> ".deps_installed"

echo.
echo 步骤4：启动主程序...
echo.

REM 直接启动主程序
"%PYTHON_PATH%" onekey.py

echo.
echo ========================================
echo    MaiBot-Plus 环境配置完成！
echo.
echo    下次使用请直接运行：
echo    "启动一键包程序.bat"
echo.
echo   如需重新配置环境，请重新运行此脚本
echo ========================================
echo.
pause
