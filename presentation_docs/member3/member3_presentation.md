# 🎤 Member 3: RAG Engine & LLM Integration - Tài Liệu Thuyết Trình

> **Thời lượng:** ~8-10 phút | **Vai trò:** Giải thích core RAG logic và prompt engineering

---

# PHẦN 1: SEMANTIC RETRIEVAL (2 phút)

## 📽️ SLIDE 1.1: Tiêu đề phần

| Nội dung trình chiếu |
|---------------------|
| **RAG Engine & LLM Integration** |
| *Từ Search Results → Câu Trả Lời Thông Minh* |
| --- |
| 👤 Member 3 |

### 🎙️ Script:

> "Xin chào, tôi là Member 3. Sau khi Member 2 đã giải thích cách dữ liệu được index, tôi sẽ trình bày **cách hệ thống sử dụng dữ liệu đó** để tìm kiếm và sinh câu trả lời.
>
> Đây là phần **trái tim của hệ thống RAG**."

---

## 📽️ SLIDE 1.2: Keyword Search vs Semantic Search

| Aspect | Keyword Search | Semantic Search |
|--------|----------------|-----------------|
| **Matching** | Exact words | Ý nghĩa/khái niệm |
| **Query** | "nghỉ thai sản" | "được nghỉ bao lâu khi sinh con?" |
| **Miss** | "nghỉ đẻ", "maternity" | ❌ Không miss |
| **Catch** | ❌ Chỉ exact match | ✅ Tất cả khái niệm liên quan |

```
User Query: "nghỉ đẻ được mấy tháng?"

Keyword Search:
❌ Không match "thai sản"
❌ Miss relevant documents

Semantic Search:
✅ Match "nghỉ thai sản"
✅ Match "lao động nữ được nghỉ khi sinh con"
→ Hiểu NGHĨA, không chỉ từ ngữ
```

### 🎙️ Script:

> "Điểm khác biệt lớn nhất của hệ thống là **Semantic Search**.
>
> Với Keyword Search truyền thống, nếu hỏi 'nghỉ đẻ' sẽ không tìm được document chứa 'thai sản'.
>
> Với Semantic Search, hệ thống **hiểu được rằng 'nghỉ đẻ' và 'thai sản' cùng một khái niệm**. Vì sao? Vì embedding model đã học được ngữ nghĩa từ dữ liệu tiếng Việt.
>
> Nhờ vậy, user có thể hỏi bằng ngôn ngữ tự nhiên mà vẫn tìm được đúng thông tin."

---

## 📽️ SLIDE 1.3: SemanticRetriever Class

```python
# src/rag_engine/retriever.py
class SemanticRetriever:
    def __init__(self):
        # Load embedding model (vietnamese-bi-encoder)
        self.embeddings = HuggingFaceEmbeddings(...)
        
        # Load FAISS index
        self.vector_store = FAISS.load_local(...)
    
    def get_relevant_docs(self, query: str, k: int = 10):
        """Retrieve top-k relevant documents."""
        docs = self.vector_store.similarity_search(query, k=k)
        return docs
```

| Parameter | Giá trị | Ý nghĩa |
|-----------|---------|---------|
| **k** | 10 | Lấy top 10 documents liên quan nhất |
| **Search** | similarity_search | Dựa trên cosine similarity |

### 🎙️ Script:

> "**SemanticRetriever** là class chịu trách nhiệm tìm kiếm.
>
> Khi khởi tạo, nó load embedding model và FAISS index vào memory.
>
> Method `get_relevant_docs` nhận câu hỏi, tìm **top 10 documents** có similarity cao nhất.
>
> Tại sao chọn k=10? Đây là trade-off giữa recall và noise. 10 docs đủ để cover nhiều góc độ của câu hỏi mà không quá nhiều noise."

---

# PHẦN 2: INTENT ROUTING (2 phút)

## 📽️ SLIDE 2.1: Vấn đề - Off-topic Queries

```
Không có Router:
─────────────────
User: "Xin chào!"
System: [searches legal database]
System: "Tôi không tìm thấy tài liệu về 'xin chào'..."
❌ Bad UX

Có Router:
──────────
User: "Xin chào!"
Router: → GENERAL
System: "Xin chào! Tôi là trợ lý pháp lý AI..."
✅ Good UX
```

### 🎙️ Script:

