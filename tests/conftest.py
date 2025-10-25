"""
Pytest configuration and fixtures for AI Meme Video Agent
"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "True"
os.environ["LOG_LEVEL"] = "ERROR"

from backend.config_loader import config
from backend.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def test_config():
    """Test configuration"""
    return config


@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {"choices": [{"message": {"content": "Mock AI response for testing"}}]}


@pytest.fixture
def sample_media_input():
    """Sample media input for testing"""
    return {
        "media": {"filename": "test_video.mp4", "duration": 30, "format": "mp4"},
        "description": "Test meme video description",
        "style": "funny",
    }


@pytest.fixture
def sample_agent_node_input():
    """Sample input for agent nodes"""
    return {
        "media": {"filename": "test_video.mp4", "duration": 30, "format": "mp4"},
        "description": "Test description",
        "request_id": "test-request-123",
    }


@pytest.fixture
def mock_redis():
    """Mock Redis connection"""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    return mock_redis


@pytest.fixture
def mock_database():
    """Mock database session"""
    mock_session = Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    return mock_session


@pytest.fixture
def mock_langchain_tracer():
    """Mock LangChain tracer"""
    with patch("langsmith.trace") as mock_trace:
        mock_trace.return_value.__enter__.return_value = Mock()
        yield mock_trace


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    with patch("openai.OpenAI") as mock_client:
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))]
        )
        mock_client.return_value = mock_instance
        yield mock_instance


# Async test fixtures
@pytest.fixture
async def async_client():
    """Async test client for testing async endpoints"""
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Agent node fixtures
@pytest.fixture
def ingest_node():
    """Ingest node for testing"""
    from backend.nodes.ingest_node import IngestNode

    return IngestNode()


@pytest.fixture
def perception_node():
    """Perception node for testing"""
    from backend.nodes.perception_node import PerceptionNode

    return PerceptionNode()


# Test data fixtures
@pytest.fixture
def test_video_generation_data():
    """Test data for video generation"""
    return {
        "request_id": "test-123",
        "description": "Test meme video",
        "style": "funny",
        "filename": "test.mp4",
        "duration": 30,
        "status": "pending",
    }


@pytest.fixture
def test_agent_node_data():
    """Test data for agent node execution"""
    return {
        "generation_id": 1,
        "node_name": "ingest",
        "node_type": "IngestNode",
        "status": "pending",
        "input_data": '{"test": "data"}',
        "output_data": None,
    }


# Environment fixtures
@pytest.fixture(autouse=True)
def test_environment():
    """Set up test environment"""
    # Set test environment variables
    os.environ.update(
        {
            "ENVIRONMENT": "testing",
            "DEBUG": "True",
            "LOG_LEVEL": "ERROR",
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "sqlite:///:memory:",
            "REDIS_URL": "redis://localhost:6379/1",  # Use different DB for tests
        }
    )

    yield

    # Cleanup after test
    # Remove test environment variables if needed
    test_vars = ["ENVIRONMENT", "DEBUG", "LOG_LEVEL"]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]
