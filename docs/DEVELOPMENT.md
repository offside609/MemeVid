# AI Meme Video Agent - Development Guide

## Project Overview

The AI Meme Video Agent is an async AI-powered system for generating meme videos. It uses a modular node-based architecture with FastAPI for the API layer.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │───▶│  Agent Workflow │───▶│   AI Nodes      │
│                 │    │                 │    │                 │
│ • /health       │    │ • Orchestration │    │ • Ingest        │
│ • /generate     │    │ • State Management│   │ • Perception    │
│ • CORS          │    │ • Error Handling │    │ • Narrative     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
MemeVid/
├── backend/                 # Main application code
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration management
│   ├── nodes/              # AI agent nodes
│   │   ├── base_node.py    # Abstract base class
│   │   ├── ingest_node.py  # Media ingestion
│   │   └── perception_node.py # Content analysis
│   └── database/           # Database models
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── requirements.txt        # Dependencies
```

## Development Setup

### 1. Environment Setup

```bash
# Create virtual environment
conda create -n memevid python=3.11
conda activate memevid

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

Required variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGCHAIN_API_KEY`: LangSmith API key (optional)
- `DEBUG`: Set to "true" for development

### 3. Code Quality Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run quality checks
make quality
```

## Development Workflow

### 1. Code Style

We use automated formatting and linting:

- **Black**: Code formatting
- **Isort**: Import organization
- **Flake8**: Linting
- **MyPy**: Type checking

```bash
# Format code
make format

# Check quality
make quality
```

### 2. Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_config.py -v
```

### 3. Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-node
   ```

2. **Implement feature**
   - Add new node in `backend/nodes/`
   - Add tests in `tests/unit/`
   - Update documentation

3. **Quality checks**
   ```bash
   make quality
   make test
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new perception node"
   ```

## Agent Node Development

### Creating a New Node

1. **Inherit from BaseNode**
   ```python
   from backend.nodes.base_node import BaseNode

   class MyNode(BaseNode):
       async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           # Your node logic here
           pass
   ```

2. **Implement required methods**
   - `process()`: Main processing logic
   - Handle errors gracefully
   - Use async/await for I/O operations

3. **Add tests**
   ```python
   def test_my_node():
       node = MyNode("test_node")
       result = await node.process({"input": "data"})
       assert result["output"] == "expected"
   ```

### Node Best Practices

- **Async operations**: Use `asyncio.sleep()` for I/O simulation
- **Error handling**: Catch and log errors appropriately
- **Logging**: Use the node's logger for debugging
- **Timeout**: Respect the node's timeout setting
- **State management**: Pass state between nodes via dictionaries

## API Development

### Adding New Endpoints

1. **Define request/response models**
   ```python
   class MyRequest(BaseModel):
       field1: str
       field2: int = 10

   class MyResponse(BaseModel):
       success: bool
       data: Dict[str, Any]
   ```

2. **Create endpoint**
   ```python
   @app.post("/my-endpoint", response_model=MyResponse)
   async def my_endpoint(request: MyRequest) -> MyResponse:
       # Implementation
   ```

3. **Add tests**
   ```python
   def test_my_endpoint():
       response = client.post("/my-endpoint", json={"field1": "value"})
       assert response.status_code == 200
   ```

## Database Development

### Adding New Models

1. **Define SQLAlchemy model**
   ```python
   class MyModel(Base):
       __tablename__ = "my_table"

       id = Column(Integer, primary_key=True)
       name = Column(String(100), nullable=False)
   ```

2. **Create migration**
   ```bash
   alembic revision --autogenerate -m "Add my table"
   alembic upgrade head
   ```

3. **Add tests**
   ```python
   def test_my_model():
       model = MyModel(name="test")
       db.add(model)
       db.commit()
       assert model.id is not None
   ```

## Debugging

### Logging

The application uses structured logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing request", extra={"request_id": "123"})
logger.error("Processing failed", exc_info=True)
```

### Debug Mode

Set `DEBUG=true` in `.env` for:
- Detailed error messages
- SQL query logging
- Verbose logging

### Common Issues

1. **Import errors**: Check Python path and virtual environment
2. **Async issues**: Ensure all I/O operations are awaited
3. **Configuration errors**: Verify environment variables
4. **Test failures**: Check test database setup

## Performance Optimization

### Async Best Practices

- Use `asyncio.gather()` for parallel operations
- Avoid blocking I/O in async functions
- Use connection pooling for databases
- Implement proper timeout handling

### Monitoring

- Use structured logging for metrics
- Implement health checks
- Monitor memory usage
- Track request/response times

## Deployment

### Local Development

```bash
# Run with auto-reload
uvicorn backend.main:app --reload --port 8000
```

### Production

```bash
# Run with Gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Follow code style guidelines**
4. **Add tests for new features**
5. **Update documentation**
6. **Submit pull request**

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Async Python Guide](https://docs.python.org/3/library/asyncio.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
