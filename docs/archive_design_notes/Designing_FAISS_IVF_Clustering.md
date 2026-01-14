# Design Note: FAISS IVF Clustering & Comparison Framework

## Mục tiêu
Triển khai FAISS IVF (Inverted File Index) clustering-based search và xây dựng framework so sánh tốc độ vs độ chính xác giữa brute-force (Flat) và approximate search (IVF).

---

## 1. Bối cảnh: Vấn đề cần giải quyết

### 1.1 Hệ thống hiện tại hoạt động như thế nào?

Khi user hỏi một câu hỏi pháp luật, hệ thống cần tìm các đoạn văn bản liên quan trong database:

```
User Query: "Thủ tục đăng ký kinh doanh"
                    ↓
           [Embedding Model]
                    ↓
         Query Vector (768 chiều)
                    ↓
    ┌───────────────────────────────────┐
    │     FAISS Index (1,787 vectors)   │
    │                                   │
    │  So sánh query với TẤT CẢ 1,787   │
    │  vectors để tìm top-10 gần nhất   │
    │                                   │
    │  Complexity: O(n) = 1,787 phép so │
    └───────────────────────────────────┘
                    ↓
           Top 10 documents
```

**Vấn đề**: Hiện tại dùng **Flat Index** (brute-force) - phải so sánh query với **TẤT CẢ** vectors trong database.

### 1.2 Tại sao cần thay đổi?

| Dataset Size | Flat Index Time | Chấp nhận được? |
|--------------|-----------------|-----------------|
| 1,787 vectors | 112ms | ✅ OK |
| 10,000 vectors | ~650ms | ⚠️ Chậm |
| 100,000 vectors | ~6.5 giây | ❌ Không thể dùng |
| 1,000,000 vectors | ~65 giây | ❌ Thảm họa |

**Kết luận**: Flat Index không scale được. Khi thêm nhiều tài liệu pháp luật, hệ thống sẽ chậm dần.

---

## 2. Giải pháp: IVF (Inverted File Index)

### 2.1 Ý tưởng cốt lõi

**Thay vì tìm trong TẤT CẢ vectors, ta chia thành các NHÓM (clusters) và chỉ tìm trong vài nhóm liên quan.**

```
Ví dụ thực tế:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Flat Index (Hiện tại):
    Bạn muốn tìm sách về "Luật Lao động" trong thư viện 10,000 cuốn.
    → Phải đi qua TỪNG KỆ, xem TỪNG CUỐN SÁCH.
    → Rất chậm!

IVF Index (Đề xuất):
    Thư viện được chia thành 64 KHU VỰC theo chủ đề:
    - Khu 1: Luật Hình sự
    - Khu 2: Luật Dân sự
    - Khu 3: Luật Lao động  ← Chỉ tìm ở đây!
    - Khu 4: Luật Thương mại
    - ...

    → Chỉ cần tìm trong 1-2 khu vực liên quan.
    → Nhanh hơn 5-10 lần!
```

### 2.2 IVF hoạt động như thế nào?

**BƯỚC 1: Training (Chạy 1 lần khi build index)**

```
1,787 document vectors
         ↓
   [K-means Clustering]
         ↓
    Chia thành 64 nhóm (clusters)

    Cluster 0: 28 vectors về Luật Hình sự
    Cluster 1: 32 vectors về Luật Dân sự
    Cluster 2: 25 vectors về Luật Lao động
    ...
    Cluster 63: 30 vectors về Luật Môi trường

    Mỗi cluster có 1 "centroid" (điểm trung tâm)
```

**BƯỚC 2: Search (Mỗi khi user query)**

```
User Query: "Nghỉ thai sản được bao nhiêu ngày?"
                    ↓
         Query Vector (768D)
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ BƯỚC 2a: Tìm clusters gần nhất với query                    │
│                                                             │
│   So sánh query với 64 centroids                            │
│   → Tìm ra 8 clusters gần nhất (nprobe=8)                   │
│   → Clusters: [2, 5, 12, 18, 23, 31, 45, 52]                │
│                                                             │
│   Cluster 2 (Luật Lao động) ← Gần nhất!                     │
│   Cluster 5 (Bảo hiểm XH)   ← Cũng liên quan                │
│   ...                                                       │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ BƯỚC 2b: Tìm trong các clusters đã chọn                     │
│                                                             │
│   Chỉ search trong 8/64 clusters = 12.5% data               │
│   Thay vì 1,787 vectors → chỉ ~220 vectors                  │
│                                                             │
│   → Nhanh hơn 5-8 lần!                                      │
└─────────────────────────────────────────────────────────────┘
                    ↓
            Top 10 documents
```

