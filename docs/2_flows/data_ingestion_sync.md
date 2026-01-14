# Quy trình Nạp & Đồng bộ Dữ liệu (Data Ingestion)

Tài liệu này giải thích cách hệ thống chuyển đổi văn bản luật (PDF/DOCX) thành Vector để tìm kiếm.

## Luồng xử lý (Workflow)

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant UI as Streamlit UI
    participant Scan as File Scanner
    participant Meta as MetadataStore (SQLite)
    participant Proc as Document Processor
    participant Embed as Embedding Model
    participant VDB as FAISS Vector DB

    U->>UI: Nhấn "Cập nhật Index"
    UI->>Scan: Quét thư mục data/raw/
    Scan->>Scan: Tính hash MD5/SHA256 cho từng file
    Scan->>Meta: Lấy trạng thái cũ

    Note over Scan,Meta: So sánh và phân loại

    loop Với mỗi file
        alt File mới (chưa có trong DB)
            Scan->>Proc: Xử lý mới
        else File đã sửa (hash khác)
            Scan->>Proc: Cập nhật lại
        else File không đổi (hash trùng)
            Scan->>Scan: Bỏ qua
        end
    end

    Proc->>Proc: Load (PyPDFLoader/Docx2txtLoader)
    Proc->>Proc: Split (RecursiveCharacterTextSplitter)
    Proc->>Embed: Chuyển text thành vector
    Embed->>VDB: Thêm vectors vào index
    VDB->>VDB: Lưu index.faiss + index.pkl
    Meta->>Meta: Cập nhật metadata

    VDB-->>UI: Hoàn thành
    UI-->>U: Báo cáo kết quả
```

```mermaid
flowchart LR
    subgraph Input
        A[PDF/DOCX Files]
    end

    subgraph Processing
        B[File Loader] --> C[Text Splitter]
        C --> D[Embedding Model]
    end

    subgraph Output
        E[(FAISS Index)]
        F[(Metadata JSON)]
    end

    A --> B
    D --> E
    D --> F
```

### 1. Trigger
Quá trình này được kích hoạt khi người dùng nhấn nút **"Cập nhật Index"** trên giao diện Streamlit hoặc chạy script `ingest.py`.

### 2. Quét file (Scanning)
*   Hệ thống quét thư mục `data/raw`.
*   Lọc các file có đuôi `.pdf`, `.docx`, `.doc`.

### 3. Kiểm tra thay đổi (Incremental Check)
*   Sử dụng `MetadataStore` (SQLite) để lưu hash (MD5/SHA256) của các file đã xử lý.
*   **Logic**:
    *   Nếu File chưa có trong DB -> **Xử lý mới**.
    *   Nếu File có trong DB nhưng Hash thay đổi -> **Cập nhật lại**.
    *   Nếu File có trong DB và Hash khớp -> **Bỏ qua**.

### 4. Xử lý Văn bản (Processing)
Với các file cần xử lý:
1.  **Load**: Dùng `PyPDFLoader` hoặc `Docx2txtLoader` để đọc text.
2.  **Split**: Dùng `RecursiveCharacterTextSplitter`.
    *   `chunk_size`: 1000 ký tự.
    *   `chunk_overlap`: 200 ký tự.
3.  **Embed**: Gọi model Embedding để chuyển text thành vector.

### 5. Lưu trữ (Indexing)
*   Thêm vector vào FAISS Index.
*   Lưu Index xuống đĩa: `data/vector_store/index.faiss`.
*   Lưu thông tin metadata (source, page) vào `index.pkl`.
