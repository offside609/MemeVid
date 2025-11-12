"""Compose caption timing beats from the selected scene segment."""

import json
import logging
from typing import Any, Dict

from ..llm_provider import run_openai_completion
from ..prompts.timing_composer_prompt import TIMING_COMPOSER_PROMPT
from .timing_schema import TimingBeat, TimingPlan

logger = logging.getLogger(__name__)


def _strip_code_fences(text: str) -> str:
    """Remove optional Markdown code fences around JSON."""

    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    return raw


async def timing_composer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the overlay window for the selected caption."""
    """Composes caption timing beats from the selected scene segment."""
    logger.info("timing_composer input state: %s", json.dumps(state, indent=2))
    logs = state.get("logs", [])
    logs.append("timing_composer:start")

    selected_caption = state.get("user_selected_caption", "")
    selected_segment = state.get("selected_segment", "")
    if not selected_caption:
        raise ValueError("selected_caption is required for timing composition")
    if not selected_segment:
        raise ValueError("selected_segment is required for timing composition")

    prompt = TIMING_COMPOSER_PROMPT.format(
        scene_segment=selected_segment,
        caption=selected_caption,
    )
    raw = await run_openai_completion(prompt)
    parsed = json.loads(_strip_code_fences(raw))

    start = float(parsed["start"])
    end = float(parsed["end"])
    if end <= start:
        raise ValueError("LLM returned invalid timing window")

    beat = TimingBeat(
        start=start,
        end=end,
        caption=selected_caption,
        action="Overlay selected caption on screen",
        audio_cue="",
    )
    plan = TimingPlan(beats=[beat])

    logs.append("timing_composer:done")
    return {
        "logs": logs,
        "timing_composer_done": True,
        "timing_plan": plan.dict(),
    }
