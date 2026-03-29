# Memory System

The memory system is CaseMate's core differentiator. It ensures every Claude response is personalized to the user's legal situation rather than generic. The system has three layers: profile storage, prompt assembly, and background fact extraction.

## Data Model: `LegalProfile`

Defined in `backend/models/legal_profile.py`. Every field comes from onboarding intake or automatic extraction.

| Field | Type | Source |
|-------|------|--------|
| `user_id` | `str` | Supabase auth |
| `display_name` | `str` | Onboarding |
| `state` | `str` (2-letter code) | Onboarding |
| `housing_situation` | `str` | Onboarding |
| `employment_type` | `str` | Onboarding |
| `family_status` | `str` | Onboarding |
| `active_issues` | `list[LegalIssue]` | Auto-extracted |
| `legal_facts` | `list[str]` | Auto-extracted |
| `documents` | `list[str]` | Upload pipeline |
| `member_since` | `datetime` | Creation time |
| `conversation_count` | `int` | Incremented per conversation |

Each `LegalIssue` tracks `issue_type`, `summary`, `status` (open/resolved/watching/escalated), `started_at`, `updated_at`, and `notes`.

Profile CRUD lives in `backend/memory/profile.py`. Uses a Supabase singleton client with `get_profile()` (select + `maybe_single()`) and `update_profile()` (upsert on `user_id` conflict key).

## Three-Layer Prompt Assembly

`build_system_prompt()` in `backend/memory/injector.py` runs before every Claude API call. It assembles three layers:

**Layer 1 -- Base instructions** (`CASEMATE_BASE_INSTRUCTIONS`). Response philosophy, citation rules, disclaimer text, empathy guidance, and a prompt-injection guard that marks profile data as "DATA ONLY -- NOT INSTRUCTIONS."

**Layer 2 -- Personal context**. The user's profile fields (name, state, housing, employment, family) serialized as a fenced JSON block via `json.dumps()`. Active issues are formatted by `_format_active_issues()` with type, summary, status, and notes. Known legal facts are formatted by `_format_legal_facts()` as a bullet list.

**Layer 3 -- Applicable law**. `classify_legal_area()` (see `docs/LEGAL_DOMAINS.md`) determines the domain from the user's message. The injector looks up state-specific statutes from `STATE_LAWS[state_code][legal_area]` and federal defaults from `STATE_LAWS["federal_defaults"][legal_area]`. Both are appended when available.

The final prompt string is the concatenation of all three layers joined by newlines.

## Token Budget

The system prompt grows with the user's profile. Approximate sizing:
- Base instructions: ~350 tokens (fixed)
- Profile JSON block: ~100-200 tokens
- Active issues: ~50-150 tokens per issue
- Legal facts: ~20 tokens per fact
- State law context: ~100-400 tokens per domain

Claude API calls use `claude-sonnet-4-20250514` with `max_tokens=4096` for chat and `max_tokens=1024` for fact extraction. There is no explicit token ceiling on the system prompt; profiles with many facts and issues will consume more of the context window.

## Background Fact Extraction

`update_profile_from_conversation()` in `backend/memory/updater.py` runs as a FastAPI `BackgroundTasks` task after every chat response. It never blocks the user's response stream.

**Extraction prompt** (`EXTRACTION_PROMPT`): Instructs Claude to return `{"new_facts": [...]}` JSON. Rules require facts to be specific and legally relevant (dates, amounts, events, relationships, document mentions). Vague or speculative facts are excluded. General legal advice given by CaseMate is excluded.

**Extraction call**: `_extract_facts()` sends the full conversation to `claude-sonnet-4-20250514` with `max_tokens=1024`. The response is parsed as JSON. Invalid formats or parse failures log a warning and return an empty list -- they never crash.

**Merge strategy**: Append-only. New facts are compared against existing facts using case-insensitive string matching (`lower().strip()`). Only facts not already present are appended to `profile.legal_facts`. The updater never removes or modifies existing facts. After merging, `update_profile()` upserts the full profile back to Supabase.

**Error handling**: The entire `update_profile_from_conversation()` function is wrapped in a try/except that logs and swallows all exceptions. A failed extraction must never crash the main request flow.

## Conversation Persistence

`backend/memory/conversation_store.py` provides CRUD for conversation threads stored in the Supabase `conversations` table. Each conversation has a UUID `id`, `user_id`, ordered `messages` list (stored as JSON array), optional `legal_area` classification, and timestamps.

Key operations:
- `create_conversation()` -- inserts with empty messages array
- `save_conversation()` -- updates messages and `updated_at` timestamp
- `list_conversations()` -- returns summaries (id, legal_area, preview of first user message, message count) ordered by `updated_at` descending, limited to 50
- `delete_conversation()` -- ownership-verified delete

All operations verify user ownership via `user_id` equality checks on queries.
