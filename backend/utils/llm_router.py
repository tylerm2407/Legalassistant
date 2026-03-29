"""LLM router using Anthropic Claude for all chat completions.

Routes all chat requests through Anthropic Claude (claude-sonnet-4-20250514),
protected by a circuit breaker for resilience. Provides both synchronous
(full response) and streaming modes.

Architecture::

    chat request
        │
        ▼
    ┌──────────────────────────┐
    │  Anthropic Claude        │
    │  claude-sonnet-4-20250514│
    │  (circuit-breaker guard) │
    └────────────┬─────────────┘
                 │
                 ▼
             response

Usage::

    router = get_llm_router()
    response = await router.chat(system_prompt, messages)
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import anthropic
from anthropic.types import TextBlock

from backend.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger

_logger = get_logger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    """Response from the LLM router.

    Attributes:
        content: The generated text response.
        provider: Which provider served this request (always 'anthropic').
        model: The specific model used (e.g., 'claude-sonnet-4-20250514').
        latency_ms: Round-trip latency in milliseconds.
        was_fallback: Always False (single-provider architecture).
    """

    content: str
    provider: str
    model: str
    latency_ms: float
    was_fallback: bool = False


@dataclass
class ProviderMetrics:
    """Tracks per-provider call statistics for observability.

    Attributes:
        total_calls: Total number of calls routed to this provider.
        total_failures: Total number of failed calls.
        total_latency_ms: Cumulative latency for averaging.
        last_error: Most recent error message, if any.
    """

    total_calls: int = 0
    total_failures: int = 0
    total_latency_ms: float = 0.0
    last_error: str = ""


class LLMRouter:
    """Anthropic Claude LLM router with circuit-breaker protection.

    Routes all chat completions through Anthropic Claude, protected by a
    circuit breaker that temporarily halts requests after repeated failures
    to allow the service to recover.

    Args:
        model: The Anthropic model to use. Defaults to 'claude-sonnet-4-20250514'.
        max_tokens: Maximum tokens for the response. Defaults to 4096.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens

        self._breaker = CircuitBreaker(
            service_name="anthropic_chat",
            failure_threshold=3,
            recovery_timeout=30.0,
        )

        self._metrics = ProviderMetrics()

    @property
    def metrics(self) -> dict[str, object]:
        """Current router metrics for observability.

        Returns:
            Dict with provider metrics and circuit breaker state.
        """
        return {
            "anthropic": {
                **self._metrics.__dict__,
                "circuit": self._breaker.metrics,
            },
        }

    async def chat(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> LLMResponse:
        """Send a chat completion request to Anthropic Claude.

        Args:
            system_prompt: The fully assembled system prompt from the memory injector.
            messages: Conversation history as dicts with 'role' and 'content' keys.

        Returns:
            LLMResponse with the generated content and metadata.

        Raises:
            CircuitBreakerOpenError: If the circuit breaker is open.
            anthropic.APIError: If the API call fails.
        """
        start = time.monotonic()

        try:
            @self._breaker
            async def _request() -> str:
                client = get_anthropic_client()
                anthropic_messages = [
                    {"role": m["role"], "content": m["content"]} for m in messages
                ]
                response = await client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt,
                    messages=anthropic_messages,  # type: ignore[arg-type]
                )
                first_block = response.content[0] if response.content else None
                return first_block.text if isinstance(first_block, TextBlock) else ""

            content = await _request()
            latency = (time.monotonic() - start) * 1000
            self._metrics.total_calls += 1
            self._metrics.total_latency_ms += latency

            _logger.info(
                "llm_router_success",
                provider="anthropic",
                model=self.model,
                latency_ms=round(latency, 2),
            )

            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model,
                latency_ms=round(latency, 2),
                was_fallback=False,
            )

        except (CircuitBreakerOpenError, anthropic.APIError, Exception) as exc:
            self._metrics.total_failures += 1
            self._metrics.last_error = str(exc)
            _logger.error(
                "llm_router_error",
                provider="anthropic",
                error_type=type(exc).__name__,
                error=str(exc)[:200],
            )
            raise

    async def stream(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> tuple[str, object]:
        """Create a streaming chat completion from Anthropic Claude.

        Returns a tuple of (provider_name, stream_object) that the caller
        can iterate over using the Anthropic streaming API.

        Args:
            system_prompt: The fully assembled system prompt.
            messages: Conversation history as role/content dicts.

        Returns:
            Tuple of ('anthropic', async_stream) where async_stream is the
            Anthropic streaming response context manager.

        Raises:
            CircuitBreakerOpenError: If the circuit breaker is open.
            anthropic.APIError: If stream creation fails.
        """
        await self._breaker._check_state()
        client = get_anthropic_client()
        anthropic_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        stream = client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=anthropic_messages,  # type: ignore[arg-type]
        )
        self._metrics.total_calls += 1
        return "anthropic", stream


_router: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    """Get or create the singleton LLM router instance.

    Returns:
        The shared LLMRouter instance.
    """
    global _router  # noqa: PLW0603
    if _router is None:
        _router = LLMRouter()
        _logger.info(
            "llm_router_initialized",
            provider="anthropic/claude-sonnet-4-20250514",
        )
    return _router
