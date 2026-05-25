#!/usr/bin/env python3
"""
简单测试脚本，验证提示词管理器功能
"""
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from agent.prompt_manager import PromptManager


def test_prompt_manager():
    print("=" * 70)
    print("提示词管理器测试")
    print("=" * 70)
    
    # 1. 初始化
    print("\n[1/8] 初始化 PromptManager...")
    pm = PromptManager()
    print("✓ 初始化成功")
    
    # 2. 列出模板
    print("\n[2/8] 列出所有模板...")
    templates = pm.list_templates()
    print(f"✓ 找到 {len(templates)} 个模板")
    for t in templates:
        print(f"  - {t.name}")
    
    # 3. 获取模板
    print("\n[3/8] 获取主播推荐模板...")
    template = pm.get_template("streamer_recommendation")
    assert template is not None, "模板不存在"
    print(f"✓ 成功获取模板，输入变量: {template.input_variables}")
    
    # 4. 格式化提示词
    print("\n[4/8] 测试格式化提示词...")
    result = pm.format_prompt(
        "streamer_recommendation",
        streamer_name="测试主播",
        streamer_tags="搞笑,游戏",
        streamer_content="每天直播有趣的内容",
        user_preferences="喜欢娱乐内容"
    )
    assert result is not None, "格式化失败"
    print("✓ 格式化成功")
    print(f"  结果预览: {result[:50]}...")
    
    # 5. 调试功能
    print("\n[5/8] 测试调试功能...")
    debug_info = pm.debug_prompt(
        "streamer_recommendation",
        streamer_name="测试",
        streamer_tags="测试标签"
    )
    assert debug_info is not None, "调试失败"
    print("✓ 调试功能正常")
    print(f"  缺失变量: {debug_info['missing_variables']}")
    
    # 6. 添加自定义模板
    print("\n[6/8] 测试添加自定义模板...")
    success = pm.add_template(
        name="test_template",
        template="Hello {name}!",
        description="Test template",
        category="test"
    )
    assert success, "添加模板失败"
    print("✓ 添加模板成功")
    
    # 7. 验证自定义模板
    print("\n[7/8] 验证自定义模板...")
    test_result = pm.format_prompt("test_template", name="World")
    assert test_result == "Hello World!", "模板格式化不正确"
    print(f"✓ 验证成功: {test_result}")
    
    # 8. 删除自定义模板
    print("\n[8/8] 测试删除自定义模板...")
    delete_success = pm.delete_template("test_template")
    assert delete_success, "删除模板失败"
    print("✓ 删除模板成功")
    
    print("\n" + "=" * 70)
    print("所有测试通过! ✓")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_prompt_manager()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
