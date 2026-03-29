# Data Models Reference

All data flows through strictly typed models. Python models (Pydantic v2) live in `backend/models/`.
TypeScript interfaces live in `shared/types/` and are consumed by both `web/` and `mobile/`.

## Python Models (Backend)

### LegalProfile (`backend/models/legal_profile.py`)

The single most important model. Injected into every Claude API call via `backend/memory/injector.py`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `user_id` | `str` | required | Supabase auth user ID (primary key) |
| `display_name` | `str` | required | First name for personalized responses |
| `state` | `str` | required | Two-letter state code (determines applicable laws) |
| `housing_situation` | `str` | required | Renter/owner/etc with relevant details |
| `employment_type` | `str` | required | Employment classification affecting rights |
| `family_status` | `str` | required | Family context for family law questions |
| `active_issues` | `list[LegalIssue]` | `[]` | Ongoing legal disputes tracked over time |
| `legal_facts` | `list[str]` | `[]` | Facts extracted from conversations by auto-updater |
| `documents` | `list[str]` | `[]` | References to uploaded docs in Supabase Storage |
| `member_since` | `datetime` | `utcnow()` | Account creation timestamp |
| `conversation_count` | `int` | `0` | Total conversations (shows usage depth) |

Methods: `to_context_string()` serializes the profile to JSON for prompt injection, including active issues and known facts only when present.

### LegalIssue (`backend/models/legal_profile.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `issue_type` | `str` | required | Legal domain (landlord_tenant, employment, etc.) |
| `summary` | `str` | required | One-sentence description of the dispute |
| `status` | `IssueStatus` | `OPEN` | Current state of the issue |
| `started_at` | `datetime` | `utcnow()` | When the issue was first mentioned |
| `updated_at` | `datetime` | `utcnow()` | When last updated |
| `notes` | `list[str]` | `[]` | Context extracted from conversations over time |

### IssueStatus (`backend/models/legal_profile.py`)

`StrEnum` with values: `open`, `resolved`, `watching`, `escalated`.

### Message (`backend/models/conversation.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `role` | `Literal["user", "assistant", "error"]` | required | Message sender role |
| `content` | `str` | required | Full text content |
| `timestamp` | `datetime` | `utcnow()` | Creation time |
| `legal_area` | `str \| None` | `None` | Optional legal domain classification |

### Conversation (`backend/models/conversation.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | UUID string |
| `user_id` | `str` | required | Owning user's Supabase auth ID |
| `messages` | `list[Message]` | `[]` | Ordered message list |
| `legal_area` | `str \| None` | `None` | Primary legal domain for the conversation |
| `created_at` | `datetime` | `utcnow()` | Conversation start time |
| `updated_at` | `datetime` | `utcnow()` | Last message time |

Methods: `add_message(role, content, legal_area)` appends and updates timestamp. `to_anthropic_messages()` converts to Anthropic API format (filters out error messages).

### DemandLetter (`backend/models/action_output.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | required | Full letter text, ready to send |
| `citations` | `list[str]` | `[]` | Statute citations referenced |
| `recipient` | `str \| None` | `None` | Letter recipient name |
| `subject` | `str` | required | Subject line or topic |

### RightsSummary (`backend/models/action_output.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | required | Full narrative explanation |
| `key_rights` | `list[str]` | `[]` | Bulleted list of important rights |
| `applicable_laws` | `list[str]` | `[]` | Statute citations |

### Checklist (`backend/models/action_output.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `list[str]` | `[]` | Action items |
| `deadlines` | `list[str \| None]` | `[]` | Parallel deadline strings (index-aligned with items) |
| `priority_order` | `list[int]` | `[]` | Indices into items sorted by urgency |

## TypeScript Interfaces (Shared)

All live in `shared/types/`. The mobile app re-exports them via `mobile/lib/types.ts`.

### `shared/types/legal-profile.ts`
`LegalProfile` and `LegalIssue` -- mirrors the Python models. `IssueStatus` is a union type: `"open" | "resolved" | "watching" | "escalated"`. Dates are `string` (ISO format) instead of `datetime`.

### `shared/types/conversation.ts`
`Message`, `ChatResponse` (includes `suggested_actions: string[]`), `ConversationSummary` (list view), `ConversationDetail` (full thread with inline message type).

### `shared/types/actions.ts`
`DemandLetter` (fields: `letter_text`, `legal_citations`), `RightsSummary` (`summary_text`, `key_rights`), `Checklist` (`items`, `deadlines`). Field names differ slightly from Python models.

### `shared/types/deadlines.ts`
`Deadline` (id, title, date, legal_area, status, notes), `DeadlineCreateRequest`, `DeadlineUpdateRequest`.

### `shared/types/rights.ts`
`RightsGuide` (domain, title, your_rights, action_steps, common_mistakes, when_to_get_a_lawyer), `RightsDomain` (domain, label, guide_count).

### `shared/types/workflows.ts`
`WorkflowStep` (title, required_documents, tips, status), `WorkflowTemplate`, `WorkflowInstance`, `WorkflowSummary`.

### `shared/types/referrals.ts`
`Attorney` (name, state, specializations, rating, cost_range, accepts_free_consultations), `ReferralSuggestion` (attorney, match_reason, relevance_score).

## Python/TypeScript Field Name Differences

| Concept | Python (Pydantic) | TypeScript |
|---------|-------------------|------------|
| Demand letter text | `text` | `letter_text` |
| Demand letter citations | `citations` | `legal_citations` |
| Rights summary text | `text` | `summary_text` |
| Checklist priority | `priority_order` | (not present) |
