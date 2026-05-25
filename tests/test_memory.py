
import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.agent.memory import ChatMemoryConfig, ConversationTurn, ChatMemoryManager


class TestChatMemoryConfig:
    def test_default_config(self):
        config = ChatMemoryConfig()
        assert config.max_token_limit == 2000
        assert config.use_summary is True
        assert config.summary_model == "gpt-3.5-turbo"

    def test_custom_config(self):
        config = ChatMemoryConfig(
            max_token_limit=4000,
            use_summary=False,
            summary_model="gpt-4"
        )
        assert config.max_token_limit == 4000
        assert config.use_summary is False
        assert config.summary_model == "gpt-4"


class TestConversationTurn:
    def test_create_turn(self):
        turn = ConversationTurn(
            role="user",
            content="Hello"
        )
        assert turn.role == "user"
        assert turn.content == "Hello"
        assert turn.timestamp is not None


class TestChatMemoryManager:
    @pytest.fixture
    def temp_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationSummaryBufferMemory')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_init_with_summary(self, mock_buffer, mock_summary, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_summary.return_value = mock_memory

        manager = ChatMemoryManager(
            config=ChatMemoryConfig(use_summary=True)
        )

        assert manager is not None

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_init_without_summary(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(
            config=ChatMemoryConfig(use_summary=False)
        )

        assert manager is not None

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_add_user_message(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_user_message("Hello user")

        mock_memory.chat_memory.add_user_message.assert_called_once_with("Hello user")
        assert len(manager.conversation_history) == 1
        assert manager.conversation_history[0].role == "user"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_add_ai_message(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_ai_message("Hello AI")

        mock_memory.chat_memory.add_ai_message.assert_called_once_with("Hello AI")
        assert len(manager.conversation_history) == 1
        assert manager.conversation_history[0].role == "assistant"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_add_system_message(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_system_message("System prompt")

        assert len(manager.conversation_history) == 1
        assert manager.conversation_history[0].role == "system"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_add_message(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))

        msg = HumanMessage(content="Test human")
        manager.add_message(msg)

        mock_memory.chat_memory.add_message.assert_called_once_with(msg)

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_get_chat_history(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = [
            HumanMessage(content="Hi"),
            AIMessage(content="Hello")
        ]
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))

        history = manager.get_chat_history()
        assert len(history) == 2

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_get_conversation_history(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_user_message("Test 1")
        manager.add_ai_message("Response 1")

        history = manager.get_conversation_history()
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_clear(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_user_message("Test")
        manager.clear()

        mock_memory.clear.assert_called_once()
        assert len(manager.conversation_history) == 0

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_save_and_load_from_file(self, mock_buffer, mock_llm, temp_file):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager1 = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager1.add_user_message("Saved message")
        manager1.save_to_file(temp_file)

        manager2 = ChatMemoryManager.load_from_file(temp_file)
        assert len(manager2.conversation_history) == 1
        assert manager2.conversation_history[0].content == "Saved message"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationSummaryBufferMemory')
    def test_get_summary_enabled(self, mock_summary, mock_llm):
        mock_memory = Mock()
        mock_memory.moving_summary_buffer = "Test summary"
        mock_summary.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=True))

        summary = manager.get_summary()
        assert summary == "Test summary"

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_get_summary_disabled(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))

        summary = manager.get_summary()
        assert summary is None

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_prune_history(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        for i in range(10):
            manager.add_user_message(f"Message {i}")

        manager.prune_history(max_messages=5)
        assert len(manager.conversation_history) == 5

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_get_memory_stats(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        manager.add_user_message("Test")

        stats = manager.get_memory_stats()
        assert stats["num_messages"] == 1

    @patch('src.agent.memory.ChatOpenAI')
    @patch('src.agent.memory.ConversationBufferMemory')
    def test_get_memory_variables(self, mock_buffer, mock_llm):
        mock_memory = Mock()
        mock_memory.load_memory_variables.return_value = {"chat_history": []}
        mock_memory.chat_memory = Mock()
        mock_memory.chat_memory.messages = []
        mock_buffer.return_value = mock_memory

        manager = ChatMemoryManager(config=ChatMemoryConfig(use_summary=False))
        variables = manager.get_memory_variables()

        assert "chat_history" in variables

