# 🧮 Embedding Models - Chuyển Text thành Vector

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- Embedding là gì và hoạt động như thế nào
- Tại sao cần model embedding cho tiếng Việt
- vietnamese-bi-encoder và các đặc điểm

---

## 1. Embedding là gì?

### 1.1 Định nghĩa
**Text Embedding** là quá trình chuyển đổi văn bản thành vector số học trong không gian nhiều chiều.

```
Input Text: "Thai sản được nghỉ bao nhiêu ngày?"
     │
     ▼ Embedding Model
     │
Output Vector: [0.12, -0.34, 0.56, ..., 0.78]
               ↑
               768 dimensions
```

### 1.2 Tại sao cần Embedding?

| Vấn đề | Giải pháp |
|--------|-----------|
| Machine không hiểu text | Chuyển text → số |
| So sánh semantic similarity | Vectors gần nhau = ý nghĩa giống nhau |
| Efficient search | Vector search nhanh hơn text search |

### 1.3 Semantic Similarity

```
Vector Space Visualization (simplified 2D):

                    ↑
        "nghỉ thai sản"  • "maternity leave"
                         •
                    ─────●───────────────────────→
                         •
        "nghỉ hè"    •   "summer vacation"
                         
Vectors gần nhau có nghĩa tương tự!
```

---

## 2. Embedding Model Types

### 2.1 Single Encoder (BERT-based)
```
Query:    "thai sản" ──► Encoder ──► Vector_Q
Document: "nghỉ đẻ"  ──► Encoder ──► Vector_D
                              ↓
                    cosine_sim(Vector_Q, Vector_D) = 0.87
```
**Nhược điểm**: Chậm khi cần encode cả query và documents realtime

### 2.2 Bi-Encoder (Sentence Transformers)
```
Offline: Encode tất cả documents ──► Store vectors in FAISS
Online:  Encode query only      ──► Search against stored vectors
```
**Ưu điểm**: Nhanh - chỉ encode query khi search

### 2.3 Cross-Encoder
```
Query + Document ──► [CLS] query [SEP] document [SEP] ──► Score
```
**Ưu điểm**: Accurate nhất
**Nhược điểm**: Chậm - phải encode mỗi cặp (query, doc)

**Trong dự án chúng ta dùng**: ✅ **Bi-Encoder**

---

## 3. vietnamese-bi-encoder

### 3.1 Model Info

| Attribute | Value |
|-----------|-------|
| **Name** | `bkai-foundation-models/vietnamese-bi-encoder` |
| **Type** | Bi-Encoder (Sentence Transformer) |
| **Dimensions** | 768 |
| **Language** | Vietnamese optimized |
| **Base Model** | XLM-RoBERTa |
| **Source** | HuggingFace |

### 3.2 Tại sao chọn model này?

| Reason | Explanation |
|--------|-------------|
| **Vietnamese specialized** | Trained trên Vietnamese data |
| **Bi-Encoder** | Fast retrieval - encode 1 lần, search nhiều lần |
| **768D** | Industry standard, compatible với FAISS |
| **Open source** | Miễn phí, chạy local |
| **BKAI** | Nguồn uy tín - VN AI lab |

### 3.3 Comparison với alternatives

| Model | Lang | Dims | Speed | VN Quality |
|-------|------|------|-------|------------|
| **vietnamese-bi-encoder** | VI | 768 | Fast | ⭐⭐⭐⭐⭐ |
| multilingual-e5-base | Multi | 768 | Fast | ⭐⭐⭐ |
| sentence-transformers | EN | 768 | Fast | ⭐⭐ |
| OpenAI text-embedding-3 | Multi | 3072 | API | ⭐⭐⭐⭐ |

---

## 4. Cách sử dụng trong dự án

### 4.1 Initialization

```python
# src/ingestion/indexer.py & src/rag_engine/retriever.py

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="bkai-foundation-models/vietnamese-bi-encoder",
    model_kwargs={'device': 'cpu'},  # hoặc 'cuda' nếu có GPU
    encode_kwargs={'normalize_embeddings': True}
)
```

### 4.2 Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `model_name` | string | HuggingFace model path |
| `device` | 'cpu' | Chạy trên CPU (production) |
| `normalize_embeddings` | True | L2 normalize → cosine similarity |

### 4.3 Encoding Text

