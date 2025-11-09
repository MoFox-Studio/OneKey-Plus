# -*- coding: utf-8 -*-
import tomlkit
import os
import re
import json
import subprocess
from collections.abc import MutableMapping

# --- 路径定义 ---
BASE_DIR = os.path.dirname(__file__)
BOT_CONFIG_PATH = os.path.join(BASE_DIR, "core", "Bot", "config", "bot_config.toml")
MODEL_CONFIG_PATH = os.path.join(BASE_DIR, "core", "Bot", "config", "model_config.toml")
NAPCAT_ADAPTER_CONFIG_PATH = os.path.join(
    BASE_DIR, "core", "Bot", "config", "plugins", "napcat_adapter", "config.toml"
)
ENV_PATH = os.path.join(BASE_DIR, "core", "Bot", ".env")


# --- 注释定义 ---
# 在这里为 bot_config.toml 的配置项添加更友好的注释
BOT_CONFIG_COMMENTS = {
    "permission": {
        "master_users": "在这里填上你的 QQ 号，你就是这台 Bot 的最高指挥官！"
    },
    "bot": {
        "qq_account": "Bot 要用哪个 QQ 号登录？填在这里。",
    },
}

# Napcat 适配器配置的注释
NAPCAT_CONFIG_COMMENTS = {
    "plugin": {
        "enabled": "要不要启用 Napcat 适配器？没它 Bot 可没法在 QQ 里说话哦。填 true 或 false。"
    },
    "features": {
        "group_list_type": "群聊的准入模式：'whitelist' - 只在名单上的群里说话, 'blacklist' - 除了名单上的群，其他都说话。",
        "group_list": "把要加入白名单或黑名单的群号都扔到这里，用逗号或空格隔开。",
        "private_list_type": "私聊也一样：'whitelist' - 只回复名单上的人, 'blacklist' - 除了名单上的人，都回复。",
        "private_list": "把要加入白名单或黑名单的用户 QQ 号都扔到这里，用逗号或空格隔开。",
        "enable_video_analysis": "是否允许适配器处理视频文件？（这会消耗更多资源，需要主配置和适配器同时开启）",
    },
}


def ask_for_config(config, comments, parent_key=""):
    """递归地向用户询问配置项。"""
    # 通用配置处理逻辑
    for key, value in config.items():
        current_comments = comments.get(key, {})
        if isinstance(value, MutableMapping):
            if key in comments:  # 只进入在COMMENTS中定义了的配置部分
                print(f"\n--- 正在配置 [{key}] 部分 ---")
                ask_for_config(value, current_comments, parent_key=key)
        else:
            comment_key_to_check = key
            if comment_key_to_check in comments:
                comment_text = comments[comment_key_to_check]

                # 通用键值对输入
                print(f"-> 正在配置 '{key}':")
                print(f"   说明：{comment_text}")
                print(f"   当前值：{value}")

                new_value_str = input("   请输入新值 (直接回车则不修改): ").strip()

                if new_value_str:
                    original_type = type(value)
                    try:
                        new_value = None
                        if key == "master_users":
                            # master_users 的格式是 [['qq', '...']]
                            current_list = (
                                value.tolist()
                                if hasattr(value, "tolist")
                                else list(value)
                            )
                            current_list.append(["qq", new_value_str])
                            # 去重
                            unique_list = []
                            seen = set()
                            for item in current_list:
                                t_item = tuple(item)
                                if t_item not in seen:
                                    unique_list.append(item)
                                    seen.add(t_item)
                            new_value = unique_list
                        elif original_type == bool:
                            new_value = new_value_str.lower() in [
                                "true",
                                "1",
                                "t",
                                "y",
                                "yes",
                            ]
                        elif original_type == list:
                            new_value = [
                                item.strip()
                                for item in re.split(r"[\s,]+", new_value_str)
                                if item.strip()
                            ]
                        elif original_type == int:  # noqa: E721
                            new_value = tomlkit.integer(int(new_value_str))
                        elif original_type == float:
                            new_value = float(new_value_str)
                        else:
                            new_value = original_type(new_value_str)

                        if new_value is not None:
                            config[key] = new_value
                            print(f"   '{key}' 已更新为: {new_value}")

                    except (ValueError, TypeError) as e:
                        print(
                            f"   输入格式错误或转换失败！'{key}' 的值类型应为 {original_type.__name__}。错误：{e}。跳过此项。"
                        )


