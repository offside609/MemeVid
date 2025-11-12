"""Prompt template for the timing composer node."""

from textwrap import dedent

TIMING_COMPOSER_PROMPT = dedent(
    """
You are a meme caption timing assistant.

Scene mapping entry:
{scene_segment}

Task:
Extract the best timing window for the caption described above. Use only the information in this segment. Return strictly valid JSON:
{{
  "start": <float>,
  "end": <float>,
  "reason": "<short explanation>"
}}

Rules:
- start and end must be floats in seconds.
- start must be less than end.
- If the segment does not include timings, infer a reasonable 2–3 second window based on the text.
"""
).strip()
