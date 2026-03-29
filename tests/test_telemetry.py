"""Tests for the observability middleware and metrics collection.

Validates the MetricsCollector, LatencyHistogram, and telemetry
middleware for request tracing and metric aggregation.
"""

from __future__ import annotations

from backend.utils.telemetry import (
    LatencyHistogram,
    MetricsCollector,
    generate_trace_id,
)


class TestTraceIdGeneration:
    """Test trace ID generation for request correlation."""

    def test_generates_32_char_hex(self) -> None:
        trace_id = generate_trace_id()
        assert len(trace_id) == 32
        assert all(c in "0123456789abcdef" for c in trace_id)

    def test_generates_unique_ids(self) -> None:
        ids = {generate_trace_id() for _ in range(100)}
        assert len(ids) == 100  # All unique


class TestLatencyHistogram:
    """Test the latency histogram for percentile calculation."""

    def test_empty_histogram(self) -> None:
        hist = LatencyHistogram()
        assert hist.count == 0
        assert hist.total == 0.0
        assert hist.percentile(0.5) == 0.0

    def test_single_observation(self) -> None:
        hist = LatencyHistogram()
        hist.observe(0.15)
        assert hist.count == 1
        assert hist.total == 0.15

    def test_percentile_p50(self) -> None:
        hist = LatencyHistogram()
        for _ in range(50):
            hist.observe(0.1)
        for _ in range(50):
            hist.observe(1.0)

        p50 = hist.percentile(0.5)
        assert 0.1 <= p50 <= 1.0

    def test_percentile_p99(self) -> None:
        hist = LatencyHistogram()
        for _ in range(99):
            hist.observe(0.05)
        hist.observe(5.0)

        p99 = hist.percentile(0.99)
        assert p99 >= 0.05

    def test_to_dict_includes_required_fields(self) -> None:
        hist = LatencyHistogram()
        hist.observe(0.1)
        hist.observe(0.5)

        data = hist.to_dict()
        assert "buckets" in data
        assert "total" in data
        assert "count" in data
        assert "avg" in data
        assert "p50" in data
        assert "p95" in data
        assert "p99" in data
        assert data["count"] == 2


class TestMetricsCollector:
    """Test the in-process metrics collector singleton."""

    def test_increment_counter(self) -> None:
        collector = MetricsCollector()
        collector.increment("test_counter")
        collector.increment("test_counter")
        snapshot = collector.snapshot()
        assert snapshot["counters"]["test_counter"] == 2

    def test_observe_latency(self) -> None:
        collector = MetricsCollector()
        collector.observe_latency("test_latency", 0.1)
        collector.observe_latency("test_latency", 0.5)
        snapshot = collector.snapshot()
        assert "test_latency" in snapshot["histograms"]
        assert snapshot["histograms"]["test_latency"]["count"] == 2

    def test_increment_label(self) -> None:
        collector = MetricsCollector()
        collector.increment_label("status_codes", "200")
        collector.increment_label("status_codes", "200")
        collector.increment_label("status_codes", "404")
        snapshot = collector.snapshot()
        assert snapshot["labeled_counters"]["status_codes"]["200"] == 2
        assert snapshot["labeled_counters"]["status_codes"]["404"] == 1

    def test_snapshot_structure(self) -> None:
        collector = MetricsCollector()
        snapshot = collector.snapshot()
        assert "counters" in snapshot
        assert "histograms" in snapshot
        assert "labeled_counters" in snapshot