def configure_bot():
    """配置 bot_config.toml 文件。"""
    try:
        with open(BOT_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = tomlkit.load(f)

        print("\n--- 开始配置 `bot_config.toml` ---")
        print("将引导您配置核心选项，其他高级选项请直接编辑文件。")
        ask_for_config(config, BOT_CONFIG_COMMENTS)

        # 保存一次，确保QQ号写入
        with open(BOT_CONFIG_PATH, "w", encoding="utf-8") as f:
            tomlkit.dump(config, f)

        print("\n核心配置完成！")
        print(
            "接下来将为您打开配置文件，您可以检查或修改其他高级设置。"
        )
        print("如果你不知道怎么配置，请参阅 https://docs.mofox-sama.com/docs/guides/bot_config_guide.html")

        # --- 打开编辑器 ---
        vscode_path = os.path.join(BASE_DIR, "core", "vscode", "Code.exe")
        
        # 科普时间！
        print("\n--- ✨ VS Code 配置文件编辑小贴士 ✨ ---")
        print("正在为您启动 VS Code 来编辑 TOML 配置文件。")
        print("💡 专业提示：VS Code 能够实时检查语法！")
        print("   - 如果您看到代码下面有红色的波浪线 (就像这样: ~~~)，说明您的配置文件可能写错了。")
        print("   - 把鼠标悬停在红色波浪线上，通常会显示详细的错误信息。")
        print("   - 如果看不懂错误信息，可以尝试复制下来，使用翻译软件或者直接找 AI 助手帮忙分析和修正！")
        print("------------------------------------------\n")
        input("按 Enter 键继续...")


        try:
            if os.path.exists(vscode_path):
                # 使用 subprocess.Popen 启动 VS Code
                subprocess.Popen([vscode_path, BOT_CONFIG_PATH])
                print(f"已使用 VS Code 打开配置文件: {BOT_CONFIG_PATH}")
                print("请在 VS Code 中完成修改后，手动返回此窗口继续后续步骤。")
            else:
                print("未在本目录找到 VS Code，将尝试使用系统默认编辑器打开。")
                os.startfile(BOT_CONFIG_PATH)
                print("配置文件已在默认文本编辑器中打开，请在修改完成后关闭它。")
        except Exception as e:
            print(f"无法自动打开配置文件: {e}")
            print("请手动打开以下文件进行修改：")
            print(BOT_CONFIG_PATH)

        input("完成修改后，请按 Enter 键返回此窗口并继续后续步骤...")
    except FileNotFoundError:
        print(f"错误：找不到 `bot_config.toml` 文件，路径：{BOT_CONFIG_PATH}")
    except Exception as e:
        print(f"处理 `bot_config.toml` 时发生未知错误：{e}")


def check_eula():
    """检查并处理EULA协议确认。"""
    env_content = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_content[key.strip()] = value.strip()
    if env_content.get("EULA_CONFIRMED", "false").lower() == "true":
        print("您已同意 EULA 协议。")
        return True
    print("=" * 60)
    print("MoFox-Bot 用户许可协议 (EULA) 确认")
    print("=" * 60)
    print("在使用 MoFox-Bot 之前,您需要同意 EULA 和隐私条款。")
    print("请花时间阅读以下文件(它们应该在 OneKey-Plus/core/bot 目录下):")
    print("  - EULA.md (用户许可协议)")
    print("  - PRIVACY.md (隐私条款)")
    print("-" * 60)

    while True:
        confirm = (
            input("您是否同意上述用户许可协议和隐私条款? (yes/no): ").strip().lower()
        )
        if confirm in ["yes", "y"]:
            env_content["EULA_CONFIRMED"] = "true"
            try:
                with open(ENV_PATH, "w", encoding="utf-8") as f:
                    for key, value in env_content.items():
                        f.write(f"{key}={value}\n")
                print("感谢您的同意! EULA 状态已更新。")
                return True
            except Exception as e:
                print(f"写入 .env 文件失败: {e}")
                return False
        elif confirm in ["no", "n"]:
            print("您必须同意协议才能使用 MoFox-Bot。程序即将退出。")
            return False
        else:
            print("无效输入,请输入 'yes' 或 'no'。")


def configure_model():
    """配置 model_config.toml 文件。"""
    try:
        with open(MODEL_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = tomlkit.load(f)

        print("\n--- 开始配置 `model_config.toml` ---")
        print("主要配置 SiliconFlow 的 API Key。")

        found = False
        api_providers = config.get("api_providers")
        if api_providers and isinstance(api_providers, list):
            for provider in api_providers:
                if provider.get("name") == "SiliconFlow":
                    found = True
                    print("-> 正在配置 'SiliconFlow' API Key:")
                    print(f"   当前值: {provider.get('api_key')}")

                    api_key = input(
                        "   请输入你的 SiliconFlow API Key(如果没有可以在https://cloud.siliconflow.cn/这里注册) (直接回车则不修改): "
                    ).strip()
                    if api_key:
                        provider["api_key"] = api_key
                        print("   SiliconFlow API Key 已更新！")
                        break

        if not found:
            print("未找到 SiliconFlow 的配置项，请检查 `model_config.toml` 文件。")

        with open(MODEL_CONFIG_PATH, "w", encoding="utf-8") as f:
            tomlkit.dump(config, f)
        print("\n`model_config.toml` 配置完成！")

    except FileNotFoundError:
        print(f"错误：找不到 `model_config.toml` 文件，路径：{MODEL_CONFIG_PATH}")
    except Exception as e:
        print(f"处理 `model_config.toml` 时发生未知错误：{e}")


def configure_napcat_adapter():
    """配置 napcat_adapter_config.toml 文件。"""
    try:
        # 检查文件是否存在，如果不存在则不进行配置
        if not os.path.exists(NAPCAT_ADAPTER_CONFIG_PATH):
            print(
                f"\n跳过 Napcat 适配器配置：未找到配置文件于 {NAPCAT_ADAPTER_CONFIG_PATH}"
            )
            return

        with open(NAPCAT_ADAPTER_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = tomlkit.load(f)

        print("\n--- 开始配置 `napcat_adapter_config.toml` (QQ适配器) ---")
        print("在这里，你可以调整 Bot 在 QQ 中的具体行为。")

        ask_for_config(config, NAPCAT_CONFIG_COMMENTS)

        with open(NAPCAT_ADAPTER_CONFIG_PATH, "w", encoding="utf-8") as f:
            tomlkit.dump(config, f)
        print("\n`napcat_adapter_config.toml` 配置完成！")

    except FileNotFoundError:
        # 理论上上面的 os.path.exists 已经处理了，但为了保险起见
        print(
            f"错误：找不到 `napcat_adapter_config.toml` 文件，路径：{NAPCAT_ADAPTER_CONFIG_PATH}"
        )
        print(
            "请确认 'Napcat-Adapter' 是否已正确安装在 'OneKey-Plus/core/Bot/src/plugins/built_in/' 目录下。"
        )
    except Exception as e:
        print(f"处理 `napcat_adapter_config.toml` 时发生未知错误：{e}")


def auto_configure_onebot_for_napcat():
    """
    静默检查并为 Napcat-Adapter 自动配置 OneBot v11 的 JSON 文件。
    - 仅在配置文件不存在时创建。
    - 创建的配置文件默认启用 WS 客户端。
    - 整个过程无用户交互。
    """
    try:
        # 1. 先获取 QQ 账号
        qq_account = None
        if os.path.exists(BOT_CONFIG_PATH):
            with open(BOT_CONFIG_PATH, "r", encoding="utf-8") as f:
                bot_config = tomlkit.load(f)
                qq_account = bot_config.get("bot", {}).get("qq_account")

        if not qq_account:
            return  # 没有 QQ 号，静默退出

        # 2. 确定 Napcat 内的配置文件路径
        napcat_config_dir = os.path.join(BASE_DIR, "core", "Napcat", "config")
        onebot_config_path = os.path.join(
            napcat_config_dir, f"onebot11_{qq_account}.json"
        )

        # 3. 如果文件已存在，则不做任何操作
        if os.path.exists(onebot_config_path):
            return

        # 4. 创建目录（如果需要）
        os.makedirs(napcat_config_dir, exist_ok=True)

        # 5. 定义默认配置并写入文件
        default_config = {
            "network": {
                "httpServers": [],
                "httpClients": [],
                "websocketServers": [],
                "websocketClients": [
                    {
                        "name": "MoFox-Bot-clinet",
                        "enable": True,  # 默认启用
                        "url": "ws://localhost:8095",
                        "messagePostFormat": "array",
                        "reportSelfMessage": False,
                        "reconnectInterval": 5000,
                        "token": "",
                        "debug": False,
                        "heartInterval": 30000,
                    }
                ],
            },
            "musicSignUrl": "",
            "enableLocalFile2Url": False,
            "parseMultMsg": False,
        }

        with open(onebot_config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)

        print(
            f"已为 Napcat 自动创建 OneBot 配置文件: {os.path.basename(onebot_config_path)}"
        )

    except Exception:
        # 发生任何错误都静默失败，不影响主流程
        pass


def auto_configure_ffmpeg():
    """自动检测并配置 FFmpeg 路径。"""
    config_changed = False
    try:
        with open(BOT_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = tomlkit.load(f)

        ffmpeg_dir = os.path.join(BASE_DIR, "core", "ffmpeg", "bin")
        ffmpeg_path_str = ffmpeg_dir.replace("\\", "/")

        if os.path.isdir(ffmpeg_dir):
            video_analysis_config = config.get("video_analysis")
            if video_analysis_config and isinstance(
                video_analysis_config, MutableMapping
            ):
                current_path = video_analysis_config.get("ffmpeg_path")
                if current_path != ffmpeg_path_str:
                    print(f"检测到 FFmpeg 目录，自动配置路径为: {ffmpeg_path_str}")
                    video_analysis_config["ffmpeg_path"] = ffmpeg_path_str
                    config_changed = True
        else:
            print(
                f"警告：未在 {ffmpeg_dir} 找到 FFmpeg 目录，视频分析功能可能无法使用。"
            )

        if config_changed:
            with open(BOT_CONFIG_PATH, "w", encoding="utf-8") as f:
                tomlkit.dump(config, f)

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"自动配置 FFmpeg 时发生错误：{e}")


if __name__ == "__main__":
    if not check_eula():
        input("按 Enter 键退出...")
    else:
        auto_configure_ffmpeg()  # 在向导开始前自动配置
        print("\n")
        print("=" * 60)
        print("欢迎使用 MoFox-Bot 配置向导！")
        print("接下来，我会引导你完成一些基本设置。")
        print("如果不想修改，直接按 Enter 键跳过即可。")
        print("=" * 60)
        print("\n")
        configure_bot()
        configure_model()
        configure_napcat_adapter()
        auto_configure_onebot_for_napcat()
        print("\n\n==============================================")
        print("所有配置已完成！现在你可以启动主程序了。")
        print("==============================================")
