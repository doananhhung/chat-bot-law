# ✂️ Text Chunking - Chiến Lược Chia Văn Bản

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- Tại sao cần chia văn bản thành chunks
- Các chiến lược chunking phổ biến
- RecursiveCharacterTextSplitter hoạt động như thế nào
- Chunk size và overlap optimization

---

## 1. Tại sao cần Chunking?

### 1.1 Giới hạn của LLM
| Model | Max Context (tokens) | 
|-------|----------------------|
| GPT-3.5 | 4,096 |
| GPT-4 | 8,192 - 128K |
| Gemini Pro | 32,768 |
| Kimi K2 | 32,768 |

**Vấn đề**: Document pháp luật có thể dài hàng nghìn trang!

### 1.2 Lý do Chunking

| Lý do | Giải thích |
|-------|------------|
| **Context limit** | LLM không thể xử lý document quá dài |
| **Precision** | Chunks nhỏ = tìm kiếm chính xác hơn |
| **Cost** | Ít tokens = rẻ hơn |
| **Noise reduction** | Chỉ lấy phần liên quan, bỏ qua phần không cần |

### 1.3 Trade-off

```
┌─────────────────────────────────────────────────────┐
│                  CHUNK SIZE TRADE-OFF               │
│                                                     │
│   Nhỏ quá              Vừa phải            Lớn quá │
│   ──────────────────────────────────────────────── │
│   ❌ Mất context       ✅ Balanced          ❌ Noise │
│   ❌ Nhiều chunks      ✅ Searchable        ❌ Slow  │
│   ✅ Precise search    ✅ Context ok        ❌ Costly│
└─────────────────────────────────────────────────────┘
```

---

## 2. Các chiến lược Chunking

### 2.1 Fixed Size Chunking
```python
# Đơn giản nhưng có thể cắt giữa câu
chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
```
❌ **Nhược điểm**: Cắt giữa câu, mất ngữ nghĩa

### 2.2 Sentence Chunking
```python
# Chia theo câu
sentences = text.split(". ")
```
❌ **Nhược điểm**: Mỗi câu quá ngắn, mất ngữ cảnh

### 2.3 Semantic Chunking
```python
# Chia theo ý nghĩa (paragraph, section)
chunks = text.split("\n\n")
```
⚠️ **Nhược điểm**: Kích thước không đều, có thể quá lớn

### 2.4 ✅ Recursive Character Chunking (Dùng trong dự án)
```python
# Kết hợp: Cố gắng cắt theo paragraph, nếu không được thì cắt theo sentence, ...
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
```

---

## 3. RecursiveCharacterTextSplitter

### 3.1 Hoạt động như thế nào

```
Separators: ["\n\n", "\n", " ", ""]
             ↓
Priority:   1st   2nd   3rd   4th (fallback)
```

**Algorithm**:
1. Thử split theo separator đầu tiên (`"\n\n"` - paragraph)
2. Nếu chunk vẫn > 1000 chars → thử separator tiếp theo (`"\n"` - line)
3. Tiếp tục cho đến khi chunk ≤ 1000 chars
4. Fallback cuối cùng: cắt theo character

### 3.2 Ví dụ minh họa

```
Original Document:
┌────────────────────────────────────────────────────────────┐
│ Điều 139. Nghỉ thai sản                                    │
│                                                            │
│ 1. Lao động nữ được nghỉ trước và sau khi sinh con        │
│ là 6 tháng; trường hợp sinh đôi trở lên thì tính từ       │
│ con thứ 2 trở đi, cứ mỗi con được nghỉ thêm 1 tháng.     │
│                                                            │
│ 2. Trong thời gian nghỉ thai sản...                       │
│ [text dài ~2000 chars]                                     │
└────────────────────────────────────────────────────────────┘

After RecursiveCharacterTextSplitter(chunk_size=1000):
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Chunk 1    │    │   Chunk 2    │    │   Chunk 3    │
│ Điều 139...  │    │...thêm 1     │    │ 2. Trong     │
│ 1. Lao động  │◄──►│ tháng...     │◄──►│ thời gian... │
│ ~1000 chars  │    │ ~1000 chars  │    │ ~1000 chars  │
└──────────────┘    └──────────────┘    └──────────────┘
       ↑ overlap 200 ↑
```

---

## 4. Cấu hình trong dự án

### 4.1 Parameters

```python
# src/ingestion/splitter.py
splitter = RecursiveCharacterTextSplitter(
    chunk_size=AppConfig.CHUNK_SIZE,      # 1000
    chunk_overlap=AppConfig.CHUNK_OVERLAP, # 200
    separators=["\n\n", "\n", " ", ""]
)
```

