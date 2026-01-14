# Luồng AI RAG (Retrieval-Augmented Generation)

Tài liệu này mô tả chi tiết cách hệ thống xử lý một câu hỏi từ người dùng để đưa ra câu trả lời pháp lý chính xác.

## Sơ đồ Tuần tự (Sequence Diagram)

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant UI as Streamlit UI
    participant RAG as RAGChain (Orchestrator)
    participant Router as IntentRouter
    participant VDB as Vector DB (FAISS)
    participant LLM as Gemini/Groq

    U->>UI: Nhập câu hỏi
    UI->>RAG: generate_answer(query, history)

    Note over RAG: Bước 1: Rewriting (nếu có history)
    opt Có lịch sử chat
        RAG->>LLM: condense_question_chain(history, query)
        LLM-->>RAG: Standalone question
    end

    Note over RAG: Bước 2: Intent Classification
    RAG->>Router: classify(standalone_query)
    Router->>LLM: Classify prompt
    LLM-->>Router: "LEGAL" / "GENERAL"
    Router-->>RAG: intent

    alt intent == GENERAL
        Note over RAG: Bước 3a: General Response
        RAG->>LLM: general_chain(query, history)
        LLM-->>RAG: Câu trả lời xã giao
    else intent == LEGAL
        Note over RAG: Bước 3b: RAG Pipeline
        RAG->>VDB: retriever.get_relevant_docs(standalone_query)
        VDB-->>RAG: Relevant chunks + metadata

        RAG->>LLM: qa_chain(context, standalone_query)
        LLM-->>RAG: Câu trả lời pháp lý
    end

    RAG-->>UI: {answer, source_documents, intent, standalone_query}
    UI->>UI: Lưu tin nhắn vào Database
    UI-->>U: Hiển thị kết quả
```

## Các bước xử lý chi tiết

### 1. Query Rewriting (Conditional)
*   **Điều kiện**: Chỉ thực hiện khi `chat_history_str` không rỗng (có lịch sử hội thoại).
*   **Mục đích**: Chuyển câu hỏi phụ thuộc ngữ cảnh (ví dụ: "Nó có áp dụng cho tôi không?") thành câu hỏi độc lập.
*   **Implementation**: `condense_question_chain.invoke({chat_history, question})` → `standalone_query`
*   **Fallback**: Nếu không có history hoặc rewriting thất bại → `standalone_query = query` (giữ nguyên).

### 2. Intent Classification
*   **Input**: `standalone_query` (đã rewrite hoặc query gốc).
*   **Process**: `IntentRouter.classify(standalone_query)` gọi LLM để phân loại.
*   **Output**: `"LEGAL"` hoặc `"GENERAL"`.
*   **Fallback**: Nếu classification thất bại → mặc định `"LEGAL"` để đảm bảo trả lời.

### 3. Response Generation (Branching)

#### 3a. GENERAL Intent
*   **Chain**: `general_chain.invoke({question, chat_history})`
*   **Output**: Câu trả lời xã giao, thân thiện.
*   **Không truy xuất**: Bỏ qua Vector DB.

#### 3b. LEGAL Intent (RAG Pipeline)
*   **Retrieval**:
    *   `retriever.get_relevant_docs(standalone_query)` → Vector search trong FAISS.
    *   Sử dụng model `bkai-foundation-models/vietnamese-bi-encoder` để embedding.
    *   Trả về `k` chunks có độ tương đồng cao nhất + metadata.
*   **Generation**:
    *   `qa_chain.invoke({context, standalone_query})`
    *   Context = formatted chunks từ bước Retrieval.
*   **Edge case**: Nếu không tìm thấy documents → trả về thông báo không tìm thấy.

### 4. Response Return
*   **Output format**:
    ```python
    {
        "answer": str,           # Câu trả lời cuối cùng
        "source_documents": [],  # Danh sách chunks (chỉ có với LEGAL)
        "intent": str,           # "LEGAL" hoặc "GENERAL"
        "standalone_query": str  # Query sau khi rewrite
    }
    ```
*   **Post-processing**: UI lưu tin nhắn vào Database và hiển thị kết quả.
