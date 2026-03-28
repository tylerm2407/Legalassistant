# ADR 001 — Memory as the core differentiator

**Date:** 2026-03-27
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Persistent user legal profile — injected into every Claude API call as structured context — is the primary differentiator of CaseMate. We build deep on personalization rather than broad on legal domain coverage.

---

## Context

The legal AI space already has generic chatbots that answer one question and forget you exist. The core product question was: what makes a user pay $20/month instead of just asking Claude directly?

We evaluated three differentiation strategies:

1. **Breadth** — cover more legal areas than any competitor
2. **Accuracy** — invest in fine-tuned legal models with citation verification
3. **Memory** — build persistent context that makes every conversation smarter than the last

The problem with breadth is that it is easily copied. Any team can add ten more legal areas in a weekend. The problem with accuracy is that it requires proprietary legal data and model training that cannot be built in 36 hours.

Memory is defensible in a way the others are not. A user whose full legal situation — their state, their housing dispute, their employer's specific violation, the exact facts they shared two months ago — is known by the system has an experience that no generic tool can replicate. The longer they use CaseMate, the better CaseMate gets at helping them specifically. That is a compounding retention advantage.

There is also a direct analogy to what makes a human attorney relationship valuable. The most important thing your lawyer knows is not case law — it is your situation. A lawyer you have worked with for three years is categorically more useful than a new one, even if the new one graduated from a better school. CaseMate replicates that relationship dynamic for people who cannot afford $349/hour.

---

## The implementation

Every Claude API call in CaseMate receives a system prompt assembled from three layers:

1. **CaseMate base instructions** — response philosophy, plain English mandate, action-first rules
2. **User's legal profile** — state, housing, employment, active issues, extracted legal facts
3. **State-specific legal context** — relevant statutes for the user's jurisdiction and the classified legal domain of their question

The `memory/injector.py` module owns this assembly. It is the most important file in the codebase.

After every conversation, the `memory/updater.py` background task extracts new legal facts from the exchange and writes them back to the user's profile in Supabase. The memory compounds automatically without user action.

---

## Alternatives considered

**No persistent memory — stateless per conversation**
Rejected. This is indistinguishable from any other legal chatbot. No retention advantage, no pricing power, no moat.

**Vector database RAG over conversation history**
Considered but rejected for MVP. The user's legal situation is structured data — state, housing type, active issues — not semantic embeddings. A Pydantic model in Postgres is faster to build, easier to display in the UI, and more reliable for the core use case. RAG can be added in a future version for document retrieval.

**User manually maintains their profile**
Rejected. If users have to update their own profile, they won't. The auto-updater running as a background task after every response means the memory grows without friction.

---

## Consequences

**Positive:**
- Every conversation after the first is meaningfully more valuable than a generic tool
- Retention compounds — the longer a user stays, the harder CaseMate is to replace
- The profile sidebar makes the memory visible during chat, creating a tangible product experience
- Clear moat that grows over time as legal facts accumulate

**Negative:**
- Requires Supabase setup and auth before any legal functionality works
- Profile auto-updater adds backend complexity (background tasks, retry logic)
- Profile quality depends on conversation quality — if users give vague answers, facts are vague
- Privacy surface area is larger than a stateless tool (mitigated by Supabase RLS)

---

## Status

Accepted. The entire architecture flows from this decision. All other ADRs are downstream of this one.
