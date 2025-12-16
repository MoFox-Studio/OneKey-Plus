#!/usr/bin/env bash

# 设置UTF-8编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       MoFox-Core 首次启动配置${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo "本程序将为您完成以下操作："
echo "  1. 检查并安装系统依赖 (Python3, Git)"
echo "  2. 拉取/更新 MoFox-Core 主程序"
echo "  3. 创建 Python 虚拟环境"
echo "  4. 安装项目依赖包"
echo "  5. 初始化运行环境"
echo
echo -e "${YELLOW}注意：安装系统依赖可能需要管理员权限 (sudo)${NC}"
echo

# 检查是否在压缩包中运行
if [[ "$(pwd)" =~ "temp" ]] || [[ "$(pwd)" =~ "tmp" ]]; then
    echo -e "${RED}检测到在压缩包中运行！请解压后运行。${NC}"
    exit 1
fi

# --- 步骤 1: 检查并安装系统依赖 ---
echo -e "${GREEN}步骤 1: 检查系统依赖...${NC}"

install_packages() {
    # 检查权限
    if [ "$EUID" -ne 0 ] && ! command -v sudo &> /dev/null; then
        echo -e "${RED}错误: 需要 root 权限或 sudo 来安装系统依赖。${NC}"
        return 1
    fi

    if command -v apt-get &> /dev/null; then
        echo "检测到 Debian/Ubuntu 系统，正在安装依赖..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git
    elif command -v yum &> /dev/null; then
        echo "检测到 CentOS/RHEL 系统，正在安装依赖..."
        sudo yum install -y python3 python3-pip git
    elif command -v dnf &> /dev/null; then
        echo "检测到 Fedora 系统，正在安装依赖..."
        sudo dnf install -y python3 python3-pip git
    elif command -v pacman &> /dev/null; then
        echo "检测到 Arch Linux 系统，正在安装依赖..."
        sudo pacman -S --noconfirm python python-pip git
    else
        echo -e "${RED}未检测到支持的包管理器，请手动安装 python3, python3-venv, git${NC}"
        return 1
    fi
}

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}未找到 Python3，尝试安装...${NC}"
    install_packages
else
    echo -e "✅ Python3 已安装"
fi

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}未找到 Git，尝试安装...${NC}"
    install_packages
else
    echo -e "✅ Git 已安装"
fi

# 再次检查
if ! command -v python3 &> /dev/null || ! command -v git &> /dev/null; then
    echo -e "${RED}依赖安装失败，请手动安装 Python3 和 Git 后重试。${NC}"
    exit 1
fi

# --- 步骤 2: 拉取/更新主程序 ---
echo
echo -e "${GREEN}步骤 2: 拉取 MoFox-Core 主程序...${NC}"

REPO_URL="https://github.com/MoFox-Studio/MoFox-Core.git"
TARGET_DIR="Bot"

if [ -d "$TARGET_DIR" ]; then
    echo "检测到 Bot 目录已存在，尝试更新..."
    cd "$TARGET_DIR"
    if [ -d ".git" ]; then
        git pull
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 更新成功${NC}"
        else
            echo -e "${RED}❌ 更新失败，请检查网络或手动解决冲突${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Bot 目录存在但不是 Git 仓库，跳过更新${NC}"
    fi
    cd "$SCRIPT_DIR"
else
    echo "正在克隆仓库..."
    git clone "$REPO_URL" "$TARGET_DIR"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 克隆成功${NC}"
    else
        echo -e "${RED}❌ 克隆失败！${NC}"
        echo -e "${YELLOW}可能的原因：${NC}"
        echo "  1. 网络连接问题 (GitHub 访问受限)"
        echo "  2. 目标目录没有写入权限"
        echo -e "${YELLOW}建议：${NC}"
        echo "  - 检查网络或配置代理"
        echo "  - 尝试手动克隆: git clone $REPO_URL $TARGET_DIR"
        exit 1
    fi
fi

# --- 步骤 3: 创建虚拟环境 ---
echo
echo -e "${GREEN}步骤 3: 创建虚拟环境...${NC}"

# 删除旧的虚拟环境
if [ -d ".venv" ]; then
    echo "清理旧的虚拟环境..."
    rm -rf ".venv"
fi

python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 虚拟环境创建失败！请尝试安装 python3-venv (如: sudo apt install python3-venv)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"

# --- 步骤 4: 安装依赖 ---
echo
echo -e "${GREEN}步骤 4: 安装依赖包...${NC}"

VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
VENV_PIP="$SCRIPT_DIR/.venv/bin/pip"

# 升级 pip
"$VENV_PYTHON" -m pip install --upgrade pip

if [ -f "Bot/requirements.txt" ]; then
    echo "正在安装 Bot 依赖..."
    "$VENV_PIP" install -r Bot/requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 依赖安装成功${NC}"
    else
        echo -e "${RED}❌ 依赖安装失败${NC}"
        echo -e "${YELLOW}建议：${NC}"
        echo "  - 检查网络连接"
        echo "  - 尝试更换 pip 源 (例如使用清华源)"
        echo "  - 手动运行: $VENV_PIP install -r Bot/requirements.txt"
    fi
else
    echo -e "${YELLOW}⚠️ 未找到 Bot/requirements.txt，跳过依赖安装${NC}"
fi

# 标记安装完成
echo "Initialized on $(date)" > ".deps_installed"

# --- 步骤 5: 启动 ---
echo
echo -e "${GREEN}步骤 5: 启动管理程序...${NC}"
echo

if [ -f "mofox-core.py" ]; then
    "$VENV_PYTHON" mofox-core.py
else
    echo -e "${RED}❌ 错误：找不到 mofox-core.py 主程序文件！${NC}"
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   MoFox-Core 环境配置完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo "下次请直接运行 ./linux启动点我.sh"
echo
read -p "按任意键退出..."
