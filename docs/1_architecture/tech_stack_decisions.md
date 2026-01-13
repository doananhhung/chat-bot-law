# Quyết định Công nghệ (Tech Stack Decisions)

Tài liệu này giải thích lý do tại sao các công nghệ cụ thể được chọn cho dự án, cùng với các ưu nhược điểm của chúng.

## 1. Ngôn ngữ & Framework
*   **Python 3.10+**: Ngôn ngữ tiêu chuẩn của AI/Data Science.
*   **Streamlit**:
    *   *Lý do*: Phát triển UI cực nhanh (Rapid Prototyping), tích hợp tốt với Python.
    *   *Đánh đổi*: Khó tùy biến giao diện sâu (CSS/JS) so với React/Vue, nhưng đủ cho ứng dụng nội bộ/MVP.
*   **LangChain**: Framework mạnh mẽ để kết nối LLM, Vector DB và Data Sources.

## 2. Large Language Model (LLM)
*   **Google Gemini (Pro/Flash)**:
    *   *Lý do*: Miễn phí (với giới hạn), cửa sổ ngữ cảnh (Context Window) lớn (từ 128k đến 1M tokens), xử lý tiếng Việt rất tốt.
*   **Groq (Llama 3 / Mixtral)**:
    *   *Lý do*: Tốc độ siêu nhanh (gần như realtime), phù hợp cho các tác vụ Router hoặc tóm tắt nhanh.

## 3. RAG Components
*   **Embedding Model: `bkai-foundation-models/vietnamese-bi-encoder`**:
    *   *Lý do*: Được train riêng cho tiếng Việt, hiệu năng tốt hơn nhiều so với `openai-ada-002` hay `huggingface-bert` gốc khi xử lý văn bản pháp luật VN.
*   **Vector Database: FAISS (CPU version)**:
    *   *Lý do*: Thư viện của Facebook, chạy local cực nhẹ, không cần setup server riêng (như Qdrant/Milvus). Phù hợp cho bộ dữ liệu luật < 10GB.
    *   *Định hướng*: Nếu dữ liệu lớn > 100GB, sẽ chuyển sang Qdrant Cloud.

## 4. Database
*   **SQLite**:
    *   *Lý do*: Serverless, file-based, không cần cài đặt. Đủ sức chứa lịch sử chat cho nhóm nhỏ.
    *   *ORM*: **SQLAlchemy** được dùng để trừu tượng hóa DB. Điều này giúp việc chuyển đổi sang PostgreSQL sau này chỉ cần đổi chuỗi kết nối (`DATABASE_URL`).
