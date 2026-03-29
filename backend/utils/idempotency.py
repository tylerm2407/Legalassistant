"""Redis-backed idempotency layer for API request deduplication.

Prevents duplicate operations (double-submits, webhook retries, network replays)
by fingerprinting requests and caching responses. Uses SHA-256 of request content
as the idempotency key, stores results in Redis with configurable TTL.

Fail-open design: if Redis is unavailable, every request is treated as unique.
This ensures the idempotency layer never blocks legitimate traffic.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any, ClassVar

from fastapi import Request
from pydantic import BaseModel, ConfigDict

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

DEFAULT_TTL_SECONDS = 300
KEY_PREFIX = "idempotency"


class IdempotencyResult(BaseModel):
    """Result of an idempotency check against the store.

    Attributes:
        is_duplicate: True if a cached response exists for this key.
        cached_response: The previously stored response dict, or None if not a duplicate.
        idempotency_key: The SHA-256 key used for deduplication.
        created_at: Timestamp when the original response was cached.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_duplicate: bool
    cached_response: dict[str, Any] | None = None
    idempotency_key: str
    created_at: datetime | None = None
    store_response: Callable[[dict[str, Any]], Coroutine[Any, Any, None]] | None = None


def _compute_idempotency_key(user_id: str, endpoint: str, body_hash: str) -> str:
    """Compute a deterministic idempotency key from request components.

    Produces a SHA-256 hash of the composite key so that identical requests
    from the same user to the same endpoint always resolve to the same key.

    Args:
        user_id: The authenticated user's ID.
        endpoint: The request path (e.g. /api/chat).
        body_hash: SHA-256 hex digest of the raw request body.

    Returns:
        A 64-character hex string suitable for use as a Redis key suffix.
    """
    composite = f"{user_id}:{endpoint}:{body_hash}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


def _hash_request_body(body: bytes) -> str:
    """Compute a SHA-256 hex digest of the raw request body.

    Used as one component of the composite idempotency key so that
    different payloads to the same endpoint produce different keys.

    Args:
        body: The raw request body bytes.

    Returns:
        A 64-character hex string.
    """
    return hashlib.sha256(body).hexdigest()


