# -*- coding: utf-8 -*-
import tomlkit
import os
import re
from collections.abc import MutableMapping

# --- 路径定义 ---
BASE_DIR = os.path.dirname(__file__)
BOT_CONFIG_PATH = os.path.join(BASE_DIR, 'core', 'Bot', 'config', 'bot_config.toml')
MODEL_CONFIG_PATH = os.path.join(BASE_DIR, 'core', 'Bot', 'config', 'model_config.toml')
ENV_PATH = os.path.join(BASE_DIR, 'core', 'Bot', '.env')


# --- 注释定义 ---
# 在这里为 bot_config.toml 的配置项添加更友好的注释
BOT_CONFIG_COMMENTS = {
    'database': {
        'database_type': "你想用哪种数据库？'sqlite' 就像个便签本，简单方便；'mysql' 则像个大书柜，适合管理大量数据。"
    },
    'permission': {
        'master_users': "在这里填上你的 QQ 号，你就是这台 Bot 的最高指挥官！"
    },
    'bot': {
        'qq_account': "Bot 要用哪个 QQ 号登录？填在这里。",
        'nickname': "给你的 Bot 起个好听的名字吧！",
        'alias_names': "再给 Bot 起几个小名，方便大家称呼。多个用逗号或空格隔开。"
    },
    'personality': {
        'personality_core': "一句话描述 Bot 的核心性格，比如“一个傲娇的猫娘”。",
        'identity': "详细描述一下 Bot 的设定，比如年龄、性别、外貌等等。",
        'background_story': "如果你想给 Bot 设定更复杂的背景故事，可以在这里写。",
        'reply_style': "定义 Bot 的说话风格，让它更符合你的想象。"
    },
    'expression': {
        'use_expression': "是否让 Bot 学习并使用新的说话方式？填 true 或 false。",
        'learn_expression': "是否允许 Bot 从聊天中学习新的表达方式？填 true 或 false。"
    },
    'chat': {
        'group_chat_mode': "在群里,Bot 应该是什么样的聊天模式?'auto' - 智能切换,'normal' - 普通模式,'focus' - 专注模式。",
        'talk_frequency': "调整 Bot 的话痨程度,数值越高,它就越活跃。",
        'enable_proactive_thinking': "是否允许 Bot 在没人理它的时候主动找话题? 填 true 或 false。",
        'proactive_thinking_interval': "Bot 主动思考一次后,大概要等多久(秒)才会再次主动思考?",
        'proactive_thinking_enable_in_private': "在这里添加允许 Bot 主动思考的私聊 QQ 号(多个用逗号或空格隔开)。",
        'proactive_thinking_enable_in_groups': "在这里添加允许 Bot 主动思考的QQ群号(多个用逗号或空格隔开)。"
    },
    'anti_prompt_injection': {
        'enabled': "是否开启防御模式，防止别人对你的 Bot 进行“催眠”或“洗脑”？填 true 或 false。(但是会拖慢消息处理速度)"
    },
    'mood': {
        'enable_mood': "是否让 Bot 拥有自己的情绪？开启后，它的心情会根据聊天内容变化。填 true 或 false。"
    },
    'emoji': {
        'emoji_chance': "Bot 有多大的概率会发表情包？(0.0 到 1.0 之间的小数)",
        'steal_emoji': "是否允许 Bot“偷”群友的表情包自己用？填 true 或 false。"
    },
    'memory': {
        'enable_memory': "是否让 Bot 拥有记忆力，能记住和大家的聊天内容？填 true 或 false。",
    },
    'web_search': {
        'enable_web_search_tool': "是否允许 Bot 上网查资料？填 true 或 false。",
        'enabled_engines': "你想启用哪些搜索引擎？可选 'ddg', 'bing', 'exa', 'tavily'。多个用逗号隔开。",
        'tavily_api_keys': "如果你要用 Tavily，在这里填上你的 API Key。多个 Key 用逗号或空格隔开。",
        'exa_api_keys': "同上，这是 EXA 搜索引擎的 API Key。多个 Key 用逗号或空格隔开。"
    },
    'planning_system': {
        'schedule_enable': "是否让 Bot 每天自动生成日程表？填 true 或 false。",
        'monthly_plan_enable': "是否让 Bot 每月自动生成计划？填 true 或 false。"
    },
    'sleep_system': {
        'enable': "是否启用睡眠系统？开启后 Bot 会在指定时间“睡觉”，期间不会回复。填 true 或 false。",
        'sleep_by_schedule': "是严格按照日程表的时间睡觉，还是使用下面固定的时间？填 true 或 false。",
        'fixed_sleep_time': "如果不用日程表，Bot 每天几点睡觉？格式：HH:MM，例如 '23:00'。",
        'fixed_wake_up_time': "如果不用日程表，Bot 每天几点起床？格式：HH:MM，例如 '07:00'。"
    }
}


