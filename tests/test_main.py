"""
Tests for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "AI Meme Video Agent"}

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_generate_endpoint_structure(client):
    """Test that generate endpoint accepts proper structure"""
    test_data = {
        "media": {
            "filename": "test_video.mp4",
            "duration": 30,
            "format": "mp4"
        },
        "description": "Test meme video",
        "style": "funny"
    }
    
    response = client.post("/generate", json=test_data)
    # Should return 200 (success) or 500 (internal error), not 422 (validation error)
    assert response.status_code in [200, 500]

def test_generate_endpoint_validation(client):
    """Test that generate endpoint validates input"""
    # Test missing required fields
    response = client.post("/generate", json={})
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_async_workflow():
    """Test async workflow execution"""
    # This will test your async node execution
    pass
