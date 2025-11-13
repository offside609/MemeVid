# MemeVid – AI Meme Video Agent

Human-in-the-loop LangGraph workflow for turning short clips into captioned meme videos. The backend runs on FastAPI, calls Gemini/OpenAI for analysis and captioning, and renders final videos with FFmpeg. A Streamlit UI keeps a reviewer in the loop to pick the winning joke before rendering.

---

## Features

- **LangGraph workflow** with interrupt/resume for human caption selection  
- **Video insight pipeline** using Gemini structured output  
- **Humor lever selection + caption generation** via OpenAI  
- **FFmpeg rendering** with timing plan to produce captioned clips  
- **Streamlit front-end** for upload, review, and render

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/offside609/MemeVid.git
cd MemeVid
```

### 2. Create & activate environment
```bash
conda create -n memevid python=3.11 -y
conda activate memevid
```

### 3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment variables
Create a `.env` (or export manually) with:
```
OPENAI_API_KEY=...
GEMINI_API_KEY=...     # or GOOGLE_API_KEY
```
Load it when running locally:
```bash
python -c "from dotenv import load_dotenv; load_dotenv()"
```

### 5. Start the FastAPI backend
```bash
uvicorn app:app --reload
```
- API docs: http://localhost:8000/docs  
- Health check: http://localhost:8000/health

### 6. Launch the Streamlit UI
Open a new terminal (same env) and run:
```bash
streamlit run scripts/streamlit_app.py
```
- Upload a video  
- Inspect generated captions  
- Pick the funniest option  
- Streamlit calls `/jokestruc/resume` to render the final meme

---

## Workflow Overview

1. **input_parser** – validates `media_path`  
2. **video_insight** – uploads clip to Gemini, extracts timeline/tags  
3. **humor_framer** – chooses a humor lever and segment  
4. **caption_generator** – requests multiple caption options from OpenAI  
5. **human_review** – LangGraph interrupt; Streamlit displays the choices  
6. **timing_composer** – generates precise timing for the selected caption  
7. **dag_composer** – constructs FFmpeg commands with font + layout  
8. **renderer** – executes FFmpeg to produce `renders/..._captioned.mp4`

---

## Helpful Scripts

| Script | Description |
| --- | --- |
| `scripts/streamlit_app.py` | Streamlit UI for upload & caption review |
| `scripts/inspect_checkpoint.py` | Inspect LangGraph checkpoints (for debugging) |

---

## Development Tips

- Run **pre-commit hooks**: `pre-commit run --all-files`  
- Update dependencies in `requirements.txt` and test by creating a clean env  
- Keep generated videos out of git; they’re ignored via `.gitignore`

---

## License

MIT License – see `LICENSE` for details.  
Questions? Ping the MemeVid maintainers! 💥🎬

