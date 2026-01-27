# 🧠 Khái Niệm RAG (Retrieval-Augmented Generation)

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- RAG là gì và tại sao cần RAG
- Các thành phần của RAG pipeline
- Ưu nhược điểm so với các phương pháp khác
- Cách RAG hoạt động trong dự án

---

## 1. RAG là gì?

### 1.1 Định nghĩa
**RAG (Retrieval-Augmented Generation)** là kỹ thuật kết hợp:
- **Retrieval**: Tìm kiếm thông tin từ knowledge base
- **Generation**: Sử dụng LLM để tạo câu trả lời dựa trên thông tin tìm được

### 1.2 Ý tưởng cốt lõi
```
┌──────────────────────────────────────────────────────────┐
│                    Without RAG                            │
│                                                          │
│   User Question ──────────────────────► LLM ─────► Answer │
│                    (Limited/Outdated Knowledge)          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                     With RAG                              │
│                                                          │
│   User Question ───► Retrieve ───► Context + Question    │
│                        │               │                 │
│                   Knowledge Base       ▼                 │
│                        │            LLM ────► Answer     │
│                        │          (With citations)       │
│                   Vector Database                        │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Tại sao cần RAG?

### 2.1 Hạn chế của LLM thuần túy
| Vấn đề | Mô tả |
|--------|-------|
| **Knowledge Cutoff** | LLM chỉ biết data đến thời điểm training |
| **Hallucination** | LLM có thể bịa thông tin sai |
| **No Citation** | Không thể trích dẫn nguồn cụ thể |
| **Domain Knowledge** | Thiếu kiến thức chuyên ngành (ví dụ: luật VN) |

### 2.2 RAG giải quyết như thế nào?
| Vấn đề | Giải pháp RAG |
|--------|---------------|
| Knowledge Cutoff | Cập nhật knowledge base mới không cần retrain |
| Hallucination | LLM chỉ trả lời dựa trên context được cung cấp |
| No Citation | Kèm theo source document và page number |
| Domain Knowledge | Inject domain-specific documents vào context |

---

## 3. RAG Pipeline Chi Tiết

### 3.1 Offline Phase (Indexing)
Chuyển đổi documents thành vector và lưu trữ:

```
PDF/DOCX Files
      │
      ▼
┌─────────────┐
│   Loader    │  ← Load file, extract text
└─────────────┘
      │
      ▼
┌─────────────┐
│  Splitter   │  ← Chia thành chunks nhỏ (1000 chars)
└─────────────┘
      │
      ▼
┌─────────────┐
│  Embedding  │  ← Chuyển text → vector (768 dimensions)
└─────────────┘
      │
      ▼
┌─────────────┐
│   FAISS     │  ← Lưu trữ và index vectors
└─────────────┘
```

### 3.2 Online Phase (Query)
Xử lý câu hỏi và tạo câu trả lời:

```
User Query: "Thai sản được nghỉ bao nhiêu ngày?"
      │
      ▼
┌─────────────┐
│  Embedding  │  ← Query → vector
└─────────────┘
      │
      ▼
┌─────────────┐
│  Retrieval  │  ← Tìm top-K vectors tương tự
└─────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  Context = [                            │
│    "Điều 139: Lao động nữ được nghỉ     │
│    trước và sau khi sinh con là 6       │
│    tháng..." (Trang 45)                 │
│  ]                                      │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────┐
│     LLM     │  ← Context + Question → Answer
└─────────────┘
      │
      ▼
"Theo Điều 139 Bộ luật Lao động, người lao động nữ
được nghỉ thai sản 6 tháng. [Nguồn: file.pdf, Trang 45]"
```

---

## 4. Các khái niệm quan trọng

### 4.1 Embedding
- **Định nghĩa**: Biểu diễn text dưới dạng vector số học
- **Mục đích**: So sánh semantic similarity giữa các văn bản
- **Trong dự án**: Sử dụng `vietnamese-bi-encoder` (768 dimensions)

```python
# Ví dụ conceptual
text = "Thai sản được nghỉ bao nhiêu ngày?"
vector = embed(text)  # → [0.12, -0.45, ..., 0.78]  (768 values)
```

### 4.2 Chunking
- **Tại sao cần**: LLM có giới hạn context window
- **Chiến lược**: Chia document thành chunks ~1000 characters
- **Overlap**: 200 characters để giữ ngữ cảnh liên tục

```
Document: "Điều 139... (1000 chars) ... Điều 140... (1000 chars)"
             │                          │
             ▼                          ▼
         Chunk 1                    Chunk 2
    (overlap 200 chars với chunk 2)
