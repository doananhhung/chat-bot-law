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

# Database Imports
from src.database.engine import init_db, SessionLocal
from src.database.repository import ChatRepository

# Page Config
st.set_page_config(page_title="Trợ lý Luật Lao Động AI", layout="wide")

# --- Database Initialization ---
try:
    init_db()
    AppConfig.validate()  # Validate LLM configuration on startup
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    raise e

# --- Helper Functions ---
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

def get_db_session():
    return SessionLocal()

def format_chat_history(messages):
    """Convert list of DB objects to string format for LLM."""
    buffer = ""
    for msg in messages:
        role = "User" if msg.role == "user" else "AI"
        buffer += f"{role}: {msg.content}\n"
    return buffer

def display_sources(sources):
    """Helper to display source documents in an expander."""
    if sources:
        with st.expander("📚 Nguồn tham khảo"):
            for doc in sources:
                # Handle both dict (from DB) and Document object (from RAG)
                if isinstance(doc, dict):
                    source = doc.get("source", "Unknown")
                    page = doc.get("page", "N/A")
                    content = doc.get("page_content", "") or doc.get("content", "")
                else:
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page", "N/A")
                    content = doc.page_content

                try:
                    # Convert 0-based to 1-based for UI
                    page_display = int(page) + 1
                except (ValueError, TypeError):
                    page_display = page
                st.caption(f"📄 **{source}** (Trang {page_display})")
                st.text(content[:300] + "...")

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

def handle_delete_session(repo, session_id):
    """Delete a session. If active, switch to another."""
    is_active = (session_id == st.session_state.session_id)
    
    repo.delete_session(session_id)
    
    if is_active:
        # Try to find another session
        remaining = repo.get_recent_sessions(limit=1)
        if remaining:
            st.session_state.session_id = remaining[0].id
        else:
            # If no sessions left, create a new one
            new_sess = repo.create_session(title="Cuộc hội thoại mới")
            st.session_state.session_id = new_sess.id
    
    st.rerun()

def handle_delete_all_sessions(repo):
    """Delete all sessions and create a fresh one."""
    repo.delete_all_sessions()
    new_sess = repo.create_session(title="Cuộc hội thoại mới")
    st.session_state.session_id = new_sess.id
    st.rerun()

# --- Session Management ---
if "session_id" not in st.session_state:
    # Initialize a new session in DB
    db = get_db_session()
    repo = ChatRepository(db)
    new_session = repo.create_session(title="Cuộc hội thoại mới")
    st.session_state.session_id = new_session.id
    db.close()

if "search_mode" not in st.session_state:
    st.session_state.search_mode = "balanced"

# --- Main UI ---
st.title("🤖 Trợ lý AI Tra cứu Pháp Luật")

