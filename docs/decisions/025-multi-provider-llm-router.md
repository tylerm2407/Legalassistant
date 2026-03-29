# ADR 025: Anthropic-Only LLM Router with Circuit Breaker

## Status

Accepted (supersedes original dual-provider design)

## Context

CaseMate's chat endpoint is the core user-facing feature. Initially, a dual-provider architecture (OpenAI GPT-4o primary, Anthropic Claude fallback) was implemented for resilience. However, this introduced unnecessary complexity — two API keys, response style variance during failover, and coupling to a provider we don't need. The master plan specifies Anthropic Claude (claude-sonnet-4-20250514) as the sole LLM, and Claude's instruction-following quality is superior for CaseMate's structured legal context injection.

## Decision

Simplify to a single-provider LLM router (`backend/utils/llm_router.py`) with:

1. **Single provider**: Anthropic Claude (claude-sonnet-4-20250514) for all chat completions
2. **Circuit breaker**: 3-failure threshold, 30s recovery timeout — prevents hammering a degraded API
3. **Per-provider metrics**: Track call counts, failure counts, latency, and circuit state for observability
4. **Observability endpoint**: `GET /api/llm/status` exposes router health for monitoring
5. **Streaming support**: SSE streaming via the Anthropic streaming API

## Architecture

```
chat request
    │
    ▼
┌──────────────────────────┐
│  Anthropic Claude        │
│  claude-sonnet-4-20250514│
│  (circuit-breaker guard) │
└────────────┬─────────────┘
             │
             ▼
         response
```

## Consequences

### Positive

- **Simpler architecture**: One provider, one API key, one response style
- **Better quality**: Claude's instruction-following is superior for structured legal context injection
- **Reduced cost**: No unused OpenAI API key or dependency
- **Resilience**: Circuit breaker still prevents cascading failures during API outages

### Negative

- **Single point of failure**: If Anthropic is down, chat is unavailable (mitigated by circuit breaker which fails fast rather than timing out)

### Trade-offs

We chose simplicity over redundancy. A dual-provider architecture adds complexity that isn't justified when the primary provider (Anthropic) has consistently high uptime and the response quality difference makes failover problematic anyway. If Anthropic reliability becomes an issue, a fallback provider can be re-added to the router with minimal changes.

## Alternatives Considered

1. **Dual-provider with failover**: OpenAI primary, Anthropic fallback. Rejected — unnecessary complexity, two API keys, response style variance.
2. **Load balancer pattern**: Round-robin between providers. Rejected — response quality differs between models.
3. **No circuit breaker**: Direct API calls with retry only. Rejected — doesn't prevent hammering a degraded service.
