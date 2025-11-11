# AI Meme Video Agent

An async AI agent system for generating meme videos with intelligent narrative and caption generation.

## 🚀 Features

- **Async Node Architecture**: Modular, scalable agent nodes
- **FastAPI Backend**: High-performance async API
- **AI Integration**: OpenAI, LangChain, LangGraph support
- **In-Memory Persistence**: Fast state management
- **Production Ready**: Proper logging, error handling, monitoring

## 📁 Project Structure

```
MemeVid/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── graphs/              # LangGraph workflows
│   ├── nodes/               # Agent nodes
│   │   ├── base_node.py     # Base node class
│   │   ├── ingest_node.py   # Media ingestion
│   │   ├── perception_node.py # Content analysis
│   │   └── ...              # Other nodes
│   └── database/            # Database models
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── logs/                    # Log files
```

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Conda environment
- OpenAI API key

### Installation

1. **Clone and navigate to project**
   ```bash
   cd MemeVid
   ```

2. **Activate conda environment**
   ```bash
   conda activate your_env_name
   ```

3. **Install dependencies**
   ```bash
   # Production dependencies
   pip install -r requirements.txt

   # Development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   uvicorn app:app --reload --port 8000

6. **Curl for getting output
   curl -X POST http://localhost:8000/jokestruc/generate \
  -H "Content-Type: application/json" \
  -d '{
        "media_path": "/Users/admin/Documents/MemeVid/workflows/Jokestruc/zostel_demo_video.mp4"
      }'

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_main.py
```

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference with examples
- [Development Guide](docs/DEVELOPMENT.md) - Setup, architecture, and contribution guide
- [Project Structure](#-project-structure) - Overview of code organization

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Development

### Code Quality
```bash
# Format code
black backend/ tests/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Pre-commit Hooks
```bash
# Install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🚀 Deployment

### Production Setup
1. Set production environment variables
2. Configure database (PostgreSQL/Redis)
3. Set up monitoring (LangSmith)
4. Deploy with Docker/Gunicorn

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_key

# Optional
DEBUG=False
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/0
```

## 🤖 Agent Architecture

### Node Types
- **IngestNode**: Media file processing
- **PerceptionNode**: Content analysis
- **NarrativeNode**: Story generation
- **TemplateNode**: Template selection
- **CaptionNode**: Caption generation
- **RenderNode**: Video rendering

### Workflow
1. **Ingest** → Process media input
2. **Perceive** → Analyze content
3. **Narrate** → Generate storyline
4. **Template** → Select meme template
5. **Caption** → Generate captions
6. **Render** → Create final video

## 📊 Monitoring

- **LangSmith**: AI workflow tracing
- **Logs**: Structured logging
- **Metrics**: Performance tracking
- **Health**: System status

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details
