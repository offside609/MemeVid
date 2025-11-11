"""
Production-specific configuration
"""

import os

from .config import Config


class ProductionConfig(Config):
    """Production configuration"""

    # Override for production
    DEBUG = False
    LOG_LEVEL = "WARNING"
    DATABASE_ECHO = False

    # Production-specific settings
    OPENAI_MODEL = "gpt-4-turbo-preview"  # Best model for production
    MAX_RETRIES = 3  # More retries for production
    TIMEOUT_SECONDS = 60  # Longer timeouts for production

    # Production database (must be set via environment)
    DATABASE_URL = os.getenv("DATABASE_URL")  # Required in production
    REDIS_URL = os.getenv("REDIS_URL")  # Required in production

    # Production API settings
    CORS_ORIGINS = (
        os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    )

    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY")  # Required in production
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Required in production

    # Performance settings
    WORKER_PROCESSES = int(os.getenv("WORKER_PROCESSES", "8"))
    MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "1000"))

    # Production validation
    @classmethod
    def validate_config(cls) -> bool:
        """Strict validation for production"""
        required_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL",
            "SECRET_KEY",
            "JWT_SECRET_KEY",
        ]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables for production: {missing_vars}"
            )

        return True
