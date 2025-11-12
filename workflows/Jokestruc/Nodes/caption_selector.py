"""LLM-based caption selection node."""

import json
import re
from typing import Any, Dict, List

from ..humor_config import load_humor_levers
from ..llm_provider import run_openai_completion  # or Gemini equivalent
from ..prompts.caption_selector_prompt import CAPTION_SELECTOR_PROMPT


async def caption_selector(state: Dict[str, Any]) -> Dict[str, Any]:
    """Ask an LLM judge to select the best caption."""
    logs = state.get("logs", [])
    logs.append("caption_selector:start")

    raw = state.get("captions", "")
    selected_lever = state.get("selected_lever") or {}
    selected_segment = state.get("selected_segment") or {}
    scene_map_text = state.get("scene_map") or ""

    if not raw:
        raise ValueError("captions are required for selection")

    # Parse numbered captions
    caption_lines = [
        re.sub(r"^\s*\d+\.\s*", "", line.strip())
        for line in raw.splitlines()
        if line.strip()
    ]
    if not caption_lines:
        raise ValueError("No caption candidates found")

    # Levers are stored as full dict now; ensure we have description/example
    lever_info = selected_lever
    if not lever_info:
        lever_info = next(iter(load_humor_levers()), {})

    segment_hint = ""
    if selected_segment:
        segment_hint = (
            f"- Start: {selected_segment.get('start')}s\n"
            f"- End: {selected_segment.get('end')}s\n"
            f"- Description: {selected_segment.get('description')}\n"
            f"- Emotional tone: {selected_segment.get('emotional_tone')}"
        )

    prompt = CAPTION_SELECTOR_PROMPT.format(
        lever_name=lever_info.get("name", "<unknown>"),
        lever_description=lever_info.get("description", ""),
        lever_example=lever_info.get("example", ""),
        segment_hint=segment_hint or "None supplied.",
        caption_list="\n".join(caption_lines),
    )

    raw_json = await run_openai_completion(prompt)
    raw_json = raw_json.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.strip("`")
        if raw_json.lower().startswith("json"):
            raw_json = raw_json[4:].strip()
    parsed = json.loads(raw_json)

    selected_index = parsed.get("selected_index")
    reason = parsed.get("reason", "")
    if selected_index is None or not (1 <= selected_index <= len(caption_lines)):
        raise ValueError(f"LLM returned invalid caption index: {selected_index}")

    selected_caption = caption_lines[selected_index - 1]

    # Match scene line if available
    selected_scene_line = ""
    for line in scene_map_text.splitlines():
        if selected_caption in line:
            selected_scene_line = line
            break

    logs.append("caption_selector:done")
    return {
        "logs": logs,
        "caption_selector_done": True,
        "selected_caption": selected_caption,
        "selected_scene_segment": selected_scene_line or scene_map_text,
        "caption_selection_reason": reason,
    }
