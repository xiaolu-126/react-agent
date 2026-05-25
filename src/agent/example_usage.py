"""
ReAct Agent 使用示例
"""
from pathlib import Path
import os

from .react_agent import ReActAgent
from .memory import ChatMemoryManager
from .prompt_manager import PromptManager
from src.models.model_manager import ModelManager
from src.tools.knowledge_base import KnowledgeBase
from src.tools.web_search import WebSearch
from src.models.config import ModelType


def main():
    """主函数 - 演示 ReAct Agent 的使用方法"""
    print("=" * 80)
    print("LangGraph ReAct Agent 使用示例")
    print("=" * 80)
    
    # 1. 初始化各个组件
    print("\n[1/5] 初始化组件...")
    print("-" * 80)
    
    model_manager = ModelManager()
    print(f"✓ 模型管理器初始化完成，当前模型: {model_manager.get_current_model().value}")
    
    prompt_manager = PromptManager()
    print(f"✓ 提示词管理器初始化完成，可用模板: {[t.name for t in prompt_manager.list_templates()]}")
    
    memory_manager = ChatMemoryManager()
    print("✓ 对话记忆管理器初始化完成")
    
    # 可选：初始化知识库
    knowledge_base = None
    try:
        knowledge_base = KnowledgeBase()
        print("✓ 知识库初始化完成")
    except Exception as e:
        print(f"⚠ 知识库初始化跳过: {e}")
    
    # 可选：初始化网络搜索
    web_search = None
    try:
        web_search = WebSearch()
        print("✓ 网络搜索初始化完成")
    except Exception as e:
        print(f"⚠ 网络搜索初始化跳过: {e}")
    
    # 2. 创建 ReAct Agent
    print("\n[2/5] 创建 ReAct Agent...")
    print("-" * 80)
    
    agent = ReActAgent(
        model_manager=model_manager,
        prompt_manager=prompt_manager,
        memory_manager=memory_manager,
        knowledge_base=knowledge_base,
        web_search=web_search,
        max_iterations=5
    )
    print("✓ ReAct Agent 创建完成")
    
    # 3. 示例 1: 基本使用
    print("\n[3/5] 示例 1: 基本使用（不调用工具）")
    print("-" * 80)
    
    input1 = "你好，请介绍一下你自己"
    print(f"\n用户输入: {input1}")
    print("\nAgent 回复:")
    response1 = agent.run(input1, stream=True)
    print(f"\n完整回复: {response1}")
    
    # 4. 示例 2: 查看对话历史
    print("\n[4/5] 示例 2: 查看对话历史")
    print("-" * 80)
    
    history = agent.get_conversation_history()
    print(f"✓ 对话历史共 {len(history)} 条")
    for turn in history:
        print(f"\n- {turn.role.upper()}: {turn.content}")
    
    # 5. 示例 3: 流式输出
    print("\n[5/5] 示例 3: 流式输出接口")
    print("-" * 80)
    
    input3 = "请帮我推荐一个有趣的主播"
    print(f"\n用户输入: {input3}")
    print("\nAgent 流式输出:")
    output3 = ""
    for chunk in agent.stream(input3):
        output3 += chunk
        print(chunk, end="", flush=True)
    print(f"\n\n完整回复: {output3}")
    
    # 6. 清空记忆（可选）
    print("\n" + "=" * 80)
    print("示例运行完成！")
    print("=" * 80)
    print("\n提示: 你可以:")
    print("- 使用 agent.run() 方法运行 Agent")
    print("- 使用 agent.stream() 方法获取流式输出")
    print("- 使用 agent.switch_model() 切换模型")
    print("- 使用 agent.get_conversation_history() 查看对话历史")
    print("- 使用 agent.clear_memory() 清空对话记忆")


def example_with_streamer_recommendation():
    """示例：主播推荐场景"""
    print("\n" + "=" * 80)
    print("主播推荐场景示例")
    print("=" * 80)
    
    # 创建 Agent
    agent = ReActAgent()
    
    # 模拟推荐场景
    streamer_name = "示例主播"
    user_preferences = "喜欢游戏直播，特别是搞笑互动类型的"
    
    print(f"\n主播: {streamer_name}")
    print(f"用户偏好: {user_preferences}")
    
    input_query = f"请帮我分析一下主播 {streamer_name}，用户偏好是 {user_preferences}，请生成推荐理由"
    print(f"\n查询: {input_query}")
    print("\nAgent 回复:")
    
    response = agent.run(
        input_query,
        streamer_name=streamer_name,
        user_preferences=user_preferences,
        stream=True
    )


def example_with_model_switch():
    """示例：模型切换"""
    print("\n" + "=" * 80)
    print("模型切换示例")
    print("=" * 80)
    
    agent = ReActAgent()
    
    print("\n当前可用模型:")
    for model in agent.model_manager.get_available_models():
        print(f"  - {model.value}")
    
    # 切换到 OpenAI
    print(f"\n切换到 OpenAI 模型...")
    agent.switch_model(ModelType.OPENAI)
    print(f"✓ 当前模型: {agent.model_manager.get_current_model().value}")
    
    # 测试
    response = agent.run("你好，简单介绍一下你自己", stream=False)
    print(f"\nAgent 回复: {response}")


if __name__ == "__main__":
    # 运行主示例
    main()
    
    # 可选：运行其他示例
    # example_with_streamer_recommendation()
    # example_with_model_switch()