### 2.3 Trade-off: Tốc độ vs Độ chính xác

**Tham số quan trọng: `nprobe` = số clusters tìm kiếm**

```
nprobe = 1:  Chỉ tìm trong 1 cluster  → Cực nhanh, nhưng có thể bỏ sót
nprobe = 8:  Tìm trong 8 clusters     → Cân bằng tốt
nprobe = 64: Tìm trong TẤT CẢ         → Giống Flat, chính xác 100%
```

| nprobe | % Data Searched | Tốc độ | Recall (Độ chính xác) |
|--------|-----------------|--------|----------------------|
| 1 | 1.5% | ⚡ Cực nhanh | ~70% (bỏ sót 30%) |
| 4 | 6% | ⚡ Rất nhanh | ~92% |
| **8** | **12.5%** | **🔄 Cân bằng** | **~96%** |
| 16 | 25% | 🐢 Vừa phải | ~98% |
| 64 | 100% | 🐌 Như Flat | 100% |

**Khuyến nghị**: `nprobe=8` cho hệ thống này (12.5% data, 96% recall)

---

## 3. Phân tích hiện trạng

| Metric | Giá trị hiện tại |
|--------|------------------|
| Index Type | IndexFlatL2 (exact search) |
| Vectors | ~1,787 embeddings |
| Dimension | 768D (vietnamese-bi-encoder) |
| Index Size | 5.3MB |
| Search Latency | ~112ms (warm) |

---

## 4. Kiến trúc đề xuất

### 4.1 Tổng quan hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                      AppConfig                               │
│                                                             │
│  VECTOR_INDEX_TYPE: flat | ivf | ivfpq                       │
│  ├── "flat"  = Brute-force, chính xác 100%                  │
│  ├── "ivf"   = Clustering, nhanh hơn 5x, ~96% recall        │
│  └── "ivfpq" = Clustering + Compression, tiết kiệm memory   │
│                                                             │
│  IVF_NLIST: 64  ← Số clusters (nhóm)                        │
│  IVF_NPROBE: 8  ← Số clusters tìm kiếm mỗi query            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Đọc config
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│     VectorIndexer       │           │   SemanticRetriever     │
│     (Build time)        │           │   (Query time)          │
│                         │           │                         │
│ Nhiệm vụ:               │           │ Nhiệm vụ:               │
│ 1. Đọc config           │           │ 1. Load index từ disk   │
│ 2. Tạo FAISS index      │           │ 2. Auto-detect loại     │
│ 3. Train IVF clusters   │           │ 3. Set nprobe nếu IVF   │
│ 4. Add vectors          │           │ 4. Thực hiện search     │
│ 5. Save to disk         │           │                         │
└─────────────────────────┘           └─────────────────────────┘
          │                                       │
          │ Tạo index                             │ Load index
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FAISS Index (Switchable)                    │
│                                                             │
│   ┌───────────┐    ┌───────────────┐    ┌───────────────┐   │
│   │   Flat    │    │   IVF,Flat    │    │   IVF,PQ      │   │
│   │           │    │               │    │               │   │
│   │ Brute-    │    │ Clustering    │    │ Clustering +  │   │
│   │ force     │    │ approximate   │    │ Compression   │   │
│   │           │    │               │    │               │   │
│   │ 100%      │    │ ~96% recall   │    │ ~92% recall   │   │
│   │ accuracy  │    │ 5x faster     │    │ 10x faster    │   │
│   │           │    │               │    │ 50% memory    │   │
│   └───────────┘    └───────────────┘    └───────────────┘   │
│        ▲                  ▲                    ▲             │
│        │                  │                    │             │
│   Hiện tại           Đề xuất             Tương lai           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Giải thích từng thành phần

#### **AppConfig** - Trung tâm cấu hình

```python
# Người dùng chỉ cần thay đổi file .env để switch giữa các loại index

VECTOR_INDEX_TYPE=flat   # Giữ nguyên như cũ (an toàn)
# hoặc
VECTOR_INDEX_TYPE=ivf    # Bật IVF clustering (nhanh hơn)
```