```

### 4.3 Similarity Search
- **Cosine Similarity**: Đo góc giữa 2 vectors
- **L2 Distance**: Khoảng cách Euclidean
- **Top-K**: Lấy K documents có similarity cao nhất

```
Query Vector: [0.1, 0.2, 0.3]

Document Vectors:
- Doc A: [0.11, 0.19, 0.31]  ← Similarity: 0.99 ✓ Top-1
- Doc B: [0.5, -0.1, 0.2]   ← Similarity: 0.45
- Doc C: [-0.3, 0.0, 0.1]   ← Similarity: 0.12
```

### 4.4 Context Window
- **Giới hạn LLM**: Số lượng token tối đa LLM có thể nhận
- **Trade-off**: Nhiều context = nhiều thông tin nhưng chậm hơn
- **Trong dự án**: Lấy top 10 documents, tổng ~2000-3000 tokens

---

## 5. So sánh các phương pháp

| Tiêu chí | RAG | Fine-tuning | Prompt Engineering |
|----------|-----|-------------|-------------------|
| **Cost** | Thấp | Cao | Thấp |
| **Update Knowledge** | Dễ (thêm docs) | Khó (retrain) | Không thể |
| **Citation** | ✅ Có | ❌ Không | ❌ Không |
| **Domain Accuracy** | Cao | Cao | Trung bình |
| **Hallucination** | Thấp | Trung bình | Cao |
| **Complexity** | Trung bình | Cao | Thấp |

---

## 6. RAG trong dự án AI Legal Assistant

### 6.1 Đặc thù domain Pháp luật
- **Yêu cầu chính xác**: Trả lời sai có thể gây hậu quả nghiêm trọng
- **Cần trích dẫn**: Người dùng muốn verify thông tin
- **Cập nhật thường xuyên**: Luật thay đổi theo năm

### 6.2 Customizations
| Component | Customization |
|-----------|---------------|
| Embedding Model | `vietnamese-bi-encoder` - optimized cho tiếng Việt |
| Prompt | IRAC structure (Issue-Rule-Analysis-Conclusion) |
| Router | Phân loại LEGAL vs GENERAL intent |
| Rewriter | Viết lại câu hỏi follow-up thành standalone |

### 6.3 Prompt Engineering cho Legal
```python
QA_SYSTEM_PROMPT = """
Bạn là Cố vấn Pháp lý AI cấp cao...

QUY TRÌNH TƯ DUY (Chain of Thought):
1. Đọc kỹ câu hỏi để xác định vấn đề pháp lý cốt lõi
2. Rà soát [TÀI LIỆU THAM KHẢO] để tìm Điều khoản liên quan
3. Xây dựng câu trả lời theo cấu trúc IRAC

NGUYÊN TẮC BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (Hallucination)
2. CHỈ sử dụng thông tin từ Context
3. LUÔN trích dẫn nguồn cụ thể
"""
```

---

## 7. Điểm mạnh của RAG trong dự án này

> [!TIP]
> **Highlight khi thuyết trình:**
> 1. **Accuracy + Citation**: Mọi câu trả lời đều có nguồn verify
> 2. **Easy Update**: Thêm luật mới chỉ cần copy file PDF vào folder
> 3. **Vietnamese Optimized**: Embedding model được train cho tiếng Việt
> 4. **Conversational**: Hỗ trợ hỏi tiếp (follow-up questions)

---

## 8. Limitations & Trade-offs

| Limitation | Mitigation |
|------------|------------|
| Retrieval quality depends on chunking | Overlap 200 chars để giữ context |
| Top-K might miss relevant docs | K=10 để tăng recall |
| Embedding model không perfect | Dùng model specialized cho Vietnamese |
| LLM có thể ignore context | Strict prompt engineering |

---

## Tài liệu liên quan
- [Overview Architecture](./01_overview_architecture.md)
- [Tech Stack Summary](./03_tech_stack_summary.md)
