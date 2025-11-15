# Workflow Flow Map

## Overview

The MemeVid workflow is a linear LangGraph state machine that processes video clips through 8 sequential nodes, with one interrupt point for human review.

## Workflow Graph

```
┌─────────────┐
│ input_parser│
└──────┬──────┘
       │
       ▼
┌──────────────┐
│video_insight │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│humor_framer  │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│caption_generator│
└──────┬──────────┘
       │
       ▼
┌──────────────┐
│human_review  │ ◄─── INTERRUPT (awaiting human input)
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│timing_composer  │
└──────┬──────────┘
       │
       ▼
┌──────────────┐
│dag_composer  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   renderer   │
└──────┬───────┘
       │
       ▼
      END
```

## Node Descriptions

### 1. input_parser
**Purpose**: Validate and parse input video file
**Input**: `state["input"]["media_path"]`
**Output**: `state["input"]["duration_sec"]`, `state["input_parser_done"] = True`
**Dependencies**: FFprobe for duration extraction
**Error Handling**: Raises `ValueError` if file not found or invalid

**Flow**:
1. Validate `media_path` exists
2. Extract duration using FFprobe
3. Store duration in state
4. Mark node as complete

---

### 2. video_insight
**Purpose**: Analyze video content using Gemini to extract structured insights
**Input**: `state["input"]["media_path"]`, `state["input"]["duration_sec"]`
**Output**: `state["video_insights"]` (raw_description, timeline, tags), `state["video_insight_done"] = True`
**Dependencies**: Google Gemini API, `video_io.py` for file upload
**Error Handling**: Handles API timeouts (300s), validates JSON response

**Flow**:
1. Upload video file to Gemini
2. Generate content with structured output schema
3. Parse JSON response (raw_description, timeline, tags)
4. Clamp timeline timestamps to video duration
5. Store insights in state

---

### 3. humor_framer
**Purpose**: Select humor lever and generate framing strategy
**Input**: `state["video_insights"]` (raw_description, timeline, tags)
**Output**: `state["humor_framing"]`, `state["selected_lever"]`, `state["selected_segment"]`, `state["humor_framer_done"] = True`
**Dependencies**: Gemini API, `humor_config.py` for lever definitions
**Error Handling**: Strips code fences, validates JSON structure

**Flow**:
1. Load humor levers from YAML config
2. Format prompt with timeline, tags, and lever options
3. Call Gemini to select lever and match segment
4. Parse JSON response (selected lever, matched segment, framing)
5. Store results in state

---

### 4. caption_generator
**Purpose**: Generate multiple candidate captions
**Input**: `state["humor_framing"]`, `state["selected_lever"]`, `state["selected_segment"]`
**Output**: `state["captions"]` (list of strings), `state["caption_generator_done"] = True`
**Dependencies**: OpenAI API
**Error Handling**: Validates caption format, ensures character limits

**Flow**:
1. Format prompt with lever context and segment hint
2. Call OpenAI to generate 3-5 captions
3. Parse numbered list from response
4. Strip numbering and store as list
5. Validate each caption ≤50 characters

---

### 5. human_review (INTERRUPT NODE)
**Purpose**: Pause workflow for human caption selection
**Input**: `state["captions"]`, `state["selected_lever"]`, `state["selected_segment"]`
**Output**: `state["user_selected_caption"]`, `state["caption_selection_reason"]`
**Dependencies**: LangGraph `interrupt`, Streamlit UI
**Error Handling**: Validates human input is not empty

**Flow**:
1. Create interrupt payload with candidates, lever, segment
2. Call `interrupt(payload)` to pause workflow
3. Wait for resume with `user_selected_caption`
4. Store selected caption and optional reason
5. Continue to next node

**Resume Mechanism**:
- FastAPI `/resume` endpoint receives `user_selected_caption`
- LangGraph `Command(resume=...)` resumes thread
- Workflow continues from `timing_composer`

---

### 6. timing_composer
**Purpose**: Determine caption overlay timing window
**Input**: `state["user_selected_caption"]`, `state["selected_segment"]`
**Output**: `state["timing_plan"]` (beats with start/end), `state["timing_composer_done"] = True`
**Dependencies**: OpenAI API
**Error Handling**: Validates start < end, handles missing timestamps

**Flow**:
1. Format prompt with selected segment and caption
2. Call OpenAI to extract timing window
3. Parse JSON response (start, end, reason)
4. Validate timing bounds
5. Create `TimingPlan` with single beat
6. Store in state

---

### 7. dag_composer
**Purpose**: Construct FFmpeg filter commands for caption overlay
**Input**: `state["timing_plan"]`, `state["input"]["media_path"]`
**Output**: `state["dag_plan"]`, `state["output_target"]`, `state["dag_composer_done"] = True`
**Dependencies**: `ffmpeg_util.py` for filter construction
**Error Handling**: Handles text wrapping, font path resolution

**Flow**:
1. Load font path from `arial/` directory
2. For each beat in timing plan:
   - Wrap caption text to fit video width
   - Build `drawtext` filters for each line
   - Position in lower third with proper spacing
3. Construct `filter_complex` string
4. Generate output file path
5. Store FFmpeg command components in state

---

### 8. renderer
**Purpose**: Execute FFmpeg to render final video
**Input**: `state["dag_plan"]`, `state["input"]["media_path"]`, `state["output_target"]`
**Output**: `state["output_path"]`, `state["renderer_done"] = True`
**Dependencies**: FFmpeg binary, subprocess execution
**Error Handling**: Captures FFmpeg errors, validates output file creation

**Flow**:
1. Construct full FFmpeg command from dag_plan
2. Execute FFmpeg subprocess
3. Wait for completion
4. Validate output file exists
5. Store output path in state
6. Mark workflow complete

---

## State Transitions

| From Node | To Node | Condition | State Updates |
|-----------|---------|-----------|---------------|
| START | input_parser | Always | `logs: []` |
| input_parser | video_insight | `input_parser_done == True` | `input["duration_sec"]` |
| video_insight | humor_framer | `video_insight_done == True` | `video_insights` |
| humor_framer | caption_generator | `humor_framer_done == True` | `humor_framing`, `selected_lever`, `selected_segment` |
| caption_generator | human_review | `caption_generator_done == True` | `captions` |
| human_review | timing_composer | Resume with `user_selected_caption` | `user_selected_caption` |
| timing_composer | dag_composer | `timing_composer_done == True` | `timing_plan` |
| dag_composer | renderer | `dag_composer_done == True` | `dag_plan`, `output_target` |
| renderer | END | `renderer_done == True` | `output_path` |

## Error Handling Flow

If any node raises an exception:
1. Exception is caught by LangGraph
2. Workflow state is preserved in checkpointer
3. Error is logged with context
4. API returns error response to client
5. User can inspect state via checkpoint inspection tools

## Parallel Execution Opportunities

Currently, all nodes execute sequentially. Future optimizations could parallelize:
- Video upload and initial analysis (if multiple models needed)
- Caption generation and alternative lever exploration
- Multiple caption candidate generation in parallel

## Checkpointing

- **Development**: `MemorySaver` (in-memory, resets on process restart)
- **Production**: `SqliteSaver` or `PostgresSaver` (persistent across restarts)
- Checkpoints created after each node completion
- Resume capability via `thread_id` and `Command(resume=...)`
