#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoFox-Core 一键管理程序 (Linux版本)
功能：
1. 启动 MoFox Core 主程序
2. 更新GitHub仓库
3. 管理配置文件
"""

import os
import sys
import subprocess
import time
import json
import base64
import platform
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

class MoFoxManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.venv_python = self.base_path / ".venv" / "bin" / "python"
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
        # GitHub Access Token (编码，仅具有指定仓库的读取权限)
        self._github_token_encoded = "Z2hwX2NPVlVkYk8wa2RBVzM1bEVJaHdqUmxFQlNIQUwyRjNoSll4Rg=="
        
        # 服务配置
        self.services = {
            "bot": {
                "name": "MoFox Core 主程序",
                "path": self.base_path / "Bot",
                "main_file": "bot.py",
                "description": "AI聊天机器人主程序",
                "repo_url": "https://github.com/MoFox-Studio/MoFox-Core.git",
                "type": "python"
            }
        }
    
    def clear_screen(self):
        """清屏"""
        os.system('clear')
    
    def print_header(self):
        """打印程序头部"""
        print("=" * 60)
        print(Colors.cyan(Colors.bold("          MoFox-Core 一键管理程序 (Linux)")))
        print(Colors.yellow("              Version 1.0"))
        print("=" * 60)
        print(Colors.blue("Edited by 阿范 @212898630"))
    
    def _get_github_token(self) -> Optional[str]:
        """获取GitHub访问Token"""
        try:
            token = base64.b64decode(self._github_token_encoded).decode('utf-8')
            return token
        except Exception as e:
            print(Colors.red(f"获取GitHub Token失败: {e}"))
            return None

    def print_menu(self):
        """打印主菜单"""
        print(Colors.bold("主菜单："))
        print()
        print(Colors.green("快捷启动服务管理："))
        print("  1. 启动 MoFox Core 主程序")
        print("  2. 查看运行状态")
        print("  3. 启动数据库管理程序 (暂不支持Linux)")
        print()
        print(Colors.blue("更新管理："))
        print("  4. 更新 Bot 仓库")
        print()
        print(Colors.yellow("其他功能："))
        print("  5. 安装/更新依赖包")
        print("  6. 查看系统信息")
        print("  7. 尝试自我修复 pip 权限问题（仅供测试，安装依赖报错时使用）")
        print()
        print(Colors.yellow("仓库状态检查："))
        print("  8. 检查 MoFox-Core 仓库状态")
        print("  0. 退出程序")
        print()
    
    def print_service_groups_menu(self):
        """打印服务组合菜单"""
        pass
    
    def start_service_group(self):
        """启动服务组合"""
        pass
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, show_output: bool = True) -> tuple:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                capture_output=not show_output,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout if not show_output else ""
        except Exception as e:
            print(Colors.red(f"命令执行失败: {e}"))
            return False, str(e)
    
    def run_command_with_env(self, cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None, show_output: bool = True) -> tuple:
        """运行命令（支持自定义环境变量）"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                env=env,
                capture_output=not show_output,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if not show_output:
                output_info = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                return result.returncode == 0, output_info
            else:
                return result.returncode == 0, ""
                
        except Exception as e:
            print(Colors.red(f"命令执行失败: {e}"))
            return False, str(e)
    
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
            
            # 尝试在新终端中启动
            terminal_found = False
            cmd_to_run = ""
            
            if service_type == "python":
                cmd_to_run = f"cd '{service_path}' && '{self.venv_python}' '{main_file}'; echo; read -p 'Press Enter to exit...'"
            elif service_type == "shell":
                script_path = service_path / main_file
                # 确保脚本有执行权限
                script_path.chmod(0o755)
                cmd_to_run = f"cd '{service_path}' && './{main_file}'; echo; read -p 'Press Enter to exit...'"
            elif service_type == "executable":
                exec_path = service_path / main_file
                # 确保文件有执行权限
                exec_path.chmod(0o755)
                cmd_to_run = f"cd '{service_path}' && './{main_file}'; echo; read -p 'Press Enter to exit...'"
            else:
                print(Colors.red(f"不支持的服务类型: {service_type}"))
                return False

            terminal_commands = [
                ["gnome-terminal", "--", "bash", "-c", cmd_to_run],
                ["konsole", "-e", "bash", "-c", cmd_to_run],
                ["xfce4-terminal", "--command", f"bash -c \"{cmd_to_run}\""],
                ["xterm", "-e", f"bash -c \"{cmd_to_run}\""]
            ]
            
            for cmd in terminal_commands:
                try:
                    process = subprocess.Popen(cmd, cwd=service_path)
                    terminal_found = True
                    break
                except FileNotFoundError:
                    continue
            
            if not terminal_found:
                print(Colors.yellow("未找到图形终端，将在后台运行..."))
                if service_type == "python":
                    process = subprocess.Popen([str(self.venv_python), main_file], cwd=service_path)
                elif service_type in ["shell", "executable"]:
                    process = subprocess.Popen([f"./{main_file}"], cwd=service_path)
            
            self.running_processes[service_key] = process
            print(Colors.green(f"✅ {service['name']} 已启动 (PID: {process.pid})"))
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
                    pid_info = f"(PID: {process.pid})"
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
            print(Colors.cyan("提示：服务可能运行在独立的终端窗口中"))
            print(Colors.cyan("关闭对应窗口即可停止服务"))
        print()
    
    def start_sqlite_studio(self):
        """启动SQLiteStudio数据库管理程序"""
        print(Colors.red("❌ 此功能暂不支持Linux"))
        print(Colors.yellow("请使用您喜欢的数据库管理工具手动打开数据库文件。"))
        print(Colors.cyan("数据库文件位置：Bot/data/MaiBot.db"))
        return False
    
    def update_repository(self, service_key: str):
        """更新仓库"""
        if service_key not in self.services:
            print(Colors.red(f"未知服务: {service_key}"))
            return False
        
        service = self.services[service_key]
        
        if not service.get("repo_url"):
            print(Colors.yellow(f"{service['name']} 没有关联的Git仓库，跳过更新"))
            return True
        
        repo_path = service["path"]
        
        if not repo_path.exists():
            print(Colors.red(f"仓库目录不存在: {repo_path}"))
            return False
        
        print(Colors.yellow(f"准备更新 {service['name']} 仓库"))
        print(Colors.yellow("更新将会覆盖本地修改，请确认是否继续？"))
        confirm = input("输入 'yes' 确认更新，其他任意输入取消: ").strip().lower()
        
        if confirm != 'yes':
            print(Colors.blue("取消更新"))
            return False
        
        print(Colors.blue(f"正在更新 {service['name']} 仓库..."))
        
        github_token = self._get_github_token()
        
        if github_token:
            success = self._update_with_token(service, repo_path, github_token)
        else:
            print(Colors.red("GitHub Token不可用，无法更新私有仓库"))
            print(Colors.cyan("提示：请检查Token配置或手动更新"))
            return False
        
        if success:
            print(Colors.green(f"✅ {service['name']} 仓库更新成功"))
            
            requirements_file = repo_path / "requirements.txt"
            if requirements_file.exists():
                print(Colors.blue("正在更新依赖包..."))
                
                install_commands = [
                    [str(self.venv_python), '-m', 'pip', 'install', '-r', 'requirements.txt'],
                    [str(self.venv_python), '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'],
                    [str(self.venv_python), '-m', 'pip', 'install', '--force-reinstall', '-r', 'requirements.txt']
                ]
                
                dep_success = False
                for cmd in install_commands:
                    dep_success, _ = self.run_command(cmd, cwd=repo_path, show_output=False)
                    if dep_success:
                        break
                
                if dep_success:
                    print(Colors.green("✅ 依赖包更新成功"))
                else:
                    print(Colors.yellow("⚠️ 依赖包更新可能有问题，建议手动检查"))
            
            return True
        else:
            print(Colors.red(f"❌ {service['name']} 仓库更新失败"))
            return False
    
    def _update_with_token(self, service: dict, repo_path: Path, token: str) -> bool:
        """使用Token进行认证更新"""
        try:
            repo_url = service.get("repo_url", "")
            if repo_url.startswith("https://github.com/"):
                auth_url = repo_url.replace("https://github.com/", f"https://{token}@github.com/")
                
                original_helper = self._get_git_config(repo_path, "credential.helper")
                original_askpass = self._get_git_config(repo_path, "core.askpass")
                
                try:
                    self._set_git_config(repo_path, "credential.helper", "")
                    self._set_git_config(repo_path, "core.askpass", "")
                    
                    env = os.environ.copy()
                    env['GIT_TERMINAL_PROMPT'] = '0'
                    env['GIT_ASKPASS'] = ''
                    env['SSH_ASKPASS'] = ''
                    
                    set_url_cmd = ['git', 'remote', 'set-url', 'origin', auth_url]
                    success, output = self.run_command_with_env(set_url_cmd, cwd=repo_path, env=env, show_output=False)
                    
                    if not success:
                        stderr = output.get('stderr', '') if isinstance(output, dict) else str(output)
                        print(Colors.red(f"设置认证URL失败: {stderr}"))
                        return False
                    
                    pull_success, pull_output = self.run_command_with_env(['git', 'pull'], cwd=repo_path, env=env, show_output=False)
                    
                    restore_url_cmd = ['git', 'remote', 'set-url', 'origin', repo_url]
                    self.run_command_with_env(restore_url_cmd, cwd=repo_path, env=env, show_output=False)
                    
                    if pull_success:
                        stdout = pull_output.get('stdout', '') if isinstance(pull_output, dict) else str(pull_output)
                        print(Colors.green("✅ 使用Token认证更新成功"))
                        if stdout.strip():
                            print(Colors.cyan(f"更新信息: {stdout.strip()}"))
                        return True
                    else:
                        stderr = pull_output.get('stderr', '') if isinstance(pull_output, dict) else str(pull_output)
                        print(Colors.red(f"Token认证更新失败: {stderr}"))
                        return False
                        
                finally:
                    self._restore_git_config(repo_path, "credential.helper", original_helper)
                    self._restore_git_config(repo_path, "core.askpass", original_askpass)
                    
            else:
                print(Colors.red("不支持的仓库URL格式"))
                return False
                
        except Exception as e:
            print(Colors.red(f"Token认证更新出错: {e}"))
            return False
    
    def _get_git_config(self, repo_path: Path, key: str) -> Optional[str]:
        """获取Git配置值"""
        try:
            result = subprocess.run(
                ['git', 'config', '--local', '--get', key],
                cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='ignore'
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _set_git_config(self, repo_path: Path, key: str, value: str):
        """设置Git配置值"""
        try:
            subprocess.run(
                ['git', 'config', '--local', key, value],
                cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='ignore'
            )
        except:
            pass
    
    def _restore_git_config(self, repo_path: Path, key: str, original_value: Optional[str]):
        """恢复Git配置值"""
        try:
            if original_value is not None:
                subprocess.run(
                    ['git', 'config', '--local', key, original_value],
                    cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='ignore'
                )
            else:
                subprocess.run(
                    ['git', 'config', '--local', '--unset', key],
                    cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='ignore'
                )
        except:
            pass
    
    def install_requirements(self):
        """安装/更新所有依赖包"""
        print(Colors.blue("正在检查并安装所有依赖包..."))
        
        for service_key, service in self.services.items():
            requirements_file = service["path"] / "requirements.txt"
            if requirements_file.exists():
                print(Colors.blue(f"正在安装 {service['name']} 的依赖..."))
                
                install_commands = [
                    [str(self.venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
                    [str(self.venv_python), '-m', 'pip', 'install', '--user', '-r', str(requirements_file)],
                    [str(self.venv_python), '-m', 'pip', 'install', '--force-reinstall', '-r', str(requirements_file)],
                    [str(self.venv_python), '-m', 'pip', 'install', '--cache-dir', str(self.base_path / '.pip_cache'), '-r', str(requirements_file)]
                ]
                
                success = False
                for i, cmd in enumerate(install_commands):
                    print(Colors.yellow(f"尝试安装方式 {i+1}/4..."))
                    success, output = self.run_command(cmd, show_output=True)
                    if success:
                        print(Colors.green(f"✅ {service['name']} 依赖安装完成"))
                        break
                    else:
                        print(Colors.yellow(f"方式 {i+1} 失败，尝试下一种方式..."))
                
                if not success:
                    print(Colors.red(f"❌ {service['name']} 依赖安装失败，请尝试手动安装"))
                    print(Colors.red(f"手动安装命令: cd {service['path']} && {self.venv_python} -m pip install -r requirements.txt"))
        
        print(Colors.green("依赖安装检查完成"))
    
    def check_repository_status(self, service_key):
        """检查指定仓库的commit状态（支持Token认证）"""
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
        
        github_token = self._get_github_token()
        
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            original_url = None
            if github_token:
                print(Colors.blue("使用Token认证获取远程仓库更新..."))
                get_url_result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
                if get_url_result.returncode == 0:
                    original_url = get_url_result.stdout.strip()
                    if original_url.startswith("https://github.com/"):
                        auth_url = original_url.replace("https://github.com/", f"https://{github_token}@github.com/")
                        set_url_result = subprocess.run(["git", "remote", "set-url", "origin", auth_url], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
                        if set_url_result.returncode != 0:
                            print(Colors.yellow("设置认证URL失败，使用普通方式检查"))
                            github_token = None
            else:
                print(Colors.blue("正在获取远程仓库更新..."))
            
            fetch_result = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
            
            if github_token and original_url:
                subprocess.run(["git", "remote", "set-url", "origin", original_url], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
            
            if fetch_result.returncode != 0:
                print(Colors.red(f"获取远程更新失败: {fetch_result.stderr}"))
                return
            else:
                print(Colors.green("✅ 成功获取远程更新"))
            
            branch_result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
            current_branch = branch_result.stdout.strip() or "master"
            
            log_result = subprocess.run(["git", "log", f"HEAD..origin/{current_branch}", "--oneline"], capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
            
            if log_result.returncode != 0:
                print(Colors.red(f"检查commit差异失败: {log_result.stderr}"))
                return
            
            commits_behind = log_result.stdout.strip()
            
            if not commits_behind:
                print(Colors.green("✅ 仓库已是最新状态，没有落后的commit"))
            else:
                commit_lines = commits_behind.split('\n')
                commit_count = len(commit_lines)
                print(Colors.yellow(f"你的本地仓库落后了 {commit_count} 个commit"))
                print()
                print(Colors.bold("落后的commit详情："))
                for i, commit_line in enumerate(commit_lines, 1):
                    if commit_line.strip():
                        print(f"{Colors.cyan(f'{i:2d}.')} {commit_line}")
                
        except Exception as e:
            print(Colors.red(f"检查仓库状态时发生错误: {e}"))
        finally:
            os.chdir(original_cwd)
        
        print()
    
    def show_system_info(self):
        """显示系统信息"""
        print(Colors.bold("系统信息："))
        print()
        
        try:
            result = subprocess.run([str(self.venv_python), '--version'], 
                                  capture_output=True, text=True, encoding='utf-8', errors='ignore')
            python_version = result.stdout.strip()
            print(f"  Python版本: {Colors.green(python_version)}")
        except:
            print(f"  Python版本: {Colors.red('获取失败')}")
        
        print(f"  工作目录: {Colors.cyan(str(self.base_path))}")
        
        venv_status = Colors.green("已配置") if self.venv_python.exists() else Colors.red("未配置")
        print(f"  虚拟环境: {venv_status}")
        
        print(f"  仓库状态:")
        for service_key, service in self.services.items():
            repo_exists = service["path"].exists()
            status = Colors.green("存在") if repo_exists else Colors.red("不存在")
            print(f"    {service['name']}: {status}")
        
        print()
    
    def fix_pip_permissions(self):
        """修复 pip 权限问题"""
        print(Colors.bold("修复 pip 权限问题"))
        print(Colors.yellow("这个功能将尝试修复Python包安装时的权限问题"))
        print()
        
        print(Colors.blue("步骤 1: 升级 pip..."))
        upgrade_commands = [
            [str(self.venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'],
            [str(self.venv_python), '-m', 'pip', 'install', '--user', '--upgrade', 'pip']
        ]
        
        pip_upgraded = False
        for cmd in upgrade_commands:
            success, _ = self.run_command(cmd, show_output=True)
            if success:
                print(Colors.green("✅ pip 升级成功"))
                pip_upgraded = True
                break
        
        if not pip_upgraded:
            print(Colors.yellow(" pip 升级失败，但继续进行其他修复步骤"))
        
        print(Colors.blue("步骤 2: 清除 pip 缓存..."))
        success, _ = self.run_command([str(self.venv_python), '-m', 'pip', 'cache', 'purge'], show_output=False)
        if success:
            print(Colors.green("✅ pip 缓存清除成功"))

        print()
        print(Colors.bold("权限问题解决建议："))
        print(Colors.cyan("1. 使用 sudo 运行此脚本 (sudo ./首次启动点我.sh)"))
        print(Colors.cyan("2. 使用 --user 参数安装包（已在程序中自动尝试）"))
        print(Colors.cyan("3. 检查并确保虚拟环境目录有写入权限 (chmod -R 755 .venv)"))
        
        retry = input("是否现在重新尝试安装依赖包？(y/n): ").strip().lower()
        if retry == 'y':
            self.install_requirements()
        
        input(Colors.blue("按回车键返回主菜单..."))

    def run(self):
        """运行主程序"""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_menu()
                
                try:
                    choice = input(Colors.bold("请选择操作 (0-8): ")).strip()
                    
                    if choice == '0':
                        print(Colors.green("程序退出，感谢使用！"))
                        break
                    elif choice == '1':
                        self.start_service('bot')
                    elif choice == '2':
                        self.show_status()
                    elif choice == '3':
                        self.start_sqlite_studio()
                    elif choice == '4':
                        self.update_repository('bot')
                    elif choice == '5':
                        self.install_requirements()
                    elif choice == '6':
                        self.show_system_info()
                    elif choice == '7':
                        self.fix_pip_permissions()
                    elif choice == '8':
                        self.check_repository_status('bot')
                    else:
                        print(Colors.red("无效选择，请输入 0-8 之间的数字"))
                    
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
    manager = MoFoxManager()
    manager.run()