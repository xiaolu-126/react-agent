import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """项目配置管理类

    负责加载和管理项目的所有配置项，支持从环境变量和 .env 文件读取配置。
    """

    def __init__(self, env_file: Optional[str] = None):
        """初始化配置管理器

        Args:
            env_file: 可选的 .env 文件路径，如果不指定则自动查找
        """
        self._env_file = env_file or self._find_env_file()
        if self._env_file and Path(self._env_file).exists():
            load_dotenv(self._env_file)

        # 基础路径配置
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"

        # 确保必要的目录存在
        self._ensure_directories()

    def _find_env_file(self) -> Optional[str]:
        """自动查找 .env 文件

        Returns:
            .env 文件路径，如果没有找到则返回 None
        """
        possible_paths = [
            Path.cwd() / "config" / ".env",
            Path.cwd() / ".env",
            Path(__file__).parent.parent.parent / "config" / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return None

    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def default_model(self) -> str:
        """默认模型类型"""
        return os.getenv("DEFAULT_MODEL", "openai").lower()

    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API 密钥"""
        return os.getenv("OPENAI_API_KEY")

    @property
    def openai_api_base(self) -> str:
        """OpenAI API 基础 URL"""
        return os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    @property
    def openai_model(self) -> str:
        """OpenAI 模型名称"""
        return os.getenv("OPENAI_MODEL", "gpt-4o")

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Anthropic API 密钥"""
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def anthropic_model(self) -> str:
        """Anthropic 模型名称"""
        return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    @property
    def dashscope_api_key(self) -> Optional[str]:
        """通义千问 API 密钥"""
        return os.getenv("DASHSCOPE_API_KEY")

    @property
    def dashscope_model(self) -> str:
        """通义千问模型名称"""
        return os.getenv("DASHSCOPE_MODEL", "qwen-max")

    @property
    def qianfan_api_key(self) -> Optional[str]:
        """文心一言 API 密钥"""
        return os.getenv("QIANFAN_API_KEY")

    @property
    def qianfan_secret_key(self) -> Optional[str]:
        """文心一言 Secret Key"""
        return os.getenv("QIANFAN_SECRET_KEY")

    @property
    def qianfan_model(self) -> str:
        """文心一言模型名称"""
        return os.getenv("QIANFAN_MODEL", "ernie-4.0")

    @property
    def deepseek_api_key(self) -> Optional[str]:
        """DeepSeek API 密钥"""
        return os.getenv("DEEPSEEK_API_KEY")

    @property
    def deepseek_api_base(self) -> str:
        """DeepSeek API 基础 URL"""
        return os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

    @property
    def deepseek_model(self) -> str:
        """DeepSeek 模型名称"""
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @property
    def embedding_model(self) -> str:
        """Embedding 模型类型"""
        return os.getenv("EMBEDDING_MODEL", "openai")

    @property
    def embedding_api_key(self) -> Optional[str]:
        """Embedding 专用 API 密钥"""
        return os.getenv("EMBEDDING_API_KEY")

    @property
    def embedding_api_base(self) -> Optional[str]:
        """Embedding API 基础 URL"""
        return os.getenv("EMBEDDING_API_BASE")

    @property
    def chroma_db_path(self) -> str:
        """ChromaDB 持久化路径"""
        path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        if not os.path.isabs(path):
            path = str(self.project_root / path)
        return path

    @property
    def chroma_collection_name(self) -> str:
        """ChromaDB 集合名称"""
        return os.getenv("CHROMA_COLLECTION_NAME", "agent_documents")

    @property
    def agent_name(self) -> str:
        """Agent 名称"""
        return os.getenv("AGENT_NAME", "SmartAgent")

    @property
    def agent_temperature(self) -> float:
        """Agent 温度参数"""
        return float(os.getenv("AGENT_TEMPERATURE", "0.7"))

    @property
    def agent_max_tokens(self) -> int:
        """Agent 最大 Token 数"""
        return int(os.getenv("AGENT_MAX_TOKENS", "2048"))

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def log_file(self) -> str:
        path = os.getenv("LOG_FILE", "./logs/agent.log")
        if not os.path.isabs(path):
            path = str(self.project_root / path)
        return path

    @property
    def prompts_dir(self) -> Path:
        """提示词模板目录"""
        return self.config_dir / "prompts"

    def check_required_configs(self) -> list[str]:
        """检查必要的配置项是否存在

        Returns:
            缺失的配置项列表
        """
        missing = []
        # 根据默认模型检查相应的 API 密钥
        model = self.default_model
        if model == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        elif model == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        elif model == "dashscope" and not self.dashscope_api_key:
            missing.append("DASHSCOPE_API_KEY")
        elif model == "qianfan" and (not self.qianfan_api_key or not self.qianfan_secret_key):
            if not self.qianfan_api_key:
                missing.append("QIANFAN_API_KEY")
            if not self.qianfan_secret_key:
                missing.append("QIANFAN_SECRET_KEY")
        return missing


# 全局配置实例
_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None) -> Config:
    """获取全局配置实例

    Args:
        env_file: 可选的 .env 文件路径

    Returns:
        配置实例
    """
    global _config
    if _config is None:
        _config = Config(env_file)
    return _config
