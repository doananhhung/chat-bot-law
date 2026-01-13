# AI Legal Assistant (Trợ lý Luật Lao Động)

Hệ thống Chatbot tra cứu pháp luật thông minh sử dụng kỹ thuật **RAG (Retrieval-Augmented Generation)**, cho phép trả lời câu hỏi pháp lý dựa trên văn bản luật với độ chính xác cao và trích dẫn nguồn cụ thể.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-v0.1-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Database](https://img.shields.io/badge/DB-SQLite-lightgrey)

---

## 🚀 Tính năng nổi bật

*   **Tra cứu chính xác**: Sử dụng Vector Database (FAISS) để tìm kiếm ngữ nghĩa, không chỉ khớp từ khóa.
*   **Trích dẫn nguồn**: Mọi câu trả lời đều đi kèm trích dẫn văn bản luật (Tên file, Số trang) để người dùng kiểm chứng.
*   **Hội thoại thông minh**:
    *   **Nhớ ngữ cảnh**: Có thể hỏi tiếp (Follow-up questions) như "Nó áp dụng cho ai?".
    *   **Phân loại ý định**: Tự động nhận biết câu hỏi pháp lý hay giao tiếp xã giao.
*   **Quản lý lịch sử**:
    *   Lưu trữ toàn bộ lịch sử chat (Persistence) vào cơ sở dữ liệu.
    *   Tạo hội thoại mới, xem lại hội thoại cũ.
    *   Xóa hội thoại không cần thiết.
*   **Đa mô hình**: Hỗ trợ Google Gemini, Groq, Ollama.

---

## 🛠️ Cài đặt & Chạy

### 1. Yêu cầu hệ thống
*   Python 3.10 trở lên
*   Git

### 2. Cài đặt

1.  **Clone repository**:
    ```bash
    git clone <repo_url>
    cd chat-bot-law
    ```

2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Cấu hình môi trường**:
    *   Tạo file `.env` từ file mẫu:
        ```bash
        cp .env.example .env
        ```
    *   Cập nhật API Key trong `.env`:
        ```env
        GOOGLE_API_KEY=AIzaSy...
        # Hoặc dùng Groq
        GROQ_API_KEY=gsk_...
        ```

### 3. Chuẩn bị Dữ liệu

1.  Copy các file văn bản luật (PDF, DOCX) vào thư mục `data/raw/`.
2.  (Tùy chọn) Chạy lệnh khởi tạo dữ liệu mẫu nếu cần test nhanh.

### 4. Chạy Ứng dụng

1.  **Khởi động Web App**:
    ```bash
    streamlit run app.py
    ```

2.  **Sử dụng**:
    *   Truy cập địa chỉ hiển thị trên terminal (thường là `http://localhost:8501`).
    *   Trong lần chạy đầu tiên, nhấn **"Cập nhật Index"** ở Sidebar để hệ thống xử lý dữ liệu.

---

## 📂 Cấu trúc Dự án (Modular Monolith)

```text
project_root/
├── data/                   # Lưu trữ dữ liệu
│   ├── raw/                # File PDF/DOCX gốc
│   ├── vector_store/       # FAISS Index (Vector DB)
│   └── chat_history.db     # SQLite Database (Lịch sử chat)
├── src/
│   ├── config.py           # Quản lý cấu hình tập trung
│   ├── database/           # Persistent Layer (SQLAlchemy)
│   │   ├── models.py       # DB Schema
│   │   ├── repository.py   # CRUD Operations
│   │   └── engine.py       # DB Connection
│   ├── ingestion/          # ETL Pipeline (Load -> Split -> Embed)
│   ├── rag_engine/         # Core Logic (Retrieve -> Generate)
│   └── utils/              # Tiện ích chung
├── app.py                  # Streamlit UI Entry point
└── tests/                  # Unit & Integration Tests
```

## 🧠 Kiến trúc Kỹ thuật

1.  **Ingestion Layer**: Sử dụng `PyPDFLoader` và `RecursiveCharacterTextSplitter`.
2.  **Embedding**: Model `bkai-foundation-models/vietnamese-bi-encoder` (HuggingFace).
3.  **Storage**:
    *   Vector: FAISS (Local).
    *   Metadata: SQLite.
4.  **RAG Engine**:
    *   **Retrieval**: Semantic Search.
    *   **Generation**: Google Gemini Pro / Groq Llama 3.
    *   **Routing**: Phân loại Intent (Legal vs General).

---

## 🤝 Đóng góp

Vui lòng đọc `DEV_LOG.md` để hiểu lịch sử thay đổi và các quyết định kiến trúc (ADR) trước khi submit PR.
