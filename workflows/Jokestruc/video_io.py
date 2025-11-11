"""Video I/O utilities for duration probing and uploads."""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

import google.generativeai as genai

# from google.generativeai import files


logger = logging.getLogger(__name__)


def probe_duration_seconds(video_path: Path) -> Optional[float]:
    """Return the duration of a video file in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return None

    try:
        data = json.loads(completed.stdout)
        return float(data["format"]["duration"])
    except (KeyError, ValueError):
        return None


async def upload_video_file(video_path: Path) -> str:
    """Upload a video to Gemini and return its file URI."""
    logger.info(f"Uploading video: {video_path.name}")

    def _upload():
        return genai.upload_file(
            path=str(video_path),
            display_name=video_path.name,
        )

    file_obj = await asyncio.to_thread(_upload)
    logger.info(f"Upload initiated for {video_path.name}, state={file_obj.state.name}")

    while file_obj.state.name == "PROCESSING":
        logger.debug(f"File {file_obj.name} still processing...")
        await asyncio.sleep(2)
        file_obj = genai.get_file(file_obj.name)

    if file_obj.state.name != "ACTIVE":
        logger.error(f"Upload failed: state={file_obj.state.name}")
        raise RuntimeError(f"Upload failed with state={file_obj.state.name}")

    logger.info(f"Upload complete: {file_obj.uri}")
    return file_obj.uri
