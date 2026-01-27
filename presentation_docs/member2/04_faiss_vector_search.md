# 🔍 FAISS Vector Search

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- FAISS là gì và tại sao cần vector database
- Các loại index (Flat, IVF, IVFPQ)
- Trade-offs giữa accuracy và speed
- Cách cấu hình FAISS trong dự án

---

## 1. FAISS là gì?

### 1.1 Định nghĩa
**FAISS (Facebook AI Similarity Search)** là thư viện tìm kiếm vector hiệu quả, phát triển bởi Facebook AI Research.

### 1.2 Tại sao cần Vector Database?

| Traditional DB | Vector DB (FAISS) |
|----------------|-------------------|
| Keyword search | Semantic search |
| Exact match | Similarity match |
| "thai sản" | "nghỉ đẻ", "maternity leave" |
| O(n) scan hoặc index | O(1) → O(log n) với index |

### 1.3 Use Case trong dự án

```
User Query: "Nghỉ sinh con được mấy tháng?"
      │
      ▼ Embedding
[0.12, -0.34, ..., 0.78]  (query vector)
      │
      ▼ FAISS Search
      │
Find Top-10 similar vectors from 1500 chunks
      │
      ▼
[Chunk về Điều 139], [Chunk về thai sản], ...
```

---

## 2. FAISS Index Types

### 2.1 Index Types trong dự án

| Type | Factory String | Mô tả |
|------|----------------|-------|
| **Flat** | `"Flat"` | Brute-force exact search |
| **IVF** | `"IVF64,Flat"` | Clustering-based approximate |
| **IVFPQ** | `"IVF64,PQ48x8"` | Clustering + Product Quantization |

### 2.2 Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                        INDEX TYPES                           │
│                                                             │
│   FLAT                    IVF                    IVFPQ      │
│   ●●●●●●●●               ┌──●●●┐                ┌──○○○┐    │
│   ●●●●●●●●               │     │                │     │    │
│   ●●●●●●●●               └──●●●┘ Cluster 1      └──○○○┘    │
│   (all dots)             ┌──●●●┐                ┌──○○○┐    │
│                          │     │                │     │    │
│   Search ALL             └──●●●┘ Cluster 2      └──○○○┘    │
│                          (search some clusters) (compressed)│
│                                                             │
│   Speed: Slow            Speed: Fast            Speed: Fastest│
│   Accuracy: 100%         Accuracy: ~96%         Accuracy: ~92%│
│   Memory: Large          Memory: Medium         Memory: Small │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Flat Index (Exact Search)

### 3.1 Hoạt động

```
Query Vector ──►┌─────────────────────────────┐
                │  Compare với TẤT CẢ vectors │
                │  trong database             │
                └─────────────────────────────┘
                              │
                              ▼
                        Top-K Results (100% accurate)
```

### 3.2 Complexity

| Metric | Value |
|--------|-------|
| Search | O(n × d) |
| Memory | O(n × d) |
| Accuracy | 100% |

Với n = 1500 vectors, d = 768:
- ~1.15M comparisons per query

### 3.3 Khi nào dùng?
- Dataset nhỏ (< 10K vectors)
- Cần 100% accuracy
- Latency không critical

---

## 4. IVF Index (Inverted File)

### 4.1 Ý tưởng: Clustering

```
Training Phase:               Search Phase:
                              
K-means clustering            1. Find nearest cluster(s)
    on vectors                2. Search only within those
        │                            clusters
        ▼                            
┌───────────────────┐        Query ──► Cluster 3 ──► Top-K
│  64 clusters       │                 (skip other clusters)
│  ●──┐  ●──┐  ●──┐ │
│  ●  │  ●  │  ●  │ │
│  ●──┘  ●──┘  ●──┘ │
└───────────────────┘
```

### 4.2 Parameters

| Parameter | Meaning | Trong dự án |
|-----------|---------|-------------|
| **nlist** | Số clusters | 64 |
| **nprobe** | Clusters to search | 8-32 |

### 4.3 Trade-off: nprobe

```
nprobe = 1:   Search 1.5% of data    → Fast, Low recall
nprobe = 8:   Search 12.5% of data   → Balanced
nprobe = 32:  Search 50% of data     → Slow, High recall
nprobe = 64:  Search 100% of data    → Same as Flat
```

### 4.4 Benchmark Results (1530 vectors)

| nprobe | Latency | Recall@10 |
|--------|---------|-----------|
| 1 | 88ms | 33.3% |
| 8 | 87ms | 73.3% |
| 32 | 94ms | 96.7% ✓ |
| 64 | 93ms | 100% |

**Recommendation**: nprobe=32 cho 97% recall với minimal latency impact

---

## 5. IVFPQ (IVF + Product Quantization)

### 5.1 Ý tưởng: Compression

```
Original Vector (768D, 3KB):
[0.12, -0.34, 0.56, ... , 0.78]
        │
        ▼ Product Quantization
        │
Compressed (48 bytes):
[code1, code2, ..., code48]

Memory savings: ~98%
```

### 5.2 Khi nào dùng?
- Dataset rất lớn (100K+ vectors)
- Memory constrained
- Có thể chấp nhận ~92% accuracy

### 5.3 Trong dự án
```
VECTOR_INDEX_TYPE=ivfpq
Factory: "IVF64,PQ48x8"
         ↑     ↑
         │     PQ48: 768/48 = 16 dimensions per subvector
         │     x8: 8-bit codes
         nlist=64 clusters
```

