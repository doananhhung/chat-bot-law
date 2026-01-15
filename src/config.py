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

    # --- FAISS Index Configuration ---
    # Index type: "flat" (exact search), "ivf" (approximate), "ivfpq" (approximate + compression)
    VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "flat")

    # IVF-specific parameters
    IVF_NLIST = int(os.getenv("IVF_NLIST", "64"))    # Number of clusters (Voronoi cells)
    IVF_NPROBE = int(os.getenv("IVF_NPROBE", "8"))   # Number of clusters to search at query time

    # Embedding dimension (must match embedding model output)
    EMBEDDING_DIMENSION = 768  # vietnamese-bi-encoder outputs 768D vectors

    @classmethod
    def get_index_factory_string(cls) -> str:
        """Generate FAISS index factory string based on configuration."""
        if cls.VECTOR_INDEX_TYPE == "flat":
            return "Flat"
        elif cls.VECTOR_INDEX_TYPE == "ivf":
            return f"IVF{cls.IVF_NLIST},Flat"
        elif cls.VECTOR_INDEX_TYPE == "ivfpq":
            # PQ48 = 768/16 subvectors, x8 = 8-bit codes
            return f"IVF{cls.IVF_NLIST},PQ48x8"
        else:
            raise ValueError(f"Unknown VECTOR_INDEX_TYPE: {cls.VECTOR_INDEX_TYPE}. Use 'flat', 'ivf', or 'ivfpq'.")
    
    # --- LLM Factory Config ---
    # Main Generator (RAG)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google") # google, ollama, etc.
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite")
    
    # Router (Intent Classification)
    # Default to use the same provider/model as main if not specified
    ROUTER_PROVIDER = os.getenv("ROUTER_PROVIDER", "google")
    ROUTER_MODEL_NAME = os.getenv("ROUTER_MODEL_NAME", "gemini-2.5-flash-lite")

    # Rewriter (Query Reformulation)
    # Default to use the same provider/model as main if not specified
    REWRITER_PROVIDER = os.getenv("REWRITER_PROVIDER", LLM_PROVIDER)
    REWRITER_MODEL_NAME = os.getenv("REWRITER_MODEL_NAME", LLM_MODEL_NAME)

    @classmethod
    def validate(cls):
        """Validate critical configuration for all LLM providers."""
        providers_to_check = [
            ("Main Generator", cls.LLM_PROVIDER),
            ("Router", cls.ROUTER_PROVIDER),
            ("Rewriter", cls.REWRITER_PROVIDER),
        ]

        for name, provider in providers_to_check:
            if provider == "google" and not cls.GOOGLE_API_KEY:
                raise ValueError(
                    f"GOOGLE_API_KEY is missing but {name} provider is set to 'google'. "
                    "Check your .env file."
                )
            if provider == "groq" and not cls.GROQ_API_KEY:
                raise ValueError(
                    f"GROQ_API_KEY is missing but {name} provider is set to 'groq'. "
                    "Check your .env file."
                )