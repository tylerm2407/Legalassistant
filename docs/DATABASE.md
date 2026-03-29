# Database Schema

CaseMate uses Supabase (PostgreSQL) with Row Level Security (RLS) on all tables. Migrations live in `supabase/migrations/`.

See `ARCHITECTURE.md` for how these tables fit into the overall system.

## Migrations

| File | Tables |
|------|--------|
| `001_user_profiles_rls.sql` | `user_profiles` |
| `002_conversations_deadlines_workflows_attorneys.sql` | `conversations`, `deadlines`, `workflow_instances`, `attorneys` |

## Tables

### user_profiles

The most important table. Stores each user's persistent legal context, injected into every Claude API call via `backend/memory/injector.py`.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `user_id` | `UUID` (PK) | — | FK to `auth.users(id)`, CASCADE delete |
| `display_name` | `TEXT` | `''` | User's first name |
| `state` | `TEXT` | `''` | Two-letter state code (e.g. "MA") |
| `housing_situation` | `TEXT` | `''` | Free-text housing description |
| `employment_type` | `TEXT` | `''` | Employment classification |
| `family_status` | `TEXT` | `''` | Family and dependent info |
| `active_issues` | `JSONB` | `'[]'` | Array of `LegalIssue` objects (see below) |
| `legal_facts` | `JSONB` | `'[]'` | Array of strings extracted from conversations |
| `documents` | `JSONB` | `'[]'` | Array of uploaded document references |
| `member_since` | `TIMESTAMPTZ` | `now()` | When the user joined |
| `conversation_count` | `INTEGER` | `0` | Total conversations held |
| `created_at` | `TIMESTAMPTZ` | `now()` | Row creation time |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**JSONB structures:**

`active_issues` stores an array of objects matching the `LegalIssue` Pydantic model in `backend/models/legal_profile.py`:

```json
[
  {
    "issue_type": "landlord_tenant",
    "summary": "Landlord has not returned $2,400 security deposit",
    "status": "open",
    "started_at": "2026-02-01T00:00:00",
    "updated_at": "2026-03-15T00:00:00",
    "notes": ["Move-out date was January 15, 2026"]
  }
]
```

`legal_facts` stores an array of plain strings:

```json
["Landlord did not perform move-in inspection", "Pre-existing water damage documented"]
```

### conversations

Stores multi-turn chat histories. Messages are stored as a JSONB array rather than individual rows.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | Conversation ID |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `messages` | `JSONB` | `'[]'` | Array of message objects (`role`, `content`, `legal_area`, `timestamp`) |
| `legal_area` | `TEXT` | `NULL` | Primary legal domain for this conversation |
| `created_at` | `TIMESTAMPTZ` | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**Indexes:** `(user_id)`, `(user_id, updated_at DESC)` for list queries.

### deadlines

Legal deadlines detected from conversations or created manually.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | — |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `title` | `TEXT` | — | Deadline description |
| `date` | `TEXT` | — | ISO date string (e.g. `2026-04-15`) |
| `legal_area` | `TEXT` | `NULL` | — |
| `source_conversation_id` | `UUID` | `NULL` | FK to `conversations(id)`, SET NULL on delete |
| `status` | `TEXT` | `'active'` | CHECK: `active`, `completed`, `dismissed`, `expired` |
| `notes` | `TEXT` | `''` | — |
| `created_at` | `TIMESTAMPTZ` | `now()` | — |

**Indexes:** `(user_id)`, `(user_id, status)`, `(user_id, date ASC)`, `(source_conversation_id)`.

### workflow_instances

Tracks user progress through guided legal workflows.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | — |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `template_id` | `TEXT` | — | Reference to workflow template definition |
| `title` | `TEXT` | — | Workflow display name |
| `domain` | `TEXT` | — | Legal domain |
| `steps` | `JSONB` | `'[]'` | Array of step objects with status |
| `current_step` | `INTEGER` | `0` | Index of the current step |
| `status` | `TEXT` | `'in_progress'` | CHECK: `not_started`, `in_progress`, `completed`, `skipped` |
| `started_at` | `TIMESTAMPTZ` | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**Indexes:** `(user_id)`, `(user_id, updated_at DESC)`, `(template_id)`.

### attorneys

Shared directory of attorney referrals. No `user_id` — this is admin-managed, not user-owned.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `TEXT` (PK) | — | Unique attorney identifier |
| `name` | `TEXT` | — | Attorney name |
| `state` | `TEXT` | — | Two-letter state code (uppercase) |
| `specializations` | `JSONB` | `'[]'` | Array of legal area strings |
| `rating` | `NUMERIC(3,2)` | `0.00` | CHECK: 0-5 |
| `cost_range` | `TEXT` | `''` | e.g. "$200-400/hr" |
| `phone` | `TEXT` | `''` | — |
| `email` | `TEXT` | `''` | — |
| `website` | `TEXT` | `''` | — |
| `accepts_free_consultations` | `BOOLEAN` | `FALSE` | — |
| `bio` | `TEXT` | `''` | — |

**Indexes:** `(state)`, `(state, rating DESC)`, GIN on `specializations` for containment queries.

## Row Level Security

All user-owned tables (`user_profiles`, `conversations`, `deadlines`, `workflow_instances`) have full CRUD RLS policies scoped to `auth.uid() = user_id`. Users can only read, insert, update, and delete their own rows.

The `attorneys` table uses public read access (`USING (true)`) with no INSERT/UPDATE/DELETE policies for application users. Attorney records are managed by administrators directly in Supabase.

## Triggers

An `update_updated_at_column()` trigger function (created in migration 001) automatically sets `updated_at = now()` before any UPDATE on `user_profiles`, `conversations`, and `workflow_instances`.
