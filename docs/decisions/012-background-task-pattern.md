# ADR 012 — FastAPI BackgroundTasks for post-response processing

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Post-response work — profile fact extraction, conversation persistence, and deadline detection — runs as FastAPI `BackgroundTasks` that are scheduled inside the `POST /api/chat` endpoint handler. These tasks execute after the HTTP response is sent to the client, so the user never waits for them.

---

## Context

The `POST /api/chat` endpoint does three things after generating the Claude response:

1. **Save the conversation** — Persist the updated conversation to Supabase
2. **Update the user's profile** — Extract new legal facts from the exchange and merge them into the profile
3. **Detect deadlines** — Scan the exchange for dates and statutes of limitations

Tasks 2 and 3 each make their own Claude API call (the extraction prompt in `backend/memory/updater.py` and the deadline detection prompt in `backend/deadlines/detector.py`). If these ran synchronously before returning the response, they would add 1–3 seconds of latency to every chat turn. Users would feel the delay and perceive the product as slow.

The key constraint is that these tasks must never crash the main request. A failure in fact extraction or deadline detection must not prevent the user from receiving their response. The tasks are fire-and-forget from the user's perspective — the memory compounds silently.

---

## The implementation

In `backend/main.py`, the `chat()` endpoint accepts `background_tasks: BackgroundTasks` as a dependency. After the Claude response is generated, three tasks are scheduled:

```python
background_tasks.add_task(save_conversation, conversation)
background_tasks.add_task(update_profile_from_conversation, user_id, conversation_messages)
background_tasks.add_task(detect_and_save_deadlines, user_id, conversation_messages, conversation.id)
```

Each background task function catches all exceptions internally and logs them with structured context. `backend/memory/updater.py` wraps its entire `update_profile_from_conversation()` function in a try/except that logs the error and returns silently. The `@retry_anthropic` decorator on the internal `_extract_facts()` function handles transient API failures with exponential backoff (up to 3 retries).

The fact extraction flow: Claude receives the conversation with an extraction prompt, returns a JSON object with `new_facts`, the updater deduplicates against existing facts (case-insensitive comparison), and appends only genuinely new facts to `profile.legal_facts` before upserting to Supabase.

---

## Alternatives considered

**Synchronous post-processing**
Rejected. Would add 1–3 seconds to every chat response. Users would notice and the product would feel sluggish. The post-processing results do not affect the current response — they improve future responses.

**Celery / Redis task queue**
Considered but rejected for MVP. Celery adds infrastructure complexity (Redis broker, worker process, task serialization). FastAPI BackgroundTasks run in the same process and are sufficient for our scale. The tasks are lightweight (one API call + one database write each). At high scale, migrating to Celery would be straightforward since the task functions are already standalone async functions.

**Webhooks / event-driven architecture**
Over-engineered for this use case. A pub/sub system for "conversation completed" events would add architectural complexity without benefit at current scale. The three post-processing tasks are tightly coupled to the chat endpoint and unlikely to be triggered from other sources.

**Client-side polling for profile updates**
Rejected. Would require the frontend to repeatedly check if the profile was updated, adding network traffic and complexity. The background task writes directly to Supabase, and the profile sidebar can refresh on the next page load or via a Supabase realtime subscription.

---

## Consequences

**Positive:**
- Zero latency impact on chat responses — users get their answer immediately
- Memory compounds silently — users do not need to do anything for their profile to grow
- Failure isolation — a crash in fact extraction does not affect the user's conversation
- Simple deployment — no additional worker processes or message brokers needed
- All three tasks share the same async event loop, minimizing resource overhead

**Negative:**
- Tasks share the main process — a very slow task could theoretically affect other requests under high load
- No built-in retry at the task level (retries are handled within each task via `@retry_anthropic`)
- No task monitoring dashboard — failures are only visible in structured logs
- If the server crashes mid-task, the work is lost (no persistent queue)
- No ordering guarantees between the three tasks

---

## Status

Accepted. FastAPI BackgroundTasks are the right tool for MVP-scale post-response processing. If CaseMate reaches a scale where background task volume affects request handling, migrating to a dedicated task queue (Celery or Arq) is a straightforward refactor since the task functions are already decoupled.
