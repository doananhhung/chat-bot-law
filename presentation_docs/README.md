# 📊 Presentation Materials - AI Legal Assistant

## 🎯 Mục đích
Thư mục này chứa tất cả tài liệu chuẩn bị cho buổi thuyết trình về dự án **AI Legal Assistant** (Trợ lý Pháp luật AI).

---

## 📁 Cấu Trúc Thư Mục

```
presentation/
├── README.md                    # Tổng quan (file này)
├── presentation_plan.md         # Kế hoạch thuyết trình tổng thể
│
├── member1/                     # Thành viên 1: Giới thiệu & Kiến trúc
│   ├── 01_overview_architecture.md   # Tổng quan kiến trúc hệ thống
│   ├── 02_rag_concepts.md            # Khái niệm RAG
│   └── 03_tech_stack_summary.md      # Tổng hợp công nghệ
│
├── member2/                     # Thành viên 2: Data Processing
│   ├── 01_ingestion_pipeline.md      # Pipeline nạp dữ liệu
│   ├── 02_text_chunking.md           # Chiến lược chia văn bản
│   ├── 03_embedding_models.md        # Mô hình embedding
│   └── 04_faiss_vector_search.md     # Tìm kiếm vector FAISS
│
├── member3/                     # Thành viên 3: RAG Engine
│   ├── 01_semantic_retrieval.md      # Tìm kiếm ngữ nghĩa
│   ├── 02_intent_routing.md          # Phân loại intent
│   ├── 03_prompt_engineering.md      # Kỹ thuật prompt
│   └── 04_llm_factory_pattern.md     # Factory pattern cho LLM
│
└── member4/                     # Thành viên 4: UI & Demo
    ├── 01_streamlit_ui.md            # Giao diện Streamlit
    ├── 02_database_persistence.md    # Lưu trữ database
    ├── 03_performance_optimization.md # Tối ưu hiệu năng
    └── 04_demo_script.md             # Hướng dẫn demo
```

---

## 👥 Phân Công Thành Viên

| Thành viên | Phần trình bày | Thời lượng |
|------------|----------------|------------|
| **Member 1** | Giới thiệu, Kiến trúc, RAG Concepts, Tech Stack | 10-12 phút |
| **Member 2** | Ingestion Pipeline, Chunking, Embedding, FAISS | 10-12 phút |
| **Member 3** | Semantic Retrieval, Intent Routing, Prompts, LLM Factory | 10-12 phút |
| **Member 4** | Streamlit UI, Database, Performance, Live Demo | 10-12 phút |

**Tổng thời gian**: ~45-50 phút (bao gồm Q&A)

---

## 📋 Checklist Chuẩn Bị

### Trước buổi thuyết trình
- [ ] Đọc kỹ tài liệu trong thư mục assigned
- [ ] Chạy thử ứng dụng: `streamlit run app.py`
- [ ] Chuẩn bị slide (nếu cần) từ nội dung markdown
- [ ] Đảm bảo có file `.env` với API key hợp lệ
- [ ] Test demo flow với các câu hỏi mẫu

### Ngày thuyết trình
- [ ] Activate virtual environment
- [ ] Chạy app warm-up (để cache model)
- [ ] Verify internet connection (cho API calls)
- [ ] Chuẩn bị backup plan nếu API fail

---

## 🎯 Key Points để Nhấn Mạnh

### Member 1 (Intro & Architecture)
1. **RAG** - Retrieval-Augmented Generation: Tìm kiếm + Sinh nội dung
2. **Modular Monolith** - Clean Architecture với các layer rõ ràng
3. **Multi-provider LLM** - Dễ dàng switch giữa Google và Groq

### Member 2 (Data Processing)
1. **4-step Pipeline**: Load → Split → Embed → Index
2. **Incremental Sync** - Chỉ xử lý files thay đổi
3. **vietnamese-bi-encoder** - Embedding model tối ưu cho tiếng Việt

### Member 3 (RAG Engine)
1. **Semantic Search** - Hiểu ý nghĩa, không chỉ từ khóa
2. **Intent Router** - Phân biệt LEGAL vs GENERAL
3. **IRAC Structure** - Chuẩn trả lời pháp lý

### Member 4 (UI & Demo)
1. **@st.cache_resource** - Cold start 17s → <1s reload
2. **Stateless Design** - Cho phép caching
3. **Live Demo** - Show real accuracy và citations

---

## 📚 Tài Liệu Tham Khảo Bổ Sung

Trong dự án chính:
- `README.md` - Overview dự án
- `DEV_LOG.md` - Lịch sử phát triển & ADRs
- `CLAUDE.md` - Guidelines và context
- `docs/` - Technical documentation

---

## 🚀 Quick Start Demo

```bash
# 1. Activate environment
cd d:\heheboi\Project\chat-bot-law
.\venv\Scripts\activate

# 2. Run app
streamlit run app.py

# 3. Wait for cold start (~17s first time)
# 4. Start demoing!
```

---

*Chúc buổi thuyết trình thành công! 🎉*
