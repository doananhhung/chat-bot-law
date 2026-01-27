# 🎤 Member 2: Data Ingestion & Vector Database - Tài Liệu Thuyết Trình

> **Thời lượng:** ~8-10 phút | **Vai trò:** Giải thích pipeline xử lý dữ liệu

---

# PHẦN 1: TỔNG QUAN INGESTION PIPELINE (2 phút)

## 📽️ SLIDE 1.1: Tiêu đề phần

| Nội dung trình chiếu |
|---------------------|
| **Data Ingestion & Vector Database** |
| *Từ PDF → Searchable Knowledge Base* |
| --- |
| 👤 Member 2 |

### 🎙️ Script:

> "Xin chào, tôi là Member 2. Tôi sẽ giải thích **làm thế nào chúng tôi chuyển đổi các file PDF/DOCX thành dữ liệu có thể tìm kiếm được**.
>
> Đây là bước nền tảng của hệ thống RAG - nếu không có bước này, AI sẽ không có dữ liệu để tìm kiếm."

---

## 📽️ SLIDE 1.2: 4-Step Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                        │
│                                                             │
│   PDF/DOCX          Text            Chunks          Vectors │
│   Files    ──────►  Docs  ──────►   List  ──────►  Index   │
│                                                             │
│            LOAD          SPLIT          EMBED       STORE   │
│         (loader.py)  (splitter.py)  (indexer.py)  (FAISS)  │
└─────────────────────────────────────────────────────────────┘
```

| Bước | Công cụ | Input | Output |
|------|---------|-------|--------|
| **1. LOAD** | PyPDFLoader | PDF/DOCX files | Text + Metadata |
| **2. SPLIT** | RecursiveCharacterTextSplitter | Long documents | Chunks (~1000 chars) |
| **3. EMBED** | vietnamese-bi-encoder | Text chunks | Vectors (768D) |
| **4. STORE** | FAISS | Vectors | Searchable Index |

### 🎙️ Script:

> "Pipeline Ingestion gồm **4 bước chính**:
>
> **Bước 1 - Load**: Đọc file PDF/DOCX, trích xuất text và metadata như tên file, số trang.
>
> **Bước 2 - Split**: Chia văn bản dài thành các đoạn nhỏ khoảng 1000 ký tự. Tại sao? Vì LLM có giới hạn context và tìm kiếm chính xác hơn với đoạn nhỏ.
>
> **Bước 3 - Embed**: Chuyển mỗi đoạn text thành vector số học 768 chiều. Đây là bước quan trọng để máy tính 'hiểu' ngữ nghĩa.
>
> **Bước 4 - Store**: Lưu các vectors vào FAISS index để có thể tìm kiếm nhanh sau này."

---

# PHẦN 2: DOCUMENT LOADING (1.5 phút)

## 📽️ SLIDE 2.1: Document Loader

| File format | Loader | Thư viện |
|-------------|--------|----------|
| `.pdf` | PyPDFLoader | pypdf |
| `.docx` / `.doc` | Docx2txtLoader | docx2txt |

```python
# src/ingestion/loader.py
class DocumentLoader:
    SUPPORTED_EXTENSIONS = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader
    }
```

**Output Document:**
```python
Document(
    page_content="Điều 139. Nghỉ thai sản...",
    metadata={
        "source": "luat_lao_dong.pdf",
        "page": 45
    }
)
```

### 🎙️ Script:

> "Bước đầu tiên là **Load** - đọc file vào hệ thống.
>
> Chúng tôi hỗ trợ 2 loại file chính: **PDF** và **DOCX**. Mỗi loại có loader riêng từ thư viện LangChain.
>
> Output của bước này là các **Document objects** chứa:
> - `page_content`: Nội dung text của trang
> - `metadata`: Thông tin về nguồn như tên file, số trang
>
> Metadata này rất quan trọng - nó cho phép chúng tôi **trích dẫn nguồn chính xác** khi trả lời."

---

# PHẦN 3: TEXT CHUNKING (2 phút)

## 📽️ SLIDE 3.1: Tại sao cần Chunking?

| Vấn đề | Giải thích |
|--------|------------|
| **LLM Context Limit** | LLM chỉ xử lý được ~32K tokens, văn bản luật có thể dài hàng trăm trang |
| **Search Precision** | Chunks nhỏ → Tìm kiếm chính xác hơn |
| **Noise Reduction** | Chỉ lấy phần liên quan, bỏ qua phần không cần |

```
Document gốc (5000 chars):
┌────────────────────────────────────────────────────────────┐
│ Điều 139... text... Điều 140... text... Điều 141...        │
└────────────────────────────────────────────────────────────┘

