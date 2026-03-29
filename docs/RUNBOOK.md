# CaseMate Operations Runbook

> Last updated: 2026-03-29
>
> This runbook covers production operations for CaseMate, a personalized legal
> assistant. Every on-call engineer should read this before their first shift.

---

## 1. Service Overview

| Component | Technology | Host | Port / URL |
|-----------|-----------|------|------------|
| Backend API | FastAPI (Python 3.12) | Railway | `:8000` / `https://api.casematelaw.com` |
| Frontend | Next.js 14 (App Router) | Vercel | `https://casematelaw.com` |
| Database | Supabase (Postgres 15 + Auth + Storage + Realtime) | Supabase Cloud | Project dashboard |
| Cache | Redis | Railway (addon) | Internal `REDIS_URL` |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) | Anthropic | `https://api.anthropic.com` |
| Error Tracking | Sentry | Sentry Cloud | Project dashboard |
| Logging | structlog (JSON) | Railway logs | `railway logs` |
| Payments | Stripe | Stripe Cloud | `dashboard.stripe.com` |

### Dependency Graph

```
User → Vercel (Next.js) → Railway (FastAPI) → Anthropic Claude API
                                            → Supabase (Postgres + Auth + Storage)
                                            → Redis (rate limiting)
                                            → Stripe (payments)
```

Critical path for chat: **FastAPI → Supabase (profile read) → Anthropic (LLM call) → Supabase (profile update)**. If any of these are down, chat degrades or fails.

---

## 2. Health Checks

### Backend Health Endpoint

```bash
curl -s https://api.casematelaw.com/health | jq .
```

Expected response:

```json
{"status": "ok", "version": "0.4.0"}
```

**Alert conditions:**
- HTTP status != 200
- `status` field != `"ok"`
- Response time > 2 seconds
- `version` does not match the latest deployed git tag

### Manual Verification Checklist

```bash
# 1. Backend health
curl -s -o /dev/null -w "%{http_code} %{time_total}s" https://api.casematelaw.com/health

# 2. Frontend loads
curl -s -o /dev/null -w "%{http_code}" https://casematelaw.com

# 3. Supabase connectivity (from Railway shell)
railway run python -c "from supabase import create_client; print('ok')"

# 4. Redis connectivity (from Railway shell)
railway run python -c "import redis, os; r=redis.from_url(os.environ['REDIS_URL']); print(r.ping())"

# 5. Anthropic API reachable
curl -s -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages \
  -d '{"model":"claude-sonnet-4-6","max_tokens":1,"messages":[{"role":"user","content":"ping"}]}' \
  -H "content-type: application/json" -H "anthropic-version: 2023-06-01" | jq .type
```

---

## 3. Common Failure Scenarios

### 3.1 Anthropic API Errors (429, 500, 529)

**Symptoms:**
- Chat responses fail with 500 or return error messages
- Action generators (letter, rights, checklist) return errors
- Logs show `anthropic_api_error` or `anthropic_api_retry` events

**Root cause:** Rate limit exceeded (429), Anthropic service degradation (500), or API overloaded (529).

**Diagnosis:**

```bash
# Check structured logs for Anthropic errors
railway logs | grep -E "anthropic_api_error|anthropic_api_retry|circuit_breaker"

# Check Anthropic status page
# https://status.anthropic.com
```

**Built-in resilience:**
- **Retry:** `tenacity` decorator retries up to 3 attempts with exponential backoff (1s, 2s, 4s) on `anthropic.APIError` and `anthropic.RateLimitError`. Defined in `backend/utils/retry.py`.
- **Circuit breaker:** Opens after 5 consecutive failures. Recovery timeout is 30 seconds, then a single probe request is allowed (HALF_OPEN state). Defined in `backend/utils/circuit_breaker.py`.

**Resolution:**
1. Check https://status.anthropic.com for ongoing incidents.
2. If rate-limited (429): wait for the circuit breaker to recover automatically. If persistent, request a rate limit increase from Anthropic.
3. If overloaded (529): transient. The retry + circuit breaker pattern handles this. No action needed unless it persists > 5 minutes.
4. If 500: Anthropic-side issue. Nothing to do but wait and monitor.

