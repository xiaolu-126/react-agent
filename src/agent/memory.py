from __future__ import annotations

import json
import os
from typing import Any, List, Optional, Dict
from datetime import datetime

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ConversationSummaryBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class ChatMemoryConfig(BaseModel):
    """对话记忆管理器的配置类。
    
    Attributes:
        max_token_limit: 对话历史的最大token限制
        use_summary: 是否使用摘要记忆模式
        summary_model: 用于生成摘要的LLM模型名称
        temperature: 摘要生成的温度参数
    """
    max_token_limit: int = Field(default=2000, description="对话历史的最大token限制")
    use_summary: bool = Field(default=True, description="是否使用摘要记忆")
    summary_model: str = Field(default="gpt-3.5-turbo", description="用于生成摘要的模型")
    temperature: float = Field(default=0.0, description="摘要生成的温度参数")


class ConversationTurn(BaseModel):
    """单个对话轮次的数据结构。
    
    Attributes:
        timestamp: 对话发生的时间戳
        role: 角色类型（user/assistant/system）
        content: 对话内容
    """
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    role: str
    content: str


class ChatMemoryManager:
    """对话记忆管理器，用于管理多轮对话的上下文。
    
    功能特性：
    - 支持 ConversationBufferMemory 和 ConversationSummaryBufferMemory 两种模式
    - 实现对话历史的存储和检索
    - 自动修剪机制避免 token 超限
    - 支持对话历史的文件持久化
    
    Examples:
        >>> from src.agent.memory import ChatMemoryManager, ChatMemoryConfig
        >>> config = ChatMemoryConfig(max_token_limit=3000)
        >>> memory = ChatMemoryManager(config=config)
        >>> memory.add_user_message("你好")
        >>> memory.add_ai_message("你好！有什么可以帮助你的？")
        >>> history = memory.get_conversation_history()
    """
    
    def __init__(self, config: Optional[ChatMemoryConfig] = None, llm: Optional[ChatOpenAI] = None):
        """初始化对话记忆管理器。
        
        Args:
            config: 记忆管理器的配置对象，如果为 None 则使用默认配置
            llm: 用于生成摘要的 ChatOpenAI 实例，如果为 None 则自动创建
        """
        self.config = config or ChatMemoryConfig()
        self.llm = llm or ChatOpenAI(model=self.config.summary_model, temperature=self.config.temperature)
        self._initialize_memory()
        self.conversation_history: List[ConversationTurn] = []

    def _initialize_memory(self) -> None:
        """根据配置初始化 LangChain 的 Memory 组件。"""
        if self.config.use_summary:
            self.memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=self.config.max_token_limit,
                return_messages=True,
                memory_key="chat_history"
            )
        else:
            self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    def add_user_message(self, content: str) -> None:
        """添加一条用户消息。
        
        Args:
            content: 用户输入的消息内容
        """
        self.memory.chat_memory.add_user_message(content)
        self.conversation_history.append(ConversationTurn(role="user", content=content))

    def add_ai_message(self, content: str) -> None:
        """添加一条 AI 回复消息。
        
        Args:
            content: AI 生成的回复内容
        """
        self.memory.chat_memory.add_ai_message(content)
        self.conversation_history.append(ConversationTurn(role="assistant", content=content))

    def add_system_message(self, content: str) -> None:
        """添加一条系统提示消息。
        
        Args:
            content: 系统提示内容
        """
        self.memory.chat_memory.add_message(SystemMessage(content=content))
        self.conversation_history.append(ConversationTurn(role="system", content=content))

    def add_message(self, message: BaseMessage) -> None:
        """添加一条 BaseMessage 类型的消息。
        
        Args:
            message: LangChain 的 BaseMessage 实例
        """
        self.memory.chat_memory.add_message(message)
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            role = "unknown"
        self.conversation_history.append(ConversationTurn(role=role, content=message.content))

    def get_memory_variables(self) -> Dict[str, Any]:
        """获取 LangChain Memory 格式的变量字典。
        
        Returns:
            包含 chat_history 的字典，可直接传递给 LLM Chain
        """
        return self.memory.load_memory_variables({})

    def get_chat_history(self) -> List[BaseMessage]:
        """获取 LangChain 格式的对话历史消息列表。
        
        Returns:
            BaseMessage 类型的消息列表
        """
        return self.memory.chat_memory.messages

    def get_conversation_history(self) -> List[ConversationTurn]:
        """获取结构化的对话历史。
        
        Returns:
            ConversationTurn 类型的对话列表副本
        """
        return self.conversation_history.copy()

    def clear(self) -> None:
        """清空所有对话历史和记忆。"""
        self.memory.clear()
        self.conversation_history.clear()

    def save_to_file(self, file_path: str) -> None:
        """将对话历史保存到 JSON 文件。
        
        Args:
            file_path: 保存文件的路径，支持相对路径或绝对路径
        """
        data = {
            "config": self.config.dict(),
            "conversation_history": [turn.dict() for turn in self.conversation_history],
            "chat_history_messages": [
                {
                    "type": type(msg).__name__,
                    "content": msg.content
                }
                for msg in self.memory.chat_memory.messages
            ],
            "saved_at": datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str, llm: Optional[ChatOpenAI] = None) -> "ChatMemoryManager":
        """从 JSON 文件加载对话历史。
        
        Args:
            file_path: 要加载的文件路径
            llm: 可选的 ChatOpenAI 实例
        
        Returns:
            恢复的 ChatMemoryManager 实例
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        config = ChatMemoryConfig(**data["config"])
        manager = cls(config=config, llm=llm)
        
        for turn_data in data["conversation_history"]:
            manager.conversation_history.append(ConversationTurn(**turn_data))
        
        for msg_data in data["chat_history_messages"]:
            if msg_data["type"] == "HumanMessage":
                manager.memory.chat_memory.add_user_message(msg_data["content"])
            elif msg_data["type"] == "AIMessage":
                manager.memory.chat_memory.add_ai_message(msg_data["content"])
            elif msg_data["type"] == "SystemMessage":
                manager.memory.chat_memory.add_message(SystemMessage(content=msg_data["content"]))
        
        return manager

    def get_summary(self) -> Optional[str]:
        """获取对话历史的摘要（如果启用了摘要模式）。
        
        Returns:
            对话摘要字符串，如未启用摘要模式则返回 None
        """
        if isinstance(self.memory, ConversationSummaryBufferMemory) or isinstance(self.memory, ConversationSummaryMemory):
            return self.memory.moving_summary_buffer
        return None

    def prune_history(self, max_messages: Optional[int] = None) -> None:
        """手动修剪对话历史，只保留最近的 N 条消息。
        
        Args:
            max_messages: 保留的最大消息数量
        """
        if max_messages and len(self.conversation_history) > max_messages:
            num_to_remove = len(self.conversation_history) - max_messages
            self.conversation_history = self.conversation_history[num_to_remove:]
            
            num_to_remove = len(self.memory.chat_memory.messages) - max_messages
            if num_to_remove > 0:
                self.memory.chat_memory.messages = self.memory.chat_memory.messages[num_to_remove:]

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆管理器的统计信息。
        
        Returns:
            包含消息数量、是否有摘要、配置信息的字典
        """
        return {
            "num_messages": len(self.conversation_history),
            "has_summary": self.get_summary() is not None,
            "config": self.config.dict()
        }
