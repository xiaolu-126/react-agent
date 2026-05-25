
import pytest
from unittest.mock import patch, Mock, MagicMock
from langchain_core.messages import AIMessage
from src.agent.react_agent import ReActAgent


class TestReActAgent:
    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_init(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        mock_prompt_instance = Mock()
        mock_prompt.return_value = mock_prompt_instance

        mock_memory_instance = Mock()
        mock_memory.return_value = mock_memory_instance

        mock_websearch_instance = Mock()
        mock_websearch.return_value = mock_websearch_instance

        agent = ReActAgent()

        assert agent is not None

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_init_with_custom_components(
        self, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        custom_model = Mock()
        custom_prompt = Mock()
        custom_memory = Mock()
        custom_kb = Mock()
        custom_websearch = Mock()

        agent = ReActAgent(
            model_manager=custom_model,
            prompt_manager=custom_prompt,
            memory_manager=custom_memory,
            knowledge_base=custom_kb,
            web_search=custom_websearch
        )

        assert agent.model_manager == custom_model
        assert agent.prompt_manager == custom_prompt
        assert agent.memory_manager == custom_memory
        assert agent.knowledge_base == custom_kb
        assert agent.web_search == custom_websearch

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_get_system_prompt(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        agent = ReActAgent()
        prompt = agent._get_system_prompt()

        assert isinstance(prompt, str)
        assert "主播推荐助手" in prompt

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_run(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Final answer")
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_model_instance.get_chat_model.return_value = mock_llm
        mock_model.return_value = mock_model_instance

        mock_memory_instance = Mock()
        mock_memory.return_value = mock_memory_instance

        agent = ReActAgent()

        with patch.object(agent, '_compiled_graph') as mock_graph:
            mock_state = {
                'messages': [AIMessage(content="Final answer")]
            }
            mock_graph.invoke.return_value = mock_state

            result = agent.run("Test query")

            assert result == "Final answer"
            mock_memory_instance.add_user_message.assert_called_once()
            mock_memory_instance.add_ai_message.assert_called_once()

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_run_with_streamer_name(
        self, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        mock_model_instance = Mock()
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Recommendation")
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_model_instance.get_chat_model.return_value = mock_llm
        mock_model.return_value = mock_model_instance

        mock_memory_instance = Mock()
        mock_memory.return_value = mock_memory_instance

        agent = ReActAgent()

        with patch.object(agent, '_compiled_graph') as mock_graph:
            mock_state = {
                'messages': [AIMessage(content="Recommendation")]
            }
            mock_graph.invoke.return_value = mock_state

            result = agent.run(
                "Test query",
                streamer_name="主播A",
                user_preferences="喜欢游戏"
            )

            assert result == "Recommendation"

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_stream(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        mock_memory_instance = Mock()
        mock_memory.return_value = mock_memory_instance

        agent = ReActAgent()

        with patch.object(agent, '_compiled_graph') as mock_graph:
            mock_chunk = {
                'agent': {
                    'messages': [AIMessage(content="Chunk 1")]
                }
            }
            mock_graph.stream.return_value = [mock_chunk]

            chunks = list(agent.stream("Test query"))

            assert len(chunks) &gt; 0
            mock_memory_instance.add_user_message.assert_called_once()

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_get_conversation_history(
        self, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        mock_memory_instance = Mock()
        mock_memory_instance.get_conversation_history.return_value = ["history"]
        mock_memory.return_value = mock_memory_instance

        agent = ReActAgent()

        history = agent.get_conversation_history()

        assert history == ["history"]
        mock_memory_instance.get_conversation_history.assert_called_once()

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_clear_memory(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        mock_memory_instance = Mock()
        mock_memory.return_value = mock_memory_instance

        agent = ReActAgent()
        agent.clear_memory()

        mock_memory_instance.clear.assert_called_once()

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_switch_model(self, mock_websearch, mock_memory, mock_prompt, mock_model):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        agent = ReActAgent()
        agent.switch_model("test_model")

        mock_model_instance.set_current_model.assert_called_once_with("test_model")

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    @patch('src.agent.react_agent.KnowledgeBase')
    def test_setup_tools_with_kb(
        self, mock_kb, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        mock_kb_instance = Mock()
        mock_kb_instance.similarity_search.return_value = []

        agent = ReActAgent(knowledge_base=mock_kb_instance)

        tools = agent._setup_tools()

        assert len(tools) == 2

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    @patch('src.agent.react_agent.KnowledgeBase')
    def test_knowledge_base_search_tool(
        self, mock_kb, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        from langchain_core.documents import Document
        mock_kb_instance = Mock()
        mock_kb_instance.similarity_search.return_value = [
            Document(page_content="Test knowledge", metadata={"source": "test"})
        ]

        agent = ReActAgent(knowledge_base=mock_kb_instance)

        tools = agent._setup_tools()
        kb_tool = next(t for t in tools if t.name == "knowledge_base_search")

        result = kb_tool.func("test query", k=2)

        assert "知识库搜索结果" in result
        mock_kb_instance.similarity_search.assert_called_once()

    @patch('src.agent.react_agent.ModelManager')
    @patch('src.agent.react_agent.PromptManager')
    @patch('src.agent.react_agent.ChatMemoryManager')
    @patch('src.agent.react_agent.WebSearch')
    def test_knowledge_base_search_no_kb(
        self, mock_websearch, mock_memory, mock_prompt, mock_model
    ):
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance

        agent = ReActAgent(knowledge_base=None)

        tools = agent._setup_tools()
        kb_tool = next(t for t in tools if t.name == "knowledge_base_search")

        result = kb_tool.func("test query")

        assert "知识库未初始化" in result

