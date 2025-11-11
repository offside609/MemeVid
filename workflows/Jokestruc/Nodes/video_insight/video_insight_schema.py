"""Pydantic models structuring video insight responses."""

from typing import List

from pydantic import BaseModel, Field


class TimelineSegment(BaseModel):
    """A single entry in the structured clip timeline."""

    start: float = Field(..., description="start time in seconds")
    end: float = Field(..., description="end time in seconds")
    description: str = Field(..., description="what happens in this span")


class VideoInsightModel(BaseModel):
    """Raw description, tags, and timeline for a video clip."""

    raw_description: str
    tags: List[str]
    timeline: List[TimelineSegment]
