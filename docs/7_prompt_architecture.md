# Prompt Architecture

## Overview

All LLM prompts are stored in `workflows/Jokestruc/prompts/` directory as separate Python modules. This centralizes prompt management and enables easy updates without modifying node logic.

## Prompt Organization

```
workflows/Jokestruc/prompts/
├── video_insight_prompt.py      # Gemini: Video analysis
├── humor_framer_prompt.py       # Gemini: Humor lever selection
├── caption_generator_prompt.py  # OpenAI: Caption generation
├── caption_selector_prompt.py   # OpenAI: Caption selection (optional)
└── timing_composer_prompt.py    # OpenAI: Timing extraction
```

## Prompt Structure

All prompts follow this pattern:
```python
from textwrap import dedent

PROMPT_NAME = dedent(
    """
    Prompt text with {placeholders}
    for dynamic content.
    """
).strip()
```

**Benefits**:
- `dedent()` removes leading whitespace for readability
- `.strip()` removes trailing newlines
- Placeholders use `.format()` for variable substitution

---

## 1. Video Insight Prompt

**File**: `prompts/video_insight_prompt.py`
**Model**: Google Gemini (`gemini-2.5-flash-lite`)
**Output Format**: Structured JSON via `response_schema`

### Prompt Template
```
You are a meme moment analyst for short-form videos. Your goal is to detect moments
that could be used for memes, captions, or jokes—visually or emotionally funny, awkward,
exaggerated, ironic, or absurd actions.

Return ONLY valid JSON with the following fields:

- raw_description: A vivid one-paragraph summary of the entire clip, describing tone,
  emotion, and what generally happens. Focus on elements that might feel meme-worthy,
  exaggerated, or awkward.

- timeline: An array of 6–10 segments covering the clip in chronological order.
  Each segment should describe the visible on-screen activity in 1–2 sentences,
  and highlight any potentially humorous or meme-worthy aspect.
  Each segment must include:
    • start (float seconds)
    • end (float seconds)
    • description (text: describe what is happening and why it might be funny or ironic)
  Segments should be at least 5 seconds long (≥5s) and can be longer if necessary.
  Ensure the segments together cover the entire clip chronologically.
{duration_hint}

- tags: A list of concise action/activity tags seen in the clip, such as
  'eye roll', 'trip', 'overreaction', 'dramatic pause', 'zoom in', 'confused face', etc.
  If any tag corresponds to humor potential, mark it with '*'.

Respond with strictly valid JSON only—no commentary or text outside the JSON block.
```

### Dynamic Variables
- `{duration_hint}`: Injected as `f"\nVideo duration: {duration_sec} seconds. Ensure all timestamps are within [0, {duration_sec}].\n"`

### Output Schema
Defined in `video_insight_schema.py`:
```python
class VideoInsightModel(BaseModel):
    raw_description: str
    tags: List[str]
    timeline: List[TimelineSegment]
```

### Usage
```python
from .prompts.video_insight_prompt import VIDEO_INSIGHT_PROMPT

duration_hint = f"\nVideo duration: {duration_sec} seconds..."
prompt = VIDEO_INSIGHT_PROMPT.format(duration_hint=duration_hint)
response = model.generate_content(prompt, response_schema=VIDEO_INSIGHT_SCHEMA)
```

---

## 2. Humor Framer Prompt

**File**: `prompts/humor_framer_prompt.py`
**Model**: Google Gemini (`gemini-2.5-flash-lite`)
**Output Format**: JSON (parsed manually)