def update_comment(table, key, comment_text):
    """智能更新或添加注释，保留原有注释。"""
    if key in table and hasattr(table, 'item'):
        item = table.item(key)
        if item is None: return

        # 使用 trivia 获取注释信息
        existing_comment = item.trivia.comment
        
        # 避免重复添加完全相同的注释
        if comment_text and (not existing_comment or comment_text not in existing_comment):
            new_comment = f" {comment_text}" # 加个空格美观一些
            
            # tomlkit 的注释是整个替换的，所以需要拼接
            full_comment = (existing_comment.strip() + " |" + new_comment) if existing_comment else new_comment
            item.comment(full_comment.strip())

def ask_for_config(config, comments, parent_key=''):
    """递归地向用户询问配置项。"""
    if parent_key == 'expression' and 'rules' in config:
        print("\n--- 正在配置 [expression] (表达学习规则) ---")
        for i, rule in enumerate(config['rules']):
            rule_id = rule.get('chat_stream_id') or "全局规则"
            print(f"\n--- 编辑规则 {i+1}: {rule_id} ---")
            ask_for_config(rule, comments, parent_key='expression_rule')
        
        while True:
            add_new = input("\n是否要为特定群聊或私聊添加新的表达学习规则? (y/n): ").strip().lower()
            if add_new == 'y':
                chat_id = input("请输入群号或私聊 QQ 号: ").strip()
                chat_type = input("请输入类型 (group/private): ").strip().lower()
                if chat_id and chat_type in ['group', 'private']:
                    new_rule = tomlkit.table()
                    new_rule.add('chat_stream_id', f"qq:{chat_id}:{chat_type}")
                    new_rule.add('use_expression', True)
                    new_rule.add('learn_expression', True)
                    config['rules'].append(new_rule)
                    print(f"已为 qq:{chat_id}:{chat_type} 添加新规则，默认启用学习和使用。")
                else:
                    print("输入无效，请重新输入。")
            else:
                break
        return

    for key, value in config.items():
        if key == 'rules' and parent_key == 'expression':
            continue

        current_comments = comments.get(key, {})
        if isinstance(value, MutableMapping):
            if key in comments:
                print(f"\n--- 正在配置 [{key}] 部分 ---")
                ask_for_config(value, current_comments, parent_key=key)
        else:
            comment_key_to_check = key if parent_key != 'expression_rule' else key
            if comment_key_to_check in comments:
                comment_text = comments[comment_key_to_check]
                
                # 特殊处理主动思考的列表
                if key in ['proactive_thinking_enable_in_private', 'proactive_thinking_enable_in_groups']:
                    print(f"-> 正在配置 '{key}':")
                    print(f"   说明：{comment_text}")
                    print(f"   当前值：{value}")
                    new_ids_str = input("   请输入要添加的新 ID (多个用逗号或空格隔开, 直接回车则不添加): ").strip()
                    if new_ids_str:
                        import re
                        new_ids = [f"qq:{item.strip()}" for item in re.split(r'[\s,]+', new_ids_str) if item.strip()]
                        # 去重合并
                        current_set = set(value)
                        current_set.update(new_ids)
                        config[key] = sorted(list(current_set))
                        print(f"   '{key}' 已更新为: {config[key]}")
                    continue # 处理完跳过后面的通用逻辑

                print(f"-> 正在配置 '{key}':")
                print(f"   说明：{comment_text}")
                print(f"   当前值：{value}")
                
                new_value_str = input("   请输入新值 (直接回车则不修改): ").strip()
                
                if new_value_str:
                    original_type = type(value)
                    try:
                        new_value = None
                        if key == 'master_users':
                            new_value = [['qq', new_value_str]]
                        elif original_type == bool:
                            new_value = new_value_str.lower() in ['true', '1', 't', 'y', 'yes']
                        elif original_type == list:
                            import re
                            new_value = [item.strip() for item in re.split(r'[\s,]+', new_value_str) if item.strip()]
                        elif original_type == int:
                            new_value = int(new_value_str)
                        elif original_type == float:
                            new_value = float(new_value_str)
                        else:
                            new_value = original_type(new_value_str)
                        
                        if new_value is not None:
                            config[key] = new_value
                            print(f"   '{key}' 已更新为: {new_value}")

                    except (ValueError, TypeError) as e:
                        print(f"   输入格式错误或转换失败！'{key}' 的值类型应为 {original_type.__name__}。错误：{e}。跳过此项。")

                update_comment(config, key, comment_text)

