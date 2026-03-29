"""Graceful shutdown manager for CaseMate's FastAPI application.

Manages application lifecycle with proper request draining on shutdown.
When SIGTERM or SIGINT is received, the manager stops accepting new requests,
waits for in-flight requests to complete (with a configurable timeout), then
cleanly shuts down after calling all registered cleanup hooks.

Lifecycle states:
  - STARTING: Application is initializing. Not yet accepting requests.
  - READY: Normal operation. Requests are accepted and processed.
  - DRAINING: Shutdown initiated. New requests are rejected with 503.
    In-flight requests are allowed to complete up to the drain timeout.
  - STOPPED: All requests drained and cleanup hooks executed. Process can exit.
"""

from __future__ import annotations

import asyncio
import enum
import signal
import time
from collections.abc import Awaitable, Callable
from typing import ClassVar

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


class LifecycleState(enum.Enum):
    """The four states of the application lifecycle."""

    STARTING = "starting"
    READY = "ready"
    DRAINING = "draining"
    STOPPED = "stopped"


class ServiceUnavailableError(Exception):
    """Raised when a request arrives while the application is draining.

    Attributes:
        state: The current lifecycle state that caused rejection.
    """

    def __init__(self, state: LifecycleState) -> None:
        self.state = state
        super().__init__(f"Service unavailable — application is {state.value}")


