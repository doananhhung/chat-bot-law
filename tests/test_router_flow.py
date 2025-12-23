import pytest
from unittest.mock import MagicMock, patch
from src.rag_engine.router import IntentRouter
from src.rag_engine.generator import RAGChain
from src.rag_engine.llm_factory import LLMFactory

# --- Test IntentRouter ---

@pytest.fixture
def mock_llm():
    return MagicMock()

def test_router_classify_legal(mock_llm):
    """Test router correctly identifies LEGAL intent."""
    # Setup mock response
    mock_llm.invoke.return_value = "LEGAL" # Simulate chain output
    # Note: Router uses chain.invoke, checking internal logic
    
    # We need to mock the chain inside Router because it's created in __init__
    with patch("src.rag_engine.router.PromptTemplate") as MockPrompt:
        with patch("src.rag_engine.router.StrOutputParser") as MockParser:
            router = IntentRouter(mock_llm)
            # Mock the internal chain
            router.chain = MagicMock()
            router.chain.invoke.return_value = "LEGAL"
            
            intent = router.classify("Quy định về hợp đồng lao động")
            assert intent == IntentRouter.INTENT_LEGAL

def test_router_classify_general(mock_llm):
    """Test router correctly identifies GENERAL intent."""
    with patch("src.rag_engine.router.PromptTemplate"), \
         patch("src.rag_engine.router.StrOutputParser"):
        router = IntentRouter(mock_llm)
        router.chain = MagicMock()
        router.chain.invoke.return_value = "GENERAL"
        
        intent = router.classify("Xin chào, bạn khỏe không?")
        assert intent == IntentRouter.INTENT_GENERAL

def test_router_fallback_on_error(mock_llm):
    """Test router falls back to LEGAL on error."""
    with patch("src.rag_engine.router.PromptTemplate"), \
         patch("src.rag_engine.router.StrOutputParser"):
        router = IntentRouter(mock_llm)
        router.chain = MagicMock()
        router.chain.invoke.side_effect = Exception("API Error")
        
        intent = router.classify("Bất kỳ câu hỏi nào")
        assert intent == IntentRouter.INTENT_LEGAL

def test_router_classify_ambiguous_output(mock_llm):
    """Test router handles messy LLM output (e.g., 'The intent is LEGAL')."""
    with patch("src.rag_engine.router.PromptTemplate"), \
         patch("src.rag_engine.router.StrOutputParser"):
        router = IntentRouter(mock_llm)
        router.chain = MagicMock()
        router.chain.invoke.return_value = "The intent is LEGAL."
        
        intent = router.classify("Câu hỏi")
        assert intent == IntentRouter.INTENT_LEGAL


# --- Test RAGChain Integration ---

@pytest.fixture
def mock_retriever():
    return MagicMock()

@pytest.fixture
def rag_chain(mock_retriever):
    # Mock LLMFactory to avoid real API calls during init
    with patch("src.rag_engine.generator.LLMFactory") as MockFactory:
        MockFactory.create_llm.return_value = MagicMock()
        chain = RAGChain(mock_retriever)
        
        # Mock internal components for testing flow
        chain.router = MagicMock()
        chain.general_chain = MagicMock()
        chain.qa_chain = MagicMock()
        
        return chain

def test_rag_flow_general_intent(rag_chain):
    """Test GENERAL intent skips retriever and uses general chain."""
    # Setup
    rag_chain.router.classify.return_value = IntentRouter.INTENT_GENERAL
    rag_chain.general_chain.invoke.return_value = "Chào bạn!"
    
    # Execute
    result = rag_chain.generate_answer("Xin chào")
    
    # Assert
    assert result["answer"] == "Chào bạn!"
    assert result["intent"] == IntentRouter.INTENT_GENERAL
    # Verify Retriever was NOT called
    rag_chain.retriever.get_relevant_docs.assert_not_called()
    # Verify General Chain was called
    rag_chain.general_chain.invoke.assert_called_once()
    # Verify QA Chain was NOT called
    rag_chain.qa_chain.invoke.assert_not_called()

def test_rag_flow_legal_intent(rag_chain):
    """Test LEGAL intent calls retriever and qa chain."""
    # Setup
    rag_chain.router.classify.return_value = IntentRouter.INTENT_LEGAL
    
    # Mock retrieval results
    mock_doc = MagicMock()
    mock_doc.page_content = "Nội dung luật"
    mock_doc.metadata = {"source": "luat.pdf", "page": 1}
    rag_chain.retriever.get_relevant_docs.return_value = [mock_doc]
    
    rag_chain.qa_chain.invoke.return_value = "Câu trả lời pháp lý."
    
    # Execute
    result = rag_chain.generate_answer("Luật hình sự là gì?")
    
    # Assert
    assert result["answer"] == "Câu trả lời pháp lý."
    assert result["intent"] == IntentRouter.INTENT_LEGAL
    # Verify Retriever WAS called
    rag_chain.retriever.get_relevant_docs.assert_called_once()
    # Verify QA Chain WAS called
    rag_chain.qa_chain.invoke.assert_called_once()
    
def test_rag_flow_legal_no_docs(rag_chain):
    """Test LEGAL intent but no documents found."""
    # Setup
    rag_chain.router.classify.return_value = IntentRouter.INTENT_LEGAL
    rag_chain.retriever.get_relevant_docs.return_value = [] # Empty list
    
    # Execute
    result = rag_chain.generate_answer("Câu hỏi lạ")
    
    # Assert
    assert "không tìm thấy tài liệu" in result["answer"]
    # Verify QA Chain was NOT called (saved tokens)
    rag_chain.qa_chain.invoke.assert_not_called()

# --- Test LLM Factory ---

def test_llm_factory_google():
    with patch("src.rag_engine.llm_factory.ChatGoogleGenerativeAI") as MockGemini:
        with patch("src.rag_engine.llm_factory.AppConfig") as MockConfig:
            MockConfig.GOOGLE_API_KEY = "fake_key"
            
            LLMFactory.create_llm("google", "gemini-pro")
            
            MockGemini.assert_called_once()
            _, kwargs = MockGemini.call_args
            assert kwargs["model"] == "gemini-pro"
            assert kwargs["google_api_key"] == "fake_key"

def test_llm_factory_ollama():
    # Mock sys.modules to simulate langchain_community existing or not
    with patch("src.rag_engine.llm_factory.AppConfig") as MockConfig:
        # We need to mock the import inside the method or assume it's installed in env
        # Simpler: just patch the return since we want to test the logic branch
        with patch.dict("sys.modules", {"langchain_community.chat_models": MagicMock()}):
             with patch("langchain_community.chat_models.ChatOllama") as MockOllama:
                LLMFactory.create_llm("ollama", "mistral")
                MockOllama.assert_called_once()
