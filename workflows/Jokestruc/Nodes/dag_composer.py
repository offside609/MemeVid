"""Construct FFmpeg commands to render captions onto the video."""
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from ..utils.ffmpeg_util import build_drawtext_filters, pick_font_path

# from dotenv import load_dotenv

# load_dotenv()

# FONT_ENV_VAR = "CAPTION_FONT_PATH"
# DEFAULT_FONT_PATHS = [
#     "/Users/admin/Documents/MemeVid/workflows/Jokestruc/arial/ARIAL.TTF",  # macOS (adjust to a font you have)
#     "/System/Library/Fonts/Supplemental/Arial.ttf",
#     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # common Linux
# ]


async def dag_composer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Compile the caption timing plan into FFmpeg commands."""
    logs = state.get("logs", [])
    logs.append("dag_composer:start")

    timing_plan = state.get("timing_plan") or {}
    beats = timing_plan.get("beats") or []
    if not beats:
        raise ValueError("timing_plan['beats'] is required for DAG composition")

    input_data = state.get("input") or {}
    media_path = input_data.get("media_path")
    if not media_path:
        raise ValueError("input['media_path'] is required for DAG composition")

    font_path = pick_font_path()

    draw_filters = []
    for beat in beats:
        draw_filters.extend(build_drawtext_filters(beat, font_path))
    filter_complex = ",".join(draw_filters)

    input_video = Path(media_path)
    output_dir = input_video.parent / "renders"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{input_video.stem}_captioned.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-vf",
        filter_complex,
        "-c:a",
        "copy",
        str(output_path),
    ]

    logs.append("dag_composer:done")
    return {
        "logs": logs,
        "dag_composer_done": True,
        "dag_plan": [{"step": "overlay_caption", "command": command}],
        "output_target": str(output_path),
    }