**Escalation:** If the outage persists > 30 minutes, post a status banner on the frontend and notify users via email.

---

### 3.2 Supabase Connection Failure

**Symptoms:**
- All authenticated endpoints return 401
- Profile reads/writes fail with 500
- Conversation storage fails
- Document uploads fail
- Logs show connection errors or timeout events

**Diagnosis:**

```bash
# Check Supabase status
# https://status.supabase.com

# Verify environment variables are set
railway variables | grep SUPABASE

# Test connectivity from Railway shell
railway run python -c "
import os
from supabase import create_client
c = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])
print(c.table('user_profiles').select('id').limit(1).execute())
"
```

**Resolution:**
1. Check Supabase dashboard for project status and any paused/rate-limited state.
2. If keys were rotated: update `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_JWT_SECRET` in Railway dashboard, then redeploy.
3. If connection pool exhausted: check active connections in Supabase dashboard under Database > Connection Pooling. Consider increasing pool size via Supavisor settings.
4. If project is paused (free tier): resume from the Supabase dashboard.

---

### 3.3 Redis Unavailable

**Symptoms:**
- Rate limiting silently stops working (fail-open design)
- No user-visible errors (by design)
- Logs show `redis_connection_error` events
- Potential for abuse if down for extended period

**Diagnosis:**

```bash
# Check Redis connectivity
railway run python -c "
import redis, os
r = redis.from_url(os.environ.get('REDIS_URL', ''))
print(r.ping())
"

# Check if REDIS_URL is set
railway variables | grep REDIS_URL
```

**Resolution:**
1. Rate limiting fails open by design: availability of the chat feature takes priority over rate enforcement. This is intentional.
2. Restart the Redis addon in Railway if it is unresponsive.
3. If the connection string changed, update `REDIS_URL` in Railway and redeploy.
4. While Redis is down, monitor for abuse patterns (excessive requests from single IPs/users) via Railway logs.
5. If abuse is detected during the outage, block at the Railway/Vercel edge level.

---

### 3.4 Memory Injection Failure

**Symptoms:**
- Chat responses become generic (no state law citations, no personal context references)
- Users report CaseMate "forgot" their situation
- Logs show `profile_not_found` or `injection_error` events

**Diagnosis:**

```bash
# Check for injection errors in logs
railway logs | grep -E "profile_not_found|injection_error|build_system_prompt"

# Verify profile exists for a specific user
railway run python -c "
import os
from supabase import create_client
c = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])
result = c.table('user_profiles').select('*').eq('user_id', 'USER_ID_HERE').execute()
print(result.data)
"
```

**Root causes:**
- Profile missing from Supabase (user skipped onboarding somehow)
- Profile data is corrupted or missing required fields (state, housing_situation)
- `build_system_prompt()` in `backend/memory/injector.py` threw an exception
- Legal area classification failed, returning no state context

**Resolution:**
1. If profile is missing: check if the user completed onboarding. If not, redirect them to `/onboarding`.
2. If profile is corrupted: manually inspect and fix via Supabase dashboard SQL editor.
3. If `build_system_prompt()` is throwing: check for missing state laws in `backend/legal/state_laws.py` for the user's state + legal area combination.
4. Memory injection is the core product. Treat any injection failure as P1.

---

### 3.5 Stripe Webhook Failure

**Symptoms:**
- New subscriptions are not reflected in user accounts
- Cancellations are not processed
- Payment status is stale
- Stripe dashboard shows webhook delivery failures

**Diagnosis:**

```bash
# Check Stripe webhook logs
# https://dashboard.stripe.com/webhooks (click the CaseMate endpoint)

# Check backend logs for webhook errors
railway logs | grep -E "stripe_webhook_error|webhook_signature"
```

**Common causes:**
- `STRIPE_WEBHOOK_SECRET` mismatch after Stripe endpoint was recreated
- Backend deployed to a new URL but Stripe webhook endpoint not updated
- Webhook endpoint timing out (Stripe expects response within 20 seconds)

**Resolution:**
1. Verify `STRIPE_WEBHOOK_SECRET` in Railway matches the secret shown in Stripe dashboard for this endpoint.
2. If the backend URL changed, update the webhook endpoint URL in Stripe dashboard.
3. Replay failed events: Stripe dashboard > Webhooks > select endpoint > Failed deliveries > Retry.
4. If events are consistently timing out, check if the webhook handler is doing too much synchronous work. Offload to background tasks.

