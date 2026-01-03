import time
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import AppConfig
import torch

def benchmark_embedding():
    print("=== Embedding Performance Benchmark ===")
    print(f"Model: {AppConfig.EMBEDDING_MODEL_NAME}")
    print(f"Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    # 1. Load Model
    start_load = time.time()
    embeddings = HuggingFaceEmbeddings(
        model_name=AppConfig.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    load_time = time.time() - start_load
    print(f"Model Load Time: {load_time:.2f}s")

    # Sample texts
    single_text = "Thủ tục đăng ký kinh doanh hộ cá thể như thế nào?"
    batch_10 = [f"Câu hỏi thứ {i}: Điều kiện hưởng bảo hiểm xã hội một lần là gì?" for i in range(10)]
    batch_100 = [f"Đoạn văn bản mẫu số {i} dùng để kiểm tra tốc độ xử lý của hệ thống embedding trên CPU." for i in range(100)]

    # 2. Benchmark Single Query (Lặp lại 5 lần để lấy trung bình)
    print("\n--- 1. Single Query Latency ---")
    latencies = []
    for _ in range(5):
        st = time.time()
        _ = embeddings.embed_query(single_text)
        latencies.append(time.time() - st)
    avg_latency = np.mean(latencies)
    print(f"Average Latency: {avg_latency*1000:.2f}ms")

    # 3. Benchmark Batch 10
    print("\n--- 2. Batch Processing (10 texts) ---")
    st = time.time()
    _ = embeddings.embed_documents(batch_10)
    batch_10_time = time.time() - st
    print(f"Total Time: {batch_10_time:.2f}s")
    print(f"Per Document: {(batch_10_time/10)*1000:.2f}ms")

    # 4. Benchmark Batch 100 (Stress Test)
    print("\n--- 3. Batch Processing (100 texts) ---")
    st = time.time()
    _ = embeddings.embed_documents(batch_100)
    batch_100_time = time.time() - st
    print(f"Total Time: {batch_100_time:.2f}s")
    print(f"Throughput: {100/batch_100_time:.2f} docs/sec")

if __name__ == "__main__":
    benchmark_embedding()
