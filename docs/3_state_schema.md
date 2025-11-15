# State Schema

## Overview

The `JokeState` TypedDict represents the complete state of the MemeVid workflow. It is passed between nodes and persisted via LangGraph checkpoints.

## Type Definitions

### InputPayload
```python
class InputPayload(TypedDict, total=False):
    media_path: str          # Path to input video file
    duration_sec: Optional[float]  # Video duration in seconds (from FFprobe)
```

### TimelineSegmentDict
```python
class TimelineSegmentDict(TypedDict):
    start: float        # Segment start time in seconds
    end: float          # Segment end time in seconds
    description: str    # Text description of segment content
```

### VideoInsightsDict
```python
class VideoInsightsDict(TypedDict, total=False):
    raw_description: str                    # One-paragraph summary of entire clip
    tags: List[str]                         # Action/activity tags (e.g., "eye roll*", "trip")
    timeline: List[TimelineSegmentDict]     # 6-10 chronological segments
```

### TimingBeatDict
```python
class TimingBeatDict(TypedDict):
    start: float        # Beat start time in seconds
    end: float          # Beat end time in seconds
    caption: str        # Caption text to display
    action: str         # Description of action (e.g., "Overlay selected caption on screen")
    audio_cue: str      # Audio cue description (currently empty)
```

### TimingPlanDict
```python
class TimingPlanDict(TypedDict):
    beats: List[TimingBeatDict]  # List of timing beats (typically one for single caption)
```

### SelectedSegmentDict
```python
class SelectedSegmentDict(TypedDict, total=False):
    start: float            # Segment start time
    end: float              # Segment end time
    description: str        # Segment description
    emotional_tone: str    # Emotional tone (e.g., "wholesome", "dramatic")
```

## Complete JokeState Schema

```python
class JokeState(TypedDict, total=False):
    # Input
    input: Optional[InputPayload]

    # Logging
    logs: List[str]                    # Workflow execution log entries

    # Output
    output_path: Optional[str]          # Path to final rendered video

    # Video Analysis
    video_insights: Optional[VideoInsightsDict]

    # Humor Strategy
    humor_framing: Optional[str]       # Generated humor framing text
    selected_lever: Optional[Dict[str, str]]  # Selected humor lever (name, description, example)
    selected_segment: Optional[SelectedSegmentDict]  # Matched timeline segment

    # Caption Generation
    captions: Optional[List[str]]      # List of candidate captions (3-5 items)
    user_selected_caption: Optional[str]  # Human-selected caption

    # Timing
    timing_plan: Optional[TimingPlanDict]

    # Rendering
    dag_plan: Optional[List[Dict[str, Any]]]  # FFmpeg command components
    output_target: Optional[str]       # Output file path for FFmpeg

    # Node Completion Flags
    input_parser_done: bool
    video_insight_done: bool
    humor_framer_done: bool
    caption_generator_done: bool
    scene_mapper_done: bool
    timing_composer_done: bool
    dag_composer_done: bool
    renderer_done: bool
    caption_selector_done: bool
```

## State Lifecycle

### Initial State
```python
{
    "input": {"media_path": "/path/to/video.mp4"},
    "logs": [],
    "input_parser_done": False,
    "video_insight_done": False,
    # ... all other flags False
}
```

### After input_parser
```python
{
    "input": {
        "media_path": "/path/to/video.mp4",
        "duration_sec": 15.5
    },
    "logs": ["input_parser:start", "input_parser:done"],
    "input_parser_done": True,
    # ... other flags still False
}
```

### After video_insight
```python
{
    "video_insights": {
        "raw_description": "Four people playing Ludo...",
        "tags": ["board game*", "laughter", "dice roll"],
        "timeline": [
            {"start": 0.0, "end": 5.0, "description": "..."},
            # ... more segments
        ]
    },
    "video_insight_done": True,
    # ... previous state preserved
}
```

### After humor_framer
```python
{
    "humor_framing": "Mechanism: Exaggeration\nTone: Wholesome\n...",
    "selected_lever": {
        "name": "Relatable pain",
        "description": "Converts everyday GenZ struggles...",
        "example": "When the meeting 'just 5 mins'..."
    },
    "selected_segment": {
        "start": 6.0,
        "end": 10.0,
        "description": "One player moves their game piece...",
        "emotional_tone": "competitive"
    },
    "humor_framer_done": True,
    # ... previous state preserved
}
```

### After caption_generator
```python
{
    "captions": [
        "The fate of worlds depends on this dice roll.",
        "Friendship level: Ludo champion.",
        "When the snacks run out but the drama doesn't."
    ],
    "caption_generator_done": True,
    # ... previous state preserved
}
```

### After human_review (Interrupt Resume)
```python
{
    "user_selected_caption": "Friendship level: Ludo champion.",
    "caption_selection_reason": "Chosen by human reviewer",
    # ... previous state preserved
}
```

### After timing_composer
```python
{
    "timing_plan": {
        "beats": [
            {
                "start": 6.0,
                "end": 10.0,
                "caption": "Friendship level: Ludo champion.",
                "action": "Overlay selected caption on screen",
                "audio_cue": ""
            }
        ]
    },
    "timing_composer_done": True,
    # ... previous state preserved
}
```

### After dag_composer
```python
{
    "dag_plan": [
        {
            "filter_complex": "drawtext=text='Friendship level: Ludo champion.':...",
            "input_file": "/path/to/video.mp4",
            "output_file": "/path/to/renders/video_captioned.mp4"
        }
    ],
    "output_target": "/path/to/renders/video_captioned.mp4",
    "dag_composer_done": True,
    # ... previous state preserved
}
```

### Final State (After renderer)
```python
{
    "output_path": "/path/to/renders/video_captioned.mp4",
    "renderer_done": True,
    "logs": [
        "input_parser:start",
        "input_parser:done",
        "video_insight:start",
        "video_insight:done",
        # ... all node logs
        "rendered"
    ],
    # ... all flags True
}
```

## State Validation Rules

1. **Required Dependencies**:
   - `video_insight` requires `input["duration_sec"]`
   - `humor_framer` requires `video_insights["raw_description"]` and `video_insights["timeline"]`
   - `caption_generator` requires `humor_framing` and `selected_lever`
   - `timing_composer` requires `user_selected_caption` and `selected_segment`
   - `dag_composer` requires `timing_plan`
   - `renderer` requires `dag_plan` and `output_target`

2. **Timing Constraints**:
   - All `start` and `end` times must be non-negative
   - `end` must be greater than `start` for all segments/beats
   - All timestamps must be ≤ `input["duration_sec"]`

3. **Caption Constraints**:
   - Each caption in `captions` must be ≤50 characters
   - `user_selected_caption` must be non-empty string

4. **Completion Flags**:
   - Flags should be set to `True` only after node successfully completes
   - Previous flags remain `True` throughout workflow

## State Serialization

- State is serialized to JSON for checkpointing
- TypedDict ensures type safety at development time
- `total=False` allows optional fields to be omitted
- Lists and nested dicts are JSON-serializable

## State Inspection

Use `scripts/inspect_checkpoint.py` to view state at any checkpoint:
```bash
python scripts/inspect_checkpoint.py <thread_id>
```

This prints the complete state dictionary for debugging and monitoring.