---

### 3.6 Document Upload / OCR Pipeline Failure

**Symptoms:**
- Document uploads fail or return errors
- Uploaded PDFs are not analyzed (no facts extracted)
- Image-based document uploads fail specifically

**Diagnosis:**

```bash
# Check for OCR-specific errors
railway logs | grep -E "tesseract_not_found|ocr_error|document_extract|pdfplumber"

# Verify Tesseract is installed (for image-based documents)
railway run tesseract --version

# Verify Supabase Storage is accessible
railway run python -c "
import os
from supabase import create_client
c = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])
buckets = c.storage.list_buckets()
print([b.name for b in buckets])
"
```

**Resolution:**
1. PDF text extraction uses `pdfplumber` (pure Python, no system dependency). If this fails, check the pip install.
2. Image OCR requires `pytesseract` + system `tesseract-ocr`. Ensure the Railway Dockerfile or Nixpack includes `tesseract-ocr`.
3. If Supabase Storage is full or the bucket does not exist, create it via dashboard or `supabase` CLI.
4. Large files (>10MB) may timeout. Check the upload size limit in FastAPI config.

---

### 3.7 Profile Auto-Updater Failure

**Symptoms:**
- New facts mentioned in conversations are not appearing in the user profile
- Profile sidebar in the UI shows stale data
- Logs show `profile_update_error` events

**Diagnosis:**

```bash
railway logs | grep -E "profile_update_error|update_profile_from_conversation"
```

**Root cause:** The profile updater runs as a FastAPI `BackgroundTask` after each chat response. If the background task crashes, the user never sees an error (the chat response already returned), but facts are silently lost.

**Resolution:**
1. Check if the Anthropic API call within the updater is failing (separate from the main chat call).
2. Verify the Supabase write for the profile is succeeding.
3. The updater only adds facts, never removes them. If facts are disappearing, something else is overwriting the profile.
4. Restart the backend service to clear any stuck background tasks.

---

## 4. Performance Baselines

| Metric | Target (P50) | Alert Threshold (P95) | Notes |
|--------|-------------|----------------------|-------|
| Chat response (non-streaming) | < 3s | > 5s | Includes profile read + LLM call + response |
| Chat response (SSE first token) | < 200ms | > 500ms | Time to first streamed token |
| Profile load (`GET /api/profile`) | < 100ms | > 300ms | Single Supabase read |
| Legal classification (keyword) | < 5ms | > 50ms | In-memory keyword matching |
| Legal classification (LLM fallback) | < 1s | > 2s | Only when keyword matching fails |
| Document upload + OCR | < 5s | > 10s | Depends on document size |
| Action generation (letter/rights/checklist) | < 4s | > 8s | Single LLM call with profile context |
| Health check (`GET /health`) | < 50ms | > 200ms | No external dependencies |
| Memory injection (`build_system_prompt`) | < 10ms | > 50ms | In-memory string assembly |
| Profile auto-update (background) | < 5s | N/A | Runs async, user does not wait |

**Monitoring approach:** structlog emits `duration_ms` on every request via middleware. Aggregate in your log analysis tool and set alerts on P95 thresholds.

---

## 5. Deployment Procedures

### Standard Deployment

```bash
# 1. Verify locally before deploying
make verify   # Runs lint + full test suite. Must pass with zero failures.

# 2. Backend (Railway) — auto-deploys from main branch
git push origin main
# Railway watches main and deploys automatically.

# 3. Frontend (Vercel) — auto-deploys from main branch
# Same push triggers Vercel deployment.

# 4. Verify deployment
curl -s https://api.casematelaw.com/health | jq .version
# Should match the version in pyproject.toml
```

### Rollback

```bash
# Backend rollback (Railway)
railway rollback
# Or: revert the commit and push to main

# Frontend rollback (Vercel)
# Use Vercel dashboard: Deployments > select previous > Promote to Production
# Or: revert the commit and push to main
```

### Database Migrations

