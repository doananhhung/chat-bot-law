from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.chat_models import ChatOllama # Uncomment when needed
# from langchain_openai import ChatOpenAI # Uncomment when needed
from src.config import AppConfig
from src.utils.logger import logger

class LLMFactory:
    """
    Factory to create LLM instances based on provider configuration.
    Supports: Google (Gemini), Ollama (Local), OpenAI, etc.
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
                
            elif provider.lower() == "ollama":
                # Lazy import to avoid hard dependency if not used
                try:
                    from langchain_community.chat_models import ChatOllama
                except ImportError:
                    raise ImportError("Please install langchain-community to use Ollama: pip install langchain-community")
                    
                return ChatOllama(
                    model=model_name,
                    base_url=AppConfig.OLLAMA_BASE_URL,
                    **kwargs
                )
                
            # Add more providers here (OpenAI, Anthropic...)
            
            else:
                raise ValueError(f"Unsupported LLM Provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM ({provider}/{model_name}): {e}")
            raise e
