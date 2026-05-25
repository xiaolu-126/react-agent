import os
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

from .config import ModelType, ModelConfig, ModelManagerConfig


load_dotenv()


class ModelManager:
    """
    模型管理器，负责配置、初始化和切换不同的 LLM 模型
    
    支持的模型类型：
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - 通义千问 (DashScope)
    - 文心一言 (Qianfan)
    - DeepSeek
    """
    
    def __init__(self, config: Optional[ModelManagerConfig] = None):
        """
        初始化模型管理器
        
        Args:
            config: 可选的模型管理器配置，如果不提供则从环境变量加载
        """
        self._chat_models: Dict[ModelType, BaseChatModel] = {}
        self._current_model: Optional[ModelType] = None
        self._config = config or self._load_config_from_env()
        self._initialize_models()
    
    def _load_config_from_env(self) -> ModelManagerConfig:
        """
        从环境变量加载配置
        
        Returns:
            ModelManagerConfig: 模型管理器配置
        """
        config = ModelManagerConfig()
        
        default_model_str = os.getenv("DEFAULT_MODEL", "openai").lower()
        config.default_model = ModelType(default_model_str)
        
        openai_config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", 2048)),
        )
        config.models[ModelType.OPENAI] = openai_config
        
        anthropic_config = ModelConfig(
            model_type=ModelType.ANTHROPIC,
            model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", 2048)),
        )
        config.models[ModelType.ANTHROPIC] = anthropic_config
        
        dashscope_config = ModelConfig(
            model_type=ModelType.DASHSCOPE,
            model_name=os.getenv("DASHSCOPE_MODEL", "qwen-max"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", 2048)),
        )
        config.models[ModelType.DASHSCOPE] = dashscope_config
        
        qianfan_config = ModelConfig(
            model_type=ModelType.QIANFAN,
            model_name=os.getenv("QIANFAN_MODEL", "ernie-4.0"),
            api_key=os.getenv("QIANFAN_API_KEY"),
            api_base=os.getenv("QIANFAN_SECRET_KEY"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", 2048)),
        )
        config.models[ModelType.QIANFAN] = qianfan_config
        
        deepseek_config = ModelConfig(
            model_type=ModelType.DEEPSEEK,
            model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", 2048)),
        )
        config.models[ModelType.DEEPSEEK] = deepseek_config
        
        return config
    
    def _initialize_models(self):
        """初始化所有配置的模型"""
        self.set_current_model(self._config.default_model)
    
    def _create_openai_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建 OpenAI 模型
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: OpenAI 聊天模型实例
        """
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.model_name,
            api_key=config.api_key,
            base_url=config.api_base,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _create_anthropic_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建 Anthropic 模型
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: Anthropic 聊天模型实例
        """
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.model_name,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _create_dashscope_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建通义千问 (DashScope) 模型
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: 通义千问聊天模型实例
        """
        from langchain_community.chat_models import ChatTongyi
        return ChatTongyi(
            model=config.model_name,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _create_qianfan_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建文心一言 (Qianfan) 模型
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: 文心一言聊天模型实例
        """
        from langchain_community.chat_models import QianfanChatEndpoint
        return QianfanChatEndpoint(
            model=config.model_name,
            qianfan_ak=config.api_key,
            qianfan_sk=config.api_base,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _create_deepseek_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建 DeepSeek 模型
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: DeepSeek 聊天模型实例
        """
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.model_name,
            api_key=config.api_key,
            base_url=config.api_base,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def get_chat_model(self, model_type: Optional[ModelType] = None) -> BaseChatModel:
        """
        获取指定类型的聊天模型
        
        Args:
            model_type: 模型类型，如果不指定则使用当前模型
            
        Returns:
            BaseChatModel: 聊天模型实例
            
        Raises:
            ValueError: 如果模型类型未配置
        """
        target_type = model_type or self._current_model
        if target_type not in self._chat_models:
            if target_type not in self._config.models:
                raise ValueError(f"Model type {target_type} is not configured")
            config = self._config.models[target_type]
            
            if target_type == ModelType.OPENAI:
                model = self._create_openai_model(config)
            elif target_type == ModelType.ANTHROPIC:
                model = self._create_anthropic_model(config)
            elif target_type == ModelType.DASHSCOPE:
                model = self._create_dashscope_model(config)
            elif target_type == ModelType.QIANFAN:
                model = self._create_qianfan_model(config)
            elif target_type == ModelType.DEEPSEEK:
                model = self._create_deepseek_model(config)
            else:
                raise ValueError(f"Unsupported model type: {target_type}")
            
            self._chat_models[target_type] = model
        
        return self._chat_models[target_type]
    
    def set_current_model(self, model_type: ModelType):
        """
        设置当前使用的模型
        
        Args:
            model_type: 要切换到的模型类型
            
        Raises:
            ValueError: 如果模型类型未配置
        """
        if model_type not in self._config.models:
            raise ValueError(f"Model type {model_type} is not configured")
        
        self._current_model = model_type
        self.get_chat_model(model_type)
    
    def get_current_model(self) -> ModelType:
        """
        获取当前使用的模型类型
        
        Returns:
            ModelType: 当前模型类型
        """
        return self._current_model
    
    def get_available_models(self) -> list[ModelType]:
        """
        获取所有可用的模型类型列表
        
        Returns:
            list[ModelType]: 可用模型类型列表
        """
        return list(self._config.models.keys())
    
    def update_model_config(self, model_type: ModelType, config: ModelConfig):
        """
        更新指定模型的配置
        
        Args:
            model_type: 模型类型
            config: 新的模型配置
        """
        self._config.models[model_type] = config
        if model_type in self._chat_models:
            del self._chat_models[model_type]
