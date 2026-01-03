import time
import os
from src.rag_engine.retriever import SemanticRetriever
from src.utils.logger import logger

# Disable detailed logging for benchmark clarity
logger.setLevel("CRITICAL")

def benchmark_retrieval():
    print("=== Document Retrieval Benchmark ===")
    
    # 1. Measure Initialization Time (Load Index from Disk)
    print("1. Loading Vector Store (Cold Start)...")
    start_init = time.time()
    try:
        retriever = SemanticRetriever()
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Please run ingestion first!")
        return
        
    init_time = time.time() - start_init
    print(f"-> Load Time: {init_time:.4f}s")

    # Sample Queries
    queries = [
        "Thủ tục đăng ký kinh doanh",
        "Luật lao động về nghỉ thai sản",
        "Quyền lợi bảo hiểm y tế",
        "Hợp đồng lao động không xác định thời hạn",
        "Xử phạt vi phạm giao thông"
    ]

    # 2. Measure Search Latency
    print("\n2. Measuring Search Latency (k=10)...")
    latencies = []
    
    # Warm-up (First search often takes longer due to loading libraries/caches)
    _ = retriever.get_relevant_docs("Warm up query", k=10)
    
    for query in queries:
        st = time.time()
        docs = retriever.get_relevant_docs(query, k=10)
        et = time.time()
        duration = et - st
        latencies.append(duration)
        print(f"   Query: '{query[:30]}...' -> Found {len(docs)} docs in {duration*1000:.2f}ms")

    avg_latency = sum(latencies) / len(latencies)
    print(f"\n-> Average Search Latency: {avg_latency*1000:.2f}ms")
    print(f"-> Min: {min(latencies)*1000:.2f}ms | Max: {max(latencies)*1000:.2f}ms")

if __name__ == "__main__":
    benchmark_retrieval()
