import time
from src.config import AppConfig
from src.ingestion.loader import DocumentLoader
from src.ingestion.splitter import TextSplitter
from src.ingestion.indexer import VectorIndexer
from src.utils.logger import logger

def main():
    start_time = time.time()
    logger.info("Starting Ingestion Pipeline...")
    
    # 1. Load
    load_result = DocumentLoader.load_documents(AppConfig.RAW_DATA_PATH)
    if not load_result.documents:
        logger.warning("No documents found to process.")
        return

    if load_result.failed_files:
        logger.warning(f"Failed to load {len(load_result.failed_files)} files.")

    # 2. Split
    chunks = TextSplitter.split_documents(load_result.documents)
    
    # 3. Index
    VectorIndexer.build_index(chunks)
    
    elapsed = time.time() - start_time
    logger.info(f"Ingestion complete in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
