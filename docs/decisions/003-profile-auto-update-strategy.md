# ADR 003 — Profile auto-update strategy

**Date:** 2026-03-27
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

After every CaseMate response, a background task automatically extracts new legal facts from the conversation and writes them to the user's profile in Supabase. Users never manually update their profile. The memory grows without friction.

---

## Context

The value of CaseMate's memory layer depends entirely on whether the memory stays current and grows over time. If users have to manually update their profile after every conversation, most won't — and the memory stagnates at the initial five onboarding answers.

The auto-updater solves this. When a user says "by the way, my landlord never gave me a copy of the lease" in conversation 8, that fact gets extracted and stored automatically. Conversation 12, when they ask about their rights, CaseMate already knows this without them having to mention it again.

This is the mechanism that makes the memory compound. Without it, CaseMate is a chatbot with a profile. With it, CaseMate is an assistant that gets smarter the more you use it.

---

## The implementation

The auto-updater runs as a FastAPI `BackgroundTask` — it starts after the response has been sent to the user, never blocking the main response stream.

```python
# backend/memory/updater.py

async def update_profile_from_conversation(
    user_id: str,
    conversation: list[dict],
    supabase: Client,
) -> None:
    """
    Extracts new legal facts from the latest conversation exchange and
    writes them to the user's profile in Supabase.

    Called as a FastAPI BackgroundTask after every chat response.
    Never blocks the user-facing response stream.

    Extraction prompt instructs Claude to identify:
    - New factual claims about the user's legal situation
    - New active issues (disputes, violations, ongoing cases)
    - Updates to existing issues (resolved, escalated, new developments)
    - Document references mentioned but not yet uploaded

    Only new facts are written. Existing facts are never overwritten.
    Profile grows monotonically — facts are added, never removed.

    Args:
        user_id: Authenticated user ID for profile lookup and write.
        conversation: Full message history including the latest exchange.
        supabase: Service-role Supabase client for profile writes.
    """
```

### What gets extracted

The updater passes the conversation to Claude with a structured extraction prompt:

```
Review this conversation and extract:

1. NEW LEGAL FACTS — specific factual claims about the user's situation
   that were not in their profile before this conversation.
   Examples:
   - "Landlord did not provide move-in checklist"
   - "Employee was paid below minimum wage for 3 months"
   - "Contract was signed under duress"

2. NEW ACTIVE ISSUES — disputes or legal situations mentioned for the
   first time. Include: type, brief summary, apparent status.

3. ISSUE UPDATES — changes to existing active issues:
   resolved, escalated, new information emerged.

Return JSON only. If nothing new was learned, return empty arrays.
Do not extract opinions, advice, or questions — only facts about
the user's actual legal situation.
```

### What does NOT get extracted

- Legal advice given by CaseMate (not facts about the user)
- Hypothetical scenarios the user asked about
- Questions the user asked
- General legal information discussed
- Anything already in the profile

### Supabase write strategy

Facts are appended to the `legal_facts[]` array. The updater checks for semantic duplicates before writing — if a fact with the same meaning already exists, it is not duplicated.

Active issues are created or updated in the `active_issues[]` array using the issue type and summary as a deduplication key.

Row Level Security ensures users can only read and write their own profiles.

---

## Alternatives considered

**User manually updates their own profile**
Rejected. Users won't do it consistently. The auto-updater removes the friction entirely. The profile improves whether or not the user thinks about it.

**Real-time extraction during streaming response**
Considered. Rejected because it adds complexity to the streaming pipeline and risks delaying the response if extraction is slow. Running it after the response is sent is simpler and has zero user-perceived latency impact.

**Vector embeddings of conversation history (RAG approach)**
Considered for future version. For MVP, structured fact extraction into a typed Pydantic model is faster to build, easier to display in the profile sidebar, and more reliable for the core use case. Embeddings and semantic search can be layered on later.

**Webhook-triggered extraction on Supabase**
Considered. Rejected in favor of FastAPI BackgroundTask because it adds a Supabase Edge Function dependency and makes the extraction logic harder to test and iterate on during the hackathon.

---

## Consequences

**Positive:**
- Profile grows automatically — no user action required
- The longer a user engages with CaseMate, the richer their profile becomes
- Memory compounds as a retention flywheel: more history → better answers → more engagement → more history
- Users can observe their profile updating in real time in the sidebar — makes the memory tangible

**Negative:**
- Background task adds backend complexity (error handling, retry logic, idempotency)
- Extraction quality depends on Claude's ability to parse implicit facts from natural conversation
- Occasional false positives (extracting something that is not actually a legal fact about the user)
- Service role key required for background profile writes — must be kept server-side only

---

## Risk mitigation

**Incorrect fact extraction:** The extraction prompt is conservative — it only extracts clear factual claims, not inferences. A human review UI in the profile page lets users remove incorrect facts.

**Background task failures:** The updater uses retry with exponential backoff. Failures are logged with the user_id and conversation_id for manual recovery. Profile updates failing silently is acceptable — the conversation response already succeeded.

**Duplicate facts:** Semantic deduplication check before every write. If the extracted fact is substantially the same as an existing one, it is discarded.

---

## Status

Accepted. Implemented in `backend/memory/updater.py` as a FastAPI BackgroundTask.
