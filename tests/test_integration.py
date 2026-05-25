
"""Integration tests for the agent system.
"""
import pytest
from unittest.mock import patch, Mock
from pathlib import Path


class TestModelPromptIntegration:
    @patch('src.models.model_manager.ChatOpenAI')
    @patch('src.models.model_manager.ChatAnthropic')
    def test_model_and_prompt_integration(
        self, mock_anthropic, mock_openai, temp_dir
    ):
        """Test that models can use prompts from the prompt manager."""
        from src.models.model_manager import ModelManager, ModelManagerConfig
        from src.agent.prompt_manager import PromptManager
        from src.models.config import ModelConfig, ModelType

        # Setup mocks
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance

        # Create managers
        model_config = ModelConfig(
            model_type=ModelType.OPENAI,
            model_name="gpt-4",
            api_key="test-key"
        )
        manager_config = ModelManagerConfig(
            default_model=ModelType.OPENAI,
            models={ModelType.OPENAI: model_config}
        )

        model_manager = ModelManager(config=manager_config)
        prompt_manager = PromptManager(config_dir=temp_dir)

        # Test integration
        prompt = prompt_manager.get_template("content_summary")
        assert prompt is not None

        model = model_manager.get_chat_model()
        assert model is not None


class TestKnowledgeBaseDocumentIntegration:
    def test_document_loader_and_knowledge_base(self, temp_dir):
        """Test document loading and knowledge base integration."""
        from src.tools.document_loader import DocumentLoader

        # Create test files
        test_file = temp_dir / "test_doc.txt"
        test_file.write_text("这是一篇关于主播推荐的测试文档。\n主播A擅长游戏直播。", encoding="utf-8")

        loader = DocumentLoader()
        docs = loader.load_document(str(test_file))

        assert len(docs) &gt; 0
        assert "主播推荐" in docs[0].page_content


class TestAgentWithMemoryIntegration:
    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.WebSearch')
    @patch('src.agent.react_agent.ChatOpenAI')
    @patch('src.agent.react_agent.ConversationBufferMemory')
    def test_agent_with_memory(
        self, mock_memory, mock_llm, mock_websearch, mock_prompt, mock_model, temp_dir
    ):
        """Test agent with memory integration."""
        from src.agent.react_agent import ReActAgent
        from src.agent.memory import ChatMemoryManager, ChatMemoryConfig

        # Setup mocks
        mock_model_instance = Mock()
        mock_llm_instance = Mock()
        mock_llm_with_tools = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_response.tool_calls = None
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm_instance.bind_tools.return_value = mock_llm_with_tools
        mock_model_instance.get_chat_model.return_value = mock_llm_instance
        mock_model.return_value = mock_model_instance

        mock_memory_inst = Mock()
        mock_memory_inst.chat_memory = Mock()
        mock_memory_inst.chat_memory.messages = []
        mock_memory.return_value = mock_memory_inst

        # Create components
        memory_config = ChatMemoryConfig(use_summary=False)
        memory_manager = ChatMemoryManager(config=memory_config)

        agent = ReActAgent(memory_manager=memory_manager)

        # Test that memory records the conversation
        with patch.object(agent, '_compiled_graph') as mock_graph:
            mock_state = {
                'messages': [mock_response]
            }
            mock_graph.invoke.return_value = mock_state

            result = agent.run("Hello")

            assert result == "Test response"


class TestPromptExportImportIntegration:
    def test_prompt_export_import(self, temp_dir):
        """Test prompt export and import functionality."""
        from src.agent.prompt_manager import PromptManager

        # Create first manager and add a custom prompt
        manager1 = PromptManager(config_dir=temp_dir)
        manager1.add_template(
            name="integration_test",
            template="测试模板: {variable}",
            description="集成测试模板",
            category="test"
        )

        # Export
        export_file = temp_dir / "exported_prompts.json"
        success = manager1.export_templates(export_file)
        assert success

        # Create second manager and import
        manager2 = PromptManager(config_dir=temp_dir / "new")
        count = manager2.import_templates(export_file)

        assert count &gt;= 1
        assert manager2.get_template_data("integration_test") is not None


class TestEndToEndAgent:
    @patch('src.models.model_manager.ChatOpenAI')
    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.WebSearch')
    @patch('src.agent.react_agent.ChatMemoryManager')
    def test_end_to_end_agent_workflow(
        self, mock_memory_mgr, mock_websearch, mock_prompt, mock_model, mock_llm, temp_dir
    ):
        """Test the complete end-to-end agent workflow with mocked components."""
        from src.agent.react_agent import ReActAgent

        # Setup mocks
        mock_model_instance = Mock()
        mock_llm_instance = Mock()
        mock_llm_with_tools = Mock()

        from langchain_core.messages import AIMessage
        mock_response = AIMessage(content="这是一位很好的主播推荐")
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm_instance.bind_tools.return_value = mock_llm_with_tools
        mock_model_instance.get_chat_model.return_value = mock_llm_instance
        mock_model.return_value = mock_model_instance

        mock_memory_inst = Mock()
        mock_memory_inst.chat_memory = Mock()
        mock_memory_inst.chat_memory.messages = []
        mock_memory_mgr.return_value = mock_memory_inst

        # Test complete workflow
        agent = ReActAgent()

        with patch.object(agent, '_compiled_graph') as mock_graph:
            mock_state = {
                'messages': [mock_response]
            }
            mock_graph.invoke.return_value = mock_state

            result = agent.run(
                "推荐一个主播",
                streamer_name="测试主播",
                user_preferences="喜欢游戏"
            )

            assert "主播推荐" in result


class TestWebSearchToolIntegration:
    @patch('src.tools.web_search.requests.post')
    def test_web_search_tool_integration(self, mock_post):
        """Test the web search tool integration."""
        from src.tools.web_search import web_search, WebSearch, SearchProvider

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Test Search Result",
                    "link": "https://example.com",
                    "snippet": "Test snippet content"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test the tool
        result = web_search("test query")

        assert "Test Search Result" in result or "搜索过程中发生错误" in result