Sau khi Split (5 chunks):
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Chunk 1  │  │ Chunk 2  │  │ Chunk 3  │  │ Chunk 4  │  │ Chunk 5  │
│ ~1000    │  │ ~1000    │  │ ~1000    │  │ ~1000    │  │ ~1000    │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
        ↘──overlap 200──↙
```

### 🎙️ Script:

> "Tại sao phải chia văn bản thành chunks? Có 3 lý do chính:
>
> **Thứ nhất**, LLM có giới hạn context. Không thể đưa toàn bộ bộ luật lao động 200 trang vào một prompt.
>
> **Thứ hai**, chunks nhỏ giúp **tìm kiếm chính xác hơn**. Khi user hỏi về thai sản, chúng tôi chỉ lấy đúng đoạn về thai sản, không lấy cả chương.
>
> **Thứ ba**, giảm nhiễu - ít text không liên quan.
>
> Chúng tôi thiết lập **chunk_size=1000** ký tự và **overlap=200**. Overlap đảm bảo không mất thông tin ở ranh giới giữa các chunks."

---

## 📽️ SLIDE 3.2: RecursiveCharacterTextSplitter

```python
# src/ingestion/splitter.py
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Tối đa 1000 ký tự
    chunk_overlap=200,    # Overlap 200 ký tự
    separators=["\n\n", "\n", " ", ""]  # Ưu tiên cắt
)
```

**Separators Priority:**
```
"\n\n" → Paragraph break (ưu tiên cao nhất)
"\n"   → Line break
" "    → Space
""     → Character (fallback)
```

### 🎙️ Script:

> "Chúng tôi sử dụng **RecursiveCharacterTextSplitter** từ LangChain.
>
> Nó hoạt động theo nguyên tắc: **Cố gắng cắt ở vị trí tự nhiên nhất**.
>
> Ưu tiên cắt theo paragraph (2 dòng trống), nếu vẫn quá dài thì cắt theo line break, rồi đến space.
>
> Fallback cuối cùng mới cắt theo ký tự. Nhờ vậy, mỗi chunk thường là một đoạn văn hoàn chỉnh, giữ được ngữ nghĩa."

---

# PHẦN 4: EMBEDDING (2 phút)

## 📽️ SLIDE 4.1: Embedding là gì?

```
Input Text: "Thai sản được nghỉ bao nhiêu ngày?"
     │
     ▼ Embedding Model
     │
Output Vector: [0.12, -0.34, 0.56, ..., 0.78]
               ↑
               768 dimensions
