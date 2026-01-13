# Thiết lập Môi trường Phát triển (Local Development)

Hướng dẫn này giúp bạn cài đặt dự án trên máy cá nhân (Windows/Mac/Linux) để bắt đầu code.

## 1. Chuẩn bị (Prerequisites)
*   **Python**: Phiên bản 3.10 trở lên. Kiểm tra bằng `python --version`.
*   **Git**: Để quản lý mã nguồn.
*   **VS Code** (Khuyên dùng): Cài thêm extension "Python" và "Pylance".

## 2. Cài đặt chi tiết

### Bước 1: Clone Repository
```bash
git clone <URL_REPO>
cd chat-bot-law
```

### Bước 2: Tạo môi trường ảo (Virtual Environment)
Luôn luôn dùng venv để cô lập thư viện của dự án.
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies
```bash
pip install -r requirements.txt
```
*Lưu ý: Nếu gặp lỗi cài đặt thư viện `faiss` hay `huggingface`, hãy đảm bảo bạn đã cài **C++ Build Tools** (trên Windows).*

### Bước 4: Cấu hình biến môi trường
1.  Copy file mẫu: `cp .env.example .env` (hoặc copy paste thủ công).
2.  Điền API Key vào `.env`:
    *   `GOOGLE_API_KEY`: Lấy tại [Google AI Studio](https://aistudio.google.com/).
    *   `GROQ_API_KEY`: Lấy tại [Groq Console](https://console.groq.com/).

### Bước 5: Chuẩn bị dữ liệu mẫu
1.  Tạo thư mục: `mkdir -p data/raw`
2.  Copy một vài file PDF luật (ví dụ: Luật Lao Động) vào đó.

### Bước 6: Chạy ứng dụng
```bash
streamlit run app.py
```
Truy cập `http://localhost:8501`.

## Debugging trong VS Code
Để debug (đặt breakpoint), bạn cần tạo file `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Streamlit",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "args": [
                "run",
                "${workspaceFolder}/app.py"
            ]
        }
    ]
}
```
Sau đó nhấn F5 để bắt đầu Debug.
