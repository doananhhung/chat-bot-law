# Vòng đời Chat Session & Database Lifecycle

Tài liệu này giải thích cách dữ liệu hội thoại được khởi tạo, lưu trữ và truy xuất.

## Sơ đồ Tổng quan

```mermaid
stateDiagram-v2
    [*] --> AppStart: Khởi động ứng dụng
    AppStart --> CheckDB: Kiểm tra DB

    state CheckDB <<choice>>
    CheckDB --> CreateTables: Chưa có DB
    CheckDB --> Ready: DB đã tồn tại
    CreateTables --> Ready

    Ready --> NewSession: User bấm "New Chat"
    Ready --> LoadSession: User chọn phiên cũ

    NewSession --> ActiveSession: Tạo UUID mới
    LoadSession --> ActiveSession: Load messages

    ActiveSession --> SaveMessage: User/AI gửi tin nhắn
    SaveMessage --> ActiveSession

    ActiveSession --> DeleteSession: User xóa phiên
    DeleteSession --> Ready
```

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant UI as Streamlit UI
    participant State as Session State
    participant Repo as ChatRepository
    participant DB as SQLite Database

    Note over UI,DB: 1. Khởi tạo Ứng dụng
    UI->>Repo: init_db()
    Repo->>DB: CREATE TABLE IF NOT EXISTS
    DB-->>Repo: OK
    Repo-->>UI: Database ready

    Note over UI,DB: 2. Tạo Phiên Chat Mới
    U->>UI: Bấm "New Chat"
    UI->>Repo: create_session()
    Repo->>DB: INSERT INTO chat_sessions
    DB-->>Repo: session_id (UUID)
    Repo-->>UI: Session object
    UI->>State: session_id = new_id

    Note over UI,DB: 3. Lưu Tin nhắn
    U->>UI: Gửi câu hỏi
    UI->>Repo: add_message(session_id, "user", content)
    Repo->>DB: INSERT INTO chat_messages
    UI->>UI: Xử lý RAG...
    UI->>Repo: add_message(session_id, "assistant", answer, sources)
    Repo->>DB: INSERT INTO chat_messages

    Note over UI,DB: 4. Tải Lịch sử
    U->>UI: Chọn phiên cũ từ Sidebar
    UI->>Repo: get_messages(session_id)
    Repo->>DB: SELECT * FROM chat_messages WHERE session_id=?
    DB-->>Repo: List[Message]
    Repo-->>UI: Messages
    UI->>State: messages = loaded_messages
    UI-->>U: Hiển thị lịch sử chat
```

## 1. Khởi tạo Ứng dụng (App Initialization)
Khi ứng dụng khởi động (`app.py`):
1.  Gọi `init_db()` từ `src.database.engine`.
2.  Kiểm tra file `chat_history.db`.
3.  Nếu chưa có, dùng SQLAlchemy `Base.metadata.create_all()` để tạo bảng `chat_sessions` và `chat_messages`.

## 2. Tạo Phiên Chat Mới (New Session)
Khi người dùng bấm "New Chat" hoặc lần đầu vào app:
1.  Tạo một `session_id` mới (UUID).
2.  Tạo record mới trong bảng `chat_sessions`:
    *   `id`: UUID
    *   `created_at`: Thời gian hiện tại.
    *   `title`: Mặc định là "New Chat" (Sau này có thể cập nhật title dựa trên câu hỏi đầu tiên).

## 3. Lưu trữ Tin nhắn (Message Persistence)
Mỗi khi có một lượt hội thoại (Turn):

### User Message
*   Insert vào bảng `chat_messages`.
*   `role`: "user"
*   `content`: Câu hỏi người dùng.
*   `session_id`: ID của phiên hiện tại.

### Assistant Message
*   Insert vào bảng `chat_messages`.
*   `role`: "assistant"
*   `content`: Câu trả lời của AI.
*   `sources`: Lưu JSON list các nguồn tham khảo (Tên file, số trang).

## 4. Tải Lịch sử (Load History)
Khi người dùng chọn một phiên cũ từ Sidebar:
1.  Query bảng `chat_messages` với `WHERE session_id = selected_id`.
2.  Sắp xếp theo `created_at` tăng dần.
3.  Load dữ liệu vào `st.session_state.messages` để hiển thị lên UI.
