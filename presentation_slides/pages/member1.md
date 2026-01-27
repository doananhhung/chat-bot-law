---
---

<LayoutSection title="AI Legal Assistant">

**Trợ lý Pháp luật Thông minh**

*Luật Lao Động Việt Nam*

<div class="my-8 border-t border-slate-300 opacity-50 w-24"></div>

👤 Member 1: Giới thiệu & Kiến trúc

📅 27/01/2026

</LayoutSection>

---

<LayoutTitleContent title="Problem Statement">

| Pain Point | Mô tả |
|------------|-------|
| 🔍 **Tìm kiếm thủ công** | Phải đọc hàng trăm trang văn bản luật để tìm điều khoản liên quan |
| 🤔 **Thiếu ngữ cảnh** | Keyword search không hiểu ý nghĩa câu hỏi |
| ❌ **Không có trích dẫn** | Khó xác minh nguồn thông tin được cung cấp |
| 📚 **Ngôn ngữ pháp lý** | Thuật ngữ chuyên môn khó hiểu với người thường |

</LayoutTitleContent>

---

<LayoutComparison title="Solution: RAG" leftTitle="Without RAG" rightTitle="With RAG">

<template #left>

### LLM thông thường

```
Câu hỏi 
    ↓
   LLM 
    ↓
Trả lời
```

- Kiến thức giới hạn
- Có thể sai/hallucination
- Không có nguồn verify

</template>

<template #right>

### Retrieval-Augmented Generation

```
Câu hỏi 
    ↓
Tìm kiếm (FAISS) 
    ↓
Context + Câu hỏi 
    ↓
   LLM 
    ↓
Trả lời + Trích dẫn ✅
```

</template>

</LayoutComparison>

---

<LayoutTitleContent title="Key System Features">

| Tính năng | Mô tả |
|-----------|-------|
| 🧠 **Semantic Search** | Hiểu ý nghĩa câu hỏi, không chỉ keyword |
| 📚 **Citation** | Trích dẫn nguồn: file, trang cụ thể |
| 💬 **Conversational** | Nhớ ngữ cảnh hội thoại, hỏi follow-up |
| 🔄 **Easy Update** | Thêm luật mới chỉ cần copy PDF vào folder |
| 🚀 **Fast Response** | Trả lời trong 1-2 giây |

**Ví dụ:** Hiểu được "nghỉ đẻ" và "thai sản" là cùng một khái niệm

</LayoutTitleContent>

---

<LayoutSection title="Architecture Overview">

**Modular Monolith Architecture**

</LayoutSection>

---

<LayoutDiagram title="System Architecture">

```mermaid
flowchart TB
    subgraph Presentation["PRESENTATION LAYER"]
        UI["🖥️ Streamlit UI<br/>(app.py)"]
    end
    
    subgraph Business["BUSINESS LOGIC LAYER"]
        RAG["🤖 RAG Engine<br/>Generator | Retriever | Router"]
        ING["📄 Ingestion<br/>Loader | Splitter | Indexer"]
        DB["💾 Database<br/>Models | Repository"]
    end
    
    subgraph Data["DATA ACCESS LAYER"]
        FAISS["🔍 FAISS<br/>Vector DB"]
        SQLite["📊 SQLite<br/>Chat History"]
    end
    
    subgraph External["EXTERNAL SERVICES"]
        Groq["☁️ Groq API<br/>LLM - Kimi K2"]
        HF["🤗 HuggingFace<br/>vietnamese-bi-encoder"]
    end
    
    UI --> RAG
    UI --> ING
    UI --> DB
    RAG --> FAISS
    RAG --> Groq
    ING --> FAISS
    ING --> HF
    DB --> SQLite
```

</LayoutDiagram>

---

<LayoutDiagram title="Query Processing Flow">

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🖥️ UI
    participant Router as 🔀 Router
    participant RAG as 🤖 RAG
    participant VDB as 🔍 FAISS
    participant LLM as ☁️ Groq

    User->>UI: "Thai sản nghỉ mấy tháng?"
    UI->>Router: Classify Intent
    Router->>LLM: LEGAL or GENERAL?
    LLM-->>Router: LEGAL
    
    Router->>RAG: Process Query
    RAG->>VDB: Similarity Search
    VDB-->>RAG: Top 10 chunks
    
    RAG->>LLM: Context + Question
    LLM-->>RAG: Structured Answer
    
    RAG-->>UI: Answer + Citations
    UI-->>User: Display Result
```

</LayoutDiagram>

---

<LayoutTwoCol title="RAG Engine Components">

<template #left>

### Components

| Component | Chức năng |
|-----------|-----------|
| **Generator** | Điều phối toàn bộ flow RAG |
| **Retriever** | Tìm kiếm semantic trong FAISS |
| **Router** | Phân loại intent LEGAL/GENERAL |
| **Prompts** | Template prompt cho LLM |
| **LLM Factory** | Tạo LLM instance |

</template>

<template #right>

### Files

```
src/rag_engine/
├── generator.py    # Main orchestrator
├── retriever.py    # Vector search
├── router.py       # Intent classification
├── prompts.py      # Prompt templates
└── llm_factory.py  # LLM provider abstraction
```

</template>

</LayoutTwoCol>

---

<LayoutTitleContent title="Tech Stack">

| Layer | Công nghệ | Mục đích |
|-------|-----------|----------|
| **Frontend** | Streamlit | Web UI với Python thuần |
| **AI Framework** | LangChain | Orchestration cho LLM và RAG |
| **Vector DB** | FAISS | Similarity search hiệu quả |
| **Embedding** | vietnamese-bi-encoder | Optimized cho tiếng Việt (768D) |
| **LLM** | Groq (Kimi K2) | Fast inference, free tier |
| **Database** | SQLite + SQLAlchemy | Lưu lịch sử chat |
| **Config** | python-dotenv | Environment variables |

</LayoutTitleContent>

---

<LayoutTitleContent title="Introduction Summary">

| Chủ đề | Điểm chính |
|--------|------------|
| **Vấn đề** | Tra cứu luật thủ công, thiếu ngữ cảnh, không có nguồn |
| **Giải pháp** | RAG = Retrieval + Generation |
| **Kiến trúc** | Modular Monolith với Clean Architecture |
| **Luồng xử lý** | Router → Retrieval → Generation → Citation |
| **Tech Stack** | Streamlit, LangChain, FAISS, Groq |

### Chuyển tiếp
**Tiếp theo:** Member 2 - Data Ingestion & Vector Database

*"Làm sao chuyển PDF thành searchable data?"*

</LayoutTitleContent>
