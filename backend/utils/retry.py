"""Tenacity retry decorator for Anthropic API calls.

Provides a pre-configured retry decorator that handles transient API
errors and rate limits with exponential backoff. Every Anthropic API
call in the codebase should use this decorator.
"""

from __future__ import annotations

from typing import TypeVar

import anthropic
import tenacity

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

F = TypeVar("F")


def _log_retry(retry_state: tenacity.RetryCallState) -> None:
    """Log each retry attempt with structured context.

    Args:
        retry_state: The tenacity retry state containing attempt info.
    """
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    _logger.warning(
        "anthropic_api_retry",
        attempt=retry_state.attempt_number,
        exception_type=type(exception).__name__ if exception else None,
        exception_message=str(exception) if exception else None,
        wait_seconds=getattr(retry_state.next_action, "sleep", None),
    )


retry_anthropic = tenacity.retry(
    retry=tenacity.retry_if_exception_type((anthropic.APIError, anthropic.RateLimitError)),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=16),
    stop=tenacity.stop_after_attempt(3),
    before_sleep=_log_retry,
    reraise=True,
)
"""Retry decorator for Anthropic API calls.

Retries up to 3 times with exponential backoff (1s, 2s, 4s) on
anthropic.APIError and anthropic.RateLimitError. Logs each retry
attempt with structured context. Re-raises the final exception
if all retries are exhausted.

Usage::

    @retry_anthropic
    async def call_claude(prompt: str) -> str:
        ...
"""