class IdempotencyStore:
    """Redis-backed store for idempotency keys and cached responses.

    Provides async check/store/invalidate operations against Redis.
    Follows fail-open semantics: if Redis is unavailable or errors occur,
    every request is treated as unique rather than blocking.

    Attributes:
        _redis_url: Redis connection URL from environment.
        _prefix: Key prefix for namespacing in Redis.
        _default_ttl: Default time-to-live in seconds for cached entries.
    """

    _instance: ClassVar[IdempotencyStore | None] = None

    def __init__(
        self,
        redis_url: str | None = None,
        prefix: str = KEY_PREFIX,
        default_ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self._redis_url = redis_url or os.environ.get("REDIS_URL", "")
        self._prefix = prefix
        self._default_ttl = default_ttl
        self._client: Any = None

    def _full_key(self, key: str) -> str:
        """Build the full Redis key with prefix.

        Args:
            key: The idempotency key suffix.

        Returns:
            Prefixed Redis key string.
        """
        return f"{self._prefix}:{key}"

    async def _get_client(self) -> Any:
        """Lazily initialize and return the async Redis client.

        Returns:
            An aioredis-compatible client, or None if unavailable.
        """
        if self._client is not None:
            return self._client
        if not self._redis_url:
            _logger.warning("redis_not_configured", detail="Idempotency checks disabled")
            return None
        try:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(self._redis_url, decode_responses=True)
            await self._client.ping()
            _logger.info("idempotency_redis_connected")
            return self._client
        except Exception as exc:
            _logger.error("idempotency_redis_connection_failed", error=str(exc))
            return None

    async def check(self, key: str) -> IdempotencyResult:
        """Check whether an idempotency key already exists in the store.

        Args:
            key: The idempotency key to look up.

        Returns:
            IdempotencyResult with is_duplicate=True and cached_response if found,
            or is_duplicate=False if the key is new or Redis is unavailable.
        """
        client = await self._get_client()
        if client is None:
            return IdempotencyResult(is_duplicate=False, idempotency_key=key)
        try:
            raw = await client.get(self._full_key(key))
            if raw is None:
                return IdempotencyResult(is_duplicate=False, idempotency_key=key)
            data = json.loads(raw)
            return IdempotencyResult(
                is_duplicate=True,
                cached_response=data.get("response"),
                idempotency_key=key,
                created_at=datetime.fromisoformat(data["created_at"]),
            )
        except Exception as exc:
            _logger.error("idempotency_check_failed", key=key, error=str(exc))
            return IdempotencyResult(is_duplicate=False, idempotency_key=key)

    async def store(self, key: str, response: dict[str, Any], ttl: int | None = None) -> None:
        """Store a response against an idempotency key with TTL.

        Args:
            key: The idempotency key.
            response: The response dict to cache.
            ttl: Time-to-live in seconds. Uses default_ttl if None.
        """
        client = await self._get_client()
        if client is None:
            return
        effective_ttl = ttl if ttl is not None else self._default_ttl
        try:
            payload = json.dumps(
                {
                    "response": response,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
            await client.set(self._full_key(key), payload, ex=effective_ttl)
            _logger.info("idempotency_stored", key=key, ttl=effective_ttl)
        except Exception as exc:
            _logger.error("idempotency_store_failed", key=key, error=str(exc))

    async def invalidate(self, key: str) -> None:
        """Manually invalidate a cached idempotency entry.

        Useful when a previously cached response is no longer valid
        (e.g. the user explicitly retries an action).

        Args:
            key: The idempotency key to remove.
        """
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.delete(self._full_key(key))
            _logger.info("idempotency_invalidated", key=key)
        except Exception as exc:
            _logger.error("idempotency_invalidate_failed", key=key, error=str(exc))


def get_idempotency_store() -> IdempotencyStore:
    """Get or create the module-level IdempotencyStore singleton.

    Returns:
        The shared IdempotencyStore instance.
    """
    if IdempotencyStore._instance is None:
        IdempotencyStore._instance = IdempotencyStore()
    return IdempotencyStore._instance


_IdempotencyDep = Callable[..., Coroutine[Any, Any, IdempotencyResult]]


def idempotency_guard(ttl: int = DEFAULT_TTL_SECONDS) -> _IdempotencyDep:
    """FastAPI dependency factory for request-level idempotency.

    Reads the raw request body, computes an idempotency key from the
    authenticated user_id, request path, and body hash, then checks
    the store. If a cached response exists, it is returned immediately.

    Supports an explicit ``Idempotency-Key`` header override: when present,
    the client-provided key is used instead of the computed hash.

    Args:
        ttl: Cache time-to-live in seconds for stored responses.

    Returns:
        A FastAPI dependency that yields an IdempotencyResult. If not a
        duplicate, the result includes a ``store_response`` callback that
        the endpoint must call to cache its response.
    """

    async def _dependency(request: Request) -> IdempotencyResult:
        """Resolve idempotency for the current request.

        Args:
            request: The incoming FastAPI request.

        Returns:
            IdempotencyResult with store_response callback attached when unique.
        """
        store = get_idempotency_store()
        body = await request.body()
        user_id = getattr(request.state, "user_id", "anonymous")
        endpoint = request.url.path

        # Allow client-provided idempotency key override
        header_key = request.headers.get("Idempotency-Key")
        if header_key:
            key = header_key
        else:
            body_hash = _hash_request_body(body)
            key = _compute_idempotency_key(user_id, endpoint, body_hash)

        result = await store.check(key)
        if result.is_duplicate:
            _logger.info(
                "idempotency_duplicate_detected",
                user_id=user_id,
                endpoint=endpoint,
                key=key,
            )
            return result

        # Attach a callback so the endpoint can store its response
        async def _store_response(response: dict[str, Any]) -> None:
            await store.store(key, response, ttl=ttl)

        result.store_response = _store_response
        return result

    return _dependency
