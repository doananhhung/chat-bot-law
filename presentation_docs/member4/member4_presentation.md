# 🎤 Member 4: Frontend, Database & Demo - Tài Liệu Thuyết Trình

> **Thời lượng:** ~8-10 phút | **Vai trò:** UI, Persistence, Demo thực tế & Tổng kết

---

# PHẦN 1: STREAMLIT UI (2 phút)

## 📽️ SLIDE 1.1: Tiêu đề phần

| Nội dung trình chiếu |
|---------------------|
| **Frontend, Database & Live Demo** |
| *Trải nghiệm người dùng thực tế* |
| --- |
| 👤 Member 4 |

### 🎙️ Script:

> "Xin chào, tôi là Member 4. Sau khi các thành viên đã giải thích backend, tôi sẽ trình bày về **giao diện người dùng, cách lưu trữ dữ liệu**, và cuối cùng sẽ **demo thực tế** hệ thống.
>
> Đây là phần các bạn sẽ thấy sản phẩm hoạt động thực sự."

---

## 📽️ SLIDE 1.2: Tại sao chọn Streamlit?

| Đặc điểm | Lợi ích |
|----------|---------|
| **Pure Python** | Không cần JavaScript, HTML, CSS |
| **Hot reload** | Code thay đổi → UI update ngay |
| **Chat components** | `st.chat_input`, `st.chat_message` có sẵn |
| **Session state** | Quản lý state dễ dàng |
| **Widgets** | Buttons, sliders, expanders... built-in |

```python
# Chỉ cần vài dòng Python để tạo chat UI
import streamlit as st

st.title("🤖 Trợ lý AI")

if prompt := st.chat_input("Nhập câu hỏi..."):
    with st.chat_message("user"):
        st.markdown(prompt)
```

### 🎙️ Script:

> "Chúng tôi chọn **Streamlit** vì nhiều lý do:
>
> **Pure Python**: Team AI thường quen Python, không cần học thêm JavaScript.
>
> **Chat components có sẵn**: `st.chat_input` và `st.chat_message` built-in, không cần tự implement.
>
> **Hot reload**: Khi sửa code, UI update ngay lập tức, rất tiện khi develop.
>
> Chỉ với khoảng 300 dòng code Python, chúng tôi có một chat interface hoàn chỉnh."

---

## 📽️ SLIDE 1.3: Layout giao diện

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 Trợ lý AI Tra cứu Pháp Luật                            │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  SIDEBAR         │           MAIN CHAT AREA                 │
│                  │                                          │
│  ➕ Cuộc hội     │  👤 User: Thai sản nghỉ mấy tháng?      │
│  thoại mới       │                                          │
│                  │  🤖 AI: Theo Điều 139...                │
│  ─────────       │         📚 Nguồn tham khảo              │
│  Gần đây         │             └─ [expandable]             │
│  💬 Session 1    │                                          │
│  💬 Session 2    │  ─────────────────────────────────────── │
│                  │                                          │
│  ⚙️ Quản lý     │  💬 Nhập câu hỏi của bạn...             │
│  ⚡ Chế độ TK    │                                          │
│                  │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

### 🎙️ Script:

> "Giao diện chia làm 2 phần chính:
>
> **Sidebar bên trái**: Quản lý hội thoại - tạo mới, chuyển đổi, xóa session. Có thêm phần quản lý dữ liệu và chọn chế độ tìm kiếm.
>
> **Main area bên phải**: Khu vực chat chính. Hiển thị lịch sử tin nhắn, câu trả lời của AI kèm nguồn tham khảo có thể expand.
>
> Bên dưới là input box để nhập câu hỏi mới."

---

## 📽️ SLIDE 1.4: Các tính năng UI

| Tính năng | Mô tả |
|-----------|-------|
| **Session Management** | Tạo mới, chuyển đổi, xóa hội thoại |
| **Source Display** | Expandable panel hiển thị nguồn trích dẫn |
| **Context Understanding** | Hiển thị câu hỏi đã được viết lại |
| **Search Mode** | Chọn quality/balanced/speed |
| **Data Update** | Button cập nhật index khi có luật mới |

```python
# Hiển thị nguồn tham khảo
with st.expander("📚 Nguồn tham khảo"):
    for doc in sources:
        st.caption(f"📄 {doc.source} (Trang {doc.page})")
        st.text(doc.content[:300] + "...")

# Hiển thị query rewriting
with st.expander("🧠 Tư duy ngữ cảnh"):
    st.info(f"AI đã hiểu: **{standalone_query}**")
```

### 🎙️ Script:

> "Một số tính năng UI đáng chú ý:
>
> **Session Management**: Mỗi cuộc trò chuyện là một session riêng. User có thể tạo mới, quay lại session cũ, hoặc xóa.
>
> **Source Display**: Nguồn tham khảo được hiển thị trong expandable panel. User có thể click để xem chi tiết.
>
> **Context Understanding**: Khi hỏi follow-up, user có thể xem AI đã hiểu câu hỏi thành gì.
>
> **Search Mode**: Cho phép user chọn giữa accuracy cao vs tốc độ nhanh."

---

# PHẦN 2: DATABASE PERSISTENCE (2 phút)

## 📽️ SLIDE 2.1: Tại sao cần Database?

```
Không có Database:
──────────────────
User chat → Close browser → Mất hết lịch sử 😢

Có Database:
────────────
User chat → Close browser → Reopen → Thấy lại lịch sử ✅
```

| Mục đích | Giải thích |
|----------|------------|
| **Persistence** | Lưu trữ lịch sử chat qua các session |
| **Resume** | User có thể tiếp tục hội thoại cũ |
| **Analysis** | Có thể phân tích câu hỏi thường gặp |

### 🎙️ Script:

> "Tại sao cần database? Đơn giản: **để lưu lịch sử**.
>
> Không có database, mỗi lần user đóng browser là mất hết. Rất frustrating.
>
> Với database, user có thể đóng trình duyệt, hôm sau quay lại vẫn thấy các cuộc hội thoại trước.
>
> Ngoài ra, data lưu lại còn phục vụ phân tích - xem user hỏi gì nhiều nhất, để cải thiện hệ thống."

---

## 📽️ SLIDE 2.2: Database Schema

```
┌─────────────────────────┐       ┌─────────────────────────┐
│      ChatSession        │       │      ChatMessage        │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │───┐   │ id (PK)                 │
│ title                   │   │   │ session_id (FK)         │
│ created_at              │   └──►│ role ("user"/"assistant")│
│ updated_at              │  1:N  │ content                 │
└─────────────────────────┘       │ sources (JSON)          │
                                  │ standalone_query        │
                                  │ created_at              │
                                  └─────────────────────────┘
```

| Model | Fields | Mục đích |
|-------|--------|----------|
| **ChatSession** | id, title, timestamps | Một cuộc hội thoại |
| **ChatMessage** | role, content, sources | Một tin nhắn trong hội thoại |

### 🎙️ Script:

> "Schema rất đơn giản với 2 bảng:
>
> **ChatSession**: Đại diện cho một cuộc hội thoại. Có ID, tiêu đề (tự động từ tin nhắn đầu), và timestamps.
>
> **ChatMessage**: Mỗi tin nhắn trong session. Có role (user hoặc assistant), nội dung, và quan trọng là **sources** - lưu nguồn trích dẫn dưới dạng JSON.
>
> Relationship là 1:N - một session có nhiều messages."

---

## 📽️ SLIDE 2.3: Repository Pattern

```python
# src/database/repository.py
class ChatRepository:
    def create_session(self, title: str) -> ChatSession:
        """Tạo hội thoại mới."""
        
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Lấy tất cả tin nhắn của một session."""
        
    def add_message(self, session_id, role, content, sources):
        """Thêm tin nhắn mới."""
        
    def delete_session(self, session_id: str):
        """Xóa hội thoại (cascade delete messages)."""
```

| Pattern | Lợi ích |
|---------|---------|
| **Centralized** | Tất cả DB logic ở một nơi |
| **Abstraction** | UI không cần biết SQL details |
| **Testable** | Dễ dàng mock cho testing |

### 🎙️ Script:

> "Chúng tôi dùng **Repository Pattern** - một layer abstraction trên database.
>
> **ChatRepository** cung cấp các methods như `create_session`, `get_messages`, `add_message`.
>
> UI layer chỉ cần gọi `repo.add_message(...)`, không cần biết SQL như thế nào bên dưới.
>
> Pattern này giúp code clean hơn và dễ test hơn."

---

# PHẦN 3: PERFORMANCE OPTIMIZATION (2 phút)

## 📽️ SLIDE 3.1: Cold Start Problem

```
Vấn đề:
───────
User opens app
    └── Load Embedding Model (~17s) ← CHẬM!
        └── Load FAISS Index (~0.5s)
            └── Initialize LLMs (~1s)
                └── Ready to chat (~18.5s total)

Mỗi lần reload page: 18.5s lại delay!

Giải pháp: @st.cache_resource
────────────────────────────
First load: 17s (unavoidable)
Subsequent loads: < 1s ✅
```

### 🎙️ Script:

> "Một vấn đề lớn với AI apps là **cold start**.
>
> Embedding model nặng 1.5GB. Load lần đầu mất 17 giây. Nếu mỗi lần reload page đều phải load lại, user experience sẽ rất tệ.
>
> Giải pháp là **caching**. Streamlit có decorator `@st.cache_resource` - load model một lần, cache trong memory.
>
> Kết quả: Lần đầu vẫn 17 giây, nhưng reload sau đó chỉ dưới 1 giây."