**Tại sao đặt ở Config?**
- Dễ dàng switch giữa các mode mà không cần sửa code
- Có thể test cả 2 mode để so sánh
- Backward compatible: default là `flat`

#### **VectorIndexer** - Xây dựng Index

```
Khi chạy: python ingest.py

1. Đọc config VECTOR_INDEX_TYPE
2. Nếu "ivf":
   a. Tạo empty IVF index với 64 clusters
   b. TRAIN: Học vị trí 64 centroids từ data
   c. ADD: Thêm tất cả vectors vào clusters
3. Nếu "flat":
   a. Tạo Flat index (như hiện tại)
4. Save index to disk
```

#### **SemanticRetriever** - Thực hiện Search

```
Khi user query:

1. Load index từ disk
2. Auto-detect loại index:
   - Nếu có thuộc tính `nprobe` → là IVF index
   - Set nprobe = 8 (từ config)
3. Thực hiện similarity_search()
   - IVF: Chỉ search trong 8 clusters
   - Flat: Search tất cả
4. Trả về top-k documents
```

### 4.3 Flow Diagram chi tiết

```
                        BUILD TIME (ingest.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PDF/DOCX Files
      ↓
[Document Loader] → Load văn bản
      ↓
[Text Splitter] → Chia thành chunks (1000 chars)
      ↓
[Embedding Model] → Chuyển text → vectors (768D)
      ↓
┌─────────────────────────────────────────┐
│ VectorIndexer._create_faiss_index()     │
│                                         │
│   if VECTOR_INDEX_TYPE == "ivf":        │
│       index = IVF64,Flat                │
│       index.train(vectors)  ← Học       │
│       index.add(vectors)                │
│   else:                                 │
│       index = Flat (như cũ)             │
│       index.add(vectors)                │
└─────────────────────────────────────────┘
      ↓
[Save] → data/vector_store/index.faiss


                        QUERY TIME (app.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: "Nghỉ thai sản được bao nhiêu ngày?"
      ↓
[Embedding Model] → Query vector (768D)
      ↓
┌─────────────────────────────────────────┐
│ SemanticRetriever                       │
│                                         │
│   index = load("index.faiss")           │
│                                         │
│   if is_ivf(index):                     │
│       index.nprobe = 8  ← Set tham số   │
│                                         │
│   results = index.search(query, k=10)   │
│   ├── IVF: Search 8/64 clusters (~220   │
│   │         vectors) → ~20ms            │
│   └── Flat: Search all 1787 vectors     │
│             → ~112ms                    │
└─────────────────────────────────────────┘
      ↓
Top 10 Documents → RAG Chain → Answer
```

---

## 5. Benchmarking Framework: So sánh Flat vs IVF

### 5.1 Tại sao cần Benchmark?

Khi dùng IVF, ta đánh đổi **độ chính xác** để có **tốc độ**. Cần đo lường cụ thể:

1. **Nhanh hơn bao nhiêu?** (Latency)
2. **Bỏ sót bao nhiêu kết quả?** (Recall)

### 5.2 Cách đo Recall@K

```
Recall@K = Số kết quả đúng trong top-K của IVF
           ─────────────────────────────────────
           Số kết quả trong top-K của Flat (ground truth)

Ví dụ:
  Query: "Nghỉ thai sản"

  Flat (Ground Truth) Top-5:  [Doc_A, Doc_B, Doc_C, Doc_D, Doc_E]
  IVF  (Approximate)  Top-5:  [Doc_A, Doc_B, Doc_C, Doc_F, Doc_G]

  Trùng nhau: Doc_A, Doc_B, Doc_C = 3 docs
  Recall@5 = 3/5 = 60%

  (Doc_D, Doc_E bị bỏ sót vì nằm ở cluster khác không được search)
```

### 5.3 Output mong muốn

```
╔════════════════════════════════════════════════════════════╗
║           FAISS Index Comparison Report                     ║
╠════════════════╦══════════════╦════════════╦═══════════════╣
║ Index Type     ║ Latency (ms) ║ Recall@10  ║ Speedup       ║
╠════════════════╬══════════════╬════════════╬═══════════════╣
║ Flat (baseline)║ 112          ║ 100%       ║ 1.0x          ║
║ IVF nprobe=4   ║ 18           ║ 92%        ║ 6.2x          ║
║ IVF nprobe=8   ║ 25           ║ 96%        ║ 4.5x          ║
║ IVF nprobe=16  ║ 40           ║ 98%        ║ 2.8x          ║
╚════════════════╩══════════════╩════════════╩═══════════════╝

Kết luận: nprobe=8 là lựa chọn tối ưu cho hệ thống này.
- Speedup 4.5x (từ 112ms → 25ms)
- Chỉ mất 4% recall (96% vs 100%)
```

