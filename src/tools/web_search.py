import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field


load_dotenv()


class SearchProvider(Enum):
    SERPER = "serper"
    TAVILY = "tavily"
    GOOGLE = "google"


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: Optional[str] = None


class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        pass


class SerperSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY must be set in environment variables")
        self.base_url = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query,
            "num": num_results,
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("site", "serper")
            ))
        
        return results


class TavilySearchProvider(BaseSearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY must be set in environment variables")
        self.base_url = "https://api.tavily.com/search"

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": num_results,
        }
        
        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", [])[:num_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                source="tavily"
            ))
        
        return results


class WebSearch:
    def __init__(
        self,
        provider: SearchProvider = SearchProvider.SERPER,
        api_key: Optional[str] = None,
        default_num_results: int = 5,
        max_num_results: int = 10
    ):
        self.provider = provider
        self.default_num_results = min(default_num_results, max_num_results)
        self.max_num_results = max_num_results
        
        if provider == SearchProvider.SERPER:
            self.search_provider = SerperSearchProvider(api_key)
        elif provider == SearchProvider.TAVILY:
            self.search_provider = TavilySearchProvider(api_key)
        else:
            raise ValueError(f"Unsupported search provider: {provider}")

    def search(
        self,
        query: str,
        num_results: Optional[int] = None
    ) -> List[SearchResult]:
        if num_results is None:
            num_results = self.default_num_results
        num_results = min(num_results, self.max_num_results)
        
        return self.search_provider.search(query, num_results)

    def format_results(self, results: List[SearchResult]) -> str:
        if not results:
            return "未找到相关搜索结果。"
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result.title}\n"
                f"   链接: {result.url}\n"
                f"   摘要: {result.snippet}\n"
            )
        
        return "\n".join(formatted)


web_search_instance = WebSearch()


@tool
def web_search(
    query: str = Field(..., description="要搜索的查询内容"),
    num_results: int = Field(5, description="返回的搜索结果数量，最多10个")
) -> str:
    """
    网络搜索工具，用于搜索网络获取最新信息。
    
    使用默认的搜索服务提供商进行网络搜索，返回相关的搜索结果。
    可以限制搜索结果数量以避免token超限。
    
    Args:
        query: 要搜索的查询字符串
        num_results: 返回的结果数量，默认5个，最多10个
    
    Returns:
        格式化的搜索结果字符串
    """
    try:
        results = web_search_instance.search(query, num_results)
        return web_search_instance.format_results(results)
    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}"
