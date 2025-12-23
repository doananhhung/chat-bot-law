from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from src.config import AppConfig
from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.prompts import QA_PROMPT, GENERAL_PROMPT, format_context
from src.rag_engine.llm_factory import LLMFactory
from src.rag_engine.router import IntentRouter
from src.utils.logger import logger

class RAGChain:
    """Orchestrates the RAG flow with Intent Routing."""
    
    def __init__(self, retriever: SemanticRetriever):
        self.retriever = retriever
        
        # 1. Initialize Main Generator LLM
        self.llm = LLMFactory.create_llm(
            provider=AppConfig.LLM_PROVIDER,
            model_name=AppConfig.LLM_MODEL_NAME,
            temperature=0.3 # Low temp for factual answers
        )
        self.qa_chain = QA_PROMPT | self.llm | StrOutputParser()
        
        # 2. Initialize Router LLM & Router
        # Use Router config, fallback to Main config if needed (handled in config/factory implicitly or explicitly here)
        self.router_llm = LLMFactory.create_llm(
            provider=AppConfig.ROUTER_PROVIDER,
            model_name=AppConfig.ROUTER_MODEL_NAME,
            temperature=0.0 # Lowest temp for classification stability
        )
        self.router = IntentRouter(self.router_llm)
        self.general_chain = GENERAL_PROMPT | self.router_llm | StrOutputParser()
        
    def generate_answer(self, query: str) -> Dict[str, Any]:
        """
        Generate answer for the query.
        
        Flow:
        1. Classify Intent (LEGAL vs GENERAL)
        2. If GENERAL -> Respond conversationally.
        3. If LEGAL -> Retrieve -> RAG Generation.
        """
        # --- Step 1: Intent Classification ---
        try:
            intent = self.router.classify(query)
            logger.info(f"Query Intent: {intent} | Query: '{query}'")
        except Exception as e:
            logger.error(f"Router failed: {e}. Fallback to LEGAL flow.")
            intent = IntentRouter.INTENT_LEGAL

        # --- Step 2: Handle GENERAL Intent ---
        if intent == IntentRouter.INTENT_GENERAL:
            try:
                answer = self.general_chain.invoke({"question": query})
                return {
                    "answer": answer,
                    "source_documents": [],
                    "intent": intent
                }
            except Exception as e:
                logger.error(f"General chat failed: {e}")
                return {"answer": "Xin lỗi, tôi đang gặp sự cố kết nối.", "source_documents": []}

        # --- Step 3: Handle LEGAL Intent (RAG Flow) ---
        # 3.1 Retrieve
        try:
            docs = self.retriever.get_relevant_docs(query)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"answer": "Lỗi truy xuất dữ liệu.", "source_documents": [], "error": str(e)}
            
        if not docs:
            # Even if legal intent, if no docs found, we might want to let LLM handle it gracefully 
            # OR stick to "No info found". For now, stick to "No info found".
            return {
                "answer": "Tôi không tìm thấy tài liệu pháp lý nào liên quan đến câu hỏi của bạn trong cơ sở dữ liệu hiện có.",
                "source_documents": [],
                "intent": intent
            }
            
        # 3.2 Format Context
        context_str = format_context(docs)
        
        # 3.3 Generate
        try:
            logger.info("Sending RAG request to LLM...")
            answer = self.qa_chain.invoke({
                "context": context_str,
                "question": query
            })
            
            return {
                "answer": answer,
                "source_documents": docs,
                "intent": intent
            }
            
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể xử lý yêu cầu lúc này (Lỗi kết nối hoặc API).",
                "source_documents": docs,
                "error": str(e)
            }