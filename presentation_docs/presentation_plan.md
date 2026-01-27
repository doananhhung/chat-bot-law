# 📋 Kế Hoạch Thuyết Trình - AI Legal Assistant (Chatbot Luật Lao Động)

> **Dự án**: Hệ thống Chatbot tra cứu Luật Lao Động thông minh sử dụng kỹ thuật RAG (Retrieval-Augmented Generation)
>
> **Ngày**: 27/01/2026  
> **Số thành viên**: 4 người

---

## 🎯 Mục tiêu thuyết trình

1. Giới thiệu tổng quan về dự án và vấn đề cần giải quyết
2. Giải thích kiến trúc hệ thống và công nghệ sử dụng
3. Demo chức năng thực tế
4. Trình bày kỹ thuật RAG và các thành phần chi tiết
5. Đánh giá kết quả và hướng phát triển

---

## 📊 Phân chia nội dung cho 4 thành viên

### 👤 **Thành viên 1: Giới thiệu & Tổng quan Kiến trúc**
**Thời lượng dự kiến**: 8-10 phút

| Nội dung | Chi tiết |
|----------|----------|
| **1.1 Giới thiệu vấn đề** | Tại sao cần Chatbot tra cứu Luật? Pain points của việc tìm kiếm thủ công |
| **1.2 Giải pháp đề xuất** | RAG - Kết hợp Retrieval + Generation |
| **1.3 Kiến trúc tổng quan** | Modular Monolith, Clean Architecture layers |
| **1.4 Luồng dữ liệu tổng quan** | User Query → Router → RAG/General → Response |
| **1.5 Tech Stack Overview** | Streamlit, LangChain, FAISS, SQLAlchemy |

📁 **Tài liệu đọc**: `presentation/member1/`
- `01_overview_architecture.md`
- `02_rag_concepts.md`
- `03_tech_stack_summary.md`

---

### 👤 **Thành viên 2: Data Ingestion & Vector Database**
**Thời lượng dự kiến**: 8-10 phút

| Nội dung | Chi tiết |
|----------|----------|
| **2.1 Pipeline Ingestion** | Load → Split → Embed → Index |
| **2.2 Document Loader** | PyPDFLoader, Docx2txtLoader, metadata handling |
| **2.3 Text Splitting** | RecursiveCharacterTextSplitter, chunk_size=1000, overlap=200 |
| **2.4 Embedding** | HuggingFace `vietnamese-bi-encoder` (768D) |
| **2.5 FAISS Vector Store** | Flat vs IVF index, nlist/nprobe configuration |
| **2.6 Incremental Sync** | Metadata tracking, differential indexing |

📁 **Tài liệu đọc**: `presentation/member2/`
- `01_ingestion_pipeline.md`
- `02_text_chunking.md`
- `03_embedding_models.md`
- `04_faiss_vector_search.md`

---

### 👤 **Thành viên 3: RAG Engine & LLM Integration**
**Thời lượng dự kiến**: 8-10 phút

| Nội dung | Chi tiết |
|----------|----------|
| **3.1 Semantic Retrieval** | Similarity search, Top-K retrieval |
| **3.2 Intent Router** | LEGAL vs GENERAL classification |
| **3.3 Query Rewriting** | Conversational context, standalone question |
| **3.4 Prompt Engineering** | System prompt, IRAC structure, Chain-of-Thought |
| **3.5 LLM Factory** | Multi-provider support (Google Gemini, Groq) |
| **3.6 Response Generation** | Context formatting, citation handling |

📁 **Tài liệu đọc**: `presentation/member3/`
- `01_semantic_retrieval.md`
- `02_intent_routing.md`
- `03_prompt_engineering.md`
- `04_llm_factory_pattern.md`

---

### 👤 **Thành viên 4: Frontend, Database & Demo**
**Thời lượng dự kiến**: 8-10 phút

| Nội dung | Chi tiết |
|----------|----------|
| **4.1 Streamlit UI** | Chat interface, session management, sidebar |
| **4.2 SQLite Database** | Schema design, ChatSession/ChatMessage models |
| **4.3 Repository Pattern** | CRUD operations, SQLAlchemy ORM |
| **4.4 Session & State** | st.session_state, @st.cache_resource |
| **4.5 Demo thực tế** | Chạy ứng dụng, demo các tính năng chính |
| **4.6 Kết quả & Đánh giá** | Latency, accuracy, user experience |

📁 **Tài liệu đọc**: `presentation/member4/`
- `01_streamlit_ui.md`
- `02_database_persistence.md`
- `03_performance_optimization.md`
- `04_demo_script.md`

---

## 🗂️ Cấu trúc thư mục presentation

```
presentation/
├── presentation_plan.md          # File này - Kế hoạch tổng thể
├── member1/                      # Tài liệu cho Thành viên 1
│   ├── 01_overview_architecture.md
│   ├── 02_rag_concepts.md
│   └── 03_tech_stack_summary.md
├── member2/                      # Tài liệu cho Thành viên 2
│   ├── 01_ingestion_pipeline.md
│   ├── 02_text_chunking.md
│   ├── 03_embedding_models.md
│   └── 04_faiss_vector_search.md
├── member3/                      # Tài liệu cho Thành viên 3
│   ├── 01_semantic_retrieval.md
│   ├── 02_intent_routing.md
│   ├── 03_prompt_engineering.md
│   └── 04_llm_factory_pattern.md
└── member4/                      # Tài liệu cho Thành viên 4
    ├── 01_streamlit_ui.md
    ├── 02_database_persistence.md
    ├── 03_performance_optimization.md
    └── 04_demo_script.md
```

---

## 📅 Lịch trình thuyết trình (Suggested)

| Thời gian | Nội dung | Người trình bày |
|-----------|----------|-----------------|
| 0:00 - 10:00 | Giới thiệu & Kiến trúc tổng quan | Thành viên 1 |
| 10:00 - 20:00 | Data Ingestion & Vector DB | Thành viên 2 |
| 20:00 - 30:00 | RAG Engine & LLM | Thành viên 3 |
| 30:00 - 40:00 | Frontend, DB & Demo | Thành viên 4 |
| 40:00 - 45:00 | Q&A | Cả nhóm |

---

## 📚 Tài liệu tham khảo chính (Trong dự án)

- `DEV_LOG.md` - Lịch sử phát triển và các quyết định kiến trúc
- `README.md` - Tổng quan dự án
- `CLAUDE.md` - Project context và conventions
- `docs/` - Tài liệu kỹ thuật chi tiết
  - `docs/1_architecture/` - Kiến trúc hệ thống
  - `docs/2_flows/` - Luồng hoạt động
  - `docs/3_database/` - Schema database
  - `docs/4_guides/` - Hướng dẫn setup

---

## ✅ Checklist trước khi thuyết trình

- [ ] Đọc hiểu tài liệu trong folder của mình
- [ ] Đọc `DEV_LOG.md` để nắm lịch sử phát triển
- [ ] Chạy thử ứng dụng (`streamlit run app.py`)
- [ ] Chuẩn bị slide presentation (nếu cần)
- [ ] Thống nhất format trình bày với các thành viên khác
- [ ] Chuẩn bị câu hỏi phỏng vấn có thể gặp

---

> **Note**: Mỗi thành viên nên đọc tài liệu trong folder của mình trước, sau đó đọc thêm tài liệu của các thành viên khác để hiểu toàn bộ hệ thống.
