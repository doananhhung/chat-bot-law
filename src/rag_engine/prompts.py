from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

QA_SYSTEM_PROMPT = """Bạn là trợ lý pháp luật AI chuyên về luật Việt Nam. 
Nhiệm vụ của bạn là trả lời câu hỏi DỰA TRÊN các tài liệu được cung cấp.

NGUYÊN TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên thông tin trong phần [TÀI LIỆU THAM KHẢO]
2. Nếu không tìm thấy thông tin liên quan, trả lời: "Tôi không tìm thấy thông tin về vấn đề này trong các tài liệu hiện có."
3. LUÔN trích dẫn nguồn theo format: [Nguồn: tên_file, Trang: số_trang]
4. Trả lời bằng tiếng Việt
5. Giữ câu trả lời súc tích, rõ ràng
6. KHÔNG bịa đặt thông tin không có trong tài liệu"""

QA_USER_PROMPT_TEMPLATE_STR = """[TÀI LIỆU THAM KHẢO]
{context}

[CÂU HỎI]
{question}

[TRẢ LỜI]
Hãy trả lời câu hỏi trên dựa trên tài liệu tham khảo. Nhớ trích dẫn nguồn."""

QA_PROMPT = PromptTemplate.from_template(
    QA_SYSTEM_PROMPT + "\n\n" + QA_USER_PROMPT_TEMPLATE_STR
)

def format_context(documents: List[Document]) -> str:
    """Format retrieved documents into context string."""
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.strip()
        
        context_parts.append(
            f"--- Tài liệu {i} ---\n"
            f"Nguồn: {source} | Trang: {page}\n"
            f"Nội dung:\n{content}\n"
        )
    
    return "\n".join(context_parts)
