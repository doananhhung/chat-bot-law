# TECHNICAL DESIGN DOCUMENT (TDD)
**Project Name:** AI Legal Assistant (RAG System) - MVP Version
**Version:** 1.0.0
**Status:** Approved for Development

---

## 1. TỔNG QUAN KIẾN TRÚC (SYSTEM ARCHITECTURE)

Hệ thống được thiết kế theo mô hình **Modular Monolith**, chia tách rõ ràng giữa hai luồng xử lý chính để đảm bảo khả năng mở rộng (Scalability) và bảo trì (Maintainability).

### 1.1. High-Level Data Flow
1.  **Offline Pipeline (Data Ingestion):**
    * Input: Văn bản pháp luật (PDF, Docx).
    * Process: Load -> Clean -> Chunking -> Embedding.
    * Output: Vector Index (lưu trữ trên đĩa cứng/memory).
2.  **Online Pipeline (RAG Inference):**
    * Input: User Query.
    * Process: Query Embedding -> Semantic Search (Vector DB) -> Context Construction -> LLM Generation.
    * Output: Natural Language Answer + Citation.

### 1.2. Tech Stack (Hard Constraints)
* **Language:** Python 3.10+
* **Orchestration Framework:** LangChain (Core framework).
* **Vector Database:** FAISS (Local) hoặc ChromaDB (ưu tiên FAISS cho MVP vì dễ triển khai).
* **Embedding Model:** `bkai-foundation-models/vietnamese-bi-encoder` (HuggingFace).
* **LLM Provider:** Google Gemini API (`gemini-pro`).
* **Frontend:** Streamlit.

---

## 2. CẤU TRÚC THƯ MỤC (DIRECTORY STRUCTURE)

Kỹ sư cần tuân thủ chính xác cấu trúc này để đảm bảo Clean Architecture.

```text
project_root/
├── .env                    # Chứa API KEYS (Google API, LangSmith...)
├── requirements.txt        # Danh sách thư viện
├── README.md               # Hướng dẫn chạy
├── data/                   # Tầng lưu trữ dữ liệu
│   ├── raw/                # Chứa file PDF/Docx gốc do người dùng upload
│   └── vector_store/       # Chứa index file của FAISS/Chroma (được sinh ra tự động)
├── src/
│   ├── __init__.py
│   ├── config.py           # Quản lý cấu hình tập trung (Singleton)
│   ├── ingestion/          # MODULE 1: Xử lý dữ liệu đầu vào
│   │   ├── __init__.py
│   │   ├── loader.py       # Xử lý đọc file
│   │   ├── splitter.py     # Xử lý cắt văn bản
│   │   └── indexer.py      # Xử lý Embedding và lưu vào Vector DB
│   ├── rag_engine/         # MODULE 2: Xử lý logic RAG
│   │   ├── __init__.py
│   │   ├── retriever.py    # Logic tìm kiếm vector
│   │   ├── generator.py    # Logic gọi LLM và tạo câu trả lời
│   │   └── prompts.py      # Quản lý Prompt Templates tập trung
│   └── utils/              # Các hàm tiện ích chung
│       ├── __init__.py
│       └── logger.py       # Cấu hình logging hệ thống
└── app.py                  # Entry point cho Streamlit UI
```

---

## 3. THIẾT KẾ CHI TIẾT MODULE (DETAILED COMPONENT DESIGN)

### 3.1. Module Cấu Hình (`src/config.py`)

**Mục tiêu:** Tránh hard-code, quản lý biến môi trường tại một nơi duy nhất.

-   **Class:** `AppConfig`
    
    -   **Attributes:**
        
        -   `GOOGLE_API_KEY`: String
            
        -   `EMBEDDING_MODEL_NAME`: String (Default: "bkai-foundation-models/vietnamese-bi-encoder")
            
        -   `VECTOR_DB_PATH`: Path (Đường dẫn lưu file index)
            
        -   `CHUNK_SIZE`: Integer (Default: 1000)
            
        -   `CHUNK_OVERLAP`: Integer (Default: 200)
            
    -   **Behavior:** Tự động load từ file `.env` khi khởi tạo.
        

### 3.2. Module Ingestion (`src/ingestion`)

