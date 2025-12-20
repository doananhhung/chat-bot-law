<style>
    /* Force white background and black text for the whole page */
    body, .vscode-body {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Style code blocks to be readable on white */
    code, pre {
        background-color: #f0f0f0 !important;
        color: #222222 !important;
    }
</style>

## [2025-12-20] Task: Initial MVP Implementation & Testing Framework
### 1. Technical Explanation
- **Changes**: 
    - **Architecture**: Established a **Modular Monolith** structure as per `Designing.md`.
    - **Configuration**: Implemented `src/config.py` for centralized environment and path management.
    - **Ingestion Layer** (`src/ingestion/`):
        - `DocumentLoader`: Handles PDF/Docx loading using LangChain's `PyPDFLoader` and `Docx2txtLoader`.
        - `TextSplitter`: Implements `RecursiveCharacterTextSplitter` with chunk size of 1000 and overlap of 200.
        - `VectorIndexer`: Uses `HuggingFaceEmbeddings` (`bkai-foundation-models/vietnamese-bi-encoder`) and `FAISS` for vector storage.
    - **RAG Engine** (`src/rag_engine/`):
        - `SemanticRetriever`: Encapsulates FAISS index loading and similarity search.
        - `RAGChain`: Orchestrates the retrieval and generation flow using `Google Gemini API` (`gemini-pro`).
    - **UI** (`app.py`): Built a Streamlit interface for Chat and Data Re-indexing.
    - **Testing**: Added a robust test suite (`tests/`) using `pytest` to verify Ingestion (Loader, Splitter, Indexer) and RAG logic (mocking LLM).
- **Why**: To provide a functional prototype of the "AI Legal Assistant" that meets the core requirement of answering legal questions with accurate citations using a local vector database and a cloud-based LLM.

### 2. Flow Visualization (Mermaid)
```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'background': '#ffffff' }}}%%
sequenceDiagram
    participant User
    participant StreamlitUI as App (UI)
    participant RAGChain
    participant Retriever
    participant VectorDB as FAISS
    participant LLM as Gemini API

    User->>StreamlitUI: Enters Question
    StreamlitUI->>RAGChain: generate_answer(query)
    
    rect rgb(240, 240, 240)
        Note right of RAGChain: Retrieval Phase
        RAGChain->>Retriever: get_relevant_docs(query)
        Retriever->>VectorDB: similarity_search(query)
        VectorDB-->>Retriever: Returns Top K Chunks
        Retriever-->>RAGChain: List[Document]
    end

    alt No Documents Found
        RAGChain-->>StreamlitUI: "No info found"
    else Documents Found
        rect rgb(240, 248, 255)
            Note right of RAGChain: Generation Phase
            RAGChain->>RAGChain: format_context(docs)
            RAGChain->>LLM: invoke(prompt + context + query)
            LLM-->>RAGChain: Natural Language Answer
        end
        RAGChain-->>StreamlitUI: {answer, source_documents}
    end

    StreamlitUI-->>User: Display Answer + Citations
```
