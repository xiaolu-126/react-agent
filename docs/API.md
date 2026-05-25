
# API 参考文档

本文件包含项目中所有主要类和函数的完整 API 参考。

## 目录
- [Agent 模块](#agent-模块)
  - [ReActAgent](#reactagent)
  - [PromptManager](#promptmanager)
  - [ChatMemoryManager](#chatmemorymanager)
- [Model 模块](#model-模块)
  - [ModelManager](#modelmanager)
  - [ModelType](#modeltype)
  - [ModelConfig](#modelconfig)
  - [ModelManagerConfig](#modelmanagerconfig)
- [Tools 模块](#tools-模块)
  - [KnowledgeBase](#knowledgebase)
  - [DocumentLoader](#documentloader)
  - [WebSearch](#websearch)

---

## Agent 模块

### ReActAgent

基于 LangGraph 的 ReAct 模式 Agent，可用于主播推荐等任务。

#### 初始化

```python
ReActAgent(
    model_manager: Optional[ModelManager] = None,
    prompt_manager: Optional[PromptManager] = None,
    memory_manager: Optional[ChatMemoryManager] = None,
    knowledge_base: Optional[KnowledgeBase] = None,
    web_search: Optional[WebSearch] = None,
    max_iterations: int = 5
)
```

**参数：**
- `model_manager`：模型管理器，若不提供则自动创建
- `prompt_manager`：提示词管理器，若不提供则自动创建
- `memory_manager`：对话记忆管理器，若不提供则自动创建
- `knowledge_base`：知识库，可选
- `web_search`：网络搜索工具，若不提供则自动创建
- `max_iterations`：最大迭代次数，默认 5

#### 方法

##### `run()`
运行 Agent 并返回结果。

```python
def run(
    self,
    input: str,
    streamer_name: Optional[str] = None,
    user_preferences: Optional[str] = None,
    stream: bool = False
) -&gt; str
```

**参数：**
- `input`：用户输入文本
- `streamer_name`：主播名称，可选
- `user_preferences`：用户偏好，可选
- `stream`：是否使用流式输出，默认 False

**返回：** Agent 的最终响应字符串

##### `stream()`
流式输出运行结果。

```python
def stream(
    self,
    input: str,
    streamer_name: Optional[str] = None,
    user_preferences: Optional[str] = None
) -&gt; Generator[str, None, None]
```

**参数：**
- `input`：用户输入文本
- `streamer_name`：主播名称，可选
- `user_preferences`：用户偏好，可选

**返回：** 生成器，逐个返回输出块

##### `get_conversation_history()`
获取对话历史。

```python
def get_conversation_history(self) -&gt; List[ConversationTurn]
```

**返回：** ConversationTurn 对象列表

##### `clear_memory()`
清空对话记忆。

```python
def clear_memory(self) -&gt; None
```

##### `switch_model()`
切换模型。

```python
def switch_model(self, model_type: ModelType) -&gt; None
```

**参数：**
- `model_type`：要切换到的模型类型

---

### PromptManager

提示词模板管理器，用于管理和使用提示词模板。

#### 初始化

```python
PromptManager(config_dir: Optional[Path] = None)
```

**参数：**
- `config_dir`：配置目录路径，默认为项目根目录的 `config/prompts`

#### 方法

##### `get_template()`
获取 LangChain PromptTemplate 对象。

```python
def get_template(self, name: str) -&gt; Optional[PromptTemplate]
```

**参数：**
- `name`：模板名称

**返回：** PromptTemplate 对象，不存在则返回 None

##### `get_template_data()`
获取提示词模板数据。

```python
def get_template_data(self, name: str) -&gt; Optional[PromptTemplateData]
```

**参数：**
- `name`：模板名称

**返回：** PromptTemplateData 对象，不存在则返回 None

##### `list_templates()`
列出所有提示词模板。

```python
def list_templates(self, category: Optional[str] = None) -&gt; List[PromptTemplateData]
```

**参数：**
- `category`：分类筛选，可选

**返回：** PromptTemplateData 列表

##### `add_template()`
添加自定义提示词模板。

```python
def add_template(
    self,
    name: str,
    template: str,
    input_variables: Optional[List[str]] = None,
    description: str = "",
    category: str = "default"
) -&gt; bool
```

**参数：**
- `name`：模板名称
- `template`：模板内容
- `input_variables`：输入变量列表，可选，会自动从模板提取
- `description`：描述，可选
- `category`：分类，默认 "default"

**返回：** 是否添加成功

##### `edit_template()`
编辑提示词模板。

```python
def edit_template(
    self,
    name: str,
    template: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    description: Optional[str] = None,
    category: Optional[str] = None
) -&gt; bool
```

**参数：**
- `name`：模板名称
- `template`：新的模板内容，可选
- `input_variables`：新的输入变量列表，可选
- `description`：新的描述，可选
- `category`：新的分类，可选

**返回：** 是否编辑成功

##### `delete_template()`
删除提示词模板。

```python
def delete_template(self, name: str) -&gt; bool
```

**参数：**
- `name`：模板名称

**返回：** 是否删除成功

##### `format_prompt()`
格式化提示词。

```python
def format_prompt(self, name: str, **kwargs: Any) -&gt; Optional[str]
```

**参数：**
- `name`：模板名称
- `**kwargs`：模板变量值

**返回：** 格式化后的字符串，失败则返回 None

##### `debug_prompt()`
调试提示词，显示完整信息。

```python
def debug_prompt(self, name: str, **kwargs: Any) -&gt; Optional[Dict[str, Any]]
```

**参数：**
- `name`：模板名称
- `**kwargs`：模板变量值

**返回：** 包含调试信息的字典

##### `export_templates()`
导出所有提示词模板。

```python
def export_templates(self, file_path: Path, format: str = "json") -&gt; bool
```

**参数：**
- `file_path`：导出文件路径
- `format`：格式，"json" 或 "yaml"

**返回：** 是否导出成功

##### `import_templates()`
导入提示词模板。

```python
def import_templates(self, file_path: Path, overwrite: bool = False) -&gt; int
```

**参数：**
- `file_path`：导入文件路径
- `overwrite`：是否覆盖已存在的模板，默认 False

**返回：** 成功导入的模板数量

---

### ChatMemoryManager

对话记忆管理器，管理多轮对话的上下文。

#### 初始化

```python
ChatMemoryManager(
    config: Optional[ChatMemoryConfig] = None,
    llm: Optional[ChatOpenAI] = None
)
```

**参数：**
- `config`：配置对象
- `llm`：用于生成摘要的 LLM

#### 方法

##### `add_user_message()`
添加用户消息。

```python
def add_user_message(self, content: str) -&gt; None
```

**参数：**
- `content`：消息内容

##### `add_ai_message()`
添加 AI 回复消息。

```python
def add_ai_message(self, content: str) -&gt; None
```

**参数：**
- `content`：消息内容

##### `add_system_message()`
添加系统提示消息。

```python
def add_system_message(self, content: str) -&gt; None
```

**参数：**
- `content`：消息内容

##### `add_message()`
添加任意类型的消息。

```python
def add_message(self, message: BaseMessage) -&gt; None
```

**参数：**
- `message`：BaseMessage 对象

##### `get_memory_variables()`
获取 LangChain Memory 格式的变量字典。

```python
def get_memory_variables(self) -&gt; Dict[str, Any]
```

**返回：** 包含 chat_history 的字典

##### `get_chat_history()`
获取 LangChain 格式的对话历史。

```python
def get_chat_history(self) -&gt; List[BaseMessage]
```

**返回：** BaseMessage 列表

##### `get_conversation_history()`
获取结构化的对话历史。

```python
def get_conversation_history(self) -&gt; List[ConversationTurn]
```

**返回：** ConversationTurn 列表

##### `clear()`
清空所有对话历史和记忆。

```python
def clear(self) -&gt; None
```

##### `save_to_file()`
保存对话历史到文件。

```python
def save_to_file(self, file_path: str) -&gt; None
```

**参数：**
- `file_path`：保存文件路径

##### `load_from_file()`
从文件加载对话历史。

```python
@classmethod
def load_from_file(cls, file_path: str, llm: Optional[ChatOpenAI] = None) -&gt; ChatMemoryManager
```

**参数：**
- `file_path`：加载文件路径
- `llm`：可选的 ChatOpenAI 实例

**返回：** ChatMemoryManager 实例

##### `get_summary()`
获取对话历史的摘要（如果启用）。

```python
def get_summary(self) -&gt; Optional[str]
```

**返回：** 摘要字符串，未启用则返回 None

##### `prune_history()`
手动修剪对话历史。

```python
def prune_history(self, max_messages: Optional[int] = None) -&gt; None
```

**参数：**
- `max_messages`：保留的最大消息数量

##### `get_memory_stats()`
获取记忆管理器的统计信息。

```python
def get_memory_stats(self) -&gt; Dict[str, Any]
```

**返回：** 统计信息字典

---

## Model 模块

### ModelManager

模型管理器，负责配置、初始化和切换不同的 LLM 模型。

#### 初始化

```python
ModelManager(config: Optional[ModelManagerConfig] = None)
```

**参数：**
- `config`：模型管理器配置，若不提供则从环境变量加载

#### 方法

##### `get_chat_model()`
获取指定类型的聊天模型。

```python
def get_chat_model(self, model_type: Optional[ModelType] = None) -&gt; BaseChatModel
```

**参数：**
- `model_type`：模型类型，可选，默认使用当前模型

**返回：** BaseChatModel 实例

**异常：** ValueError - 如果模型类型未配置

##### `set_current_model()`
设置当前使用的模型。

```python
def set_current_model(self, model_type: ModelType) -&gt; None
```

**参数：**
- `model_type`：要切换到的模型类型

**异常：** ValueError - 如果模型类型未配置

##### `get_current_model()`
获取当前使用的模型类型。

```python
def get_current_model(self) -&gt; ModelType
```

**返回：** 当前 ModelType

##### `get_available_models()`
获取所有可用的模型类型列表。

```python
def get_available_models(self) -&gt; List[ModelType]
```

**返回：** ModelType 列表

##### `update_model_config()`
更新指定模型的配置。

```python
def update_model_config(self, model_type: ModelType, config: ModelConfig) -&gt; None
```

**参数：**
- `model_type`：模型类型
- `config`：新的 ModelConfig

---

### ModelType

支持的模型类型枚举。

**成员：**
- `OPENAI` - OpenAI 模型
- `ANTHROPIC` - Anthropic 模型
- `DASHSCOPE` - 通义千问模型
- `QIANFAN` - 文心一言模型

---

### ModelConfig

单个模型的配置。

**字段：**
- `model_type: ModelType` - 模型类型
- `model_name: str` - 模型名称
- `api_key: Optional[str]` - API 密钥
- `api_base: Optional[str]` - API 基础 URL
- `temperature: float` - 温度参数，默认 0.7
- `max_tokens: int` - 最大 token 数，默认 2048

---

### ModelManagerConfig

模型管理器配置。

**字段：**
- `default_model: ModelType` - 默认模型类型，默认 ModelType.OPENAI
- `models: Dict[ModelType, ModelConfig]` - 模型配置字典

---

## Tools 模块

### KnowledgeBase

知识库核心类，集成向量存储、文档管理和检索功能。

#### 初始化

```python
KnowledgeBase(
    collection_name: str = "knowledge_base",
    persist_directory: Optional[str] = None,
    embedding_model: Optional[Embeddings] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
)
```

**参数：**
- `collection_name`：向量数据库集合名称，默认 "knowledge_base"
- `persist_directory`：持久化目录，可选
- `embedding_model`：嵌入模型，默认使用 OpenAIEmbeddings
- `chunk_size`：文档分块大小，默认 1000
- `chunk_overlap`：分块重叠大小，默认 200

#### 方法

##### `add_documents()`
添加文档到知识库。

```python
def add_documents(
    self,
    documents: List[Document],
    metadata: Optional[Dict[str, Any]] = None
) -&gt; List[str]
```

**参数：**
- `documents`：Document 列表
- `metadata`：附加元数据

**返回：** 添加的文档 ID 列表

##### `add_document_from_path()`
从文件路径添加文档。

```python
def add_document_from_path(
    self,
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -&gt; List[str]
```

**参数：**
- `file_path`：文件路径
- `metadata`：附加元数据

**返回：** 添加的文档 ID 列表

##### `add_documents_from_directory()`
从目录批量添加文档。

```python
def add_documents_from_directory(
    self,
    directory: str,
    recursive: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -&gt; List[str]
```

**参数：**
- `directory`：目录路径
- `recursive`：是否递归，默认 True
- `metadata`：附加元数据

**返回：** 添加的文档 ID 列表

##### `delete_documents()`
根据 ID 删除文档。

```python
def delete_documents(self, ids: List[str]) -&gt; None
```

**参数：**
- `ids`：文档 ID 列表

##### `delete_documents_by_metadata()`
根据元数据过滤删除文档。

```python
def delete_documents_by_metadata(self, filter_dict: Dict[str, Any]) -&gt; None
```

**参数：**
- `filter_dict`：过滤条件字典

##### `update_document()`
更新文档。

```python
def update_document(self, doc_id: str, new_document: Document) -&gt; None
```

**参数：**
- `doc_id`：文档 ID
- `new_document`：新 Document

##### `similarity_search()`
相似度搜索。

```python
def similarity_search(
    self,
    query: str,
    k: int = 4,
    filter_dict: Optional[Dict[str, Any]] = None
) -&gt; List[Document]
```

**参数：**
- `query`：查询文本
- `k`：返回结果数量，默认 4
- `filter_dict`：元数据过滤条件

**返回：** Document 列表

##### `similarity_search_with_score()`
相似度搜索，带分数。

```python
def similarity_search_with_score(
    self,
    query: str,
    k: int = 4,
    filter_dict: Optional[Dict[str, Any]] = None
) -&gt; List[Tuple[Document, float]]
```

**参数：**
- `query`：查询文本
- `k`：返回结果数量，默认 4
- `filter_dict`：元数据过滤条件

**返回：** (Document, score) 元组列表

##### `max_marginal_relevance_search()`
MMR（最大边际相关性）搜索。

```python
def max_marginal_relevance_search(
    self,
    query: str,
    k: int = 4,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
    filter_dict: Optional[Dict[str, Any]] = None
) -&gt; List[Document]
```

**参数：**
- `query`：查询文本
- `k`：返回结果数量，默认 4
- `fetch_k`：预取文档数量，默认 20
- `lambda_mult`：多样性参数，默认 0.5
- `filter_dict`：元数据过滤条件

**返回：** Document 列表

##### `as_retriever()`
获取检索器。

```python
def as_retriever(
    self,
    search_type: str = "similarity",
    search_kwargs: Optional[Dict[str, Any]] = None
) -&gt; VectorStoreRetriever
```

**参数：**
- `search_type`：检索类型，默认 "similarity"
- `search_kwargs`：检索参数字典

**返回：** VectorStoreRetriever 实例

##### `get_document_count()`
获取知识库中的文档块数量。

```python
def get_document_count(self) -&gt; int
```

**返回：** 文档块数量

##### `clear()`
清空知识库。

```python
def clear(self) -&gt; None
```

##### `persist()`
持久化知识库到磁盘。

```python
def persist(self) -&gt; None
```

---

### DocumentLoader

文档加载器，支持多种格式文档的加载。

#### 初始化

```python
DocumentLoader()
```

#### 方法

##### `load_document()`
加载单个文档。

```python
def load_document(self, file_path: str) -&gt; List[Document]
```

**参数：**
- `file_path`：文件路径

**返回：** Document 列表

**异常：**
- FileNotFoundError - 文件不存在
- ValueError - 不支持的文件格式

##### `load_documents()`
批量加载目录下的文档。

```python
def load_documents(self, directory: str, recursive: bool = True) -&gt; List[Document]
```

**参数：**
- `directory`：目录路径
- `recursive`：是否递归，默认 True

**返回：** Document 列表

**支持的格式：**
- PDF (.pdf)
- 文本 (.txt)
- Markdown (.md, .markdown)

---

### WebSearch

网络搜索工具类。

#### 初始化

```python
WebSearch(
    provider: SearchProvider = SearchProvider.SERPER,
    api_key: Optional[str] = None,
    default_num_results: int = 5,
    max_num_results: int = 10
)
```

**参数：**
- `provider`：搜索提供商，默认 SERPER
- `api_key`：API 密钥，可选
- `default_num_results`：默认结果数，默认 5
- `max_num_results`：最大结果数，默认 10

#### 方法

##### `search()`
执行网络搜索。

```python
def search(self, query: str, num_results: Optional[int] = None) -&gt; List[SearchResult]
```

**参数：**
- `query`：查询文本
- `num_results`：结果数量，可选

**返回：** SearchResult 列表

##### `format_results()`
格式化搜索结果。

```python
def format_results(self, results: List[SearchResult]) -&gt; str
```

**参数：**
- `results`：SearchResult 列表

**返回：** 格式化的字符串

---

### web_search()

网络搜索工具函数，供 Agent 使用。

```python
def web_search(query: str, num_results: int = 5) -&gt; str
```

**参数：**
- `query`：查询文本
- `num_results`：结果数量，默认 5

**返回：** 格式化的搜索结果字符串

---

## 数据结构

### PromptTemplateData

提示词模板数据结构。

**字段：**
- `name: str` - 模板名称
- `template: str` - 模板内容
- `input_variables: List[str]` - 输入变量列表
- `description: str` - 描述
- `category: str` - 分类

---

### SearchResult

搜索结果数据结构。

**字段：**
- `title: str` - 标题
- `url: str` - URL
- `snippet: str` - 摘要
- `source: Optional[str]` - 来源

---

### ConversationTurn

单个对话轮次的数据结构。

**字段：**
- `timestamp: str` - 时间戳
- `role: str` - 角色类型
- `content: str` - 内容

---

### ChatMemoryConfig

对话记忆管理器的配置类。

**字段：**
- `max_token_limit: int` - 最大 token 限制，默认 2000
- `use_summary: bool` - 是否使用摘要，默认 True
- `summary_model: str` - 摘要模型，默认 "gpt-3.5-turbo"
- `temperature: float` - 摘要温度，默认 0.0

---

### AgentState

ReAct Agent 的状态结构。

**字段：**
- `messages: Annotated[Sequence[BaseMessage], add]` - 消息列表
- `input: str` - 用户输入
- `streamer_name: Optional[str]` - 主播名称
- `tools: List[Any]` - 可用工具
- `tool_calls: List[Dict[str, Any]]` - 工具调用历史
- `observations: List[str]` - 观察结果
- `final_output: Optional[str]` - 最终输出
- `user_preferences: Optional[str]` - 用户偏好

