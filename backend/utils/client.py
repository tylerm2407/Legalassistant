"""Singleton Anthropic client for the Lex backend.

Provides a single shared AsyncAnthropic client instance to avoid
creating a new client on every API request.
"""

from __future__ import annotations

import os

import anthropic

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def get_anthropic_client() -> anthropic.AsyncAnthropic:
    """Get or create the singleton AsyncAnthropic client.

    Returns:
        A shared AsyncAnthropic client instance.
    """
    global _client  # noqa: PLW0603
    if _client is None:
        _client = anthropic.AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            timeout=30.0,
        )
        _logger.info("anthropic_client_initialized")
    return _client