**Mục tiêu:** Chuyển đổi tài liệu thô thành Vector Database. Module này chạy độc lập (batch processing).

#### Component: `DocumentLoader` (`loader.py`)

-   **Function:** `load_documents(directory_path: str) -> List[Document]`
    
    -   **Logic:**
        
        1.  Duyệt qua thư mục `data/raw`.
            
        2.  Phát hiện định dạng file (PDF hoặc Docx).
            
        3.  Sử dụng `PyPDFLoader` (cho PDF) hoặc `Docx2txtLoader` (cho Word) của LangChain.
            
        4.  Trả về danh sách đối tượng `Document` chứa nội dung text và metadata (số trang, tên file).
            

#### Component: `TextSplitter` (`splitter.py`)

-   **Function:** `split_documents(documents: List[Document]) -> List[Document]`
    
    -   **Logic:**
        
        1.  Khởi tạo `RecursiveCharacterTextSplitter` với cấu hình từ `AppConfig`.
            
        2.  Thực hiện split.
            
        3.  **Quan trọng:** Đảm bảo metadata của document gốc được sao chép sang từng chunk con.
            

#### Component: `VectorIndexer` (`indexer.py`)

-   **Function:** `build_index(chunks: List[Document]) -> None`
    
    -   **Logic:**
        
        1.  Khởi tạo `HuggingFaceEmbeddings` với model từ config.
            
        2.  Khởi tạo Vector Store (FAISS) từ các chunks và model embedding.
            
        3.  Lưu (Save) index xuống đĩa cứng tại đường dẫn `VECTOR_DB_PATH`.
            

### 3.3. Module RAG Engine (`src/rag_engine`)

**Mục tiêu:** Xử lý truy vấn thời gian thực.

#### Component: `VectorRetriever` (`retriever.py`)

-   **Class:** `SemanticRetriever`
    
    -   **Method:** `__init__(db_path, embedding_model_name)`
        
        -   Load FAISS index từ đĩa cứng (tránh việc build lại mỗi lần chạy).
            
    -   **Method:** `get_relevant_docs(query: str, k: int = 4) -> List[Document]`
        
        -   Thực hiện similarity search.
            
        -   Trả về top `k` đoạn văn bản liên quan nhất.
            

#### Component: `PromptManager` (`prompts.py`)

-   **Variable:** `QA_PROMPT_TEMPLATE`
    
    -   **Content:** Template chuỗi chứa placeholder `{context}` và `{question}`.
        
    -   **Yêu cầu:** Phải có chỉ dẫn rõ ràng cho LLM: "Chỉ trả lời dựa trên context", "Trích dẫn nguồn nếu có thể", "Nếu không biết thì nói không biết".
        

#### Component: `RAGGenerator` (`generator.py`)

-   **Class:** `RAGChain`
    
    -   **Attributes:** `llm`, `retriever`, `prompt`.
        
    -   **Method:** `generate_answer(query: str) -> Dict`
        
        -   **Input:** Câu hỏi người dùng.
            
        -   **Steps:**
            
            1.  Gọi `retriever.get_relevant_docs(query)`.
                
            2.  Format prompt với context lấy được.
                
            3.  Gửi request tới Gemini API (`ChatGoogleGenerativeAI`).
                
        -   **Output:** Dictionary chứa:
            
            -   `answer`: Câu trả lời từ LLM.
                
            -   `source_documents`: List các documents được dùng để tham khảo (dùng cho tính năng trích dẫn).
                

### 3.4. Application Entry Point (`app.py`)

**Mục tiêu:** Giao diện người dùng (Streamlit).

-   **Logic Flow:**
    
    1.  **Initialize:** Khi app khởi động, gọi `RAGChain` (Load model và Vector DB một lần duy nhất vào `st.session_state` để tối ưu hiệu năng).
        
    2.  **Sidebar:** Nút "Re-index Data" -> Gọi `src.ingestion.indexer` để build lại dữ liệu nếu người dùng upload file mới vào `data/raw`.
        
    3.  **Main Chat Interface:**
        
        -   Input box cho người dùng.
            
        -   Khi Enter -> Gọi `chain.generate_answer`.
            
        -   Hiển thị câu trả lời.
            
        -   **UI Requirement:** Bên dưới câu trả lời, hiển thị block "Nguồn tham khảo" (Expandable), liệt kê tên file và nội dung trích dẫn từ `source_documents`.
            

