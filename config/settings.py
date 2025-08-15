import os
import logging
from typing import Optional
from langchain.chat_models import init_chat_model

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("Settings")

class Settings:
    """💡 Centralized Configuration for the AI Dev Pipeline"""
    _llm_instance = None

    # === 🚀 Runtime Environment Variables ===
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "your-org/your-repo")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://memory_cache:6379/0")
    AGENTS_FOLDER = os.getenv("AGENTS_FOLDER", "agents")
    PROVIDER = os.getenv("PROVIDER", "openai")

    # === 🤖 LLM Model Settings ===
    MODEL = os.getenv("MODEL", "gpt-4o")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
    BASE_URL: Optional[str] = os.getenv("BASE_URL", "https://api.openai.com/v1")

    @classmethod
    def get_llm(cls):
        """🔁 Get or initialize the chat LLM instance via LangChain."""
        if cls._llm_instance is None:
            try:
                cls._llm_instance = init_chat_model(
                    model=cls.MODEL,
                    temperature=cls.TEMPERATURE,
                    max_tokens=cls.MAX_TOKENS,
                    api_key=cls.OPENAI_API_KEY,
                    base_url=cls.BASE_URL,
                    model_provider=cls.PROVIDER
                )
                logger.info(f"✅ LLM initialized: {cls.MODEL} (via {cls.PROVIDER})")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LLM: {e}")
                raise
        return cls._llm_instance

    @classmethod
    def validate(cls):
        """✅ Validate required environment variables."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("❌ Missing OPENAI_API_KEY")
        if not cls.GITHUB_TOKEN:
            errors.append("❌ Missing GITHUB_TOKEN")
        if not cls.GITHUB_REPO:
            errors.append("❌ Missing GITHUB_REPO")

        if errors:
            for err in errors:
                logger.error(err)
            raise EnvironmentError("❌ Configuration validation failed.")
        
        logger.info("✅ All required configuration variables are set.")