---

## 📽️ SLIDE 3.2: Caching Strategy

```python
# app.py
@st.cache_resource(show_spinner="Đang khởi động...")
def get_retriever():
    """Load ONCE, reuse forever."""
    return SemanticRetriever()  # Load embedding + FAISS

@st.cache_resource
def get_rag_chain():
    """Load ONCE, reuse across all users."""
    retriever = get_retriever()
    return RAGChain(retriever)  # Initialize LLMs
```

| What's Cached | Size | Load Time |
|---------------|------|-----------|
| Embedding Model | ~1.5 GB | ~15s |
| FAISS Index | ~10 MB | ~0.5s |
| LLM Connections | ~100 MB | ~1s |

### 🎙️ Script:

> "Đây là code caching:
>
> `get_retriever()` load embedding model và FAISS index. Được cache, chỉ chạy một lần.
>
> `get_rag_chain()` tạo RAG chain với LLM connections. Cũng được cache.
>
> Kết quả: **First load ~17s, subsequent loads <1s**. Trải nghiệm user smooth hơn nhiều."

---

## 📽️ SLIDE 3.3: Stateless Design

```
❌ Stateful (Cannot cache):
──────────────────────────
class RAGChain:
    def __init__(self):
        self.history = []  # State stored inside
    
    def answer(self, query):
        # Uses internal history

✅ Stateless (Can cache):
─────────────────────────
class RAGChain:
    def __init__(self):
        pass  # No internal state
    
    def answer(self, query, history_str):  # History injected
        # Uses externally provided history
```

### 🎙️ Script:

> "Để caching hoạt động, RAGChain phải là **stateless**.
>
> Nếu RAGChain lưu history bên trong, mỗi user cần một instance riêng, không thể share.
>
> Thiết kế của chúng tôi: RAGChain **không lưu state**. History được pass vào từ bên ngoài mỗi lần gọi.
>
> Nhờ vậy, một RAGChain instance có thể phục vụ tất cả users."

---

# PHẦN 4: LIVE DEMO (3 phút)

## 📽️ SLIDE 4.1: Demo Flow

| Bước | Nội dung | Mục đích |
|------|----------|----------|
| 1 | Giới thiệu giao diện | Show layout |
| 2 | Câu hỏi pháp lý đầu tiên | Show RAG + citations |
| 3 | Follow-up question | Show query rewriting |
| 4 | General chat | Show intent routing |
| 5 | Session management | Show persistence |

### 🎙️ Script:

> "Bây giờ tôi sẽ demo thực tế hệ thống.
>
> Tôi sẽ show 5 tình huống: Câu hỏi pháp lý, follow-up, chat xã giao, và quản lý session."

---

## 📽️ SLIDE 4.2: Demo - Câu hỏi pháp lý

**Câu hỏi demo:**
```
Thai sản được nghỉ bao nhiêu ngày?
```

**Kỳ vọng:**
- AI trả lời theo cấu trúc IRAC
- Có trích dẫn nguồn (file, trang)
- Response time ~1-2s

### 🎙️ Script (khi demo):

> "Tôi sẽ hỏi một câu về luật lao động: 'Thai sản được nghỉ bao nhiêu ngày?'
>
> ... [đợi response] ...
>
> Như các bạn thấy, AI đã trả lời với cấu trúc: Căn cứ pháp lý, Phân tích, Kết luận.
>
> Click vào 'Nguồn tham khảo' - đây là file và trang cụ thể. User có thể verify."

---

## 📽️ SLIDE 4.3: Demo - Follow-up Question

**Câu hỏi demo:**
```
Còn nam thì sao?
```

**Kỳ vọng:**
- AI hiểu context "nam" là "lao động nam"
- Expand "Tư duy ngữ cảnh" để xem query đã được rewrite

### 🎙️ Script (khi demo):

> "Bây giờ tôi hỏi tiếp: 'Còn nam thì sao?'
>
> Câu này rất ngắn, nhưng AI cần hiểu context là đang nói về thai sản.
>
> ... [đợi response] ...
>
> Click vào 'Tư duy ngữ cảnh' - AI đã hiểu câu hỏi thành 'Lao động nam có được nghỉ thai sản không?' Đây là Query Rewriting hoạt động."

---

## 📽️ SLIDE 4.4: Demo - General Chat

**Câu hỏi demo:**
```
Xin chào, tên tôi là Hùng
```

**Kỳ vọng:**
- AI không search database (GENERAL intent)
- Trả lời thân thiện

**Câu hỏi tiếp theo:**
```
Tên tôi là gì?
```

**Kỳ vọng:**
- AI nhớ context, trả lời "Hùng"

### 🎙️ Script (khi demo):

