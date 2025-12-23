from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.logger import logger

class IntentRouter:
    """
    Classifies user queries into intents (e.g., LEGAL vs GENERAL).
    """
    
    INTENT_LEGAL = "LEGAL"
    INTENT_GENERAL = "GENERAL"
    
    ROUTER_TEMPLATE = """Bạn là bộ phân loại câu hỏi cho một Trợ lý Luật sư AI.
    
    Nhiệm vụ: Phân loại câu hỏi của người dùng vào một trong hai nhóm sau:
    1. "LEGAL": Câu hỏi liên quan đến luật pháp Việt Nam, quy định, nghị định, thủ tục hành chính, tra cứu luật, hoặc các vấn đề pháp lý.
    2. "GENERAL": Câu hỏi chào hỏi, xã giao, thời tiết, toán học, lập trình, khen ngợi, hoặc các kiến thức không liên quan đến luật pháp.

    Yêu cầu đầu ra: CHỈ trả về đúng 1 từ duy nhất: "LEGAL" hoặc "GENERAL". Không giải thích thêm.

    Câu hỏi: {question}
    
    Phân loại:"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(self.ROUTER_TEMPLATE)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def classify(self, query: str) -> str:
        """
        Classify the user query.
        Returns: 'LEGAL' or 'GENERAL'
        """
        try:
            # clean whitespace
            query = query.strip()
            if not query:
                return self.INTENT_GENERAL
                
            result = self.chain.invoke({"question": query})
            intent = result.strip().upper()
            
            # Fallback/Safety check if LLM chats too much
            if "LEGAL" in intent:
                return self.INTENT_LEGAL
            return self.INTENT_GENERAL
            
        except Exception as e:
            logger.warning(f"Router classification failed: {e}. Defaulting to LEGAL.")
            return self.INTENT_LEGAL # Fail-safe to LEGAL to try answering anyway
