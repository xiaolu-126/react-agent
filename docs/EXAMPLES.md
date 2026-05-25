
# 使用示例

本文件提供本项目的多种使用场景示例。

---

## 1. 基础 Agent 使用

### 简单问答

```python
from src.agent.react_agent import ReActAgent

# 创建 Agent
agent = ReActAgent()

# 简单问答
response = agent.run("你好，请介绍一下你自己")
print(response)
```

### 主播推荐

```python
from src.agent.react_agent import ReActAgent

agent = ReActAgent()

# 主播推荐
response = agent.run(
    "请推荐一位适合的主播",
    streamer_name="张三",
    user_preferences="喜欢游戏直播，风格幽默风趣"
)
print(response)
```

### 流式输出

```python
from src.agent.react_agent import ReActAgent

agent = ReActAgent()

# 流式输出
print("Agent 响应：")
for chunk in agent.stream(
    "请详细介绍一下如何开始直播",
    streamer_name="李四"
):
    print(chunk, end="", flush=True)
print()
```

---

## 2. 模型管理

### 切换模型

```python
from src.models.model_manager import ModelManager
from src.models.config import ModelType

# 创建模型管理器
model_manager = ModelManager()

# 查看可用模型
print("可用模型：", model_manager.get_available_models())

# 获取当前模型
print("当前模型：", model_manager.get_current_model())

# 切换到 Anthropic
model_manager.set_current_model(ModelType.ANTHROPIC)
print("切换后的模型：", model_manager.get_current_model())

# 获取模型实例
llm = model_manager.get_chat_model()
response = llm.invoke("你好")
print(response.content)
```

### 自定义模型配置

```python
from src.models.model_manager import ModelManager
from src.models.config import ModelType, ModelConfig, ModelManagerConfig

# 自定义配置
openai_config = ModelConfig(
    model_type=ModelType.OPENAI,
    model_name="gpt-4",
    api_key="your-api-key",
    temperature=0.8,
    max_tokens=4096
)

manager_config = ModelManagerConfig(
    default_model=ModelType.OPENAI,
    models={ModelType.OPENAI: openai_config}
)

# 使用自定义配置创建管理器
model_manager = ModelManager(config=manager_config)
```

---

## 3. 提示词管理

### 使用预设模板

```python
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 获取模板
template = pm.get_template("streamer_recommendation")
print("模板：", template.template)

# 获取模板数据
data = pm.get_template_data("streamer_recommendation")
print("输入变量：", data.input_variables)
```

### 格式化提示词

```python
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 格式化提示词
formatted = pm.format_prompt(
    "streamer_recommendation",
    streamer_name="王五",
    streamer_tags="游戏, 幽默",
    streamer_content="主打英雄联盟直播",
    user_preferences="喜欢游戏直播"
)
print(formatted)
```

### 添加自定义模板

```python
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 添加自定义模板
success = pm.add_template(
    name="custom_template",
    template="你是一名{role}，请回答用户的问题：{question}",
    description="自定义助手模板",
    category="custom"
)

if success:
    print("模板添加成功")

# 使用自定义模板
result = pm.format_prompt(
    "custom_template",
    role="编程助手",
    question="如何学习 Python"
)
print(result)
```

### 编辑和删除模板

```python
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 添加模板
pm.add_template(
    name="temp_template",
    template="旧模板",
    category="test"
)

# 编辑模板
pm.edit_template(
    name="temp_template",
    template="新模板内容：{content}",
    description="更新后的描述"
)

# 调试模板
debug_info = pm.debug_prompt("temp_template", content="测试内容")
print(debug_info)

# 删除模板
pm.delete_template("temp_template")
```

### 导出和导入模板

```python
from pathlib import Path
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 添加几个自定义模板
pm.add_template("export1", "模板1: {var1}", category="export")
pm.add_template("export2", "模板2: {var2}", category="export")

# 导出模板
export_file = Path("templates_export.json")
pm.export_templates(export_file, format="json")

# 创建新的 PromptManager 并导入
pm2 = PromptManager()
count = pm2.import_templates(export_file, overwrite=True)
print(f"导入了 {count} 个模板")
```

---

## 4. 知识库使用

### 添加文档

```python
from langchain_core.documents import Document
from src.tools.knowledge_base import KnowledgeBase

# 创建知识库
kb = KnowledgeBase(
    collection_name="streamer_kb",
    chunk_size=500,
    chunk_overlap=50
)

# 创建文档
docs = [
    Document(
        page_content="张三是一名知名的游戏主播，主要直播英雄联盟，风格幽默风趣。",
        metadata={"source": "doc1", "type": "streamer"}
    ),
    Document(
        page_content="李四专注于音乐直播，擅长吉他弹唱，拥有大量粉丝。",
        metadata={"source": "doc2", "type": "streamer"}
    )
]

# 添加文档
ids = kb.add_documents(docs)
print(f"添加了 {len(ids)} 个文档块")
```

