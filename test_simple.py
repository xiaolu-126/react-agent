#!/usr/bin/env python3
"""
简单测试脚本 - 验证基本功能
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("LangGraph 主播推荐 Agent - 快速测试")
print("=" * 80)
print()

# 测试 1: 检查依赖
print("测试 1: 检查依赖导入...")
try:
    from src.agent.react_agent import ReActAgent
    from src.models.model_manager import ModelManager
    from src.agent.prompt_manager import PromptManager
    print("  ✓ 核心模块导入成功")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    sys.exit(1)

# 测试 2: 检查配置
print("\n测试 2: 检查配置文件...")
config_dir = Path("config")
env_example = config_dir / ".env.example"
if env_example.exists():
    print(f"  ✓ 配置示例文件存在: {env_example}")
else:
    print(f"  ✗ 配置示例文件不存在")

env_file = config_dir / ".env"
if env_file.exists():
    print(f"  ✓ 配置文件存在: {env_file}")
else:
    print(f"  ⚠ 配置文件不存在，请复制 .env.example 并填入 API 密钥")

# 测试 3: 测试模型管理器
print("\n测试 3: 测试模型管理器...")
try:
    manager = ModelManager()
    print(f"  ✓ 模型管理器初始化成功")
    print(f"  ✓ 当前模型: {manager.current_model_type}")
    print(f"  ✓ 可用模型: {', '.join(manager.get_available_models())}")
except Exception as e:
    print(f"  ✗ 模型管理器测试失败: {e}")

# 测试 4: 测试提示词管理器
print("\n测试 4: 测试提示词管理器...")
try:
    pm = PromptManager()
    print(f"  ✓ 提示词管理器初始化成功")
    print(f"  ✓ 可用模板: {', '.join([t.name for t in pm.list_templates()])}")
    
    # 测试主播推荐模板
    debug_info = pm.debug_prompt(
        "streamer_recommendation",
        streamer_name="岑先生",
        streamer_tags="音乐,互动",
        streamer_content="优质音乐内容",
        user_preferences="喜欢音乐类直播"
    )
    if debug_info:
        print(f"  ✓ 主播推荐模板测试成功")
except Exception as e:
    print(f"  ✗ 提示词管理器测试失败: {e}")

# 显示使用说明
print("\n" + "=" * 80)
print("使用说明")
print("=" * 80)
print()
print("1. 配置 API 密钥:")
print("   cp config/.env.example config/.env")
print("   编辑 config/.env，填入你的 API 密钥")
print()
print("2. 生成主播推荐理由:")
print("   python main.py generate \"岑先生\" --preferences \"喜欢音乐类直播\"")
print()
print("3. 交互式聊天:")
print("   python main.py chat")
print()
print("4. 查看更多帮助:")
print("   python main.py --help")
print()
print("=" * 80)
print()
