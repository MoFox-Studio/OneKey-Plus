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
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
import threading

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
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.python_executable = self.base_path / "python_embedded" / "python.exe"
        self.running_processes: Dict[str, subprocess.Popen] = {}

        self.services = {
            "bot": {
                "name": "MoFox_Bot 主程序",
                "path": self.base_path/ "core" / "Bot",
                "main_file": "__main__.py",
                "type": "python",
            },
            "napcat": {
                "name": "Napcat 服务",
                "path": self.base_path / "core" / "Napcat" / "Shell",
                "main_file": "napcat.bat",
                "type": "batch",
            },
        }

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        print("=" * 60)
        print(Colors.cyan(Colors.bold("          MoFox_Bot 一键管理程序")))
        print(Colors.yellow("              Version 2.0"))
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
        print(Colors.green("快捷启动服务管理："))
        print("  1. 启动服务组合 →")
        print("  2. 启动 MoFox_Bot 主程序")
        print("  3. 启动 Napcat 服务")
        print("  5. 查看运行状态")
        print("  6. 启动数据库管理程序")
        print()
        print(Colors.yellow("其他功能："))
        print("  7. 安装/更新依赖包")
        print("  8. 查看系统信息")
        print("  11. 启动知识库学习工具")
        print()
        print(Colors.magenta("配置管理："))
        print("  9. 打开配置文件")
        print("  10. 修改权限设置")
        print()
        print("  0. 退出程序")
        print()

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
                process = subprocess.Popen(
                    [str(service_path / main_file)],
                    cwd=service_path,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
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
        sqlite_studio_path = self.base_path / "SQLiteStudio" / "SQLiteStudio.exe"
        if not sqlite_studio_path.exists():
            print(Colors.red(f"❌ SQLiteStudio未找到: {sqlite_studio_path}"))
            return

        try:
            print(Colors.blue("正在启动SQLiteStudio..."))
            subprocess.Popen(
                [str(sqlite_studio_path)],
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
            print("  0. 返回主菜单")

            choice = input(Colors.bold("请选择操作 (0-3): ")).strip()

            if choice == "0":
                break
            elif choice == "1":
                self._install_service_requirements("bot")
            elif choice == "3":
                self._install_all_requirements()
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

    def open_config_file(self):
        config_files = [
            ("Bot 核心配置", self.base_path / "core" / "Bot" / "config" / "bot_config.toml"),
            ("模型相关配置", self.base_path / "core" / "Bot" / "config" / "model_config.toml"),
            (
                "Napcat 适配器配置",
                self.base_path / "core" / "Bot" / "config" / "plugins" / "napcat_adapter" / "config.toml",
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
                    print(Colors.green(f"✅ 已尝试打开"))
                else:
                    print(Colors.red(f"❌ 配置文件不存在: {path}"))
            except (ValueError, IndexError):
                print(Colors.red("无效选择"))
            input("按回车键继续...")

    def modify_permission_settings(self):
        # This function requires tomlkit, which is not a standard library.
        # For simplicity, this is left as an exercise for the user to implement if needed.
        print(Colors.yellow("此功能需要 `tomlkit` 库，请按需实现。"))
        pass

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
        script_path = self.base_path / "core" / "Bot" / "scripts" / "lpmm_learning_tool.py"
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
                choice = input(Colors.bold("请选择操作 (0-12): ")).strip()

                actions = {
                    "1": self.start_service_group,
                    "2": lambda: self.start_service("bot"),
                    "3": lambda: self.start_service("napcat"),
                    "5": self.show_status,
                    "6": self.start_sqlite_studio,
                    "7": self.install_requirements,
                    "8": self.show_system_info,
                    "9": self.open_config_file,
                    "10": self.modify_permission_settings,
                    "11": self.start_learning_tool,
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
