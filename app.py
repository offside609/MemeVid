"""FastAPI application entry point for MemeVid."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the Jokestruc router
from workflows.Jokestruc.main import router as jokestruc_router

load_dotenv(override=True)

import logging

logging.basicConfig(level=logging.INFO)


app = FastAPI(title="MemeVid API")

# Optional: open CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Report service health status."""
    return {"status": "ok"}


# Include Jokestruc workflow endpoints
app.include_router(jokestruc_router)
