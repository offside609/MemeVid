"""FastAPI router exposing the Jokestruc meme workflow."""

import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .graph import run_graph

router = APIRouter(prefix="/jokestruc", tags=["jokestruc"])


class GenerateRequest(BaseModel):
    """Request payload for the meme generation workflow."""

    media_path: Optional[str] = None


@router.post("/generate")
async def generate(req: GenerateRequest):
    """Run the workflow and return the final state."""
    thread_id = str(uuid.uuid4())
    final_state = await run_graph(
        {"input": {"media_path": req.media_path}, "logs": []},
        thread_id=thread_id,
    )
    return {"thread_id": thread_id, "state": final_state}
