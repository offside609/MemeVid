"""Pydantic models describing caption timing plans."""

from typing import List

from pydantic import BaseModel, Field


class TimingBeat(BaseModel):
    """A single caption overlay beat."""

    start: float = Field(..., description="start time in seconds")
    end: float = Field(..., description="end time in seconds")
    caption: str = Field(..., description="caption text to display")
    action: str = Field(..., description="instruction to editor or renderer")
    audio_cue: str = Field("", description="sound effect or note (optional)")


class TimingPlan(BaseModel):
    """A collection of caption beats for a render session."""

    beats: List[TimingBeat]
