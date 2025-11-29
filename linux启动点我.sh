#!/bin/bash

# 设置UTF-8编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

echo "========================================"
echo "      MoFox-Core 一键启动程序"
echo "========================================"
echo

# 切换到脚本所在目录
CALL_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
cd "$SCRIPT_DIR"

SCRIPT_FILENAME="mofox-core.py"
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_FILENAME"

# 解析可选参数
while [ $# -gt 0 ]; do
    case "$1" in
        -s|--script-path)
            shift
            if [ -z "$1" ]; then
                echo "❌ 错误：参数 -s/--script-path 需要指定 $SCRIPT_FILENAME 的路径！"
                echo
                read -p "按任意键退出..."
                exit 1
            fi
            ARG_TARGET="$1"
            if [[ "$ARG_TARGET" != /* ]]; then
                ARG_TARGET="$CALL_DIR/$ARG_TARGET"
            fi
            if [ -d "$ARG_TARGET" ]; then
                ARG_TARGET="${ARG_TARGET%/}/$SCRIPT_FILENAME"
            fi
            if [ "$(basename "$ARG_TARGET")" != "$SCRIPT_FILENAME" ]; then
                echo "❌ 错误：指定路径必须指向 $SCRIPT_FILENAME！"
                echo
                read -p "按任意键退出..."
                exit 1
            fi
            if ! ARG_DIR="$(cd "$(dirname "$ARG_TARGET")" 2>/dev/null && pwd)"; then
                echo "❌ 错误：无法解析脚本路径：$ARG_TARGET"
                echo
                read -p "按任意键退出..."
                exit 1
            fi
            SCRIPT_PATH="$ARG_DIR/$SCRIPT_FILENAME"
            shift
            ;;
        --)
            shift
            break
            ;;
        -* )
            echo "❌ 错误：未知参数：$1"
            echo
            read -p "按任意键退出..."
            exit 1
            ;;
        * )
            break
            ;;
    esac
done

# 检测是否在临时目录中运行
CURRENT_PATH="$(pwd)"
IN_ARCHIVE=0

if echo "$CURRENT_PATH" | grep -qi "temp"; then
    IN_ARCHIVE=1
elif echo "$CURRENT_PATH" | grep -qi "tmp"; then
    IN_ARCHIVE=1
fi

if [ "$IN_ARCHIVE" -eq 1 ]; then
    echo "❌ 检测到在临时目录中运行！"
    echo
    echo "请先解压缩文件到本地目录再运行此脚本"
    echo
    read -p "按任意键退出..."
    exit 1
fi

# 检查关键文件是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ 错误：未找到 $SCRIPT_FILENAME 文件！"
    echo
    echo "请确保此脚本位于MoFox-Core项目根目录中，或通过 -s/--script-path 参数指定 $SCRIPT_FILENAME 文件路径"
    echo "当前目录：$SCRIPT_DIR"
    echo "尝试的脚本路径：$SCRIPT_PATH"
    echo
    read -p "按任意键退出..."
    exit 1
fi

# 检查虚拟环境和依赖标记
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON_PATH="$VENV_PATH/bin/python"
DEPS_CHECK_FILE="$SCRIPT_DIR/.deps_installed"

echo "检查运行环境..."

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ 虚拟环境未找到！"
    echo
    echo "请先运行 \"./linux首次启动点我.sh\" 初始化环境"
    echo
    read -p "按任意键退出..."
    exit 1
fi

if [ ! -f "$DEPS_CHECK_FILE" ]; then
    echo "❌ 依赖未安装！"
    echo
    echo "请先运行 \"./linux首次启动点我.sh\" 安装依赖"
    echo
    read -p "按任意键退出..."
    exit 1
fi

echo "✅ 环境检查通过"
echo
echo "启动 MoFox-Core 管理程序..."
echo "========================================"

# 启动mofox-core.py
"$PYTHON_PATH" "$SCRIPT_PATH"
EXIT_CODE=$?

# 如果程序异常退出，显示错误信息
if [ $EXIT_CODE -ne 0 ]; then
    echo
    echo "========================================"
    echo "程序异常退出，错误代码：$EXIT_CODE"
    echo
    echo "如果遇到依赖问题，请重新运行："
    echo "   \"./linux首次启动点我.sh\""
    echo "========================================"
fi

echo
echo "按任意键退出..."
read -n 1 -s