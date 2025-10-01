#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import io
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Colors:
    """控制台颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
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

class Updater:
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.python_executable = self.base_path / "python_embedded" / "python.exe"
        self.services = {
            "bot": {
                "name": "MoFox_Bot 主程序",
                "path": self.base_path / "core" / "Bot",
                "repo_url": "https://github.com/MoFox-Studio/MoFox_Bot.git",
                "branch": "master"
            },
            "onekey": {
                "name": "OneKey-Plus 管理程序",
                "path": self.base_path,
                "repo_url": "https://github.com/MoFox-Studio/OneKey-Plus.git",
                "branch": "Windows"
            }
        }

    def _find_git_executable(self) -> Optional[str]:
        import shutil
        git_path = shutil.which('git')
        if git_path:
            return git_path
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

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, show_output: bool = True) -> tuple:
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
        try:
            if cmd and cmd[0] == 'git':
                git_path = self._find_git_executable()
                if git_path:
                    cmd = [git_path] + cmd[1:]
                else:
                    print(Colors.red("错误：系统中未找到Git"))
                    return False, "Git not found"
            
            result = subprocess.run(
                cmd, 
                cwd=str(cwd) if cwd else None,
                env=env,
                capture_output=not show_output,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if not show_output:
                output_info = {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
                return result.returncode == 0, output_info
            return result.returncode == 0, ""
        except Exception as e:
            print(Colors.red(f"命令执行失败: {e}"))
            return False, str(e)

    def _update_repo(self, service: dict, repo_path: Path) -> bool:
        try:
            repo_url = service["repo_url"]
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            self.run_command_with_env(['git', 'remote', 'set-url', 'origin', repo_url], cwd=repo_path, env=env, show_output=False)
            
            branch = service.get("branch", "master")
            checkout_success, _ = self.run_command_with_env(['git', 'checkout', branch], cwd=repo_path, env=env, show_output=False)
            if not checkout_success:
                self.run_command_with_env(['git', 'checkout', '-b', branch, f'origin/{branch}'], cwd=repo_path, env=env, show_output=False)

            pull_success, pull_output = self.run_command_with_env(['git', 'pull', 'origin', branch], cwd=repo_path, env=env, show_output=False)
            
            if pull_success:
                stdout = pull_output.get('stdout', '')
                if "Already up to date" in stdout:
                    print(Colors.cyan("仓库已是最新版本。"))
                else:
                    print(Colors.cyan("Git更新详情：\n" + stdout))
                return True
            else:
                print(Colors.red(f"仓库更新失败: {pull_output.get('stderr', '')}"))
                return False
        except Exception as e:
            print(Colors.red(f"仓库更新出错: {e}"))
            return False

    def _install_requirements(self, service: dict, repo_path: Path):
        requirements_file = repo_path / "requirements.txt"
        if requirements_file.exists():
            print(Colors.blue(f"  -> 发现依赖文件，正在安装/更新 {service['name']} 的依赖..."))
            mirror_url = "https://pypi.tuna.tsinghua.edu.cn/simple"
            cmd = [str(self.python_executable), '-m', 'pip', 'install', '-r', str(requirements_file), '-i', mirror_url, '--upgrade']
            
            # 使用 show_output=False 来捕获输出
            success, output = self.run_command(cmd, show_output=False)
            
            if success:
                print(Colors.green(f"  -> ✅ {service['name']} 依赖安装成功"))
            else:
                print(Colors.red(f"  -> ❌ {service['name']} 依赖安装失败"))
                # 打印详细错误信息
                print(Colors.yellow("错误详情:\n" + output))
        else:
            print(Colors.cyan(f"  -> {service['name']} 无需安装依赖。"))

    def update_all(self):
        print(Colors.bold(Colors.cyan("=" * 60)))
        print(Colors.bold(Colors.cyan("          开始执行一键更新程序")))
        print(Colors.bold(Colors.cyan("=" * 60)))
        print()

        if not self._find_git_executable():
            print(Colors.red("❌ Git未安装或不在系统PATH中。请先安装Git。"))
            return

        services_to_update = ['bot', 'onekey']
        
        for service_key in services_to_update:
            service = self.services[service_key]
            repo_path = service["path"]
            
            print(Colors.yellow(f"--- 正在更新 {service['name']} ---"))
            
            if not (repo_path / ".git").exists():
                print(Colors.red(f"目录 {repo_path} 不是一个有效的Git仓库，跳过。"))
                print()
                continue

            update_success = self._update_repo(service, repo_path)
            
            if update_success:
                print(Colors.green(f"✅ {service['name']} 更新成功"))
                self._install_requirements(service, repo_path)
            else:
                print(Colors.red(f"❌ {service['name']} 更新失败"))
            
            print()
            time.sleep(1)

        print(Colors.bold(Colors.green("=" * 60)))
        print(Colors.bold(Colors.green("          所有仓库更新及依赖检查完毕")))
        print(Colors.bold(Colors.green("=" * 60)))

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('color')
    
    updater = Updater()
    updater.update_all()
    input(Colors.cyan("按回车键退出..."))