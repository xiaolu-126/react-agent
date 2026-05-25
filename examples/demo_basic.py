
#!/usr/bin/env python3
"""
基本演示脚本 - 展示核心功能的简单使用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("LangGraph Agent - 基础功能演示")
print("=" * 60)


def demo_prompt_manager():
    """演示提示词管理器"""
    print("\n1. 提示词管理器演示")
    print("-" * 40)

    from src.agent.prompt_manager import PromptManager

    pm = PromptManager()

    # 列出所有模板
    templates = pm.list_templates()
    print(f"找到 {len(templates)} 个模板:")
    for t in templates:
        print(f"  - {t.name} ({t.category})")

    # 添加自定义模板
    print("\n添加自定义模板...")
    success = pm.add_template(
        name="demo_template",
        template="你是一个{role}，请为用户提供{topic}相关的帮助。",
        input_variables=["role", "topic"],
        description="演示用模板",
        category="demo"
    )
    print(f"添加成功: {success}")

    # 格式化模板
    print("\n格式化提示词...")
    result = pm.format_prompt("demo_template", role="主播推荐官", topic="游戏主播")
    print(result)


def demo_memory():
    """演示对话记忆"""
    print("\n2. 对话记忆演示")
    print("-" * 40)

    from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

    config = ChatMemoryConfig(
        max_token_limit=2000,
        use_summary=False
    )
    memory = ChatMemoryManager(config=config)

    # 添加对话
    print("添加对话历史...")
    memory.add_user_message("你好！")
    memory.add_ai_message("你好！有什么可以帮助你的？")
    memory.add_user_message("我想找一个游戏主播")
    memory.add_ai_message("好的，请问你喜欢什么类型的游戏？")

    # 获取历史
    history = memory.get_conversation_history()
    print(f"历史记录数: {len(history)}")
    for turn in history:
        print(f"  [{turn.role}] {turn.content}")

    # 获取统计
    stats = memory.get_memory_stats()
    print(f"\n统计信息: {stats}")


def demo_document_loader():
    """演示文档加载器"""
    print("\n3. 文档加载器演示")
    print("-" * 40)

    from src.tools.document_loader import DocumentLoader

    loader = DocumentLoader()

    # 加载示例文档
    data_dir = Path(__file__).parent / "data"
    demo_file = data_dir / "streamer_demo.txt"

    if demo_file.exists():
        print(f"加载文件: {demo_file}")
        docs = loader.load_document(str(demo_file))
        print(f"加载文档数: {len(docs)}")
        if docs:
            content = docs[0].page_content[:200]
            print(f"文档预览: {content}...")
    else:
        print("示例文件不存在，跳过加载演示")


def demo_knowledge_base():
    """演示知识库（内存模式）"""
    print("\n4. 知识库演示（内存模式）")
    print("-" * 40)

    from src.tools.knowledge_base import KnowledgeBase
    from langchain_core.documents import Document

    # 创建内存知识库
    kb = KnowledgeBase(
        collection_name="demo_collection",
        persist_directory=None  # 内存模式
    )

    # 添加示例文档
    print("添加文档...")
    docs = [
        Document(
            page_content="小明是一位游戏主播，主要玩王者荣耀，风格幽默",
            metadata={"source": "demo", "type": "streamer"}
        ),
        Document(
            page_content="小红是音乐主播，擅长吉他弹唱",
            metadata={"source": "demo", "type": "streamer"}
        ),
        Document(
            page_content="大胃王是美食主播，喜欢探店",
            metadata={"source": "demo", "type": "streamer"}
        )
    ]
    ids = kb.add_documents(docs)
    print(f"添加了 {len(ids)} 个文档块")

    # 搜索
    print("\n搜索: '游戏主播'")
    results = kb.similarity_search("游戏主播", k=2)
    for i, doc in enumerate(results, 1):
        print(f"  结果 {i}: {doc.page_content}")


def main():
    """主函数"""
    try:
        demo_prompt_manager()
        demo_memory()
        demo_document_loader()
        demo_knowledge_base()

        print("\n" + "=" * 60)
        print("基础功能演示完成！")
        print("=" * 60)
        print("\n更多示例请查看:")
        print("  - examples/demo_agent.py")
        print("  - docs/EXAMPLES.md")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n注意: 部分功能需要配置 API Key 才能正常运行")
        print("请复制 config/.env.example 为 config/.env 并配置相关密钥")


if __name__ == "__main__":
    main()

