
import os
import pytest
from unittest.mock import patch, Mock
from src.tools.web_search import (
    SearchProvider,
    SearchResult,
    SerperSearchProvider,
    TavilySearchProvider,
    WebSearch,
    web_search
)


class TestSearchResult:
    def test_create_search_result(self):
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="test"
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"


class TestSerperSearchProvider:
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_init(self):
        provider = SerperSearchProvider()
        assert provider.api_key == "test_key"

    def test_init_with_api_key(self):
        provider = SerperSearchProvider(api_key="custom_key")
        assert provider.api_key == "custom_key"

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                SerperSearchProvider()

    @patch('requests.post')
    def test_search(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Result 1",
                    "link": "https://example1.com",
                    "snippet": "Snippet 1",
                    "site": "example1"
                },
                {
                    "title": "Result 2",
                    "link": "https://example2.com",
                    "snippet": "Snippet 2",
                    "site": "example2"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = SerperSearchProvider(api_key="test_key")
        results = provider.search("test query", num_results=2)

        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].url == "https://example1.com"
        mock_post.assert_called_once()


class TestTavilySearchProvider:
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    def test_init(self):
        provider = TavilySearchProvider()
        assert provider.api_key == "test_key"

    def test_init_with_api_key(self):
        provider = TavilySearchProvider(api_key="custom_key")
        assert provider.api_key == "custom_key"

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                TavilySearchProvider()

    @patch('requests.post')
    def test_search(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Tavily Result 1",
                    "url": "https://tavily1.com",
                    "content": "Content 1"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = TavilySearchProvider(api_key="test_key")
        results = provider.search("test query", num_results=1)

        assert len(results) == 1
        assert results[0].title == "Tavily Result 1"
        assert results[0].source == "tavily"


class TestWebSearch:
    @patch.object(SerperSearchProvider, 'search')
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_init_serper(self, mock_search):
        mock_search.return_value = []
        ws = WebSearch(provider=SearchProvider.SERPER)
        assert ws.provider == SearchProvider.SERPER

    @patch.object(TavilySearchProvider, 'search')
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    def test_init_tavily(self, mock_search):
        mock_search.return_value = []
        ws = WebSearch(provider=SearchProvider.TAVILY)
        assert ws.provider == SearchProvider.TAVILY

    def test_init_unsupported_provider(self):
        with pytest.raises(ValueError):
            WebSearch(provider="unsupported")

    @patch.object(SerperSearchProvider, 'search')
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_search(self, mock_search):
        mock_search.return_value = [
            SearchResult(title="Test", url="https://test.com", snippet="test")
        ]
        ws = WebSearch(provider=SearchProvider.SERPER)
        results = ws.search("test query")

        assert len(results) &gt; 0
        mock_search.assert_called_once_with("test query", 5)

    @patch.object(SerperSearchProvider, 'search')
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_search_with_num_results(self, mock_search):
        mock_search.return_value = []
        ws = WebSearch(provider=SearchProvider.SERPER, default_num_results=3)
        ws.search("test query", num_results=10)

        mock_search.assert_called_once_with("test query", 10)

    @patch.object(SerperSearchProvider, 'search')
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_search_max_results_limit(self, mock_search):
        mock_search.return_value = []
        ws = WebSearch(provider=SearchProvider.SERPER, max_num_results=5)
        ws.search("test query", num_results=20)

        mock_search.assert_called_once_with("test query", 5)

    def test_format_results(self):
        ws = WebSearch.__new__(WebSearch)
        ws.default_num_results = 5
        ws.max_num_results = 10

        results = [
            SearchResult(title="Title 1", url="https://1.com", snippet="Snippet 1"),
            SearchResult(title="Title 2", url="https://2.com", snippet="Snippet 2")
        ]

        formatted = ws.format_results(results)

        assert "Title 1" in formatted
        assert "https://1.com" in formatted
        assert "Snippet 1" in formatted

    def test_format_empty_results(self):
        ws = WebSearch.__new__(WebSearch)
        ws.default_num_results = 5
        ws.max_num_results = 10

        formatted = ws.format_results([])
        assert "未找到" in formatted


class TestWebSearchTool:
    @patch('src.tools.web_search.web_search_instance')
    def test_web_search_tool(self, mock_instance):
        mock_instance.search.return_value = [
            SearchResult(title="Test", url="https://test.com", snippet="test snippet")
        ]
        mock_instance.format_results.return_value = "Formatted results"

        result = web_search("test query", num_results=3)

        assert result == "Formatted results"
        mock_instance.search.assert_called_once_with("test query", 3)

    @patch('src.tools.web_search.web_search_instance')
    def test_web_search_tool_error(self, mock_instance):
        mock_instance.search.side_effect = Exception("Test error")

        result = web_search("test query")

        assert "搜索过程中发生错误" in result