### 4.2 Tại sao chọn chunk_size=1000?

| Factor | Consideration |
|--------|---------------|
| Vietnamese text | ~2 chars/word → ~500 words |
| Legal context | Một điều luật thường 500-1500 chars |
| Embedding model | Optimal cho semantic encoding |
| Retrieval precision | Đủ context nhưng không quá nhiều noise |

### 4.3 Tại sao overlap=200?

```
Chunk 1: [───────────────────]  (1000 chars)
Chunk 2:           [───────────────────]  (1000 chars)
                   └─ overlap 200 ─┘

Lợi ích:
✅ Giữ ngữ cảnh liên tục giữa các chunks
✅ Không mất thông tin ở ranh giới
✅ 20% overlap là balanced
```

---

## 5. Metadata Enhancement

### 5.1 Sau khi split, thêm metadata

```python
# src/ingestion/splitter.py
for source, source_docs in docs_by_source.items():
    total = len(source_docs)
    for idx, doc in enumerate(source_docs):
        doc.metadata.update({
            "chunk_id": str(uuid.uuid4()),  # Unique ID
            "chunk_index": idx,              # Thứ tự chunk
            "total_chunks": total,           # Tổng chunks của file
            "created_at": timestamp
        })
```

### 5.2 Metadata Example

```python
Document(
    page_content="Điều 139. Nghỉ thai sản...",
    metadata={
        # From loader
        "source": "luat_lao_dong.pdf",
        "page": 45,
        
        # From splitter
        "chunk_id": "uuid-abc-123",
        "chunk_index": 0,
        "total_chunks": 150,
        "created_at": "2026-01-27T10:00:00Z"
    }
)
```

---

## 6. Edge Cases

### 6.1 Chunk quá nhỏ sau khi split
```python
# Xử lý: LangChain tự merge chunks nhỏ
# Nếu chunk < chunk_size/2, merge với chunk tiếp theo
```

### 6.2 Document rất ngắn
```python
# Nếu document < chunk_size:
# → Không split, giữ nguyên là 1 chunk
```

### 6.3 Bảng biểu, hình ảnh trong PDF
```python
# PyPDFLoader chỉ extract text
# → Bảng có thể bị mất format
# → Hình ảnh bị bỏ qua (chỉ có OCR mới đọc được)
```

---

## 7. Performance

### 7.1 Thống kê trong dự án

| Metric | Value |
|--------|-------|
| Input | 1 PDF (200 pages) |
| Raw pages | 200 documents |
| After split | ~1500 chunks |
| Avg chunk size | ~900 chars |
| Split time | ~0.1s |

### 7.2 Memory Usage
```python
# Chunks được xử lý in-memory
# ~1500 chunks * 1KB = ~1.5MB
# Không cần streaming cho document nhỏ
```

---

## 8. Best Practices

### 8.1 Tuning chunk_size

| Document Type | Recommended chunk_size |
|---------------|------------------------|
| Legal documents (dense) | 800-1200 |
| General articles | 1000-1500 |
| Code documentation | 500-800 |

### 8.2 Tuning overlap

| Use Case | Recommended overlap |
|----------|---------------------|
| High context importance | 25-30% of chunk_size |
| Standard | 20% of chunk_size |
| Low context dependency | 10-15% |

---

## 9. Code trong dự án

```python
# src/ingestion/splitter.py

class TextSplitter:
    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=AppConfig.CHUNK_SIZE,
            chunk_overlap=AppConfig.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} input docs into {len(split_docs)} chunks.")
        
        # Group by source to calculate total_chunks
        docs_by_source = {}
        for doc in split_docs:
            source = doc.metadata.get("source", "unknown")
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        # Add metadata
        final_docs = []
        for source, source_docs in docs_by_source.items():
            total = len(source_docs)
            for idx, doc in enumerate(source_docs):
                doc.metadata.update({
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_index": idx,
                    "total_chunks": total,
                    "created_at": datetime.utcnow().isoformat() + "Z"
                })
                final_docs.append(doc)
        
        return final_docs
```

---

## 10. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **RecursiveCharacterTextSplitter**: Chia thông minh theo priority separators
> 2. **chunk_size=1000**: Balanced cho legal documents
> 3. **overlap=200**: Giữ ngữ cảnh liên tục
> 4. **Metadata enrichment**: Thêm chunk_id, index, total

---

## Tài liệu liên quan
- [Ingestion Pipeline](./01_ingestion_pipeline.md)
- [Embedding Models](./03_embedding_models.md)
