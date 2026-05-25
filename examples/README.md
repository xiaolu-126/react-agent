
# 示例目录

这里包含了项目的使用示例和演示脚本。

## 目录结构

```
examples/
├── README.md              # 本文件
├── demo_basic.py          # 基础功能演示
├── demo_agent.py        # Agent 使用演示
└── data/
    └── streamer_demo.txt  # 示例数据
```

## 快速开始

### 1. 基础功能演示

运行基础演示脚本，了解各个核心模块的功能：

```bash
python examples/demo_basic.py
```

这个脚本会演示：
- 提示词管理器
- 对话记忆
- 文档加载器
- 知识库使用

### 2. Agent 使用演示

运行 Agent 演示脚本：

```bash
python examples/demo_agent.py
```

这个脚本会演示：
- 基础 Agent 使用
- Agent + 知识库集成
- 对话记忆功能

注意：Agent 演示默认使用模拟模式，不会实际调用 API。要使用真实的 Agent，请先配置 API Key。

## 示例数据

`data/` 目录包含了一些示例数据文件，可以用于测试知识库功能。

### streamer_demo.txt

包含几位主播介绍资料：
- 游戏主播 - 小明
- 音乐主播 - 小红
- 美食主播 - 大胃王
- 户外主播 - 阿强

## 更多示例

详细的使用示例请查看：

- [docs/EXAMPLES.md](../docs/EXAMPLES.md) - 代码示例文档
- [docs/QUICKSTART.md](../docs/QUICKSTART.md) - 快速开始指南
- [docs/API.md](../docs/API.md) - API 参考文档

## 真实使用

配置好 API Key 后，可以使用：

```bash
# 交互式聊天
agent chat

# 生成推荐
agent generate "主播名" --preferences "用户偏好

# 上传文档
agent upload-docs examples/data/
```

详细使用方法请查看项目根目录的 [README.md](../README.md)。

