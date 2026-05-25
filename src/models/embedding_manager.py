import os
from enum import Enum
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

project_root = Path(__file__).parent.parent.parent
env_path = project_root / "config" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


class EmbeddingModelType(Enum):
    """支持的 Embedding 模型类型枚举"""
    OPENAI = "openai"
    DASHSCOPE = "dashscope"
    QIANFAN = "qianfan"
    DOUBAO = "doubao"
    LOCAL = "local"


class EmbeddingManager:
    """
    Embedding 模型管理器，负责配置、初始化和切换不同的 Embedding 模型
    
    支持的模型类型：
    - OpenAI Embeddings
    - 通义千问 Embeddings (DashScope)
    - 文心一言 Embeddings (Qianfan)
    - 豆包 Embeddings (Doubao)
    - 本地模型 (Sentence Transformers)
    """
    
    def __init__(self):
        """初始化 Embedding 模型管理器"""
        self._current_model: Optional[Embeddings] = None
        self._current_type: Optional[EmbeddingModelType] = None
        self._config = self._load_config_from_env()
        try:
            self._initialize_model()
        except Exception:
            pass
    
    def _load_config_from_env(self):
        """从环境变量加载配置"""
        return {
            "default_model": os.getenv("EMBEDDING_MODEL", "openai").lower(),
            "api_key": os.getenv("EMBEDDING_API_KEY"),
            "api_base": os.getenv("EMBEDDING_API_BASE"),
        }
    
    def _initialize_model(self):
        """初始化默认的 Embedding 模型"""
        model_type = EmbeddingModelType(self._config["default_model"])
        self.set_current_model(model_type)
    
    def _create_openai_embedding(self) -> Embeddings:
        """创建 OpenAI Embedding 模型"""
        from langchain_openai import OpenAIEmbeddings
        api_key = self._config["api_key"] or os.getenv("OPENAI_API_KEY")
        api_base = self._config["api_base"] or os.getenv("OPENAI_API_BASE")
        
        return OpenAIEmbeddings(
            api_key=api_key,
            base_url=api_base,
        )
    
    def _create_dashscope_embedding(self) -> Embeddings:
        """创建通义千问 Embedding 模型"""
        from langchain_community.embeddings import DashScopeEmbeddings
        api_key = self._config["api_key"] or os.getenv("DASHSCOPE_API_KEY")
        
        return DashScopeEmbeddings(
            dashscope_api_key=api_key,
        )
    
    def _create_qianfan_embedding(self) -> Embeddings:
        """创建文心一言 Embedding 模型"""
        from langchain_community.embeddings import QianfanEmbeddingsEndpoint
        api_key = self._config["api_key"] or os.getenv("QIANFAN_API_KEY")
        secret_key = os.getenv("QIANFAN_SECRET_KEY")
        
        return QianfanEmbeddingsEndpoint(
            qianfan_ak=api_key,
            qianfan_sk=secret_key,
        )
    
    def _create_doubao_embedding(self) -> Embeddings:
        """创建豆包 (Doubao) Embedding 模型"""
        from .doubao_embeddings import DoubaoEmbeddings
        api_key = self._config["api_key"] or os.getenv("DOUBAO_API_KEY")
        api_base = self._config["api_base"] or os.getenv("DOUBAO_API_BASE")
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "doubao-embedding-vision")
        
        return DoubaoEmbeddings(
            api_key=api_key,
            api_base=api_base,
            model_name=model_name,
        )
    
    def _create_local_embedding(self) -> Embeddings:
        """创建本地 Embedding 模型 (Sentence Transformers)"""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except ImportError:
            raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")
    
    def get_embedding_model(self) -> Embeddings:
        """
        获取当前的 Embedding 模型
        
        Returns:
            Embeddings: 当前 Embedding 模型实例
        """
        if self._current_model is None:
            raise ValueError("Embedding 模型未初始化")
        return self._current_model
    
    def set_current_model(self, model_type: EmbeddingModelType):
        """
        设置当前使用的 Embedding 模型
        
        Args:
            model_type: 要切换到的模型类型
        """
        if model_type == EmbeddingModelType.OPENAI:
            self._current_model = self._create_openai_embedding()
        elif model_type == EmbeddingModelType.DASHSCOPE:
            self._current_model = self._create_dashscope_embedding()
        elif model_type == EmbeddingModelType.QIANFAN:
            self._current_model = self._create_qianfan_embedding()
        elif model_type == EmbeddingModelType.DOUBAO:
            self._current_model = self._create_doubao_embedding()
        elif model_type == EmbeddingModelType.LOCAL:
            self._current_model = self._create_local_embedding()
        else:
            raise ValueError(f"不支持的 Embedding 模型类型: {model_type}")
        
        self._current_type = model_type
    
    def get_current_model_type(self) -> EmbeddingModelType:
        """
        获取当前使用的 Embedding 模型类型
        
        Returns:
            EmbeddingModelType: 当前模型类型
        """
        return self._current_type
    
    def get_available_models(self) -> list[EmbeddingModelType]:
        """
        获取所有可用的 Embedding 模型类型列表
        
        Returns:
            list[EmbeddingModelType]: 可用模型类型列表
        """
        return list(EmbeddingModelType)
