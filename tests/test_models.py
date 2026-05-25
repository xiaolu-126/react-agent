
import os
import pytest
from unittest.mock import Mock, patch
from src.models.model_manager import ModelManager
from src.models.config import ModelType, ModelConfig, ModelManagerConfig


class TestModelConfig:
    def test_model_config_creation(self):
        config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name="gpt-4",
            api_key="test-key"
        )
        assert config.model_type == ModelType.OPENAI
        assert config.model_name == "gpt-4"
        assert config.api_key == "test-key"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048

    def test_model_config_custom_values(self):
        config = ModelConfig(
            model_type=ModelType.ANTHROPIC,
            model_name="claude-3-opus",
            api_key="test-key",
            temperature=0.5,
            max_tokens=4096
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 4096


class TestModelManagerConfig:
    def test_default_config(self):
        config = ModelManagerConfig()
        assert config.default_model == ModelType.OPENAI
        assert isinstance(config.models, dict)

    def test_custom_config(self):
        openai_config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name="gpt-4",
            api_key="test-key"
        )
        config = ModelManagerConfig(
            default_model=ModelType.ANTHROPIC,
            models={ModelType.OPENAI: openai_config}
        )
        assert config.default_model == ModelType.ANTHROPIC
        assert ModelType.OPENAI in config.models


class TestModelManager:
    @pytest.fixture
    def mock_openai_config(self):
        return ModelConfig(
            model_type=ModelType.OPENAI,
            model_name="gpt-4",
            api_key="test-key"
        )

    @pytest.fixture
    def model_manager_config(self, mock_openai_config):
        return ModelManagerConfig(
            default_model=ModelType.OPENAI,
            models={ModelType.OPENAI: mock_openai_config}
        )

    @patch('src.models.model_manager.ChatOpenAI')
    def test_init_with_config(self, mock_chat_openai, model_manager_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        assert manager.get_current_model() == ModelType.OPENAI
        assert ModelType.OPENAI in manager.get_available_models()

    @patch('src.models.model_manager.ChatOpenAI')
    def test_get_chat_model(self, mock_chat_openai, model_manager_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        model = manager.get_chat_model()
        assert model is not None
        mock_chat_openai.assert_called_once()

    @patch('src.models.model_manager.ChatOpenAI')
    def test_set_current_model(self, mock_chat_openai, model_manager_config, mock_openai_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        anthropic_config = ModelConfig(
            model_type=ModelType.ANTHROPIC,
            model_name="claude-3",
            api_key="test-key"
        )
        model_manager_config.models[ModelType.ANTHROPIC] = anthropic_config

        manager = ModelManager(config=model_manager_config)

        with patch('src.models.model_manager.ChatAnthropic') as mock_chat_anthropic:
            mock_anthropic_instance = Mock()
            mock_chat_anthropic.return_value = mock_anthropic_instance

            manager.set_current_model(ModelType.ANTHROPIC)
            assert manager.get_current_model() == ModelType.ANTHROPIC

    @patch('src.models.model_manager.ChatOpenAI')
    def test_update_model_config(self, mock_chat_openai, model_manager_config, mock_openai_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        new_config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name="gpt-5",
            api_key="new-key"
        )
        manager.update_model_config(ModelType.OPENAI, new_config)

    @patch('src.models.model_manager.ChatOpenAI')
    def test_get_available_models(self, mock_chat_openai, model_manager_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        available = manager.get_available_models()
        assert isinstance(available, list)
        assert ModelType.OPENAI in available

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.models.model_manager.ChatOpenAI')
    def test_load_config_from_env(self, mock_chat_openai):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        with patch.dict(os.environ, {
            'DEFAULT_MODEL': 'anthropic',
            'OPENAI_MODEL': 'gpt-4',
            'OPENAI_API_KEY': 'env-key',
            'AGENT_TEMPERATURE': '0.8',
            'AGENT_MAX_TOKENS': '1024'
        }):
            manager = ModelManager()
            assert manager is not None

    @patch('src.models.model_manager.ChatAnthropic')
    @patch('src.models.model_manager.ChatOpenAI')
    def test_create_anthropic_model(self, mock_chat_openai, mock_chat_anthropic, model_manager_config):
        mock_openai = Mock()
        mock_chat_openai.return_value = mock_openai

        mock_anthropic = Mock()
        mock_chat_anthropic.return_value = mock_anthropic

        anthropic_config = ModelConfig(
            model_type=ModelType.ANTHROPIC,
            model_name="claude-3",
            api_key="test-key"
        )
        model_manager_config.models[ModelType.ANTHROPIC] = anthropic_config
        model_manager_config.default_model = ModelType.ANTHROPIC

        manager = ModelManager(config=model_manager_config)
        model = manager.get_chat_model(ModelType.ANTHROPIC)
        assert model == mock_anthropic

    @patch('src.models.model_manager.ChatTongyi')
    @patch('src.models.model_manager.ChatOpenAI')
    def test_create_dashscope_model(self, mock_chat_openai, mock_chat_tongyi, model_manager_config):
        mock_openai = Mock()
        mock_chat_openai.return_value = mock_openai

        mock_tongyi = Mock()
        mock_chat_tongyi.return_value = mock_tongyi

        dashscope_config = ModelConfig(
            model_type=ModelType.DASHSCOPE,
            model_name="qwen-max",
            api_key="test-key"
        )
        model_manager_config.models[ModelType.DASHSCOPE] = dashscope_config
        model_manager_config.default_model = ModelType.DASHSCOPE

        manager = ModelManager(config=model_manager_config)
        model = manager.get_chat_model(ModelType.DASHSCOPE)
        assert model == mock_tongyi

    @patch('src.models.model_manager.QianfanChatEndpoint')
    @patch('src.models.model_manager.ChatOpenAI')
    def test_create_qianfan_model(self, mock_chat_openai, mock_qianfan, model_manager_config):
        mock_openai = Mock()
        mock_chat_openai.return_value = mock_openai

        mock_qianfan_instance = Mock()
        mock_qianfan.return_value = mock_qianfan_instance

        qianfan_config = ModelConfig(
            model_type=ModelType.QIANFAN,
            model_name="ernie-4.0",
            api_key="test-key",
            api_base="test-secret"
        )
        model_manager_config.models[ModelType.QIANFAN] = qianfan_config
        model_manager_config.default_model = ModelType.QIANFAN

        manager = ModelManager(config=model_manager_config)
        model = manager.get_chat_model(ModelType.QIANFAN)
        assert model == mock_qianfan_instance

    @patch('src.models.model_manager.ChatOpenAI')
    def test_set_current_model_invalid(self, mock_chat_openai, model_manager_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        with pytest.raises(ValueError):
            manager.set_current_model(ModelType.ANTHROPIC)

    @patch('src.models.model_manager.ChatOpenAI')
    def test_get_chat_model_invalid(self, mock_chat_openai, model_manager_config):
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        manager = ModelManager(config=model_manager_config)

        with pytest.raises(ValueError):
            manager.get_chat_model(ModelType.ANTHROPIC)

