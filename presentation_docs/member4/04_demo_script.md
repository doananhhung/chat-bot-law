# 🎬 Demo Script - Hướng Dẫn Demo Thực Tế

## Mục tiêu
Hướng dẫn chi tiết cách demo ứng dụng AI Legal Assistant để showcase các tính năng chính.

---

## 1. Chuẩn Bị Demo

### 1.1 Requirements

```bash
# Đảm bảo đã cài đặt dependencies
pip install -r requirements.txt

# Đảm bảo có file .env với API keys
GROQ_API_KEY=...

# Đảm bảo có data trong data/raw/
# - Ít nhất 1 file PDF luật lao động
```

### 1.2 Pre-flight Check

```bash
# 1. Activate virtual environment
cd d:\heheboi\Project\chat-bot-law
.\venv\Scripts\activate

# 2. Run app
streamlit run app.py

# 3. Đợi cold start (~17s lần đầu)
```

---

## 2. Demo Flow (10 phút)

### 2.1 Giới Thiệu Giao Diện (1 phút)

**Nói**:
> "Đây là giao diện Streamlit của ứng dụng AI Legal Assistant. Giao diện chia làm 2 phần chính: Sidebar bên trái để quản lý hội thoại, và khu vực chat chính ở giữa."

**Thao tác**:
1. Point to sidebar: "Quản lý hội thoại"
2. Point to main area: "Chat với AI"
3. Point to title: "Trợ lý AI Tra cứu Pháp Luật"

---

### 2.2 Demo Câu Hỏi Pháp Lý (3 phút)

**Câu hỏi demo 1** - Basic legal query:
```
Thai sản được nghỉ bao nhiêu ngày?
```

**Nói**:
> "Bây giờ tôi sẽ hỏi một câu hỏi về luật lao động..."

**Thao tác**:
1. Nhập câu hỏi
2. Đợi response (~1-2s)
3. Highlight: "Như các bạn thấy, AI đã trả lời với cấu trúc IRAC..."
4. Click "📚 Nguồn tham khảo" để show citations
5. Point to page number: "Và có trích dẫn trang cụ thể để verify"

---

### 2.3 Demo Follow-up Question (2 phút)

**Câu hỏi demo 2** - Follow-up:
```
Còn nam thì sao?
```

**Nói**:
> "Bây giờ tôi sẽ hỏi câu follow-up. Câu hỏi này ngắn gọn, nhưng AI sẽ hiểu ngữ cảnh..."

**Thao tác**:
1. Nhập câu hỏi ngắn
2. Đợi response
3. Click "🧠 Tư duy ngữ cảnh"
4. Point to standalone query: "AI đã hiểu câu hỏi là về 'lao động nam có được nghỉ thai sản không'"
5. Explain: "Đây là tính năng Query Rewriting"

---

### 2.4 Demo General Chat (1 phút)

**Câu hỏi demo 3** - General:
```
Xin chào, tên tôi là Hùng
```

**Nói**:
> "Ngoài câu hỏi pháp lý, AI cũng có thể chat xã giao..."

**Thao tác**:
1. Nhập câu chào
2. Show AI responds friendly
3. Explain: "Intent Router đã phân loại đây là GENERAL, không cần search legal database"

**Câu hỏi demo 4** - Memory test:
```
Tên tôi là gì?
```

**Nói**:
> "AI nhớ ngữ cảnh trong cuộc hội thoại..."

---

### 2.5 Demo Session Management (1 phút)

**Thao tác**:
1. Click "➕ Cuộc hội thoại mới"
2. Explain: "Tạo session mới"
3. Click back to previous session
4. Explain: "Tất cả lịch sử được lưu trong database"

---

### 2.6 Demo Search Mode (IVF) (1 phút)

**Nói**:
> "Đối với hệ thống sử dụng IVF index, người dùng có thể điều chỉnh mode tìm kiếm..."

**Thao tác**:
1. Open "⚡ Chế độ tìm kiếm"
2. Show options: quality/balanced/speed
3. Explain: "Quality = search nhiều clusters hơn, chính xác hơn nhưng chậm hơn"
4. Switch mode, show percentage change

---

### 2.7 Demo Data Update (1 phút)