> "Thử chat xã giao: 'Xin chào, tên tôi là Hùng'
>
> ... [đợi response] ...
>
> AI chào lại thân thiện, không cố search luật. Intent Router đã phân loại đây là GENERAL.
>
> Hỏi tiếp: 'Tên tôi là gì?'
>
> ... [đợi response] ...
>
> AI nhớ được tên 'Hùng' từ context trước. Conversational memory hoạt động."

---

## 📽️ SLIDE 4.5: Demo - Session Management

**Thao tác:**
1. Click "➕ Cuộc hội thoại mới"
2. Click quay lại session cũ
3. Thấy lịch sử vẫn còn

### 🎙️ Script (khi demo):

> "Cuối cùng, demo session management.
>
> Click 'Cuộc hội thoại mới' - tạo session mới, chat area trống.
>
> Click quay lại session cũ trong sidebar - lịch sử chat vẫn còn đầy đủ.
>
> Tất cả được lưu trong SQLite database."

---

# PHẦN 5: TỔNG KẾT TOÀN BỘ (1 phút)

## 📽️ SLIDE 5.1: Recap hệ thống

| Thành phần | Người trình bày | Key Points |
|------------|-----------------|------------|
| **Kiến trúc** | Member 1 | RAG, Modular Monolith |
| **Data Ingestion** | Member 2 | Load, Split, Embed, Index |
| **RAG Engine** | Member 3 | Semantic Search, Prompts |
| **Frontend & DB** | Member 4 | Streamlit, SQLite, Caching |

### 🎙️ Script:

> "Tổng kết toàn bộ buổi thuyết trình:
>
> **Member 1** đã giới thiệu kiến trúc RAG và tổng quan hệ thống.
>
> **Member 2** giải thích cách chuyển PDF thành searchable data.
>
> **Member 3** trình bày core RAG logic và prompt engineering.
>
> **Member 4** - phần của tôi - cover UI, database, và demo thực tế."

---

## 📽️ SLIDE 5.2: Kết quả đạt được

| Metric | Kết quả |
|--------|---------|
| **Response Time** | ~1-2 giây |
| **Accuracy** | Có trích dẫn nguồn verify được |
| **User Experience** | Chat tự nhiên, nhớ context |
| **Maintainability** | Cập nhật luật mới dễ dàng |

### 🎙️ Script:

> "Kết quả đạt được:
>
> **Tốc độ**: Response trong 1-2 giây, phù hợp chat experience.
>
> **Accuracy**: Mọi câu trả lời đều có nguồn để verify, giảm hallucination.
>
> **UX**: Chat tự nhiên, hiểu follow-up, nhớ context.
>
> **Maintainability**: Thêm luật mới chỉ cần copy PDF vào folder và click update."

---

## 📽️ SLIDE 5.3: Q&A

| Nội dung |
|----------|
| **❓ Câu hỏi & Thảo luận** |
| Mời mọi người đặt câu hỏi |
| --- |
| 🙏 Cảm ơn đã lắng nghe! |

### 🎙️ Script:

> "Đó là toàn bộ phần thuyết trình của nhóm chúng tôi.
>
> Bây giờ xin mời mọi người đặt câu hỏi. Tất cả thành viên sẽ sẵn sàng trả lời.
>
> Cảm ơn mọi người đã lắng nghe!"

---

# 📋 CHECKLIST CHUẨN BỊ DEMO

- [ ] Chạy app trước 5 phút để warm up cache
- [ ] Verify `.env` file có API key valid
- [ ] Test thử các câu hỏi demo
- [ ] Chuẩn bị backup plan nếu API fail
- [ ] Check internet connection
- [ ] Tắt notifications trên máy

---

# ❓ CÂU HỎI CÓ THỂ GẶP

| Câu hỏi | Gợi ý trả lời |
|---------|---------------|
| "Tại sao dùng SQLite thay vì PostgreSQL?" | SQLite đủ cho MVP, zero config, file-based. Có thể migrate sau nếu cần scale. |
| "Cold start 17s có chấp nhận được không?" | Chỉ xảy ra lần đầu. Production có thể dùng pre-warming strategies. |
| "Streamlit có scale được không?" | Cho demo/internal tool thì OK. Production lớn nên dùng React/Vue. |
| "Nếu API fail thì sao?" | Hiện có error handling hiển thị message. Có thể improve với retry logic và fallback provider. |

---

# 🔧 BACKUP PLAN

Nếu demo gặp vấn đề:

| Vấn đề | Giải pháp |
|--------|-----------|
| **App không start** | Chạy `pip install -r requirements.txt` lại |
| **API timeout** | Đổi sang provider khác trong `.env` |
| **No response** | Restart app: `Ctrl+C` rồi `streamlit run app.py` |
| **Internet mất** | Chuẩn bị screenshots/video backup |
