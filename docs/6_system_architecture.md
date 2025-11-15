# System Architecture

## Overview

MemeVid is a distributed system with three main components:
1. **FastAPI Backend**: Orchestrates LangGraph workflow and exposes REST API
2. **LangGraph Workflow**: State machine executing video processing pipeline
3. **Streamlit UI**: Human-in-the-loop interface for caption review

## High-Level Architecture

```
┌─────────────────┐
│  Streamlit UI   │ ◄─── User uploads video, reviews captions
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP (httpx)
         ▼
┌─────────────────┐
│  FastAPI Server │ ◄─── Orchestrates workflow
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph App  │ ◄─── State machine with nodes
│  (MemorySaver)   │
└────────┬────────┘
         │
         ├──► Google Gemini API (video analysis)
         ├──► OpenAI API (caption generation)
         └──► FFmpeg (video rendering)
```

## Component Details

### 1. FastAPI Backend

**File**: `workflows/Jokestruc/main.py`

**Responsibilities**:
- Expose REST endpoints (`/jokestruc/generate`, `/jokestruc/resume`)
- Generate unique `thread_id` for each workflow run
- Handle interrupt payloads from LangGraph
- Return workflow state or interrupt information

**Key Functions**:
```python
@router.post("/generate")
async def generate(req: GenerateRequest):
    """Start workflow; return state or interrupt payload."""
    thread_id = str(uuid.uuid4())
    result = await run_graph(initial_state, thread_id)
    # Handle interrupts or return final state

@router.post("/resume")
async def resume(req: ResumeRequest):
    """Resume workflow after human review."""
    final_state = await resume_graph(thread_id, resume_payload)
    return {"thread_id": thread_id, "state": final_state}
```

**Dependencies**:
- `graph.py`: `run_graph()`, `resume_graph()`
- `langgraph.types.Command` for resume mechanism

---

### 2. LangGraph Workflow

**File**: `workflows/Jokestruc/graph.py`

**Architecture**:
- **State Graph**: `StateGraph(JokeState)`
- **Checkpointer**: `MemorySaver()` (in-memory, resets on restart)
- **Nodes**: 8 sequential nodes + 1 interrupt node
- **Edges**: Linear flow with conditional resume

**State Management**:
```python
_memory = MemorySaver()
app = _builder.compile(checkpointer=_memory)
```

**Execution**:
- `run_graph()`: Invokes graph with initial state
- `resume_graph()`: Resumes paused thread with `Command(resume=...)`
- Thread isolation via `thread_id` in config

**Checkpointing**:
- Checkpoints created after each node
- State persisted in `MemorySaver` (or `SqliteSaver` in production)
- Resume capability via `thread_id`

---

### 3. Streamlit UI

**File**: `scripts/streamlit_app.py`

**Responsibilities**:
- File upload interface
- Display candidate captions
- Human caption selection
- Display final rendered video
- Show workflow logs and timing plan

**Key Functions**:
```python
async def start_workflow(media_path: str):
    """POST to /jokestruc/generate and handle response."""
    resp = await client.post(f"{API_BASE}/jokestruc/generate", json={"media_path": media_path})
    # Handle interrupt or completion

async def resume_workflow(thread_id: str, caption: str):
    """POST to /jokestruc/resume with selected caption."""
    resp = await client.post(f"{API_BASE}/jokestruc/resume", json={"thread_id": thread_id, "user_selected_caption": caption})
```

**Dependencies**:
- `httpx.AsyncClient` for API calls
- `streamlit` for UI components
- Timeout: 180 seconds for long-running operations

---

## Data Flow

### Workflow Execution Flow

```
1. User uploads video in Streamlit
   ↓
2. Streamlit POSTs to /jokestruc/generate
   ↓
3. FastAPI creates thread_id, calls run_graph()
   ↓
4. LangGraph executes nodes sequentially:
   - input_parser → video_insight → humor_framer → caption_generator
   ↓
5. human_review node calls interrupt()
   ↓
6. LangGraph returns interrupt payload to FastAPI
   ↓
7. FastAPI returns {"status": "awaiting_review", "payload": {...}}
   ↓
8. Streamlit displays captions, user selects one
   ↓
9. Streamlit POSTs to /jokestruc/resume
   ↓
10. FastAPI calls resume_graph() with user_selected_caption
   ↓
11. LangGraph continues: timing_composer → dag_composer → renderer
   ↓
12. Final state returned to FastAPI
   ↓
13. Streamlit displays rendered video
```

### State Persistence

```
Initial State
  ↓ (checkpoint)
input_parser
  ↓ (checkpoint)
video_insight
  ↓ (checkpoint)
humor_framer
  ↓ (checkpoint)
caption_generator
  ↓ (checkpoint)
human_review [INTERRUPT]
  ← (resume with user_selected_caption)
  ↓ (checkpoint)
timing_composer
  ↓ (checkpoint)
dag_composer
  ↓ (checkpoint)
renderer
  ↓ (checkpoint)
Final State
```

---

## External Dependencies