**Nói**:
> "Khi có văn bản luật mới, chỉ cần copy file PDF vào thư mục data/raw và click update..."

**Thao tác**:
1. Open "⚙️ Quản lý Dữ liệu"
2. Show path: `data/raw`
3. Click "🔄 Cập nhật Index" (if safe to demo)
4. Explain: "Hệ thống sẽ tự động detect file mới và chỉ index những file thay đổi"

---

## 3. Demo Queries Cheat Sheet

### 3.1 Câu Hỏi Pháp Lý (LEGAL)

| Query | Expected Behavior |
|-------|-------------------|
| "Thai sản được nghỉ bao nhiêu ngày?" | RAG + cited answer |
| "Hợp đồng lao động cần những gì?" | RAG + multiple sources |
| "Điều 139 nói gì?" | Direct article lookup |
| "Thử việc tối đa bao lâu?" | RAG search |

### 3.2 Follow-up Queries

| After | Query | Expected |
|-------|-------|----------|
| Thai sản | "Còn nam thì sao?" | Query rewrite visible |
| Thai sản | "Nếu sinh đôi?" | Context understood |

### 3.3 General Chat (GENERAL)

| Query | Expected |
|-------|----------|
| "Xin chào" | Friendly greeting |
| "Tên tôi là Hùng" | Acknowledged |
| "Tên tôi là gì?" | Remembers "Hùng" |
| "1 + 1 = ?" | Math answer (skip RAG) |

---

## 4. Potential Issues & Handling

### 4.1 Slow First Load

**Nếu xảy ra**: "Đang khởi động Model & Index..." quá lâu

**Giải thích**:
> "Lần đầu load embedding model mất khoảng 17s vì phải download ~1.5GB model weights. Sau đó sẽ cached và load rất nhanh."

### 4.2 API Error

**Nếu xảy ra**: "Max retries exceeded" hoặc connection error

**Giải thích**:
> "Có thể do rate limit từ Groq API. Đợi vài giây rồi thử lại."

### 4.3 No Sources Found

**Nếu xảy ra**: "Tôi không tìm thấy tài liệu..."

**Giải thích**:
> "Đây là behavior đúng! Nếu không có tài liệu liên quan trong database, AI sẽ thành thật nói không tìm thấy thay vì bịa thông tin."

---

## 5. Q&A Preparation

### 5.1 Các câu hỏi có thể gặp

| Question | Answer |
|----------|--------|
| "Tại sao dùng Groq thay vì OpenAI?" | Groq nhanh hơn (LPU), free tier generous |
| "Có hỗ trợ nhiều ngôn ngữ không?" | Embedding model optimize cho Vietnamese, nhưng LLM multilingual |
| "Dữ liệu có bị gửi ra ngoài không?" | Embedding local, chỉ query gửi đến LLM API |
| "Có thể deploy lên cloud không?" | Có, Streamlit Cloud hoặc Docker |

### 5.2 Follow-up Demo Requests

Nếu có yêu cầu demo thêm:

| Request | How to Demo |
|---------|-------------|
| "Delete session" | Click ✕ button |
| "Clear all data" | 🔥 Xóa toàn bộ |
| "Show database" | Open data/chat_history.db in SQLite viewer |
| "Show FAISS index" | Explain files in data/vector_store/ |

---

## 6. Closing Demo

**Nói**:
> "Tóm lại, AI Legal Assistant là chatbot RAG-based với các tính năng chính:
> 1. Tìm kiếm ngữ nghĩa - hiểu ý nghĩa câu hỏi
> 2. Trích dẫn nguồn - verify được
> 3. Conversational - nhớ ngữ cảnh
> 4. Dễ cập nhật - chỉ cần copy PDF mới
> 
> Cảm ơn đã theo dõi. Có câu hỏi gì không?"

---

## 7. Demo Recording Tips

Nếu cần record demo:

1. **Resolution**: 1920x1080 recommended
2. **Speed**: Nói chậm, đợi response hiển thị hết
3. **Mouse**: Di chuyển chậm, highlight khu vực quan trọng
4. **Audio**: Đảm bảo clear, không background noise
5. **Length**: Target 5-8 minutes

---

## Tài liệu liên quan
- [Streamlit UI](./01_streamlit_ui.md)
- [Performance Optimization](./03_performance_optimization.md)
