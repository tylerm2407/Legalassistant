"""Tests for the circuit breaker resilience pattern.

Validates the three-state circuit breaker (CLOSED → OPEN → HALF_OPEN)
for protecting external service calls against cascading failures.
"""

from __future__ import annotations

import asyncio

import pytest

from backend.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


@pytest.fixture
def breaker() -> CircuitBreaker:
    """Create a circuit breaker with low thresholds for fast testing."""
    return CircuitBreaker(
        service_name="test_service",
        failure_threshold=3,
        recovery_timeout=0.5,
        half_open_max_calls=1,
    )


class TestCircuitBreakerStates:
    """Test state transitions: CLOSED → OPEN → HALF_OPEN → CLOSED."""

    async def test_starts_closed(self, breaker) -> None:
        assert breaker.state == CircuitState.CLOSED

    async def test_stays_closed_on_success(self, breaker) -> None:
        @breaker
        async def success() -> str:
            return "ok"

        result = await success()
        assert result == "ok"
        assert breaker.state == CircuitState.CLOSED

    async def test_opens_after_threshold_failures(self, breaker) -> None:
        @breaker
        async def failing() -> str:
            raise RuntimeError("boom")

        for _ in range(3):
            with pytest.raises(RuntimeError, match="boom"):
                await failing()

        assert breaker.state == CircuitState.OPEN

    async def test_open_rejects_calls_immediately(self, breaker) -> None:
        @breaker
        async def failing() -> str:
            raise RuntimeError("boom")

        # Trip the breaker
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await failing()

        # Next call should be rejected by the breaker, not reach the function
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await failing()

        assert exc_info.value.service_name == "test_service"
        assert exc_info.value.retry_after >= 0

    async def test_transitions_to_half_open_after_timeout(self, breaker) -> None:
        @breaker
        async def failing() -> str:
            raise RuntimeError("boom")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await failing()

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.6)
        assert breaker.state == CircuitState.HALF_OPEN

    async def test_half_open_success_closes_breaker(self, breaker) -> None:
        call_count = 0

        @breaker
        async def sometimes_fails() -> str:
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise RuntimeError("boom")
            return "recovered"

        # Trip the breaker
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await sometimes_fails()

        await asyncio.sleep(0.6)

        # Probe call succeeds → back to CLOSED
        result = await sometimes_fails()
        assert result == "recovered"
        assert breaker.state == CircuitState.CLOSED

    async def test_half_open_failure_reopens_breaker(self, breaker) -> None:
        @breaker
        async def always_fails() -> str:
            raise RuntimeError("still broken")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await always_fails()

        await asyncio.sleep(0.6)

        # Probe call fails → back to OPEN
        with pytest.raises(RuntimeError, match="still broken"):
            await always_fails()

        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerMetrics:
    """Test the metrics reporting for observability."""

    async def test_metrics_after_calls(self, breaker) -> None:
        @breaker
        async def success() -> str:
            return "ok"

        await success()
        await success()

        metrics = breaker.metrics
        assert metrics["service"] == "test_service"
        assert metrics["state"] == "closed"
        assert metrics["total_calls"] == 2
        assert metrics["failure_count"] == 0

    async def test_metrics_track_failures(self, breaker) -> None:
        @breaker
        async def failing() -> str:
            raise RuntimeError("boom")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await failing()

        metrics = breaker.metrics
        assert metrics["total_failures"] == 2
        assert metrics["failure_count"] == 2

    async def test_metrics_track_rejections(self, breaker) -> None:
        @breaker
        async def failing() -> str:
            raise RuntimeError("boom")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await failing()

        with pytest.raises(CircuitBreakerOpenError):
            await failing()

        metrics = breaker.metrics
        assert metrics["total_rejected"] == 1
