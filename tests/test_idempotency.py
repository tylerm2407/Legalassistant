"""Tests for the Redis-backed idempotency layer.

Covers key computation, body hashing, store check/store/invalidate operations,
fail-open behavior on Redis failure, header override, and concurrent access.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.utils.idempotency import (
    IdempotencyResult,
    IdempotencyStore,
    _compute_idempotency_key,
    _hash_request_body,
    get_idempotency_store,
    idempotency_guard,
)

# ---------------------------------------------------------------------------
# Key computation
# ---------------------------------------------------------------------------


def test_compute_idempotency_key_deterministic():
    """Same inputs always produce the same key."""
    key_a = _compute_idempotency_key("user_1", "/api/chat", "abc123")
    key_b = _compute_idempotency_key("user_1", "/api/chat", "abc123")
    assert key_a == key_b
    assert len(key_a) == 64  # SHA-256 hex digest


def test_compute_idempotency_key_varies_with_inputs():
    """Changing any component produces a different key."""
    base = _compute_idempotency_key("user_1", "/api/chat", "abc123")
    diff_user = _compute_idempotency_key("user_2", "/api/chat", "abc123")
    diff_endpoint = _compute_idempotency_key("user_1", "/api/profile", "abc123")
    diff_body = _compute_idempotency_key("user_1", "/api/chat", "xyz789")

    assert base != diff_user
    assert base != diff_endpoint
    assert base != diff_body


# ---------------------------------------------------------------------------
# Body hashing
# ---------------------------------------------------------------------------


def test_hash_request_body_deterministic():
    """Same body bytes always produce the same hash."""
    body = b'{"message": "hello"}'
    assert _hash_request_body(body) == _hash_request_body(body)
    assert len(_hash_request_body(body)) == 64


def test_different_bodies_different_keys():
    """Different request bodies produce different hashes."""
    hash_a = _hash_request_body(b'{"message": "hello"}')
    hash_b = _hash_request_body(b'{"message": "world"}')
    assert hash_a != hash_b


# ---------------------------------------------------------------------------
# IdempotencyStore — check / store / invalidate
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_redis():
    """Create a mock async Redis client with get/set/delete/ping."""
    client = AsyncMock()
    client.ping = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def store(mock_redis):
    """Return an IdempotencyStore with a pre-injected mock Redis client."""
    s = IdempotencyStore(redis_url="redis://localhost:6379", prefix="test")
    s._client = mock_redis
    return s


@pytest.mark.asyncio
async def test_check_returns_not_duplicate_when_empty(store, mock_redis):
    """Check returns is_duplicate=False when the key does not exist in Redis."""
    mock_redis.get.return_value = None

    result = await store.check("some_key")

    assert result.is_duplicate is False
    assert result.cached_response is None
    assert result.idempotency_key == "some_key"
    mock_redis.get.assert_called_once_with("test:some_key")


@pytest.mark.asyncio
async def test_store_and_check_returns_duplicate(store, mock_redis):
    """After storing a response, check returns is_duplicate=True with cached data."""
    response_data = {"status": "ok", "data": {"id": 42}}
    now = datetime.now(UTC)

    # Store the response
    await store.store("dup_key", response_data, ttl=60)
    mock_redis.set.assert_called_once()

    # Simulate Redis returning the stored value
    stored_payload = json.dumps(
        {
            "response": response_data,
            "created_at": now.isoformat(),
        }
    )
    mock_redis.get.return_value = stored_payload

    result = await store.check("dup_key")

    assert result.is_duplicate is True
    assert result.cached_response == response_data
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_store_respects_ttl(store, mock_redis):
    """Store passes the TTL to Redis set command."""
    await store.store("ttl_key", {"ok": True}, ttl=120)

    call_args = mock_redis.set.call_args
    assert call_args.kwargs.get("ex") == 120 or call_args[1].get("ex") == 120


@pytest.mark.asyncio
async def test_invalidate_removes_entry(store, mock_redis):
    """Invalidate calls Redis delete on the correct key."""
    await store.invalidate("old_key")

    mock_redis.delete.assert_called_once_with("test:old_key")


# ---------------------------------------------------------------------------
# Fail-open behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_redis_failure_fails_open():
    """When Redis raises an exception, check returns is_duplicate=False."""
    failing_client = AsyncMock()
    failing_client.get = AsyncMock(side_effect=ConnectionError("Redis down"))

    s = IdempotencyStore(redis_url="redis://localhost:6379")
    s._client = failing_client

    result = await s.check("any_key")

    assert result.is_duplicate is False
    assert result.cached_response is None


# ---------------------------------------------------------------------------
# Idempotency-Key header override
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_idempotency_key_header_override():
    """Client-provided Idempotency-Key header overrides computed key."""
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b'{"msg": "test"}')
    mock_request.url.path = "/api/chat"
    mock_request.headers = {"Idempotency-Key": "custom-key-abc"}
    mock_request.state = MagicMock()
    mock_request.state.user_id = "user_1"

    mock_store = AsyncMock(spec=IdempotencyStore)
    mock_store.check = AsyncMock(
        return_value=IdempotencyResult(
            is_duplicate=False,
            idempotency_key="custom-key-abc",
        )
    )

    with patch("backend.utils.idempotency.get_idempotency_store", return_value=mock_store):
        dep = idempotency_guard(ttl=300)
        result = await dep(mock_request)

    assert result.idempotency_key == "custom-key-abc"
    mock_store.check.assert_called_once_with("custom-key-abc")


# ---------------------------------------------------------------------------
# Concurrent requests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_requests_same_key(store, mock_redis):
    """Multiple concurrent checks for the same key all resolve correctly."""
    mock_redis.get.return_value = None

    results = await asyncio.gather(
        store.check("concurrent_key"),
        store.check("concurrent_key"),
        store.check("concurrent_key"),
    )

    assert all(not r.is_duplicate for r in results)
    assert mock_redis.get.call_count == 3

    # Now simulate one having stored
    stored = json.dumps(
        {
            "response": {"done": True},
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    mock_redis.get.return_value = stored

    results_after = await asyncio.gather(
        store.check("concurrent_key"),
        store.check("concurrent_key"),
    )
    assert all(r.is_duplicate for r in results_after)


# ---------------------------------------------------------------------------
# Singleton getter
# ---------------------------------------------------------------------------


def test_get_idempotency_store_returns_singleton():
    """get_idempotency_store returns the same instance on repeated calls."""
    # Reset singleton for test isolation
    IdempotencyStore._instance = None
    try:
        a = get_idempotency_store()
        b = get_idempotency_store()
        assert a is b
    finally:
        IdempotencyStore._instance = None
