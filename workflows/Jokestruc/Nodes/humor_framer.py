"""Select a humor lever and framing for the current clip."""

import asyncio
import json
from typing import Any, Dict, List, cast

import google.generativeai as genai

from ..humor_config import load_humor_levers
from ..llm_provider import configure_genai
from ..prompts.humor_framer_prompt import HUMOR_FRAMER_PROMPT
from ..state import SelectedSegmentDict


async def humor_framer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Choose the best humor lever and produce framing guidance."""
    logs = state.get("logs", [])
    logs.append("humor_framer:start")

    video_insights = state.get("video_insights") or {}
    raw_description = video_insights.get("raw_description", "")
    timeline = cast(List[Dict[str, Any]], video_insights.get("timeline", []))
    if not raw_description or not timeline:
        raise ValueError(
            "video_insights['raw_description'] and video_insights['timeline'] are required for humor framing"
        )

    configure_genai()

    tags = video_insights.get("tags") or []
    tag_line = "Tags: " + ", ".join(tags) if tags else "Tags: (none supplied)"

    def _generate():
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        HUMOR_LEVERS = load_humor_levers()
        lever_json = json.dumps(HUMOR_LEVERS, ensure_ascii=False)
        timeline_json = json.dumps(timeline, ensure_ascii=False)
        prompt = HUMOR_FRAMER_PROMPT.format(
            timeline_json=timeline_json,
            tag_line=tag_line,
            lever_json=lever_json,
        )
        response = model.generate_content(prompt)

        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        if not raw:
            raise RuntimeError("Humor framer returned empty response")
        parsed = json.loads(raw)

        lever_name = parsed.get("lever", {})
        segment = parsed.get("matched_segment", {}) or {}
        framing_text = json.dumps(
            parsed.get("framing", {}), indent=2, ensure_ascii=False
        )
        return framing_text, lever_name, segment

    result = await asyncio.to_thread(_generate)
    framing_text, lever_name, segment = result

    logs.append("humor_framer:done")
    return {
        "logs": logs,
        "humor_framer_done": True,
        "humor_framing": framing_text,
        "selected_lever": lever_name,
        "selected_segment": segment,
    }
