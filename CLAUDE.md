# CLAUDE.md - Core Template v1.0

## How This File Works
This file provides context to Claude Code. It is automatically injected into every conversation.
- **Top sections**: Static principles (rarely change)
- **Bottom sections**: Project-specific context (Claude updates as it learns)

---

## General Principles

### Code Quality
- Read existing code before making changes
- Follow existing patterns in the codebase
- Keep changes minimal and focused
- No over-engineering or premature abstractions

### Communication
- Ask clarifying questions when requirements are ambiguous
- Explain trade-offs when multiple approaches exist
- Be direct about limitations or concerns

### Documentation
- Update DEV_LOG.md after significant changes
- Update "Recent Context" section below after updating DEV_LOG
- Keep commit messages descriptive
- Document "why" not just "what"

### When to Read DEV_LOG.md
Read the full DEV_LOG.md when:
- Fixing bugs (check if related issues were solved before)
- Modifying existing features (understand past decisions)
- User asks about project history
- Context in "Recent Context" section is not enough

Skip reading DEV_LOG.md when:
- Answering general questions
- Creating new independent features
- Task has no relation to past work

---

## Workflows

### Bug Fix
1. Reproduce → 2. Find root cause → 3. Fix minimally → 4. Verify → 5. Document

### New Feature
1. Clarify requirements → 2. Check impact on existing code → 3. Implement → 4. Test → 5. Document

### Refactor
1. Ensure tests exist → 2. Small incremental changes → 3. Verify no regression → 4. Document

---

## DEV_LOG Format
```markdown
## [YYYY-MM-DD] Task: [Brief Description]
### Context
Why this change was needed

### Decision
What approach was taken and why

### Impact
What files/systems were affected
```

---

## Recent Context
<!--
Claude: Keep this section updated with the last 3 significant changes.
Format: [Date] Brief description - key insight
This provides quick context without reading the full DEV_LOG.
-->

1. [2026-01-16] Retrieval Mode Selector - Added UI to choose search mode (quality/balanced/speed) for IVF index nprobe tuning
2. [2026-01-15] Code Health Audit & Bug Fixes - Fixed DB session leak in app.py using try/finally, added config validation on startup, removed unused Ollama provider code
3. [2026-01-14] FAISS IVF Clustering - Implemented configurable approximate search (IVF/IVFPQ) for scalability

---

## Project Context
<!--
Claude: Update this section as you learn about the project.
User can also edit this section directly.
-->

**Status**: Production-ready MVP (v1.0)

**Tech Stack**:
- Frontend: Streamlit
- LLM: Google Gemini / Groq (Kimi K2)
- Embedding: bkai-foundation-models/vietnamese-bi-encoder (768D)
- Vector DB: FAISS (Flat/IVF/IVFPQ configurable)
- SQL DB: SQLite + SQLAlchemy ORM
- Framework: LangChain 0.2+

**Key Directories**:
- `app.py` - Main Streamlit entry point
- `src/config.py` - Centralized configuration
- `src/rag_engine/` - RAG core (generator, retriever, router, prompts, llm_factory)
- `src/ingestion/` - ETL pipeline (loader, splitter, indexer, metadata)
- `src/database/` - Persistence layer (models, repository, engine)
- `data/raw/` - Source PDF/DOCX legal documents
- `data/vector_store/` - FAISS index + metadata
- `data/chat_history.db` - SQLite chat persistence

**Architecture Notes**:
- Modular Monolith with clear separation of concerns
- Stateless RAGChain (singleton cached via @st.cache_resource)
- Intent Routing: LEGAL queries → RAG pipeline, GENERAL → casual chat
- Query Rewriting for context-aware follow-up questions
- Incremental indexing (only processes changed files)
- Multi-LLM support via Factory pattern (separate configs for Generator, Router, Rewriter)

**Conventions**:
- Vietnamese UI and prompts
- IRAC structure for legal responses (Issue, Rule, Analysis, Conclusion)
- 0-based page index from PyPDF → +1 for display
- Chunk size: 1000, overlap: 200

**Known Issues / Gotchas**:
- IVF index needs sufficient vectors for training (min = nlist, recommend 39*nlist)
- Cold start ~7-17s due to embedding model loading (mitigated by caching)
- Deprecated `datetime.utcnow()` used (works but should migrate to timezone-aware)
