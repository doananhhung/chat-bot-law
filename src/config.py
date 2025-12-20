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
    
    # Embedding Model (HuggingFace)
    EMBEDDING_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
    
    # Vector Database
    VECTOR_DB_PATH = os.path.join(PROJECT_ROOT, "data", "vector_store")
    
    # Data Paths
    RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
    
    # Text Splitting
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # LLM Config
    LLM_MODEL_NAME = "gemini-pro"
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing. Please check your .env file.")
