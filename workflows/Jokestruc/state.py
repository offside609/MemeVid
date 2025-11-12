"""Typed dictionaries representing workflow state."""

from typing import Any, Dict, List, Optional, TypedDict


class InputPayload(TypedDict, total=False):
    media_path: str
    duration_sec: Optional[float]


class TimelineSegmentDict(TypedDict):
    start: float
    end: float
    description: str


class VideoInsightsDict(TypedDict, total=False):
    raw_description: str
    tags: List[str]
    timeline: List[TimelineSegmentDict]


class TimingBeatDict(TypedDict):
    start: float
    end: float
    caption: str
    action: str
    audio_cue: str


class TimingPlanDict(TypedDict):
    beats: List[TimingBeatDict]


class SelectedSegmentDict(TypedDict, total=False):
    start: float
    end: float
    description: str
    emotional_tone: str


class JokeState(TypedDict, total=False):
    input: Optional[InputPayload]
    logs: List[str]
    output_path: Optional[str]

    video_insights: Optional[VideoInsightsDict]

    humor_framing: Optional[str]
    selected_lever: Optional[Dict[str, str]]
    selected_segment: Optional[SelectedSegmentDict]
    captions: Optional[List[str]]
    user_selected_caption: Optional[str]
    timing_plan: Optional[TimingPlanDict]
    dag_plan: Optional[List[Dict[str, Any]]]
    output_target: Optional[str]

    # scene_map: Optional[str]
    # selected_caption: Optional[str]
    # selected_scene_segment: Optional[str]

    #   # new

    # caption_selection_reason: Optional[str]

    input_parser_done: bool
    video_insight_done: bool
    humor_framer_done: bool
    caption_generator_done: bool
    scene_mapper_done: bool
    timing_composer_done: bool
    dag_composer_done: bool
    renderer_done: bool
    caption_selector_done: bool
