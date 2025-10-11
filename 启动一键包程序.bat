@echo off
CHCP 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
::      MaiBot-Plus 一键启动程序
:: ========================================
echo.

:: ----------------------------------------
:: 1. 环境检测
:: ----------------------------------------
echo [INFO] 正在进行环境检测...

:: 检测是否在压缩包内运行
set "CURRENT_PATH=%~dp0"
echo %CURRENT_PATH% | findstr /i "temp" >nul && set "IN_ARCHIVE=1" || set "IN_ARCHIVE=0"
echo %CURRENT_PATH% | findstr /i "tmp" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "rar$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "zip$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "7z$" >nul && set "IN_ARCHIVE=1"

if "%IN_ARCHIVE%"=="1" (
    echo.
    echo  你妈的, 是不是脑子有什么大病?
    echo.
    echo  在压缩包里直接点? 你当这是你家客厅啊, 想怎么来就怎么来?
    echo.
    echo  赶紧给老子滚去解压, 不然我顺着网线过去给你两拳!
    echo.
    pause >nul
    exit /b 1
)

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 定义核心路径
set "PYTHON_EXECUTABLE=%~dp0python_embedded\python.exe"
set "INIT_FLAG_FILE=%~dp0core\.initialized"
set "UPDATE_SCRIPT=%~dp0update.py"
set "CONFIG_SCRIPT=%~dp0config_wizard.py"
set "MAIN_SCRIPT=%~dp0onekey.py"

:: 检查Python解释器
if not exist "%PYTHON_EXECUTABLE%" (
    echo [ERROR] 未找到核心依赖: python_embedded\python.exe
    echo.
    echo         请确认程序文件是否完整。
    echo.
    pause >nul
    exit /b 1
)
echo [INFO] 环境检测通过。
echo.

:: ========================================
:: 2. 初始化与启动逻辑
:: ========================================

:: 检查初始化标记文件
if exist "%INIT_FLAG_FILE%" (
    echo [INFO] 检测到已完成初始化, 直接启动主程序...
    goto :start_main_program
)

echo [INFO] 未检测到初始化标记, 开始执行首次配置流程...
echo.

:: 确保core文件夹存在
if not exist "%~dp0core" (
    echo [INFO] 正在创建core文件夹...
    mkdir "%~dp0core"
)

:: 执行更新脚本
echo ========================================
echo      STEP 1: 执行更新程序
echo ========================================
"%PYTHON_EXECUTABLE%" "%UPDATE_SCRIPT%"
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] 更新程序执行失败, 错误代码: !errorlevel!
    echo.
    echo         请检查网络连接或查看上方日志输出。
    pause >nul
    exit /b !errorlevel!
)
echo [SUCCESS] 更新程序执行成功。
echo.

:: 执行配置向导
echo ========================================
echo      STEP 2: 执行配置向导
echo ========================================
"%PYTHON_EXECUTABLE%" "%CONFIG_SCRIPT%"
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] 配置向导执行失败, 错误代码: !errorlevel!
    echo.
    echo         请根据向导提示完成配置。
    pause >nul
    exit /b !errorlevel!
)
echo [SUCCESS] 配置向导执行成功。
echo.

:: 创建初始化标记
echo [INFO] 首次配置流程全部成功, 创建初始化标记...
echo Initialized on %date% %time% > "%INIT_FLAG_FILE%"
echo.

:start_main_program
:: ========================================
::      STEP 3: 启动主程序
:: ========================================
echo [INFO] 正在启动 MaiBot-Plus 管理程序...
echo.
"%PYTHON_EXECUTABLE%" "%MAIN_SCRIPT%"

if !errorlevel! neq 0 (
    echo.
    echo ========================================
    echo [WARNING] 主程序异常退出, 错误代码: !errorlevel!
    echo ========================================
)

echo.
echo 程序已结束, 按任意键退出...
pause >nul
exit /b 0