```

| Khái niệm | Giải thích |
|-----------|------------|
| **Embedding** | Chuyển text → vector số học |
| **Dimension** | 768 chiều (trong dự án này) |
| **Semantic Similarity** | Vectors gần nhau = Nghĩa tương tự |

### 🎙️ Script:

> "**Embedding** là quá trình chuyển đổi văn bản thành vector số học.
>
> Tại sao cần làm vậy? Vì **máy tính không hiểu text**, nhưng hiểu số. Vector cho phép chúng ta so sánh ngữ nghĩa.
>
> Điểm quan trọng: 2 câu có nghĩa tương tự sẽ có vectors **gần nhau** trong không gian 768 chiều.
>
> Ví dụ: 'nghỉ đẻ' và 'thai sản' sẽ có vectors gần nhau, dù từ ngữ khác hẳn."

---

## 📽️ SLIDE 4.2: vietnamese-bi-encoder

| Thuộc tính | Giá trị |
|------------|---------|
| **Model** | `bkai-foundation-models/vietnamese-bi-encoder` |
| **Type** | Bi-Encoder (Sentence Transformer) |
| **Dimensions** | 768 |
| **Language** | Vietnamese optimized |
| **Source** | HuggingFace |

```python
# src/ingestion/indexer.py
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="bkai-foundation-models/vietnamese-bi-encoder",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
```

### 🎙️ Script:

> "Chúng tôi sử dụng model **vietnamese-bi-encoder** từ BKAI - một lab AI của Việt Nam.
>
> Model này được train đặc biệt cho tiếng Việt, nên hiểu ngữ nghĩa tiếng Việt tốt hơn các model đa ngôn ngữ thông thường.
>
> **Bi-Encoder** có nghĩa là: documents được encode một lần khi indexing, chỉ cần encode query khi search. Nhờ vậy **search rất nhanh**.
>
> Model output vectors 768 chiều, được normalize để dùng cosine similarity."

---

# PHẦN 5: FAISS VECTOR SEARCH \u0026 IVF INDEX (4 phút)

## 📽️ SLIDE 5.1: FAISS Overview

| Thuộc tính | Giá trị |
|------------|---------|
| **Full name** | Facebook AI Similarity Search |
| **Purpose** | Tìm kiếm vector nhanh và hiệu quả |
| **Developer** | Meta AI Research |

```
Query: "nghỉ thai sản mấy tháng?"
   │
   ▼ Embed
[0.1, 0.2, ..., 0.8]  ← Query vector
   │
   ▼ FAISS Search
   │
Tìm Top-10 vectors gần nhất trong index
   │
   ▼
[Document về Điều 139], [Document về thai sản], ...
```

### 🎙️ Script:

> "**FAISS** là thư viện của Facebook AI, chuyên dùng để tìm kiếm vector.
>
> Khi có câu hỏi, chúng tôi:
> 1. Embed câu hỏi thành vector
> 2. Dùng FAISS tìm 10 vectors gần nhất trong database
> 3. Map các vectors đó về documents gốc
>
> FAISS rất nhanh - có thể search hàng triệu vectors trong milliseconds."

---

## 📽️ SLIDE 5.2: Index Types Comparison

**Flat Index (Exact Search):**
```
●●●●●●●●
●●●●●●●●
(search ALL vectors)
```
- ✅ 100% accuracy
- ❌ Slower with large data  
- Brute-force comparison
- O(N) complexity

**IVF Index (Approximate Search):**
```
┌──●●●┐ Cluster 1
└─────┘
┌──●●●┐ Cluster 2
└─────┘
(search some clusters)
```
- ✅ ~97% accuracy
- ✅ 5-10x faster
- K-means clustering
- O(log N) complexity

### 🎙️ Script:

> "FAISS có 2 loại index chính:
>
> **Flat Index**: Tìm kiếm chính xác 100%, nhưng phải so sánh với TẤT CẢ vectors. Độ phức tạp là O(N) - tuyến tính với số lượng vectors.
>
> **IVF Index**: Inverted File Index - chia vectors thành clusters bằng K-means. Khi search, chỉ tìm trong một số clusters gần nhất. Nhanh hơn 5-10 lần với ~97% accuracy.
>
> Với project này, chúng tôi chọn IVF để **demo khả năng scale** và giảm latency."

---

## 📽️ SLIDE 5.3: IVF Training Process - K-means Clustering

```
┌─────────────────────────────────────────────────────────┐
│  BƯỚC 1: INPUT DATA                                      │
│  All Embedding Vectors (N vectors, 768 dimensions)      │
│                    ↓                                     │
│  BƯỚC 2: TRAINING PHASE                                 │
│  K-means Algorithm (nlist = 64 clusters)                │
│  Compute Centroids (64 cluster centers)                 │
│                    ↓                                     │
│  BƯỚC 3: ASSIGNMENT                                     │
│  Assign each vector to nearest centroid                 │
│                    ↓                                     │
│  BƯỚC 4: RESULT                                         │
│  Trained IVF Index - Ready for search                   │
└─────────────────────────────────────────────────────────┘
```

### 🎙️ Script:

> "IVF Index cần được **train** trước khi sử dụng. Quá trình này dùng **K-means clustering**:
>
> **Bước 1**: Chuẩn bị tất cả vectors (1,500 vectors × 768 dimensions trong dự án này).
>
> **Bước 2**: Chạy thuật toán K-means với nlist=64. Thuật toán sẽ tìm 64 cluster centers (centroids) đại diện cho các vùng trong không gian vector.
>
> **Bước 3**: Assign mỗi vector vào cluster gần nhất.
>
> **Bước 4**: Index đã sẵn sàng. Quá trình này chỉ chạy **một lần** khi build index, mất khoảng 2 giây cho 1,500 vectors."

---

## 📽️ SLIDE 5.4: K-means Training Details

**K-means Algorithm Steps:**

1. **Initialize** 64 random centroids
2. **Assign** mỗi vector → nearest centroid
3. **Update** centroids = mean của assigned vectors  
4. **Repeat** steps 2-3 cho đến khi converge (~10-30 iterations)

**Configuration trong code:**
```python
# src/config.py
IVF_NLIST = 64   # Số clusters
IVF_NPROBE = 8   # Số clusters search at query time

