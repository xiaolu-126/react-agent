
# LangGraph 智能 Agent 项目

基于 LangGraph 构建的智能 Agent 项目，支持多种 LLM 模型和向量数据库，提供专业的主播推荐功能。

## 功能特性

- 🤖 **交互式聊天模式** - 与 Agent 进行自然语言对话
- 📢 **主播推荐生成** - 一键生成高质量的主播推荐理由
- 📚 **知识库管理** - 上传文档构建专属知识库
- 🔍 **网络搜索** - 集成搜索引擎获取实时信息
- 🔄 **多模型切换** - 支持 OpenAI、Anthropic、通义千问、文心一言
- 💾 **对话记忆** - 智能记忆多轮对话历史
- 📝 **提示词管理** - 灵活的模板系统
- 🎨 **友好的 CLI 界面** - 彩色输出，直观易用

## 项目结构

```
.
├── main.py              # 程序主入口
├── src/                 # 源代码目录
│   ├── agent/           # Agent 核心逻辑
│   │   ├── __init__.py
│   │   ├── memory.py         # 对话记忆管理
│   │   ├── prompt_manager.py # 提示词模板管理
│   │   ├── react_agent.py    # ReAct Agent 实现
│   │   └── example_usage.py
│   ├── models/          # 模型管理
│   │   ├── __init__.py
│   │   ├── config.py         # 模型配置
│   │   └── model_manager.py  # 模型管理器
│   ├── tools/           # 工具模块
│   │   ├── __init__.py
│   │   ├── document_loader.py # 文档加载器
│   │   ├── knowledge_base.py # 知识库
│   │   └── web_search.py      # 网络搜索
│   └── utils/           # 工具类
│       ├── __init__.py
│       └── config.py
├── config/              # 配置文件
│   ├── .env.example    # 配置示例
│   └── prompts/        # 提示词模板
│       ├── custom_prompts.example.json
│       └── example_templates.yaml
├── tests/               # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_prompt_manager.py
│   ├── test_knowledge_base.py
│   ├── test_web_search.py
│   ├── test_memory.py
│   ├── test_agent.py
│   └── test_integration.py
├── docs/                # 文档
│   ├── QUICKSTART.md   # 快速开始指南
│   ├── API.md          # API 参考文档
│   └── EXAMPLES.md     # 使用示例
├── pyproject.toml      # 项目配置
└── README.md
```

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone &lt;repository-url&gt;
cd langgraph-agent

# 安装依赖
pip install -e .
```

### 2. 配置

首次运行会自动创建配置文件：

```bash
# 复制示例配置
cp config/.env.example config/.env

# 编辑配置文件，填入你的 API 密钥
vim config/.env
```

需要配置的主要项：
- OpenAI/Anthropic/通义千问/文心一言的 API Key
- Serper/Tavily 的搜索 API Key（可选）

### 3. 运行

#### 查看所有可用命令

```bash
agent --help
```

#### 交互式聊天

```bash
agent chat
```

输入 `quit` 或 `exit` 退出，`clear` 清空对话历史。

#### 生成主播推荐

```bash
agent generate "主播名称"

# 带用户偏好
agent generate "主播名称" --preferences "喜欢游戏直播"

# 非流式输出
agent generate "主播名称" --no-stream
```

#### 上传文档到知识库

```bash
# 上传单个文件
agent upload-docs /path/to/document.pdf

# 上传整个目录
agent upload-docs /path/to/docs/

# 添加元数据
agent upload-docs /path/to/docs/ -m category=主播资料 -m source=官方
```

#### 管理模型

```bash
# 列出所有可用模型
agent list-models

# 切换模型
agent switch-model anthropic
```

#### 查看系统状态

```bash
agent status
```

## 文档

- [快速开始指南](./docs/QUICKSTART.md) - 详细的安装和入门教程
- [API 参考文档](./docs/API.md) - 完整的 API 说明
- [使用示例](./docs/EXAMPLES.md) - 各种使用场景的代码示例

## 测试

项目使用 pytest 进行测试。

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_agent.py

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行集成测试
pytest tests/test_integration.py
```

测试覆盖范围：
- 模型管理器测试
- 提示词管理测试
- 知识库测试
- 网络搜索测试
- 对话记忆测试
- Agent 集成测试
- 端到端集成测试

## 核心模块介绍

