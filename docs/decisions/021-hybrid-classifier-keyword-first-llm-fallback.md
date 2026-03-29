# ADR 021 — Hybrid Classifier: Keyword-First with LLM Fallback

**Status:** Accepted
**Date:** 2026-03-29
**Decision Makers:** Tyler Moore, Owen Ash

---

## Context

Legal area classification is the first step in every chat request. The user's question must be routed to one of 10 legal domains (landlord_tenant, employment_rights, consumer_protection, etc.) before `build_system_prompt()` in `memory/injector.py` can select the correct state-specific statute context from `STATE_LAWS`. A misclassification means the user gets statutes for the wrong legal area — which is worse than no statutes at all.

ADR 009 established a pure keyword classifier. That works for clear-cut questions like "my landlord won't return my deposit" (unambiguously landlord_tenant). But user testing surfaced a class of ambiguous queries where keyword matching fails or misclassifies:

- "My boss won't let me take breaks" — could be employment_rights or labor law depending on state
- "I got a letter saying I owe money for a car accident" — debt_collections or traffic_violations or consumer_protection
- "Can they really do this?" — no domain keywords at all, falls to `"general"` and loses all state-specific context

The `"general"` fallback rate in testing was approximately 8-12% of queries. Those users get a noticeably worse experience — no state-specific citations, no statute references. That gap is unacceptable for a product where personalization is the differentiator.

We needed a solution that preserves the speed of keyword matching for the 90%+ of queries where it works, while recovering the ambiguous 8-12% without adding latency or cost to the majority of requests.

---

## Decision

Implement a hybrid classifier: keyword-first with LLM fallback only when the keyword classifier's confidence is below a configurable threshold.

The flow:

1. `classify_legal_area()` runs the existing keyword matcher. It returns the top domain and a confidence score (ratio of top domain's keyword hits to total keyword hits across all domains).
2. If confidence >= 0.6 (top domain has at least 60% of all keyword matches), return immediately. Cost: 0. Latency: <1ms.
3. If confidence < 0.6 OR no keywords matched at all, invoke a lightweight Claude Haiku call with a classification-only prompt. The prompt lists the 10 domains with one-sentence descriptions and asks for a single-word response. Cost: ~$0.003. Latency: ~800ms.
4. The LLM fallback result is cached per normalized query string (lowercased, stripped of punctuation) for 1 hour in Redis. Repeated ambiguous questions from any user hit cache instead of the API.

The confidence threshold of 0.6 was chosen empirically: at 0.5, too many clear-cut queries fall through to the LLM. At 0.7, the LLM handles 20%+ of traffic, which defeats the purpose. At 0.6, keyword handles ~92% of queries and the LLM sees ~8%.

---

## Alternatives Considered

### Pure LLM classification (every request)

Accurate across all query types, including ambiguous and novel phrasing. But this adds ~800ms latency and ~$0.003 cost to every single chat request, before the main Claude Sonnet call even begins. At 10,000 daily active users averaging 5 messages each, that is 50,000 classification calls/day = $150/day just for classification. The latency compounds: users wait 800ms longer for every response, and the classification call can fail independently, requiring its own retry logic. Rejected because 90%+ of queries do not need it.

### Pure keyword matching (status quo from ADR 009)

Free, fast, deterministic. But the 8-12% general fallback rate means roughly 1 in 10 users gets a degraded experience on any given question. For a product where personalized state-specific legal context is the entire value proposition, losing that context 10% of the time is a meaningful quality gap. The pure keyword approach was the right v1 decision (ADR 009), but user testing showed it needs a safety net.

### Fine-tuned classification model

A fine-tuned distilBERT or similar small model could classify all 10 domains in <10ms with high accuracy. But: (a) we do not have labeled training data — building a dataset of 1,000+ classified legal questions per domain is weeks of work, (b) the model needs retraining every time we add a legal domain, (c) hosting a custom model adds infrastructure (GPU instance or serverless inference endpoint), and (d) the accuracy advantage over keyword+LLM-fallback is marginal for our 10-class problem. This becomes attractive if we scale to 50+ legal domains. Not justified now.

### Embedding similarity classification

Embed each domain's description and the user's query, return the closest domain by cosine similarity. Similar infrastructure burden to fine-tuning (need an embedding model hosted or an API call). Adds latency comparable to an LLM call. Does not meaningfully outperform keyword matching for well-separated domains. Rejected.

---

## Consequences

### Positive

- 92%+ of requests classified in <1ms with zero API cost — identical to the pure keyword approach for the common case
- Ambiguous queries now get correct domain classification instead of falling through to `"general"`
- Redis caching means repeated ambiguous queries (common in legal Q&A — many users ask similar things) only hit the LLM once
- The confidence threshold is configurable — we can tune it based on production classification accuracy data without code changes
- LLM fallback uses Haiku (cheapest model), not Sonnet — cost per fallback is ~$0.003, not ~$0.015

### Negative

- Added complexity: two classification paths instead of one, plus cache management
- LLM fallback introduces non-determinism — the same ambiguous query could theoretically classify differently on cache miss (mitigated by caching)
- Redis becomes a soft dependency for the caching layer (fail-open: if Redis is down, LLM is called every time for ambiguous queries)
- The confidence threshold (0.6) was tuned on a small test set — may need adjustment with real production traffic

### Risks

- If the keyword lists become stale (e.g., new legal terminology emerges), the LLM fallback rate could creep above 10%, increasing costs. Mitigation: monitor fallback rate weekly, update keyword lists when fallback rate exceeds 15%.
- Cache poisoning: if the LLM misclassifies an ambiguous query, the wrong answer is cached for 1 hour. Mitigation: short TTL (1 hour), cache is per-query not per-domain, and misclassification of ambiguous queries is low-impact (user still gets a relevant response, just with slightly less targeted statute context).

---

## Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Keyword hit rate | >90% of requests | Log classification path (keyword vs. LLM) per request |
| LLM fallback rate | <10% of requests | Count of LLM classification calls / total classifications |
| P95 classification latency | <50ms | Timer around `classify_legal_area()` including fallback |
| LLM fallback cache hit rate | >60% after warm-up | Redis cache hit/miss ratio for classification keys |
| Classification accuracy | >95% on test set | Periodic manual review of 100 random classifications |
