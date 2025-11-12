"""Generate captions tailored to the selected humor lever."""

import asyncio
import json
from typing import Any, Dict, Optional

import google.generativeai as genai

from ..humor_config import load_humor_levers
from ..llm_provider import configure_genai, run_openai_completion
from ..prompts.caption_generator_prompt import CAPTION_GENERATOR_PROMPT


async def caption_generator(state: Dict[str, Any]) -> Dict[str, Any]:
    """Create short meme captions aligned with the current humor lever."""
    logs = state.get("logs", [])
    logs.append("caption_generator:start")

    video_insights = state.get("video_insights") or {}
    raw_description = video_insights.get("raw_description", "")
    humor_framing = state.get("humor_framing", "")
    timeline = video_insights.get("timeline", [])
    if not raw_description:
        raise ValueError("video_insights['raw_description'] is required")

    configure_genai()
    HUMOR_LEVERS = load_humor_levers()

    lever = state.get("selected_lever") or {}
    lever_hint = ""
    if lever:
        lever_hint = (
            f"The humor lever is {lever.get('name', '<unknown>')} "
            f"(Description: {lever.get('description', '')} "
            f"| Example: {lever.get('example', '')})."
        )

    selected_lever = state.get("selected_lever") or {}
    selected_segment = state.get("selected_segment") or {}

    segment_hint = ""
    if selected_segment:
        segment_hint = (
            "Matched segment:\n"
            f"- Start: {selected_segment.get('start')}\n"
            f"- End: {selected_segment.get('end')}\n"
            f"- Description: {selected_segment.get('description')}\n"
            f"- Emotional tone: {selected_segment.get('emotional_tone')}\n"
        )

    prompt = CAPTION_GENERATOR_PROMPT.format(
        segment_hint=segment_hint,
        lever_hint=lever_hint,
    )

    # def _generate() -> str:
    #     model = genai.GenerativeModel("gemini-2.5-flash-lite")
    #     response = model.generate_content(prompt)
    #     return response.text

    # captions_text = await asyncio.to_thread(_generate)
    captions_text = await run_openai_completion(prompt)

    logs.append("caption_generator:done")
    return {
        "logs": logs,
        "caption_generator_done": True,
        "captions": captions_text,
    }