class LifecycleManager:
    """Singleton manager for application startup, request tracking, and graceful shutdown.

    Tracks in-flight requests with an asyncio lock for thread safety. On shutdown,
    transitions to DRAINING state, polls until active requests reach zero (or timeout
    expires), executes registered cleanup hooks, then transitions to STOPPED.

    Attributes:
        state: Current lifecycle state.

    Example::

        manager = get_lifecycle_manager()
        await manager.startup()

        # In middleware:
        manager.request_started()
        try:
            response = await handler(request)
        finally:
            manager.request_finished()
    """

    _instance: ClassVar[LifecycleManager | None] = None

    def __init__(self, drain_timeout: int = 30) -> None:
        self._state: LifecycleState = LifecycleState.STARTING
        self._active_requests: int = 0
        self._drain_timeout: int = drain_timeout
        self._shutdown_hooks: list[Callable[[], None | Awaitable[None]]] = []
        self._lock: asyncio.Lock = asyncio.Lock()
        self._start_time: float = 0.0

    @classmethod
    def get_instance(cls, drain_timeout: int = 30) -> LifecycleManager:
        """Get or create the singleton LifecycleManager.

        Args:
            drain_timeout: Maximum seconds to wait for in-flight requests
                to complete during shutdown. Only used on first call.

        Returns:
            The shared LifecycleManager instance.
        """
        if cls._instance is None:
            cls._instance = cls(drain_timeout=drain_timeout)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Used in tests only."""
        cls._instance = None

    @property
    def state(self) -> LifecycleState:
        """Current application lifecycle state."""
        return self._state

    @property
    def active_requests(self) -> int:
        """Number of in-flight requests currently being processed."""
        return self._active_requests

    async def startup(self) -> None:
        """Transition from STARTING to READY and register OS signal handlers.

        Registers handlers for SIGTERM and SIGINT that trigger graceful shutdown.
        Safe to call multiple times — subsequent calls are no-ops.
        """
        if self._state != LifecycleState.STARTING:
            return

        self._start_time = time.monotonic()
        self._state = LifecycleState.READY

        # Register signal handlers — best-effort, may fail on Windows or in threads
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        except (NotImplementedError, RuntimeError):
            _logger.warning(
                "signal_handler_registration_failed",
                detail="Signal handlers not supported on this platform",
            )

        _logger.info("lifecycle_started", state=self._state.value)

    async def shutdown(self) -> None:
        """Initiate graceful shutdown: drain requests, run hooks, then stop.

        Transitions READY -> DRAINING, waits for active requests to complete
        (polling every 0.5 seconds up to drain_timeout), calls all registered
        shutdown hooks in registration order, then transitions to STOPPED.

        If drain timeout is exceeded, proceeds with shutdown regardless —
        in-flight requests will be abandoned.
        """
        if self._state in (LifecycleState.DRAINING, LifecycleState.STOPPED):
            return

        self._state = LifecycleState.DRAINING
        _logger.info(
            "lifecycle_draining",
            active_requests=self._active_requests,
            drain_timeout=self._drain_timeout,
        )

        # Wait for in-flight requests to complete
        elapsed = 0.0
        while self._active_requests > 0 and elapsed < self._drain_timeout:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            _logger.debug(
                "drain_progress",
                active_requests=self._active_requests,
                elapsed_seconds=elapsed,
            )

        if self._active_requests > 0:
            _logger.warning(
                "drain_timeout_exceeded",
                remaining_requests=self._active_requests,
                timeout=self._drain_timeout,
            )

        # Execute registered shutdown hooks in order
        for hook in self._shutdown_hooks:
            try:
                result = hook()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:  # noqa: BLE001 — hooks must not prevent shutdown
                _logger.error("shutdown_hook_failed", error=str(exc), hook=hook.__name__)

        self._state = LifecycleState.STOPPED
        _logger.info("lifecycle_stopped")

    def request_started(self) -> None:
        """Increment the active request counter.

        Called at the beginning of each request by the lifecycle middleware.
        Accepts requests in both STARTING and READY states — STARTING allows
        the application to serve during initialization (e.g., health checks,
        test clients that do not trigger FastAPI startup events).

        Raises:
            ServiceUnavailableError: If the application is DRAINING or STOPPED.
        """
        if self._state in (LifecycleState.DRAINING, LifecycleState.STOPPED):
            raise ServiceUnavailableError(self._state)
        self._active_requests += 1

    def request_finished(self) -> None:
        """Decrement the active request counter.

        Called at the end of each request by the lifecycle middleware.
        Safe to call even if the counter is already zero.
        """
        self._active_requests = max(0, self._active_requests - 1)

    def register_shutdown_hook(self, callback: Callable[[], None | Awaitable[None]]) -> None:
        """Register a cleanup function to run during shutdown.

        Hooks are called in registration order after all in-flight requests
        have drained (or the drain timeout has expired).

        Args:
            callback: A sync or async callable that performs cleanup
                (e.g., closing Redis connections, flushing metrics).
        """
        self._shutdown_hooks.append(callback)
        _logger.debug("shutdown_hook_registered", hook=callback.__name__)

    def get_health(self) -> dict[str, object]:
        """Return current lifecycle health information.

        Returns:
            Dict with the current state, active request count, and uptime.
        """
        uptime = time.monotonic() - self._start_time if self._start_time > 0 else 0.0
        return {
            "state": self._state.value,
            "active_requests": self._active_requests,
            "uptime_seconds": round(uptime, 2),
        }


async def lifecycle_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """FastAPI middleware that integrates request tracking with the lifecycle manager.

    Increments the active request counter before processing and decrements it
    after. Returns a 503 Service Unavailable response if the application is
    draining or not yet ready.

    Args:
        request: The incoming FastAPI request.
        call_next: The next middleware or route handler.

    Returns:
        The response from the route handler, or a 503 JSON response during drain.
    """
    manager = get_lifecycle_manager()

    try:
        manager.request_started()
    except ServiceUnavailableError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Service is shutting down. Please retry later."},
            headers={"Retry-After": "5"},
        )

    try:
        response: Response = await call_next(request)
        return response
    finally:
        manager.request_finished()


def get_lifecycle_manager(drain_timeout: int = 30) -> LifecycleManager:
    """Get the singleton LifecycleManager instance.

    Convenience function that delegates to LifecycleManager.get_instance().

    Args:
        drain_timeout: Maximum seconds to wait for request draining.
            Only used on first call when the instance is created.

    Returns:
        The shared LifecycleManager instance.
    """
    return LifecycleManager.get_instance(drain_timeout=drain_timeout)
