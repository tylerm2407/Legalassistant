# ADR 009 — Keyword-based legal classifier over LLM call

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Legal domain classification uses deterministic keyword matching against 10 legal domains rather than an LLM call. The classifier in `backend/legal/classifier.py` scores each domain by counting keyword hits in the user's message and returns the highest-scoring domain — or `"general"` if nothing matches.

---

## Context

Every user message must be classified into one of 10 legal domains (landlord_tenant, employment_rights, consumer_protection, debt_collections, small_claims, contract_disputes, traffic_violations, family_law, criminal_records, immigration) before the system prompt can be assembled. The classifier output feeds directly into `build_system_prompt()` in `memory/injector.py`, which uses it to select state-specific statute context from `STATE_LAWS`.

We evaluated two approaches:

1. **LLM classification** — Send the question to Claude with a classification prompt and parse the response
2. **Keyword matching** — Compare the question against curated keyword lists per domain

The classifier runs on every single user message, before the main Claude API call. It is in the critical path of chat latency. An LLM classification call would add 500–1500ms to every request and consume tokens that do not contribute to the user-facing response. It would also double the Anthropic API cost per conversation turn.

The legal domain space is well-bounded at 10 categories. The vocabulary users employ when asking about landlord disputes, employment issues, or debt collections is highly predictable. A keyword list of 15–20 terms per domain captures the vast majority of real user questions without ambiguity.

---

## The implementation

`backend/legal/classifier.py` defines a `DOMAIN_KEYWORDS` dictionary mapping each of the 10 legal domains to 15–20 representative keywords. The `classify_legal_area()` function lowercases the user's question, counts keyword matches per domain using substring matching, and returns the domain with the highest score. If no domain scores above zero, it returns `"general"`.

The function is synchronous and pure — no I/O, no API calls, no database reads. It executes in microseconds. Each domain has keywords chosen to minimize cross-domain overlap (e.g., "eviction" is unambiguously landlord_tenant, "garnishment" is unambiguously debt_collections).

---

## Alternatives considered

**LLM-based classification with Claude**
Rejected. Adds latency (500–1500ms), doubles API cost per turn, and introduces a failure point before the main response. The bounded domain space does not justify the overhead. Classification accuracy for these 10 categories is achievable with keywords alone.

**Embedding-based classification**
Considered but rejected. Requires maintaining an embedding model or making an additional API call. Over-engineered for a 10-class problem where the classes have distinct vocabularies. Would also add a dependency on a vector similarity library.

**Hybrid: keyword first, LLM fallback**
Deferred to a future version. The `"general"` fallback currently handles ambiguous messages by letting the system prompt work without domain-specific statute context. If classification accuracy becomes a measurable problem, a secondary LLM call for `"general"` cases could be added without changing the hot path.

---

## Consequences

**Positive:**
- Zero additional latency — classification is synchronous and sub-millisecond
- Zero additional API cost — no tokens consumed for classification
- Fully deterministic — same question always maps to the same domain, which simplifies testing
- No external dependency — works offline, no API key required for classification

**Negative:**
- Keyword lists require manual curation when adding new legal domains
- Ambiguous questions (e.g., "my landlord broke our contract") may match multiple domains — highest count wins, which is imperfect
- Novel phrasing with no matching keywords falls through to `"general"` and loses state-specific context
- Cannot handle nuanced multi-domain questions (e.g., employment discrimination leading to a housing issue)

---

## Status

Accepted. The keyword classifier handles the current 10 legal domains well. If a future domain expansion or user testing reveals significant classification failures, the hybrid approach (keyword first, LLM fallback for `"general"`) can be added incrementally.
