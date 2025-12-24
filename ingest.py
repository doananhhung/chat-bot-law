import time
from src.ingestion.indexer import VectorIndexer
from src.utils.logger import logger

def main():
    start_time = time.time()
    logger.info("Starting Incremental Ingestion Pipeline...")
    
    # 3. Sync Index (Now handles loading and splitting internally based on changes)
    try:
        VectorIndexer.sync_index()
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return
    
    elapsed = time.time() - start_time
    logger.info(f"Ingestion complete in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()