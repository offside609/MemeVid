"""Compose precise caption timing beats for the render stage."""
import asyncio
import json
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from ..llm_provider import MissingAPIKeyError, configure_genai
from .timing_schema import TimingBeat, TimingPlan


async def _normalize_segment_with_llm(
    segment_text: str,
    timeline: List[Dict[str, Any]],
    duration: Optional[float],
) -> Optional[tuple[float, float]]:
    """
    Ask Gemini to convert the selected scene snippet into numeric start/end seconds.
    Returns None if the LLM cannot parse it.
    """
    configure_genai()

    timeline_summary = "\n".join(
        f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['description']}"
        for seg in timeline
    )
    duration_hint = (
        f"The video length is {duration:.2f} seconds. Keep start/end within 0–{duration:.2f}."
        if duration is not None
        else "Keep start/end within the clip length."
    )

    def _generate():
        model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                    },
                    "required": ["start", "end"],
                },
            },
        )
        prompt = (
            "Normalize the following scene timestamp into numeric seconds and return JSON with keys 'start' and 'end'.\n"
            f"{duration_hint}\n"
            "Known timeline segments:\n"
            f"{timeline_summary}\n\n"
            "Scene snippet:\n"
            f"{segment_text}\n\n"
            'Respond ONLY with JSON: {"start": ..., "end": ...}'
        )
        response = model.generate_content(prompt)
        return response.text

    try:
        result_text = await asyncio.to_thread(_generate)
        data = json.loads(result_text)
        start = float(data["start"])
        end = float(data["end"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return None

    return (start, end)


async def timing_composer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a timing plan for the selected caption and scene."""
    logs = state.get("logs", [])
    logs.append("timing_composer:start")

    video_insights = state.get("video_insights") or {}
    timeline: List[Dict[str, Any]] = video_insights.get("timeline") or []

    selected_caption = state.get("selected_caption", "")
    selected_scene_segment = state.get("selected_scene_segment", "")

    if not selected_caption:
        raise ValueError("selected_caption is required for timing composition")
    if not selected_scene_segment:
        raise ValueError("selected_scene_segment is required for timing composition")

    duration = (state.get("input") or {}).get("duration_sec")

    start_end = await _normalize_segment_with_llm(
        selected_scene_segment, timeline, duration
    )

    if start_end is None and timeline:
        matched = next(
            (
                seg
                for seg in timeline
                if selected_caption.lower() in seg["description"].lower()
            ),
            timeline[0],
        )
        start_end = (matched["start"], matched["end"])
    if start_end is None:
        start_end = (0.0, duration or 5.0)

    start, end = start_end
    if duration is not None:
        start = max(0.0, min(start, duration))
        end = max(start, min(end, duration))

    beat = TimingBeat(
        start=start,
        end=end,
        caption=selected_caption,
        action="Overlay selected caption on screen",
        audio_cue="",
    )
    plan = TimingPlan(beats=[beat])

    logs.append("timing_composer:done")
    return {
        "logs": logs,
        "timing_composer_done": True,
        "timing_plan": plan.dict(),
    }
