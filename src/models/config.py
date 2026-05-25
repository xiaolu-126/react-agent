from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ModelType(Enum):
    """支持的模型类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DASHSCOPE = "dashscope"
    QIANFAN = "qianfan"
    DEEPSEEK = "deepseek"


class ModelConfig(BaseModel):
    """单个模型的配置"""
    model_type: ModelType
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1)


class ModelManagerConfig(BaseModel):
    """模型管理器配置"""
    default_model: ModelType = ModelType.OPENAI
    models: Dict[ModelType, ModelConfig] = Field(default_factory=dict)
