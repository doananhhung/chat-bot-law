# 🔎 Semantic Retrieval - Tìm Kiếm Ngữ Nghĩa

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- Semantic search khác keyword search như thế nào
- Cách SemanticRetriever hoạt động
- Top-K retrieval và relevance scoring

---

## 1. Keyword Search vs Semantic Search

### 1.1 So sánh

| Aspect | Keyword Search | Semantic Search |
|--------|----------------|-----------------|
| **Matching** | Exact words | Meaning/concept |
| **Query** | "nghỉ thai sản" | "được nghỉ bao lâu khi sinh con?" |
| **Miss** | "nghỉ đẻ", "maternity leave" | ❌ |
| **Catch** | ✅ All related concepts | ✅ |

### 1.2 Ví dụ minh họa

```
User Query: "nghỉ đẻ được mấy tháng"

Keyword Search (TF-IDF, BM25):
❌ Không match "thai sản"
❌ Không match "sinh con"
❌ Miss relevant documents

Semantic Search (Embedding):
✅ Match "nghỉ thai sản"
✅ Match "lao động nữ được nghỉ khi sinh con"
✅ Match "maternity leave"
→ Understands MEANING, not just words
```

---

## 2. Semantic Search Process

### 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                   SEMANTIC RETRIEVAL                     │
│                                                         │
│   Query: "nghỉ đẻ mấy tháng?"                          │
│          │                                              │
│          ▼                                              │
│   ┌─────────────┐                                       │
│   │  Embedding  │  ← vietnamese-bi-encoder              │
│   │   Model     │                                       │
│   └──────┬──────┘                                       │
│          │                                              │
│          ▼                                              │
│   Query Vector: [0.12, -0.34, ..., 0.78]               │
│          │                                              │
│          ▼                                              │
│   ┌─────────────┐                                       │
│   │   FAISS     │  ← Similarity search                  │
│   │   Index     │                                       │
│   └──────┬──────┘                                       │
│          │                                              │
│          ▼                                              │
│   Top-K Documents (by similarity score)                 │
│   • Điều 139: Nghỉ thai sản... (score: 0.92)           │
│   • Điều 140: Chế độ khi mang thai... (score: 0.85)    │
│   • ...                                                 │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Step by Step

1. **Embed Query**: Chuyển câu hỏi → vector 768D
2. **Search FAISS**: Tìm K vectors gần nhất
3. **Map to Documents**: Convert vector IDs → Document objects
4. **Return Results**: Trả về top-K documents với metadata

---

## 3. SemanticRetriever Class

### 3.1 Initialization

```python
# src/rag_engine/retriever.py

class SemanticRetriever:
    def __init__(self):
        # 1. Load embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 2. Load FAISS vector store
        self.vector_store = self._load_vector_store()
        
        # 3. Configure search parameters (IVF nprobe)
        self._configure_search_params()
```

### 3.2 Load Vector Store

```python
def _load_vector_store(self):
    try:
        return FAISS.load_local(
            AppConfig.VECTOR_DB_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True
            # Safe because we created the index ourselves
        )
    except Exception as e:
        raise RuntimeError("Vector Store not found. Please run ingestion first.")
```

### 3.3 Get Relevant Documents

```python
def get_relevant_docs(self, query: str, k: int = 10) -> List[Document]:
    """
    Retrieve top k relevant documents for the query.
    """
    if not self.vector_store:
        return []

    logger.info(f"Searching for: '{query}'")
    docs = self.vector_store.similarity_search(query, k=k)
    logger.info(f"Found {len(docs)} relevant documents.")
    return docs
```

---

## 4. Top-K Retrieval

### 4.1 Tại sao Top-K?

| Vấn đề | Giải pháp |
|--------|-----------|
| LLM context limit | Không thể đưa tất cả documents |
| Noise reduction | Chỉ lấy most relevant |
| Cost optimization | Ít tokens = rẻ hơn |

### 4.2 Chọn K như thế nào?

| K Value | Trade-off |
|---------|-----------|
| K = 3 | Risk missing relevant info |
| **K = 10** | ✅ Balanced (dùng trong dự án) |
| K = 20 | Risk including noise |

### 4.3 Trong dự án

```python
# Default K = 10
docs = self.retriever.get_relevant_docs(query, k=10)
```

---

## 5. Similarity Metrics

### 5.1 L2 Distance (Euclidean)

```
distance = sqrt(Σ(a_i - b_i)²)

Smaller distance = More similar
```

### 5.2 Cosine Similarity

