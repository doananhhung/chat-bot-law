from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from src.config import AppConfig
from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.prompts import QA_PROMPT, format_context
from src.utils.logger import logger

class RAGChain:
    """Orchestrates the RAG flow."""
    
    def __init__(self, retriever: SemanticRetriever):
        self.retriever = retriever
        
        # Initialize LLM
        # Note: API Key is expected in environment variables as GOOGLE_API_KEY
        if not AppConfig.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not found in configuration.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=AppConfig.LLM_MODEL_NAME,
            temperature=0.3, # Low temperature for factual answers
            convert_system_message_to_human=True # Sometimes needed for Gemini
        )
        self.chain = QA_PROMPT | self.llm | StrOutputParser()
        
    def generate_answer(self, query: str) -> Dict[str, Any]:
        """
        Generate answer for the query using RAG.
        Returns dictionary with 'answer' and 'source_documents'.
        """
        # 1. Retrieve
        try:
            docs = self.retriever.get_relevant_docs(query)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"answer": "Lỗi truy xuất dữ liệu.", "source_documents": [], "error": str(e)}
            
        if not docs:
            return {
                "answer": "Tôi không tìm thấy tài liệu nào liên quan đến câu hỏi của bạn.",
                "source_documents": []
            }
            
        # 2. Format Context
        context_str = format_context(docs)
        
        # 3. Generate
        try:
            logger.info("Sending request to LLM...")
            answer = self.chain.invoke({
                "context": context_str,
                "question": query
            })
            
            return {
                "answer": answer,
                "source_documents": docs
            }
            
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể xử lý yêu cầu lúc này (Lỗi kết nối hoặc API).",
                "source_documents": docs, # Still return docs even if LLM fails? Maybe.
                "error": str(e)
            }