### 从文件加载文档

```python
from src.tools.knowledge_base import KnowledgeBase
from src.tools.document_loader import DocumentLoader

kb = KnowledgeBase()
loader = DocumentLoader()

# 从单个文件加载
kb.add_document_from_path("data/streamer_info.txt")

# 从目录批量加载
kb.add_documents_from_directory("data/docs/")
```

### 相似度搜索

```python
from src.tools.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# 基本相似度搜索
results = kb.similarity_search("游戏主播", k=3)
for i, doc in enumerate(results, 1):
    print(f"结果 {i}：{doc.page_content}")
    print(f"元数据：{doc.metadata}\n")

# 带分数的搜索
results_with_score = kb.similarity_search_with_score("音乐", k=2)
for doc, score in results_with_score:
    print(f"相似度：{score:.4f}")
    print(f"内容：{doc.page_content}\n")
```

### MMR 搜索（多样化结果）

```python
from src.tools.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# MMR 搜索，获取更多样化的结果
results = kb.max_marginal_relevance_search(
    query="主播",
    k=4,
    lambda_mult=0.5  # 0 = 更多样化，1 = 更相关
)

for doc in results:
    print(doc.page_content)
```

### 删除文档

```python
from src.tools.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# 添加一些文档
from langchain_core.documents import Document
docs = [
    Document(page_content="临时文档1", metadata={"id": "temp1"}),
    Document(page_content="临时文档2", metadata={"id": "temp2"})
]
ids = kb.add_documents(docs)

# 根据 ID 删除
kb.delete_documents(ids[:1])

# 根据元数据删除
kb.delete_documents_by_metadata({"id": "temp2"})
```

### 持久化

```python
from src.tools.knowledge_base import KnowledgeBase

# 创建可持久化的知识库
kb = KnowledgeBase(
    collection_name="persistent_kb",
    persist_directory="./data/vectorstore"
)

# 添加文档
# ... 添加文档 ...

# 持久化到磁盘
kb.persist()

# 清空
kb.clear()

# 再次加载时会从磁盘恢复
kb2 = KnowledgeBase(
    collection_name="persistent_kb",
    persist_directory="./data/vectorstore"
)
```

---

## 5. 对话记忆

### 基本记忆使用

```python
from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

# 配置记忆
config = ChatMemoryConfig(
    max_token_limit=3000,
    use_summary=True
)

memory = ChatMemoryManager(config=config)

# 添加消息
memory.add_user_message("你好")
memory.add_ai_message("你好！有什么可以帮助你的？")
memory.add_user_message("推荐一些主播")
memory.add_ai_message("当然可以！请问你想看什么类型的直播？")

# 获取对话历史
history = memory.get_conversation_history()
for turn in history:
    print(f"[{turn.role}] {turn.content}")
```

### 获取 LangChain 格式

```python
from src.agent.memory import ChatMemoryManager

memory = ChatMemoryManager()

memory.add_user_message("Hi")
memory.add_ai_message("Hello!")

# 获取 LangChain 格式，可直接用于链
memory_vars = memory.get_memory_variables()
chat_history = memory.get_chat_history()

print("记忆变量：", memory_vars)
print("聊天历史：", chat_history)
```

### 保存和加载

```python
from src.agent.memory import ChatMemoryManager

memory = ChatMemoryManager()

# 添加一些对话
memory.add_user_message("问题1")
memory.add_ai_message("回答1")
memory.add_user_message("问题2")
memory.add_ai_message("回答2")

# 保存到文件
memory.save_to_file("saved_conversation.json")

# 从文件加载
loaded_memory = ChatMemoryManager.load_from_file("saved_conversation.json")

# 查看加载的对话
for turn in loaded_memory.get_conversation_history():
    print(f"{turn.role}: {turn.content}")
```

### 获取摘要

```python
from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

config = ChatMemoryConfig(use_summary=True)
memory = ChatMemoryManager(config=config)

# 添加多轮对话
for i in range(10):
    memory.add_user_message(f"用户问题 {i}")
    memory.add_ai_message(f"AI回答 {i}")

# 获取摘要
summary = memory.get_summary()
if summary:
    print("对话摘要：", summary)

# 查看统计信息
stats = memory.get_memory_stats()
print("记忆统计：", stats)
```

### 修剪历史

```python
from src.agent.memory import ChatMemoryManager

memory = ChatMemoryManager()

# 添加很多消息
for i in range(20):
    memory.add_user_message(f"消息 {i}")

print(f"修剪前消息数：{len(memory.get_conversation_history())}")

# 只保留最近 10 条
memory.prune_history(max_messages=10)

print(f"修剪后消息数：{len(memory.get_conversation_history())}")
```

---

## 6. 网络搜索

### 基本搜索

