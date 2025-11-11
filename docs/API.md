# AI Meme Video Agent - API Documentation

## Overview

The AI Meme Video Agent provides a RESTful API for generating meme videos using AI-powered workflows. The API is built with FastAPI and supports async processing.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication is required. In production, JWT tokens will be implemented.

## Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Meme Video Agent"
}
```

### Generate Meme Video

**POST** `/generate`

Generate a meme video based on input media and description.

**Request Body:**
```json
{
  "media": {
    "filename": "example.mp4",
    "duration": 30,
    "format": "mp4"
  },
  "description": "A funny video about cats",
  "style": "funny"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meme video generated successfully",
  "data": {
    "storyline": "A funny video about cats",
    "captions": ["Funny caption 1", "Funny caption 2"],
    "render_url": "https://memevid.com/renders/example.mp4"
  }
}
```

## Error Responses

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "description"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": null
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, rate limiting will be added.

## Examples

### cURL Examples

**Health Check:**
```bash
curl -X GET http://localhost:8000/health
```

**Generate Video:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "media": {
      "filename": "party.mp4",
      "duration": 30,
      "format": "mp4"
    },
    "description": "Afterparty vibes",
    "style": "funny"
  }'
```

### Python Examples

```python
import httpx

# Health check
response = httpx.get("http://localhost:8000/health")
print(response.json())

# Generate video
data = {
    "media": {
        "filename": "party.mp4",
        "duration": 30,
        "format": "mp4"
    },
    "description": "Afterparty vibes",
    "style": "funny"
}
response = httpx.post("http://localhost:8000/generate", json=data)
print(response.json())
```

## Development

To run the API locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn backend.main:app --reload --port 8000
```

## Production Deployment

The API is designed to be deployed with:
- **Gunicorn** for WSGI server
- **Nginx** for reverse proxy
- **Redis** for caching
- **PostgreSQL** for persistence

## Monitoring

The API includes:
- Health check endpoint for load balancers
- Structured logging
- Error tracking
- Performance metrics (coming soon)
