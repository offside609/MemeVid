"""Map captions to specific timeline segments."""

import asyncio
from typing import Any, Dict, List

import google.generativeai as genai

from ..llm_provider import configure_genai


def timeline_to_text(timeline: List[Dict[str, Any]]) -> str:
    """Represent the timeline as human-readable text lines."""
    return "\n".join(
        f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['description']}"
        for seg in timeline
    )


async def scene_mapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """Align candidate captions with their most relevant scene segments."""
    logs = state.get("logs", [])
    logs.append("scene_mapper:start")

    video_insights = state.get("video_insights") or {}
    timeline = video_insights.get("timeline") or []
    captions = state.get("captions", "")

    if not captions:
        raise ValueError("captions text is required for scene mapping")
    if not timeline:
        raise ValueError("video_insights['timeline'] is required for scene mapping")

    duration = (state.get("input") or {}).get("duration_sec")
    duration_line = (
        f"The video length is {duration:.1f} seconds; keep all timestamp ranges within 0–{duration:.1f}."
        if duration
        else "Keep timestamp ranges within the actual video length."
    )

    configure_genai()

    def _generate():
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = (
            "You are a meme caption scene mapper.\n"
            f"{duration_line}\n"
            "Here are the key scene beats:\n"
            f"{timeline_to_text(timeline)}\n\n"
            "Here are the candidate captions:\n"
            f"{captions}\n\n"
            "For each caption, assign a timestamp range (start–end seconds) that "
            "best matches the scene list above. Use existing segments; do not invent times outside the video.\n"
            "Return a numbered list where each line is:\n"
            "Caption -> start-end (seconds) – brief justification."
        )
        response = model.generate_content(prompt)
        return response.text

    scene_map_text = await asyncio.to_thread(_generate)

    logs.append("scene_mapper:done")
    return {
        "logs": logs,
        "scene_mapper_done": True,
        "scene_map": scene_map_text,
    }
