from typing import Dict, Any, Optional
from langchain_core.output_parsers import StrOutputParser
from src.config import AppConfig
from src.rag_engine.retriever import SemanticRetriever
from src.rag_engine.prompts import (
    QA_PROMPT, 
    GENERAL_PROMPT, 
    CONDENSE_QUESTION_PROMPT,
    format_context
)
from src.rag_engine.llm_factory import LLMFactory
from src.rag_engine.router import IntentRouter
from src.utils.logger import logger
from src.utils.history_manager import InMemoryHistoryManager

class RAGChain:
    """Orchestrates the RAG flow with Intent Routing and Context Memory."""
    
    def __init__(self, retriever: SemanticRetriever):
        self.retriever = retriever
        self.history_manager = InMemoryHistoryManager(max_history_length=10)
        
        # 1. Initialize Main Generator LLM
        self.llm = LLMFactory.create_llm(
            provider=AppConfig.LLM_PROVIDER,
            model_name=AppConfig.LLM_MODEL_NAME,
            temperature=0.3
        )
        self.qa_chain = QA_PROMPT | self.llm | StrOutputParser()
        
        # 2. Initialize Router LLM
        self.router_llm = LLMFactory.create_llm(
            provider=AppConfig.ROUTER_PROVIDER,
            model_name=AppConfig.ROUTER_MODEL_NAME,
            temperature=0.0
        )
        self.router = IntentRouter(self.router_llm)
        self.general_chain = GENERAL_PROMPT | self.router_llm | StrOutputParser()
        
        # 3. Initialize Query Rewriter Chain
        self.condense_question_chain = CONDENSE_QUESTION_PROMPT | self.llm | StrOutputParser()
        
    def generate_answer(self, query: str, session_id: str = "default_session") -> Dict[str, Any]:
        """
        Generate answer for the query with context awareness.
        """
        # --- Step 1: Contextualize Query (Rewriting) ---
        chat_history_str = self.history_manager.get_context_string(session_id)
        standalone_query = query
        
        if chat_history_str:
            try:
                # Rewrite query if there is history
                logger.info("History found. Rewriting query...")
                standalone_query = self.condense_question_chain.invoke({
                    "chat_history": chat_history_str,
                    "question": query
                })
                logger.info(f"Original: '{query}' -> Standalone: '{standalone_query}'")
            except Exception as e:
                logger.error(f"Query rewriting failed: {e}")
                standalone_query = query # Fallback to original

        # --- Step 2: Intent Classification (on Standalone Query) ---
        try:
            # We classify the INTENT based on the rewritten query to see if it's legally relevant
            intent = self.router.classify(standalone_query)
            logger.info(f"Query Intent: {intent} | Query: '{standalone_query}'")
        except Exception as e:
            logger.error(f"Router failed: {e}. Fallback to LEGAL flow.")
            intent = IntentRouter.INTENT_LEGAL

        final_answer = ""
        source_docs = []

        # --- Step 3: Handle GENERAL Intent ---
        if intent == IntentRouter.INTENT_GENERAL:
            try:
                # Chat casually with original query but WITH history
                final_answer = self.general_chain.invoke({
                    "question": query,
                    "chat_history": chat_history_str
                })
            except Exception as e:
                logger.error(f"General chat failed: {e}")
                final_answer = "Xin lỗi, tôi đang gặp sự cố kết nối."

        # --- Step 4: Handle LEGAL Intent (RAG Flow) ---
        else:
            # 4.1 Retrieve (using Standalone Query)
            try:
                docs = self.retriever.get_relevant_docs(standalone_query)
                source_docs = docs
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                final_answer = "Lỗi truy xuất dữ liệu."
            
            if not source_docs and not final_answer:
                final_answer = "Tôi không tìm thấy tài liệu pháp lý nào liên quan đến câu hỏi của bạn trong cơ sở dữ liệu hiện có."
            
            elif not final_answer:
                # 4.2 Format Context & Generate
                context_str = format_context(source_docs)
                try:
                    logger.info("Sending RAG request to LLM...")
                    final_answer = self.qa_chain.invoke({
                        "context": context_str,
                        "question": standalone_query # Use clear query for answer generation
                    })
                except Exception as e:
                    logger.error(f"LLM Generation failed: {e}")
                    final_answer = "Xin lỗi, tôi không thể xử lý yêu cầu lúc này (Lỗi kết nối hoặc API)."

        # --- Step 5: Update History ---
        self.history_manager.add_message(session_id, "user", query) # Save original query
        self.history_manager.add_message(session_id, "assistant", final_answer)

        return {
            "answer": final_answer,
            "source_documents": source_docs,
            "intent": intent,
            "standalone_query": standalone_query # Return for debugging/UI
        }