### Prompt Template
```
You are a meme humor strategist. Analyze the video timeline and select the best humor lever
that matches the content, then generate a framing strategy.

Timeline segments:
{timeline_json}

{tag_line}

Available humor levers:
{lever_json}

Task:
1. Choose exactly ONE humor lever that best fits the video content.
2. Match one timeline segment that aligns with the selected lever.
3. Generate a humor framing text (2-3 sentences) that explains how to apply the lever
   to this segment.

Return strictly valid JSON only:
{{
  "selected_lever": "<lever name>",
  "matched_segment": {{
    "start": <float>,
    "end": <float>,
    "description": "<segment description>",
    "emotional_tone": "<tone>"
  }},
  "framing": "<2-3 sentence humor framing text>"
}}

Rules:
- selected_lever must match one of the lever names from the list above.
- matched_segment must be one of the timeline segments.
- No extra text outside the JSON object.
```

### Dynamic Variables
- `{timeline_json}`: JSON string of timeline segments
- `{tag_line}`: Formatted as `"Tags: tag1, tag2*"` or `"Tags: (none supplied)"`
- `{lever_json}`: JSON string of humor levers from YAML

### Output Format
```json
{
  "selected_lever": "Relatable pain",
  "matched_segment": {
    "start": 6.0,
    "end": 10.0,
    "description": "One player moves their game piece...",
    "emotional_tone": "competitive"
  },
  "framing": "Mechanism: Exaggeration\nTone: Wholesome\n..."
}
```

### Usage
```python
from .prompts.humor_framer_prompt import HUMOR_FRAMER_PROMPT

timeline_json = json.dumps(timeline, ensure_ascii=False)
lever_json = json.dumps(HUMOR_LEVERS, ensure_ascii=False)
prompt = HUMOR_FRAMER_PROMPT.format(
    timeline_json=timeline_json,
    tag_line=tag_line,
    lever_json=lever_json
)
response = model.generate_content(prompt)
```

---

## 3. Caption Generator Prompt

**File**: `prompts/caption_generator_prompt.py`
**Model**: OpenAI (`gpt-4o-mini`)
**Output Format**: Numbered list (parsed manually)

### Prompt Template
```
You are an Instagram meme creator with millions of GenZ followers in India. You know
every trending slang, tone, and reference, and you instinctively craft captions that
are short, punchy, and instantly relatable.

Segment context:
{segment_hint}

Humor lever:
{lever_hint}

Using the timeline and lever, write 3–5 joke captions. Each caption must be a single
line (≤ 50 characters), tuned for GenZ humor, and aligned with the video context.
Return them as a numbered list.
```

### Dynamic Variables
- `{segment_hint}`: Formatted as:
  ```
  Matched segment:
  - Start: {start}
  - End: {end}
  - Description: {description}
  - Emotional tone: {emotional_tone}
  ```
- `{lever_hint}`: Formatted as:
  ```
  The humor lever is {name} (Description: {description} | Example: {example}).
  ```

### Output Format
```
Here are 3 punchy captions for your meme reel:

1. The fate of worlds depends on this dice roll.
2. Friendship level: Ludo champion.
3. When the snacks run out but the drama doesn't.
```

### Usage
```python
from .prompts.caption_generator_prompt import CAPTION_GENERATOR_PROMPT

prompt = CAPTION_GENERATOR_PROMPT.format(
    segment_hint=segment_hint,
    lever_hint=lever_hint
)
response = await run_openai_completion(prompt)
# Parse numbered list from response
```

---

## 4. Caption Selector Prompt

**File**: `prompts/caption_selector_prompt.py`
**Model**: OpenAI (`gpt-4o-mini`)
**Output Format**: JSON (parsed manually)
**Status**: Optional (currently not used in workflow, replaced by human review)

### Prompt Template
```
You are a meme caption judge with razor-sharp GenZ instincts.

Lever context:
- Name: {lever_name}
- Description: {lever_description}
- Example: {lever_example}

Segment context:
{segment_hint}

Candidate captions:
{caption_list}

Choose exactly ONE caption that best fits the lever and segment. Return valid JSON only:
{{
  "selected_index": <number>,
  "reason": "<short explanation>"
}}

Rules:
- selected_index must match a candidate (1-based)
- No extra text outside the JSON object
```