* * *

## 4. QUY TRÌNH PHÁT TRIỂN (DEVELOPMENT WORKFLOW)

Kỹ sư thực hiện theo thứ tự sau để đảm bảo kiểm thử từng phần:

1.  **Setup Environment:** Tạo venv, cài thư viện (`langchain`, `faiss-cpu`, `google-generativeai`, `streamlit`, `pypdf`, `sentence-transformers`).
    
2.  **Implement Ingestion Layer:** Viết code cho `src/ingestion`. Chạy thử script để đảm bảo file PDF được biến thành folder `vector_store` thành công.
    
3.  **Implement RAG Engine:** Viết code cho `src/rag_engine`. Viết script test nhỏ: hard-code một câu hỏi, in ra câu trả lời và nguồn trên terminal.
    
4.  **Implement UI:** Viết `app.py` để kết nối giao diện với RAG Engine.
    

## 5. LƯU Ý KỸ THUẬT QUAN TRỌNG (ENGINEERING NOTES)

-   **Abstraction:** Không gọi trực tiếp `google.generativeai` trong `app.py`. Mọi logic gọi API phải nằm trong `src/rag_engine/generator.py`. Điều này giúp sau này đổi sang Model khác dễ dàng.

-   **Error Handling:** Phải xử lý trường hợp Vector DB chưa tồn tại (lần đầu chạy). Nếu chưa có, hiển thị cảnh báo trên UI yêu cầu người dùng bấm "Build Index".

-   **Citation Key:** Khi chunking, đảm bảo `metadata` của chunk chứa `source` (tên file) và `page` (trang số). Đây là chìa khóa để tính năng trích dẫn hoạt động.

---

## 6. LOW-LEVEL DESIGN SUPPLEMENT (CHI TIẾT BỔ SUNG)

Phần này bổ sung các chi tiết kỹ thuật cần thiết để triển khai code mà không cần suy luận.

---

### 6.1. Error Handling Specification

#### 6.1.1. API Error Handling (`src/rag_engine/generator.py`)

| Error Type | HTTP Code | Behavior | Retry Strategy |
|------------|-----------|----------|----------------|
| Rate Limit | `429` | Log warning, retry với exponential backoff | Max 3 retries, delay: 1s → 2s → 4s |
| Server Error | `500-503` | Log error, retry | Max 2 retries, delay: 2s |
| Auth Error | `401/403` | Log critical, raise exception | No retry, notify user |
| Timeout | N/A | Log warning, retry | Max 2 retries, timeout: 30s |
| Invalid Response | N/A | Log error, return fallback message | No retry |

**Fallback Message:**
```python
FALLBACK_RESPONSE = {
    "answer": "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau.",
    "source_documents": [],
    "error": True
}
```

#### 6.1.2. File Processing Errors (`src/ingestion/loader.py`)

| Error Type | Behavior | User Notification |
|------------|----------|-------------------|
| Corrupt PDF | Skip file, log error with filename | Add to `failed_files` list |
| Password-protected PDF | Skip file, log warning | Add to `failed_files` list |
| Unsupported format | Skip file, log warning | Add to `failed_files` list |
| Empty file | Skip file, log info | Add to `failed_files` list |
| Encoding error | Try UTF-8 → Latin-1 → Skip | Add to `failed_files` if all fail |

**Return Type:**
```python
@dataclass
class LoadResult:
    documents: List[Document]
    failed_files: List[Dict[str, str]]  # {"file": "name.pdf", "reason": "corrupt"}
```

#### 6.1.3. Embedding Model Errors (`src/ingestion/indexer.py`)

| Error Type | Behavior |
|------------|----------|
| Model download timeout | Timeout after 300s, raise exception with clear message |
| CUDA out of memory | Fallback to CPU, log warning |
| Invalid chunk (empty text) | Skip chunk, log warning |

---

### 6.2. Validation Logic

#### 6.2.1. File Upload Validation