# Database Connection for this run (with proper cleanup)
db = get_db_session()
try:
    repo = ChatRepository(db)

    # Sidebar
    with st.sidebar:
        st.header("🗂️ Quản lý Hội thoại")

        if st.button("➕ Cuộc hội thoại mới", use_container_width=True):
            new_session = repo.create_session(title="Cuộc hội thoại mới")
            st.session_state.session_id = new_session.id
            st.rerun()

        st.divider()
        st.subheader("Gần đây")

        recent_sessions = repo.get_recent_sessions(limit=10)
        for s in recent_sessions:
            col_nav, col_del = st.columns([0.8, 0.2])

            with col_nav:
                # Highlight active session
                button_type = "primary" if s.id == st.session_state.session_id else "secondary"
                label = s.title if s.title else "Không tiêu đề"
                if st.button(f"💬 {label}", key=f"nav_{s.id}", type=button_type, use_container_width=True):
                    st.session_state.session_id = s.id
                    st.rerun()

            with col_del:
                if st.button("✕", key=f"del_{s.id}", help="Xóa hội thoại này", use_container_width=True):
                    handle_delete_session(repo, s.id)

        st.divider()
        with st.expander("⚙️ Quản lý Dữ liệu"):
            st.info(f"Nguồn: `{AppConfig.RAW_DATA_PATH}`")
            if st.button("🔄 Cập nhật Index"):
                build_index()

            st.divider()

            if st.button("🔥 Xóa toàn bộ dữ liệu chat", type="primary", use_container_width=True):
                handle_delete_all_sessions(repo)

        # Search Mode Selector
        retriever = get_retriever()
        if retriever:
            mode_info = retriever.get_current_search_mode()
            if mode_info.get("is_ivf"):
                with st.expander("⚡ Chế độ tìm kiếm"):
                    search_mode = st.radio(
                        "Chọn chế độ:",
                        options=["balanced", "quality", "speed"],
                        format_func=lambda x: {
                            "quality": "🎯 Chính xác cao",
                            "balanced": "⚖️ Cân bằng (Khuyến nghị)",
                            "speed": "🚀 Tốc độ cao"
                        }[x],
                        index=["balanced", "quality", "speed"].index(st.session_state.search_mode),
                        key="search_mode_radio",
                        help="Điều chỉnh cân bằng giữa tốc độ và độ chính xác"
                    )

                    # Update session state if changed
                    if search_mode != st.session_state.search_mode:
                        st.session_state.search_mode = search_mode
                        retriever.set_search_mode(search_mode)
                        st.rerun()

                    # Display current mode info
                    current_info = retriever.get_current_search_mode()
                    st.caption(f"📊 Phạm vi: {current_info['search_scope_pct']}% clusters ({current_info['nprobe']}/{current_info['nlist']})")
            else:
                with st.expander("⚡ Chế độ tìm kiếm"):
                    st.info("Index hiện tại là Flat (tìm kiếm chính xác), không cần điều chỉnh.")

    # Main Chat Area
    current_session_id = st.session_state.session_id
    messages = repo.get_messages(current_session_id)

    # Display History
    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
            if msg.role == "assistant":
                if msg.standalone_query:
                    with st.expander("🧠 Tư duy ngữ cảnh"):
                        st.info(f"AI đã hiểu: **{msg.standalone_query}**")
                if msg.sources:
                    display_sources(msg.sources)

    # Chat Input
    rag_chain = get_rag_chain()

    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        # 1. Display User Message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Save User Message to DB
        repo.add_message(current_session_id, "user", prompt)

        # 3. Generate Answer
        with st.chat_message("assistant"):
            if not rag_chain:
                st.error("Hệ thống chưa sẵn sàng.")
                answer = "Lỗi hệ thống."
                sources = []
            else:
                with st.spinner("Đang tra cứu và phân tích..."):
                    # Format history for Context
                    history_str = format_chat_history(messages)  # Use DB messages

                    # Update Session Title if it's the first message
                    if len(messages) == 0:
                        # Simple heuristic: Use first 6 words of prompt
                        new_title = " ".join(prompt.split()[:6]) + "..."
                        repo.update_session_title(current_session_id, new_title)

                    # Apply search mode before querying
                    retriever = get_retriever()
                    if retriever:
                        retriever.set_search_mode(st.session_state.search_mode)

                    # Call RAG
                    response = rag_chain.generate_answer(prompt, chat_history_str=history_str)
                    answer = response["answer"]

                    # Normalize sources for DB storage (must be JSON serializable)
                    # RAG returns Document objects, we need dicts
                    raw_sources = response.get("source_documents", [])
                    json_sources = []
                    for doc in raw_sources:
                        json_sources.append({
                            "source": doc.metadata.get("source", "Unknown"),
                            "page": doc.metadata.get("page", "N/A"),
                            "page_content": doc.page_content
                        })

                    standalone = response.get("standalone_query")

                st.markdown(answer)

                if standalone and standalone != prompt:
                    with st.expander("🧠 Tư duy ngữ cảnh"):
                        st.info(f"AI đã hiểu: **{standalone}**")

                display_sources(json_sources)

                # 4. Save Assistant Message to DB
                standalone_to_save = standalone if (standalone and standalone != prompt) else None
                repo.add_message(current_session_id, "assistant", answer,
                                 sources=json_sources, standalone_query=standalone_to_save)

        # 5. Rerun to refresh UI/Sidebar
        st.rerun()

finally:
    # Ensure DB connection is always closed
    db.close()
