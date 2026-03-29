# Deadlines — Detection & Tracking

> How CaseMate automatically detects legal deadlines from conversations and tracks them for users.

---

## Overview

Legal deadlines are critical — missing a statute of limitations or a filing window can forfeit a user's rights entirely. CaseMate handles deadlines in two ways:

1. **Auto-detection:** After every chat response, a background task scans the conversation for mentioned deadlines
2. **Manual creation:** Users can create deadlines directly via the API or UI

---

## Auto-Detection Flow

**Source:** `backend/deadlines/detector.py` → `detect_and_save_deadlines()`

```
User sends message
        ↓
  Claude responds
        ↓
  Background task fires (never blocks response)
        ↓
  Full conversation → Claude with DEADLINE_DETECTION_PROMPT
        ↓
  Claude returns JSON: [{title, date, legal_area, notes}]
        ↓
  Regex JSON parse (handles markdown fences)
        ↓
  Relative dates → absolute dates (YYYY-MM-DD)
        ↓
  create_deadline() for each detected deadline
```

### Detection prompt

Claude is instructed to extract any deadlines, filing windows, statute of limitations periods, or time-sensitive requirements mentioned in the conversation. It returns a JSON array:

```json
[
  {
    "title": "File small claims court complaint",
    "date": "2026-04-15",
    "legal_area": "small_claims",
    "notes": "Must file within 30 days of incident per M.G.L. c.218 §21"
  }
]
```

### Safety guarantees

- Runs as a `FastAPI BackgroundTask` — never blocks the chat response
- Entire function wrapped in `try/except` — errors are logged but never crash the main request
- Relative dates (e.g., "within 30 days") are converted to absolute dates based on the current date
- Duplicate detection is not currently implemented — the same deadline may be created multiple times if mentioned in multiple conversations

---

## Manual Creation

Users can create deadlines directly via `POST /api/deadlines`:

```json
{
  "title": "Respond to eviction notice",
  "date": "2026-04-01",
  "legal_area": "landlord_tenant",
  "notes": "14-day notice received March 18"
}
```

---

## Deadline Model

**Source:** `backend/deadlines/tracker.py`

```python
class Deadline(BaseModel):
    id: str                          # UUID
    user_id: str                     # Owner
    title: str                       # Description of the deadline
    date: str                        # ISO date string (YYYY-MM-DD)
    legal_area: str                  # Legal domain (e.g., "landlord_tenant")
    source_conversation_id: str | None  # FK to conversation that triggered detection
    status: DeadlineStatus           # Current state
    notes: str | None                # Additional context
    created_at: str                  # ISO timestamp
```

### `DeadlineStatus` Enum

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Deadline is upcoming and requires attention |
| `COMPLETED` | User has completed the required action |
| `DISMISSED` | User dismissed the deadline (no longer relevant) |
| `EXPIRED` | Date has passed without action |

---

## CRUD Operations

**Source:** `backend/deadlines/tracker.py`

### `create_deadline(user_id, title, date, legal_area, conversation_id, notes)`

Inserts a new deadline into Supabase `deadlines` table. Logs failure but raises `RuntimeError` on insert failure.

### `list_deadlines(user_id, status=None)`

Fetches all deadlines for a user, optionally filtered by status. Returns ordered by `date ASC` (earliest first).

### `update_deadline(user_id, deadline_id, status, notes)`

Updates a specific deadline. Verifies ownership via `user_id` match. Supports partial updates — only non-`None` fields are changed.

### `delete_deadline(user_id, deadline_id)`

Deletes a deadline by `id` + `user_id` (ownership check). Returns `bool` indicating success.

---

## API Endpoints

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|------------|-------------|
| `POST` | `/api/deadlines` | JWT | 10/min | Create a deadline manually |
| `GET` | `/api/deadlines` | JWT | 10/min | List all deadlines (optional `?status=active`) |
| `PATCH` | `/api/deadlines/{id}` | JWT | 10/min | Update status or notes |
| `DELETE` | `/api/deadlines/{id}` | JWT | 10/min | Delete a deadline |

---

## Database Schema

```sql
CREATE TABLE deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    legal_area TEXT,
    source_conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active','completed','dismissed','expired')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_deadlines_user ON deadlines(user_id);
CREATE INDEX idx_deadlines_user_status ON deadlines(user_id, status);
CREATE INDEX idx_deadlines_user_date ON deadlines(user_id, date ASC);
CREATE INDEX idx_deadlines_conversation ON deadlines(source_conversation_id);
```

RLS ensures users can only access their own deadlines (`auth.uid() = user_id`).

---

## Conversation Linking

When a deadline is auto-detected, the `source_conversation_id` links it back to the conversation that triggered detection. This allows the UI to show "Detected from conversation about [topic]" and lets users navigate back to the original context.

If the source conversation is deleted, the deadline persists but `source_conversation_id` is set to `NULL` via `ON DELETE SET NULL`.

---

## Related

- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — Background task pattern shared with profile updater
- [DATABASE.md](DATABASE.md) — Full schema including deadlines table
- [API.md](API.md) — Complete API reference
- [WORKFLOWS.md](WORKFLOWS.md) — Guided workflows that may also create deadlines
