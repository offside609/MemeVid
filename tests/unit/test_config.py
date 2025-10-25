"""
Unit tests for configuration management
"""

import os
from unittest.mock import patch

import pytest

from backend.config import Config
from backend.config_development import DevelopmentConfig
from backend.config_loader import get_config
from backend.config_production import ProductionConfig


class TestConfig:
    """Test base configuration"""

    def test_config_attributes(self, test_config):
        """Test that config has required attributes"""
        assert hasattr(test_config, "API_TITLE")
        assert hasattr(test_config, "API_VERSION")
        assert hasattr(test_config, "DEBUG")
        assert hasattr(test_config, "OPENAI_API_KEY")
        assert hasattr(test_config, "LOG_LEVEL")

    def test_config_defaults(self, test_config):
        """Test configuration defaults"""
        assert test_config.API_TITLE == "AI Meme Video Agent"
        assert test_config.API_VERSION == "0.1.0"
        assert test_config.LOG_LEVEL == "DEBUG"  # Set in test environment

    def test_config_validation(self, test_config):
        """Test configuration validation"""
        # Should not raise exception for test environment
        assert test_config.validate_config() is True


class TestDevelopmentConfig:
    """Test development configuration"""

    def test_development_config(self):
        """Test development config settings"""
        config = DevelopmentConfig()
        assert config.DEBUG is True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.DATABASE_ECHO is True
        assert config.OPENAI_MODEL == "gpt-3.5-turbo"
        assert config.MAX_RETRIES == 1
        assert config.TIMEOUT_SECONDS == 10

    def test_development_validation(self):
        """Test development config validation"""
        config = DevelopmentConfig()
        # Should not raise exception even without API key
        assert config.validate_config() is True


class TestProductionConfig:
    """Test production configuration"""

    def test_production_config(self):
        """Test production config settings"""
        config = ProductionConfig()
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "WARNING"
        assert config.DATABASE_ECHO is False
        assert config.OPENAI_MODEL == "gpt-4-turbo-preview"
        assert config.MAX_RETRIES == 3
        assert config.TIMEOUT_SECONDS == 60

    def test_production_validation_missing_vars(self):
        """Test production config validation with missing variables"""
        # Clear environment variables to test missing vars
        import os

        original_env = {}
        required_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL",
            "SECRET_KEY",
            "JWT_SECRET_KEY",
        ]

        # Save original values
        for var in required_vars:
            original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        try:
            config = ProductionConfig()
            # Should raise exception without required variables
            with pytest.raises(
                ValueError, match="Missing required environment variables"
            ):
                config.validate_config()
        finally:
            # Restore original environment
            for var, value in original_env.items():
                if value is not None:
                    os.environ[var] = value

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test",
            "SECRET_KEY": "test-secret",
            "JWT_SECRET_KEY": "test-jwt",
        },
    )
    def test_production_validation_with_vars(self):
        """Test production config validation with all variables"""
        config = ProductionConfig()
        assert config.validate_config() is True


class TestConfigLoader:
    """Test configuration loader"""

    def test_get_config_development(self):
        """Test getting development config"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            config = get_config()
            assert isinstance(config, DevelopmentConfig)

    def test_get_config_production(self):
        """Test getting production config"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            config = get_config()
            assert isinstance(config, ProductionConfig)

    def test_get_config_default(self):
        """Test getting default config when environment not set"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert isinstance(config, DevelopmentConfig)

    def test_get_config_unknown(self):
        """Test getting config for unknown environment"""
        with patch.dict(os.environ, {"ENVIRONMENT": "unknown"}):
            config = get_config()
            assert isinstance(
                config, DevelopmentConfig
            )  # Should fallback to development
