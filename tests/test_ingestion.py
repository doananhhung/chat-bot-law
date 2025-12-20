import pytest
from src.ingestion.loader import DocumentLoader
from src.ingestion.splitter import TextSplitter
from src.ingestion.indexer import VectorIndexer
from src.config import AppConfig
import os

def test_document_loader(dummy_pdf):
    """Test loading documents from directory."""
    result = DocumentLoader.load_documents(AppConfig.RAW_DATA_PATH)
    
    assert len(result.documents) > 0
    assert result.documents[0].metadata["source"] == "test_doc.pdf"
    assert len(result.failed_files) == 0

def test_text_splitter(dummy_pdf):
    """Test splitting documents."""
    # Load first
    load_result = DocumentLoader.load_documents(AppConfig.RAW_DATA_PATH)
    
    # Split
    chunks = TextSplitter.split_documents(load_result.documents)
    
    assert len(chunks) > 0
    assert "chunk_id" in chunks[0].metadata
    assert "total_chunks" in chunks[0].metadata
    # Check if context is preserved (metadata)
    assert chunks[0].metadata["source"] == "test_doc.pdf"

def test_vector_indexer(dummy_pdf):
    """Test creating vector index."""
    # Load & Split
    load_result = DocumentLoader.load_documents(AppConfig.RAW_DATA_PATH)
    chunks = TextSplitter.split_documents(load_result.documents)
    
    # Index
    VectorIndexer.build_index(chunks)
    
    # Check if index file exists
    index_path = os.path.join(AppConfig.VECTOR_DB_PATH, "index.faiss")
    assert os.path.exists(index_path)
