# Utils — Backend Utilities Reference

> Authentication, rate limiting, retry logic, API client, and structured logging.

---

## Auth — JWT Verification

**Source:** `backend/utils/auth.py`

```python
async def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> str:
```

FastAPI dependency that protects all authenticated endpoints.

### How it works

1. Extracts the Bearer token from the `Authorization` header
2. Decodes the JWT using `SUPABASE_JWT_SECRET` with:
   - Algorithm: `HS256`
   - Audience: `"authenticated"`
3. Returns the `sub` claim as `user_id` (string UUID)

### Error handling

| Condition | HTTP Status | Detail |
|-----------|-------------|--------|
| `SUPABASE_JWT_SECRET` not set | 500 | `"Server configuration error"` |
| Token expired | 401 | `"Token has expired"` |
| Invalid token / bad signature | 401 | `"Invalid authentication token"` |

### Usage in routes

```python
@app.get("/api/profile")
async def get_profile(user_id: str = Depends(verify_supabase_jwt)):
    # user_id is guaranteed to be a valid, authenticated user
    ...
```

---

## Rate Limiter — Redis Sliding Window

**Source:** `backend/utils/rate_limiter.py`

```python
def rate_limit(max_requests: int, window_seconds: int) -> Callable:
```

Returns a FastAPI dependency that enforces per-user rate limits using Redis.

### Algorithm

Uses a **sliding window counter** in Redis:

1. Key format: `rate_limit:{user_id}:{endpoint}`
2. Increments the counter for the current window
3. If count exceeds `max_requests`, raises `HTTPException(429)`
4. Keys auto-expire after `window_seconds`

### Fail-open pattern

If Redis is unavailable (connection error, timeout), the rate limiter **allows all requests** and logs a warning. This ensures the app doesn't break if Redis goes down — rate limiting degrades gracefully rather than blocking legitimate users.

### Usage

```python
@app.post("/api/actions/letter")
async def generate_letter(
    user_id: str = Depends(verify_supabase_jwt),
    _: None = Depends(rate_limit(max_requests=5, window_seconds=60)),
):
    ...
```

### Standard limits

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| Chat | 20/min | 60s |
| Actions (letter/rights/checklist) | 5/min | 60s |
| Profile CRUD | 10/min | 60s |
| Deadlines CRUD | 10/min | 60s |
| Export | 5/min | 60s |
| Export email | 3/min | 60s |

---

## Retry — Anthropic API Calls

**Source:** `backend/utils/retry.py`

```python
@retry_anthropic
async def some_claude_call(...):
    ...
```

A [tenacity](https://tenacity.readthedocs.io/) decorator for all Anthropic API calls.

### Configuration

| Parameter | Value |
|-----------|-------|
| Max attempts | 3 |
| Backoff strategy | Exponential (1s → 2s → 4s) |
| Min wait | 1 second |
| Max wait | 16 seconds |
| Multiplier | 1 |
| Retried exceptions | `anthropic.APIError`, `anthropic.RateLimitError` |

### Logging

Each retry attempt is logged with:
- `attempt_number` — which retry this is (1, 2, 3)
- `exception_type` — the exception class name
- `exception_message` — the error detail
- `wait_seconds` — how long until the next attempt

### Behavior

After all 3 attempts are exhausted, the original exception is re-raised to the caller. This is intentional — the caller (usually an API endpoint) handles the final error and returns an appropriate HTTP response.

---

## Client — Singleton Anthropic

**Source:** `backend/utils/client.py`

```python
def get_anthropic_client() -> AsyncAnthropic:
```

Returns a singleton `AsyncAnthropic` client instance. Created once on first call, reused for all subsequent calls.

### Configuration

| Parameter | Value |
|-----------|-------|
| `api_key` | From `ANTHROPIC_API_KEY` env var |
| `timeout` | 30.0 seconds |

### Why singleton

Creating multiple `AsyncAnthropic` instances wastes connection pool resources. The singleton pattern ensures one client handles all API calls with shared connection pooling.

Logs `"anthropic_client_initialized"` on first creation.

---

## Logger — Structured Logging

**Source:** `backend/utils/logger.py`

```python
def get_logger(name: str) -> structlog.BoundLogger:
```

Returns a [structlog](https://www.structlog.org/) logger with JSON rendering and context binding.

### Configuration

`configure_logging(log_level="INFO")` sets up:

| Feature | Detail |
|---------|--------|
| Rendering | JSON in production, console (colored) if `DEBUG` |
| Processors | contextvars merge, log level, logger name, ISO timestamp, stack info, exception info, unicode decode |
| stdlib integration | Bridges Python's built-in `logging` to structlog |

### Usage

```python
from backend.utils.logger import get_logger

log = get_logger(__name__)

# Always include user_id for debugging
log.info("profile_updated", user_id=user_id, facts_added=3)
log.error("claude_api_failed", user_id=user_id, error=str(e))
log.warning("rate_limit_exceeded", user_id=user_id, endpoint="/api/chat")
```

### Rules

1. **Always include `user_id`** — every log entry must be traceable to a user
2. **Use structured key-value pairs** — not string interpolation
3. **Never use `print()`** — always use the structured logger
4. **Log at appropriate levels:** `info` for normal operations, `warning` for degraded state, `error` for failures

---

## Additional Utilities

### Circuit Breaker — `backend/utils/circuit_breaker.py`

Prevents cascading failures when external services (Anthropic API) are down. Opens after consecutive failures, half-opens to test recovery.

### Telemetry — `backend/utils/telemetry.py`

Request/response tracking middleware. Logs request method, path, status code, and duration for every API call.

### Token Budget — `backend/utils/token_budget.py`

Manages context window usage for Claude API calls. Ensures profile data + state laws + conversation history fit within model limits.

---

## Related

- [SECURITY.md](SECURITY.md) — How secrets and auth are managed
- [API.md](API.md) — Endpoints that use these utilities
- [TESTING.md](TESTING.md) — How utilities are mocked in tests
