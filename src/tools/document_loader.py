import os
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from src.utils.logger import get_logger

logger = get_logger("agent")


class DocumentLoader:
    """文档加载器，支持多种格式文档的加载"""

    def __init__(self):
        self.supported_formats = {
            ".pdf": self._load_pdf,
            ".txt": self._load_txt,
            ".md": self._load_markdown,
            ".markdown": self._load_markdown,
        }

    def load_document(self, file_path: str) -> List[Document]:
        """加载单个文档"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        suffix = path.suffix.lower()
        if suffix not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {suffix}")

        return self.supported_formats[suffix](file_path)

    def load_documents(self, directory: str, recursive: bool = True) -> List[Document]:
        """批量加载目录下的文档"""
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileNotFoundError(f"目录不存在: {directory}")

        documents = []
        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    docs = self.load_document(str(file_path))
                    documents.extend(docs)
                except Exception as e:
                    logger.error("加载文件 %s 失败: %s", file_path, e)

        return documents

    def _load_pdf(self, file_path: str) -> List[Document]:
        """加载 PDF 文档"""
        loader = PyPDFLoader(file_path)
        return loader.load()

    def _load_txt(self, file_path: str) -> List[Document]:
        """加载 TXT 文档"""
        loader = TextLoader(file_path, encoding="utf-8")
        return loader.load()

    def _load_markdown(self, file_path: str) -> List[Document]:
        """加载 Markdown 文档"""
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()
