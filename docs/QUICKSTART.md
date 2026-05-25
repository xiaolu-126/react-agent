
# 快速开始指南

本指南将帮助你快速上手使用这个基于 LangGraph 的智能 Agent 系统。

## 前置要求

- Python 3.10 或更高版本
- pip 包管理器

## 安装步骤

1. 克隆或下载项目到本地：
```bash
cd langgraph-agent
```

2. 安装项目依赖：
```bash
pip install -e .
```

或者使用 pip 安装：
```bash
pip install -e ".[dev]"
```

## 配置环境变量

在项目根目录创建 `.env` 文件，并配置以下环境变量：

```env
# OpenAI 配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic 配置（可选）
ANTHROPIC_API_KEY=your-anthropic-api-key

# 通义千问配置（可选）
DASHSCOPE_API_KEY=your-dashscope-api-key

# 文心一言配置（可选）
QIANFAN_API_KEY=your-qianfan-api-key
QIANFAN_SECRET_KEY=your-qianfan-secret-key

# SerpAPI 配置（网络搜索）
SERPER_API_KEY=your-serper-api-key

# Tavily 配置（网络搜索）
TAVILY_API_KEY=your-tavily-api-key

# Agent 配置
DEFAULT_MODEL=openai
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048
```

你可以复制 `config/.env.example` 并重命名为 `.env` 作为起点。

## 快速使用

### 1. 基础使用 - 运行 Agent

```python
from src.agent.react_agent import ReActAgent

# 创建 Agent
agent = ReActAgent()

# 运行 Agent
result = agent.run(
    "推荐一个游戏主播",
    streamer_name="某知名主播",
    user_preferences="喜欢玩射击游戏，风格幽默"
)

print(result)
```

### 2. 流式输出

```python
agent = ReActAgent()

for chunk in agent.stream(
    "推荐一个主播",
    streamer_name="主播名称",
    user_preferences="喜欢音乐直播"
):
    print(chunk, end="", flush=True)
```

### 3. 切换模型

```python
from src.models.config import ModelType

agent = ReActAgent()
agent.switch_model(ModelType.ANTHROPIC)  # 切换到 Anthropic
```

## 核心组件使用

### 模型管理器 (ModelManager)

```python
from src.models.model_manager import ModelManager
from src.models.config import ModelType

manager = ModelManager()

# 获取模型
model = manager.get_chat_model()

# 切换模型
manager.set_current_model(ModelType.DASHSCOPE)
```

### 提示词管理器 (PromptManager)

```python
from src.agent.prompt_manager import PromptManager

prompt_manager = PromptManager()

# 获取模板
template = prompt_manager.get_template("streamer_recommendation")

# 添加自定义模板
prompt_manager.add_template(
    name="my_template",
    template="你好，{name}！这是我的自定义模板。",
    description="我的模板",
    category="custom"
)

# 使用模板
formatted = prompt_manager.format_prompt("my_template", name="世界")
print(formatted)
```

### 知识库 (KnowledgeBase)

```python
from src.tools.knowledge_base import KnowledgeBase
from langchain_core.documents import Document

kb = KnowledgeBase()

# 添加文档
docs = [
    Document(page_content="主播A擅长游戏直播...", metadata={"source": "file1"}),
    Document(page_content="主播B擅长音乐直播...", metadata={"source": "file2"})
]
ids = kb.add_documents(docs)

# 搜索文档
results = kb.similarity_search("游戏主播", k=3)
for result in results:
    print(result.page_content)
```

### 对话记忆 (ChatMemoryManager)

```python
from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

config = ChatMemoryConfig(
    max_token_limit=4000,
    use_summary=True
)
memory = ChatMemoryManager(config=config)

# 添加消息
memory.add_user_message("你好")
memory.add_ai_message("你好，有什么可以帮助你？")

# 获取历史
history = memory.get_conversation_history()
```

## 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_agent.py

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 下一步

- 查看 [API.md](./API.md) 了解完整的 API 文档
- 查看 [EXAMPLES.md](./EXAMPLES.md) 获取更多使用示例
- 阅读项目的 [README.md](../README.md) 了解项目架构

