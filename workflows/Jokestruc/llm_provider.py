"""Utility helpers for configuring language model providers."""

import os
from typing import Optional

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY_ENV_VARS = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
DEFAULT_VIDEO_MODEL = "gemini-2.5-pro"  # adjust if needed


class MissingAPIKeyError(RuntimeError):
    """Raised when no Gemini API key is available."""

    pass


def _get_api_key() -> str:
    """Return the first available Gemini API key from the environment."""
    for key in API_KEY_ENV_VARS:
        value = os.getenv(key)
        if value:
            return value
    raise MissingAPIKeyError(
        "Set GEMINI_API_KEY or GOOGLE_API_KEY before running video insights."
    )


def configure_genai() -> None:
    """Configure the Google Generative AI SDK with the active API key."""
    genai.configure(api_key=_get_api_key())


def get_google_genai_client(model: Optional[str] = None) -> ChatGoogleGenerativeAI:
    """Return a LangChain Gemini chat client for the requested model."""
    api_key = _get_api_key()
    return ChatGoogleGenerativeAI(
        model=model or os.getenv("GEMINI_VIDEO_MODEL", DEFAULT_VIDEO_MODEL),
        google_api_key=api_key,
        temperature=0.2,
        convert_system_message_to_human=True,
    )


from openai import AsyncOpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # pick your latest model
_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Return a shared AsyncOpenAI client, creating it if needed."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise MissingAPIKeyError("Set OPENAI_API_KEY before running humor framing.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def run_openai_completion(prompt: str) -> str:
    """Execute a chat completion request and return the model's reply text."""
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful meme caption writer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content
