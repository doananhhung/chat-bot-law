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
st.set_page_config(page_title="Trợ lý Pháp Luật AI", layout="wide")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def build_index():
    """Run the ingestion pipeline."""
    try:
        with st.status("Đang xử lý dữ liệu...", expanded=True) as status:
            st.write("Đang đọc tài liệu...")
            load_result = DocumentLoader.load_documents(AppConfig.RAW_DATA_PATH)
            
            if not load_result.documents:
                status.update(label="Không tìm thấy tài liệu!", state="error")
                return
                
            st.write(f"Đã đọc {len(load_result.documents)} trang/file.")
            
            st.write("Đang chia nhỏ văn bản...")
            chunks = TextSplitter.split_documents(load_result.documents)
            st.write(f"Đã tạo {len(chunks)} phân đoạn.")
            
            st.write("Đang tạo Vector Index (Điều này có thể mất vài phút)...")
            VectorIndexer.build_index(chunks)
            
            status.update(label="Xử lý dữ liệu thành công!", state="complete")
            st.success("Hệ thống đã sẵn sàng!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Lỗi hệ thống: {str(e)}")

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
                    st.caption(f"📄 **{source}** (Trang {page})")
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
                        st.caption(f"📄 **{source}** (Trang {page})")
                        st.text(doc.page_content[:300] + "...")

    # Save history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response["answer"],
        "sources": response.get("source_documents", [])
    })
