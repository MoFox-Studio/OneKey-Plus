@echo off
CHCP 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
::      WSL 一键安装程序
:: ========================================
echo.
echo 正在检查管理员权限...

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ========================================================
    echo  错误：需要管理员权限
    echo  请右键点击本文件，选择“以管理员身份运行”来安装 WSL。
    echo ========================================================
    echo.
    pause
    exit
)

echo 管理员权限已确认。
echo.
echo ========================================================
echo  正在开始安装 Windows Subsystem for Linux (WSL)...
echo  目标发行版: Ubuntu
echo ========================================================
echo.

:: 尝试安装 WSL 和 Ubuntu
:: wsl --install 默认会安装 Ubuntu。如果 WSL 已安装，它可能会提示。
wsl --install -d Ubuntu

if %errorLevel% equ 0 (
    echo.
    echo ========================================================
    echo  安装命令执行成功！
    echo.
    echo  [重要提示]
    echo  1. 如果这是您首次安装 WSL，您必须 **重启计算机** 才能生效。
    echo  2. 重启后，请去微软商店安装Windows Terminal，点击上面的小三角，选择Ubuntu，终端窗口将弹出，请等待它完成初始化。
    echo  3. 初始化完成后，您需要设置一个用户名和密码。
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  安装命令返回了非零状态码。
    echo.
    echo  [常见故障排查]
    echo  1. **虚拟化未开启** (最常见原因)：
    echo     请进入 BIOS/UEFI 设置，找到 Intel VT-x 或 AMD-V 选项并设为 Enabled。
    echo     (您可以在 任务管理器 -^> 性能 -^> CPU 中查看“虚拟化”是否显示为“已启用”)
    echo.
    echo  2. WSL 或 Ubuntu 已安装：
    echo     如果已经安装，无需重复运行。
    echo.
    echo  3. Windows 版本过旧：
    echo     请确保您的 Windows 10 版本高于 2004，或使用 Windows 11。
    echo.
    echo  4. 系统需要重启：
    echo     某些 Windows 更新可能需要重启才能完成，请重启后再试。
    echo ========================================================
)

echo.
echo 按任意键退出...
pause >nul
