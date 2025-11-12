"""FastAPI router exposing the Jokestruc meme workflow."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter
from langgraph.types import Command
from pydantic import BaseModel

from .graph import app, resume_graph, run_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jokestruc", tags=["jokestruc"])


class GenerateRequest(BaseModel):
    """Request payload for the meme generation workflow."""

    media_path: Optional[str] = None


class ResumeRequest(BaseModel):
    """Payload for resuming the workflow after human review."""

    thread_id: str
    user_selected_caption: str


@router.post("/generate")
async def generate(req: GenerateRequest):
    """Start the workflow; return state or interrupt payload."""
    thread_id = str(uuid.uuid4())
    logger.info(
        "Starting jokestruc run with thread_id=%s media=%s",
        thread_id,
        req.media_path,
    )

    result = await run_graph(
        {"input": {"media_path": req.media_path}, "logs": []},
        thread_id=thread_id,
    )

    interrupts = result.get("__interrupt__")
    if interrupts:
        payload = interrupts[0].value
        logger.info("Workflow thread %s awaiting human review", thread_id)
        return {
            "thread_id": thread_id,
            "status": "awaiting_review",
            "payload": payload,
        }

    logger.info("Workflow thread %s completed automatically", thread_id)
    return {"thread_id": thread_id, "status": "completed", "state": result}


@router.post("/resume")
async def resume(req: ResumeRequest):
    """Resume workflow after human review."""
    logger.info(
        "Resuming thread %s with caption=%r",
        req.thread_id,
        req.user_selected_caption,
    )
    final_state = await resume_graph(
        req.thread_id,
        {"user_selected_caption": req.user_selected_caption},
    )
    logger.info(
        "Thread %s resumed successfully; state keys=%s",
        req.thread_id,
        list(final_state.keys()),
    )
    return {"thread_id": req.thread_id, "state": final_state}