### 1. Google Gemini API
- **Purpose**: Video content analysis
- **Endpoint**: `genai.upload_file()`, `model.generate_content()`
- **Model**: `gemini-2.5-flash-lite`
- **Timeout**: 300 seconds for file upload
- **Configuration**: `GOOGLE_API_KEY` or `GEMINI_API_KEY` env var

### 2. OpenAI API
- **Purpose**: Caption generation and timing extraction
- **Endpoint**: `openai.AsyncOpenAI().chat.completions.create()`
- **Model**: `gpt-4o-mini` (default)
- **Configuration**: `OPENAI_API_KEY` env var

### 3. FFmpeg
- **Purpose**: Video rendering and caption overlay
- **Binary**: System-installed `ffmpeg` and `ffprobe`
- **Operations**:
  - Duration extraction: `ffprobe -v error -show_entries format=duration`
  - Video rendering: `ffmpeg -i input.mp4 -filter_complex "..." output.mp4`

---

## File System Structure

```
MemeVid/
├── workflows/Jokestruc/
│   ├── Nodes/              # Workflow nodes
│   │   ├── input_parser.py
│   │   ├── video_insight/
│   │   ├── humor_framer.py
│   │   ├── caption_generator.py
│   │   ├── human_review.py
│   │   ├── timing_composer.py
│   │   ├── dag_composer.py
│   │   └── renderer.py
│   ├── prompts/            # LLM prompt templates
│   ├── config/             # Configuration files
│   │   └── humor_levers.yaml
│   ├── utils/              # Utility functions
│   │   └── ffmpeg_util.py
│   ├── graph.py            # LangGraph definition
│   ├── state.py            # State schema
│   └── main.py             # FastAPI router
├── scripts/
│   ├── streamlit_app.py    # Streamlit UI
│   └── inspect_checkpoint.py
├── inputvid/               # Input video directory
├── renders/                # Output video directory
└── workflows/Jokestruc/arial/  # Font files
```

---

## Configuration Management

### Environment Variables
```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...  # or GOOGLE_API_KEY
```

### Configuration Files
- `humor_levers.yaml`: Humor lever definitions
- `prompts/*.py`: LLM prompt templates
- `requirements.txt`: Python dependencies

---

## Error Handling

### API Level
- FastAPI exception handlers catch workflow errors
- Returns 500 with error message
- Logs errors with context

### Workflow Level
- Nodes raise `ValueError` for invalid inputs
- LangGraph preserves state on error
- Checkpoints allow recovery

### UI Level
- Streamlit displays error messages
- Timeout handling (180s)
- Graceful degradation on API failures

---

## Scalability Considerations

### Current Limitations
- **MemorySaver**: In-memory, resets on restart (not production-ready)
- **Single-threaded**: One workflow per process
- **Local file system**: No cloud storage

### Production Recommendations
1. **Persistent Checkpointing**: Use `SqliteSaver` or `PostgresSaver`
2. **Task Queue**: Use Celery or similar for async processing
3. **Cloud Storage**: Store videos in S3/GCS
4. **Caching**: Cache video insights to avoid re-analysis
5. **Load Balancing**: Multiple FastAPI instances behind nginx
6. **Database**: Store workflow metadata and results

---

## Security Considerations

### API Keys
- Loaded from environment variables (never hardcoded)
- Not logged or exposed in responses
- Rotated regularly

### File Access
- Validate file paths to prevent directory traversal
- Restrict file size (100MB limit)
- Sanitize user inputs

### Network
- HTTPS in production
- Rate limiting on API endpoints
- CORS configuration for Streamlit

---

## Monitoring & Observability

### Logging
- Structured logging in all nodes
- Log levels: INFO, WARNING, ERROR
- Context: thread_id, node_name, timestamps

### Metrics (Future)
- Workflow execution time
- Node success/failure rates
- API response times
- Caption selection distribution

### Debugging Tools
- `scripts/inspect_checkpoint.py`: View state at any checkpoint
- LangGraph visualization (future)
- API docs: `http://localhost:8000/docs`

---

## Deployment Architecture

### Development
```
Local Machine:
  - FastAPI: uvicorn app:app --reload
  - Streamlit: streamlit run scripts/streamlit_app.py
  - MemorySaver: In-memory checkpoints
```

### Production (Recommended)
```
Load Balancer (nginx)
  ├── FastAPI Instance 1 (Gunicorn + uvicorn workers)
  ├── FastAPI Instance 2
  └── FastAPI Instance 3

Database (PostgreSQL)
  └── LangGraph checkpoints (PostgresSaver)

Object Storage (S3/GCS)
  ├── Input videos
  └── Rendered outputs

Monitoring
  ├── Application logs (CloudWatch/DataDog)
  └── Metrics (Prometheus/Grafana)
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Workflow Engine | LangGraph | 1.0.2+ |
| API Framework | FastAPI | Latest |
| UI Framework | Streamlit | Latest |
| LLM (Video) | Google Gemini | gemini-2.5-flash-lite |
| LLM (Captions) | OpenAI | gpt-4o-mini |
| Video Processing | FFmpeg | System-installed |
| HTTP Client | httpx | Latest |
| State Schema | TypedDict | Python 3.11+ |
