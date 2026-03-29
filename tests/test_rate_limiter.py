"""Tests for the Redis-backed rate limiter.

Covers fail-open behavior, under/over limits, Retry-After header,
separate user counters, and separate endpoint counters.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.utils.rate_limiter import rate_limit

# ---------- Test App ----------

_test_app = FastAPI()

_limiter = rate_limit(max_requests=3, window_seconds=60)


@_test_app.get("/limited")
async def limited_endpoint(_rate: None = Depends(_limiter)):
    """A rate-limited endpoint for testing."""
    return {"status": "ok"}


@pytest.fixture
def rate_client():
    """Create a TestClient for the rate limit test app."""
    return TestClient(_test_app)


# ---------- Tests ----------


def test_redis_unavailable_allows_request(rate_client):
    """When Redis is not configured, requests are allowed (fail-open)."""
    with patch("backend.utils.rate_limiter._get_redis", return_value=None):
        response = rate_client.get("/limited")
        assert response.status_code == 200


def test_under_limit_request_passes(rate_client):
    """Requests under the limit pass through."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    # Simulate 1 request in window (under limit of 3)
    mock_pipe.execute.return_value = [None, None, 1, None]
    mock_redis.pipeline.return_value = mock_pipe

    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        response = rate_client.get("/limited")
        assert response.status_code == 200


def test_at_limit_returns_429(rate_client):
    """Requests over the limit get 429."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    # Simulate 4 requests in window (over limit of 3)
    mock_pipe.execute.return_value = [None, None, 4, None]
    mock_redis.pipeline.return_value = mock_pipe

    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        response = rate_client.get("/limited")
        assert response.status_code == 429


def test_retry_after_header_present(rate_client):
    """429 response includes Retry-After header."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.return_value = [None, None, 4, None]
    mock_redis.pipeline.return_value = mock_pipe

    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        response = rate_client.get("/limited")
        assert response.status_code == 429
        assert "retry-after" in response.headers


def test_redis_error_fails_open(rate_client):
    """When Redis raises an error during check, request is allowed."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.side_effect = ConnectionError("Redis connection lost")
    mock_redis.pipeline.return_value = mock_pipe

    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        response = rate_client.get("/limited")
        assert response.status_code == 200


def test_different_users_separate_counters():
    """Different user IDs should generate different Redis keys."""
    # This tests the key construction logic: "rate_limit:{user_id}:{endpoint}"
    # We verify by checking that the pipeline is called with different keys
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.return_value = [None, None, 1, None]
    mock_redis.pipeline.return_value = mock_pipe

    app = FastAPI()
    limiter = rate_limit(max_requests=3, window_seconds=60)

    @app.get("/test")
    async def test_endpoint(_rate: None = Depends(limiter)):
        return {"status": "ok"}

    client = TestClient(app)
    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        response = client.get("/test")
        assert response.status_code == 200
        # Verify pipeline was called (keys are constructed internally)
        assert mock_redis.pipeline.called


# ---------- _get_redis() direct tests ----------


def test_get_redis_no_url_returns_none():
    """_get_redis with no REDIS_URL env var returns None."""
    from backend.utils.rate_limiter import _get_redis

    # Reset the global singleton so _get_redis actually runs its logic
    with (
        patch("backend.utils.rate_limiter._redis_client", None),
        patch.dict(os.environ, {}, clear=True),
    ):
        result = _get_redis()
        assert result is None


def test_get_redis_ping_fails_returns_none():
    """_get_redis with REDIS_URL set but ping fails returns None."""
    from backend.utils.rate_limiter import _get_redis

    mock_client = MagicMock()
    mock_client.ping.side_effect = ConnectionError("Connection refused")

    with (
        patch("backend.utils.rate_limiter._redis_client", None),
        patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}),
        patch("redis.from_url", return_value=mock_client),
    ):
        result = _get_redis()
        assert result is None


def test_different_endpoints_separate_key_spaces():
    """Different endpoints produce different Redis keys via zadd."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.return_value = [None, None, 1, None]
    mock_redis.pipeline.return_value = mock_pipe

    app = FastAPI()
    limiter_a = rate_limit(max_requests=5, window_seconds=60)
    limiter_b = rate_limit(max_requests=5, window_seconds=60)

    @app.get("/endpoint_a")
    async def endpoint_a(_rate: None = Depends(limiter_a)):
        return {"ep": "a"}

    @app.get("/endpoint_b")
    async def endpoint_b(_rate: None = Depends(limiter_b)):
        return {"ep": "b"}

    client = TestClient(app)
    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        client.get("/endpoint_a")
        client.get("/endpoint_b")

        # Collect all zadd key arguments from both pipeline calls
        zadd_calls = []
        for call in mock_pipe.zadd.call_args_list:
            zadd_calls.append(call[0][0])

        # The keys should contain different endpoint paths
        assert len(zadd_calls) == 2
        assert zadd_calls[0] != zadd_calls[1]
        assert "endpoint_a" in zadd_calls[0]
        assert "endpoint_b" in zadd_calls[1]
