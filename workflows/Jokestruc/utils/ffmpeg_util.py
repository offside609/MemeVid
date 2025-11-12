"""FFmpeg utilities for caption rendering."""

import os
import textwrap
from pathlib import Path
from typing import Any, Dict, List

FONT_ENV_VAR = "CAPTION_FONT_PATH"
FONT_SIZE = 36
LINE_SPACING = 6
DEFAULT_FONT_PATHS = [
    "/Users/admin/Documents/MemeVid/workflows/Jokestruc/arial/ARIAL.TTF",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def pick_font_path() -> str:
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


def _escape_drawtext(text: str) -> str:
    """Escape special characters for drawtext."""
    return (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace(",", r"\,")
        .replace("'", r"\'")
        .replace('"', r"\"")
    )


def wrap_caption_lines(
    text: str, video_width: int, font_size: int = FONT_SIZE
) -> List[str]:
    """Return caption lines wrapped to fit the video width."""
    stripped = text.strip()
    avg_char_width = font_size * 0.6
    safe_width = video_width * 0.8
    max_chars = max(int(safe_width / avg_char_width), 1)

    if len(stripped) <= max_chars:
        return [stripped]

    wrapped = textwrap.fill(stripped, width=max_chars)
    return wrapped.splitlines()


def build_drawtext_filters(
    beat: Dict[str, Any],
    font_path: str,
    video_width: int = 1280,
    font_size: int = FONT_SIZE,
) -> List[str]:
    """Create drawtext filters for a timing beat, one per wrapped line."""
    caption_lines = wrap_caption_lines(
        beat["caption"], video_width=video_width, font_size=font_size
    )
    start = float(beat["start"])
    end = float(beat["end"])

    filters: List[str] = []
    total_height = len(caption_lines) * (font_size + LINE_SPACING) - LINE_SPACING

    bottom_margin = font_size  # tweak as needed

    for idx, line in enumerate(caption_lines):
        escaped = _escape_drawtext(line)
        y_offset = (
            f"h - {bottom_margin} - "
            f"({len(caption_lines) - idx})*({font_size + LINE_SPACING})"
        )
        filters.append(
            "drawtext="
            f"text='{escaped}':"
            f"fontfile='{font_path}':"
            f"fontsize={font_size}:"
            "fontcolor=white:"
            "box=1:boxcolor=0x00000099:boxborderw=20:"
            "x=(w-text_w)/2:"
            f"y={y_offset}:"
            f"enable=between(t\\,{start}\\,{end})"
        )

    return filters