```bash
# Apply migrations via Supabase CLI
supabase db push

# Or apply manually via Supabase dashboard SQL editor
# Always test migrations against the staging branch first:
supabase db reset --linked  # Reset staging to verify migration chain
```

### Environment Variable Changes

1. Backend: Set via Railway dashboard (Settings > Variables). Redeploy after changes.
2. Frontend: Set via Vercel dashboard (Settings > Environment Variables). Redeploy after changes.
3. Never store secrets in code or commit them to git.

### Pre-Deployment Checklist

- [ ] `make verify` passes (lint + tests)
- [ ] No secrets in the diff (`git diff --cached | grep -iE "sk-|eyJ|password|secret"`)
- [ ] CHANGELOG.md updated if user-facing changes
- [ ] Database migrations tested against staging branch (if applicable)
- [ ] Stripe webhook endpoint updated (if backend URL changed)

---

## 6. Monitoring and Alerting

### Structured Logging

All backend logs are JSON-formatted via `structlog`. Every log entry includes:

- `user_id` — the authenticated user (if applicable)
- `request_id` — unique per-request identifier
- `duration_ms` — request processing time
- `event` — structured event name (not free-form text)

### Key Log Events to Monitor

| Event | Severity | Meaning |
|-------|----------|---------|
| `anthropic_api_error` | ERROR | Claude API call failed after all retries |
| `anthropic_api_retry` | WARNING | Claude API call retrying (transient failure) |
| `circuit_breaker_opened` | ERROR | Circuit breaker tripped for a service |
| `circuit_breaker_closed` | INFO | Circuit breaker recovered |
| `rate_limit_exceeded` | WARNING | User hit rate limit |
| `profile_not_found` | ERROR | Chat attempted without a user profile |
| `injection_error` | ERROR | Memory injection failed (P1) |
| `profile_update_error` | ERROR | Background profile updater failed |
| `stripe_webhook_error` | ERROR | Stripe webhook processing failed |
| `redis_connection_error` | WARNING | Redis unavailable (rate limiting disabled) |
| `document_extract_error` | ERROR | Document text extraction failed |
| `tesseract_not_found` | ERROR | OCR system dependency missing |

### Sentry Integration

- All unhandled exceptions are captured with `user_id` context.
- Performance tracing is enabled for all API endpoints.
- Dashboard: check Sentry project for error spikes after deployments.

### Log Querying (Railway)

```bash
# All errors in the last hour
railway logs --since 1h | grep '"level":"error"'

# Anthropic-specific issues
railway logs --since 1h | grep "anthropic_api"

# Specific user's requests
railway logs --since 1h | grep '"user_id":"USER_ID_HERE"'

# Circuit breaker state changes
railway logs --since 6h | grep "circuit_breaker"
```

---

## 7. Scaling Considerations

### Backend (Railway)

- Railway auto-scales horizontally. No sticky sessions are required — all state is in Supabase.
- Each instance handles ~100 concurrent SSE connections comfortably.
- If response times degrade under load, add instances via Railway scaling settings.
- Background tasks (profile updater) run in-process. Under extreme load, these may compete with request handling. Consider moving to a task queue (Celery/Redis) if this becomes a bottleneck.

### Supabase (Database)

- Connection pooling is handled by Supavisor. Monitor connection count in Supabase dashboard.
- If connection count approaches pool limit: check for connection leaks, increase pool size, or add read replicas for profile reads.
- Row-level security (RLS) is enabled. Ensure policies are optimized to avoid full table scans.

### Redis (Rate Limiting)

- Single instance is sufficient for rate limiting up to ~10K concurrent users.
- If Redis memory usage grows: check for key expiry issues in the rate limiter. Keys should have TTLs matching the rate limit window.
- Rate limiting is not in the critical path (fail-open). Redis scaling is low priority.

### Anthropic API

- Rate limits are per-organization. Monitor usage in the Anthropic console.
- Each chat request makes 1 LLM call (chat) + 1 background LLM call (profile updater) = 2 calls per user message.
- Action generation adds 1 additional call per action.
- If approaching rate limits: implement request queuing or upgrade the Anthropic API tier.

### Frontend (Vercel)

- Vercel edge network handles scaling automatically.
- SSE connections from the chat interface are proxied through Vercel to Railway. Under very high load, consider having the frontend connect directly to the Railway backend for SSE.

