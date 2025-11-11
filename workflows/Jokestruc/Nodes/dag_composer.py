"""Construct FFmpeg commands to render captions onto the video."""
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

FONT_ENV_VAR = "CAPTION_FONT_PATH"
DEFAULT_FONT_PATHS = [
    "/Users/admin/Documents/MemeVid/workflows/Jokestruc/arial/ARIAL.TTF",  # macOS (adjust to a font you have)
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # common Linux
]


def _escape_drawtext(text: str) -> str:
    """Escape special characters for FFmpeg drawtext filter."""
    escaped = (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace(",", r"\,")
        .replace("'", r"\'")
        .replace('"', r"\"")
    )
    return escaped


def _pick_font_path() -> str:
    """Resolve a usable font path for caption rendering."""
    env_font = os.getenv(FONT_ENV_VAR)
    if env_font and Path(env_font).exists():
        return env_font
    for candidate in DEFAULT_FONT_PATHS:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError(
        f"No usable font found. Set {FONT_ENV_VAR} to a valid .ttf path."
    )


FONT_SIZE = 36  # adjust as needed


def _build_drawtext_filter(beat: Dict[str, Any], font_path: str) -> str:
    """Create a drawtext filter string for a single timing beat."""
    text = _escape_drawtext(beat["caption"])
    start = float(beat["start"])
    end = float(beat["end"])

    return (
        "drawtext="
        f"text='{text}':"
        f"fontfile='{font_path}':"
        f"fontsize={FONT_SIZE}:"
        "fontcolor=white:"
        "box=1:boxcolor=0x00000099:boxborderw=20:"
        "x=(w-text_w)/2:"
        "y=h-220:"
        f"enable=between(t\\,{start}\\,{end})"
    )


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

    font_path = _pick_font_path()

    draw_filters = [_build_drawtext_filter(beat, font_path) for beat in beats]
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
