# workflows/Jokestruc/Nodes/caption_selector.py
"""Select a meme caption and matching scene segment."""

import re
from typing import Any, Dict


async def caption_selector(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pick a caption and scene segment using simple heuristics."""
    logs = state.get("logs", [])
    logs.append("caption_selector:start")

    raw = state.get("captions", "")
    matches = re.findall(r"\d+\.\s*(.+)", raw)
    captions = [m.strip().strip('"') for m in matches]
    selected_caption = captions[0] if captions else ""

    scene_map_text = state.get("scene_map") or ""
    if not captions or not scene_map_text:
        raise ValueError("captions and scene_map are required for selection")

    # Hard pick first caption and its scene line
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
    }