---

## 6. Kế hoạch triển khai

### Phase 1: Configuration Foundation
**Files:** `src/config.py`

Thêm cấu hình FAISS index:
```python
# Vector Search Configuration
VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "flat")  # flat, ivf, ivfpq
IVF_NLIST = int(os.getenv("IVF_NLIST", "64"))   # Số clusters
IVF_NPROBE = int(os.getenv("IVF_NPROBE", "8"))  # Clusters tìm kiếm

@classmethod
def get_index_factory_string(cls) -> str:
    if cls.VECTOR_INDEX_TYPE == "flat":
        return "Flat"
    elif cls.VECTOR_INDEX_TYPE == "ivf":
        return f"IVF{cls.IVF_NLIST},Flat"
    elif cls.VECTOR_INDEX_TYPE == "ivfpq":
        return f"IVF{cls.IVF_NLIST},PQ48x8"
```

### Phase 2: Retriever Enhancement
**Files:** `src/rag_engine/retriever.py`

Thêm auto-detection và cấu hình nprobe:
```python
def _configure_search_params(self):
    """Configure search parameters based on index type."""
    index = self.vector_store.index

    if hasattr(index, 'nprobe'):  # IVF index detected
        index.nprobe = AppConfig.IVF_NPROBE
        logger.info(f"IVF Index: nlist={index.nlist}, nprobe={index.nprobe}")
    else:
        logger.info(f"Flat index detected: {type(index).__name__}")
```

### Phase 3: Indexer IVF Support
**Files:** `src/ingestion/indexer.py`

Thay thế `FAISS.from_documents()` bằng custom index creation:
```python
def _create_faiss_index(self, docs, embeddings, chunk_ids):
    # 1. Generate embeddings matrix
    texts = [doc.page_content for doc in docs]
    emb_matrix = np.array(embeddings.embed_documents(texts)).astype('float32')

    # 2. Create index with factory
    factory = AppConfig.get_index_factory_string()
    index = faiss.index_factory(768, factory, faiss.METRIC_L2)

    # 3. Train IVF (CRITICAL - required before adding vectors)
    if hasattr(index, 'train'):
        index.train(emb_matrix)

    # 4. Add vectors
    index.add(emb_matrix)

    # 5. Wrap with LangChain FAISS
    return FAISS(embedding_function=..., index=index, docstore=..., ...)
```

### Phase 4: Benchmarking Framework
**Files:** `tests/benchmark_comparison.py` (NEW)

#### 4.1 Accuracy Benchmark (Recall@K)
```python
def calculate_recall_at_k(ground_truth_ids, search_result_ids, k=10):
    """So sánh kết quả IVF với Flat (ground truth)"""
    gt_set = set(ground_truth_ids[:k])
    sr_set = set(search_result_ids[:k])
    return len(gt_set & sr_set) / len(gt_set)
```

#### 4.2 Speed vs Accuracy Matrix
```python
def run_comparison_benchmark():
    configs = [
        {"type": "flat", "name": "Flat (Baseline)"},
        {"type": "ivf", "nprobe": 4, "name": "IVF nprobe=4"},
        {"type": "ivf", "nprobe": 8, "name": "IVF nprobe=8"},
        {"type": "ivf", "nprobe": 16, "name": "IVF nprobe=16"},
    ]

    for config in configs:
        latency = measure_latency(config)
        recall = measure_recall(config, ground_truth)
        print(f"{config['name']}: {latency}ms, Recall@10={recall}%")
```

