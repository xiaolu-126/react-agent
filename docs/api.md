# AI Agent API 文档

## 基础信息

- **基础 URL**: `http://localhost:8000/api/v1`
- **Swagger 文档**: `http://localhost:8000/docs`
- **ReDoc 文档**: `http://localhost:8000/redoc`
- **API 版本**: `1.0.0`

## 启动服务

```bash
# 默认启动（127.0.0.1:8000）
python main.py api

# 自定义主机和端口
python main.py api --host 0.0.0.0 --port 8080

# 开发模式（热重载）
python main.py api --reload
```

---

## 目录

1. [聊天 API](#1-聊天-api)
2. [推荐生成 API](#2-推荐生成-api)
3. [模型管理 API](#3-模型管理-api)
4. [系统提示词管理 API](#4-系统提示词管理-api)
5. [知识库管理 API](#5-知识库管理-api)
6. [自定义提示词管理 API](#6-自定义提示词管理-api)
7. [系统信息 API](#7-系统信息-api)

---

## 1. 聊天 API

### 1.1 发送聊天消息（非流式）

发送消息给 Agent，等待完整回复。

- **POST** `/chat`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | ✅ | 用户消息 |
| `streamer_name` | string | ❌ | 主播名称 |
| `user_preferences` | string | ❌ | 用户偏好 |

#### 请求示例

```json
{
  "message": "推荐几位技术型游戏主播",
  "streamer_name": null,
  "user_preferences": "喜欢观看游戏攻略和技术教学"
}
```

#### 响应示例

```json
{
  "reply": "为你推荐以下技术型游戏主播...",
  "conversation_id": "default"
}
```

---

### 1.2 流式聊天（SSE）

发送消息给 Agent，通过 Server-Sent Events 获取流式回复。

- **POST** `/chat/stream`
- **Content-Type**: `application/json`

#### 请求参数

同 `/chat` 接口。

#### SSE 事件格式

| 事件类型 | 说明 |
|---------|------|
| `chunk` | 内容片段 |
| `done` | 回复完成，`data` 为完整内容 |
| `error` | 发生错误 |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "推荐一位游戏主播"}'
```

#### 响应示例（SSE 流）

```
event: chunk
data: 为你推荐

event: chunk
data: 以下主播

event: done
data: 为你推荐以下主播...
```

---

## 2. 推荐生成 API

### 2.1 生成主播推荐理由（非流式）

根据主播名称和相关信息生成推荐理由。

- **POST** `/generate`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `streamer_name` | string | ✅ | 主播名称 |
| `tags` | string | ❌ | 主播标签（如"游戏主播、技术分享"）|
| `content` | string | ❌ | 主播内容简介 |
| `preferences` | string | ❌ | 用户偏好 |

#### 请求示例

```json
{
  "streamer_name": "岑先生",
  "tags": "游戏主播、技术分享",
  "content": "专注于游戏攻略和技术教学",
  "preferences": "喜欢技术型主播"
}
```

#### 响应示例

```json
{
  "streamer_name": "岑先生",
  "recommendation": "🎯 为你精准推荐：岑先生\n\n如果你是一位热爱硬核内容、追求技术深度的观众，那岑先生绝对是你不容错过的宝藏主播！\n\n🔥 为什么岑先生适合你？\n...",
  "sources": []
}
```

---

### 2.2 流式生成推荐理由（SSE）

根据主播名称流式生成推荐理由。

- **POST** `/generate/stream`
- **Content-Type**: `application/json`

#### 请求参数

同 `/generate` 接口。

#### SSE 事件格式

同 `/chat/stream` 接口。

---

## 3. 模型管理 API

### 3.1 获取模型列表

获取所有可用模型及当前使用的模型。

- **GET** `/models`

#### 请求示例

```bash
curl "http://localhost:8000/api/v1/models"
```

#### 响应示例

```json
{
  "models": [
    {
      "name": "openai",
      "display_name": "GPT-4 / GPT-3.5",
      "is_current": false
    },
    {
      "name": "deepseek",
      "display_name": "DeepSeek",
      "is_current": true
    }
  ],
  "current": "deepseek"
}
```

---

### 3.2 切换模型

切换到指定模型。

- **POST** `/models/switch`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model_type` | string | ✅ | 模型类型，可选值: `openai`, `anthropic`, `dashscope`, `qianfan`, `deepseek` |

#### 请求示例

```json
{
  "model_type": "deepseek"
}
```

#### 响应示例

```json
{
  "name": "deepseek",
  "display_name": "DeepSeek",
  "is_current": true
}
```

---

## 4. 系统提示词管理 API

### 4.1 获取系统提示词列表

获取所有可用的系统提示词列表。

- **GET** `/system-prompts`

#### 请求示例

```bash
curl "http://localhost:8000/api/v1/system-prompts"
```

#### 响应示例

```json
{
  "prompts": [
    {
      "name": "streamer_recommender",
      "description": "主播推荐专家 - 用于生成主播推荐理由",
      "category": "recommendation",
      "is_current": true
    },
    {
      "name": "general_assistant",
      "description": "通用AI助手 - 日常对话和问题解答",
      "category": "general",
      "is_current": false
    },
    {
      "name": "code_expert",
      "description": "代码专家 - 编程相关问题解答",
      "category": "code",
      "is_current": false
    }
  ],
  "current": "streamer_recommender"
}
```

---

### 4.2 获取系统提示词内容

获取指定系统提示词的详细内容和文件路径。

- **GET** `/system-prompts/{name}`

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 系统提示词名称 |

#### 请求示例

```bash
curl "http://localhost:8000/api/v1/system-prompts/streamer_recommender"
```

#### 响应示例

```json
{
  "name": "streamer_recommender",
  "content": "你是一位专业的主播推荐专家。\n\n请遵守以下准则：\n1. 根据用户偏好提供个性化推荐\n2. 关注主播的特色和优势\n3. 推荐理由要有说服力...",
  "file_path": "/workspace/config/system_prompts/streamer_recommender.md"
}
```

---

### 4.3 创建系统提示词

创建新的系统提示词，会自动创建对应的 `.md` 文件。

- **POST** `/system-prompts`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 提示词名称 |
| `content` | string | ✅ | 提示词内容 |
| `description` | string | ❌ | 描述 |
| `category` | string | ❌ | 分类（默认: `custom`）|

#### 请求示例

```json
{
  "name": "my_agent",
  "content": "你是一位我的专属助手。\n请友好地帮助我。",
  "description": "专属助手",
  "category": "custom"
}
```

#### 响应示例

```json
{
  "name": "my_agent",
  "description": "专属助手",
  "category": "custom",
  "is_current": false
}
```

---

### 4.4 切换系统提示词

切换到指定系统提示词。

- **POST** `/system-prompts/switch`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt_name` | string | ✅ | 系统提示词名称 |

#### 请求示例

```json
{
  "prompt_name": "general_assistant"
}
```

#### 响应示例

```json
{
  "name": "general_assistant",
  "description": "通用AI助手 - 日常对话和问题解答",
  "category": "general",
  "is_current": true
}
```

---

### 4.5 编辑系统提示词

编辑系统提示词的内容或元数据。

- **PUT** `/system-prompts/{name}`
- **Content-Type**: `application/json`

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 系统提示词名称 |

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | ❌ | 新的提示词内容 |
| `description` | string | ❌ | 新的描述 |
| `category` | string | ❌ | 新的分类 |

#### 请求示例

```json
{
  "content": "你是一位升级版的助手。\n请热情帮助我。",
  "description": "升级版专属助手"
}
```

---

### 4.6 删除系统提示词

删除自定义系统提示词（预设提示词不可删除）。

- **DELETE** `/system-prompts/{name}`

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 系统提示词名称 |

#### 响应示例

```json
{
  "message": "系统提示词 'my_agent' 已删除"
}
```

---

## 5. 知识库管理 API

### 5.1 获取知识库状态

获取知识库的状态信息。

- **GET** `/knowledge/status`

#### 响应示例

```json
{
  "document_count": 5,
  "collection_name": "agent_documents",
  "persist_directory": "/workspace/chroma_db",
  "embedding_model": "DoubaoEmbeddings"
}
```

---

### 5.2 搜索知识库

在知识库中搜索相关内容。

- **POST** `/knowledge/search`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 搜索查询文本 |
| `k` | int | ❌ | 返回结果数量（1-20，默认: 4）|

#### 请求示例

```json
{
  "query": "游戏主播推荐",
  "k": 5
}
```

#### 响应示例

```json
{
  "results": [
    {
      "content": "推荐游戏主播时需要考虑...",
      "metadata": {
        "source": "recommendation_guide.pdf"
      },
      "score": null
    }
  ],
  "total": 1
}
```

---

### 5.3 上传文档到知识库

上传文件到知识库（支持 PDF、TXT、Markdown 等格式）。

- **POST** `/knowledge/upload`
- **Content-Type**: `multipart/form-data`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 文件（支持: .pdf, .txt, .md, .yaml, .yml, .json, .csv）|

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/upload" \
  -F "file=@streamer_info.pdf"
```

#### 响应示例

```json
{
  "file_name": "streamer_info.pdf",
  "document_ids": ["doc-uuid-1", "doc-uuid-2"],
  "chunk_count": 5
}
```

---

## 6. 自定义提示词管理 API

### 6.1 获取自定义提示词列表

获取所有自定义提示词模板。

- **GET** `/custom-prompts`

#### 响应示例

```json
{
  "prompts": [
    {
      "name": "streamer_recommendation",
      "description": "生成主播推荐理由",
      "category": "recommendation",
      "input_variables": ["streamer_name", "streamer_tags", "streamer_content", "user_preferences"]
    },
    {
      "name": "content_summary",
      "description": "内容摘要生成",
      "category": "analysis",
      "input_variables": ["content"]
    }
  ]
}
```

---

### 6.2 获取自定义提示词详情

获取指定提示词模板的详情。

- **GET** `/custom-prompts/{name}`

---

### 6.3 创建自定义提示词

创建新的自定义提示词模板。

- **POST** `/custom-prompts`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 模板名称 |
| `template` | string | ✅ | 模板内容，支持 `{变量名}` 占位符 |
| `description` | string | ❌ | 描述 |
| `category` | string | ❌ | 分类（默认: `custom`）|
| `input_variables` | string[] | ❌ | 输入变量列表（不提供则自动从模板提取）|

#### 请求示例

```json
{
  "name": "streamer_comparison",
  "template": "请比较主播 {name1} 和 {name2}，分别说明他们的优点和适合人群。",
  "description": "主播对比分析",
  "category": "analysis"
}
```

#### 响应示例

```json
{
  "message": "自定义提示词 'streamer_comparison' 已创建",
  "name": "streamer_comparison"
}
```

---

### 6.4 编辑自定义提示词

编辑自定义提示词模板。

- **PUT** `/custom-prompts/{name}`
- **Content-Type**: `application/json`

请求参数同创建接口。

---

### 6.5 删除自定义提示词

删除自定义提示词模板。

- **DELETE** `/custom-prompts/{name}`

---

### 6.6 格式化提示词

使用变量值格式化指定的提示词模板。

- **POST** `/custom-prompts/format`
- **Content-Type**: `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt_name` | string | ✅ | 提示词名称 |
| `variables` | object | ✅ | 变量值键值对 |

#### 请求示例

```json
{
  "prompt_name": "streamer_comparison",
  "variables": {
    "name1": "主播A",
    "name2": "主播B"
  }
}
```

#### 响应示例

```json
{
  "prompt_name": "streamer_comparison",
  "formatted": "请比较主播 主播A 和 主播B，分别说明他们的优点和适合人群。",
  "variables": ["name1", "name2"]
}
```

---

## 7. 系统信息 API

### 7.1 获取 Agent 状态

获取 Agent 的当前状态信息。

- **GET** `/status`

#### 响应示例

```json
{
  "current_model": "deepseek",
  "available_models": [
    "openai",
    "anthropic",
    "dashscope",
    "qianfan",
    "deepseek"
  ],
  "current_system_prompt": "streamer_recommender",
  "conversation_length": 3,
  "knowledge_base_count": 5
}
```

---

### 7.2 获取对话历史

获取当前会话的对话历史。

- **GET** `/history`

#### 响应示例

```json
{
  "messages": [
    {
      "role": "user",
      "content": "推荐一位游戏主播"
    },
    {
      "role": "assistant",
      "content": "为你推荐..."
    }
  ],
  "total": 2
}
```

---

### 7.3 清空对话记忆

清空当前会话的对话记忆。

- **POST** `/memory/clear`

#### 响应示例

```json
{
  "message": "对话记忆已清空"
}
```

---

## 错误处理

所有 API 在发生错误时返回以下格式：

```json
{
  "error": "错误信息",
  "detail": "详细错误描述（可选）"
}
```

### HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复创建） |
| 500 | 服务器内部错误 |

---

## 快速使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 获取状态
r = requests.get(f"{BASE_URL}/status")
print(r.json())

# 2. 生成推荐理由
r = requests.post(f"{BASE_URL}/generate", json={
    "streamer_name": "岑先生",
    "tags": "游戏主播",
    "preferences": "技术型"
})
print(r.json()["recommendation"])

# 3. 聊天
r = requests.post(f"{BASE_URL}/chat", json={
    "message": "岑先生有什么特点？"
})
print(r.json()["reply"])
```

### cURL

```bash
# 生成推荐理由
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "streamer_name": "岑先生",
    "tags": "游戏主播、技术分享",
    "content": "专注于游戏攻略和技术教学",
    "preferences": "喜欢技术型主播"
  }' | jq .

# 获取系统提示词列表
curl "http://localhost:8000/api/v1/system-prompts" | jq .

# 切换系统提示词
curl -X POST "http://localhost:8000/api/v1/system-prompts/switch" \
  -H "Content-Type: application/json" \
  -d '{"prompt_name": "general_assistant"}' | jq .
```

### JavaScript (Fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// 生成推荐理由
async function generateRecommendation(name) {
  const response = await fetch(`${BASE_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      streamer_name: name,
      tags: '游戏主播',
      preferences: '技术型'
    })
  });
  return await response.json();
}

// 流式聊天
async function streamChat(message) {
  const response = await fetch(`${BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(decoder.decode(value));
  }
}
```