import streamlit as st
import time
import uuid
from src.config import AppConfig
from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.generator import RAGChain
from src.ingestion.loader import DocumentLoader
from src.ingestion.splitter import TextSplitter
from src.ingestion.indexer import VectorIndexer
from src.utils.logger import logger

# Page Config
st.set_page_config(page_title="Trợ lý Luật Lao Động AI", layout="wide")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

@st.cache_resource(show_spinner="Đang khởi động Model & Index...")
def get_retriever():
    """Load and cache the Retriever (Embedding Model + FAISS Index)."""
    try:
        return SemanticRetriever()
    except RuntimeError:
        return None

@st.cache_resource(show_spinner="Đang kết nối AI...")
def get_rag_chain():
    """Initialize and cache the RAG Chain logic (Stateless)."""
    retriever = get_retriever()
    if retriever:
        return RAGChain(retriever)
    return None

def build_index():
    """Run the incremental ingestion pipeline."""
    try:
        with st.status("Đang đồng bộ dữ liệu...", expanded=True) as status:
            st.write("Đang quét thư mục và kiểm tra thay đổi...")
            VectorIndexer.sync_index()
            
            # Clear cache to reload new index next time
            st.cache_resource.clear()
            
            status.update(label="Đồng bộ dữ liệu thành công!", state="complete")
            st.success("Hệ thống đã cập nhật những thay đổi mới nhất!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Lỗi khi đồng bộ dữ liệu: {str(e)}")

def format_chat_history(history):
    """Convert list of dicts to string format for LLM."""
    buffer = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "AI"
        buffer += f"{role}: {msg['content']}\n"
    return buffer

# --- UI ---
st.title("🤖 Trợ lý AI Tra cứu Pháp Luật")

# Sidebar
with st.sidebar:
    st.header("Quản lý Dữ liệu")
    st.info(f"Thư mục dữ liệu: `{AppConfig.RAW_DATA_PATH}`")
    
    if st.button("🔄 Cập nhật Dữ liệu"):
        build_index()
        
    st.divider()
    if st.button("🧹 Xóa Lịch sử Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Main Chat Logic
rag_chain = get_rag_chain()

def display_sources(sources):
    """Helper to display source documents in an expander."""
    if sources:
        with st.expander("📚 Nguồn tham khảo"):
            for doc in sources:
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "N/A")
                try:
                    # Convert 0-based to 1-based for UI
                    page_display = int(page) + 1
                except (ValueError, TypeError):
                    page_display = page
                st.caption(f"📄 **{source}** (Trang {page_display})")
                st.text(doc.page_content[:300] + "...")

# Display History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg:
            display_sources(msg["sources"])

# Chat Input
if prompt := st.chat_input("Nhập câu hỏi của bạn về văn bản pháp luật..."):
    # Add user message to history and display immediately
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate Answer
    with st.chat_message("assistant"):
        if not rag_chain:
            st.error("Hệ thống chưa sẵn sàng. Vui lòng kiểm tra cấu hình hoặc Build Index.")
            answer = "Lỗi hệ thống."
            sources = []
            standalone = None
        else:
            with st.spinner("Đang suy nghĩ..."):
                # Get history as string for context
                history_str = format_chat_history(st.session_state.chat_history[:-1]) # Exclude current prompt
                
                response = rag_chain.generate_answer(prompt, chat_history_str=history_str)
                answer = response["answer"]
                sources = response.get("source_documents", [])
                standalone = response.get("standalone_query")
                
            st.markdown(answer)
            
            # Show Debug Info (Standalone Query)
            if standalone and standalone != prompt:
                with st.expander("🧠 Tư duy ngữ cảnh (Debug)"):
                    st.info(f"AI đã hiểu câu hỏi là: **{standalone}**")
            
            # Show sources
            display_sources(sources)

    # Save to history and rerun to clean up UI
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": answer,
        "sources": sources
    })
    st.rerun()