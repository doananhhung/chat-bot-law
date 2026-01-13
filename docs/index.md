# Tài liệu Kỹ thuật Dự án AI Legal Assistant

Chào mừng bạn đến với trang tài liệu kỹ thuật của dự án **AI Legal Assistant**. Tài liệu này được thiết kế để giúp các Developer hiểu rõ kiến trúc, luồng dữ liệu và cách đóng góp vào dự án.

## 📚 Mục lục

### 1. Kiến trúc Hệ thống (Architecture)
Hiểu về bức tranh tổng thể và các quyết định công nghệ.
* [Tổng quan hệ thống (System Overview)](1_architecture/system_overview.md)
* [Quyết định công nghệ (Tech Stack)](1_architecture/tech_stack_decisions.md)

### 2. Luồng Hoạt động (Flows) - **Quan trọng**
Chi tiết cách dữ liệu di chuyển và xử lý trong hệ thống.
* [Luồng AI RAG (Retrieval-Augmented Generation)](2_flows/ai_rag_pipeline.md)
* [Luồng Phân loại Ý định (Router)](2_flows/ai_router_logic.md)
* [Quy trình Nạp & Đồng bộ Dữ liệu (Ingestion)](2_flows/data_ingestion_sync.md)
* [Vòng đời Chat Session & Database](2_flows/db_session_lifecycle.md)
* [Quản lý Trạng thái UI (Streamlit State)](2_flows/ui_state_management.md)

### 3. Cơ sở dữ liệu (Database)
* [Sơ đồ Database (Schema & ERD)](3_database/schema_erd.md)
* [Hướng dẫn Migration](3_database/migration_guide.md)

### 4. Hướng dẫn Phát triển (Guides)
* [Thiết lập môi trường Local](4_guides/setup_local.md)
* [Chiến lược Testing](4_guides/testing_strategies.md)

---
*Tài liệu được cập nhật lần cuối vào tháng 01/2026.*