```python
# src/utils/validators.py

class FileValidator:
    MAX_FILE_SIZE_MB: int = 50  # Maximum 50MB per file
    MAX_TOTAL_SIZE_MB: int = 200  # Maximum 200MB total in data/raw
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".doc"}
    ALLOWED_MIME_TYPES: Set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    }
```

| Validation | Action on Failure |
|------------|-------------------|
| File size > 50MB | Reject with message: "File quá lớn. Giới hạn: 50MB" |
| Invalid extension | Reject with message: "Định dạng không hỗ trợ. Chỉ chấp nhận: PDF, DOCX" |
| MIME type mismatch | Reject with message: "File không hợp lệ" |
| Total size exceeded | Reject with message: "Đã vượt quá dung lượng lưu trữ cho phép" |

#### 6.2.2. Duplicate Document Handling

**Strategy:** `REPLACE` - Nếu file cùng tên đã tồn tại, thay thế file cũ.

```python
# src/ingestion/indexer.py

class DuplicateStrategy(Enum):
    REPLACE = "replace"  # Default: Thay thế document cũ
    SKIP = "skip"        # Bỏ qua nếu đã tồn tại
    APPEND = "append"    # Thêm suffix _v2, _v3...
```

#### 6.2.3. Query Validation

```python
# src/rag_engine/retriever.py

class QueryValidator:
    MIN_QUERY_LENGTH: int = 2
    MAX_QUERY_LENGTH: int = 1000
    
    @staticmethod
    def validate(query: str) -> Tuple[bool, str]:
        if len(query.strip()) < MIN_QUERY_LENGTH:
            return False, "Câu hỏi quá ngắn"
        if len(query) > MAX_QUERY_LENGTH:
            return False, "Câu hỏi quá dài (tối đa 1000 ký tự)"
        return True, ""
```

---

### 6.3. Data Flow Details

#### 6.3.1. Metadata Schema

```python
# src/models/document.py

@dataclass
class ChunkMetadata:
    source: str          # Tên file gốc, e.g., "luat_dan_su_2015.pdf"
    page: int            # Số trang (1-indexed), 0 nếu không xác định được
    chunk_id: str        # UUID v4, e.g., "a1b2c3d4-..."
    chunk_index: int     # Thứ tự chunk trong document (0-indexed)
    total_chunks: int    # Tổng số chunks của document
    created_at: str      # ISO 8601 timestamp, e.g., "2024-01-15T10:30:00Z"
    file_hash: str       # MD5 hash của file gốc (để detect duplicates)
```

**Example:**
```json
{
    "source": "luat_dan_su_2015.pdf",
    "page": 15,
    "chunk_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "chunk_index": 42,
    "total_chunks": 150,
    "created_at": "2024-01-15T10:30:00Z",
    "file_hash": "d41d8cd98f00b204e9800998ecf8427e"
}
```

#### 6.3.2. Chunk ID Generation

```python
import uuid

def generate_chunk_id() -> str:
    """Generate unique chunk ID using UUID v4."""
    return str(uuid.uuid4())
```

#### 6.3.3. Context Window Management

```python
# src/rag_engine/retriever.py

class ContextManager:
    MAX_CONTEXT_TOKENS: int = 8000  # Gemini context limit buffer
    CHARS_PER_TOKEN: float = 4.0    # Approximate for Vietnamese
    
    @staticmethod
    def truncate_context(chunks: List[Document], max_tokens: int = MAX_CONTEXT_TOKENS) -> List[Document]:
        """
        Truncate chunks to fit within context window.
        Strategy: Keep first N chunks that fit, prioritize by relevance score.
        """
        result = []
        current_chars = 0
        max_chars = int(max_tokens * CHARS_PER_TOKEN)
        
        for chunk in chunks:
            chunk_chars = len(chunk.page_content)
            if current_chars + chunk_chars <= max_chars:
                result.append(chunk)
                current_chars += chunk_chars
            else:
                # Truncate last chunk if partially fits
                remaining = max_chars - current_chars
                if remaining > 200:  # Minimum useful content
                    truncated = Document(
                        page_content=chunk.page_content[:remaining] + "...",
                        metadata=chunk.metadata
                    )
                    result.append(truncated)
                break
        
        return result
```

