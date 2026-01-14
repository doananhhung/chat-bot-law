from typing import List
import faiss
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
        self._configure_search_params()

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

    def _configure_search_params(self):
        """Configure search parameters based on detected index type."""
        if not self.vector_store:
            return

        index = self.vector_store.index
        index_type = self._detect_index_type(index)

        if index_type == "ivf":
            # Set nprobe for IVF-based indexes
            # Need to get the underlying IVF index
            ivf_index = self._get_ivf_index(index)
            if ivf_index:
                ivf_index.nprobe = AppConfig.IVF_NPROBE
                logger.info(f"IVF Index detected: nlist={ivf_index.nlist}, nprobe={ivf_index.nprobe}")
        else:
            logger.info(f"Flat index detected: {type(index).__name__}")

    def _detect_index_type(self, index) -> str:
        """Detect the type of FAISS index."""
        # Check if it's an IVF-based index
        if hasattr(index, 'nprobe'):
            return "ivf"

        # Check for wrapped indexes (e.g., IndexPreTransform)
        if hasattr(index, 'index'):
            inner_index = index.index
            if hasattr(inner_index, 'nprobe'):
                return "ivf"

        return "flat"

    def _get_ivf_index(self, index):
        """Extract the IVF index from potentially wrapped indexes."""
        # Direct IVF index
        if hasattr(index, 'nprobe'):
            return index

        # Wrapped index (e.g., IndexPreTransform, IndexIDMap)
        if hasattr(index, 'index'):
            inner = index.index
            if hasattr(inner, 'nprobe'):
                return inner

        return None

    def get_index_info(self) -> dict:
        """Get information about the current index for debugging/benchmarking."""
        if not self.vector_store:
            return {"error": "Vector store not loaded"}

        index = self.vector_store.index
        info = {
            "index_type": self._detect_index_type(index),
            "ntotal": index.ntotal,
            "dimension": index.d,
        }

        ivf_index = self._get_ivf_index(index)
        if ivf_index:
            info["nlist"] = ivf_index.nlist
            info["nprobe"] = ivf_index.nprobe

        return info

    def get_relevant_docs(self, query: str, k: int = 10) -> List[Document]:
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