---

## 6. Cấu hình trong dự án

### 6.1 Environment Variables (.env)

```bash
# Index type
VECTOR_INDEX_TYPE=ivf    # flat, ivf, ivfpq

# IVF parameters
IVF_NLIST=64            # Number of clusters
IVF_NPROBE=32           # Clusters to search at query time
```

### 6.2 Config Code

```python
# src/config.py
class AppConfig:
    VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "flat")
    IVF_NLIST = int(os.getenv("IVF_NLIST", "64"))
    IVF_NPROBE = int(os.getenv("IVF_NPROBE", "8"))
    
    @classmethod
    def get_index_factory_string(cls) -> str:
        if cls.VECTOR_INDEX_TYPE == "flat":
            return "Flat"
        elif cls.VECTOR_INDEX_TYPE == "ivf":
            return f"IVF{cls.IVF_NLIST},Flat"
        elif cls.VECTOR_INDEX_TYPE == "ivfpq":
            return f"IVF{cls.IVF_NLIST},PQ48x8"
```

---

## 7. Index Creation Flow

### 7.1 Code

```python
# src/ingestion/indexer.py

def _create_faiss_index(docs, embeddings, chunk_ids):
    # 1. Generate embeddings
    texts = [doc.page_content for doc in docs]
    embeddings_matrix = np.array(embeddings.embed_documents(texts))
    dimension = embeddings_matrix.shape[1]  # 768
    
    # 2. Create index using factory
    factory_string = AppConfig.get_index_factory_string()
    index = faiss.index_factory(dimension, factory_string, faiss.METRIC_L2)
    
    # 3. Train if IVF
    if not index.is_trained:
        logger.info("Training IVF index...")
        index.train(embeddings_matrix)
    
    # 4. Add vectors
    index.add(embeddings_matrix)
    
    # 5. Wrap with LangChain FAISS
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(docstore_dict),
        index_to_docstore_id=index_to_docstore_id
    )
    
    return vector_store
```

### 7.2 Training Requirements

```
IVF64 training requires:
- Minimum: 64 vectors (= nlist)
- Recommended: 64 × 39 = 2,496 vectors

If not enough vectors:
→ Fallback to Flat index automatically
```

---

## 8. Query Time Configuration

### 8.1 Set nprobe at Runtime

```python
# src/rag_engine/retriever.py

def set_search_mode(self, mode: str):
    ivf_index = self._get_ivf_index(index)
    
    mode_config = {
        "quality": ivf_index.nlist,  # 64 - search all
        "balanced": 8,               # 12.5% of clusters
        "speed": 2,                  # 3% of clusters
    }
    
    ivf_index.nprobe = mode_config[mode]
```

### 8.2 UI Selection

```python
# app.py
search_mode = st.radio(
    "Chọn chế độ:",
    options=["balanced", "quality", "speed"],
    format_func=lambda x: {
        "quality": "🎯 Chính xác cao",
        "balanced": "⚖️ Cân bằng (Khuyến nghị)",
        "speed": "🚀 Tốc độ cao"
    }[x]
)
```

---

## 9. Similarity Search

### 9.1 Search Flow

```python
# src/rag_engine/retriever.py

def get_relevant_docs(self, query: str, k: int = 10):
    # LangChain wrapper handles:
    # 1. Embed query
    # 2. Call FAISS similarity_search
    # 3. Map results back to Documents
    
    docs = self.vector_store.similarity_search(query, k=k)
    return docs
```

### 9.2 Under the hood

```python
# What LangChain does:
query_vector = embeddings.embed_query(query)
distances, indices = index.search(query_vector, k=10)
# distances: [0.12, 0.15, 0.18, ...]  (L2 distances)
# indices: [42, 156, 789, ...]        (document IDs)
```

---

## 10. Storage

### 10.1 Files Generated

```
data/vector_store/
├── index.faiss              # FAISS binary index (~9MB for 1500 vectors)
├── index.pkl                # LangChain docstore mapping
└── indexing_metadata.json   # File tracking metadata
```

### 10.2 Memory Usage

| Index Type | Memory (1500 vectors, 768D) |
|------------|----------------------------|
| Flat | ~4.6 MB |
| IVF | ~4.8 MB (+ cluster centroids) |
| IVFPQ | ~2.5 MB (compressed) |

---

## 11. Comparison Summary

| Metric | Flat | IVF | IVFPQ |
|--------|------|-----|-------|
| **Accuracy** | 100% | 96%+ | 92%+ |
| **Speed (1500 vec)** | 138ms | 93ms | 85ms |
| **Speed (100K vec)** | 5s+ | 200ms | 100ms |
| **Memory** | Lớn | Trung bình | Nhỏ |
| **Complexity** | Đơn giản | Cần training | Phức tạp |

---

## 12. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **FAISS = Vector similarity search library** từ Facebook AI
> 2. **3 index types**: Flat (exact), IVF (clustering), IVFPQ (compressed)
> 3. **IVF tradeoff**: nprobe cao = accurate hơn nhưng chậm hơn
> 4. **Trong dự án**: IVF64 với nprobe=32 cho 97% recall

---

## Tài liệu liên quan
- [Ingestion Pipeline](./01_ingestion_pipeline.md)
- [Embedding Models](./03_embedding_models.md)
