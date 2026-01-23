# -*- coding: utf-8 -*-
"""
MoFox-Bot WebUI 自动安装脚本
自动从 GitHub 克隆 WebUI 预编译版本，生成随机 API Key，并配置到 bot_config.toml
"""
import tomlkit
import os
import subprocess
import secrets
import uuid
from collections.abc import MutableMapping

# --- 路径定义 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 修改为上级目录
BOT_CONFIG_PATH = os.path.join(BASE_DIR, "core", "Bot", "config", "bot_config.toml")
PLUGINS_DIR = os.path.join(BASE_DIR, "core", "Bot", "src", "plugins")
WEBUI_PLUGIN_DIR = os.path.join(PLUGINS_DIR, "webui_backend")
GIT_REPO_URL = "https://github.com/MoFox-Studio/MoFox-Core-Webui.git"
WEBUI_BRANCH = "webui-dist"

# OneKey-Plus 预置工具路径
PORTABLE_GIT_DIR = os.path.join(BASE_DIR, "PortableGit")
PORTABLE_GIT_CMD = os.path.join(PORTABLE_GIT_DIR, "bin", "git.exe")
PYTHON_EMBEDDED_DIR = os.path.join(BASE_DIR, "python_embedded")
PYTHON_EMBEDDED_EXE = os.path.join(PYTHON_EMBEDDED_DIR, "python.exe")


