"""Derive structured descriptions and tags from the input video."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

import google.generativeai as genai

from ...llm_provider import MissingAPIKeyError, configure_genai
from ...video_io import upload_video_file
from .video_insight_schema import VideoInsightModel

VIDEO_INSIGHT_SCHEMA = {
    "type": "object",
    "properties": {
        "raw_description": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "timeline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number"},
                    "end": {"type": "number"},
                    "description": {"type": "string"},
                },
                "required": ["start", "end", "description"],
            },
        },
    },
    "required": ["raw_description", "tags", "timeline"],
}


async def video_insight(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate raw description, tags, and timeline segments for a clip."""
    logs = state.get("logs", [])
    logs.append("video_insight:start")

    input_data = state.get("input") or {}
    media_path = input_data.get("media_path")
    if not media_path:
        raise ValueError("state['input']['media_path'] is required")

    video_path = Path(media_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        configure_genai()
    except MissingAPIKeyError as err:
        raise RuntimeError(str(err)) from err

    video_uri = await upload_video_file(video_path)
    file_id = video_uri.split("/")[-1]

    duration = input_data.get("duration_sec")
    duration_hint = (
        f"The video is {duration:.1f} seconds long; keep timestamps within 0–{duration:.1f}."
        if duration
        else "Keep timestamps consistent with the actual video."
    )

    def _generate() -> str:
        model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": VIDEO_INSIGHT_SCHEMA,
            },
        )
        file_ref = genai.get_file(file_id)
        prompt = (
            "You are a video analyst. Return ONLY JSON with:\n"
            "- raw_description: one paragraph summary of the entire clip.\n"
            "- timeline: array of 6–10 segments covering the whole clip in chronological order. See and highlight if something humor worthy is happening\n"
            "Each segment must include start (float seconds), end (float seconds), and a description of the on-screen action or activity. Keep segments roughly 1–2 seconds long and focus on visible actions.\n"
            f"{duration_hint}\n"
            "- tags: list of concise actions/activities seen in the clip (e.g., 'player claps', 'dice roll').\n"
            "If a moment could be humorous, call it out in the segment description.\n"
            "Respond with valid JSON only."
        )
        response = model.generate_content([file_ref, prompt])
        return response.text

    result_json = await asyncio.to_thread(_generate)
    parsed = json.loads(result_json)

    insight = VideoInsightModel(**parsed)
    dur = duration or 15.0
    clamped: List[Dict[str, Any]] = []
    for seg in insight.timeline:
        start = max(0.0, min(float(seg.start), dur))
        end = max(start, min(float(seg.end), dur))
        clamped.append({"start": start, "end": end, "description": seg.description})

    logs.append("video_insight:done")
    return {
        "logs": logs,
        "video_insight_done": True,
        "video_insights": {
            "raw_description": insight.raw_description,
            "tags": insight.tags,
            "timeline": clamped,
        },
    }