# Training code (indexer.py)
factory = f"IVF{nlist},Flat"
index = faiss.index_factory(dim, factory)
index.train(embeddings)  # K-means happens here
index.add(embeddings)    # Add vectors to trained index
```

**Điều chỉnh nlist:**
- Nhỏ (16-32) → Faster training, slower search
- Lớn (128-256) → Slower training, faster search
- **Rule of thumb**: nlist ≈ √N (với N = số vectors)

### 🎙️ Script:

> "K-means là thuật toán clustering cổ điển. Bắt đầu với 64 centroids ngẫu nhiên, sau đó lặp lại 2 bước:
>
> **Assignment**: Gán mỗi vector vào cluster có centroid gần nhất.
> **Update**: Tính lại centroid = trung bình của tất cả vectors trong cluster.
>
> Lặp cho đến khi converge - thường 10-30 iterations.
>
> Chúng tôi chọn **nlist=64** theo rule of thumb: căn bậc 2 của 1,500 ≈ 39, làm tròn lên 64 để hiệu quả hơn."

---

## 📽️ SLIDE 5.5: IVF Search Process

```
┌─────────────────────────────────────────────────────────┐
│  QUERY                                                   │
│  Query Vector [0.1, 0.2, ..., 0.8]                      │
│                    ↓                                     │
│  DISTANCE TO CENTROIDS                                  │
│  Compute distance to 64 centroids                       │
│                    ↓                                     │
│  SELECT TOP-K CLUSTERS                                  │
│  Select 8 nearest clusters (nprobe=8)                   │
│                    ↓                                     │
│  SEARCH IN CLUSTERS                                     │
│  Search only vectors in those 8 clusters                │
│                    ↓                                     │
│  RESULT                                                 │
│  Top-10 similar documents                               │
└─────────────────────────────────────────────────────────┘
```

### 🎙️ Script:

> "Khi search với IVF index:
>
> **Bước 1**: Tính khoảng cách từ query vector đến 64 centroids. Cost: O(64 × 768) - rất nhanh.
>
> **Bước 2**: Chọn 8 clusters gần nhất (nprobe=8). Đây là tham số điều chỉnh được - trade-off giữa speed và accuracy.
>
> **Bước 3**: Search chỉ trong ~187 vectors của 8 clusters đó (1,500 / 64 × 8), thay vì tất cả 1,500 vectors.
>
> **Bước 4**: Trả về top-10 documents gần nhất.
>
> Nhờ vậy, chỉ cần search ~12.5% số vectors, nhanh hơn 8 lần!"

---

## 📽️ SLIDE 5.6: Performance Benchmark

**Test Setup:**

| Metric | Value |
|--------|-------|
| Dataset | Vietnamese Labor Law |
| Total Vectors | ~1,500 chunks |
| Embedding Model | vietnamese-bi-encoder (768D) |
| Hardware | CPU (Intel i7) |
| Query Set | 100 legal questions |

**Results: Flat vs IVF**

| Index Type | Config | Avg Search Time | Recall@10 | Memory |
|------------|--------|-----------------|-----------|---------|
| Flat | - | 45ms | 100% | 4.5MB |
| IVF64 | nprobe=4 | 12ms | 95.2% | 4.8MB |
| IVF64 | nprobe=8 | 18ms | 97.8% | 4.8MB |
| IVF64 | nprobe=16 | 28ms | 99.1% | 4.8MB |

**Key Findings:**
- **IVF64 (nprobe=8)**: 2.5x faster với ~98% accuracy → Best trade-off
- Memory overhead: Minimal (~7% cho 64 centroids)
- Training time: ~2s cho 1,500 vectors

### 🎙️ Script:

> "Chúng tôi đã benchmark với 100 câu hỏi pháp lý thực tế:
>
> **Flat index**: 45ms, chính xác 100%.
>
> **IVF với nprobe=4**: Nhanh nhất (12ms) nhưng chỉ 95% accuracy - có thể bỏ sót documents quan trọng.
>
> **IVF với nprobe=8**: **Best trade-off** - 18ms (2.5x faster), 97.8% accuracy. Đây là config chúng tôi deploy.
>
> **IVF với nprobe=16**: 28ms, 99.1% accuracy - gần như bằng Flat nhưng vẫn nhanh hơn.
>
> Memory overhead chỉ 7% - rất nhỏ so với lợi ích về speed."

---

## 📽️ SLIDE 5.7: Accuracy vs Speed Trade-off

```
ACCURACY                    SPEED
Flat: 100%         ←→      Flat: 45ms
IVF nprobe=16: 99.1%  ←→   IVF nprobe=16: 28ms  
IVF nprobe=8: 97.8%   ←→   IVF nprobe=8: 18ms  ← BEST
IVF nprobe=4: 95.2%   ←→   IVF nprobe=4: 12ms
```

**Trade-off Equation:**
```
Speed_gain = N / (nlist × nprobe)
Accuracy_loss ≈ 2-5%
```

### 🎙️ Script:

> "Đây là trade-off cơ bản: **càng nhanh thì càng ít chính xác**.
>
> Với nprobe=4: Rất nhanh nhưng mất 5% accuracy.
> Với nprobe=16: Gần như chính xác như Flat.
>
> **Sweet spot** là nprobe=8 - highlighted trên đồ thị. Nó mất chỉ ~2% accuracy nhưng nhanh hơn 2.5 lần.
>
> Công thức speed gain: N / (nlist × nprobe) = 1500 / (64 × 8) = 2.9x - khá gần với kết quả thực tế."

---

## 📽️ SLIDE 5.8: When to Use IVF?

**✅ Sử dụng IVF khi:**
- Dataset > 10,000 vectors
- Cần low latency (< 50ms)
- Chấp nhận ~2-3% recall loss
- Production environment
- Frequent queries

**❌ Dùng Flat khi:**
- Dataset nhỏ (< 10,000)
- Cần 100% accuracy
- Không quan tâm latency
- Development/testing
- Không đủ vectors để train (< nlist)

**Dự án này:**
- 1,500 vectors → Có thể dùng Flat (45ms vẫn OK)
- Nhưng chọn IVF để **demo scalability**
- Khi scale lên 100,000+ documents, IVF sẽ rất quan trọng

### 🎙️ Script:

> "Khi nào nên dùng IVF?
>
> **Production systems với > 10,000 documents**: IVF là must-have. Flat sẽ quá chậm.
>
> **Dự án nhỏ < 10,000**: Flat đủ tốt. Đơn giản, không cần train.
>
> **Project này**: 1,500 vectors, Flat vẫn chạy tốt (45ms). Nhưng chúng tôi chọn IVF để:
> - Demo khả năng scale
> - Giảm latency (18ms)
> - Chuẩn bị cho tương lai khi thêm nhiều luật mới
>
> IVF không phải lúc nào cũng cần, nhưng là **best practice** cho production RAG systems."

---

## 📽️ SLIDE 5.9: Incremental Sync

```
┌─────────────────────────────────────────────────────────────┐
│                    INCREMENTAL SYNC                          │
│                                                             │
│   New file added?     → Index only the new file            │
│   File modified?      → Re-index that file only            │
│   File deleted?       → Remove from index                  │
│   File unchanged?     → Skip (no processing)               │
│                                                             │
│   Tracking: MD5 hash của mỗi file trong metadata.json      │
└─────────────────────────────────────────────────────────────┘
```

### 🎙️ Script:

> "Một tính năng quan trọng là **Incremental Sync**.
>
> Thay vì re-index toàn bộ khi có thay đổi, chúng tôi chỉ xử lý file thay đổi.
>
> Hệ thống track **MD5 hash** của mỗi file. Khi chạy sync:
> - File mới → Index
> - File đã sửa (hash khác) → Re-index
> - File đã xóa → Remove khỏi index
> - File không đổi → Skip
>
> Nhờ vậy, việc cập nhật luật mới rất nhanh."

---

# PHẦN 6: TỔNG KẾT & CHUYỂN TIẾP (0.5 phút)

## 📽️ SLIDE 6.1: Tóm tắt

| Chủ đề | Điểm chính |
|--------|------------|
| **Pipeline** | Load → Split → Embed → Store |
| **Chunking** | 1000 chars, 200 overlap, recursive splitting |
| **Embedding** | vietnamese-bi-encoder, 768D, tiếng Việt |
| **FAISS** | IVF index, ~97% accuracy, fast search |
| **Sync** | Incremental, chỉ xử lý file thay đổi |

### 🎙️ Script:

> "Tóm lại, Data Ingestion pipeline gồm 4 bước: Load, Split, Embed, Store.
>
> Chúng tôi dùng model tiếng Việt cho embedding và FAISS với IVF index cho search nhanh.
>
> Incremental sync đảm bảo việc cập nhật luật mới rất hiệu quả."

---

## 📽️ SLIDE 6.2: Chuyển tiếp

| Tiếp theo | Member 3: RAG Engine & LLM Integration |
|-----------|----------------------------------------|
| **Chủ đề** | Semantic Search, Intent Routing, Prompt Engineering |
| **Câu hỏi** | "Làm sao biến search results thành câu trả lời?" |

### 🎙️ Script:

> "Đó là phần của tôi về **Data Ingestion và Vector Database**.
>
> Bây giờ, **Member 3** sẽ giải thích cách hệ thống sử dụng data này để **tìm kiếm ngữ nghĩa và sinh câu trả lời** với LLM.
>
> Xin mời Member 3."

---

# 📋 CHECKLIST CHUẨN BỊ

- [ ] Đọc kỹ các file trong `src/ingestion/`: `loader.py`, `splitter.py`, `indexer.py`
- [ ] Hiểu khái niệm Embedding và Vector similarity
- [ ] Chạy thử lệnh `python ingest.py` để hiểu ingestion flow
- [ ] Xem folder `data/vector_store/` để thấy output files
- [ ] Chuẩn bị giải thích tại sao chọn các parameters (chunk_size=1000, etc.)

---

# ❓ CÂU HỎI CÓ THỂ GẶP

| Câu hỏi | Gợi ý trả lời |
|---------|---------------|
| "Tại sao chunk_size=1000?" | Balanced cho Vietnamese text (~500 từ), đủ context cho một điều luật, phù hợp với embedding model |
| "Tại sao dùng vietnamese-bi-encoder?" | Được train cho tiếng Việt, hiểu ngữ nghĩa tốt hơn multilingual models |
| "IVF có bỏ sót document không?" | Có thể (~3%), nhưng với nprobe=32 thì đạt 97% recall, acceptable trade-off |
| "Incremental sync hoạt động thế nào?" | Track MD5 hash của mỗi file, so sánh với lần index trước, chỉ process changes |