---

## 8. Security Incident Response

### Response Framework (NIST-aligned)

**1. Identify**
- Check Sentry alerts for unusual error patterns.
- Monitor for spikes in 401/403 responses (credential stuffing).
- Watch for unusual API consumption patterns in Anthropic console.
- Check Stripe for fraudulent payment activity.

**2. Contain**
- Rotate affected API keys immediately:
  - Anthropic: https://console.anthropic.com/settings/keys
  - Supabase: Project Settings > API (regenerate anon/service role keys)
  - Stripe: Developers > API keys > Roll key
  - Redis: Update connection string in Railway
- If a user account is compromised: disable the account via Supabase Auth dashboard.
- If the backend is compromised: take the Railway service offline (`railway down`).

**3. Eradicate**
- Identify the vulnerability and deploy a fix.
- Run `make verify` to ensure the fix does not break existing functionality.
- Audit logs for the scope of the breach (which user data was accessed).

**4. Recover**
- Re-enable services with new credentials.
- Verify all health checks pass.
- Monitor closely for 24 hours post-incident.

**5. Post-Mortem**
- Document the incident in `docs/decisions/` as an Architecture Decision Record.
- Include: timeline, root cause, impact, resolution, and preventive measures.
- Share with the team (Tyler + Owen) for review.

### Sensitive Data Inventory

| Data Type | Location | Encryption | Access Control |
|-----------|----------|------------|----------------|
| User legal profiles | Supabase (Postgres) | At rest (Supabase managed) | RLS + service role key |
| Conversation history | Supabase (Postgres) | At rest (Supabase managed) | RLS + service role key |
| Uploaded documents | Supabase Storage | At rest (Supabase managed) | Auth-gated bucket policies |
| Payment info | Stripe (never stored locally) | Stripe PCI compliance | Stripe API keys |
| API keys | Railway/Vercel env vars | Platform-managed | Dashboard access only |

---

## 9. Disaster Recovery

### Data Loss Scenarios

| Scenario | Recovery | RPO | RTO |
|----------|----------|-----|-----|
| Supabase database corruption | Supabase daily backups (Pro plan) | 24 hours | 1-2 hours |
| Supabase Storage loss | No automated backup — document re-upload required | N/A | User-dependent |
| Redis data loss | No backup needed — rate limit counters are ephemeral | 0 | Immediate (auto-reconnect) |
| Railway service gone | Redeploy from git (`railway up`) | 0 (code in git) | ~5 minutes |
| Vercel deployment gone | Redeploy from git (auto on push) | 0 (code in git) | ~2 minutes |

### Recovery Commands

```bash
# Redeploy backend from scratch
railway up

# Redeploy frontend
vercel deploy --prod

# Restore Supabase from backup (via dashboard)
# Supabase Dashboard > Project > Database > Backups > Restore

# Re-seed demo data (for staging/demo environments)
make seed
```

---

## 10. On-Call Playbook

### Severity Levels

| Level | Definition | Response Time | Examples |
|-------|-----------|--------------|---------|
| P1 | Service down or memory injection broken | 15 minutes | Backend 500s, Supabase down, injection failures |
| P2 | Degraded experience | 1 hour | Slow responses, OCR failures, stale profiles |
| P3 | Minor issue | Next business day | UI glitch, non-critical log errors |
| P4 | Improvement | Backlog | Performance tuning, log cleanup |

### Triage Steps (any alert)

1. Check `GET /health` — is the backend alive?
2. Check Sentry — are there new unhandled exceptions?
3. Check Railway logs — any error spikes in the last 15 minutes?
4. Check Anthropic status — is the API degraded?
5. Check Supabase dashboard — is the project healthy?
6. If all external dependencies are healthy, the issue is in our code. Check the most recent deployment.

### Rollback Decision

Roll back if:
- The issue appeared immediately after a deployment
- `make verify` passed locally but production is broken (environment-specific bug)
- You cannot identify the root cause within 15 minutes

Do not roll back if:
- The issue is in an external dependency (Anthropic, Supabase, Stripe)
- The issue existed before the latest deployment
- A targeted fix is ready and can be deployed in < 10 minutes