```
similarity = (A · B) / (||A|| × ||B||)

Range: [-1, 1]
1 = Identical direction
0 = Orthogonal
-1 = Opposite direction
```

### 5.3 Trong dự án

```python
# FAISS uses L2 distance
index = faiss.index_factory(768, "IVF64,Flat", faiss.METRIC_L2)

# But vectors are normalized, so:
# L2² = 2 - 2×cosine_similarity
# → Effectively equivalent to cosine similarity
```

---

## 6. Search Mode Configuration

### 6.1 Available Modes

```python
def set_search_mode(self, mode: str):
    mode_config = {
        "quality": ivf_index.nlist,  # Search all 64 clusters
        "balanced": 8,               # Search 8/64 = 12.5%
        "speed": 2,                  # Search 2/64 = 3%
    }
    ivf_index.nprobe = mode_config[mode]
```

### 6.2 Mode Comparison

| Mode | nprobe | Recall | Speed | Use Case |
|------|--------|--------|-------|----------|
| quality | 64 | ~100% | Slowest | Critical accuracy |
| **balanced** | 8 | ~73% | Balanced | Daily use |
| speed | 2 | ~33% | Fastest | Quick queries |

### 6.3 Get Current Mode

```python
def get_current_search_mode(self) -> dict:
    return {
        "mode": mode,
        "nprobe": nprobe,
        "nlist": nlist,
        "is_ivf": True,
        "search_scope_pct": (nprobe / nlist) * 100
    }
```

---

## 7. Document Output Format

### 7.1 Document Object

```python
Document(
    page_content="Điều 139. Nghỉ thai sản\n1. Lao động nữ được nghỉ...",
    metadata={
        "source": "luat_lao_dong.pdf",
        "page": 45,
        "chunk_id": "abc123_0",
        "chunk_index": 0,
        "total_chunks": 150
    }
)
```

### 7.2 Usage in RAG

```python
# generator.py
docs = self.retriever.get_relevant_docs(query)

# Format for LLM
context_str = format_context(docs)
# → "--- Tài liệu 1 ---\nNguồn: luat_lao_dong.pdf | Trang: 46\n..."

# Send to LLM
answer = llm.invoke({
    "context": context_str,
    "question": query
})
```

---

## 8. Performance Considerations

### 8.1 Latency Breakdown

| Step | Time |
|------|------|
| Embed query | ~80-100ms |
| FAISS search | ~10-30ms |
| Document mapping | ~5ms |
| **Total** | **~100-150ms** |

### 8.2 Caching

```python
# app.py uses Streamlit caching
@st.cache_resource
def get_retriever():
    return SemanticRetriever()

# Model loaded once, reused for all queries
```

### 8.3 Bottleneck Analysis

```
Cold start: ~17s  ← Embedding model loading (one-time)
Warm query: ~100ms ← Actual search (fast)
```

---

## 9. Edge Cases

### 9.1 No Results Found

```python
if not docs:
    return "Tôi không tìm thấy tài liệu pháp lý nào liên quan..."
```

### 9.2 Vector Store Not Ready

```python
try:
    retriever = SemanticRetriever()
except RuntimeError:
    st.error("Vector Store not found. Please run ingestion first.")
```

### 9.3 Low Similarity Scores

Trong dự án hiện tại, không filter theo similarity threshold.
Có thể cải tiến:

```python
# Potential improvement
docs = vector_store.similarity_search_with_score(query, k=10)
filtered = [doc for doc, score in docs if score < 0.5]  # L2 distance
```

---

## 10. Code Flow Summary

```python
# Complete retrieval flow

# 1. User enters query
query = "Thai sản được nghỉ bao nhiêu ngày?"

# 2. Get retriever (cached)
retriever = get_retriever()

# 3. Set search mode (optional)
retriever.set_search_mode("balanced")

# 4. Retrieve documents
docs = retriever.get_relevant_docs(query, k=10)

# 5. Documents ready for RAG
# Each doc has:
# - page_content: text chunk
# - metadata: source, page, chunk_id
```

---

## 11. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **Semantic search**: Hiểu ý nghĩa, không chỉ keyword
> 2. **Top-K = 10**: Balanced recall và precision
> 3. **Search modes**: quality/balanced/speed - trade-off accuracy vs speed
> 4. **~100ms latency**: Fast enough for realtime chat

---

## Tài liệu liên quan
- [Intent Routing](./02_intent_routing.md)
- [Prompt Engineering](./03_prompt_engineering.md)
