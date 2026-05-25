
#!/usr/bin/env python3
"""
Agent 演示脚本 - 展示 ReAct Agent 的使用
注意: 此脚本需要配置 API Key 才能运行
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("LangGraph Agent - ReAct Agent 演示")
print("=" * 60)


def create_mock_agent():
    """创建模拟的 Agent 用于演示（不实际调用 API）"""
    from unittest.mock import Mock, MagicMock
    from src.agent.react_agent import ReActAgent

    # 创建 mock 组件
    mock_model_manager = Mock()
    mock_prompt_manager = Mock()
    mock_memory = Mock()
    mock_web_search = Mock()

    # 创建 Agent
    agent = ReActAgent(
        model_manager=mock_model_manager,
        prompt_manager=mock_prompt_manager,
        memory_manager=mock_memory,
        web_search=mock_web_search
    )

    # Mock agent 的方法
    def mock_run(input_text, streamer_name=None, user_preferences=None, stream=False):
        print(f"\n[模拟] 处理请求...")
        print(f"  用户输入: {input_text}")
        if streamer_name:
            print(f"  主播名称: {streamer_name}")
        if user_preferences:
            print(f"  用户偏好: {user_preferences}")

        # 返回模拟的推荐理由
        return f"""
这是一个模拟的主播推荐。

根据您提供的信息，我为您推荐一位优秀的主播：

📢 主播：{streamer_name or '热门主播'}
🎯 特点：内容有趣，风格独特
👍 推荐理由：非常适合您的偏好！

希望您会喜欢！
        """.strip()

    agent.run = mock_run
    return agent


def demo_agent_basic():
    """演示基础的 Agent 使用"""
    print("\n1. 基础 Agent 演示")
    print("-" * 40)

    agent = create_mock_agent()

    print("运行 Agent...")
    response = agent.run(
        "请推荐一位游戏主播",
        streamer_name="小明",
        user_preferences="喜欢王者荣耀，风格幽默"
    )

    print("\nAgent 响应:")
    print("=" * 40)
    print(response)


def demo_agent_with_knowledge():
    """演示结合知识库的 Agent"""
    print("\n2. Agent + 知识库演示")
    print("-" * 40)

    from src.tools.knowledge_base import KnowledgeBase
    from langchain_core.documents import Document

    print("创建知识库...")
    kb = KnowledgeBase(
        collection_name="demo_streamers",
        persist_directory=None
    )

    # 添加示例文档
    docs = [
        Document(
            page_content="小明是王者荣耀主播，每晚7点开播，擅长打野位",
            metadata={"source": "demo", "type": "streamer"}
        ),
        Document(
            page_content="小红是原神主播，喜欢做攻略和开箱",
            metadata={"source": "demo", "type": "streamer"}
        )
    ]
    kb.add_documents(docs)
    print(f"知识库包含 {kb.get_document_count()} 个文档块")

    print("\n[模拟] Agent 可以使用知识库搜索相关信息")


def demo_agent_with_memory():
    """演示 Agent 的记忆功能"""
    print("\n3. Agent 对话记忆演示")
    print("-" * 40)

    from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

    config = ChatMemoryConfig(use_summary=False)
    memory = ChatMemoryManager(config=config)

    print("模拟多轮对话...")

    # 第一轮
    memory.add_user_message("你好，我想找个游戏主播")
    memory.add_ai_message("好的，请问你喜欢什么游戏？")

    # 第二轮
    memory.add_user_message("我喜欢玩王者荣耀")
    memory.add_ai_message("好的，我推荐小明主播，他很擅长王者荣耀！")

    # 显示历史
    history = memory.get_conversation_history()
    print(f"\n对话历史（共 {len(history)} 轮）:")
    for i, turn in enumerate(history, 1):
        print(f"  {i}. [{turn.role}] {turn.content}")


def main():
    """主函数"""
    try:
        print("\n注意: 这是一个模拟演示脚本")
        print("      要使用真实的 Agent，请先配置 API Key")
        print("      然后查看 docs/QUICKSTART.md 了解更多")

        demo_agent_basic()
        demo_agent_with_knowledge()
        demo_agent_with_memory()

        print("\n" + "=" * 60)
        print("Agent 演示完成！")
        print("=" * 60)
        print("\n提示:")
        print("  1. 请先配置 config/.env 文件")
        print("  2. 然后可以使用 'agent chat' 命令进行真实对话")
        print("  3. 更多示例请查看 docs/EXAMPLES.md")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

