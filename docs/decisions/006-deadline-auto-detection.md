# ADR 006 — Deadline auto-detection from conversations

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Automatically extract legal deadlines from every conversation using Claude, persist them to a dedicated `deadlines` table in Supabase, and surface them in a user-facing deadline tracking dashboard.

---

## Context

Legal deadlines are the highest-stakes element in any legal situation. Missing a statute of limitations, a filing date, or a response window has irreversible consequences — a valid claim becomes worthless, a defense is waived, or a default judgment is entered. Users who come to CaseMate are not legal professionals; they do not know which dates matter or how to track them.

ADR 001 established persistent memory as the core differentiator. That memory captures passive facts — the user's state, their housing situation, specific legal details mentioned in conversation. But passive facts alone are not enough when time-sensitive obligations exist. A user who mentioned a 30-day eviction response window in conversation 2 needs CaseMate to remember that deadline in conversation 5 — and warn them before it passes.

The question was whether to extend the memory pattern to include active, time-sensitive tracking or leave deadline management to the user.

---

## The implementation

After each conversation turn, `backend/deadlines/detector.py` runs as a background task (same pattern as the profile auto-updater from ADR 003). It sends the conversation to Claude with a structured extraction prompt that returns JSON containing deadline title, date, legal area, and contextual notes.

The detector converts relative dates ("within 30 days") to absolute dates based on conversation context. Only specific, actionable deadlines with real dates are extracted — vague time references are filtered out. Each detected deadline is saved via `backend/deadlines/tracker.py` to the `deadlines` table, linked to the user and optionally to the source conversation.

The detection function is wrapped in `@retry_anthropic` for resilience and catches all exceptions to ensure it never crashes the parent request. Structured logging with `user_id` context is used throughout.

---

## Alternatives considered

**Manual-only deadline entry**
Rejected. Users do not know which dates are legally significant. A renter who mentions "my landlord gave me a letter last Tuesday" does not realize that a clock is ticking. Manual entry defeats the purpose of an assistant that knows more than the user about what matters.

**Calendar integration (Google Calendar, Apple Calendar)**
Considered for a future phase but rejected for MVP. Calendar sync adds OAuth complexity, platform-specific code, and a dependency on third-party APIs. The built-in dashboard is simpler to build, fully controlled, and sufficient for the core use case.

**No deadline tracking**
Rejected. Deadlines are the single highest-consequence element in legal situations. A legal assistant that lets users miss statutes of limitations is worse than no assistant at all — it creates false confidence.

---

## Consequences

**Positive:**
- Extends the memory pattern from passive facts to active time-sensitive alerts
- Users are protected from missing critical legal deadlines they may not even know exist
- Background task pattern is consistent with the profile auto-updater (ADR 003)
- Deadline data enriches future conversations — CaseMate can proactively reference upcoming dates

**Negative:**
- Additional Claude API call per conversation turn increases cost
- Relative-to-absolute date conversion depends on conversation context and may be imprecise
- Deadline accuracy is only as good as the information the user provides — no external verification

---

## Status

Accepted. Implemented in `backend/deadlines/detector.py` and `backend/deadlines/tracker.py` with a user-facing dashboard at `web/app/deadlines/page.tsx`.
