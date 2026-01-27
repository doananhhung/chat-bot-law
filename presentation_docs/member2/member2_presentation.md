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

# PHẦN 5: FAISS VECTOR SEARCH (2 phút)

## 📽️ SLIDE 5.1: FAISS là gì?

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

## 📽️ SLIDE 5.2: Index Types

| Type | Factory String | Đặc điểm |
|------|----------------|----------|
| **Flat** | `"Flat"` | Exact search, brute-force, chậm |
| **IVF** | `"IVF64,Flat"` | Approximate, nhanh hơn 5x |
| **IVFPQ** | `"IVF64,PQ48x8"` | Approximate + compression, nhanh nhất |

```
┌─────────────────────────────────────────────────────────────┐
│   FLAT                    IVF                               │
│   ●●●●●●●●               ┌──●●●┐                           │
│   ●●●●●●●●               │     │ Cluster 1                 │
│   ●●●●●●●●               └──●●●┘                           │
│   (search ALL)           ┌──●●●┐                           │
│                          │     │ Cluster 2                 │
│   100% accuracy          └──●●●┘                           │
│   Slower                 (search some clusters)            │
│                          ~97% accuracy, Much faster        │
└─────────────────────────────────────────────────────────────┘
```

### 🎙️ Script:

> "FAISS có nhiều loại index với trade-off khác nhau:
>
> **Flat Index**: Tìm kiếm chính xác 100%, nhưng phải so sánh với TẤT CẢ vectors. Chậm khi data lớn.
>
> **IVF Index**: Chia vectors thành clusters. Khi search, chỉ tìm trong một số clusters. Nhanh hơn 5x với 97% accuracy.
>
> Trong dự án, chúng tôi dùng **IVF** với 64 clusters. Khi search, chỉ tìm trong 8-32 clusters gần nhất."

---

## 📽️ SLIDE 5.3: Incremental Sync

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
