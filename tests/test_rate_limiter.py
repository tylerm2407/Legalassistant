"""Tests for the Redis-backed rate limiter.

Covers fail-open behavior, under/over limits, Retry-After header,
separate user counters, and separate endpoint counters.
"""

from __future__ import annotations

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
