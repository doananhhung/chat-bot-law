# ⚡ Performance Optimization

## Mục tiêu học tập
Sau khi đọc tài liệu này, bạn sẽ hiểu:
- Các bottlenecks trong hệ thống
- Chiến lược caching với Streamlit
- Query optimization techniques

---

## 1. Performance Challenges

### 1.1 Initial State (No Optimization)

```
Cold Start Problem:
┌─────────────────────────────────────────────────────────────┐
│ User opens app                                               │
│     └── Load Embedding Model (~17s) ← SLOW!                 │
│         └── Load FAISS Index (~0.5s)                        │
│             └── Initialize LLMs (~1s)                       │
│                 └── Ready to chat (~18.5s total)            │
└─────────────────────────────────────────────────────────────┘

Every Page Reload:
Same 18.5s delay! 😢
```

### 1.2 Target State (Optimized)

```
First Load: ~17s (unavoidable - model weight download)
Subsequent Loads: < 1s ✅
Query Response: ~1-2s ✅
```

---

## 2. Caching Strategy

### 2.1 @st.cache_resource

**Purpose**: Cache objects across all sessions and reruns

```python
@st.cache_resource(show_spinner="Đang khởi động Model & Index...")
def get_retriever():
    """Load ONCE, reuse forever."""
    return SemanticRetriever()

@st.cache_resource(show_spinner="Đang kết nối AI...")
def get_rag_chain():
    """Load ONCE, reuse across all users."""
    retriever = get_retriever()
    return RAGChain(retriever)
```

### 2.2 Before vs After

| Metric | Before | After |
|--------|--------|-------|
| **First load** | 17s | 17s |
| **Page reload** | 17s | <1s ✅ |
| **New session** | 17s | <1s ✅ |

### 2.3 What Gets Cached

```
Cached (Singleton):
├── Embedding Model (~1.5GB)
├── FAISS Index (~10MB)
├── LLM connections (3 instances)
└── RAGChain orchestrator

NOT Cached (Per-session):
├── st.session_state
├── Database connections
└── Chat messages
```

---

## 3. Stateless RAGChain Design

### 3.1 Problem: Stateful RAG

```python
# BAD: Stateful design
class RAGChain:
    def __init__(self):
        self.history = []  # ← State stored here
    
    def answer(self, query):
        # Uses internal history
        pass

# Cannot cache! Each user needs different history.
```

### 3.2 Solution: Stateless RAG

```python
# GOOD: Stateless design
class RAGChain:
    def __init__(self):
        # No internal history!
        pass
    
    def answer(self, query, history_str):  # ← History injected
        # Uses externally provided history
        pass

# Can cache! History managed externally by app.py
```

### 3.3 Implementation

```python
# app.py
def format_chat_history(messages):
    """Convert DB messages to string for LLM."""
    buffer = ""
    for msg in messages:
        role = "User" if msg.role == "user" else "AI"
        buffer += f"{role}: {msg.content}\n"
    return buffer

# Usage
history_str = format_chat_history(db_messages)
response = rag_chain.generate_answer(query, chat_history_str=history_str)
```

---

## 4. Database Connection Management

### 4.1 Problem: Connection Leaks

```python
# BAD: Connection never closed
db = SessionLocal()
repo = ChatRepository(db)
# ... use repo ...
# Forgot to close!

# Result: Connection pool exhausted after many reruns
```

### 4.2 Solution: try/finally Pattern

```python
# GOOD: Always close
db = get_db_session()
try:
    repo = ChatRepository(db)
    # ... all logic here ...
finally:
    db.close()  # Always executes, even on error
```

### 4.3 Effect

| Before | After |
|--------|-------|
| Memory grows | Stable memory |
| DB locks | No locks |
| Crashes after ~100 reruns | Runs indefinitely |

---

## 5. FAISS Index Optimization

### 5.1 Index Types Performance

| Index | Latency (1500 vec) | Latency (100K vec) | Accuracy |
|-------|-------------------|-------------------|----------|
| Flat | 138ms | 5000ms | 100% |
| IVF nprobe=8 | 87ms | 200ms | 73% |
| IVF nprobe=32 | 94ms | 300ms | 97% |
| IVF nprobe=64 | 93ms | 400ms | 100% |

### 5.2 Recommended Configuration

```bash
# For current dataset (1500 vectors)
VECTOR_INDEX_TYPE=ivf
IVF_NLIST=64
IVF_NPROBE=32  # 97% recall, minimal latency impact
```

### 5.3 Runtime Mode Switching

```python
# Allow users to trade accuracy for speed
retriever.set_search_mode("speed")    # nprobe=2
retriever.set_search_mode("balanced") # nprobe=8
retriever.set_search_mode("quality")  # nprobe=64
```

