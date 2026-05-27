import os
import json
from typing import Dict, Optional, Any, List
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import LanguageModelInput

from .config import ModelType, ModelConfig, ModelManagerConfig

from langchain_deepseek import ChatDeepSeek
from src.utils.logger import get_logger

_logger = get_logger("agent")

# ─── DeepSeek reasoning_content 修复 ─────────────────────────────────────────
# langchain_openai 的 _convert_message_to_dict 不会将 additional_kwargs 中的
# reasoning_content 写入 API 请求字典。这里在模块加载时做 monkey-patch，
# 全局确保所有 assistant 消息的 reasoning_content 不被丢失。
import langchain_openai.chat_models.base as _lc_base
from langchain_core.messages import AIMessage as _AIMessage

_orig_convert_to_dict = _lc_base._convert_message_to_dict
if not hasattr(_orig_convert_to_dict, '_ds_patched'):

    def _patched_convert_message_to_dict(message, api="chat/completions"):
        msg_dict = _orig_convert_to_dict(message, api)
        if isinstance(message, _AIMessage) and "reasoning_content" in message.additional_kwargs:
            if msg_dict.get("role") == "assistant":
                msg_dict["reasoning_content"] = message.additional_kwargs["reasoning_content"]
        return msg_dict
    _patched_convert_message_to_dict._ds_patched = True
    _lc_base._convert_message_to_dict = _patched_convert_message_to_dict
    _logger.info("monkey-patch _convert_message_to_dict applied")

_orig_convert_to_msg = _lc_base._convert_dict_to_message
if not hasattr(_orig_convert_to_msg, '_ds_patched'):

    def _patched_convert_dict_to_message(dct):
        msg = _orig_convert_to_msg(dct)
        if dct.get("role") == "assistant":
            reasoning = dct.get("reasoning_content") or dct.get("reasoning")
            if reasoning is not None and isinstance(msg, _AIMessage):
                msg.additional_kwargs["reasoning_content"] = str(reasoning)
        return msg
    _patched_convert_dict_to_message._ds_patched = True
    _lc_base._convert_dict_to_message = _patched_convert_dict_to_message
    _logger.info("monkey-patch _convert_dict_to_message applied")
# ─────────────────────────────────────────────────────────────────────────────


class _FixedChatDeepSeek(ChatDeepSeek):

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        input_messages = self._convert_input(input_).to_messages()
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)

        rc_count = 0
        for im, pm in zip(input_messages, payload.get("messages", [])):
            if isinstance(im, AIMessage) and "reasoning_content" in im.additional_kwargs:
                if pm.get("role") == "assistant":
                    pm["reasoning_content"] = im.additional_kwargs["reasoning_content"]
                    rc_count += 1

        _logger.debug(
            "_get_request_payload | msgs=%d | rc_injected=%d",
            len(payload.get("messages", [])), rc_count,
        )

        return payload


