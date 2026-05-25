import os
import requests
from typing import List
from langchain_core.embeddings import Embeddings


class DoubaoEmbeddings(Embeddings):
    """
    豆包 Embedding 模型实现
    
    通过火山引擎 Ark API 调用豆包多模态嵌入服务
    支持文本、图像等多种输入类型
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_base: str = "https://ark.cn-beijing.volces.com/api/v3",
        model_name: str = "doubao-embedding-vision",
    ):
        """
        初始化豆包 Embedding
        
        Args:
            api_key: API 密钥
            api_base: API 基础 URL
            model_name: 模型名称
        """
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY") or os.getenv("EMBEDDING_API_KEY")
        self.api_base = api_base or os.getenv("DOUBAO_API_BASE") or os.getenv("EMBEDDING_API_BASE")
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL_NAME", "doubao-embedding-vision")
        
        if not self.api_key:
            raise ValueError("请配置 DOUBAO_API_KEY 或 EMBEDDING_API_KEY")
    
    def _embed(self, texts: List[str]) -> List[List[float]]:
        """
        调用豆包多模态嵌入 API 生成嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        url = f"{self.api_base}/embeddings/multimodal"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        embeddings = []
        
        for text in texts:
            input_data = [{"text": text, "type": "text"}]
            data = {
                "model": self.model_name,
                "input": input_data,
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if "data" not in result or "embedding" not in result["data"]:
                raise ValueError(f"API 响应错误: {result}")
            
            embeddings.append(result["data"]["embedding"])
        
        return embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        为多个文档生成嵌入向量
        
        Args:
            texts: 文档列表
            
        Returns:
            嵌入向量列表
        """
        return self._embed(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        为单个查询生成嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        return self._embed([text])[0]
