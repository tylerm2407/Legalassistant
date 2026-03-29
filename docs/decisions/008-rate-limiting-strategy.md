# ADR 008 — Redis sliding window rate limiting with graceful degradation

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Use a Redis-backed sliding window rate limiter using sorted sets, with fail-open behavior when Redis is unavailable. Per-endpoint configuration (chat: 20/min, actions: 10/min, documents: 5/min). Returns HTTP 429 with a `Retry-After` header when limits are exceeded.

---

## Context

Every CaseMate chat message triggers a Claude API call that costs $3–15 per million tokens. The action generators and document analyzer also call Claude. Without rate limiting, a single abusive user or automated bot could run up thousands of dollars in API costs in minutes. At the same time, CaseMate is an early-stage product where availability matters more than strict enforcement — if the rate limiter itself fails, users should still be able to use the product.

The question was how to protect against cost runaway without introducing a single point of failure.

---

## The implementation

`backend/utils/rate_limiter.py` exposes a `rate_limit(max_requests, window_seconds)` factory that returns a FastAPI dependency function. The dependency is injected into endpoint definitions.

The sliding window algorithm uses Redis sorted sets:
1. Remove all entries older than the window (`ZREMRANGEBYSCORE`)
2. Add the current timestamp (`ZADD`)
3. Count entries in the set (`ZCARD`)
4. Set TTL on the key (`EXPIRE`)

All four operations run in a single Redis pipeline for atomicity. The key format is `rate_limit:{user_id}:{endpoint}`, providing per-user, per-endpoint isolation. The `user_id` is extracted from `request.state` (set by the auth middleware).

When the count exceeds `max_requests`, a 429 response is returned with a `Retry-After` header set to the window duration.

**Graceful degradation:** The Redis client is a lazy singleton. If `REDIS_URL` is not set or the connection fails, the client returns `None` and the rate limiter allows all requests through. If Redis errors occur during a check, the exception is caught, logged, and the request proceeds. This fail-open design ensures Redis downtime never blocks users.

---

## Alternatives considered

**In-memory rate limiting (e.g., per-process dict)**
Rejected. Does not work with multiple backend processes or containers. A user could bypass limits by hitting different instances. Only viable for single-process development.

**API gateway rate limiting (e.g., Cloudflare, AWS API Gateway)**
Considered for production but rejected for MVP. Adds infrastructure dependency and configuration outside the codebase. The in-app limiter is portable, testable, and sufficient for launch.

**Fixed window counters**
Considered as a simpler alternative. Rejected because fixed windows allow burst traffic at window boundaries — a user could make 20 requests at 0:59 and 20 more at 1:01, effectively doubling their rate. Sliding windows distribute limits evenly.

**No rate limiting**
Rejected. Claude API costs make this a non-starter. A single day of abuse could exceed the monthly API budget.

---

## Consequences

**Positive:**
- Protects against API cost runaway from abuse or bugs
- Fail-open design means Redis downtime never blocks legitimate users
- Sliding window prevents burst exploitation at window boundaries
- Per-endpoint config allows tighter limits on expensive operations (documents, actions)
- `Retry-After` header gives clients clear guidance on when to retry

**Negative:**
- Requires Redis as an infrastructure dependency (optional but recommended for production)
- Fail-open means rate limiting is effectively disabled without Redis — acceptable for early stage but needs monitoring
- Sorted set memory grows with request volume (mitigated by TTL expiration)
- Per-user keying requires auth middleware to run before rate limiting — anonymous endpoints need a fallback key strategy

---

## Status

Accepted. Implemented in `backend/utils/rate_limiter.py`. Redis is optional — the app runs without it with rate limiting disabled.
