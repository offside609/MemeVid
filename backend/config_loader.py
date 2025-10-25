"""
Configuration loader for different environments
"""

import os

from .config import Config
from .config_development import DevelopmentConfig
from .config_production import ProductionConfig


def get_config() -> Config:
    """
    Get configuration based on environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "staging": ProductionConfig,  # Use production config for staging
    }

    config_class = config_map.get(env, DevelopmentConfig)

    # Validate configuration
    try:
        config_class.validate_config()
        return config_class()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print(f"Environment: {env}")
        print("Please check your .env file and ensure all required variables are set.")
        raise


# Global config instance
config = get_config()