def configure_bot():
    """配置 bot_config.toml 文件。"""
    try:
        with open(BOT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = tomlkit.load(f)

        print("\n--- 开始配置 `bot_config.toml` ---")
        ask_for_config(config, BOT_CONFIG_COMMENTS)

        with open(BOT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            tomlkit.dump(config, f)
        print("\n`bot_config.toml` 配置完成！")

    except FileNotFoundError:
        print(f"错误：找不到 `bot_config.toml` 文件，路径：{BOT_CONFIG_PATH}")
    except Exception as e:
        print(f"处理 `bot_config.toml` 时发生未知错误：{e}")


def check_eula():
    """检查并处理EULA协议确认。"""
    eula_confirmed = False
    env_content = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    if env_content.get('EULA_CONFIRMED', 'false').lower() == 'true':
        print("您已同意 EULA 协议。")
        return True
    print("="*60)
    print("MoFox-Bot 用户许可协议 (EULA) 确认")
    print("="*60)
    print("在使用 MoFox-Bot 之前,您需要同意 EULA 和隐私条款。")
    print("请花时间阅读以下文件(它们应该在 OneKey-Plus/core/bot 目录下):")
    print("  - EULA.md (用户许可协议)")
    print("  - PRIVACY.md (隐私条款)")
    print("-" * 60)

    while True:
        confirm = input("您是否同意上述用户许可协议和隐私条款? (yes/no): ").strip().lower()
        if confirm in ['yes', 'y']:
            env_content['EULA_CONFIRMED'] = 'true'
            try:
                with open(ENV_PATH, 'w', encoding='utf-8') as f:
                    for key, value in env_content.items():
                        f.write(f"{key}={value}\n")
                print("感谢您的同意! EULA 状态已更新。")
                return True
            except Exception as e:
                print(f"写入 .env 文件失败: {e}")
                return False
        elif confirm in ['no', 'n']:
            print("您必须同意协议才能使用 MoFox-Bot。程序即将退出。")
            return False
        else:
            print("无效输入,请输入 'yes' 或 'no'。")


def configure_model():
    """配置 model_config.toml 文件。"""
    try:
        with open(MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = tomlkit.load(f)

        print("\n--- 开始配置 `model_config.toml` ---")
        print("主要配置 SiliconFlow 的 API Key。")

        found = False
        api_providers = config.get('api_providers')
        if api_providers and isinstance(api_providers, list):
            for provider in api_providers:
                if provider.get('name') == 'SiliconFlow':
                    found = True
                    print(f"-> 正在配置 'SiliconFlow' API Key:")
                    print(f"   当前值: {provider.get('api_key')}")
                    
                    api_key = input("   请输入你的 SiliconFlow API Key(如果没有可以在https://cloud.siliconflow.cn/expensebill这里注册) (直接回车则不修改): ").strip()
                    if api_key:
                        provider['api_key'] = api_key
                        print(f"   SiliconFlow API Key 已更新！")
                    
                    # 添加注释
                    update_comment(provider, 'api_key', "在这里填入你的 SiliconFlow API Key")
                    break
        
        if not found:
            print("未找到 SiliconFlow 的配置项，请检查 `model_config.toml` 文件。")

        with open(MODEL_CONFIG_PATH, 'w', encoding='utf-8') as f:
            tomlkit.dump(config, f)
        print("\n`model_config.toml` 配置完成！")

    except FileNotFoundError:
        print(f"错误：找不到 `model_config.toml` 文件，路径：{MODEL_CONFIG_PATH}")
    except Exception as e:
        print(f"处理 `model_config.toml` 时发生未知错误：{e}")


if __name__ == "__main__":
    if not check_eula():
        input("按 Enter 键退出...")
    else:
        print("\n")
        print("="*60)
        print("欢迎使用 MoFox-Bot 配置向导！")
        print("接下来，我会引导你完成一些基本设置。")
        print("如果不想修改，直接按 Enter 键跳过即可。")
        print("="*60)
        print("\n")
        configure_bot()
        configure_model()
        print("\n\n==============================================")
        print("所有配置已完成！现在你可以启动主程序了。")
        print("==============================================")
        input("按 Enter 键退出...")