### 1. ModelManager (模型管理器)

支持多种 LLM 模型的统一管理：

```python
from src.models.model_manager import ModelManager
from src.models.config import ModelType

manager = ModelManager()

# 获取当前模型
llm = manager.get_chat_model()

# 切换模型
manager.set_current_model(ModelType.ANTHROPIC)
```

### 2. PromptManager (提示词管理器)

灵活的提示词模板系统：

```python
from src.agent.prompt_manager import PromptManager

pm = PromptManager()

# 添加自定义模板
pm.add_template(
    name="my_template",
    template="你是一个{role}，请回答：{question}"
)

# 格式化提示词
result = pm.format_prompt("my_template", role="助手", question="你好")
```

### 3. KnowledgeBase (知识库)

基于 ChromaDB 的向量存储：

```python
from src.tools.knowledge_base import KnowledgeBase
from langchain_core.documents import Document

kb = KnowledgeBase()

# 添加文档
docs = [Document(page_content="...", metadata={...})]
kb.add_documents(docs)

# 相似度搜索
results = kb.similarity_search("查询内容", k=5)
```

### 4. ChatMemoryManager (对话记忆)

管理多轮对话历史：

```python
from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

config = ChatMemoryConfig(
    max_token_limit=3000,
    use_summary=True
)
memory = ChatMemoryManager(config=config)

memory.add_user_message("你好")
memory.add_ai_message("你好！")

# 获取历史
history = memory.get_conversation_history()
```

### 5. ReActAgent (智能 Agent)

完整的 ReAct 模式 Agent：

```python
from src.agent.react_agent import ReActAgent

agent = ReActAgent()

response = agent.run(
    "推荐一位主播",
    streamer_name="主播名",
    user_preferences="喜欢游戏"
)
```

## 配置说明

配置文件位于 `config/.env`，主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEFAULT_MODEL` | 默认模型 | openai |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_API_BASE` | OpenAI API 基础 URL | https://api.openai.com/v1 |
| `OPENAI_MODEL` | OpenAI 模型名称 | gpt-4o |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `ANTHROPIC_MODEL` | Anthropic 模型名称 | claude-3-5-sonnet-20241022 |
| `DASHSCOPE_API_KEY` | 通义千问 API 密钥 | - |
| `DASHSCOPE_MODEL` | 通义千问模型名称 | qwen-max |
| `QIANFAN_API_KEY` | 文心一言 API 密钥 | - |
| `QIANFAN_SECRET_KEY` | 文心一言 Secret Key | - |
| `QIANFAN_MODEL` | 文心一言模型名称 | ernie-4.0 |
| `SERPER_API_KEY` | Serper 搜索 API 密钥 | - |
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | - |
| `CHROMA_DB_PATH` | ChromaDB 持久化路径 | ./chroma_db |
| `CHROMA_COLLECTION_NAME` | ChromaDB 集合名称 | agent_documents |
| `AGENT_TEMPERATURE` | Agent 温度参数 | 0.7 |
| `AGENT_MAX_TOKENS` | Agent 最大 Token 数 | 2048 |

## 支持的文档格式

- PDF (.pdf)
- 纯文本 (.txt)
- Markdown (.md, .markdown)
- 以及其他 LangChain 支持的格式

## 技术栈

- **LangGraph**: Agent 编排框架
- **LangChain**: LLM 应用开发框架
- **ChromaDB**: 向量数据库
- **Pydantic**: 数据验证
- **Click**: 命令行界面
- **OpenAI / Anthropic / 通义千问 / 文心一言**: LLM 模型支持
- **pytest**: 测试框架

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
black .
isort .
```

### 代码检查

```bash
mypy src/
```

## 常见问题

### Q: 首次运行提示缺少配置文件？
A: 程序会自动从 `config/.env.example` 复制创建 `config/.env`，请编辑该文件填入您的 API 密钥。

### Q: 如何添加自定义文档到知识库？
A: 使用 `agent upload-docs` 命令，可以上传单个文件或整个目录。

### Q: 支持哪些 LLM 模型？
A: 目前支持 OpenAI (GPT-4)、Anthropic (Claude)、通义千问、文心一言四种模型。

### Q: 如何运行测试？
A: 使用 `pytest tests/` 命令运行所有测试，或参考 [QUICKSTART.md](./docs/QUICKSTART.md) 获取更多详细信息。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

