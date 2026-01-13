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

## 📚 Tài liệu & Hướng dẫn (Documentation)

Dự án này đi kèm với bộ tài liệu kỹ thuật chi tiết dành cho Developer:

*   **[Bắt đầu nhanh (Quick Start)](docs/4_guides/setup_local.md)**: Hướng dẫn cài đặt môi trường Local và chạy thử.
*   **[Kiến trúc hệ thống (Architecture)](docs/1_architecture/system_overview.md)**: Hiểu về luồng dữ liệu và thiết kế Modular Monolith.
*   **[Cơ chế hoạt động (Flows)](docs/index.md#2-luồng-hoạt-động-flows---quan-trọng)**: Giải thích sâu về RAG Pipeline, Ingestion Sync, và Database Lifecycle.

👉 **[Xem toàn bộ tài liệu tại đây (docs/)](docs/index.md)**

---

## 🛠️ Cài đặt nhanh

Vui lòng xem hướng dẫn chi tiết tại **[docs/4_guides/setup_local.md](docs/4_guides/setup_local.md)**.

Tóm tắt lệnh cho Windows:
```powershell
# 1. Clone & Setup Env
git clone <repo_url>
cd chat-bot-law
python -m venv venv
.\venv\Scripts\activate

# 2. Install Deps
pip install -r requirements.txt

# 3. Config
copy .env.example .env
# (Nhớ điền API Key vào .env)

# 4. Run
mkdir data\raw
# (Copy file PDF luật vào data\raw)
streamlit run app.py
```

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

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng đọc **[docs/index.md](docs/index.md)** để hiểu cấu trúc dự án trước khi submit Pull Request.

Lịch sử thay đổi và các quyết định kiến trúc quan trọng được ghi lại trong `DEV_LOG.md`.
