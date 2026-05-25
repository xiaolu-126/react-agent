
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from langchain_core.documents import Document
from src.tools.knowledge_base import KnowledgeBase
from src.tools.document_loader import DocumentLoader


class TestDocumentLoader:
    @pytest.fixture
    def temp_file(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', encoding='utf-8', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        yield temp_path
        import os
        os.unlink(temp_path)

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_init(self):
        loader = DocumentLoader()
        assert loader.supported_formats is not None
        assert '.txt' in loader.supported_formats

    def test_load_text_document(self, temp_file):
        loader = DocumentLoader()
        docs = loader.load_document(temp_file)
        assert len(docs) &gt; 0
        assert isinstance(docs[0], Document)

    def test_load_nonexistent_file(self):
        loader = DocumentLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_document("nonexistent.txt")

    def test_load_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            temp_path = f.name

        loader = DocumentLoader()
        with pytest.raises(ValueError):
            loader.load_document(temp_path)

        import os
        os.unlink(temp_path)

    def test_load_documents_from_dir(self, temp_dir):
        (temp_dir / 'test1.txt').write_text('Content 1', encoding='utf-8')
        (temp_dir / 'test2.txt').write_text('Content 2', encoding='utf-8')

        loader = DocumentLoader()
        docs = loader.load_documents(str(temp_dir))
        assert len(docs) &gt;= 2

    def test_load_nonexistent_dir(self):
        loader = DocumentLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_documents("/nonexistent/path")


class TestKnowledgeBase:
    @pytest.fixture
    def mock_embeddings(self):
        mock = Mock()
        mock.embed_query.return_value = [0.1] * 10
        mock.embed_documents.return_value = [[0.1] * 10]
        return mock

    @pytest.fixture
    def temp_persist_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @patch('src.tools.knowledge_base.Chroma')
    def test_init(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(
            collection_name="test",
            embedding_model=mock_embeddings
        )
        assert kb.collection_name == "test"

    @patch('src.tools.knowledge_base.Chroma')
    def test_add_documents(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)

        docs = [
            Document(page_content="Test document 1", metadata={"source": "test1"}),
            Document(page_content="Test document 2", metadata={"source": "test2"})
        ]

        ids = kb.add_documents(docs)
        assert ids is not None
        assert len(ids) &gt; 0

    @patch('src.tools.knowledge_base.Chroma')
    def test_add_document_from_path(self, mock_chroma, mock_embeddings, temp_file):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)

        with patch.object(DocumentLoader, 'load_document') as mock_load:
            mock_load.return_value = [Document(page_content="Test")]
            ids = kb.add_document_from_path(temp_file)
            assert ids is not None

    @patch('src.tools.knowledge_base.Chroma')
    def test_add_documents_from_directory(self, mock_chroma, mock_embeddings, temp_dir):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        (temp_dir / 'doc.txt').write_text('Test doc', encoding='utf-8')

        kb = KnowledgeBase(embedding_model=mock_embeddings)

        with patch.object(DocumentLoader, 'load_documents') as mock_load:
            mock_load.return_value = [Document(page_content="Test")]
            ids = kb.add_documents_from_directory(str(temp_dir))
            assert ids is not None

    @patch('src.tools.knowledge_base.Chroma')
    def test_delete_documents(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        kb.delete_documents(["id1", "id2"])
        mock_chroma_instance.delete.assert_called_once()

    @patch('src.tools.knowledge_base.Chroma')
    def test_similarity_search(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = [
            Document(page_content="Result 1"),
            Document(page_content="Result 2")
        ]
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        results = kb.similarity_search("query", k=2)

        assert len(results) == 2
        mock_chroma_instance.similarity_search.assert_called_once_with(
            query="query", k=2, filter=None
        )

    @patch('src.tools.knowledge_base.Chroma')
    def test_similarity_search_with_score(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search_with_score.return_value = [
            (Document(page_content="Result"), 0.8)
        ]
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        results = kb.similarity_search_with_score("query")

        assert len(results) &gt; 0
        assert isinstance(results[0][0], Document)
        assert isinstance(results[0][1], float)

    @patch('src.tools.knowledge_base.Chroma')
    def test_max_marginal_relevance_search(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma_instance.max_marginal_relevance_search.return_value = [
            Document(page_content="Result")
        ]
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        results = kb.max_marginal_relevance_search("query")

        assert len(results) &gt; 0
        mock_chroma_instance.max_marginal_relevance_search.assert_called_once()

    @patch('src.tools.knowledge_base.Chroma')
    def test_as_retriever(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_retriever = Mock()
        mock_chroma_instance.as_retriever.return_value = mock_retriever
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        retriever = kb.as_retriever()

        assert retriever is not None

    @patch('src.tools.knowledge_base.Chroma')
    def test_get_document_count(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_chroma_instance._collection = mock_collection
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        count = kb.get_document_count()

        assert count == 10

    @patch('src.tools.knowledge_base.Chroma')
    def test_clear(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        kb.clear()

        mock_chroma_instance.delete_collection.assert_called_once()

    @patch('src.tools.knowledge_base.Chroma')
    def test_persist(self, mock_chroma, mock_embeddings, temp_persist_dir):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(
            persist_directory=temp_persist_dir,
            embedding_model=mock_embeddings
        )
        kb.persist()

        mock_chroma_instance.persist.assert_called_once()

    @patch('src.tools.knowledge_base.Chroma')
    def test_update_document(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        kb.update_document("doc_id", Document(page_content="New content"))

        mock_chroma_instance.delete.assert_called_once()

    @patch('src.tools.knowledge_base.Chroma')
    def test_add_documents_with_metadata(self, mock_chroma, mock_embeddings):
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        kb = KnowledgeBase(embedding_model=mock_embeddings)
        docs = [Document(page_content="Test")]

        ids = kb.add_documents(docs, metadata={"category": "test"})
        assert ids is not None

