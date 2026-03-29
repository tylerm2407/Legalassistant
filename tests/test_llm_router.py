"""Tests for the Anthropic Claude LLM router with circuit-breaker protection.

Tests the LLMRouter's chat method, streaming, circuit breaker integration,
and metrics collection. All external API calls are mocked — no real LLM
calls are made.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import TextBlock

from backend.utils.llm_router import LLMResponse, LLMRouter, ProviderMetrics, get_llm_router


@pytest.fixture(autouse=True)
def _reset_router_singleton() -> None:
    """Reset the global router singleton between tests."""
    import backend.utils.llm_router as mod
    mod._router = None


@pytest.fixture()
def router() -> LLMRouter:
    """Create a fresh LLMRouter instance for testing."""
    return LLMRouter(model="claude-sonnet-4-20250514")


class TestLLMResponse:
    """Tests for the LLMResponse dataclass."""

    def test_basic_response(self) -> None:
        """LLMResponse stores content and metadata correctly."""
        resp = LLMResponse(
            content="Hello",
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            latency_ms=150.5,
            was_fallback=False,
        )
        assert resp.content == "Hello"
        assert resp.provider == "anthropic"
        assert resp.model == "claude-sonnet-4-20250514"
        assert resp.latency_ms == 150.5
        assert resp.was_fallback is False


class TestProviderMetrics:
    """Tests for the ProviderMetrics dataclass."""

    def test_defaults(self) -> None:
        """ProviderMetrics initializes with zero counts."""
        m = ProviderMetrics()
        assert m.total_calls == 0
        assert m.total_failures == 0
        assert m.total_latency_ms == 0.0
        assert m.last_error == ""


class TestLLMRouterInit:
    """Tests for LLMRouter initialization."""

    def test_default_model(self, router: LLMRouter) -> None:
        """Router initializes with correct default model."""
        assert router.model == "claude-sonnet-4-20250514"
        assert router.max_tokens == 4096

    def test_custom_model(self) -> None:
        """Router accepts custom model name."""
        r = LLMRouter(model="claude-haiku-4-5-20251001", max_tokens=2048)
        assert r.model == "claude-haiku-4-5-20251001"
        assert r.max_tokens == 2048

    def test_metrics_initialized(self, router: LLMRouter) -> None:
        """Router initializes with empty metrics."""
        metrics = router.metrics
        assert "anthropic" in metrics


class TestLLMRouterChat:
    """Tests for the chat() method with mocked Anthropic client."""

    @pytest.mark.asyncio
    async def test_chat_success(self, router: LLMRouter) -> None:
        """Successful chat returns an LLMResponse with correct metadata."""
        mock_response = MagicMock()
        mock_response.content = [TextBlock(type="text", text="Legal advice here.")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_client):
            result = await router.chat("system prompt", [{"role": "user", "content": "question"}])

        assert result.content == "Legal advice here."
        assert result.provider == "anthropic"
        assert result.was_fallback is False
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_chat_failure_raises(self, router: LLMRouter) -> None:
        """API failure raises after circuit breaker check."""
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=Exception("Anthropic API down")
        )

        with (
            patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_client),
            pytest.raises(Exception, match="Anthropic API down"),
        ):
            await router.chat("system prompt", [{"role": "user", "content": "question"}])

    @pytest.mark.asyncio
    async def test_metrics_tracked_on_success(self, router: LLMRouter) -> None:
        """Successful calls increment the call counter."""
        mock_response = MagicMock()
        mock_response.content = [TextBlock(type="text", text="Response.")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_client):
            await router.chat("system", [{"role": "user", "content": "q"}])
            await router.chat("system", [{"role": "user", "content": "q2"}])

        metrics = router.metrics
        assert metrics["anthropic"]["total_calls"] == 2
        assert metrics["anthropic"]["total_failures"] == 0

    @pytest.mark.asyncio
    async def test_metrics_tracked_on_failure(self, router: LLMRouter) -> None:
        """Failed calls increment the failure counter."""
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=Exception("fail")
        )

        with patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_client):
            try:
                await router.chat("sys", [{"role": "user", "content": "q"}])
            except Exception:
                pass

        metrics = router.metrics
        assert metrics["anthropic"]["total_failures"] == 1


class TestLLMRouterStream:
    """Tests for the stream() method with mocked Anthropic client."""

    @pytest.mark.asyncio
    async def test_stream_returns_anthropic(self, router: LLMRouter) -> None:
        """Streaming returns anthropic provider name and stream object."""
        mock_stream = MagicMock()
        mock_client = MagicMock()
        mock_client.messages.stream = MagicMock(return_value=mock_stream)

        with patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_client):
            provider, stream_obj = await router.stream("system", [{"role": "user", "content": "q"}])

        assert provider == "anthropic"
        assert stream_obj is mock_stream


class TestLLMRouterSingleton:
    """Tests for the get_llm_router singleton."""

    def test_singleton_returns_same_instance(self) -> None:
        """get_llm_router returns the same instance on repeated calls."""
        r1 = get_llm_router()
        r2 = get_llm_router()
        assert r1 is r2

    def test_singleton_is_llm_router_type(self) -> None:
        """get_llm_router returns an LLMRouter instance."""
        r = get_llm_router()
        assert isinstance(r, LLMRouter)
