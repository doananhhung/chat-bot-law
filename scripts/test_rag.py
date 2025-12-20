import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.generator import RAGChain
from src.utils.logger import logger

def main():
    logger.info("Initializing RAG Engine...")
    
    try:
        retriever = SemanticRetriever()
        rag_chain = RAGChain(retriever)
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return

    question = "Đối tượng áp dụng của luật thử nghiệm là ai?"
    logger.info(f"Asking: {question}")
    
    result = rag_chain.generate_answer(question)
    
    print("\n" + "="*50)
    print("ANSWER:")
    print(result["answer"])
    print("="*50)
    
    print("\nSOURCES:")
    for doc in result.get("source_documents", []):
        print(f"- {doc.metadata.get('source')}")

if __name__ == "__main__":
    main()

