import os
import shutil
import numpy as np
import faiss
from typing import List, Dict, Set, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.config import AppConfig
from src.utils.logger import logger
from src.ingestion.metadata import MetadataManager
from src.ingestion.loader import DocumentLoader
from src.ingestion.splitter import TextSplitter


class VectorIndexer:
    """Handles embedding creation and vector database indexing with configurable FAISS index types."""

    @staticmethod
    def _get_embeddings():
        logger.info(f"Loading embedding model: {AppConfig.EMBEDDING_MODEL_NAME}")
        return HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    @staticmethod
    def _create_faiss_index(
        docs: List[Document],
        embeddings,
        chunk_ids: List[str]
    ) -> FAISS:
        """
        Create a FAISS index with configurable index type (Flat, IVF, IVFPQ).

        For IVF indexes, this method:
        1. Generates embeddings for all documents
        2. Creates the index using FAISS factory
        3. Trains the index (learns cluster centroids via K-means)
        4. Adds vectors to the trained index
        5. Wraps with LangChain FAISS for compatibility
        """
        # 1. Generate embeddings matrix
        texts = [doc.page_content for doc in docs]
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings_matrix = np.array(embeddings.embed_documents(texts)).astype('float32')
        dimension = embeddings_matrix.shape[1]

        # 2. Get index factory string from config
        factory_string = AppConfig.get_index_factory_string()
        logger.info(f"Creating FAISS index with factory: '{factory_string}'")

        # 3. Create index using factory
        index = faiss.index_factory(dimension, factory_string, faiss.METRIC_L2)

        # 4. Train if necessary (IVF indexes require training)
        if not index.is_trained:
            n_vectors = len(embeddings_matrix)
            # Check if we have enough vectors for training
            if AppConfig.VECTOR_INDEX_TYPE in ["ivf", "ivfpq"]:
                min_vectors_for_training = AppConfig.IVF_NLIST
                if n_vectors < min_vectors_for_training:
                    logger.warning(
                        f"Not enough vectors ({n_vectors}) for IVF training "
                        f"(need at least {min_vectors_for_training}). "
                        f"Falling back to Flat index."
                    )
                    # Fallback to Flat index
                    index = faiss.IndexFlatL2(dimension)
                else:
                    logger.info(f"Training IVF index on {n_vectors} vectors...")
                    index.train(embeddings_matrix)
                    logger.info("IVF training completed.")

        # 5. Add vectors to index
        index.add(embeddings_matrix)
        logger.info(f"Added {index.ntotal} vectors to index.")

        # 6. Build docstore and id mappings for LangChain compatibility
        docstore_dict = {chunk_ids[i]: docs[i] for i in range(len(docs))}
        index_to_docstore_id = {i: chunk_ids[i] for i in range(len(chunk_ids))}

        # 7. Create LangChain FAISS wrapper
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(docstore_dict),
            index_to_docstore_id=index_to_docstore_id
        )

        return vector_store

    @staticmethod
    def _add_to_existing_index(
        vector_store: FAISS,
        docs: List[Document],
        embeddings,
        chunk_ids: List[str]
    ) -> FAISS:
        """
        Add documents to an existing FAISS index.

        Note: For IVF indexes, adding documents without retraining may slightly
        degrade quality if the data distribution changes significantly.
        For major updates, consider rebuilding the index.
        """
        # Use LangChain's add_documents for simplicity
        # This works for both Flat and IVF indexes
        vector_store.add_documents(docs, ids=chunk_ids)
        return vector_store

    @staticmethod
    def rebuild_index() -> None:
        """
        Rebuild the entire FAISS index from scratch.

        This is recommended when:
        - Switching index types (e.g., from Flat to IVF)
        - Data distribution has changed significantly
        - You want to retrain IVF clusters with current data

        For IVF indexes, this ensures optimal cluster centroids.
        """
        raw_data_path = AppConfig.RAW_DATA_PATH
        if not os.path.exists(raw_data_path):
            logger.warning(f"Data directory not found: {raw_data_path}")
            return

        # 1. Collect all documents
        all_docs = []
        all_chunk_ids = []
        metadata_mgr = MetadataManager()

        current_files = [f for f in os.listdir(raw_data_path) if os.path.isfile(os.path.join(raw_data_path, f))]

        if not current_files:
            logger.warning("No files found in data directory.")
            return

        logger.info(f"Rebuilding index from {len(current_files)} files...")

        for filename in current_files:
            file_path = os.path.join(raw_data_path, filename)
            file_hash = MetadataManager.calculate_file_hash(file_path)

            # Load
            docs = DocumentLoader.load_single_file(file_path)
            if not docs:
                continue

            # Split
            chunks = TextSplitter.split_documents(docs)
            if not chunks:
                continue

            # Assign IDs
            chunk_ids = []
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{file_hash}_{idx}"
                chunk_ids.append(chunk_id)
                chunk.metadata['chunk_id'] = chunk_id

            all_docs.extend(chunks)
            all_chunk_ids.extend(chunk_ids)

            # Update metadata
            metadata_mgr.update_file_entry(filename, file_hash, chunk_ids)

        if not all_docs:
            logger.warning("No documents to index.")
            return

        # 2. Build index with configured type
        embeddings = VectorIndexer._get_embeddings()
        logger.info(f"Building {AppConfig.VECTOR_INDEX_TYPE.upper()} index with {len(all_docs)} chunks...")

        vector_store = VectorIndexer._create_faiss_index(all_docs, embeddings, all_chunk_ids)

        # 3. Save
        vector_store_path = AppConfig.VECTOR_DB_PATH
        os.makedirs(vector_store_path, exist_ok=True)
        vector_store.save_local(vector_store_path)
        metadata_mgr.save_metadata()

        logger.info(f"Index rebuilt successfully: {AppConfig.VECTOR_INDEX_TYPE.upper()} with {len(all_docs)} vectors.")

    @staticmethod
    def sync_index() -> None:
        """
        Synchronize the vector index with the data directory (Incremental Update).
        """
        raw_data_path = AppConfig.RAW_DATA_PATH
        if not os.path.exists(raw_data_path):
            logger.warning(f"Data directory not found: {raw_data_path}")
            return

        # 1. Initialize Metadata Manager
        metadata_mgr = MetadataManager()
        
        # 2. Get current files in data/raw
        current_files = [f for f in os.listdir(raw_data_path) if os.path.isfile(os.path.join(raw_data_path, f))]
        current_files_set = set(current_files)
        
        # 3. Identify Changes
        # Files tracked in metadata
        tracked_files = set(metadata_mgr.get_all_files())
        
        # Calculate hashes for current files
        current_hashes = {}
        for filename in current_files:
            file_path = os.path.join(raw_data_path, filename)
            current_hashes[filename] = MetadataManager.calculate_file_hash(file_path)
            
        # Classify
        files_to_add = []
        files_to_update = []
        files_to_delete = []
        files_skipped = []
        
        # Detect Deletions
        for filename in tracked_files:
            if filename not in current_files_set:
                files_to_delete.append(filename)
                
        # Detect Adds and Updates
        for filename in current_files:
            file_hash = current_hashes[filename]
            entry = metadata_mgr.get_file_entry(filename)
            
            if not entry:
                files_to_add.append(filename)
            elif entry['hash'] != file_hash:
                files_to_update.append(filename)
            else:
                files_skipped.append(filename)
                
        logger.info(f"Sync Analysis: Add={len(files_to_add)}, Update={len(files_to_update)}, Delete={len(files_to_delete)}, Skip={len(files_skipped)}")
        
        if not (files_to_add or files_to_update or files_to_delete):
            logger.info("No changes detected. Index is up to date.")
            return

        # 4. Load or Initialize Vector Store
        embeddings = VectorIndexer._get_embeddings()
        vector_store_path = AppConfig.VECTOR_DB_PATH
        
        if os.path.exists(os.path.join(vector_store_path, "index.faiss")):
            logger.info("Loading existing FAISS index...")
            try:
                vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                logger.error(f"Failed to load index: {e}. Starting fresh.")
                vector_store = None
        else:
            logger.info("No existing index found. Starting fresh.")
            vector_store = None

        # 5. Handle Deletions & Updates (Delete old chunks first)
        ids_to_remove = []
        
        # Process Deletions
        for filename in files_to_delete:
            entry = metadata_mgr.get_file_entry(filename)
            if entry and 'chunk_ids' in entry:
                ids_to_remove.extend(entry['chunk_ids'])
            metadata_mgr.remove_file_entry(filename)
            
        # Process Updates (Remove old versions)
        for filename in files_to_update:
            entry = metadata_mgr.get_file_entry(filename)
            if entry and 'chunk_ids' in entry:
                ids_to_remove.extend(entry['chunk_ids'])
            # We don't remove entry yet, we update it later
            
        if ids_to_remove:
            logger.info(f"Removing {len(ids_to_remove)} vectors...")
            if vector_store:
                try:
                    vector_store.delete(ids_to_remove)
                except Exception as e:
                    logger.error(f"Error during deletion: {e}")
                    # If deletion fails, we might have inconsistent state. 
                    # Rebuilding might be safer, but for now we proceed.

        # 6. Handle Adds & Updates (Add new chunks)
        files_to_process = files_to_add + files_to_update

        # For new index creation, collect all chunks first (needed for IVF training)
        all_new_chunks = []
        all_new_chunk_ids = []
        file_chunk_mapping = {}  # Track chunk_ids per file for metadata

        for filename in files_to_process:
            file_path = os.path.join(raw_data_path, filename)
            file_hash = current_hashes[filename]

            # Load
            docs = DocumentLoader.load_single_file(file_path)
            if not docs:
                continue

            # Split
            chunks = TextSplitter.split_documents(docs)
            if not chunks:
                continue

            # Assign IDs
            chunk_ids = []
            for idx, chunk in enumerate(chunks):
                # ID format: [filename_hash]_[chunk_index]
                # We use file_hash (content hash) as prefix
                chunk_id = f"{file_hash}_{idx}"
                chunk_ids.append(chunk_id)
                # Ensure metadata has this ID (FAISS needs it in add_documents)
                # Actually, FAISS add_documents(documents, ids=...)
                # The document metadata doesn't strictly need it, but good to have.
                chunk.metadata['chunk_id'] = chunk_id

            # Store for later
            file_chunk_mapping[filename] = (file_hash, chunk_ids)

            # Add to Vector Store
            if vector_store is None:
                # Collect all chunks first for proper IVF training
                all_new_chunks.extend(chunks)
                all_new_chunk_ids.extend(chunk_ids)
            else:
                # Add to existing index
                vector_store.add_documents(chunks, ids=chunk_ids)

        # If we need to create a new index
        if vector_store is None and all_new_chunks:
            logger.info(f"Creating new {AppConfig.VECTOR_INDEX_TYPE.upper()} index with {len(all_new_chunks)} chunks...")
            vector_store = VectorIndexer._create_faiss_index(all_new_chunks, embeddings, all_new_chunk_ids)

        # Update Metadata for all processed files
        for filename, (file_hash, chunk_ids) in file_chunk_mapping.items():
            metadata_mgr.update_file_entry(filename, file_hash, chunk_ids)

        # 7. Save Changes
        if vector_store:
            logger.info(f"Saving updated index to {vector_store_path}...")
            vector_store.save_local(vector_store_path)
            metadata_mgr.save_metadata()
            logger.info("Index sync completed successfully.")
        else:
             # If everything was deleted and nothing added
            if files_to_delete and not files_to_process:
                 # Should we delete the index file?
                 # Or keep empty index? FAISS might not save empty.
                 # For now, just save metadata.
                 metadata_mgr.save_metadata()
                 logger.info("Index is empty (all files deleted).")