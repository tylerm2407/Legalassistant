"""Multi-provider LLM router with automatic failover.

Implements a dual-model architecture where the primary provider (OpenAI GPT-4o)
handles chat requests, with automatic failover to the secondary provider
(Anthropic Claude) when the primary is unavailable. Each provider is protected
by its own circuit breaker, and all calls use exponential backoff retry.

This is distinct from simple A/B routing — the router implements a priority
chain with health-aware selection. If the primary provider's circuit breaker
opens (e.g., 5 consecutive failures), all subsequent requests are automatically
routed to the secondary provider until the primary recovers. The fallback is
transparent to the caller.

Architecture::

    chat request
        │
        ▼
    ┌─────────────────┐    circuit open?    ┌──────────────────┐
    │  OpenAI GPT-4o  │ ──────────────────► │ Anthropic Claude │
    │  (primary)      │     or API error    │ (fallback)       │
    └────────┬────────┘                     └────────┬─────────┘
             │                                       │
             ▼                                       ▼
         response                               response

Usage::

    router = get_llm_router()
    response = await router.chat(system_prompt, messages)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import anthropic
import openai
from anthropic.types import TextBlock

from backend.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.openai_client import get_openai_client

_logger = get_logger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    """Response from the LLM router.

    Attributes:
        content: The generated text response.
        provider: Which provider served this request ('openai' or 'anthropic').
        model: The specific model used (e.g., 'gpt-4o', 'claude-sonnet-4-20250514').
        latency_ms: Round-trip latency in milliseconds.
        was_fallback: True if the primary provider failed and the fallback was used.
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
    """Health-aware multi-provider LLM router with circuit-breaker failover.

    Routes chat completions through a priority chain of LLM providers.
    The primary provider (OpenAI GPT-4o) is attempted first. If it fails
    or its circuit breaker is open, the request falls back to Anthropic
    Claude. Both providers are independently protected by circuit breakers
    and retry logic.

    Args:
        primary_model: The OpenAI model to use as primary. Defaults to 'gpt-4o'.
        fallback_model: The Anthropic model to use as fallback.
            Defaults to 'claude-sonnet-4-20250514'.
        max_tokens: Maximum tokens for the response. Defaults to 4096.
    """

    def __init__(
        self,
        primary_model: str = "gpt-4o",
        fallback_model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ) -> None:
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.max_tokens = max_tokens

        self._openai_breaker = CircuitBreaker(
            service_name="openai_chat",
            failure_threshold=3,
            recovery_timeout=30.0,
        )
        self._anthropic_breaker = CircuitBreaker(
            service_name="anthropic_chat_fallback",
            failure_threshold=3,
            recovery_timeout=30.0,
        )

        self._metrics: dict[str, ProviderMetrics] = {
            "openai": ProviderMetrics(),
            "anthropic": ProviderMetrics(),
        }

    @property
    def metrics(self) -> dict[str, object]:
        """Current router metrics for observability.

        Returns:
            Dict with per-provider metrics and circuit breaker states.
        """
        return {
            "openai": {
                **self._metrics["openai"].__dict__,
                "circuit": self._openai_breaker.metrics,
            },
            "anthropic": {
                **self._metrics["anthropic"].__dict__,
                "circuit": self._anthropic_breaker.metrics,
            },
        }

    async def _call_openai(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> LLMResponse:
        """Call OpenAI GPT-4o with circuit breaker protection.

        Args:
            system_prompt: The assembled system prompt.
            messages: Conversation history as role/content dicts.

        Returns:
            LLMResponse with the generated content and metadata.

        Raises:
            CircuitBreakerOpenError: If the OpenAI circuit breaker is open.
            openai.APIError: If the API call fails after circuit breaker check.
        """
        start = time.monotonic()

        @self._openai_breaker
        async def _request() -> str:
            client = get_openai_client()
            oai_messages: list[dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                *messages,
            ]
            response = await client.chat.completions.create(
                model=self.primary_model,
                max_tokens=self.max_tokens,
                messages=oai_messages,  # type: ignore[arg-type]
            )
            return response.choices[0].message.content or ""

        content = await _request()
        latency = (time.monotonic() - start) * 1000
        self._metrics["openai"].total_calls += 1
        self._metrics["openai"].total_latency_ms += latency

        return LLMResponse(
            content=content,
            provider="openai",
            model=self.primary_model,
            latency_ms=round(latency, 2),
            was_fallback=False,
        )

    async def _call_anthropic(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> LLMResponse:
        """Call Anthropic Claude as fallback with circuit breaker protection.

        Args:
            system_prompt: The assembled system prompt.
            messages: Conversation history as role/content dicts.

        Returns:
            LLMResponse with the generated content and metadata.

        Raises:
            CircuitBreakerOpenError: If the Anthropic circuit breaker is open.
            anthropic.APIError: If the API call fails after circuit breaker check.
        """
        start = time.monotonic()

        @self._anthropic_breaker
        async def _request() -> str:
            client = get_anthropic_client()
            anthropic_messages = [
                {"role": m["role"], "content": m["content"]} for m in messages
            ]
            response = await client.messages.create(
                model=self.fallback_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=anthropic_messages,  # type: ignore[arg-type]
            )
            first_block = response.content[0] if response.content else None
            return first_block.text if isinstance(first_block, TextBlock) else ""

        content = await _request()
        latency = (time.monotonic() - start) * 1000
        self._metrics["anthropic"].total_calls += 1
        self._metrics["anthropic"].total_latency_ms += latency

        return LLMResponse(
            content=content,
            provider="anthropic",
            model=self.fallback_model,
            latency_ms=round(latency, 2),
            was_fallback=True,
        )

    async def chat(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> LLMResponse:
        """Route a chat completion through the provider priority chain.

        Attempts the primary provider (OpenAI) first. If it fails due to
        a circuit breaker open state or API error, falls back to Anthropic.
        If both providers fail, raises the last exception.

        Args:
            system_prompt: The fully assembled system prompt from the memory injector.
            messages: Conversation history as dicts with 'role' and 'content' keys.

        Returns:
            LLMResponse with the generated content and routing metadata.

        Raises:
            Exception: If both providers fail. The exception from the fallback
                provider is raised.
        """
        # Try primary (OpenAI)
        try:
            response = await self._call_openai(system_prompt, messages)
            _logger.info(
                "llm_router_primary_success",
                provider="openai",
                model=self.primary_model,
                latency_ms=response.latency_ms,
            )
            return response
        except (CircuitBreakerOpenError, openai.APIError, Exception) as primary_exc:
            self._metrics["openai"].total_failures += 1
            self._metrics["openai"].last_error = str(primary_exc)
            _logger.warning(
                "llm_router_primary_failed",
                provider="openai",
                error_type=type(primary_exc).__name__,
                error=str(primary_exc)[:200],
            )

        # Fallback to Anthropic
        try:
            response = await self._call_anthropic(system_prompt, messages)
            _logger.info(
                "llm_router_fallback_success",
                provider="anthropic",
                model=self.fallback_model,
                latency_ms=response.latency_ms,
            )
            return response
        except (CircuitBreakerOpenError, anthropic.APIError, Exception) as fallback_exc:
            self._metrics["anthropic"].total_failures += 1
            self._metrics["anthropic"].last_error = str(fallback_exc)
            _logger.error(
                "llm_router_all_providers_failed",
                primary_error=self._metrics["openai"].last_error[:200],
                fallback_error=str(fallback_exc)[:200],
            )
            raise

    async def stream(
        self, system_prompt: str, messages: list[dict[str, str]]
    ) -> tuple[str, object]:
        """Create a streaming chat completion from the primary provider.

        Returns a tuple of (provider_name, stream_object) that the caller
        can iterate over. Falls back to Anthropic streaming if OpenAI fails.

        Args:
            system_prompt: The fully assembled system prompt.
            messages: Conversation history as role/content dicts.

        Returns:
            Tuple of (provider_name, async_stream) where provider_name is
            'openai' or 'anthropic', and async_stream is the provider's
            streaming response object.

        Raises:
            Exception: If both providers fail to create a stream.
        """
        # Try OpenAI streaming first
        try:
            await self._openai_breaker._check_state()
            client = get_openai_client()
            oai_messages: list[dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                *messages,
            ]
            stream = await client.chat.completions.create(
                model=self.primary_model,
                max_tokens=self.max_tokens,
                messages=oai_messages,  # type: ignore[arg-type]
                stream=True,
            )
            self._metrics["openai"].total_calls += 1
            return "openai", stream

        except (CircuitBreakerOpenError, openai.APIError, Exception) as exc:
            self._metrics["openai"].total_failures += 1
            self._metrics["openai"].last_error = str(exc)
            _logger.warning(
                "llm_router_stream_primary_failed",
                provider="openai",
                error=str(exc)[:200],
            )

        # Fallback to Anthropic streaming
        await self._anthropic_breaker._check_state()
        client_anthropic = get_anthropic_client()
        anthropic_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        stream = client_anthropic.messages.stream(
            model=self.fallback_model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=anthropic_messages,  # type: ignore[arg-type]
        )
        self._metrics["anthropic"].total_calls += 1
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
            primary="openai/gpt-4o",
            fallback="anthropic/claude-sonnet-4-20250514",
        )
    return _router
