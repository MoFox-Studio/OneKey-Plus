#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mofox 一键管理程序
功能：
1. 启动各种服务（Bot、Adapter、Matcha-Adapter）
2. 管理配置文件
"""

import os
import sys
import io
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class Colors:
    """控制台颜色"""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    LIGHTBLUE = "\033[38;5;117m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @staticmethod
    def red(text):
        return f"{Colors.RED}{text}{Colors.END}"

    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.END}"

    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.END}"

    @staticmethod
    def blue(text):
        return f"{Colors.BLUE}{text}{Colors.END}"

    @staticmethod
    def cyan(text):
        return f"{Colors.CYAN}{text}{Colors.END}"

    @staticmethod
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.END}"

    @staticmethod
    def magenta(text):
        return f"{Colors.MAGENTA}{text}{Colors.END}"


class MaiBotManager:
    def is_bot_initialized(self):
        """判断MoFox_Bot主程序是否已初始化（即core/Bot目录和.git存在）"""
        bot_path = self.base_path / "core" / "Bot"
        git_path = bot_path / ".git"
        return bot_path.exists() and git_path.exists()

    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.python_executable = self.base_path / "python_embedded" / "python.exe"
        self.running_processes: Dict[str, subprocess.Popen] = {}

        self.services = {
            "bot": {
                "name": "MoFox_Bot 主程序",
                "path": self.base_path / "core" / "Bot",
                "main_file": "__main__.py",
                "type": "python",
            },
            "napcat": {
                "name": "Napcat 服务",
                "path": self.base_path / "core" / "Napcat",
                "main_file": "napcat.bat",
                "type": "batch",
            },
            "vscode": {
                "name": "VSCode",
                "path": self.base_path / "core" / "vscode",
                "main_file": "code.exe",
                "type": "exe",
            },
        }

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        print("=" * 60)
        print(Colors.cyan(Colors.bold("          MoFox_Bot 一键管理程序")))
        print(Colors.yellow("              Version 2.4.9"))
        print("=" * 60)
        print(Colors.green("Edited by 阿范 @212898630"))
        print(Colors.green("Ps : 修改版 问题/建议 交流群群号 169850076"))
        print(
            Colors.red(
                "> 请注意！ 这个版本的所有后续更新均为我们的第三方更新，不代表 MaiBot 官方立场"
            )
        )

    def print_menu(self):
        print(Colors.bold("主菜单："))
        print()
        # 显示路径信息
        print(f"  内置Python路径: {Colors.CYAN}{self.python_executable}{Colors.END}")
        print(f"  Bot本体路径: {Colors.CYAN}{self.services['bot']['path']}{Colors.END}")
        print(
            f"  Napcat路径: {Colors.CYAN}{self.services['napcat']['path']}{Colors.END}"
        )
        print(
            f"  GIT路径:{Colors.CYAN}{self.base_path / 'PortableGit' / 'bin' / 'git.exe'}{Colors.END}"
        )
        print("  文档网站:https://docs.mofox-sama.com/")
        print(
            "  一键包使用教程:https://docs.mofox-sama.com/docs/guides/OneKey-Plus-Usage-Guide.html"
        )
        print()
        print(Colors.green("快捷启动服务管理："))
        print("  1. 启动服务组合 →")
        print("  2. 启动 MoFox_Bot 主程序")
        print("  3. 启动 Napcat 服务")
        print("  4. 启动 vscode")
        print("  5. 查看运行状态")
        print("  6. 启动数据库管理程序")
        print()
        print(Colors.yellow("其他功能："))
        print("  7. 安装/更新依赖包")
        print("  8. 查看系统信息")
        print("  9. 切换Bot主程序分支")
        print("  10. 启动知识库学习工具")
        print()
        print(Colors.magenta(" BOT管理："))
        print("  11. 打开配置文件")
        print("  12. 打开数据文件夹")
        print("  13. 打开插件文件夹")
        print(f"  14. {Colors.RED}删除数据库 (请谨慎操作!){Colors.END}")

    def print_service_groups_menu(self):
        print(Colors.bold("选择启动组："))
        print()
        print(Colors.green("  1. 内置适配器组合(推荐使用)"))
        print("     └─ MoFox_Bot主程序(内置适配器) + Napcat服务")
        print("     └─ 用于连接QQ平台")
        print()
        print(Colors.cyan("  0. 返回主菜单"))

    def start_service_group(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_service_groups_menu()

            choice = input(Colors.bold("请选择组合 (0-1): ")).strip()

            if choice == "0":
                return
            elif choice == "1":
                print(Colors.blue("正在启动QQ机器人组合..."))
                print()
                success_count = 0
                services = ["bot", "napcat"]
                for service in services:
                    if self.start_service(service):
                        success_count += 1
                        time.sleep(2)  # 延迟启动避免冲突

                print()
                print(
                    Colors.green(
                        f"✅ QQ机器人组合启动完成 ({success_count}/{len(services)} 个服务成功)"
                    )
                )

            else:
                print(Colors.red("无效选择，请输入 0-1 之间的数字"))

            if choice in ["1"]:
                input("按回车键返回...")
                return

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None, show_output: bool = True
    ) -> tuple:
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=not show_output,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            return result.returncode == 0, result.stdout if not show_output else ""
        except Exception as e:
            print(Colors.red(f"命令执行失败: {e}"))
            return False, str(e)

    def start_service(self, service_key: str):
        if service_key not in self.services:
            print(Colors.red(f"未知服务: {service_key}"))
            return False

        service = self.services[service_key]
        service_path = service["path"]
        main_file = service["main_file"]

        if not (service_path / main_file).exists():
            print(Colors.red(f"主程序文件不存在: {service_path / main_file}"))
            return False

        if (
            service_key in self.running_processes
            and self.running_processes[service_key].poll() is None
        ):
            print(Colors.yellow(f"{service['name']} 已经在运行中"))
            return True

        print(Colors.blue(f"正在启动 {service['name']}..."))

        try:
            service_type = service.get("type", "python")
            service_name = service.get("name", "VScode")

            if service_type == "python":
                powershell_cmd = [
                    "powershell.exe",
                    "-NoExit",
                    "-Command",
                    f"chcp 65001; Set-Location '{service_path}'; & '{self.python_executable}' __main__.py",
                ]
                process = subprocess.Popen(
                    powershell_cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=service_path,
                )
            elif service_type == "batch":
                cmd_command = [
                    "cmd.exe",
                    "/c",
                    "start",
                    "cmd.exe",
                    "/k",
                    f"chcp 65001 && {service_path / main_file}",
                ]
                process = subprocess.Popen(cmd_command, cwd=service_path)
            elif service_type == "exe":
                command = [str(service_path / main_file)]
                if service_name == "VSCode":
                    command.append(" /core/Bot")

                try:
                    process = subprocess.Popen(
                        command,
                        cwd=service_path,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                    )
                except FileNotFoundError:
                    print(
                        f"错误：路径 '{service_path}' 或可执行文件 '{main_file}' 未找到。"
                    )
                except OSError as e:
                    print(f"错误：启动服务 '{service_name}' 时发生操作系统错误：{e}")
                except Exception as e:
                    print(f"错误：启动服务 '{service_name}' 时发生未知错误：{e}")
            else:
                print(Colors.red(f"不支持的服务类型: {service_type}"))
                return False

            self.running_processes[service_key] = process
            print(
                Colors.green(
                    f"✅ {service['name']} 已在新窗口启动 (PID: {process.pid})"
                )
            )
            return True

        except Exception as e:
            print(Colors.red(f"启动 {service['name']} 失败: {e}"))
            return False

    def stop_all_services(self):
        print(Colors.blue("正在停止所有服务..."))
        for service_key, process in self.running_processes.items():
            try:
                process.terminate()
                print(Colors.green(f"✅ 已停止 {self.services[service_key]['name']}"))
            except Exception as e:
                print(
                    Colors.red(f"停止 {self.services[service_key]['name']} 失败: {e}")
                )
        self.running_processes.clear()

    def show_status(self):
        print(Colors.bold("服务运行状态："))
        for service_key, service in self.services.items():
            if process := self.running_processes.get(service_key):
                if process.poll() is None:
                    status = Colors.green("🟢 运行中")
                else:
                    status = Colors.red("🔴 已停止")
                    del self.running_processes[service_key]
            else:
                status = Colors.yellow("⚪ 未启动")
            print(f"  {service['name']}: {status}")

    def start_sqlite_studio(self):
        sqlite_studio_path = (
            self.base_path / "core" / "SQLiteStudio" / "SQLiteStudio.exe"
        )
        db_path = self.base_path / "core" / "Bot" / "data" / "MaiBot.db"

        if not sqlite_studio_path.exists():
            print(Colors.red(f"❌ SQLiteStudio未找到: {sqlite_studio_path}"))
            return

        if not db_path.exists():
            print(
                Colors.red(
                    f"❌ 数据库文件MaiBot.db未找到: {db_path},你可能需要启动一次主程序来生成"
                )
            )
            return

        try:
            print(Colors.blue("正在启动SQLiteStudio并加载数据库..."))
            subprocess.Popen(
                [str(sqlite_studio_path), str(db_path)],
                cwd=str(sqlite_studio_path.parent),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            print(Colors.green("✅ SQLiteStudio已启动"))
        except Exception as e:
            print(Colors.red(f"❌ 启动SQLiteStudio失败: {e}"))

    def install_requirements(self):
        while True:
            self.clear_screen()
            print(Colors.bold("依赖包管理"))
            print("  1. 更新 / 重装 Bot本体依赖")
            print("  3. 更新 / 重装 所有依赖")
            print("  4. 从指定依赖文件安装")
            print("  5. 安装指定依赖包")
            print("  0. 返回主菜单")

            choice = input(Colors.bold("请选择操作 (0-5): ")).strip()

            if choice == "0":
                break
            elif choice == "1":
                self._install_service_requirements("bot")
            elif choice == "3":
                self._install_all_requirements()
            elif choice == "4":
                self._install_from_file()
            elif choice == "5":
                self._install_specific_package()
            else:
                print(Colors.red("无效选择"))
            input("按回车键继续...")

    def _install_service_requirements(self, service_key: str):
        service = self.services[service_key]
        requirements_file = service["path"] / "requirements.txt"
        if not requirements_file.exists():
            print(Colors.yellow(f"{service['name']} 没有 requirements.txt 文件。"))
            return

        print(Colors.blue(f"正在安装 {service['name']} 的依赖..."))

        mirrors = [
            "https://pypi.tuna.tsinghua.edu.cn/simple",
            "https://pypi.doubanio.com/simple/",
            "http://mirrors.aliyun.com/pypi/simple/",
            "https://pypi.mirrors.ustc.edu.cn/simple/",
        ]

        for mirror_url in mirrors:
            print(Colors.cyan(f"正在尝试使用镜像: {mirror_url}"))
            cmd = [
                str(self.python_executable),
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
                "-i",
                mirror_url,
            ]
            success, _ = self.run_command(cmd)
            if success:
                print(Colors.green(f"✅ {service['name']} 依赖安装完成"))
                return
            else:
                print(Colors.red(f"❌ 使用镜像 {mirror_url} 安装失败，尝试下一个..."))

        print(Colors.red(f"❌ {service['name']} 依赖安装失败，所有镜像源均尝试失败。"))

    def _install_all_requirements(self):
        for service_key in self.services:
            if (self.services[service_key]["path"] / "requirements.txt").exists():
                self._install_service_requirements(service_key)
        print(Colors.green("所有依赖安装检查完成"))

    def _install_from_file(self):
        """从指定文件安装依赖"""
        file_path_str = input(
            Colors.bold(
                "请输入依赖文件的路径 (例如: C:\\Users\\YourName\\Desktop\\requirements.txt): "
            )
        ).strip()
        requirements_file = Path(file_path_str)

        if not requirements_file.exists() or not requirements_file.is_file():
            print(Colors.red(f"❌ 文件不存在或不是一个有效文件: {requirements_file}"))
            return

        print(Colors.blue(f"正在从 {requirements_file.name} 安装依赖..."))
        self._execute_pip_install(["-r", str(requirements_file)])

    def _install_specific_package(self):
        """安装指定的Python包"""
        package_names = input(
            Colors.bold("请输入要安装的包名 (多个包请用空格隔开): ")
        ).strip()
        if not package_names:
            print(Colors.yellow("没有输入任何包名。"))
            return

        packages = package_names.split()
        print(Colors.blue(f"准备安装包: {', '.join(packages)}"))
        self._execute_pip_install(packages)

    def _execute_pip_install(self, install_args: List[str]):
        """执行pip install命令，并尝试多个镜像源"""
        mirrors = [
            "https://pypi.tuna.tsinghua.edu.cn/simple",
            "https://pypi.doubanio.com/simple/",
            "http://mirrors.aliyun.com/pypi/simple/",
            "https://pypi.mirrors.ustc.edu.cn/simple/",
        ]

        for mirror_url in mirrors:
            print(Colors.cyan(f"正在尝试使用镜像: {mirror_url}"))
            cmd = (
                [
                    str(self.python_executable),
                    "-m",
                    "pip",
                    "install",
                ]
                + install_args
                + [
                    "-i",
                    mirror_url,
                ]
            )

            success, _ = self.run_command(cmd)
            if success:
                print(Colors.green("✅ 依赖安装成功!"))
                return
            else:
                print(Colors.red(f"❌ 使用镜像 {mirror_url} 安装失败，尝试下一个..."))

        print(Colors.red("❌ 依赖安装失败，所有镜像源均尝试失败。"))

    def open_config_file(self):
        config_files = [
            (
                "Bot 核心配置",
                self.base_path / "core" / "Bot" / "config" / "bot_config.toml",
            ),
            (
                "模型相关配置",
                self.base_path / "core" / "Bot" / "config" / "model_config.toml",
            ),
            (
                "Napcat 适配器配置",
                self.base_path
                / "core"
                / "Bot"
                / "config"
                / "plugins"
                / "napcat_adapter"
                / "config.toml",
            ),
        ]
        while True:
            self.clear_screen()
            print(Colors.bold("打开配置文件"))
            for i, (name, _) in enumerate(config_files, 1):
                print(f"  {i}. 打开 {name}")
            print("  0. 返回主菜单")
            choice = input(Colors.bold(f"请选择 (0-{len(config_files)}): ")).strip()
            if choice == "0":
                break
            try:
                _, path = config_files[int(choice) - 1]
                if path.exists():
                    os.startfile(path)
                    print(Colors.green("✅ 已尝试打开"))
                else:
                    print(Colors.red(f"❌ 配置文件不存在: {path}"))
            except (ValueError, IndexError):
                print(Colors.red("无效选择"))
            input("按回车键继续...")

    def open_data_folder(self):
        """打开数据文件夹"""
        data_path = self.base_path / "core" / "Bot" / "data"
        if data_path.exists():
            os.startfile(data_path)
            print(Colors.green(f"✅ 已尝试打开数据文件夹: {data_path}"))
        else:
            print(Colors.red(f"❌ 数据文件夹不存在: {data_path}"))

    def open_plugin_folder(self):
        """打开插件文件夹"""
        plugin_path = self.base_path / "core" / "Bot" / "plugins"
        if plugin_path.exists():
            os.startfile(plugin_path)
            print(Colors.green(f"✅ 已尝试打开插件文件夹: {plugin_path}"))
        else:
            print(Colors.red(f"❌ 插件文件夹不存在: {plugin_path}"))

    def delete_database(self):
        """删除数据库文件"""
        db_path = self.base_path / "core" / "Bot" / "data" / "MaiBot.db"
        if not db_path.exists():
            print(Colors.yellow(f"数据库文件不存在，无需删除: {db_path}"))
            return

        print(Colors.red(Colors.bold("警告：这是一个危险操作！")))
        confirm = (
            input(
                Colors.yellow(
                    f"你确定要删除数据库文件 '{db_path.name}' 吗？此操作无法撤销！(y/n): "
                )
            )
            .strip()
            .lower()
        )

        if confirm == "y":
            try:
                os.remove(db_path)
                print(Colors.green("✅ 数据库文件已成功删除。"))
            except Exception as e:
                print(Colors.red(f"❌ 删除数据库文件失败: {e}"))
        else:
            print(Colors.cyan("操作已取消。"))

    def switch_bot_branch(self):
        """切换MoFox_Bot主程序分支"""
        if not self.is_bot_initialized():
            print(Colors.red("❌ Bot主程序未初始化，无法切换分支！请先完成初始化。"))
            input("按回车键返回主菜单...")
            return

        config_path = self.base_path / "update_config.json"
        if not config_path.exists():
            print(Colors.red(f"❌ 配置文件 {config_path} 不存在！"))
            input("按回车键返回主菜单...")
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(Colors.red(f"❌ 读取配置文件失败: {e}"))
            input("按回车键返回主菜单...")
            return

        current_branch = config.get("bot", {}).get("branch", "N/A")

        while True:
            self.clear_screen()
            print(Colors.bold("切换MoFox_Bot主程序分支"))
            print(f"当前分支: {Colors.green(current_branch)}")
            print("\n请选择要切换的目标分支:")
            print("  1. master (稳定版)")
            print("  2. dev (开发版)")
            print("\n  0. 返回主菜单")

            choice = input(Colors.bold("请选择操作 (0-2): ")).strip()

            if choice == "0":
                break
            elif choice in ("1", "2"):
                target_branch = "master" if choice == "1" else "dev"
                if target_branch == current_branch:
                    print(Colors.yellow(f"当前已在 {target_branch} 分支，无需切换。"))
                else:
                    config["bot"]["branch"] = target_branch
                    try:
                        # 写回JSON文件，注意路径的处理
                        for service, settings in config.items():
                            if "path" in settings:
                                # 从绝对路径转换回相对路径以便存储
                                settings["path"] = str(
                                    Path(settings["path"]).relative_to(self.base_path)
                                ).replace("\\", "/")

                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)

                        print(Colors.green(f"✅ 分支已设置为 {target_branch}。"))
                        print(
                            Colors.cyan(
                                "下次运行时，请手动执行“启动更新程序.bat”以应用更改。"
                            )
                        )
                        current_branch = target_branch  # 更新显示
                    except Exception as e:
                        print(Colors.red(f"❌ 写入配置文件失败: {e}"))
                input("按回车键继续...")
            else:
                print(Colors.red("无效选择"))
                input("按回车键继续...")

    def show_system_info(self):
        print(Colors.bold("系统信息："))
        try:
            result = subprocess.run(
                [str(self.python_executable), "--version"],
                capture_output=True,
                text=True,
            )
            print(f"  Python版本: {Colors.green(result.stdout.strip())}")
        except Exception:
            print(f"  Python版本: {Colors.red('获取失败')}")
        print(f"  工作目录: {Colors.cyan(str(self.base_path))}")
        python_status = (
            Colors.green("已配置")
            if self.python_executable.exists()
            else Colors.red("未配置")
        )
        print(f"  内置Python环境: {python_status}")

    def start_learning_tool(self):
        """启动知识库学习工具"""
        script_path = (
            self.base_path / "core" / "Bot" / "scripts" / "lpmm_learning_tool.py"
        )
        if not script_path.exists():
            print(Colors.red(f"❌ 学习工具脚本未找到: {script_path}"))
            return

        print(Colors.blue("正在启动知识库学习工具..."))
        try:
            powershell_cmd = [
                "powershell.exe",
                "-NoExit",
                "-Command",
                f"chcp 65001; Set-Location '{script_path.parent}'; & '{self.python_executable}' '{script_path.name}'",
            ]
            subprocess.Popen(
                powershell_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=script_path.parent,
            )
            print(Colors.green("✅ 知识库学习工具已在新窗口启动"))
        except Exception as e:
            print(Colors.red(f"❌ 启动知识库学习工具失败: {e}"))

    def run(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            try:
                choice = input(Colors.bold("请选择操作 (0-11): ")).strip()

                actions = {
                    "1": self.start_service_group,
                    "2": lambda: self.start_service("bot"),
                    "3": lambda: self.start_service("napcat"),
                    "4": lambda: self.start_service("vscode"),
                    "5": self.show_status,
                    "6": self.start_sqlite_studio,
                    "7": self.install_requirements,
                    "8": self.show_system_info,
                    "9": self.switch_bot_branch,
                    "10": self.start_learning_tool,
                    "11": self.open_config_file,
                    "12": self.open_data_folder,
                    "13": self.open_plugin_folder,
                    "14": self.delete_database,
                }

                if choice == "0":
                    print(Colors.green("程序退出"))
                    break

                if action := actions.get(choice):
                    action()
                else:
                    print(Colors.red("无效选择"))

                if choice != "0":
                    input("\n按回车键返回主菜单...")

            except KeyboardInterrupt:
                print(Colors.yellow("\n检测到 Ctrl+C，正在安全退出..."))
                self.stop_all_services()
                break
            except Exception as e:
                print(Colors.red(f"发生错误: {e}"))
                input("按回车键返回主菜单...")


if __name__ == "__main__":
    if os.name == "nt":
        os.system("color")
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

    manager = MaiBotManager()
    manager.run()