def print_header(text):
    """打印带装饰的标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_section(text):
    """打印小节标题"""
    print(f"\n--- {text} ---")


def print_success(text):
    """打印成功消息"""
    print(f"✅ {text}")


def print_info(text):
    """打印提示信息"""
    print(f"💡 {text}")


def print_error(text):
    """打印错误信息"""
    print(f"❌ {text}")


def print_warning(text):
    """打印警告信息"""
    print(f"⚠️  {text}")


def get_git_command():
    """获取 Git 命令路径，优先使用预置版本"""
    # 1. 优先使用 OneKey-Plus 预置的 Git
    if os.path.exists(PORTABLE_GIT_CMD):
        return PORTABLE_GIT_CMD
    
    # 2. 回退到系统 Git
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True
        )
        return "git"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def check_git_installed():
    """检查 Git 是否已安装"""
    print_section("检查 Git 环境")
    
    git_cmd = get_git_command()
    
    if git_cmd is None:
        print_error("未检测到 Git！")
        print_info("OneKey-Plus 预置的 Git 不存在，且系统也未安装 Git")
        print_info("请确保 PortableGit 目录完整，或安装系统 Git: https://git-scm.com/")
        return False
    
    try:
        result = subprocess.run(
            [git_cmd, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        if git_cmd == PORTABLE_GIT_CMD:
            print_success(f"使用 OneKey-Plus 预置 Git: {result.stdout.strip()}")
        else:
            print_success(f"使用系统 Git: {result.stdout.strip()}")
        return True
    except Exception as e:
        print_error(f"Git 检查失败: {e}")
        return False


def check_webui_exists():
    """检查 WebUI 插件是否已存在"""
    if os.path.exists(WEBUI_PLUGIN_DIR):
        print_warning(f"检测到 WebUI 插件已存在于: {WEBUI_PLUGIN_DIR}")
        choice = input("是否要重新安装？这将删除现有目录并重新克隆 (yes/no): ").strip().lower()
        if choice in ["yes", "y"]:
            print_info("正在删除现有 WebUI 目录...")
            try:
                # Windows 兼容的删除方式
                if os.name == 'nt':
                    subprocess.run(
                        ["rmdir", "/s", "/q", WEBUI_PLUGIN_DIR],
                        shell=True,
                        check=True
                    )
                else:
                    subprocess.run(
                        ["rm", "-rf", WEBUI_PLUGIN_DIR],
                        check=True
                    )
                print_success("旧目录已删除")
                return False
            except subprocess.CalledProcessError as e:
                print_error(f"删除失败: {e}")
                return True
        else:
            print_info("保留现有安装，将继续配置 API Key")
            return True
    return False


def clone_webui_repository():
    """克隆 WebUI 预编译版本"""
    print_section("克隆 WebUI 仓库")
    print_info("正在从 GitHub 克隆预编译版本...")
    print_info(f"仓库: {GIT_REPO_URL}")
    print_info(f"分支: {WEBUI_BRANCH}")
    
    git_cmd = get_git_command()
    if git_cmd is None:
        print_error("无法找到 Git 命令")
        return False
    
    try:
        # 确保插件目录存在
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        
        # 克隆仓库
        subprocess.run(
            [
                git_cmd, "clone",
                "-b", WEBUI_BRANCH,
                "--single-branch",
                "--depth", "1",  # 浅克隆，节省时间和空间
                GIT_REPO_URL,
                WEBUI_PLUGIN_DIR
            ],
            check=True,
            cwd=PLUGINS_DIR
        )
        print_success("WebUI 克隆成功！")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"克隆失败: {e}")
        print_info("请检查网络连接或访问 GitHub 的权限")
        return False


def generate_api_key():
    """生成随机 API Key"""
    print_section("生成 API Key")
    
    # 提供两种生成方式
    print("选择 API Key 生成方式：")
    print("1. UUID 格式 (推荐，易于识别)")
    print("2. 随机十六进制 (更安全)")
    
    choice = input("请选择 (1/2) [默认: 1]: ").strip() or "1"
    
    if choice == "2":
        # 生成64字符的随机十六进制字符串
        api_key = secrets.token_hex(32)
        print_info("使用随机十六进制格式")
    else:
        # 生成 UUID 格式
        api_key = str(uuid.uuid4())
        print_info("使用 UUID 格式")
    
    print_success(f"生成的 API Key: {api_key}")
    print_warning("请妥善保存此密钥！它将用于登录 WebUI！")
    
    return api_key


def configure_bot_config(api_key):
    """配置 bot_config.toml，添加 API Key"""
    print_section("配置 bot_config.toml")
    
    try:
        # 检查配置文件是否存在
        if not os.path.exists(BOT_CONFIG_PATH):
            print_error(f"找不到配置文件: {BOT_CONFIG_PATH}")
            return False
        
        # 读取配置文件
        with open(BOT_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = tomlkit.load(f)
        
        # 确保 plugin_http_system 部分存在
        if "plugin_http_system" not in config:
            print_info("配置文件中不存在 [plugin_http_system] 部分，正在创建...")
            config["plugin_http_system"] = tomlkit.table()
        
        plugin_http = config["plugin_http_system"]
        
        # 确保类型正确
        if not isinstance(plugin_http, MutableMapping):
            print_error("配置文件格式错误: [plugin_http_system] 不是有效的配置节")
            return False
        
        # 启用 HTTP 端点
        if "enable_plugin_http_endpoints" not in plugin_http:
            plugin_http["enable_plugin_http_endpoints"] = True
            print_info("已启用插件 HTTP 端点功能")
        elif not plugin_http.get("enable_plugin_http_endpoints"):
            plugin_http["enable_plugin_http_endpoints"] = True
            print_info("已将 enable_plugin_http_endpoints 设置为 true")
        else:
            print_success("HTTP 端点功能已启用")
        
        # 配置 API Key
        if "plugin_api_valid_keys" not in plugin_http:
            plugin_http["plugin_api_valid_keys"] = tomlkit.array()
        
        api_keys = plugin_http["plugin_api_valid_keys"]
        
        # 检查是否已有密钥
        if api_keys and len(api_keys) > 0:
            print_warning(f"检测到已有 {len(api_keys)} 个 API Key")
            choice = input("是否要添加新的 API Key？(yes/no) [默认: yes]: ").strip().lower() or "yes"
            if choice not in ["yes", "y"]:
                print_info("保留现有配置")
                return True
        
        # 添加新密钥
        if api_key not in api_keys:
            api_keys.append(api_key)
            print_success("已添加 API Key 到配置文件")
        else:
            print_info("该 API Key 已存在于配置中")
        
        # 配置速率限制（如果不存在）
        if "plugin_api_rate_limit_enable" not in plugin_http:
            plugin_http["plugin_api_rate_limit_enable"] = True
            plugin_http["plugin_api_rate_limit_default"] = "100/minute"
            print_info("已配置 API 速率限制")
        
        # 保存配置
        with open(BOT_CONFIG_PATH, "w", encoding="utf-8") as f:
            tomlkit.dump(config, f)
        
        print_success("配置文件已更新！")
        return True
        
    except FileNotFoundError:
        print_error(f"配置文件不存在: {BOT_CONFIG_PATH}")
        return False
    except Exception as e:
        print_error(f"配置过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_completion_info(api_key):
    """显示安装完成信息"""
    print_header("🎉 WebUI 安装完成！")
    
    print("📝 重要信息：")
    print(f"   WebUI 安装位置: {WEBUI_PLUGIN_DIR}")
    print(f"   配置文件位置: {BOT_CONFIG_PATH}")
    print()
    
    print("🔑 登录凭据：")
    print(f"   API Key: {api_key}")
    print()
    
    print("🚀 接下来的步骤：")
    print("   1. 启动或重启 MoFox-Bot 主程序")
    print("   2. 等待程序完全启动（确认 WebUI 插件已加载）")
    print("   3. 打开浏览器，访问: http://localhost:12138")
    print("   4. 使用上面的 API Key 登录")
    print()
    
    print("💡 提示：")
    print("   - 如果端口 12138 被占用，请检查 WebUI 插件配置")
    print("   - 登录后可以在「更新管理」中一键更新 WebUI 和主程序")
    print("   - 完整使用指南: https://docs.mofox-sama.com/docs/guides/webui_guide.html")
    print()
    
    print("🔐 安全建议：")
    print("   - 请妥善保管 API Key，不要泄露给他人")
    print("   - 如需远程访问，请配置防火墙和使用 HTTPS")
    print("   - 可在配置文件中添加多个 API Key 供不同用户使用")
    print()


def save_api_key_to_file(api_key):
    """将 API Key 保存到本地文件（可选）"""
    print_section("保存 API Key")
    choice = input("是否将 API Key 保存到本地文件？(yes/no) [默认: no]: ").strip().lower() or "no"
    
    if choice in ["yes", "y"]:
        key_file_path = os.path.join(BASE_DIR, "webui_api_key.txt")
        try:
            with open(key_file_path, "w", encoding="utf-8") as f:
                f.write(f"MoFox-Bot WebUI API Key\n")
                f.write(f"生成时间: {__import__('datetime').datetime.now()}\n")
                f.write(f"\n{api_key}\n")
            print_success(f"API Key 已保存到: {key_file_path}")
            print_warning("请注意文件安全，不要将其上传到公开仓库！")
        except Exception as e:
            print_error(f"保存失败: {e}")
    else:
        print_info("未保存到文件，请自行记录 API Key")


def main():
    """主函数"""
    print_header("MoFox-Bot WebUI 自动安装向导")
    print("这个脚本将帮助你：")
    print("  ✓ 自动从 GitHub 克隆 WebUI 预编译版本")
    print("  ✓ 生成安全的随机 API Key")
    print("  ✓ 自动配置 bot_config.toml")
    print("  ✓ 让你能立即使用可视化管理界面")
    print()
    
    input("按 Enter 键开始安装...")
    
    # 1. 检查 Git
    if not check_git_installed():
        print_error("安装终止：缺少 Git 环境")
        input("\n按 Enter 键退出...")
        return
    
    # 2. 检查是否已安装
    webui_exists = check_webui_exists()
    
    # 3. 克隆仓库（如果需要）
    if not webui_exists:
        if not clone_webui_repository():
            print_error("安装失败：无法克隆 WebUI 仓库")
            input("\n按 Enter 键退出...")
            return
    
    # 4. 生成 API Key
    api_key = generate_api_key()
    
    # 5. 配置 bot_config.toml
    if not configure_bot_config(api_key):
        print_error("配置失败：无法更新 bot_config.toml")
        input("\n按 Enter 键退出...")
        return
    
    # 6. 可选：保存 API Key 到文件
    save_api_key_to_file(api_key)
    
    # 7. 显示完成信息
    show_completion_info(api_key)
    
    print("=" * 60)
    print("安装向导完成！祝你使用愉快 😊")
    print("=" * 60)
    
    input("\n按 Enter 键退出...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，安装已取消。")
        input("按 Enter 键退出...")
    except Exception as e:
        print_error(f"发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
