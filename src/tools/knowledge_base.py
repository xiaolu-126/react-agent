import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .document_loader import DocumentLoader


class KnowledgeBase:
    """知识库核心类，集成向量存储、文档管理和检索功能"""

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_directory: Optional[str] = None,
        embedding_model: Optional[Embeddings] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        初始化知识库
        
        Args:
            collection_name: 向量数据库集合名称
            persist_directory: 持久化目录，None 表示内存存储
            embedding_model: 嵌入模型，默认使用 OpenAIEmbeddings
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        # 简化，不强制要求 OpenAI key
        try:
            self.embedding_model = embedding_model or OpenAIEmbeddings()
        except Exception:
            # 如果没有配置 OpenAI，使用一个简单的占位符
            self.embedding_model = None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.document_loader = DocumentLoader()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        self.vectorstore = self._init_vectorstore()

    def _init_vectorstore(self) -> Chroma:
        """初始化 ChromaDB 向量存储"""
        if self.embedding_model is None:
            # 如果没有嵌入模型，创建一个空的 Chroma 实例
            return Chroma(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory,
        )

    def add_documents(
        self,
        documents: List[Document],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        添加文档到知识库
        
        Args:
            documents: 文档列表
            metadata: 附加元数据
            
        Returns:
            添加的文档 ID 列表
        """
        chunks = self.text_splitter.split_documents(documents)
        
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        if self.embedding_model is not None:
            self.vectorstore.add_documents(documents=chunks, ids=ids)
        
        return ids

    def add_document_from_path(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        从文件路径添加文档
        
        Args:
            file_path: 文件路径
            metadata: 附加元数据
            
        Returns:
            添加的文档 ID 列表
        """
        documents = self.document_loader.load_document(file_path)
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        return self.add_documents(documents)

    def add_documents_from_directory(
        self,
        directory: str,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        从目录批量添加文档
        
        Args:
            directory: 目录路径
            recursive: 是否递归遍历子目录
            metadata: 附加元数据
            
        Returns:
            添加的文档 ID 列表
        """
        documents = self.document_loader.load_documents(directory, recursive)
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        return self.add_documents(documents)

    def delete_documents(self, ids: List[str]) -> None:
        """
        根据 ID 删除文档
        
        Args:
            ids: 文档 ID 列表
        """
        self.vectorstore.delete(ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter_dict: 元数据过滤条件
            
        Returns:
            相关文档列表
        """
        if self.embedding_model is None:
            return [
                Document(page_content="知识库未配置嵌入模型，请设置 OPENAI_API_KEY", metadata={})
            ]
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """
        相似度搜索，带分数
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter_dict: 元数据过滤条件
            
        Returns:
            (文档, 分数) 元组列表
        """
        if self.embedding_model is None:
            return [
                (Document(page_content="知识库未配置嵌入模型，请设置 OPENAI_API_KEY", metadata={}), 0.0)
            ]
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        MMR (最大边际相关性) 搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            fetch_k: 预取文档数量
            lambda_mult: 多样性参数 (0-1)，越小越多样
            filter_dict: 元数据过滤条件
            
        Returns:
            相关文档列表
        """
        if self.embedding_model is None:
            return [
                Document(page_content="知识库未配置嵌入模型，请设置 OPENAI_API_KEY", metadata={})
            ]
        return self.vectorstore.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=filter_dict,
        )

    def as_retriever(
        self,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ) -> VectorStoreRetriever:
        """
        获取检索器
        
        Args:
            search_type: 检索类型 (similarity, mmr, similarity_score_threshold)
            search_kwargs: 检索参数
            
        Returns:
            VectorStoreRetriever 实例
        """
        if self.embedding_model is None:
            raise ValueError("知识库未配置嵌入模型，请设置 OPENAI_API_KEY")
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs or {},
        )

    def get_document_count(self) -> int:
        """获取知识库中文档块数量"""
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        """清空知识库"""
        self.vectorstore.delete_collection()
        self.vectorstore = self._init_vectorstore()