```python
# Single text
vector = embeddings.embed_query("thai sản được nghỉ mấy tháng?")
# Returns: List[float] with 768 values

# Batch texts (for indexing)
texts = ["text1", "text2", "text3"]
vectors = embeddings.embed_documents(texts)
# Returns: List[List[float]] - 3 vectors, each 768 dims
```

---

## 5. Embedding Process in RAG

### 5.1 Indexing Phase (Offline)

```
┌─────────────────┐
│   1500 Chunks   │
│  (text strings) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ embed_documents │
│   (batch mode)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  1500 Vectors   │
│ (768D each)     │
│  ~9MB in FAISS  │
└─────────────────┘
```

### 5.2 Query Phase (Online)

```
User Query: "Thai sản được nghỉ bao nhiêu ngày?"
                    │
                    ▼
            ┌───────────────┐
            │  embed_query  │
            │  (~80-100ms)  │
            └───────┬───────┘
                    │
                    ▼
            [0.12, -0.34, ..., 0.78]  (768D vector)
                    │
                    ▼
            ┌───────────────┐
            │ FAISS Search  │  ← cosine similarity
            │  (~10-20ms)   │
            └───────┬───────┘
                    │
                    ▼
            Top 10 similar chunks
```

---

## 6. Performance Benchmarks

### 6.1 Trong dự án

| Metric | Value |
|--------|-------|
| Cold start (first load) | ~15-17s |
| Query embedding | ~80-100ms |
| Batch embedding (1000 texts) | ~8-10s |
| Memory usage | ~1.5GB |

### 6.2 Tối ưu Cold Start

```python
# app.py uses @st.cache_resource to cache model
@st.cache_resource(show_spinner="Đang khởi động Model & Index...")
def get_retriever():
    return SemanticRetriever()  # Loads embedding model once
```

**Kết quả**: 
- First load: ~17s
- Subsequent loads: <1s (cached)

---

## 7. Vector Normalization

### 7.1 Tại sao normalize?

```python
encode_kwargs={'normalize_embeddings': True}
```

**L2 Normalization**: Vector → unit vector (length = 1)

```
Original:   [3, 4]        → length = 5
Normalized: [0.6, 0.8]    → length = 1
```

### 7.2 Lợi ích

| Benefit | Explanation |
|---------|-------------|
| Cosine = Dot Product | Tính toán nhanh hơn |
| Fair comparison | Vectors cùng scale |
| FAISS optimization | Sử dụng IndexFlatIP thay vì IndexFlatL2 |

---

## 8. Common Issues

### 8.1 Out of Memory
```python
# Vấn đề: Encode quá nhiều texts cùng lúc
# Giải pháp: Batch processing
batch_size = 100
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    vectors = embeddings.embed_documents(batch)
```

### 8.2 Slow First Query
```python
# Vấn đề: Model loading chậm
# Giải pháp: Pre-load khi app starts
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(...)
```

### 8.3 Language Mismatch
```python
# Vấn đề: Dùng English model cho Vietnamese text
# Giải pháp: Dùng vietnamese-bi-encoder
# DON'T: "sentence-transformers/all-MiniLM-L6-v2"
# DO:    "bkai-foundation-models/vietnamese-bi-encoder"
```

---

## 9. Embedding Dimension Trade-offs

| Dimensions | Storage | Search Speed | Quality |
|------------|---------|--------------|---------|
| 384 | Nhỏ | Nhanh | Lower |
| **768** | Trung bình | Cân bằng | Good |
| 1024+ | Lớn | Chậm hơn | Higher |

**Trong dự án**: 768D là sweet spot

---

## 10. Code trong dự án

### 10.1 Indexer (Ingestion)
```python
# src/ingestion/indexer.py
class VectorIndexer:
    @staticmethod
    def _get_embeddings():
        logger.info(f"Loading embedding model: {AppConfig.EMBEDDING_MODEL_NAME}")
        return HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
```

### 10.2 Retriever (Query Time)
```python
# src/rag_engine/retriever.py
class SemanticRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=AppConfig.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = self._load_vector_store()
```

---

## 11. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **Embedding = Text → Vector** để so sánh semantic similarity
> 2. **Bi-Encoder**: Fast - encode documents offline, chỉ encode query online
> 3. **vietnamese-bi-encoder**: Optimized cho tiếng Việt
> 4. **768 dimensions**: Industry standard, balanced quality/speed

---

## Tài liệu liên quan
- [Text Chunking](./02_text_chunking.md)
- [FAISS Vector Search](./04_faiss_vector_search.md)
