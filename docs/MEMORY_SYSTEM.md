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

### Full `build_system_prompt()` Walkthrough

Here is an annotated trace of what happens when Sarah Chen asks "My landlord is saying I owe $800 for the bathroom tiles":

```
Step 1: classify_legal_area("My landlord is saying I owe $800 for the bathroom tiles")
  → Matches keywords: "landlord" (1x), "owe" (1x)
  → Returns: "landlord_tenant"

Step 2: Assemble Layer 1 (Base Instructions)
  → CASEMATE_BASE_INSTRUCTIONS constant (~350 tokens)
  → Includes: "You are CaseMate — a personalized legal assistant..."
  → Includes: prompt injection guard, response rules, disclaimer guidance

Step 3: Assemble Layer 2 (Personal Context)
  → Profile JSON block:
    ```json
    {"display_name": "Sarah", "state": "MA", "housing_situation": "Renter, month-to-month",
     "employment_type": "Full-time W2", "family_status": "Single, no dependents"}
    ```
  → Active issues:
    "Issue: landlord_tenant — Landlord claiming $800 for bathroom tile damage (open)
     Notes: Move-out date was January 15, 2026"
  → Legal facts:
    "- Landlord did not perform move-in inspection
     - Pre-existing water damage documented in move-in photos
     - Gave written 30-day notice on February 28, 2026
     - ..."

Step 4: Assemble Layer 3 (Applicable Law)
  → STATE_LAWS["MA"]["landlord_tenant"]
    → "Massachusetts General Laws Chapter 186, Section 15B governs..."
  → STATE_LAWS["federal_defaults"]["landlord_tenant"]
    → Federal housing protections

Step 5: Concatenate all layers → final system prompt string
```

### Annotated Output Structure

The final system prompt follows this structure:

```
[CASEMATE_BASE_INSTRUCTIONS]
  - Who CaseMate is
  - Response philosophy (be specific, cite statutes, calculate damages)
  - Disclaimer guidance
  - Prompt injection guard

[USER'S LEGAL PROFILE]
  - DATA ONLY marker (security)
  - Profile fields as JSON
  - Active issues with full detail
  - Known legal facts as bullet list

[STATE-SPECIFIC LEGAL CONTEXT]
  - State: {state_code} — {legal_area}
  - Full statute text with citations
  - Federal defaults for the same domain

[DETECTED LEGAL AREA]
  - "The user's question is about: {legal_area}"
```

## Token Budget

The system prompt grows with the user's profile. Approximate sizing:
- Base instructions: ~350 tokens (fixed)
- Profile JSON block: ~100-200 tokens
- Active issues: ~50-150 tokens per issue
- Legal facts: ~20 tokens per fact
- State law context: ~100-400 tokens per domain

Claude API calls use `claude-sonnet-4-20250514` with `max_tokens=4096` for chat and `max_tokens=1024` for fact extraction. There is no explicit token ceiling on the system prompt; profiles with many facts and issues will consume more of the context window.

### Token Budget Management

`backend/utils/token_budget.py` provides token budget awareness. As a user's profile grows over months of use, the system prompt can become large. The budget manager:

- Estimates token counts for each prompt section
- Ensures the total system prompt + conversation history fits within the model's context window
- If the budget is tight, older conversation messages may be trimmed (the profile is never trimmed — it is the product)

## Background Fact Extraction

`update_profile_from_conversation()` in `backend/memory/updater.py` runs as a FastAPI `BackgroundTasks` task after every chat response. It never blocks the user's response stream.

**Extraction prompt** (`EXTRACTION_PROMPT`): Instructs Claude to return `{"new_facts": [...]}` JSON. Rules require facts to be specific and legally relevant (dates, amounts, events, relationships, document mentions). Vague or speculative facts are excluded. General legal advice given by CaseMate is excluded.

**Extraction call**: `_extract_facts()` sends the full conversation to `claude-sonnet-4-20250514` with `max_tokens=1024`. The response is parsed as JSON. Invalid formats or parse failures log a warning and return an empty list -- they never crash.

**Merge strategy**: Append-only. New facts are compared against existing facts using case-insensitive string matching (`lower().strip()`). Only facts not already present are appended to `profile.legal_facts`. The updater never removes or modifies existing facts. After merging, `update_profile()` upserts the full profile back to Supabase.

