"""Circuit breaker pattern for external service resilience.

Implements the three-state circuit breaker pattern (CLOSED → OPEN → HALF_OPEN)
to protect against cascading failures when external services (Anthropic API,
Supabase, Redis) are degraded or unavailable.

State transitions:
  - CLOSED: Normal operation. Requests pass through. Failures are counted.
  - OPEN: Service is assumed down. All requests fail-fast without calling
    the service. After a configurable cooldown, transitions to HALF_OPEN.
  - HALF_OPEN: A single probe request is allowed through. If it succeeds,
    the breaker transitions back to CLOSED. If it fails, back to OPEN.

This avoids hammering a degraded service with retries and provides faster
failure responses to users during outages.
"""

from __future__ import annotations

import asyncio
import enum
import time
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class CircuitState(enum.Enum):
    """The three states of a circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when a call is rejected because the circuit breaker is OPEN.

    Attributes:
        service_name: The name of the protected service.
        retry_after: Seconds until the circuit breaker will allow a probe request.
    """

    def __init__(self, service_name: str, retry_after: float) -> None:
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker OPEN for {service_name}. Retry after {retry_after:.1f}s."
        )


class CircuitBreaker:
    """Thread-safe circuit breaker for protecting external service calls.

    Tracks consecutive failures and opens the circuit when the failure
    threshold is reached. After a cooldown period, allows a single probe
    request to test if the service has recovered.

    Args:
        service_name: Human-readable name for logging (e.g. 'anthropic_api').
        failure_threshold: Number of consecutive failures before opening. Defaults to 5.
        recovery_timeout: Seconds to wait in OPEN state before probing. Defaults to 30.
        half_open_max_calls: Max concurrent calls allowed in HALF_OPEN state. Defaults to 1.

    Example::

        breaker = CircuitBreaker("anthropic_api", failure_threshold=5, recovery_timeout=30)

        @breaker
        async def call_claude(prompt: str) -> str:
            return await client.messages.create(...)
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._total_rejected = 0
        self._last_state_change: float = time.monotonic()

    @property
    def state(self) -> CircuitState:
        """Current circuit breaker state, accounting for recovery timeout."""
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                return CircuitState.HALF_OPEN
        return self._state

    @property
    def metrics(self) -> dict[str, object]:
        """Current circuit breaker metrics for observability.

        Returns:
            Dict with state, failure count, and call statistics.
        """
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_rejected": self._total_rejected,
            "uptime_seconds": time.monotonic() - self._last_state_change,
        }

    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state with logging.

        Args:
            new_state: The target circuit state.
        """
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.monotonic()
        _logger.info(
            "circuit_breaker_state_change",
            service=self.service_name,
            from_state=old_state.value,
            to_state=new_state.value,
            failure_count=self._failure_count,
        )

    async def _record_success(self) -> None:
        """Record a successful call and reset failure count."""
        async with self._lock:
            self._failure_count = 0
            self._half_open_calls = 0
            if self._state != CircuitState.CLOSED:
                await self._transition_to(CircuitState.CLOSED)

    async def _record_failure(self) -> None:
        """Record a failed call and potentially open the circuit."""
        async with self._lock:
            self._failure_count += 1
            self._total_failures += 1
            self._last_failure_time = time.monotonic()
            self._half_open_calls = 0

            if self._failure_count >= self.failure_threshold and self._state != CircuitState.OPEN:
                await self._transition_to(CircuitState.OPEN)

    async def _check_state(self) -> None:
        """Check if the current state allows a request through.

        Raises:
            CircuitBreakerOpenError: If the circuit is OPEN and not yet
                ready for a probe request.
        """
        current = self.state

        if current == CircuitState.CLOSED:
            return

        if current == CircuitState.OPEN:
            retry_after = self.recovery_timeout - (time.monotonic() - self._last_failure_time)
            self._total_rejected += 1
            raise CircuitBreakerOpenError(self.service_name, max(0.0, retry_after))

        # HALF_OPEN: allow limited probe requests
        async with self._lock:
            if self._half_open_calls >= self.half_open_max_calls:
                self._total_rejected += 1
                raise CircuitBreakerOpenError(self.service_name, 5.0)
            self._half_open_calls += 1
            if self._state != CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.HALF_OPEN)

    def __call__(self, func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        """Decorate an async function with circuit breaker protection.

        Args:
            func: The async function to protect.

        Returns:
            Wrapped function that checks the circuit state before each call.
        """

        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            self._total_calls += 1
            await self._check_state()

            try:
                result = await func(*args, **kwargs)
                await self._record_success()
                return result
            except CircuitBreakerOpenError:
                raise
            except Exception:
                await self._record_failure()
                raise

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper


# Pre-configured circuit breakers for CaseMate's external services
anthropic_breaker = CircuitBreaker(
    service_name="anthropic_api",
    failure_threshold=5,
    recovery_timeout=30.0,
)

supabase_breaker = CircuitBreaker(
    service_name="supabase",
    failure_threshold=10,
    recovery_timeout=15.0,
)
