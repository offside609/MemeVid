"""Normalize incoming request media metadata."""

import asyncio
from pathlib import Path
from typing import Any, Dict

from ..video_io import probe_duration_seconds


async def input_parser(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input payload and attach media duration."""
    logs = state.get("logs", [])
    logs.append("input_parser:start")

    input_data = state.get("input") or {}
    media_path = input_data.get("media_path")
    if not media_path:
        raise ValueError("media_path is required in state['input']")

    video_path = Path(media_path)
    duration = probe_duration_seconds(video_path)

    normalized_input = {
        "media_path": str(video_path),
        "duration_sec": duration,
    }

    logs.append("input_parser:done")
    return {
        "logs": logs,
        "input": normalized_input,
        "input_parser_done": True,
    }