```python
from src.tools.web_search import WebSearch, SearchProvider

# 创建搜索实例
ws = WebSearch(
    provider=SearchProvider.SERPER,
    api_key="your-api-key",
    default_num_results=5
)

# 执行搜索
results = ws.search("最新游戏资讯")
for result in results:
    print(f"标题：{result.title}")
    print(f"链接：{result.url}")
    print(f"摘要：{result.snippet}\n")
```

### 格式化结果

```python
from src.tools.web_search import WebSearch

ws = WebSearch()

results = ws.search("人工智能")
formatted = ws.format_results(results)
print(formatted)
```

### 使用工具函数

```python
from src.tools.web_search import web_search

# 直接使用工具函数
result = web_search("Python 最新版本", num_results=3)
print(result)
```

---

## 7. Agent 与知识库和网络搜索集成

### 完整的主播推荐 Agent

```python
from src.agent.react_agent import ReActAgent
from src.models.model_manager import ModelManager
from src.agent.prompt_manager import PromptManager
from src.agent.memory import ChatMemoryManager
from src.tools.knowledge_base import KnowledgeBase
from src.tools.web_search import WebSearch

# 创建各个组件
model_manager = ModelManager()
prompt_manager = PromptManager()
memory_manager = ChatMemoryManager()
knowledge_base = KnowledgeBase()

# 添加一些主播信息到知识库
from langchain_core.documents import Document
docs = [
    Document(page_content="张小明是游戏主播，擅长射击游戏", metadata={"type": "streamer"}),
    Document(page_content="李小红是美食主播，直播做饭", metadata={"type": "streamer"})
]
knowledge_base.add_documents(docs)

# 创建集成的 Agent
agent = ReActAgent(
    model_manager=model_manager,
    prompt_manager=prompt_manager,
    memory_manager=memory_manager,
    knowledge_base=knowledge_base
)

# 运行 Agent
response = agent.run(
    "推荐一位游戏主播",
    user_preferences="喜欢射击游戏"
)
print(response)
```

### 多轮对话

```python
from src.agent.react_agent import ReActAgent

agent = ReActAgent()

# 第一轮
response1 = agent.run("你好，请推荐一位游戏主播")
print("第一轮：", response1)

# 第二轮（会记住上下文）
response2 = agent.run("这位主播的直播时间是什么时候？")
print("第二轮：", response2)

# 查看对话历史
history = agent.get_conversation_history()
print("\n对话历史：")
for turn in history:
    print(f"[{turn.role}] {turn.content}")

# 清空记忆
agent.clear_memory()
```

---

## 8. 高级示例

### 自定义提示词 + Agent

```python
from src.agent.prompt_manager import PromptManager
from src.agent.react_agent import ReActAgent

# 添加自定义模板
pm = PromptManager()
pm.add_template(
    name="my_prompt",
    template="""
你是一个专业的助手。
用户问题：{question}
请提供详细的回答。
""",
    category="custom"
)

# 创建 Agent
agent = ReActAgent(prompt_manager=pm)

# 使用
response = agent.run("如何提高编程能力")
print(response)
```

### 批量处理文档

```python
from pathlib import Path
from src.tools.document_loader import DocumentLoader
from src.tools.knowledge_base import KnowledgeBase

# 加载器
loader = DocumentLoader()
kb = KnowledgeBase()

# 处理目录
docs_dir = Path("data/documents")
if docs_dir.exists():
    # 加载所有文档
    all_docs = loader.load_documents(str(docs_dir), recursive=True)
    print(f"加载了 {len(all_docs)} 个文档")

    # 添加到知识库
    ids = kb.add_documents(all_docs)
    print(f"添加了 {len(ids)} 个文档块")

    # 搜索测试
    results = kb.similarity_search("重要信息", k=5)
    print(f"找到 {len(results)} 个相关片段")
```

### 使用不同的嵌入模型

```python
from src.tools.knowledge_base import KnowledgeBase
from langchain_openai import OpenAIEmbeddings
# 或者其他嵌入模型

# 使用自定义嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

kb = KnowledgeBase(
    collection_name="custom_embedding_kb",
    embedding_model=embeddings
)
```

---

## 9. 错误处理示例

### 安全的 API 调用

```python
from src.tools.web_search import WebSearch, SearchProvider

try:
    ws = WebSearch(
        provider=SearchProvider.SERPER,
        api_key="invalid-key"  # 无效的 key
    )
    results = ws.search("test")
except Exception as e:
    print(f"搜索出错：{e}")
    # 降级处理或提示用户
```

### 处理知识库操作

```python
from src.tools.knowledge_base import KnowledgeBase
from src.tools.document_loader import DocumentLoader

kb = KnowledgeBase()
loader = DocumentLoader()

try:
    docs = loader.load_document("nonexistent_file.pdf")
    kb.add_documents(docs)
except FileNotFoundError:
    print("文件不存在，请检查路径")
except Exception as e:
    print(f"处理文档时出错：{e}")
```

