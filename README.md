# AI Legal Assistant (RAG System)

Hệ thống Chatbot tra cứu pháp luật sử dụng kỹ thuật RAG (Retrieval-Augmented Generation) với Google Gemini API.

## 🚀 Cài đặt & Chạy

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên
- Git

### 2. Cài đặt

1.  **Clone repository** (nếu chưa):
    ```bash
    git clone <repo_url>
    cd chat-bot-law
    ```

2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Cấu hình môi trường**:
    - Tạo file `.env` từ file mẫu:
      ```bash
      cp .env.example .env
      ```
    - Mở file `.env` và điền `GOOGLE_API_KEY` của bạn vào.
      ```env
      GOOGLE_API_KEY=AIzaSy...
      ```

### 3. Chuẩn bị Dữ liệu

1.  Copy các file PDF hoặc DOCX văn bản luật vào thư mục `data/raw/`.
2.  (Tùy chọn) Chạy script tạo dữ liệu giả lập để test:
    ```bash
    python scripts/create_test_data.py
    ```

### 4. Chạy Ứng dụng

1.  **Khởi động Web App**:
    ```bash
    streamlit run app.py
    ```

2.  **Trên giao diện Web**:
    - Nhấn nút **"Cập nhật Dữ liệu (Re-index)"** ở thanh bên trái để hệ thống đọc và xử lý tài liệu lần đầu.
    - Nhập câu hỏi vào khung chat.

## 📂 Cấu trúc Dự án

- `src/`: Mã nguồn chính
  - `ingestion/`: Module xử lý dữ liệu (Load, Split, Index).
  - `rag_engine/`: Module RAG (Retrieve, Generate).
- `data/`:
  - `raw/`: Chứa file gốc.
  - `vector_store/`: Chứa dữ liệu đã xử lý (FAISS index).
- `app.py`: Giao diện chính (Streamlit).

## ⚠️ Lưu ý
- Nếu gặp lỗi `Google GenAI Error`, hãy kiểm tra lại API Key trong `.env`.
- Lần đầu chạy Re-index sẽ tốn thời gian để tải model Embedding (~500MB).