### Dynamic Variables
- `{lever_name}`, `{lever_description}`, `{lever_example}`: From selected lever
- `{segment_hint}`: Same format as caption generator
- `{caption_list}`: Numbered list of candidate captions

### Output Format
```json
{
  "selected_index": 2,
  "reason": "Best aligns with the wholesome friendship tone of the lever"
}
```

---

## 5. Timing Composer Prompt

**File**: `prompts/timing_composer_prompt.py`
**Model**: OpenAI (`gpt-4o-mini`)
**Output Format**: JSON (parsed manually)

### Prompt Template
```
You are a meme caption timing assistant.

Scene mapping entry:
{scene_segment}

Caption to overlay:
{caption}

Task:
Extract the best timing window for the caption described above. Use only the information
in this segment. Return strictly valid JSON:
{{
  "start": <float>,
  "end": <float>,
  "reason": "<short explanation>"
}}

Rules:
- start and end must be floats in seconds.
- start must be less than end.
- If the segment does not include timings, infer a reasonable 2–3 second window
  based on the text.
```

### Dynamic Variables
- `{scene_segment}`: String representation of selected segment (dict or formatted string)
- `{caption}`: User-selected caption text

### Output Format
```json
{
  "start": 6.0,
  "end": 10.0,
  "reason": "Matches the segment timing where the game piece is moved"
}
```

### Usage
```python
from .prompts.timing_composer_prompt import TIMING_COMPOSER_PROMPT

prompt = TIMING_COMPOSER_PROMPT.format(
    scene_segment=str(selected_segment),
    caption=selected_caption
)
response = await run_openai_completion(prompt)
parsed = json.loads(_strip_code_fences(response))
```

---

## Prompt Engineering Best Practices

### 1. Clarity
- Use clear, direct instructions
- Specify output format explicitly
- Include examples when helpful

### 2. Constraints
- Enforce character limits (≤50 for captions)
- Specify minimum/maximum counts (3-5 captions)
- Validate timing bounds (start < end)

### 3. Context
- Provide relevant context (timeline, lever, segment)
- Include duration hints for timestamp validation
- Reference humor style guidelines

### 4. Error Prevention
- Request "strictly valid JSON only"
- Specify field types (float, string, list)
- Include validation rules in prompt

### 5. Persona
- Maintain consistent voice (GenZ meme creator)
- Reference target audience (Indian GenZ)
- Use appropriate tone (relatable, self-aware)

---

## Prompt Versioning

### Current Approach
- Prompts stored in code (versioned with Git)
- Changes require code deployment
- No A/B testing infrastructure

### Future Improvements
- Store prompts in database or config file
- Version prompts with timestamps
- A/B test different prompt variations
- Track prompt performance metrics

---

## Prompt Testing

### Manual Testing
1. Run workflow with sample video
2. Inspect LLM responses at each node
3. Validate output format matches schema
4. Check for edge cases (empty responses, malformed JSON)

### Automated Testing (Future)
- Unit tests for prompt formatting
- Integration tests with mock LLM responses
- Validation tests for output schemas
- Performance tests for prompt length

---

## Common Issues & Solutions

### Issue: LLM returns Markdown code fences
**Solution**: `_strip_code_fences()` function removes ```json``` wrappers

### Issue: LLM returns extra commentary
**Solution**: Explicit "Return strictly valid JSON only" instruction

### Issue: Timestamps out of bounds
**Solution**: Duration hint in prompt + validation in node

### Issue: Caption too long
**Solution**: Character limit in prompt + validation in node

### Issue: Missing required fields
**Solution**: Structured output schema (Gemini) or explicit field list (OpenAI)

---

## Prompt Maintenance

### Regular Updates
- Review prompts quarterly for effectiveness
- Update humor references based on trends
- Adjust character limits based on platform requirements
- Refine instructions based on error patterns

### Documentation
- Document prompt purpose and expected output
- Include examples of good/bad outputs
- Note any known limitations or edge cases
