#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mofox 一键管理程序
功能：
1. 启动各种服务（Bot、Adapter、Matcha-Adapter）
2. 更新GitHub仓库
3. 管理配置文件
"""

import os
import sys
import io
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import time
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
import threading

class Colors:
    """控制台颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    LIGHTBLUE = '\033[38;5;117m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def red(text): return f"{Colors.RED}{text}{Colors.END}"
    @staticmethod
    def green(text): return f"{Colors.GREEN}{text}{Colors.END}"
    @staticmethod
    def yellow(text): return f"{Colors.YELLOW}{text}{Colors.END}"
    @staticmethod
    def blue(text): return f"{Colors.BLUE}{text}{Colors.END}"
    @staticmethod
    def cyan(text): return f"{Colors.CYAN}{text}{Colors.END}"
    @staticmethod
    def bold(text): return f"{Colors.BOLD}{text}{Colors.END}"
    @staticmethod
    def magenta(text): return f"{Colors.MAGENTA}{text}{Colors.END}"

class MaiBotManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.python_executable = self.base_path / "python_embedded" / "python.exe"  # 使用内置Python环境
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
        # 服务配置
        self.services = {
            "onekey": {
                "name": "OneKey-Plus 管理程序",
                "path": self.base_path,
                "main_file": "onekey.py",
                "description": "一键管理程序本身",
                "repo_url": "https://github.com/MoFox-Studio/OneKey-Plus.git",
                "type": "python",
                "branch": "Windows"  # 特殊标记，使用Windows分支
            },
            "bot": {
                "name": "MoFox_Bot 主程序",
                "path": self.base_path / "Bot",
                "main_file": "bot.py",
                "description": "AI聊天机器人主程序",
                "repo_url": "https://github.com/MoFox-Studio/MoFox_Bot.git",
                "type": "python"
            },
            "adapter": {
                "name": "Napcat Adapter",
                "path": self.base_path / "Adapter",
                "main_file": "main.py",
                "description": "QQ消息适配器",
                "repo_url": "https://github.com/MoFox-Studio/Napcat-Adapter.git",
                "type": "python"
            },
            "matcha_adapter": {
                "name": "Matcha Adapter",
                "path": self.base_path / "Matcha-Adapter",
                "main_file": "main.py", 
                "description": "Matcha消息适配器",
                "repo_url": "https://github.com/MoFox-Studio/Matcha-Adapter.git",
                "type": "python",
                "branch": "main"   # byd这个分支为什么改名成了main而不是master了，害得我测试的时候炸了一次（恼）
            },
            "napcat": {
                "name": "Napcat 服务",
                "path": self.base_path / "Napcat" / "Shell",
                "main_file": "napcat.bat",
                "description": "QQ协议服务",
                "repo_url": None,
                "type": "batch"
            },
            "matcha": {
                "name": "Matcha 程序",
                "path": self.base_path / "Matcha",
                "main_file": "matcha.exe",
                "description": "Matcha客户端程序",
                "repo_url": None,
                "type": "exe"
            }
        }
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印程序头部"""
        print("=" * 60)
        print(Colors.cyan(Colors.bold("          MoFox_Bot 一键管理程序")))
        print(Colors.yellow("              Version 1.3.2"))
        print("=" * 60)
        print(Colors.green("Edited by 阿范 @212898630"))
        print(Colors.green("Ps : 修改版 问题/建议 交流群群号 169850076"))
        print(Colors.red("> 请注意！ 这个版本的所有后续更新均为我们的第三方更新，不代表 MaiBot 官方立场"))
    
    def check_git_environment(self):
        """检查Git环境"""
        git_path = self._find_git_executable()
        if not git_path:
            print(Colors.red("  警告：未检测到Git，仓库更新功能将不可用"))
            print(Colors.yellow("   请安装Git并确保其在系统PATH中"))
            print(Colors.cyan("   Git下载地址: https://git-scm.com/download/windows"))
            print()
            return False
        else:
            print(Colors.green(f"✅ Git环境正常: {git_path}"))
            return True

    def print_menu(self):
        """打印主菜单"""
        print(Colors.bold("主菜单："))
        print()
        print(Colors.green("快捷启动服务管理："))
        print("  1. 启动服务组合 →")
        print("  2. 启动 MoFox_Bot 主程序")
        print("  3. 启动 Napcat Adapter")
        print("  4. 启动 Napcat 服务")
        print("  5. 启动 Matcha Adapter")
        print("  6. 启动 Matcha 程序")
        print("  7. 查看运行状态")
        print("  8. 启动数据库管理程序")
        print()
        print(Colors.yellow("其他功能："))
        print("  9. 安装/更新依赖包")
        print("  10. 查看系统信息")
        print()
        print(Colors.magenta("配置管理："))
        print("  11. 打开配置文件")
        print("  12. 修改权限设置")
        print("  0. 退出程序")
        print()
    
    def print_service_groups_menu(self):
        """打印服务组合菜单"""
        print(Colors.bold("选择启动组："))
        print()
        print(Colors.green("  1. QQ机器人组合"))
        print("     └─ MoFox_Bot主程序 + Napcat Adapter + Napcat服务")
        print("     └─ 用于连接QQ平台")
        print()
        print(Colors.green("  2. Matcha机器人组合"))  
        print("     └─ MoFox_Bot主程序 + Matcha Adapter + Matcha程序")
        print("     └─ 用于连接Matcha平台")
        print()
        print(Colors.cyan("  0. 返回主菜单"))
    
    def start_service_group(self):
        """启动服务组合"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_service_groups_menu()
            
            choice = input(Colors.bold("请选择组合 (0-2): ")).strip()
            
            if choice == '0':
                return
            elif choice == '1':
                print(Colors.blue("正在启动QQ机器人组合..."))
                print()
                success_count = 0
                services = ['bot', 'adapter', 'napcat']
                for service in services:
                    if self.start_service(service):
                        success_count += 1
                        time.sleep(2)  # 延迟启动避免冲突
                
                print()
                print(Colors.green(f"✅ QQ机器人组合启动完成 ({success_count}/{len(services)} 个服务成功)"))
                
            elif choice == '2':
                print(Colors.blue("正在启动Matcha机器人组合..."))
                print()
                success_count = 0
                services = ['bot', 'matcha_adapter', 'matcha']
                for service in services:
                    if self.start_service(service):
                        success_count += 1
                        time.sleep(2)  # 延迟启动避免冲突
                
                print()
                print(Colors.green(f"✅ Matcha机器人组合启动完成 ({success_count}/{len(services)} 个服务成功)"))
                
            else:
                print(Colors.red("无效选择，请输入 0-2 之间的数字"))
            
            if choice in ['1', '2']:
                print()
                input("按回车键返回...")
                return
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, show_output: bool = True) -> tuple:
        """运行命令"""
        try:
            if cwd:
                result = subprocess.run(
                    cmd, 
                    cwd=cwd, 
                    capture_output=not show_output,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'  # 忽略编码错误
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=not show_output,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'  # 忽略编码错误
                )
            return result.returncode == 0, result.stdout if not show_output else ""
        except Exception as e:
            print(Colors.red(f"命令执行失败: {e}"))
            return False, str(e)
    
    def run_command_with_env(self, cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None, show_output: bool = True) -> tuple:
        """运行命令（支持自定义环境变量）"""
        try:
            # 确保命令存在
            if cmd and len(cmd) > 0:
                command_name = cmd[0]
                # 对于git命令，尝试找到完整路径
                if command_name == 'git':
                    git_path = self._find_git_executable()
                    if git_path:
                        cmd = [git_path] + cmd[1:]
                    else:
                        print(Colors.red("错误：系统中未找到Git，请安装Git并确保其在PATH中"))
                        return False, "Git executable not found"
            
            # 确保工作目录存在且为绝对路径
            if cwd:
                cwd = Path(cwd).resolve()
                if not cwd.exists():
                    print(Colors.red(f"工作目录不存在: {cwd}"))
                    return False, f"Working directory does not exist: {cwd}"
            
            if cwd:
                result = subprocess.run(
                    cmd, 
                    cwd=str(cwd),  # 确保cwd是字符串格式
                    env=env,
                    capture_output=not show_output,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'  # 忽略编码错误
                )
            else:
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=not show_output,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'  # 忽略编码错误
                )
            
            # 返回成功状态和详细信息（包括stdout和stderr）
            if not show_output:
                output_info = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                return result.returncode == 0, output_info
            else:
                return result.returncode == 0, ""
                
        except FileNotFoundError as e:
            error_msg = f"文件未找到: {e}. 命令: {' '.join(cmd)}"
            if cwd:
                error_msg += f", 工作目录: {cwd}"
            print(Colors.red(error_msg))
            return False, error_msg
        except Exception as e:
            error_msg = f"命令执行失败: {e}"
            print(Colors.red(error_msg))
            return False, str(e)

    def _find_git_executable(self) -> Optional[str]:
        """查找Git可执行文件的完整路径"""
        import shutil
        
        # 首先尝试使用shutil.which查找
        git_path = shutil.which('git')
        if git_path:
            return git_path
            
        # 常见的Git安装路径
        common_paths = [
            r"C:\Program Files\Git\bin\git.exe",
            r"C:\Program Files (x86)\Git\bin\git.exe",
            r"C:\Users\{}\AppData\Local\Programs\Git\bin\git.exe".format(os.environ.get('USERNAME', '')),
            r"C:\Git\bin\git.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
        return None
    
    def start_service(self, service_key: str):
        """启动服务"""
        if service_key not in self.services:
            print(Colors.red(f"未知服务: {service_key}"))
            return False
        
        service = self.services[service_key]
        service_path = service["path"]
        main_file = service["main_file"]
        
        if not service_path.exists():
            print(Colors.red(f"服务目录不存在: {service_path}"))
            return False
        
        if not (service_path / main_file).exists():
            print(Colors.red(f"主程序文件不存在: {service_path / main_file}"))
            return False
        
        if service_key in self.running_processes and self.running_processes[service_key].poll() is None:
            print(Colors.yellow(f"{service['name']} 已经在运行中"))
            return True
        
        print(Colors.blue(f"正在启动 {service['name']}..."))
        
        try:
            service_type = service.get("type", "python")
            
            if service_type == "python":
                # Python服务 - 在新的PowerShell窗口中启动
                python_exe = str(self.python_executable).replace('\\', '\\\\')  # 处理反斜杠
                service_path_str = str(service_path).replace('\\', '\\\\')
                
                if main_file == "bot.py":
                    # Bot项目使用__main__.py启动
                    powershell_cmd = [
                        "powershell.exe", "-NoExit", "-Command",
                        f"Set-Location '{service_path_str}'; & '{python_exe}' __main__.py; if ($LASTEXITCODE -ne 0) {{ Write-Host 'Python程序异常退出，错误代码: $LASTEXITCODE' -ForegroundColor Red; Read-Host '按Enter继续' }}"
                    ]
                elif main_file == "main.py":
                    powershell_cmd = [
                        "powershell.exe", "-NoExit", "-Command",
                        f"Set-Location '{service_path_str}'; & '{python_exe}' __main__.py; if ($LASTEXITCODE -ne 0) {{ Write-Host 'Python程序异常退出，错误代码: $LASTEXITCODE' -ForegroundColor Red; Read-Host '按Enter继续' }}"
                    ]
                    """
                    temp_script = service_path / "temp_start.py"
                    script_content = f  # 取消这里的注释需要重新补上三引号，但是应该不需要（因为是不择手段写的）
                    import sys
                    sys.path.insert(0, r'{service_path_str}')
                    exec(open(r'{service_path_str}\\main.py', encoding='utf-8').read())
                    
                    # 写入临时脚本
                    with open(temp_script, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    
                    powershell_cmd = [
                        "powershell.exe", "-NoExit", "-Command",
                        f"Set-Location '{service_path_str}'; & '{python_exe}' temp_start.py; Remove-Item temp_start.py -ErrorAction SilentlyContinue; if ($LASTEXITCODE -ne 0) {{ Write-Host 'Python程序异常退出，错误代码: $LASTEXITCODE' -ForegroundColor Red; Read-Host '按Enter继续' }}"
                    ]
                    # 总之你别问为什么这么写，问就是为了解决启动adapter后一段时间就自动终止的问题不择手段了，总之现在可以正常启动了（）
                    """


                else:
                    # 其他Python文件直接运行
                    powershell_cmd = [
                        "powershell.exe", "-NoExit", "-Command",
                        f"Set-Location '{service_path_str}'; & '{python_exe}' '{main_file}'; if ($LASTEXITCODE -ne 0) {{ Write-Host 'Python程序异常退出，错误代码: $LASTEXITCODE' -ForegroundColor Red; Read-Host '按Enter继续' }}"
                    ]
                
                process = subprocess.Popen(
                    powershell_cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=service_path
                )
                
            elif service_type == "batch":
                # 批处理文件 - 在新的CMD窗口中启动
                batch_path = service_path / main_file
                cmd_command = [
                    "cmd.exe", "/c", "start", "cmd.exe", "/k", str(batch_path)
                ]
                
                process = subprocess.Popen(
                    cmd_command,
                    cwd=service_path
                )
                
            elif service_type == "exe":
                # 可执行文件 - 直接启动
                process = subprocess.Popen(
                    [str(service_path / main_file)],
                    cwd=service_path,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
            else:
                print(Colors.red(f"不支持的服务类型: {service_type}"))
                return False
            
            self.running_processes[service_key] = process
            print(Colors.green(f"✅ {service['name']} 已在新窗口启动 (PID: {process.pid})"))
            
            return True
            
        except Exception as e:
            print(Colors.red(f"启动 {service['name']} 失败: {e}"))
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        if not self.running_processes:
            print(Colors.yellow("没有正在运行的服务"))
            return
        
        print(Colors.blue("正在停止所有服务..."))
        for service_key, process in list(self.running_processes.items()):
            try:
                process.terminate()
                print(Colors.green(f"✅ 已停止 {self.services[service_key]['name']}"))
            except Exception as e:
                print(Colors.red(f"停止 {self.services[service_key]['name']} 失败: {e}"))
        
        self.running_processes.clear()
        print(Colors.green("所有服务已停止"))
    
    def show_status(self):
        """显示运行状态"""
        print(Colors.bold("服务运行状态："))
        print()
        
        for service_key, service in self.services.items():
            if service_key in self.running_processes:
                process = self.running_processes[service_key]
                if process.poll() is None:
                    status = Colors.green("🟢 运行中")
                    pid_info = f"(PID: {process.pid}) - 运行在独立窗口"
                else:
                    status = Colors.red("🔴 已停止")
                    pid_info = ""
                    del self.running_processes[service_key]
            else:
                status = Colors.yellow("⚪ 未启动")
                pid_info = ""
            
            print(f"  {service['name']}: {status} {pid_info}")
        
        if self.running_processes:
            print()
            print(Colors.cyan("提示：服务运行在独立的PowerShell窗口中"))
            print(Colors.cyan("关闭对应窗口即可停止服务"))
        print()
    
    def start_sqlite_studio(self):
        """启动SQLiteStudio数据库管理程序"""
        sqlite_studio_path = self.base_path / "SQLiteStudio" / "SQLiteStudio.exe"
        
        if not sqlite_studio_path.exists():
            print(Colors.red(f"❌ SQLiteStudio未找到: {sqlite_studio_path}"))
            return False
        
        try:
            print(Colors.blue("正在启动SQLiteStudio数据库管理程序..."))
            # 使用subprocess.Popen启动程序，不等待程序结束
            process = subprocess.Popen(
                [str(sqlite_studio_path)],
                cwd=str(sqlite_studio_path.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            print(Colors.green("✅ SQLiteStudio数据库管理程序已启动"))
            print(Colors.cyan("数据库文件位置：Bot/data 目录下"))
            return True
            
        except Exception as e:
            print(Colors.red(f"❌ 启动SQLiteStudio失败: {e}"))
            return False
    
    def _restart_program(self):
        """重启程序"""
        try:
            # 获取当前Python脚本的完整路径
            current_script = str(Path(__file__).resolve())
            python_exe = str(self.python_executable)
            
            print(Colors.green("正在重启程序..."))
            # print(Colors.cyan("注意：其他服务将继续运行，只重启管理程序"))  # 因为不需要这个print输出
            
            # 在新的 PowerShell 窗口中启动程序
            restart_cmd = [
                "powershell.exe", "-NoExit", "-Command",
                f"Set-Location '{self.base_path}'; & '{python_exe}' '{current_script}'"
            ]
            
            subprocess.Popen(
                restart_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=self.base_path
            )
            
            # 退出当前程序
            print(Colors.green("✅ 新程序窗口已启动，当前程序即将退出"))
            time.sleep(1)
            sys.exit(0)
            
        except Exception as e:
            print(Colors.red(f"❌ 程序重启失败: {e}"))
            print(Colors.yellow("请手动重启程序以应用更新"))
    
    def open_config_file(self):
        """打开配置文件"""
        config_files = [
            ("Bot 核心配置", self.base_path / "Bot" / "config" / "bot_config.toml"),
            ("模型相关配置", self.base_path / "Bot" / "config" / "model_config.toml"),
            ("Adapter 权限配置", self.base_path / "Adapter" / "config" / "features.toml"),
        ]

        while True:
            self.clear_screen()
            print(Colors.bold("打开配置文件"))
            print("=" * 50)
            for i, (name, path) in enumerate(config_files, 1):
                print(f"  {i}. 打开 {name}")
            print()
            print(Colors.cyan("  0. 返回主菜单"))
            print()

            choice = input(Colors.bold(f"请选择要打开的配置文件 (0-{len(config_files)}): ")).strip()

            if choice == '0':
                break
            
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(config_files):
                    name, path = config_files[choice_index]
                    if path.exists():
                        try:
                            os.startfile(path)
                            print(Colors.green(f"✅ 已尝试使用默认程序打开 {name}"))
                        except Exception as e:
                            print(Colors.red(f"❌ 打开文件失败: {e}"))
                    else:
                        print(Colors.red(f"❌ 配置文件不存在: {path}"))
                else:
                    print(Colors.red("无效选择"))
            except ValueError:
                print(Colors.red("无效输入，请输入数字"))

            input(Colors.blue("按回车键继续..."))

    def modify_permission_settings(self):
        """修改权限设置"""
        config_file = self.base_path / "Adapter" / "config" / "features.toml"
        if not config_file.exists():
            print(Colors.red(f"❌ 配置文件不存在: {config_file}"))
            input(Colors.blue("按回车键继续..."))
            return

        try:
            import tomlkit
        except ImportError:
            print(Colors.red("❌ tomlkit 库未安装，请先安装依赖"))
            input(Colors.blue("按回车键继续..."))
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = tomlkit.load(f)
        except Exception as e:
            print(Colors.red(f"❌ 读取配置文件失败: {e}"))
            input(Colors.blue("按回车键继续..."))
            return

        while True:
            self.clear_screen()
            print(Colors.bold("修改权限设置"))
            print("=" * 50)
            
            group_list_type = config.get("group_list_type", "whitelist")
            group_list = config.get("group_list", [])
            private_list_type = config.get("private_list_type", "whitelist")
            private_list = config.get("private_list", [])
            ban_user_list = config.get("ban_user_id", [])

            print(f"群聊模式: {Colors.green(group_list_type)} ({'白名单' if group_list_type == 'whitelist' else '黑名单'})")
            print(f"群聊列表: {Colors.cyan(str(group_list))}")
            print(f"私聊模式: {Colors.green(private_list_type)} ({'白名单' if private_list_type == 'whitelist' else '黑名单'})")
            print(f"私聊列表: {Colors.cyan(str(private_list))}")
            print(f"全局禁止列表: {Colors.red(str(ban_user_list))}")
            print("-" * 50)
            print("  1. 切换群聊模式 (白名单/黑名单)")
            print("  2. 添加群号到列表")
            print("  3. 从列表删除群号")
            print("  4. 切换私聊模式 (白名单/黑名单)")
            print("  5. 添加QQ号到列表")
            print("  6. 从列表删除QQ号")
            print("  7. 添加QQ号到全局禁止列表")
            print("  8. 从全局禁止列表删除QQ号")
            print("  9. 保存并退出")
            print()
            print(Colors.cyan("  0. 放弃修改并退出"))
            print()

            choice = input(Colors.bold("请选择操作 (0-9): ")).strip()

            if choice == '0':
                break
            elif choice == '1':
                config["group_list_type"] = "blacklist" if group_list_type == "whitelist" else "whitelist"
            elif choice == '2':
                new_id = input("输入要添加的群号: ").strip()
                if new_id.isdigit():
                    config["group_list"].append(int(new_id))
            elif choice == '3':
                del_id = input("输入要删除的群号: ").strip()
                if del_id.isdigit() and int(del_id) in config["group_list"]:
                    config["group_list"].remove(int(del_id))
            elif choice == '4':
                config["private_list_type"] = "blacklist" if private_list_type == "whitelist" else "whitelist"
            elif choice == '5':
                new_id = input("输入要添加的QQ号: ").strip()
                if new_id.isdigit():
                    config["private_list"].append(int(new_id))
            elif choice == '6':
                del_id = input("输入要删除的QQ号: ").strip()
                if del_id.isdigit() and int(del_id) in config["private_list"]:
                    config["private_list"].remove(int(del_id))
            elif choice == '7':
                new_id = input("输入要添加到全局禁止列表的QQ号: ").strip()
                if new_id.isdigit():
                    if "ban_user_id" not in config:
                        config["ban_user_id"] = []
                    config["ban_user_id"].append(int(new_id))
            elif choice == '8':
                del_id = input("输入要从全局禁止列表删除的QQ号: ").strip()
                if del_id.isdigit() and int(del_id) in config.get("ban_user_id", []):
                    config["ban_user_id"].remove(int(del_id))
            elif choice == '9':
                try:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        tomlkit.dump(config, f)
                    print(Colors.green("✅ 配置已保存"))
                except Exception as e:
                    print(Colors.red(f"❌ 保存配置文件失败: {e}"))
                break
            else:
                print(Colors.red("无效选择"))
            
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                print(Colors.green("设置已更新，请记得保存！"))
                time.sleep(1)

    def show_system_info(self):
        """显示系统信息"""
        print(Colors.bold("系统信息："))
        print()
        
        # Python版本
        try:
            result = subprocess.run([str(self.python_executable), '--version'], 
                                  capture_output=True, text=True, encoding='utf-8', errors='ignore')
            python_version = result.stdout.strip()
            print(f"  Python版本: {Colors.green(python_version)}")
        except:
            print(f"  Python版本: {Colors.red('获取失败')}")
        
        # 工作目录
        print(f"  工作目录: {Colors.cyan(str(self.base_path))}")
        
        # 内置Python环境
        python_status = Colors.green("已配置") if self.python_executable.exists() else Colors.red("未配置")
        print(f"  内置Python环境: {python_status}")
        
        # 仓库状态
        print(f"  仓库状态:")
        for service_key, service in self.services.items():
            repo_exists = service["path"].exists()
            status = Colors.green("存在") if repo_exists else Colors.red("不存在")
            print(f"    {service['name']}: {status}")
        
        print()
    def run(self):
        """运行主程序"""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_menu()
                
                try:
                    choice = input(Colors.bold("请选择操作 (0-21): ")).strip()

                    if choice == '0':
                        print(Colors.green("程序退出"))
                        break
                    elif choice == '1':
                        self.start_service_group()
                    elif choice == '2':
                        self.start_service('bot')
                    elif choice == '3':
                        self.start_service('adapter')
                    elif choice == '4':
                        self.start_service('napcat')
                    elif choice == '5':
                        self.start_service('matcha_adapter')
                    elif choice == '6':
                        self.start_service('matcha')
                    elif choice == '7':
                        self.show_status()
                    elif choice == '8':
                        self.start_sqlite_studio()
                    elif choice == '9':
                        self.update_repository('bot')
                    elif choice == '10':
                        self.update_repository('adapter')
                    elif choice == '11':
                        self.update_repository('matcha_adapter')
                    elif choice == '12':
                        self.update_repository('onekey')
                    elif choice == '13':
                        print(Colors.blue("正在更新所有仓库..."))
                        
                        # 定义更新顺序：onekey放在最后，避免过早重启
                        services_to_update = ['bot', 'adapter', 'matcha_adapter', 'onekey']
                        available_services = [key for key in services_to_update if self.services[key].get("repo_url")]
                        
                        if 'onekey' in available_services:
                            # 如果包含onekey更新，询问用户是否继续
                            print()
                            print(Colors.yellow("⚠️  注意：更新包含 OneKey-Plus 管理程序"))
                            print(Colors.yellow("   OneKey-Plus 将在其他仓库更新完成后最后更新"))
                            print(Colors.yellow("   程序将在所有更新完成后自动重启"))
                            print()
                            confirm = input(Colors.bold("是否继续更新所有仓库？(y/N): ")).strip().lower()
                            
                            if confirm not in ['y', 'yes']:
                                print(Colors.blue("取消更新"))
                                continue
                        
                        # 执行更新 - onekey已经在列表最后，会最后更新
                        for service_key in available_services:
                            if service_key == 'onekey':
                                print()
                                print(Colors.yellow("=" * 50))
                                print(Colors.yellow("最后更新 OneKey-Plus 管理程序..."))
                                print(Colors.yellow("=" * 50))
                            
                            self.update_repository(service_key)
                            # 如果更新了onekey，程序已经重启，不会执行到这里
                    elif choice == '14':
                        self.install_requirements()
                    elif choice == '15':
                        self.show_system_info()
                    elif choice == '16':
                        self.open_config_file()
                    elif choice == '17':
                        self.modify_permission_settings()
                    elif choice == '18':
                        self.check_repository_status('bot')
                    elif choice == '19':
                        self.check_repository_status('adapter')
                    elif choice == '20':
                        self.check_repository_status('matcha_adapter')
                    elif choice == '21':
                        self.check_repository_status('onekey')
                    else:
                        print(Colors.red("无效选择，请输入 0-21 之间的数字"))
                    
                    if choice != '0':
                        print()
                        input("按回车键返回主菜单...")
                
                except KeyboardInterrupt:
                    print(Colors.yellow("\n检测到 Ctrl+C，正在安全退出..."))
                    self.stop_all_services()
                    break
                except Exception as e:
                    print(Colors.red(f"发生错误: {e}"))
                    input("按回车键返回主菜单...")
        
        except Exception as e:
            print(Colors.red(f"程序发生致命错误: {e}"))
            self.stop_all_services()

if __name__ == "__main__":
    # 设置控制台支持ANSI颜色（Windows）
    if os.name == 'nt':
        os.system('color')
        # 尝试启用ANSI转义序列支持
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    manager = MaiBotManager()
    print("正在检查运行环境...")
    manager.check_git_environment()
    print()
    manager.run()
