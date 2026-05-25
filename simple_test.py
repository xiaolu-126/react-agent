#!/usr/bin/env python3
"""
简单测试，直接导入 prompt_manager
"""
import sys
from pathlib import Path

# 直接添加 src/agent 到路径
agent_path = Path(__file__).parent / "src" / "agent"
sys.path.insert(0, str(agent_path))

# 直接导入 prompt_manager
from prompt_manager import PromptManager


def test():
    print("=" * 60)
    print("提示词管理器 - 简单测试")
    print("=" * 60)
    
    # 初始化
    print("\n[1] 初始化...")
    pm = PromptManager()
    print("✓ 成功")
    
    # 列出模板
    print("\n[2] 列出模板...")
    templates = pm.list_templates()
    print(f"✓ 找到 {len(templates)} 个模板:")
    for t in templates:
        print(f"  - {t.name}")
    
    # 测试主播推荐模板
    print("\n[3] 测试主播推荐理由模板...")
    result = pm.format_prompt(
        "streamer_recommendation",
        streamer_name="小明",
        streamer_tags="游戏,娱乐",
        streamer_content="每天直播，互动性强",
        user_preferences="喜欢轻松的直播内容"
    )
    
    if result:
        print("✓ 格式化成功!")
        print("\n格式化结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)
    
    # 测试调试功能
    print("\n[4] 测试调试功能...")
    debug = pm.debug_prompt(
        "streamer_recommendation",
        streamer_name="测试",
        streamer_tags="测试标签"
    )
    
    if debug:
        print("✓ 调试成功!")
        print(f"\n调试信息:")
        print(f"  输入变量: {debug['input_variables']}")
        print(f"  缺失变量: {debug['missing_variables']}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