project_root = Path(__file__).parent.parent.parent
env_path = project_root / "config" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
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
    - 自定义模型（OpenAI 兼容接口）
    """
    
    def __init__(self, config: Optional[ModelManagerConfig] = None):
        """
        初始化模型管理器
        
        Args:
            config: 可选的模型管理器配置，如果不提供则从环境变量加载
        """
        self._chat_models: Dict[ModelType, BaseChatModel] = {}
        self._custom_models: Dict[str, ModelConfig] = {}
        self._custom_chat_models: Dict[str, BaseChatModel] = {}
        self._current_model: Optional[ModelType] = None
        self._current_custom_model: Optional[str] = None
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
        try:
            self.set_current_model(self._config.default_model)
        except Exception:
            pass
    
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
        return _FixedChatDeepSeek(
            model=config.model_name,
            api_key=config.api_key,
            api_base=config.api_base or "https://api.deepseek.com/v1",
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
        if target_type is None:
            raise ValueError("No model is currently set")
        
        if isinstance(target_type, str):
            if target_type not in self._custom_chat_models:
                if target_type not in self._custom_models:
                    raise ValueError(f"Custom model '{target_type}' is not configured")
                config = self._custom_models[target_type]
                model = self._create_openai_model(config)
                self._custom_chat_models[target_type] = model
            return self._custom_chat_models[target_type]
        
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
    
    def set_current_model(self, model_type: object):
        """
        设置当前使用的模型
        
        Args:
            model_type: 要切换到的模型类型（ModelType 枚举或自定义模型字符串）
            
        Raises:
            ValueError: 如果模型类型未配置
        """
        if isinstance(model_type, str):
            try:
                mt = ModelType(model_type.lower())
                if mt in self._config.models:
                    self._current_model = mt
                    self._current_custom_model = None
                    self.get_chat_model(mt)
                    return
            except ValueError:
                pass

            if model_type not in self._custom_models:
                raise ValueError(f"自定义模型 '{model_type}' 未配置")
            self._current_custom_model = model_type
            self._current_model = None
            self.get_chat_model(model_type)
        else:
            if model_type not in self._config.models:
                raise ValueError(f"模型类型 {model_type} 未配置")
            self._current_model = model_type
            self._current_custom_model = None
            self.get_chat_model(model_type)
    
    def get_current_model(self) -> object:
        """
        获取当前使用的模型类型
        
        Returns:
            当前模型类型（ModelType 或自定义模型字符串）
        """
        if self._current_custom_model:
            return self._current_custom_model
        return self._current_model
    
    def get_available_models(self) -> list:
        """
        获取所有可用的模型类型列表
        
        Returns:
            可用模型类型列表（包含内置 ModelType 和自定义模型字符串）
        """
        models = list(self._config.models.keys())
        models.extend(list(self._custom_models.keys()))
        return models
    
    def get_model_display_name(self, model_key: object) -> str:
        """
        获取模型的显示名称
        
        Args:
            model_key: 模型类型（ModelType 或字符串）
            
        Returns:
            str: 显示名称
        """
        model_names = {
            ModelType.OPENAI: "GPT-4 / GPT-3.5",
            ModelType.ANTHROPIC: "Claude 3",
            ModelType.DASHSCOPE: "通义千问",
            ModelType.QIANFAN: "文心一言",
            ModelType.DEEPSEEK: "DeepSeek",
        }
        
        if isinstance(model_key, str):
            config = self._custom_models.get(model_key)
            if config:
                return config.model_name
            return model_key
        
        return model_names.get(model_key, model_key.value)
    
    def add_custom_model(
        self,
        model_type: str,
        model_name: str,
        api_key: str,
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        添加自定义模型（OpenAI 兼容接口）
        
        Args:
            model_type: 模型类型标识（如 my-model）
            model_name: 模型名称（如 gpt-4o-mini）
            api_key: API 密钥
            api_base: API 基础 URL
            temperature: 温度参数
            max_tokens: 最大 Token 数
            
        Returns:
            str: 新添加的模型类型标识
            
        Raises:
            ValueError: 如果模型标识已存在
        """
        if model_type in self._custom_models:
            raise ValueError(f"自定义模型 '{model_type}' 已存在")
        
        try:
            mt = ModelType(model_type)
            if mt in self._config.models:
                raise ValueError(f"模型标识 '{model_type}' 与内置模型冲突")
        except ValueError:
            pass
        
        config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name=model_name,
            api_key=api_key,
            api_base=api_base,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._custom_models[model_type] = config
        return model_type
    
    def remove_model(self, model_type: str) -> bool:
        """
        删除指定模型
        
        Args:
            model_type: 模型类型标识
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 如果模型不存在或是当前正在使用的模型或是内置模型
        """
        if model_type in self._custom_models:
            if model_type == self._current_custom_model:
                raise ValueError("不能删除当前正在使用的模型")
            del self._custom_models[model_type]
            if model_type in self._custom_chat_models:
                del self._custom_chat_models[model_type]
            return True
        
        try:
            mt = ModelType(model_type.lower())
        except ValueError:
            raise ValueError(f"模型 '{model_type}' 不存在")
        
        raise ValueError(f"内置模型 '{model_type}' 不可删除")
    
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