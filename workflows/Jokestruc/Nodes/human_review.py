"""Workflow node that pauses for human caption selection."""

from typing import Any, Dict, List

from langgraph.types import interrupt


def human_caption_review(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pause execution to let a human pick their favorite caption."""
    captions: List[str] = state.get("captions") or []
    if not captions:
        raise ValueError("No captions available for human review.")

    payload = {
        "instruction": "Choose the caption that lands the best.",
        "candidates": captions,
        # optionally keep lever/segment if you need them in the UI
    }

    update = interrupt(payload)

    if isinstance(update, dict):
        caption = update.get("user_selected_caption") or update.get("caption")
    else:
        caption = str(update).strip()

    if not caption:
        raise ValueError("Human review did not supply a caption.")

    return {"user_selected_caption": caption}
