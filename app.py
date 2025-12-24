import streamlit as st
import time
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

def build_index():
    """Run the incremental ingestion pipeline."""
    try:
        with st.status("Đang đồng bộ dữ liệu...", expanded=True) as status:
            st.write("Đang quét thư mục và kiểm tra thay đổi...")
            VectorIndexer.sync_index()
            
            status.update(label="Đồng bộ dữ liệu thành công!", state="complete")
            st.success("Hệ thống đã cập nhật những thay đổi mới nhất!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Lỗi khi đồng bộ dữ liệu: {str(e)}")

def get_rag_chain():
    """Initialize RAG Chain (Cached in resource is not possible with custom classes easily, use session state)."""
    if "rag_chain" not in st.session_state:
        try:
            retriever = SemanticRetriever()
            st.session_state.rag_chain = RAGChain(retriever)
        except Exception as e:
            st.error(f"Không thể khởi động hệ thống: {e}")
            return None
    return st.session_state.rag_chain

# --- UI ---
st.title("🤖 Trợ lý AI Tra cứu Pháp Luật")

# Sidebar
with st.sidebar:
    st.header("Quản lý Dữ liệu")
    st.info(f"Thư mục dữ liệu: `{AppConfig.RAW_DATA_PATH}`")
    
    if st.button("🔄 Cập nhật Dữ liệu"):
        build_index()
        
 

# Main Chat
rag_chain = get_rag_chain()

# Display History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Nguồn tham khảo"):
                for doc in msg["sources"]:
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page", "N/A")
                    try:
                        page_display = int(page) + 1
                    except (ValueError, TypeError):
                        page_display = page
                    st.caption(f"📄 **{source}** (Trang {page_display})")
                    st.text(doc.page_content[:300] + "...")

# Chat Input
if prompt := st.chat_input("Nhập câu hỏi của bạn về văn bản pháp luật..."):
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate Answer
    with st.chat_message("assistant"):
        if not rag_chain:
            st.error("Hệ thống chưa sẵn sàng. Vui lòng kiểm tra cấu hình hoặc Build Index.")
            response = {"answer": "Lỗi hệ thống.", "source_documents": []}
        else:
            with st.spinner("..."):
                response = rag_chain.generate_answer(prompt)
                
            st.markdown(response["answer"])
            
            # Show sources
            if response.get("source_documents"):
                with st.expander("📚 Nguồn tham khảo"):
                    for doc in response["source_documents"]:
                        source = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", "N/A")
                        try:
                            page_display = int(page) + 1
                        except (ValueError, TypeError):
                            page_display = page
                        st.caption(f"📄 **{source}** (Trang {page_display})")
                        st.text(doc.page_content[:300] + "...")

    # Save history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response["answer"],
        "sources": response.get("source_documents", [])
    })
