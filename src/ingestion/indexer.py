import os
import shutil
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.config import AppConfig
from src.utils.logger import logger

class VectorIndexer:
    """Handles embedding creation and vector database indexing."""
    
    @staticmethod
    def build_index(chunks: List[Document]) -> None:
        """
        Build and save FAISS index from document chunks.
        """
        if not chunks:
            logger.warning("No chunks to index. Skipping.")
            return

        # 1. Initialize Embeddings
        logger.info(f"Loading embedding model: {AppConfig.EMBEDDING_MODEL_NAME}")
        embeddings = HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'}, # Force CPU for MVP/Compatibility
            encode_kwargs={'normalize_embeddings': True} # Design requirement
        )
        
        # 2. Create Vector Store
        logger.info(f"Creating FAISS index for {len(chunks)} chunks...")
        try:
            vector_store = FAISS.from_documents(chunks, embeddings)
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise e
        
        # 3. Save to Disk (Full Replace Strategy)
        save_path = AppConfig.VECTOR_DB_PATH
        
        # Clear existing
        if os.path.exists(save_path):
            logger.info("Removing existing vector store (Full Replace)...")
            shutil.rmtree(save_path)
            
        # Create dir (save_local creates it usually, but rmtree removed it)
        # FAISS save_local creates the directory if needed? 
        # Actually it expects the folder path.
        
        logger.info(f"Saving index to {save_path}...")
        vector_store.save_local(save_path)
        logger.info("Index saved successfully.")