**Error handling**: The entire `update_profile_from_conversation()` function is wrapped in a try/except that logs and swallows all exceptions. A failed extraction must never crash the main request flow.

### Append-Only Fact Strategy

The append-only design is intentional (see ADR 003):

1. **Legal facts don't expire** — A move-in inspection that didn't happen 6 months ago is still relevant today
2. **Contradictions are valuable** — If a user later says "actually, the inspection did happen," both facts remain. The newer fact takes precedence in Claude's reasoning without losing the original context
3. **Deletion is dangerous** — Removing a fact could cause CaseMate to re-ask questions the user already answered, breaking the "it remembers everything" experience
4. **Deduplication is case-insensitive** — "Landlord did not inspect" and "landlord did not inspect" are treated as the same fact

### End-to-End Trace: Fact Extraction

```
User: "I just found out my landlord never put my deposit in a separate account"

1. Claude responds with legal guidance about M.G.L. c.186 §15B
2. Response is streamed to user immediately

3. Background task fires:
   → Sends full conversation to Claude with EXTRACTION_PROMPT
   → Claude returns: {"new_facts": ["Landlord did not hold security deposit in separate account"]}

4. Merge:
   → Current profile.legal_facts: ["Landlord did not perform move-in inspection", ...]
   → New fact "Landlord did not hold security deposit in separate account" is NOT in existing facts
   → Append to list

5. Upsert:
   → update_profile() writes full profile back to Supabase
   → Next conversation will include this fact in the system prompt
```

## Conversation Persistence

`backend/memory/conversation_store.py` provides CRUD for conversation threads stored in the Supabase `conversations` table. Each conversation has a UUID `id`, `user_id`, ordered `messages` list (stored as JSON array), optional `legal_area` classification, and timestamps.

### Operations

#### `create_conversation(user_id: str) -> Conversation`

Inserts a new conversation with an empty messages array. Returns the created `Conversation` object with generated UUID.

#### `get_conversation(conversation_id: str, user_id: str) -> Conversation | None`

Fetches a single conversation by ID. Verifies ownership by including `user_id` in the query filter. Parses the JSONB `messages` field into a list of `Message` objects.

#### `save_conversation(conversation_id: str, user_id: str, messages: list[Message], legal_area: str) -> None`

Updates an existing conversation's messages and legal area classification. Also updates the `updated_at` timestamp (handled by the database trigger).

#### `list_conversations(user_id: str) -> list[dict]`

Returns up to 50 conversation summaries ordered by `updated_at DESC`. Each summary includes:
- `id` — Conversation UUID
- `legal_area` — Domain classification
- `updated_at` — Last activity timestamp
- `preview` — First user message content (truncated)
- `message_count` — Total messages in the conversation

This powers the conversation history sidebar in the chat UI.

#### `delete_conversation(conversation_id: str, user_id: str) -> bool`

Deletes a conversation by ID with ownership verification. Returns `True` if the conversation was found and deleted, `False` otherwise.

### Ownership Verification

All operations verify user ownership via `user_id` equality checks on queries. Combined with Supabase RLS policies, this provides defense-in-depth — even if the application code has a bug, the database rejects cross-user access.

## How Memory Compounds Over Time

The power of the memory system is that it compounds. Here's how a user's experience improves over weeks:

| Conversation | What CaseMate Knows | Quality of Response |
|-------------|---------------------|---------------------|
| 1 (onboarding) | State, housing, employment | Generic state-specific guidance |
| 3 | + Landlord dispute details | Cites specific deposit laws, references their lease |
| 7 | + Missing inspection, water damage | Calculates 3x damages, references their specific evidence |
| 12 | + Timeline, correspondence, photos | Drafts demand letter citing all their facts and deadlines |

This is why a user in month 3 gets dramatically better answers than a user on day 1 — and why they pay $20/month for it.

---

## Related

- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — State law database that feeds Layer 3
- [LEGAL_DOMAINS.md](LEGAL_DOMAINS.md) — How legal area classification works
- [DATABASE.md](DATABASE.md) — Supabase schema for profiles and conversations
- [TESTING.md](TESTING.md) — Memory injector tests (priority 1)
- [MODELS.md](MODELS.md) — LegalProfile, LegalIssue, Message models
- ADR 001 — Memory as differentiator
- ADR 003 — Profile auto-update strategy