---

### 6.4. State Management

#### 6.4.1. Re-indexing Behavior

**Strategy:** `FULL_REPLACE` - Xóa index cũ, build lại hoàn toàn.

```python
# src/ingestion/indexer.py

class IndexingMode(Enum):
    FULL_REPLACE = "full_replace"  # Default: Xóa index cũ, build mới
    INCREMENTAL = "incremental"    # Future: Chỉ thêm documents mới

def build_index(chunks: List[Document], mode: IndexingMode = IndexingMode.FULL_REPLACE) -> None:
    if mode == IndexingMode.FULL_REPLACE:
        # Delete existing index
        if os.path.exists(VECTOR_DB_PATH):
            shutil.rmtree(VECTOR_DB_PATH)
    # Build new index...
```

#### 6.4.2. Concurrent Access Protection

```python
# src/utils/lock.py

import filelock

INDEX_LOCK_PATH = "data/vector_store/.index.lock"

def with_index_lock(timeout: int = 60):
    """Decorator to prevent concurrent index modifications."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock = filelock.FileLock(INDEX_LOCK_PATH, timeout=timeout)
            try:
                with lock:
                    return func(*args, **kwargs)
            except filelock.Timeout:
                raise RuntimeError("Index đang được cập nhật bởi tiến trình khác. Vui lòng thử lại sau.")
        return wrapper
    return decorator
```

#### 6.4.3. Session & Chat History

**Strategy:** `SESSION_ONLY` - Chat history chỉ tồn tại trong session hiện tại.

```python
# app.py

# Session state structure
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List[Dict[str, str]]

# Chat history item format:
# {"role": "user" | "assistant", "content": "...", "sources": [...]}

# Maximum history length
MAX_CHAT_HISTORY = 50
```

---

### 6.5. Performance Specifications

#### 6.5.1. Timeout Configuration

```python
# src/config.py

class TimeoutConfig:
    LLM_REQUEST_TIMEOUT: int = 30        # seconds
    EMBEDDING_REQUEST_TIMEOUT: int = 60  # seconds
    VECTOR_SEARCH_TIMEOUT: int = 10      # seconds
    FILE_PROCESSING_TIMEOUT: int = 120   # seconds per file
```

#### 6.5.2. Batch Processing

```python
# src/ingestion/indexer.py

class BatchConfig:
    EMBEDDING_BATCH_SIZE: int = 32   # Chunks per embedding batch
    INDEX_BATCH_SIZE: int = 500      # Chunks per index write
    MAX_WORKERS: int = 4             # Parallel file processing
```

#### 6.5.3. FAISS Configuration

```python
# src/config.py

class FAISSConfig:
    INDEX_TYPE: str = "Flat"              # "Flat" for MVP, "IVF" for large scale
    USE_GPU: bool = False                 # CPU only for MVP
    NORMALIZE_VECTORS: bool = True        # L2 normalization
    SAVE_FORMAT: str = "local"            # "local" disk storage
```

---

### 6.6. Security Considerations

#### 6.6.1. Input Sanitization

```python
# src/utils/sanitizer.py

import re

class QuerySanitizer:
    # Patterns that might indicate prompt injection
    DANGEROUS_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"forget\s+(everything|all)",
        r"you\s+are\s+now",
        r"act\s+as\s+a",
        r"system\s*:\s*",
    ]
    
    @staticmethod
    def sanitize(query: str) -> str:
        """Remove potentially dangerous patterns from user query."""
        sanitized = query
        for pattern in DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()
    
    @staticmethod
    def is_suspicious(query: str) -> bool:
        """Check if query contains suspicious patterns."""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
```

#### 6.6.2. File Security

```python
# src/utils/validators.py

import magic  # python-magic library

class FileSecurityValidator:
    @staticmethod
    def validate_mime_type(file_path: str) -> bool:
        """Verify file MIME type matches extension."""
        mime = magic.Magic(mime=True)
        detected_type = mime.from_file(file_path)
        
        extension = Path(file_path).suffix.lower()
        expected_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword"
        }
        
        return detected_type == expected_types.get(extension)
```

#### 6.6.3. Environment Security

