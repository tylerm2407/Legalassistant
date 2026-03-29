# ADR 007 — Guided workflow engine with template system

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Build a template-based step-by-step workflow engine where `WorkflowTemplate` defines ordered steps and `WorkflowInstance` tracks per-user progress through a status enum (`NOT_STARTED` → `IN_PROGRESS` → `COMPLETED` / `SKIPPED`), with auto-advancement on step completion.

---

## Context

Legal processes are inherently multi-step and sequential. Filing a small claims case, responding to an eviction notice, disputing a debt collection — each involves 4–8 ordered steps that may span days or weeks. A user cannot skip ahead, and missing a step can invalidate the entire process.

Chat alone cannot guide users through these workflows. A conversation from Tuesday that said "next, file the complaint with the court" is buried by Thursday under three other questions about unrelated topics. Users need a persistent, structured view of where they are in a multi-step legal process — not just conversational advice.

The question was whether to build structured workflow tracking into CaseMate or rely on chat-based guidance with optional checklists (ADR 005's checklist generator).

---

## The implementation

The engine in `backend/workflows/engine.py` is built on three Pydantic models:

1. **`WorkflowTemplate`** — defines a reusable workflow: title, description, legal domain, estimated time, and an ordered list of `WorkflowStep` objects. Each step has a title, explanation, required documents, tips, and optional deadlines.

2. **`WorkflowInstance`** — a user's active copy of a template with progress tracking. Tracks `current_step` (0-based index), per-step status, and overall workflow status. Persisted to the `workflow_instances` table in Supabase.

3. **`WorkflowStep`** — individual step with a `StepStatus` enum: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`.

Auto-advancement logic: when a step is marked `COMPLETED`, the engine automatically sets the next step to `IN_PROGRESS` and advances `current_step`. When the final step completes, the entire workflow is marked `COMPLETED`. All mutations are persisted to Supabase with structured logging.

Templates are defined in `backend/workflows/templates/definitions.py`, covering common legal processes like small claims filing, eviction response, and debt dispute.

---

## Alternatives considered

**Chat-only guidance**
Rejected. Conversational advice about multi-step processes gets lost in message history. Users cannot reliably track progress across sessions through chat alone. The checklist generator (ADR 005) produces a one-time snapshot, not a persistent tracker.

**Third-party workflow tool (e.g., Temporal, Prefect)**
Rejected. These are designed for backend orchestration, not user-facing progress tracking. They add significant infrastructure complexity for a use case that is fundamentally a UI state machine backed by a database row.

**Static checklists without progress tracking**
Considered as a lighter alternative. Rejected because legal workflows require sequential enforcement — a user should not skip step 3 to do step 5. Static checklists have no concept of current step, auto-advancement, or completion state.

---

## Consequences

**Positive:**
- Users have a clear, persistent view of where they are in multi-step legal processes
- Auto-advancement reduces friction — completing a step automatically queues the next one
- Template system is reusable across legal domains without code changes
- Integrates with deadline tracking (ADR 006) via per-step deadline fields

**Negative:**
- Workflow templates require legal domain expertise to author correctly
- Step ordering is rigid — some legal processes have conditional branches that a linear model cannot express
- Additional Supabase table and CRUD operations add backend surface area
- Users with multiple active workflows need clear UI to avoid confusion

---

## Status

Accepted. Implemented in `backend/workflows/engine.py` with templates in `backend/workflows/templates/definitions.py` and a user-facing UI at `web/app/workflows/page.tsx`.
