# ADR 025: Multi-Provider LLM Router with Automatic Failover

## Status

Accepted

## Context

CaseMate's chat endpoint is the core user-facing feature. A single-provider architecture (only Anthropic or only OpenAI) creates a single point of failure — if the provider has an outage, degradation, or rate limit event, all users lose access to the product simultaneously.

During the hackathon, we switched from Anthropic Claude to OpenAI GPT-4o for the chat endpoint to leverage a different model's strengths. This created an opportunity to implement a more resilient architecture rather than a simple provider swap.

## Decision

Implement a dual-model LLM router (`backend/utils/llm_router.py`) with:

1. **Priority chain**: OpenAI GPT-4o as primary, Anthropic Claude as fallback
2. **Independent circuit breakers**: Each provider has its own circuit breaker (3 failures to open, 30s recovery)
3. **Transparent failover**: If the primary fails or its circuit opens, requests automatically route to the fallback with no caller-side changes
4. **Per-provider metrics**: Track call counts, failure counts, latency, and circuit state for observability
5. **Observability endpoint**: `GET /api/llm/status` exposes router health for monitoring

## Architecture

```
chat request
    │
    ▼
┌─────────────────┐    circuit open?    ┌──────────────────┐
│  OpenAI GPT-4o  │ ──────────────────► │ Anthropic Claude │
│  (primary)      │     or API error    │ (fallback)       │
└────────┬────────┘                     └────────┬─────────┘
         │                                       │
         ▼                                       ▼
     response                               response
```

## Consequences

### Positive

- **Zero-downtime AI**: Provider outages don't take down the product
- **Cost optimization**: Can route to cheaper models for specific query types in the future
- **Observability**: Per-provider metrics enable data-driven provider selection
- **Streaming support**: Both providers support SSE streaming through the router

### Negative

- **Two API keys required**: Both OPENAI_API_KEY and ANTHROPIC_API_KEY must be configured
- **Response style variance**: Users may notice subtle differences in response style during failover
- **Added complexity**: The router adds ~300 lines of code and 13 tests

### Trade-offs

We chose independent circuit breakers over a shared circuit because provider outages are independent events — OpenAI being down doesn't imply Anthropic is down. The 3-failure threshold is aggressive (vs the 5-failure threshold on the standalone Anthropic breaker) because we have a fallback and want to fail over quickly.

## Alternatives Considered

1. **Simple try/except fallback**: No circuit breaker, just catch errors and retry with the other provider. Rejected because it doesn't prevent hammering a degraded provider.
2. **Load balancer pattern**: Round-robin between providers. Rejected because response quality differs between models — we want a primary preference.
3. **Single provider with retry**: Just retry the same provider with exponential backoff. Rejected because it doesn't help during extended outages.
