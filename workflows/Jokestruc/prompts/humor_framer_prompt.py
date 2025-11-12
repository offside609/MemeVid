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
Step 1: Look at Timeline and tags to map/match it to available levers.
Step 2. Find the item in timeline list which matches the any lever.
Step 3. Return the lever which matched, its name, description and example along with matched segment details.
Step 4. Augument the matched item in timeline list with emotional tone of the segment.
Output format (valid JSON, no extra text, no markdown):
{{
  "lever": {{
    "name": "<exact lever name>",
    "description": "<copy from lever list>",
    "example": "<copy from lever list>"
  }},
  "matched_segment": {{
    "start": "<start time of the segment>",
    "end": "<end time of the segment>",
    "description": "<description of the segment>",
    "emotional_tone": "<emotional tone of the segment>"
  }}
}}

Rules:
- Lever block must match one of the provided levers exactly.
- Keep references within the clip timeline.

"""
).strip()
