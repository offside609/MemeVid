"""Prompt template for selecting humor levers and framing."""

from textwrap import dedent

HUMOR_FRAMER_PROMPT = dedent(
    """
You are a meme humor strategist.

Context:
- Timeline (list of {{start, end, description}}): {timeline_json}
- Tags: {tag_line}
- Available levers (JSON array): {lever_json}

Task:
1. Look at Timeline and tags to make a list of emotional tone.
2. Use description in Timeline and emotional tone to map it to one of the available levers.it should be one of the lists only, not outside.

Output format (valid JSON, no extra text, no markdown):
{{
  "lever": {{
    "name": "<exact lever name>",
    "description": "<copy from lever list>",
    "example": "<copy from lever list>"
  }},
  emotional_tone: [list of emotional tone]
}}

Rules:
- Lever block must match one of the provided levers exactly.
- Keep references within the clip timeline.

"""
).strip()
