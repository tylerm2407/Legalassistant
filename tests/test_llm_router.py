"""Tests for the multi-provider LLM router with failover.

Tests the LLMRouter's priority chain, circuit breaker integration,
fallback behavior, and metrics collection. All external API calls
are mocked — no real LLM calls are made.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.utils.llm_router import LLMResponse, LLMRouter, ProviderMetrics, get_llm_router


@pytest.fixture(autouse=True)
def _reset_router_singleton() -> None:
    """Reset the global router singleton between tests."""
    import backend.utils.llm_router as mod
    mod._router = None


@pytest.fixture()
def router() -> LLMRouter:
    """Create a fresh LLMRouter instance for testing."""
    return LLMRouter(primary_model="gpt-4o", fallback_model="claude-sonnet-4-20250514")


class TestLLMResponse:
    """Tests for the LLMResponse dataclass."""

    def test_basic_response(self) -> None:
        """LLMResponse stores content and metadata correctly."""
        resp = LLMResponse(
            content="Hello",
            provider="openai",
            model="gpt-4o",
            latency_ms=150.5,
            was_fallback=False,
        )
        assert resp.content == "Hello"
        assert resp.provider == "openai"
        assert resp.model == "gpt-4o"
        assert resp.latency_ms == 150.5
        assert resp.was_fallback is False

    def test_fallback_response(self) -> None:
        """LLMResponse correctly marks fallback responses."""
        resp = LLMResponse(
            content="Fallback",
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            latency_ms=300.0,
            was_fallback=True,
        )
        assert resp.was_fallback is True
        assert resp.provider == "anthropic"


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

    def test_default_models(self, router: LLMRouter) -> None:
        """Router initializes with correct default models."""
        assert router.primary_model == "gpt-4o"
        assert router.fallback_model == "claude-sonnet-4-20250514"
        assert router.max_tokens == 4096

    def test_custom_models(self) -> None:
        """Router accepts custom model names."""
        r = LLMRouter(primary_model="gpt-4o-mini", fallback_model="claude-haiku-4-5-20251001", max_tokens=2048)
        assert r.primary_model == "gpt-4o-mini"
        assert r.fallback_model == "claude-haiku-4-5-20251001"
        assert r.max_tokens == 2048

    def test_metrics_initialized(self, router: LLMRouter) -> None:
        """Router initializes with empty metrics for both providers."""
        metrics = router.metrics
        assert "openai" in metrics
        assert "anthropic" in metrics


class TestLLMRouterChat:
    """Tests for the chat() method with mocked providers."""

    @pytest.mark.asyncio
    async def test_primary_success(self, router: LLMRouter) -> None:
        """Primary provider (OpenAI) success returns non-fallback response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Legal advice here."

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("backend.utils.llm_router.get_openai_client", return_value=mock_client):
            result = await router.chat("system prompt", [{"role": "user", "content": "question"}])

        assert result.content == "Legal advice here."
        assert result.provider == "openai"
        assert result.was_fallback is False
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_primary_failure_triggers_fallback(self, router: LLMRouter) -> None:
        """When primary fails, router falls back to Anthropic."""
        import openai as openai_mod
        from anthropic.types import TextBlock

        mock_oai_client = AsyncMock()
        mock_oai_client.chat.completions.create = AsyncMock(
            side_effect=openai_mod.APIError(
                message="Service unavailable",
                request=MagicMock(),
                body=None,
            )
        )

        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Fallback legal advice."
        mock_anthropic_response = MagicMock()
        mock_anthropic_response.content = [mock_text_block]

        mock_anthropic_client = AsyncMock()
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_anthropic_response)

        with (
            patch("backend.utils.llm_router.get_openai_client", return_value=mock_oai_client),
            patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_anthropic_client),
        ):
            result = await router.chat("system prompt", [{"role": "user", "content": "question"}])

        assert result.content == "Fallback legal advice."
        assert result.provider == "anthropic"
        assert result.was_fallback is True

    @pytest.mark.asyncio
    async def test_both_providers_fail_raises(self, router: LLMRouter) -> None:
        """When both providers fail, the fallback exception is raised."""
        import openai as openai_mod

        mock_oai_client = AsyncMock()
        mock_oai_client.chat.completions.create = AsyncMock(
            side_effect=openai_mod.APIError(
                message="OpenAI down",
                request=MagicMock(),
                body=None,
            )
        )

        mock_anthropic_client = AsyncMock()
        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=Exception("Anthropic also down")
        )

        with (
            patch("backend.utils.llm_router.get_openai_client", return_value=mock_oai_client),
            patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_anthropic_client),
            pytest.raises(Exception, match="Anthropic also down"),
        ):
            await router.chat("system prompt", [{"role": "user", "content": "question"}])

    @pytest.mark.asyncio
    async def test_metrics_tracked_on_success(self, router: LLMRouter) -> None:
        """Successful calls increment the provider's call counter."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response."

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("backend.utils.llm_router.get_openai_client", return_value=mock_client):
            await router.chat("system", [{"role": "user", "content": "q"}])
            await router.chat("system", [{"role": "user", "content": "q2"}])

        metrics = router.metrics
        assert metrics["openai"]["total_calls"] == 2
        assert metrics["openai"]["total_failures"] == 0

    @pytest.mark.asyncio
    async def test_metrics_tracked_on_failure(self, router: LLMRouter) -> None:
        """Failed primary calls increment the failure counter."""
        import openai as openai_mod
        from anthropic.types import TextBlock

        mock_oai = AsyncMock()
        mock_oai.chat.completions.create = AsyncMock(
            side_effect=openai_mod.APIError(message="fail", request=MagicMock(), body=None)
        )

        mock_text = MagicMock(spec=TextBlock)
        mock_text.text = "ok"
        mock_anthropic_resp = MagicMock()
        mock_anthropic_resp.content = [mock_text]
        mock_anthropic = AsyncMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_anthropic_resp)

        with (
            patch("backend.utils.llm_router.get_openai_client", return_value=mock_oai),
            patch("backend.utils.llm_router.get_anthropic_client", return_value=mock_anthropic),
        ):
            await router.chat("sys", [{"role": "user", "content": "q"}])

        metrics = router.metrics
        assert metrics["openai"]["total_failures"] == 1
        assert metrics["anthropic"]["total_calls"] == 1


class TestLLMRouterSingleton:
    """Tests for the get_llm_router singleton."""

    def test_singleton_returns_same_instance(self) -> None:
        """get_llm_router returns the same instance on repeated calls."""
        with (
            patch("backend.utils.llm_router.get_openai_client"),
            patch("backend.utils.llm_router.get_anthropic_client"),
        ):
            r1 = get_llm_router()
            r2 = get_llm_router()
            assert r1 is r2

    def test_singleton_is_llm_router_type(self) -> None:
        """get_llm_router returns an LLMRouter instance."""
        r = get_llm_router()
        assert isinstance(r, LLMRouter)
