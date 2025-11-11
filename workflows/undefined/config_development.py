"""
Development-specific configuration
"""

import os

from .config import Config


class DevelopmentConfig(Config):
    """Development configuration"""

    # Override for development
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_ECHO = True

    # Development-specific settings
    OPENAI_MODEL = "gpt-3.5-turbo"  # Cheaper for development
    MAX_RETRIES = 1  # Faster failure for development
    TIMEOUT_SECONDS = 10  # Shorter timeouts for development

    # Development database
    DATABASE_URL = "sqlite:///memevid_dev.db"

    # Development API settings
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Development features
    ENABLE_DEBUG_TOOLBAR = True
    ENABLE_PROFILING = True

    # Relaxed validation for development
    @classmethod
    def validate_config(cls) -> bool:
        """Relaxed validation for development"""
        # Only require OpenAI key, others are optional
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Some features may not work.")
        return True
