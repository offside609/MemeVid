# Node Definitions

## Overview

This document defines all nodes in the MemeVid workflow, their inputs, outputs, dependencies, and implementation details.

## Node Architecture

All nodes follow this signature:
```python
async def node_name(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node description."""
    # Implementation
    return {"key": "value", "node_done": True}
```

Nodes read from `state` and return updates that are merged into the state.

---

## 1. input_parser

**File**: `workflows/Jokestruc/Nodes/input_parser.py`

**Purpose**: Validates input video file and extracts metadata.

**Inputs**:
- `state["input"]["media_path"]` (str, required)

**Outputs**:
- `state["input"]["duration_sec"]` (float)
- `state["input_parser_done"]` (bool = True)
- `state["logs"]` (appends "input_parser:start", "input_parser:done")

**Dependencies**:
- `video_io.py`: `probe_duration()` function
- FFprobe binary (system dependency)

**Implementation Details**:
- Validates file exists using `os.path.isfile()`
- Uses FFprobe to extract duration: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1`
- Raises `ValueError` if file not found
- Converts duration string to float

**Error Handling**:
- File not found → `ValueError("media_path not found: {path}")`
- FFprobe failure → Exception propagated

---

## 2. video_insight

**File**: `workflows/Jokestruc/Nodes/video_insight/video_insight.py`

**Purpose**: Analyzes video content using Gemini to extract structured insights.

**Inputs**:
- `state["input"]["media_path"]` (str)
- `state["input"]["duration_sec"]` (float)

**Outputs**:
- `state["video_insights"]` (VideoInsightsDict):
  - `raw_description` (str)
  - `timeline` (List[TimelineSegmentDict])
  - `tags` (List[str])
- `state["video_insight_done"]` (bool = True)
- `state["logs"]` (appends "video_insight:start", "video_insight:done")

**Dependencies**:
- `video_io.py`: `upload_video_to_gemini()`, `probe_duration()`
- `video_insight_schema.py`: `VideoInsightModel`, `VIDEO_INSIGHT_SCHEMA`
- `prompts/video_insight_prompt.py`: `VIDEO_INSIGHT_PROMPT`
- Google Gemini API (`genai.GenerativeModel`)
- `llm_provider.py`: `configure_genai()`

**Implementation Details**:
- Uploads video file to Gemini (timeout: 300 seconds)
- Uses `response_schema` for structured JSON output
- Parses response into `VideoInsightModel` (Pydantic)
- Clamps timeline timestamps to `[0, duration_sec]`
- Converts Pydantic model to dict for state storage

**Error Handling**:
- Upload timeout → `TimeoutError` (handled by 300s timeout)
- Invalid JSON → `json.JSONDecodeError` (propagated)
- Missing fields → Pydantic validation error

**Prompt Template**:
- Located in `prompts/video_insight_prompt.py`
- Requests 6-10 segments, minimum 5 seconds each
- Emphasizes meme-worthy moments

---

## 3. humor_framer

**File**: `workflows/Jokestruc/Nodes/humor_framer.py`

**Purpose**: Selects humor lever and generates framing strategy.

**Inputs**:
- `state["video_insights"]["raw_description"]` (str)
- `state["video_insights"]["timeline"]` (List[Dict])
- `state["video_insights"]["tags"]` (List[str])

**Outputs**:
- `state["humor_framing"]` (str)
- `state["selected_lever"]` (Dict[str, str] with keys: name, description, example)
- `state["selected_segment"]` (SelectedSegmentDict)
- `state["humor_framer_done"]` (bool = True)
- `state["logs"]` (appends "humor_framer:start", "humor_framer:done")

**Dependencies**:
- `humor_config.py`: `load_humor_levers()`
- `prompts/humor_framer_prompt.py`: `HUMOR_FRAMER_PROMPT`
- Google Gemini API
- `llm_provider.py`: `configure_genai()`

**Implementation Details**:
- Loads humor levers from YAML on each call (not cached)
- Formats prompt with timeline JSON, tags, and lever options
- Calls Gemini `gemini-2.5-flash-lite` model
- Strips Markdown code fences from response
- Parses JSON to extract lever name, matched segment, and framing text
- Stores full lever dict and segment dict in state

**Error Handling**:
- Missing video_insights → `ValueError`
- JSON parse failure → `json.JSONDecodeError` (with retry logic)
- Empty response → `ValueError`

**Prompt Template**:
- Located in `prompts/humor_framer_prompt.py`
- Asks Gemini to choose one lever and return structured JSON

---

## 4. caption_generator

**File**: `workflows/Jokestruc/Nodes/caption_generator.py`

**Purpose**: Generates multiple candidate captions using OpenAI.

**Inputs**:
- `state["humor_framing"]` (str)
- `state["selected_lever"]` (Dict)
- `state["selected_segment"]` (Dict)
- `state["video_insights"]["raw_description"]` (str)

**Outputs**:
- `state["captions"]` (List[str], 3-5 items)
- `state["caption_generator_done"]` (bool = True)
- `state["logs"]` (appends "caption_generator:start", "caption_generator:done")

**Dependencies**:
- `prompts/caption_generator_prompt.py`: `CAPTION_GENERATOR_PROMPT`
- OpenAI API (`openai.AsyncOpenAI`)
- `llm_provider.py`: `run_openai_completion()`

**Implementation Details**:
- Formats prompt with lever hint and segment hint
- Calls OpenAI GPT model (default: `gpt-4o-mini`)
- Parses numbered list from response (e.g., "1. Caption text")
- Strips numbering and newlines
- Validates each caption ≤50 characters
- Returns list of strings

**Error Handling**:
- Missing humor_framing → `ValueError`
- OpenAI API error → Exception propagated
- No captions parsed → Empty list (may cause downstream error)

**Prompt Template**:
- Located in `prompts/caption_generator_prompt.py`
- Emphasizes GenZ Indian humor, short punchy captions

---

## 5. human_review

**File**: `workflows/Jokestruc/Nodes/human_review.py`

**Purpose**: Pauses workflow for human caption selection (LangGraph interrupt).

**Inputs**:
- `state["captions"]` (List[str])
- `state["selected_lever"]` (Dict, optional)
- `state["selected_segment"]` (Dict, optional)

**Outputs**:
- `state["user_selected_caption"]` (str)
- `state["caption_selection_reason"]` (str, optional)
- `state["logs"]` (appends "human_review:start", "human_review:done")

**Dependencies**:
- LangGraph `interrupt` function
- FastAPI `/resume` endpoint
- Streamlit UI for human interaction

**Implementation Details**:
- Creates interrupt payload with candidates, lever, segment
- Calls `interrupt(payload)` to pause workflow
- Waits for resume with `user_selected_caption` in payload
- Handles both dict and string resume formats
- Validates caption is not empty

**Error Handling**:
- No captions → `ValueError("No captions available for human review")`
- Empty resume payload → `ValueError("Human review did not supply a caption")`

**Resume Mechanism**:
- FastAPI receives `ResumeRequest` with `thread_id` and `user_selected_caption`
- LangGraph `Command(resume=...)` resumes thread
- Workflow continues from next node

---

## 6. timing_composer

**File**: `workflows/Jokestruc/Nodes/timing_composer.py`

**Purpose**: Determines caption overlay timing window.

**Inputs**:
- `state["user_selected_caption"]` (str)
- `state["selected_segment"]` (Dict or str)

**Outputs**:
- `state["timing_plan"]` (TimingPlanDict):
  - `beats`: List with single `TimingBeatDict` (start, end, caption, action, audio_cue)
- `state["timing_composer_done"]` (bool = True)
- `state["logs"]` (appends "timing_composer:start", "timing_composer:done")

**Dependencies**:
- `prompts/timing_composer_prompt.py`: `TIMING_COMPOSER_PROMPT`
- `timing_schema.py`: `TimingBeat`, `TimingPlan` (Pydantic)
- OpenAI API
- `llm_provider.py`: `run_openai_completion()`

**Implementation Details**:
- Formats prompt with selected segment and caption
- Calls OpenAI to extract timing window
- Parses JSON response (start, end, reason)
- Validates start < end
- Creates single `TimingBeat` and wraps in `TimingPlan`
- Converts Pydantic model to dict for state

**Error Handling**:
- Missing caption/segment → `ValueError`
- Invalid timing (end <= start) → `ValueError`
- JSON parse failure → `json.JSONDecodeError`

**Prompt Template**:
- Located in `prompts/timing_composer_prompt.py`
- Asks LLM to extract timing from segment description

---

## 7. dag_composer

**File**: `workflows/Jokestruc/Nodes/dag_composer.py`

**Purpose**: Constructs FFmpeg filter commands for caption overlay.

**Inputs**:
- `state["timing_plan"]["beats"]` (List[TimingBeatDict])
- `state["input"]["media_path"]` (str)

**Outputs**:
- `state["dag_plan"]` (List[Dict[str, Any]])
- `state["output_target"]` (str, output file path)
- `state["dag_composer_done"]` (bool = True)
- `state["logs"]` (appends "dag_composed")

**Dependencies**:
- `utils/ffmpeg_util.py`: `pick_font_path()`, `build_drawtext_filters()`
- Font files in `workflows/Jokestruc/arial/` directory

**Implementation Details**:
- Picks font file path (Arial or fallback)
- For each beat in timing plan:
  - Wraps caption text to fit video width (1280px default)
  - Builds multiple `drawtext` filters (one per wrapped line)
  - Positions text in lower third with proper spacing
- Constructs `filter_complex` string from all filters
- Generates output path: `renders/{input_filename}_captioned.mp4`
- Stores FFmpeg command components in `dag_plan`

**Error Handling**:
- Missing timing_plan → `ValueError`
- Font not found → Falls back to system font
- Text wrapping failure → Exception propagated

**FFmpeg Filter Format**:
```
drawtext=text='Caption text':fontfile='/path/to/font.ttf':fontsize=48:fontcolor=white:box=1:boxcolor=0x00000099:boxborderw=20:x=(w-text_w)/2:y=h-48-...:enable=between(t\,6.0\,10.0)
```

---

## 8. renderer

**File**: `workflows/Jokestruc/Nodes/renderer.py`

**Purpose**: Executes FFmpeg to render final captioned video.

**Inputs**:
- `state["dag_plan"]` (List[Dict])
- `state["input"]["media_path"]` (str)
- `state["output_target"]` (str)

**Outputs**:
- `state["output_path"]` (str, same as output_target)
- `state["renderer_done"]` (bool = True)
- `state["logs"]` (appends "rendered")

**Dependencies**:
- FFmpeg binary (system dependency)
- `subprocess` for command execution
- `asyncio.to_thread` for non-blocking execution

**Implementation Details**:
- Extracts `filter_complex` and file paths from `dag_plan`
- Constructs FFmpeg command:
  ```bash
  ffmpeg -i {input} -filter_complex "{filter_complex}" -c:v libx264 -c:a copy {output}
  ```
- Executes command in thread pool (non-blocking)
- Waits for completion
- Validates output file exists
- Stores output path in state

**Error Handling**:
- FFmpeg execution failure → `subprocess.CalledProcessError`
- Output file not created → `FileNotFoundError`
- Missing dag_plan → `ValueError`

**Performance**:
- Typical 15-second clip: ~10-30 seconds render time
- Depends on video resolution and filter complexity

---

## Node Execution Order

1. `input_parser` → Validates input
2. `video_insight` → Analyzes video
3. `humor_framer` → Selects humor strategy
4. `caption_generator` → Generates candidates
5. `human_review` → **INTERRUPT** (human selection)
6. `timing_composer` → Determines timing
7. `dag_composer` → Builds FFmpeg commands
8. `renderer` → Renders final video

## Common Patterns

### Logging
All nodes append to `state["logs"]`:
```python
logs = state.get("logs", [])
logs.append("node_name:start")
# ... processing ...
logs.append("node_name:done")
return {"logs": logs, "node_name_done": True}
```

### Error Handling
Nodes raise `ValueError` for missing required inputs:
```python
if not required_field:
    raise ValueError("required_field is required for node_name")
```

### State Updates
Nodes return only changed fields (LangGraph merges):
```python
return {
    "new_field": value,
    "node_done": True,
    "logs": logs
}
```
