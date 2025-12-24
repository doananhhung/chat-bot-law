import pytest
from unittest.mock import MagicMock, patch
from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.generator import RAGChain
from src.ingestion.loader import DocumentLoader
from src.ingestion.splitter import TextSplitter
from src.ingestion.indexer import VectorIndexer
from src.config import AppConfig

@pytest.fixture(scope="module")
def initialized_index(test_data_dir, dummy_pdf):
    """Ensure index exists for retriever tests."""
    VectorIndexer.sync_index()
    return True

def test_retriever_initialization(initialized_index):
    """Test if retriever loads the index correctly."""
    retriever = SemanticRetriever()
    assert retriever.vector_store is not None

def test_retriever_search(initialized_index):
    """Test semantic search."""
    retriever = SemanticRetriever()
    # "test document" is in the dummy pdf content
    docs = retriever.get_relevant_docs("test document")
    
    assert len(docs) > 0
    assert "test document" in docs[0].page_content.lower()

@patch("src.rag_engine.generator.LLMFactory.create_llm")
def test_rag_generation(mock_create_llm, initialized_index):
    """Test RAG generation flow (mocking the chain execution)."""
    # Setup Mock LLM
    mock_llm = MagicMock()
    mock_create_llm.return_value = mock_llm
    
    # Initialize
    retriever = SemanticRetriever()
    rag_chain = RAGChain(retriever)
    
    # Mock the internal router to always return LEGAL
    rag_chain.router.classify = MagicMock(return_value="LEGAL")
    
    # Mock the internal qa_chain's invoke method
    rag_chain.qa_chain = MagicMock()
    rag_chain.qa_chain.invoke.return_value = "Đây là câu trả lời test."
    
    result = rag_chain.generate_answer("Test question")
    
    # Check if retrieval happened (source_documents present)
    assert len(result["source_documents"]) > 0
    # Check if answer matches mock
    assert result["answer"] == "Đây là câu trả lời test."
