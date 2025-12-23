from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config import AppConfig
from src.utils.logger import logger

class SemanticRetriever:
    """Handles semantic search against the vector database."""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = self._load_vector_store()
        
    def _load_vector_store(self):
        try:
            logger.info(f"Loading vector store from {AppConfig.VECTOR_DB_PATH}")
            return FAISS.load_local(
                AppConfig.VECTOR_DB_PATH, 
                self.embeddings,
                allow_dangerous_deserialization=True 
                # Safe because we created the index ourselves in this trusted environment
            )
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            # If load fails (e.g., no index), we might want to return None or raise
            # For now, let's raise so the app knows it's not ready
            raise RuntimeError("Vector Store not found. Please run ingestion first.")

    def get_relevant_docs(self, query: str, k: int = 4) -> List[Document]:
        """
        Retrieve top k relevant documents for the query.
        """
        if not self.vector_store:
            logger.warning("Vector store is not initialized.")
            return []
            
        logger.info(f"Searching for: '{query}'")
        docs = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Found {len(docs)} relevant documents.")
        return docs
