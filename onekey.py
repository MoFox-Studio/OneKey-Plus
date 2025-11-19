#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaiBot-Plus 一键管理程序
功能：
1. 启动各种服务（Bot、Adapter、Matcha-Adapter）
2. 更新GitHub仓库
3. 管理配置文件
"""

import os
import sys
import subprocess
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

class MaiBotManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.python_executable = self.base_path / "python_embedded" / "python.exe"  # 使用内置Python环境
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
        # 服务配置
        self.services = {
            "bot": {
                "name": "MoFox_Bot 主程序",
                "path": self.base_path / "Bot",
                "main_file": "bot.py",
                "description": "AI聊天机器人主程序",
                "repo_url": "https://github.com/MoFox-Studio/MoFox-Core.git",
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
                "type": "python"
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
        print(Colors.blue("更新管理："))
        print("  9. 更新 MoFox_Bot 仓库")
        print("  10. 更新 Napcat-Adapter 仓库")
        print("  11. 更新 Matcha-Adapter 仓库")
        print("  12. 更新所有仓库")
        print()
        print(Colors.yellow("其他功能："))
        print("  13. 安装/更新依赖包")
        print("  14. 查看系统信息")
        print()
        print(Colors.yellow("仓库状态检查："))
        print("  15. 检查 MoFox_Bot 仓库状态")
        print("  16. 检查 Napcat-Adapter 仓库状态")
        print("  17. 检查 Matcha-Adapter 仓库状态")
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
    
    def update_repository(self, service_key: str):
        """更新仓库"""
        # 首先检查Git环境
        if not self._find_git_executable():
            print(Colors.red("❌ Git未安装或不在系统PATH中"))
            print(Colors.yellow("解决方案："))
            print("  1. 下载并安装Git: https://git-scm.com/download/windows")
            print("  2. 确保Git安装时选择'Add Git to PATH'选项")
            print("  3. 重启命令行程序")
            print("  4. 或手动将Git添加到系统环境变量PATH中")
            print()
            print(Colors.cyan("建议的常见Git安装路径：（对的就是说git建议装在C盘里面）"))
            print("  - C:\\Program Files\\Git\\bin")
            print("  - C:\\Program Files (x86)\\Git\\bin")
            return False
            
        if service_key not in self.services:
            print(Colors.red(f"未知服务: {service_key}"))
            return False
        
        service = self.services[service_key]
        
        # 检查是否有仓库URL
        if not service.get("repo_url"):
            print(Colors.yellow(f"{service['name']} 没有关联的Git仓库，跳过更新"))
            return True
        
        repo_path = service["path"]
        
        if not repo_path.exists():
            print(Colors.red(f"仓库目录不存在: {repo_path}"))
            return False
        
        # 检查是否是Git仓库
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            print(Colors.red(f"目录不是Git仓库: {repo_path}"))
            print(Colors.yellow("请确保目录是通过git clone获得的"))
            return False
        
        print(Colors.yellow(f"准备更新 {service['name']} 仓库"))
        print(Colors.yellow("更新将会覆盖本地修改，请确认是否继续？"))
        confirm = input("输入 'yes' 确认更新，其他任意输入取消: ").strip().lower()
        
        if confirm != 'yes':
            print(Colors.blue("取消更新"))
            return False
        
        print(Colors.blue(f"正在更新 {service['name']} 仓库..."))
        
        # 直接使用公开仓库更新
        success = self._update_public_repo(service, repo_path)
        
        if success:
            print(Colors.green(f"✅ {service['name']} 仓库更新成功"))
            
            # 检查是否有requirements.txt文件
            requirements_file = repo_path / "requirements.txt"
            if requirements_file.exists():
                print(Colors.cyan("建议检查是否有新的依赖包需要更新"))
                print(Colors.cyan("如需更新依赖包，请选择主菜单的 '13. 安装/更新依赖包' 选项"))
                print()
            
            return True
        else:
            print(Colors.red(f"❌ {service['name']} 仓库更新失败"))
            return False
    
    def _update_public_repo(self, service: dict, repo_path: Path) -> bool:
        """更新公开仓库"""
        try:
            # 设置环境变量以禁用Git交互提示
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            env['GCM_INTERACTIVE'] = 'never'

            # 1. 确保本地在 dev 分支并尝试拉取更新
            print(Colors.cyan("正在切换到 dev 分支..."))
            switch_cmd = ['git', 'checkout', 'dev']
            switch_success, _ = self.run_command_with_env(
                switch_cmd, cwd=repo_path, env=env, show_output=False
            )
            if not switch_success:
                print(Colors.red("❌ 切换到 dev 分支失败，请检查本地仓库是否存在 dev 分支。"))
                return False

            print(Colors.cyan("正在从远程仓库的 dev 分支拉取更新..."))
            pull_cmd = ['git', 'pull', 'origin', 'dev']
            pull_success, pull_output = self.run_command_with_env(
                pull_cmd, cwd=repo_path, env=env, show_output=False
            )

            if pull_success:
                stdout = pull_output.get('stdout', '') if isinstance(pull_output, dict) else ''
                if "Already up to date" not in stdout:
                    print(Colors.green("✅ 仓库更新成功！"))
                    print(Colors.cyan(f"更新信息: \n{stdout.strip()}"))
                else:
                    print(Colors.green("✅ 仓库已是最新状态。"))
                return True
            else:
                # 2. 如果失败，提示用户手动处理
                stderr = pull_output.get('stderr', '') if isinstance(pull_output, dict) else str(pull_output)
                print(Colors.red("❌ 仓库更新失败！"))
                print(Colors.yellow("失败原因很可能是因为你本地有修改，与远程仓库的更新冲突了。"))
                print(Colors.yellow("为了保护你的修改不被覆盖，程序已停止更新。"))
                print()
                print(Colors.bold("解决方案："))
                print(Colors.cyan(f"  1. 请手动进入仓库目录: {repo_path}"))
                print(Colors.cyan("  2. 使用 `git status` 命令查看是哪些文件被修改了。"))
                print(Colors.cyan("  3. 如果这些修改是你需要的，请先将它们备份到其他地方。"))
                print(Colors.cyan("  4. 备份后，使用 `git reset --hard` 命令放弃本地修改，然后再重新运行本更新程序。"))
                print()
                print(Colors.red("详细错误信息如下："))
                print(f"{stderr.strip()}")
                return False

        except Exception as e:
            print(Colors.red(f"仓库更新过程中发生未知错误: {e}"))
            import traceback
            print(Colors.red(f"详细错误: {traceback.format_exc()}"))
            return False
    
    
    def install_requirements(self):
        """安装/更新依赖包 - 提供选择菜单"""
        while True:
            self.clear_screen()
            print(Colors.bold("依赖包管理"))
            print("=" * 50)
            print()
            print(Colors.green("选择要更新/重装的依赖："))
            print("  1. 更新 / 重装 Bot本体依赖")
            print("  2. 更新 / 重装 Adapter依赖") 
            print("  3. 更新 / 重装 Matcha-Adapter依赖")
            print("  4. 更新 / 重装 所有依赖")
            print()
            print(Colors.cyan("  0. 返回主菜单"))
            print()
            
            try:
                choice = input(Colors.bold("请选择操作 (0-4): ")).strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._install_service_requirements('bot')
                elif choice == '2':
                    self._install_service_requirements('adapter')
                elif choice == '3':
                    self._install_service_requirements('matcha_adapter')
                elif choice == '4':
                    self._install_all_requirements()
                else:
                    print(Colors.red("无效选择，请输入 0-4 之间的数字"))
                    input(Colors.blue("按回车键继续..."))
                    
            except KeyboardInterrupt:
                print(Colors.yellow("\n操作已取消"))
                break
    
    def _install_service_requirements(self, service_key: str):
        """安装指定服务的依赖包"""
        if service_key not in self.services:
            print(Colors.red(f"未知服务: {service_key}"))
            input(Colors.blue("按回车键继续..."))
            return
        
        service = self.services[service_key]
        requirements_file = service["path"] / "requirements.txt"
        
        if not requirements_file.exists():
            print(Colors.yellow(f"{service['name']} 没有 requirements.txt 文件，跳过"))
            input(Colors.blue("按回车键继续..."))
            return
        
        print(Colors.blue(f"正在安装 {service['name']} 的依赖..."))
        print(f"依赖文件: {Colors.cyan(str(requirements_file))}")
        
        # 清华大学PyPI镜像源
        mirror_url = "https://pypi.tuna.tsinghua.edu.cn/simple"
        print(f"使用清华大学PyPI镜像源: {Colors.cyan(mirror_url)}")
        print()
        
        # 尝试多种安装方式（优先使用清华源）
        install_commands = [
            # 方式1: 标准安装 + 清华源
            [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '-r', str(requirements_file)],
            # 方式2: 使用用户模式安装 + 清华源
            [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--user', '-r', str(requirements_file)],
            # 方式3: 强制重装 + 清华源
            [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--force-reinstall', '-r', str(requirements_file)],
            # 方式4: 使用缓存目录 + 清华源
            [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--cache-dir', str(self.base_path / '.pip_cache'), '-r', str(requirements_file)],
            # 方式5: 备用，不使用镜像源
            [str(self.python_executable), '-m', 'pip', 'install', '-r', str(requirements_file)]
        ]
        
        success = False
        for i, cmd in enumerate(install_commands):
            if i < 4:
                print(Colors.yellow(f"尝试安装方式 {i+1}/5 (使用清华源)..."))
            else:
                print(Colors.yellow(f"尝试安装方式 {i+1}/5 (使用官方源)..."))
            success, output = self.run_command(cmd, show_output=True)
            if success:
                print(Colors.green(f"✅ {service['name']} 依赖安装完成"))
                break
            else:
                print(Colors.yellow(f"方式 {i+1} 失败，尝试下一种方式..."))
        
        if not success:
            print(Colors.red(f"❌ {service['name']} 依赖安装失败"))
            print(Colors.red(f"手动安装命令(清华源): cd {service['path']} && {self.python_executable} -m pip install -i {mirror_url} -r requirements.txt"))
            print(Colors.red(f"手动安装命令(官方源): cd {service['path']} && {self.python_executable} -m pip install -r requirements.txt"))
        
        print()
        input(Colors.blue("按回车键继续..."))
    
    def _install_all_requirements(self):
        """安装所有服务的依赖包"""
        print(Colors.blue("正在检查并安装所有依赖包..."))
        print()
        
        # 清华大学PyPI镜像源
        mirror_url = "https://pypi.tuna.tsinghua.edu.cn/simple"
        
        for service_key, service in self.services.items():
            requirements_file = service["path"] / "requirements.txt"
            if requirements_file.exists():
                print(Colors.blue(f"正在安装 {service['name']} 的依赖..."))
                print(Colors.cyan(f"使用清华大学PyPI镜像源: {mirror_url}"))
                
                # 尝试多种安装方式（优先使用清华源）
                install_commands = [
                    [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '-r', str(requirements_file)],
                    [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--user', '-r', str(requirements_file)],
                    [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--force-reinstall', '-r', str(requirements_file)],
                    [str(self.python_executable), '-m', 'pip', 'install', '-i', mirror_url, '--cache-dir', str(self.base_path / '.pip_cache'), '-r', str(requirements_file)],
                    # 备用：不使用镜像源的原始命令
                    [str(self.python_executable), '-m', 'pip', 'install', '-r', str(requirements_file)]
                ]
                
                success = False
                for i, cmd in enumerate(install_commands):
                    if i < 4:
                        print(Colors.yellow(f"尝试安装方式 {i+1}/5 (使用清华源)..."))
                    else:
                        print(Colors.yellow(f"尝试安装方式 {i+1}/5 (使用官方源)..."))
                    success, output = self.run_command(cmd, show_output=False)
                    if success:
                        print(Colors.green(f"✅ {service['name']} 依赖安装完成"))
                        break
                    else:
                        print(Colors.yellow(f"方式 {i+1} 失败，尝试下一种方式..."))
                
                if not success:
                    print(Colors.red(f"❌ {service['name']} 依赖安装失败，请尝试手动安装"))
                    print(Colors.red(f"手动安装命令(清华源): cd {service['path']} && {self.python_executable} -m pip install -i {mirror_url} -r requirements.txt"))
                    print(Colors.red(f"手动安装命令(官方源): cd {service['path']} && {self.python_executable} -m pip install -r requirements.txt"))
                
                print()
        
        print(Colors.green("所有依赖安装检查完成"))
        input(Colors.blue("按回车键继续..."))
    
    def check_repository_status(self, service_key):
        """检查指定仓库的commit状态"""
        if service_key not in self.services:
            print(Colors.red(f"未找到服务: {service_key}"))
            return
            
        service = self.services[service_key]
        repo_path = service["path"]
        repo_name = service["name"]
        
        if not repo_path.exists():
            print(Colors.red(f"仓库目录不存在: {repo_path}"))
            return
            
        if not service.get("repo_url"):
            print(Colors.red(f"{repo_name} 没有配置远程仓库URL"))
            return
        
        print(Colors.bold(f"检查 {repo_name} 仓库状态..."))
        print(f"路径: {Colors.cyan(str(repo_path))}")
        print()
        
        try:
            # 设置环境变量禁用Git交互
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            env['GCM_INTERACTIVE'] = 'never'

            # 1. 获取远程更新
            print(Colors.blue("正在获取远程仓库更新..."))
            fetch_success, fetch_output = self.run_command_with_env(
                ['git', 'fetch'], cwd=repo_path, env=env, show_output=False
            )
            if not fetch_success:
                stderr = fetch_output.get('stderr', '') if isinstance(fetch_output, dict) else str(fetch_output)
                print(Colors.red(f"获取远程更新失败: {stderr}"))
                return
            print(Colors.green("✅ 成功获取远程更新"))

            # 2. 切换到 dev 分支
            print(Colors.cyan("正在切换到 dev 分支以进行状态检查..."))
            switch_cmd = ['git', 'checkout', 'dev']
            switch_success, switch_output = self.run_command_with_env(
                switch_cmd, cwd=repo_path, env=env, show_output=False
            )
            if not switch_success:
                stderr = switch_output.get('stderr', '') if isinstance(switch_output, dict) else ''
                print(Colors.red(f"❌ 切换到 dev 分支失败: {stderr}"))
                return

            # 3. 检查本地与远程 dev 分支的差异
            status_cmd = ['git', 'status', '-sb'] # 使用 -sb 参数获取简短格式的状态
            status_success, status_output = self.run_command_with_env(status_cmd, cwd=repo_path, env=env, show_output=False)
            
            if status_success:
                stdout = status_output.get('stdout', '').strip() if isinstance(status_output, dict) else ''
                if not stdout:
                    print(Colors.red("无法获取仓库状态。"))
                    return

                first_line = stdout.split('\n')[0]
                if '## dev...origin/dev' in first_line:
                    if 'ahead' in first_line:
                        print(Colors.yellow(f"本地仓库领先于远程仓库: {first_line}"))
                        print(Colors.cyan("提示：你可以使用 `git push` 将本地的修改推送到远程仓库。"))
                    elif 'behind' in first_line:
                        print(Colors.yellow(f"检测到新版本! 本地仓库落后于远程仓库: {first_line}"))
                        print(Colors.cyan("提示：请使用菜单中的更新功能来获取最新版本。"))
                    else:
                        print(Colors.green("✅ 仓库已是最新状态，与远程 dev 分支保持同步。"))
                else:
                     print(Colors.cyan(f"仓库状态信息：\n{stdout}"))

            else:
                print(Colors.red("检查仓库状态失败。"))

        except Exception as e:
            print(Colors.red(f"检查仓库状态时发生错误: {e}"))
        
        print()
    
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
                    choice = input(Colors.bold("请选择操作 (0-17): ")).strip()

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
                        print(Colors.blue("正在更新所有仓库..."))
                        for service_key in ['bot', 'adapter', 'matcha_adapter']:  # 只更新有仓库的服务
                            if self.services[service_key].get("repo_url"):
                                self.update_repository(service_key)
                    elif choice == '13':
                        self.install_requirements()
                    elif choice == '14':
                        self.show_system_info()
                    elif choice == '15':
                        self.check_repository_status('bot')
                    elif choice == '16':
                        self.check_repository_status('adapter')
                    elif choice == '17':
                        self.check_repository_status('matcha_adapter')
                    else:
                        print(Colors.red("无效选择，请输入 0-17 之间的数字"))
                    
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
