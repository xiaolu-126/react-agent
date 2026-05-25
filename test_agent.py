#!/usr/bin/env python3
"""
简单测试文件，验证 ReAct Agent 的基本功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ReActAgent


def test_basic_functionality():
    """测试基本功能"""
    print("测试 ReAct Agent 基本功能...")
    print("=" * 60)
    
    try:
        # 创建 Agent
        agent = ReActAgent(max_iterations=3)
        print("✓ Agent 创建成功")
        
        # 测试基本对话
        test_input = "你好，请简单介绍一下你自己"
        print(f"\n测试输入: {test_input}")
        
        response = agent.run(test_input, stream=False)
        print(f"Agent 回复: {response}")
        
        print("\n✓ 基本功能测试通过！")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streaming_output():
    """测试流式输出"""
    print("\n测试流式输出...")
    print("=" * 60)
    
    try:
        agent = ReActAgent(max_iterations=3)
        
        test_input = "请说一段简短的话"
        print(f"\n测试输入: {test_input}")
        print("流式输出: ", end="", flush=True)
        
        output = ""
        for chunk in agent.stream(test_input):
            output += chunk
            print(chunk, end="", flush=True)
        
        print(f"\n\n完整输出: {output}")
        print("✓ 流式输出测试通过！")
        return True
    except Exception as e:
        print(f"\n✗ 流式输出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("ReAct Agent 简单测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("基本功能", test_basic_functionality()))
    results.append(("流式输出", test_streaming_output()))
    
    # 打印结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
