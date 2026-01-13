import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class AppConfig:
    """Centralized configuration management."""
    
    # Project Root
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # Google API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Embedding Model (HuggingFace)
    EMBEDDING_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
    
    # Vector Database
    VECTOR_DB_PATH = os.path.join(PROJECT_ROOT, "data", "vector_store")
    
    # SQL Database (Chat History)
    SQL_DB_PATH = os.path.join(PROJECT_ROOT, "data", "chat_history.db")
    
    # Data Paths
    RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
    
    # Text Splitting
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # --- LLM Factory Config ---
    # Main Generator (RAG)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google") # google, ollama, etc.
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite")
    
    # Router (Intent Classification)
    # Default to use the same provider/model as main if not specified
    ROUTER_PROVIDER = os.getenv("ROUTER_PROVIDER", "google")
    ROUTER_MODEL_NAME = os.getenv("ROUTER_MODEL_NAME", "gemini-2.5-flash-lite")
    
    # Ollama Specific (for self-hosting)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if cls.LLM_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing but provider is set to 'google'. Check your .env file.")
        
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing but provider is set to 'groq'. Check your .env file.")