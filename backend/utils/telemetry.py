"""OpenTelemetry-compatible observability middleware for CaseMate.

Provides request tracing, latency histograms, and custom metric counters
without requiring a full OpenTelemetry collector deployment. Metrics are
collected in-process and exposed via a /metrics endpoint for Prometheus
scraping or periodic log export.

Architecture:
  - RequestTracer middleware: Captures per-request spans with method, path,
    status code, and latency. Attaches user_id for user-level analytics.
  - MetricsCollector: In-process counters and histograms for business metrics
    (chat latency, classifier distribution, profile update frequency).
  - Span context propagation: Generates trace IDs for correlating logs
    across the request lifecycle (request → background task → Supabase write).
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import ClassVar

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


def generate_trace_id() -> str:
    """Generate a unique trace ID for request correlation.

    Returns:
        A 32-character hex string suitable for W3C Trace Context.
    """
    return uuid.uuid4().hex


@dataclass
class LatencyHistogram:
    """Simple histogram for tracking latency distributions.

    Collects latency samples into predefined buckets for percentile
    estimation without requiring a full statistics library.

    Attributes:
        buckets: Sorted list of upper bounds for histogram buckets (in seconds).
        counts: Number of observations in each bucket.
        total: Sum of all observed values.
        count: Total number of observations.
    """

    buckets: list[float] = field(
        default_factory=lambda: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
    )
    counts: list[int] = field(default_factory=list)
    total: float = 0.0
    count: int = 0

    def __post_init__(self) -> None:
        """Initialize bucket counts to zero."""
        if not self.counts:
            self.counts = [0] * len(self.buckets)

    def observe(self, value: float) -> None:
        """Record a latency observation.

        Args:
            value: The observed latency in seconds.
        """
        self.total += value
        self.count += 1
        for i, bound in enumerate(self.buckets):
            if value <= bound:
                self.counts[i] += 1

    def percentile(self, p: float) -> float:
        """Estimate a percentile from the histogram.

        Args:
            p: The percentile to estimate (0.0 to 1.0, e.g. 0.95 for p95).

        Returns:
            The estimated latency at the given percentile, or 0.0 if no data.
        """
        if self.count == 0:
            return 0.0

        target = int(self.count * p)
        cumulative = 0
        for i, bucket_count in enumerate(self.counts):
            cumulative += bucket_count
            if cumulative >= target:
                return self.buckets[i]
        return self.buckets[-1]

    def to_dict(self) -> dict[str, object]:
        """Export histogram data for the metrics endpoint.

        Returns:
            Dict with bucket boundaries, counts, total, and percentiles.
        """
        return {
            "buckets": {
                str(bound): count for bound, count in zip(self.buckets, self.counts, strict=True)
            },
            "total": round(self.total, 4),
            "count": self.count,
            "avg": round(self.total / self.count, 4) if self.count > 0 else 0,
            "p50": round(self.percentile(0.5), 4),
            "p95": round(self.percentile(0.95), 4),
            "p99": round(self.percentile(0.99), 4),
        }


class MetricsCollector:
    """In-process metrics collector for CaseMate observability.

    Collects counters and histograms for key business and operational
    metrics. Thread-safe for use across concurrent async requests.

    Singleton pattern ensures a single metrics instance across the app.
    """

    _instance: ClassVar[MetricsCollector | None] = None

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, LatencyHistogram] = defaultdict(LatencyHistogram)
        self._labels: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    @classmethod
    def get_instance(cls) -> MetricsCollector:
        """Get or create the singleton MetricsCollector.

        Returns:
            The shared MetricsCollector instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a counter metric.

        Args:
            metric: The metric name (e.g. 'chat_requests_total').
            value: Amount to increment by. Defaults to 1.
        """
        self._counters[metric] += value

    def observe_latency(self, metric: str, seconds: float) -> None:
        """Record a latency observation in a histogram.

        Args:
            metric: The histogram name (e.g. 'chat_latency_seconds').
            seconds: The observed latency in seconds.
        """
        self._histograms[metric].observe(seconds)

    def increment_label(self, metric: str, label: str) -> None:
        """Increment a labeled counter (e.g. classifier domain distribution).

        Args:
            metric: The metric name (e.g. 'legal_area_classified').
            label: The label value (e.g. 'landlord_tenant').
        """
        self._labels[metric][label] += 1

    def snapshot(self) -> dict[str, object]:
        """Export a snapshot of all collected metrics.

        Returns:
            Dict with counters, histograms, and labeled counters.
        """
        return {
            "counters": dict(self._counters),
            "histograms": {name: hist.to_dict() for name, hist in self._histograms.items()},
            "labeled_counters": {name: dict(labels) for name, labels in self._labels.items()},
        }


async def telemetry_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """FastAPI middleware that traces every request with latency and metadata.

    Attaches a trace_id to the request state and structlog context for
    end-to-end correlation across the request lifecycle. Records request
    latency in a histogram and increments per-path counters.

    Args:
        request: The incoming FastAPI request.
        call_next: The next middleware or route handler.

    Returns:
        The response with an X-Trace-ID header added.
    """
    trace_id = generate_trace_id()
    request.state.trace_id = trace_id

    # Bind trace_id to structlog for correlated log entries
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(trace_id=trace_id)

    metrics = MetricsCollector.get_instance()
    start_time = time.monotonic()

    try:
        response: Response = await call_next(request)
        latency = time.monotonic() - start_time

        metrics.increment("http_requests_total")
        metrics.observe_latency("http_request_latency_seconds", latency)
        metrics.increment_label("http_status_codes", str(response.status_code))

        # Add trace headers for client-side correlation
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(int(latency * 1000))

        _logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=round(latency * 1000, 2),
            user_id=getattr(request.state, "user_id", "anonymous"),
        )

        return response

    except Exception as exc:
        latency = time.monotonic() - start_time
        metrics.increment("http_errors_total")
        metrics.observe_latency("http_request_latency_seconds", latency)

        _logger.error(
            "http_request_error",
            method=request.method,
            path=request.url.path,
            error_type=type(exc).__name__,
            latency_ms=round(latency * 1000, 2),
        )
        raise


def get_metrics_response() -> JSONResponse:
    """Generate a JSON response with all collected metrics.

    Returns:
        JSONResponse with the current metrics snapshot.
    """
    metrics = MetricsCollector.get_instance()
    return JSONResponse(content=metrics.snapshot())
