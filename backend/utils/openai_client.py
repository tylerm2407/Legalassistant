"""Singleton OpenAI client for the CaseMate backend.

Provides a single shared AsyncOpenAI client instance to avoid
creating a new client on every API request. Used for the main
chat LLM (GPT-4o).
"""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create the singleton AsyncOpenAI client.

    Returns:
        A shared AsyncOpenAI client instance.

    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    global _client  # noqa: PLW0603
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        _client = AsyncOpenAI(api_key=api_key, timeout=60.0)
        _logger.info("openai_client_initialized")
    return _client
