# Quản lý Trạng thái Giao diện (Streamlit State Management)

Streamlit hoạt động theo cơ chế chạy lại toàn bộ script (Rerun) mỗi khi có tương tác. Do đó, việc quản lý State là cực kỳ quan trọng để app không bị "quên" dữ liệu.

## Sơ đồ Luồng Cập nhật UI

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant UI as Streamlit App
    participant State as st.session_state
    participant Backend as RAG Engine
    participant DB as Database

    U->>UI: Nhập text + Enter
    UI->>UI: Streamlit phát hiện sự kiện

    Note over UI: Script Rerun bắt đầu

    UI->>State: Kiểm tra session_state.messages
    State-->>UI: Trả về lịch sử tin nhắn cũ
    UI->>UI: Vẽ lại toàn bộ tin nhắn cũ

    UI->>UI: Hiển thị Spinner "AI đang suy nghĩ..."
    UI->>Backend: Gọi xử lý RAG
    Backend-->>UI: Câu trả lời + Sources

    UI->>State: Append user message
    UI->>State: Append AI message
    UI->>DB: Lưu tin nhắn

    UI-->>U: Hiển thị kết quả mới

    opt Cần cập nhật Sidebar
        UI->>UI: st.rerun()
    end
```

```mermaid
flowchart TD
    subgraph SessionState["st.session_state"]
        A[messages: List]
        B[session_id: str]
        C[rag_chain: RAGChain]
        D[chat_repo: Repository]
    end

    subgraph Lifecycle["Vòng đời State"]
        E[App Start] --> F{State exists?}
        F -->|No| G[Initialize defaults]
        F -->|Yes| H[Preserve existing]
        G --> I[Ready]
        H --> I
    end

    subgraph Events["User Events"]
        J[Nhập tin nhắn] --> K[Append to messages]
        L[Chọn phiên cũ] --> M[Replace messages]
        N[New Chat] --> O[Clear messages]
    end
```

## Các biến Session State quan trọng

| Tên biến | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `messages` | `List[Dict]` | Lưu danh sách tin nhắn đang hiển thị trên màn hình chat hiện tại. |
| `session_id` | `str` | ID của phiên chat đang kích hoạt. Nếu `None` tức là đang ở trạng thái chờ tạo mới. |
| `uploaded_file` | `FileUploader` | Trạng thái của file tạm thời được upload (nếu có tính năng upload). |

## Luồng cập nhật UI

1.  **User Input**: Người dùng nhập text -> Nhấn Enter.
2.  **Callback**: Streamlit phát hiện sự kiện -> Rerun `app.py`.
3.  **Render History**:
    *   Kiểm tra `st.session_state.messages`.
    *   Vẽ lại toàn bộ tin nhắn cũ.
4.  **Processing**:
    *   Hiển thị Spinner ("AI đang suy nghĩ...").
    *   Gọi Backend xử lý.
5.  **Append New Message**:
    *   Thêm câu hỏi user vào `st.session_state.messages`.
    *   Thêm câu trả lời AI vào `st.session_state.messages`.
6.  **Rerun (Optional)**: Đôi khi cần `st.rerun()` để cập nhật lại tiêu đề hoặc sidebar ngay lập tức.