---

## 6. Query Latency Breakdown

### 6.1 Typical Query Flow

```
User Query: "Thai sản được nghỉ mấy tháng?"

┌────────────────────────────────────────────────────────┐
│ Step                              │ Time               │
├────────────────────────────────────────────────────────┤
│ 1. Query Rewriting (LLM call)     │ ~200-300ms        │
│ 2. Intent Classification (LLM)    │ ~200-300ms        │
│ 3. Query Embedding                │ ~80-100ms         │
│ 4. FAISS Search                   │ ~10-30ms          │
│ 5. Context Formatting             │ ~5ms              │
│ 6. Answer Generation (LLM)        │ ~500-1000ms       │
├────────────────────────────────────────────────────────┤
│ TOTAL                             │ ~1-2 seconds      │
└────────────────────────────────────────────────────────┘
```

### 6.2 Bottleneck Analysis

```
LLM calls: ~80% of latency
         ↪ 3 calls × ~300-500ms each
         
Local processing: ~20%
         ↪ Embedding: ~100ms
         ↪ FAISS: ~20ms
         ↪ Others: ~50ms
```

---

## 7. LLM Optimization

### 7.1 Parallel LLM Selection

```bash
# Use lightweight model for Router/Rewriter
ROUTER_MODEL_NAME=smaller_model    # If available
REWRITER_MODEL_NAME=smaller_model

# Use powerful model for Generator only
LLM_MODEL_NAME=kimi-k2-instruct-0905
```

### 7.2 Groq vs Google

| Provider | Avg Response | Max Tokens |
|----------|-------------|------------|
| **Groq** | ~300-500ms | 8K |
| Google Gemini | ~500-1000ms | 32K |

**Recommendation**: Use Groq for speed ✅

---

## 8. Cache Invalidation

### 8.1 When to Clear Cache

```python
# After index update
if st.button("🔄 Cập nhật Index"):
    VectorIndexer.sync_index()
    st.cache_resource.clear()  # Clear all cached resources
    st.rerun()
```

### 8.2 What Happens

```
st.cache_resource.clear()
      │
      ▼
┌─────────────────────────────────────────┐
│ Clear:                                  │
│ - get_retriever() → new SemanticRetriever│
│ - get_rag_chain() → new RAGChain        │
│                                         │
│ Next call will:                         │
│ - Reload updated FAISS index            │
│ - Recreate LLM connections              │
└─────────────────────────────────────────┘
```

---

## 9. Memory Optimization

### 9.1 Current Memory Usage

| Component | Memory |
|-----------|--------|
| Embedding Model | ~1.5 GB |
| FAISS Index (1500 vec) | ~10 MB |
| LLM Connections | ~100 MB |
| App overhead | ~200 MB |
| **Total** | **~2 GB** |

### 9.2 Optimization Options (Not implemented)

```python
# Option 1: Use GPU (if available)
model_kwargs={'device': 'cuda'}  # Instead of 'cpu'

# Option 2: Quantized model
model_name = "smaller-quantized-model"

# Option 3: External embedding API
# → Removes 1.5GB model from memory
# → Adds network latency
```

---

## 10. Benchmark Results

### 10.1 System Specs

```
CPU: [Your CPU]
RAM: [Your RAM]
GPU: None (CPU-only)
```

### 10.2 Actual Measurements

| Metric | Value |
|--------|-------|
| Cold start | ~17s |
| Warm page load | <1s |
| Average query | 1.2-1.8s |
| Embedding latency | ~90ms |
| FAISS search | ~20ms |
| LLM generation | ~800ms |

---

## 11. Optimization Summary

| Technique | Impact | Implemented |
|-----------|--------|-------------|
| **@st.cache_resource** | Page reload: 17s → <1s | ✅ |
| **Stateless RAGChain** | Enable caching | ✅ |
| **try/finally DB** | Prevent leaks | ✅ |
| **IVF Index** | Large dataset ready | ✅ |
| **Search modes** | User control | ✅ |
| **Groq LLM** | Faster inference | ✅ |

---

## 12. Key Takeaways

> [!IMPORTANT]
> **Điểm nhấn khi thuyết trình:**
> 1. **@st.cache_resource**: Biến 17s thành <1s cho page reload
> 2. **Stateless design**: Cho phép caching RAGChain
> 3. **IVF index**: Ready cho scale lên 100K vectors
> 4. **Groq API**: Fast inference cho real-time chat

---

## Tài liệu liên quan
- [Streamlit UI](./01_streamlit_ui.md)
- [Demo Script](./04_demo_script.md)