> "Một vấn đề quan trọng: **Không phải mọi câu hỏi đều cần search database**.
>
> Nếu user chào 'Xin chào!', hệ thống không cần tìm trong luật. Chỉ cần chào lại thôi.
>
> Nếu không có router, hệ thống sẽ cố search 'xin chào' trong database pháp luật, rất vô nghĩa.
>
> Vì vậy chúng tôi có **Intent Router** để phân loại câu hỏi."

---

## 📽️ SLIDE 2.2: Intent Router

| Intent | Mô tả | Flow xử lý |
|--------|-------|------------|
| **LEGAL** | Câu hỏi về luật pháp | RAG Pipeline (Search + Generate) |
| **GENERAL** | Chào hỏi, xã giao, off-topic | General Chat (Skip search) |

```python
# src/rag_engine/router.py
ROUTER_TEMPLATE = """
Phân loại câu hỏi:
1. "LEGAL": Liên quan đến luật pháp, quy định, nghị định
2. "GENERAL": Chào hỏi, xã giao, không liên quan luật

CHỈ trả về: "LEGAL" hoặc "GENERAL"

Câu hỏi: {question}
"""
```

**Ví dụ phân loại:**
| Query | Intent |
|-------|--------|
| "Thai sản nghỉ mấy tháng?" | LEGAL |
| "Xin chào!" | GENERAL |
| "Điều 139 nói gì?" | LEGAL |
| "1 + 1 = ?" | GENERAL |

### 🎙️ Script:

> "**Intent Router** sử dụng LLM để phân loại câu hỏi.
>
> Prompt rất đơn giản: Yêu cầu LLM trả về chỉ một từ - LEGAL hoặc GENERAL.
>
> Nếu là **LEGAL**, câu hỏi đi vào RAG pipeline - search database và generate từ context.
>
> Nếu là **GENERAL**, skip search, trả lời trực tiếp như chatbot thông thường.
>
> Router cũng nhớ được ngữ cảnh - nếu đang nói về luật mà user hỏi 'còn gì nữa không', nó biết đây vẫn là LEGAL."

---

## 📽️ SLIDE 2.3: Query Rewriting

```
Vấn đề:
───────
User: "Thai sản nghỉ mấy tháng?"
AI: "Lao động nữ được nghỉ 6 tháng..."

User: "Còn nam thì sao?"
        ↑
        Câu hỏi này không đủ context để search!

Giải pháp - Query Rewriting:
───────────────────────────
Original: "Còn nam thì sao?"
    │
    ▼ (với chat history)
Rewritten: "Lao động nam có được nghỉ thai sản không?"
    │
    ▼
Now searchable!
```

### 🎙️ Script:

> "Một thách thức với conversational AI là **câu hỏi follow-up**.
>
> Khi user hỏi 'Còn nam thì sao?', câu này không đủ thông tin để search. 'Nam' là gì? 'Sao' là sao?
>
> Chúng tôi có **Query Rewriting** - sử dụng LLM để viết lại câu hỏi thành dạng **độc lập**.
>
> LLM nhìn vào lịch sử chat, hiểu context là đang nói về thai sản, và viết lại thành: 'Lao động nam có được nghỉ thai sản không?'
>
> Câu này giờ đã đủ rõ ràng để search."

---

# PHẦN 3: PROMPT ENGINEERING (2.5 phút)

## 📽️ SLIDE 3.1: Prompt Engineering là gì?

| Khái niệm | Giải thích |
|-----------|------------|
| **Prompt** | Input text gửi cho LLM |
| **Engineering** | Thiết kế prompt để nhận output chất lượng cao |

```
Same LLM, Different Prompts:

Prompt 1: "Nói về thai sản"
→ "Thai sản là quá trình mang thai và sinh con..."
   ❌ Generic, không có focus pháp lý

Prompt 2: "Bạn là Cố vấn Pháp lý AI. Dựa trên tài liệu sau..."
→ "Theo Điều 139 Bộ luật Lao động, lao động nữ được nghỉ..."
   ✅ Professional, có trích dẫn nguồn
```

### 🎙️ Script:

> "**Prompt Engineering** là nghệ thuật thiết kế input cho LLM.
>
> Cùng một LLM, nhưng prompt khác nhau sẽ cho kết quả khác nhau hoàn toàn.
>
> Prompt đơn giản cho câu trả lời đơn giản. Prompt được thiết kế kỹ sẽ cho câu trả lời chuyên nghiệp, có cấu trúc, có trích dẫn.
>
> Chúng tôi đã dành nhiều thời gian để tối ưu prompt cho domain pháp luật."

---

## 📽️ SLIDE 3.2: System Prompt - Định nghĩa AI

```python
# src/rag_engine/prompts.py
QA_SYSTEM_PROMPT = """
Bạn là Cố vấn Pháp lý AI cấp cao, chuyên về Luật Lao động Việt Nam.
Phong cách: Chuyên nghiệp, Khách quan, Dựa trên bằng chứng.

QUY TRÌNH TƯ DUY (Chain of Thought):
1. Đọc kỹ câu hỏi để xác định vấn đề pháp lý cốt lõi
2. Rà soát [TÀI LIỆU THAM KHẢO] để tìm Điều khoản liên quan
3. Xây dựng câu trả lời theo cấu trúc IRAC

NGUYÊN TẮC BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (Hallucination)
2. CHỈ sử dụng thông tin từ Context
3. LUÔN trích dẫn nguồn cụ thể [Nguồn: file.pdf, Trang: X]
"""
```

### 🎙️ Script:

> "**System Prompt** định nghĩa AI là ai và phải làm gì.
>
> Chúng tôi định nghĩa: 'Bạn là Cố vấn Pháp lý AI cấp cao'. Điều này set tone chuyên nghiệp cho câu trả lời.
>
> **Chain of Thought**: Yêu cầu AI suy nghĩ từng bước trước khi trả lời. Điều này cải thiện accuracy đáng kể.
>
> **Nguyên tắc bắt buộc**: Đặc biệt quan trọng là 'KHÔNG BỊA ĐẶT'. Nếu context không có thông tin, AI phải nói rõ thay vì bịa."

---

## 📽️ SLIDE 3.3: IRAC Structure

| Component | Meaning | Mục đích |
|-----------|---------|----------|
| **I**ssue | Vấn đề | Xác định câu hỏi pháp lý |
| **R**ule | Căn cứ | Điều luật, quy định áp dụng |
| **A**nalysis | Phân tích | Áp dụng rule vào trường hợp cụ thể |
| **C**onclusion | Kết luận | Trả lời trực tiếp, ngắn gọn |

**Example Response:**
```markdown
### 1. Căn cứ pháp lý
- Điều 139 Bộ luật Lao động 2019 [Nguồn: blld.pdf, Trang: 46]

### 2. Nội dung tư vấn & Phân tích
Theo Điều 139, lao động nữ được nghỉ thai sản trước và sau 
khi sinh con tổng cộng là 6 tháng...

### 3. Kết luận
Bạn được nghỉ thai sản **6 tháng**.
```

### 🎙️ Script:

> "Chúng tôi yêu cầu AI trả lời theo cấu trúc **IRAC** - chuẩn trong tư vấn pháp lý.
>
> **Căn cứ pháp lý**: Liệt kê điều luật nào được sử dụng, từ file nào, trang nào.
>
> **Phân tích**: Giải thích điều luật áp dụng vào trường hợp của user như thế nào.
>
> **Kết luận**: Trả lời trực tiếp, ngắn gọn.
>
> Cấu trúc này giúp user dễ follow và có thể verify thông tin."

---

# PHẦN 4: LLM FACTORY (1.5 phút)

## 📽️ SLIDE 4.1: Multi-LLM Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM FACTORY PATTERN                       │
│                                                             │
│   LLMFactory.create_llm(provider="groq", model="kimi-k2")  │
│         │                                                   │
│         ├──► if "google" → ChatGoogleGenerativeAI          │
│         │                                                   │
│         └──► if "groq" → ChatGroq                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| LLM Instance | Purpose | Temperature |
|--------------|---------|-------------|
| **Generator** | Sinh câu trả lời chi tiết | 0.3 (có creativity) |
| **Router** | Phân loại LEGAL/GENERAL | 0.0 (deterministic) |
| **Rewriter** | Viết lại query | 0.0 (chính xác) |

### 🎙️ Script:

> "Hệ thống sử dụng **3 LLM instances** cho các mục đích khác nhau.
>
> **Generator**: LLM chính để sinh câu trả lời, temperature 0.3 cho phép một chút creativity trong ngôn ngữ.
>
> **Router**: Phân loại intent, temperature 0 để output luôn deterministic.
>
> **Rewriter**: Viết lại query, cũng cần chính xác nên temperature 0.
>
> **LLM Factory** cho phép dễ dàng switch giữa các provider. Đổi một dòng config là chuyển từ Groq sang Google Gemini."

---

## 📽️ SLIDE 4.2: Supported Providers

| Provider | Model | Đặc điểm |
|----------|-------|----------|
| **Groq** | Kimi K2 | Ultra-fast inference, free tier generous |
| **Google** | Gemini | High quality, large context window |

```bash
# .env configuration
LLM_PROVIDER=groq
LLM_MODEL_NAME=moonshotai/kimi-k2-instruct-0905

# Easy to switch
# LLM_PROVIDER=google
# LLM_MODEL_NAME=gemini-2.5-flash-lite
```

### 🎙️ Script:

> "Hiện tại chúng tôi hỗ trợ 2 provider: **Groq** và **Google Gemini**.
>
> **Groq** dùng LPU (Language Processing Unit), inference cực nhanh, ~300ms per response. Free tier generous cho development.
>
> **Google Gemini** chất lượng cao, context window lớn hơn.
>
> Chuyển đổi chỉ cần thay đổi 2 dòng trong file `.env`. Code không cần sửa gì."

---

# PHẦN 5: TỔNG KẾT & CHUYỂN TIẾP (0.5 phút)

## 📽️ SLIDE 5.1: Tóm tắt

| Chủ đề | Điểm chính |
|--------|------------|
| **Semantic Search** | Hiểu nghĩa, không chỉ keyword |
| **Intent Router** | LEGAL vs GENERAL, skip search khi không cần |
| **Query Rewriting** | Biến follow-up thành standalone question |
| **Prompt Engineering** | IRAC structure, Chain-of-Thought, anti-hallucination |
| **LLM Factory** | Multi-provider, easy switching |

### 🎙️ Script:

> "Tóm lại, RAG Engine là nơi 'phép màu' xảy ra:
>
> Semantic Search hiểu ngữ nghĩa. Intent Router phân loại thông minh. Query Rewriting xử lý follow-up. Prompt Engineering đảm bảo output chất lượng. Và LLM Factory cho flexibility."

---

## 📽️ SLIDE 5.2: Chuyển tiếp

| Tiếp theo | Member 4: Frontend, Database & Demo |
|-----------|--------------------------------------|
| **Chủ đề** | Streamlit UI, SQLite, Performance, Live Demo |
| **Câu hỏi** | "Trải nghiệm người dùng như thế nào?" |

### 🎙️ Script:

> "Đó là phần của tôi về **RAG Engine và LLM Integration**.
>
> Bây giờ, **Member 4** sẽ trình bày về **giao diện người dùng, database**, và đặc biệt sẽ **demo live** hệ thống.
>
> Xin mời Member 4."

---

# 📋 CHECKLIST CHUẨN BỊ

- [ ] Đọc kỹ các file trong `src/rag_engine/`: `retriever.py`, `router.py`, `generator.py`, `prompts.py`
- [ ] Hiểu khái niệm Semantic Search vs Keyword Search
- [ ] Hiểu prompt trong `prompts.py` và tại sao thiết kế như vậy
- [ ] Có thể giải thích IRAC structure
- [ ] Hiểu sự khác biệt Groq vs Google Gemini

---

# ❓ CÂU HỎI CÓ THỂ GẶP

| Câu hỏi | Gợi ý trả lời |
|---------|---------------|
| "Semantic search hoạt động thế nào?" | Chuyển text thành vector, so sánh cosine similarity. Vectors có nghĩa tương tự sẽ gần nhau trong không gian 768D. |
| "Tại sao cần Query Rewriting?" | Follow-up questions như 'còn gì nữa không' thiếu context. Rewriting thêm context từ history để search được. |
| "Prompt có thể improve thêm không?" | Luôn có room to improve. Có thể thêm few-shot examples, tune temperature, test với nhiều edge cases. |
| "Hallucination là gì?" | Khi LLM bịa thông tin không có trong context. Chúng tôi giảm thiểu bằng explicit constraint trong prompt và mandatory citations. |
