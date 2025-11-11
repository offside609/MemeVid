"""Generate captions tailored to the selected humor lever."""

import asyncio
import json
from typing import Any, Dict

import google.generativeai as genai

from ..humor_config import load_humor_levers
from ..llm_provider import configure_genai


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

    selected_lever = state.get("selected_lever")
    lever_info = (
        next(
            (
                lever
                for lever in HUMOR_LEVERS
                if lever["name"].lower() == selected_lever.lower()
            ),
            None,
        )
        if selected_lever
        else None
    )

    lever_hint = ""
    if lever_info:
        lever_hint = (
            f"The humor lever is {lever_info['name']} "
            f"(Description: {lever_info['description']} | Example: {lever_info['example']})."
        )

    from ..prompts.caption_generator_prompt import CAPTION_GENERATOR_PROMPT

    prompt = CAPTION_GENERATOR_PROMPT.format(
        timeline_json=json.dumps(timeline, ensure_ascii=False),
        humor_framing=humor_framing,
        lever_hint=lever_hint,
    )

    def _generate() -> str:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text

    captions_text = await asyncio.to_thread(_generate)

    logs.append("caption_generator:done")
    return {
        "logs": logs,
        "caption_generator_done": True,
        "captions": captions_text,
    }
