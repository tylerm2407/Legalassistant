"""Redis-backed rate limiting for API endpoints.

Provides a configurable rate limiter that tracks request counts per user
in Redis with sliding window counters.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable

from fastapi import HTTPException, Request, status

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

_redis_client = None


def _get_redis() -> object | None:
    """Get or create the Redis client singleton.

    Returns:
        An initialized Redis client, or None if Redis is not configured.
    """
    global _redis_client  # noqa: PLW0603
    if _redis_client is None:
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            _logger.warning("redis_not_configured", detail="Rate limiting disabled")
            return None
        try:
            import redis

            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
            _logger.info("redis_connected")
        except Exception as exc:
            _logger.error("redis_connection_failed", error=str(exc))
            return None
    return _redis_client


def rate_limit(max_requests: int, window_seconds: int = 60) -> Callable:
    """Create a rate limiting dependency for FastAPI endpoints.

    Uses a sliding window counter in Redis keyed by user_id.
    Falls back to allowing all requests if Redis is unavailable.

    Args:
        max_requests: Maximum number of requests allowed per window.
        window_seconds: The time window in seconds. Defaults to 60.

    Returns:
        A FastAPI dependency function that enforces the rate limit.
    """

    async def _check_rate_limit(request: Request) -> None:
        """Check if the current request exceeds the rate limit.

        Args:
            request: The incoming FastAPI request.

        Raises:
            HTTPException: 429 if the rate limit is exceeded.
        """
        client = _get_redis()
        if client is None:
            return  # Rate limiting disabled — allow request

        # Extract user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", "anonymous")
        endpoint = request.url.path
        key = f"rate_limit:{user_id}:{endpoint}"

        try:
            current_time = int(time.time())
            window_start = current_time - window_seconds

            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.zcard(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()

            request_count = results[2]

            if request_count > max_requests:
                retry_after = window_seconds
                _logger.warning(
                    "rate_limit_exceeded",
                    user_id=user_id,
                    endpoint=endpoint,
                    count=request_count,
                    limit=max_requests,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )

        except HTTPException:
            raise
        except Exception as exc:
            _logger.error("rate_limit_check_failed", error=str(exc))
            # Fail open — allow the request if Redis errors

    return _check_rate_limit