#### 4.3 Output Format
```
╔════════════════════════════════════════════════════════════╗
║           FAISS Index Comparison Report                     ║
╠════════════════╦══════════════╦════════════╦═══════════════╣
║ Index Type     ║ Latency (ms) ║ Recall@10  ║ Speedup       ║
╠════════════════╬══════════════╬════════════╬═══════════════╣
║ Flat (baseline)║ 112          ║ 100%       ║ 1.0x          ║
║ IVF nprobe=4   ║ 18           ║ 92%        ║ 6.2x          ║
║ IVF nprobe=8   ║ 25           ║ 96%        ║ 4.5x          ║
║ IVF nprobe=16  ║ 40           ║ 98%        ║ 2.8x          ║
╚════════════════╩══════════════╩════════════╩═══════════════╝
```

## 7. Files cần sửa đổi

| File | Action | Mô tả |
|------|--------|-------|
| `src/config.py` | MODIFY | Thêm VECTOR_INDEX_TYPE, IVF_NLIST, IVF_NPROBE, get_index_factory_string() |
| `src/rag_engine/retriever.py` | MODIFY | Thêm _configure_search_params() để auto-detect và set nprobe |
| `src/ingestion/indexer.py` | MODIFY | Thay _create_faiss_index() với factory pattern + IVF training |
| `tests/benchmark_comparison.py` | CREATE | Framework so sánh tốc độ vs độ chính xác |
| `.env.example` | MODIFY | Thêm cấu hình FAISS index |
| `DEV_LOG.md` | UPDATE | Document ADR |

## 8. Dự kiến hiệu năng

| Index | Vectors | Latency | Recall@10 | Speedup |
|-------|---------|---------|-----------|---------|
| Flat | 1.7K | 112ms | 100% | 1.0x |
| IVF64 nprobe=8 | 1.7K | ~20ms | ~96% | 5.6x |
| IVF64 nprobe=16 | 1.7K | ~35ms | ~98% | 3.2x |

**Scaling (10K vectors):**
| Flat: ~650ms | IVF: ~40ms | Speedup: 16x |

## 9. Verification Plan

1. **Unit Tests:**
   - `test_config_factory_string()` - Verify factory string generation
   - `test_ivf_index_creation()` - Create small IVF index
   - `test_index_type_detection()` - Load flat/IVF, check detection

2. **Integration Test:**
   ```bash
   # Build IVF index
   VECTOR_INDEX_TYPE=ivf python ingest.py

   # Run comparison benchmark
   python -m tests.benchmark_comparison
   ```

3. **Manual Verification:**
   - Compare top-10 results của cùng query trên Flat vs IVF
   - Kiểm tra recall đạt >95% với nprobe=8

## 10. Backward Compatibility

- Default: `VECTOR_INDEX_TYPE=flat` (giữ nguyên behavior)
- Retriever auto-detect index type khi load
- Không breaking change cho existing users
- Rollback: Đổi `.env` về `flat` và chạy `ingest.py`

## 11. Recommended Default Settings

```bash
# .env (cho production)
VECTOR_INDEX_TYPE=ivf
IVF_NLIST=64
IVF_NPROBE=8
```

Với dataset hiện tại (1.7K vectors), IVF sẽ cho speedup ~5x với recall ~96%.

## 12. Technical Deep-Dive: IVF Algorithm

### Cách IVF hoạt động:

```
Training Phase:
  1. Chạy K-means trên toàn bộ vectors → tạo 64 centroids (clusters)
  2. Mỗi vector được assign vào cluster gần nhất

Search Phase:
  1. Query vector → tìm 8 clusters gần nhất (nprobe=8)
  2. Chỉ search trong 8 clusters đó (8/64 = 12.5% data)
  3. Trả về top-k từ kết quả
```

### Trade-off nprobe:

| nprobe | Search Scope | Speed | Recall |
|--------|--------------|-------|--------|
| 1 | 1.5% data | Fastest | ~70% |
| 4 | 6% data | Very Fast | ~92% |
| 8 | 12.5% data | Fast | ~96% |
| 16 | 25% data | Moderate | ~98% |
| 64 | 100% data | Same as Flat | 100% |

## 13. Potential Challenges & Mitigations

1. **IVF cần training trước khi add vectors**
   - Mitigation: Implement training step trong indexer

2. **Incremental indexing với IVF**
   - Option A: Retrain on every sync (chính xác nhưng chậm)
   - Option B: Add without retrain (nhanh, có thể giảm quality)
   - Recommendation: Option B cho incremental, full retrain khi rebuild

3. **LangChain FAISS wrapper không expose IVF params**
   - Mitigation: Access `vector_store.index` trực tiếp, cast to `faiss.IndexIVF`