```text
# .gitignore (REQUIRED)

.env
.env.local
.env.*.local
data/vector_store/
*.pyc
__pycache__/
.pytest_cache/
```

---

### 6.7. Detailed Prompt Template

```python
# src/rag_engine/prompts.py

QA_SYSTEM_PROMPT = """Bạn là trợ lý pháp luật AI chuyên về luật Việt Nam. 
Nhiệm vụ của bạn là trả lời câu hỏi DỰA TRÊN các tài liệu được cung cấp.

NGUYÊN TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên thông tin trong phần [TÀI LIỆU THAM KHẢO]
2. Nếu không tìm thấy thông tin liên quan, trả lời: "Tôi không tìm thấy thông tin về vấn đề này trong các tài liệu hiện có."
3. LUÔN trích dẫn nguồn theo format: [Nguồn: tên_file, Trang: số_trang]
4. Trả lời bằng tiếng Việt
5. Giữ câu trả lời súc tích, rõ ràng
6. KHÔNG bịa đặt thông tin không có trong tài liệu"""

QA_USER_PROMPT_TEMPLATE = """[TÀI LIỆU THAM KHẢO]
{context}

[CÂU HỎI]
{question}

[TRẢ LỜI]
Hãy trả lời câu hỏi trên dựa trên tài liệu tham khảo. Nhớ trích dẫn nguồn."""

# Citation format example in response:
# "Theo Điều 15 Luật Dân sự 2015, [Nguồn: luat_dan_su_2015.pdf, Trang: 12]..."
```

#### Context Formatting

```python
# src/rag_engine/prompts.py

def format_context(documents: List[Document]) -> str:
    """Format retrieved documents into context string."""
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.strip()
        
        context_parts.append(
            f"--- Tài liệu {i} ---\n"
            f"Nguồn: {source} | Trang: {page}\n"
            f"Nội dung:\n{content}\n"
        )
    
    return "\n".join(context_parts)
```

---

### 6.8. Constants & Enums (`src/constants.py`)

```python
from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    NO_CONTEXT = "no_context"
    RATE_LIMITED = "rate_limited"

class IndexStatus(Enum):
    NOT_INITIALIZED = "not_initialized"
    BUILDING = "building"
    READY = "ready"
    ERROR = "error"

# UI Messages
UI_MESSAGES = {
    "NO_INDEX": "⚠️ Chưa có dữ liệu. Vui lòng upload file và bấm 'Build Index'.",
    "INDEXING": "🔄 Đang xử lý dữ liệu...",
    "INDEX_SUCCESS": "✅ Xử lý dữ liệu thành công!",
    "INDEX_ERROR": "❌ Lỗi xử lý dữ liệu: {error}",
    "QUERY_ERROR": "❌ Không thể xử lý câu hỏi. Vui lòng thử lại.",
    "EMPTY_QUERY": "⚠️ Vui lòng nhập câu hỏi.",
}
```

---

## 7. DEPENDENCIES (`requirements.txt`)

```text
# Core
langchain>=0.1.0
langchain-google-genai>=0.0.6
langchain-community>=0.0.10

# Vector Store
faiss-cpu>=1.7.4

# Embeddings
sentence-transformers>=2.2.2

# Document Processing
pypdf>=3.17.0
python-docx>=1.1.0
docx2txt>=0.8

# Web UI
streamlit>=1.29.0

# Utilities
python-dotenv>=1.0.0
filelock>=3.13.0
python-magic>=0.4.27

# Development
pytest>=7.4.0
black>=23.0.0
mypy>=1.7.0
```

---

## 8. APPENDIX: TYPE HINTS SUMMARY

```python
# src/types.py

from typing import TypedDict, List, Optional

class ChunkMetadataDict(TypedDict):
    source: str
    page: int
    chunk_id: str
    chunk_index: int
    total_chunks: int
    created_at: str
    file_hash: str

class RAGResponse(TypedDict):
    answer: str
    source_documents: List[dict]
    status: str  # ResponseStatus value
    error: Optional[str]

class LoadResultDict(TypedDict):
    documents: List[dict]
    failed_files: List[dict]
    total_processed: int
    total_failed: int
```


