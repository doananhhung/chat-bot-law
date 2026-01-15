from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import AppConfig
from src.utils.logger import logger

class LLMFactory:
    """
    Factory to create LLM instances based on provider configuration.
    Supports: Google (Gemini), Groq.
    """
    
    @staticmethod
    def create_llm(provider: str, model_name: str, **kwargs: Any) -> BaseChatModel:
        """
        Create and return a configured LLM instance.
        
        Args:
            provider: 'google', 'ollama', 'openai', etc.
            model_name: specific model identifier (e.g., 'gemini-pro', 'llama2')
            **kwargs: additional arguments for the LLM class (e.g., temperature)
        """
        logger.info(f"Initializing LLM: Provider={provider}, Model={model_name}")
        
        try:
            if provider.lower() == "google":
                return ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=AppConfig.GOOGLE_API_KEY,
                    convert_system_message_to_human=True,
                    **kwargs
                )

            elif provider.lower() == "groq":
                try:
                    from langchain_groq import ChatGroq
                    from pydantic import SecretStr
                except ImportError:
                    raise ImportError("Please install langchain-groq to use Groq: pip install langchain-groq")

                return ChatGroq(
                    model=model_name,
                    api_key=SecretStr(AppConfig.GROQ_API_KEY) if AppConfig.GROQ_API_KEY else None,
                    **kwargs
                )

            else:
                raise ValueError(f"Unsupported LLM Provider: {provider}. Supported: 'google', 'groq'")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM ({provider}/{model_name}): {e}")
            raise e
