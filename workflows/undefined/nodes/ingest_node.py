"""
Ingest Node - Handles media input processing
"""

import asyncio
from typing import Any, Dict

from .base_node import BaseNode


class IngestNode(BaseNode):
    """
    Node for ingesting and preprocessing media files
    """

    def __init__(self):
        super().__init__("ingest", timeout=60)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process media input and extract metadata
        """
        # Simulate async processing
        await asyncio.sleep(2)

        media_info = input_data.get("media", {})
        filename = media_info.get("filename", "unknown")
        duration = media_info.get("duration", 30)

        # Mock media processing
        processed_data = {
            "filename": filename,
            "duration": duration,
            "format": media_info.get("format", "mp4"),
            "size": "10MB",  # Mock size
            "fps": 30,  # Mock FPS
            "resolution": "1920x1080",  # Mock resolution
            "processed_at": "2024-01-01T00:00:00Z",
        }

        return {
            "media_info": processed_data,
            "status": "ingested",
            "ready_for_processing": True,
        }
