"""Tests for the graceful shutdown lifecycle manager.

Validates state transitions, request tracking, drain behavior,
shutdown hook execution, health reporting, and middleware integration.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.utils.lifecycle import (
    LifecycleManager,
    LifecycleState,
    ServiceUnavailableError,
    get_lifecycle_manager,
    lifecycle_middleware,
)


@pytest.fixture(autouse=True)
def _reset_singleton() -> None:
    """Reset the LifecycleManager singleton before each test."""
    LifecycleManager.reset()


@pytest.fixture
def manager() -> LifecycleManager:
    """Create a fresh LifecycleManager instance via the singleton getter."""
    return get_lifecycle_manager(drain_timeout=5)


class TestLifecycleState:
    """Tests for lifecycle state transitions."""

    def test_initial_state_is_starting(self, manager: LifecycleManager) -> None:
        """A freshly created manager starts in the STARTING state."""
        assert manager.state == LifecycleState.STARTING

    @pytest.mark.asyncio
    async def test_startup_transitions_to_ready(self, manager: LifecycleManager) -> None:
        """Calling startup() moves the state from STARTING to READY."""
        await manager.startup()
        assert manager.state == LifecycleState.READY

    @pytest.mark.asyncio
    async def test_startup_is_idempotent(self, manager: LifecycleManager) -> None:
        """Calling startup() multiple times does not change state or raise."""
        await manager.startup()
        await manager.startup()
        assert manager.state == LifecycleState.READY

    @pytest.mark.asyncio
    async def test_shutdown_transitions_through_draining_to_stopped(
        self, manager: LifecycleManager
    ) -> None:
        """Shutdown moves through DRAINING and ends at STOPPED."""
        await manager.startup()

        # Capture intermediate state via a hook
        observed_states: list[LifecycleState] = []

        def capture_state() -> None:
            observed_states.append(manager.state)

        manager.register_shutdown_hook(capture_state)
        await manager.shutdown()

        # Hook runs while still DRAINING (before transition to STOPPED)
        assert observed_states == [LifecycleState.DRAINING]
        assert manager.state == LifecycleState.STOPPED

    @pytest.mark.asyncio
    async def test_shutdown_is_idempotent(self, manager: LifecycleManager) -> None:
        """Calling shutdown() twice does not raise or re-run hooks."""
        await manager.startup()
        call_count = 0

        def hook() -> None:
            nonlocal call_count
            call_count += 1

        manager.register_shutdown_hook(hook)
        await manager.shutdown()
        await manager.shutdown()
        assert call_count == 1


class TestRequestTracking:
    """Tests for in-flight request counting."""

    @pytest.mark.asyncio
    async def test_request_started_increments_count(self, manager: LifecycleManager) -> None:
        """request_started() increments the active request counter."""
        await manager.startup()
        assert manager.active_requests == 0
        manager.request_started()
        assert manager.active_requests == 1
        manager.request_started()
        assert manager.active_requests == 2

    @pytest.mark.asyncio
    async def test_request_finished_decrements_count(self, manager: LifecycleManager) -> None:
        """request_finished() decrements the active request counter."""
        await manager.startup()
        manager.request_started()
        manager.request_started()
        manager.request_finished()
        assert manager.active_requests == 1
        manager.request_finished()
        assert manager.active_requests == 0

    @pytest.mark.asyncio
    async def test_request_finished_does_not_go_negative(self, manager: LifecycleManager) -> None:
        """request_finished() clamps at zero — never goes negative."""
        await manager.startup()
        manager.request_finished()
        assert manager.active_requests == 0

    @pytest.mark.asyncio
    async def test_request_rejected_during_drain(self, manager: LifecycleManager) -> None:
        """New requests are rejected with ServiceUnavailableError while draining."""
        await manager.startup()
        await manager.shutdown()

        with pytest.raises(ServiceUnavailableError) as exc_info:
            manager.request_started()
        assert exc_info.value.state == LifecycleState.STOPPED

    def test_request_accepted_before_startup(self, manager: LifecycleManager) -> None:
        """Requests are accepted in STARTING state for test clients and health checks."""
        manager.request_started()
        assert manager.active_requests == 1
        manager.request_finished()


class TestDrainBehavior:
    """Tests for the drain-and-wait shutdown logic."""

    @pytest.mark.asyncio
    async def test_drain_waits_for_active_requests(self, manager: LifecycleManager) -> None:
        """Shutdown waits for in-flight requests to finish before stopping."""
        await manager.startup()
        manager.request_started()

        # Simulate a request finishing after a short delay
        async def finish_request() -> None:
            await asyncio.sleep(0.3)
            manager.request_finished()

        asyncio.create_task(finish_request())
        await manager.shutdown()

        assert manager.active_requests == 0
        assert manager.state == LifecycleState.STOPPED

    @pytest.mark.asyncio
    async def test_drain_timeout_proceeds_with_active_requests(self) -> None:
        """If drain timeout expires, shutdown proceeds even with active requests."""
        LifecycleManager.reset()
        mgr = get_lifecycle_manager(drain_timeout=1)
        await mgr.startup()
        mgr.request_started()  # Never finished — will timeout

        await mgr.shutdown()

        assert mgr.state == LifecycleState.STOPPED
        assert mgr.active_requests == 1  # Still tracked, but shutdown proceeded


class TestShutdownHooks:
    """Tests for shutdown hook registration and execution."""

    @pytest.mark.asyncio
    async def test_shutdown_hooks_called_in_order(self, manager: LifecycleManager) -> None:
        """Shutdown hooks execute in the order they were registered."""
        await manager.startup()
        call_order: list[str] = []

        def hook_a() -> None:
            call_order.append("a")

        def hook_b() -> None:
            call_order.append("b")

        def hook_c() -> None:
            call_order.append("c")

        manager.register_shutdown_hook(hook_a)
        manager.register_shutdown_hook(hook_b)
        manager.register_shutdown_hook(hook_c)
        await manager.shutdown()

        assert call_order == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_async_shutdown_hooks_supported(self, manager: LifecycleManager) -> None:
        """Async cleanup functions are awaited during shutdown."""
        await manager.startup()
        cleaned_up = False

        async def async_hook() -> None:
            nonlocal cleaned_up
            await asyncio.sleep(0.01)
            cleaned_up = True

        manager.register_shutdown_hook(async_hook)
        await manager.shutdown()

        assert cleaned_up is True

    @pytest.mark.asyncio
    async def test_hook_failure_does_not_block_shutdown(self, manager: LifecycleManager) -> None:
        """A failing hook does not prevent other hooks or the STOPPED transition."""
        await manager.startup()
        final_hook_called = False

        def bad_hook() -> None:
            msg = "cleanup failed"
            raise RuntimeError(msg)

        def good_hook() -> None:
            nonlocal final_hook_called
            final_hook_called = True

        manager.register_shutdown_hook(bad_hook)
        manager.register_shutdown_hook(good_hook)
        await manager.shutdown()

        assert final_hook_called is True
        assert manager.state == LifecycleState.STOPPED


class TestHealth:
    """Tests for the health endpoint data."""

    @pytest.mark.asyncio
    async def test_health_returns_state_and_uptime(self, manager: LifecycleManager) -> None:
        """get_health() includes state, active_requests, and uptime_seconds."""
        await manager.startup()
        health = manager.get_health()

        assert health["state"] == "ready"
        assert health["active_requests"] == 0
        assert isinstance(health["uptime_seconds"], float)
        assert health["uptime_seconds"] >= 0.0

    def test_health_before_startup_shows_zero_uptime(self, manager: LifecycleManager) -> None:
        """Before startup, uptime is zero."""
        health = manager.get_health()
        assert health["state"] == "starting"
        assert health["uptime_seconds"] == 0.0


class TestMiddleware:
    """Tests for the lifecycle_middleware function."""

    @pytest.mark.asyncio
    async def test_middleware_returns_503_when_draining(self, manager: LifecycleManager) -> None:
        """The middleware returns 503 when the application is not READY."""
        await manager.startup()
        await manager.shutdown()

        request = MagicMock()
        call_next = AsyncMock()

        response = await lifecycle_middleware(request, call_next)

        assert response.status_code == 503
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_middleware_tracks_requests(self, manager: LifecycleManager) -> None:
        """The middleware increments and decrements the active request counter."""
        await manager.startup()

        mock_response = MagicMock()
        mock_response.status_code = 200
        request = MagicMock()

        # During call_next, active count should be 1
        observed_count = 0

        async def capturing_next(_req: MagicMock) -> MagicMock:
            nonlocal observed_count
            observed_count = manager.active_requests
            return mock_response

        response = await lifecycle_middleware(request, capturing_next)

        assert observed_count == 1
        assert manager.active_requests == 0
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_middleware_decrements_on_exception(self, manager: LifecycleManager) -> None:
        """Active count is decremented even if the handler raises."""
        await manager.startup()

        async def failing_next(_req: MagicMock) -> MagicMock:
            msg = "handler error"
            raise RuntimeError(msg)

        request = MagicMock()

        with pytest.raises(RuntimeError, match="handler error"):
            await lifecycle_middleware(request, failing_next)

        assert manager.active_requests == 0
