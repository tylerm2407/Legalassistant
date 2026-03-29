# Referrals — Attorney Matching System

> How CaseMate connects users with relevant attorneys based on state, specialization, and case details.

---

## Overview

CaseMate is not a replacement for a lawyer — it's a bridge. When a user's situation requires professional legal help, the referral system finds attorneys who match their state, legal area, and specific issue. The system uses weighted relevance scoring to rank matches.

**Source:** `backend/referrals/matcher.py`

---

## Two Lookup Modes

### 1. Basic Search — `find_attorneys()`

```python
async def find_attorneys(
    state: str,
    legal_area: str | None = None,
    limit: int = 10,
) -> list[Attorney]:
```

Simple state-filtered search. Fetches attorneys from Supabase `attorneys` table filtered by state, ordered by `rating DESC`. If `legal_area` is provided, results are further filtered by specialization match.

### 2. Relevance-Scored Referral — `get_referral_suggestions()`

```python
async def get_referral_suggestions(
    state: str,
    legal_area: str,
    issue_summary: str,
    limit: int = 5,
) -> list[ReferralSuggestion]:
```

Finds attorneys via `find_attorneys()`, then scores each by relevance using a weighted algorithm.

---

## Scoring Algorithm

Each attorney receives a **relevance score from 50 to 100**:

| Factor | Points | Condition |
|--------|--------|-----------|
| **Base** | 50 | State match (required — all results match state) |
| **Specialization match** | +30 | Attorney's specializations include the detected `legal_area` |
| **Rating bonus** | +0 to 10 | `attorney.rating * 2` (e.g., 4.5 rating → +9 points) |
| **Free consultation** | +10 | `accepts_free_consultations == True` |

### Match reason generation

Each `ReferralSuggestion` includes a human-readable `match_reason` explaining why this attorney was recommended:

- Specialization match: *"Specializes in landlord & tenant law"*
- Free consultation: *"Offers free initial consultation"*
- High rating: *"Highly rated (4.8/5.0)"*

Results are sorted by `relevance_score` descending.

---

## Data Models

### `Attorney`

```python
class Attorney(BaseModel):
    id: str
    name: str
    state: str                        # 2-letter state code (uppercase)
    specializations: list[str]        # e.g., ["landlord_tenant", "consumer"]
    rating: float                     # 0.0 - 5.0
    cost_range: str                   # e.g., "$200-400/hr"
    phone: str | None
    email: str | None
    website: str | None
    accepts_free_consultations: bool
    bio: str | None
```

### `ReferralSuggestion`

```python
class ReferralSuggestion(BaseModel):
    attorney: Attorney
    match_reason: str        # Why this attorney was recommended
    relevance_score: int     # 50-100
```

---

## Database Schema

```sql
CREATE TABLE attorneys (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    specializations JSONB DEFAULT '[]',
    rating NUMERIC(3,2) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    cost_range TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    accepts_free_consultations BOOLEAN DEFAULT false,
    bio TEXT
);

-- Indexes
CREATE INDEX idx_attorneys_state ON attorneys(state);
CREATE INDEX idx_attorneys_state_rating ON attorneys(state, rating DESC);
CREATE INDEX idx_attorneys_specializations ON attorneys USING GIN(specializations);
```

**RLS:** The `attorneys` table has a public read policy (`USING (true)`) — any authenticated user can search attorneys. Insert/update/delete is restricted to admin access via Supabase dashboard.

---

## API Endpoints

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|------------|-------------|
| `GET` | `/api/attorneys/search` | JWT | 10/min | Search attorneys by state and legal area |

### Query Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `state` | string | Yes | 2-letter state code (e.g., `MA`) |
| `legal_area` | string | No | Legal domain (e.g., `landlord_tenant`) |
| `issue_summary` | string | No | Brief description — triggers relevance scoring |

### Response

When `issue_summary` is provided, returns `list[ReferralSuggestion]` (scored and ranked).
When omitted, returns `list[Attorney]` (sorted by rating).

---

## Frontend Integration

The `AttorneyCard` component (`web/components/AttorneyCard.tsx`) displays each referral with:

- Attorney name, rating (stars), cost range
- Specializations as tags
- "Free consultation" badge when applicable
- Match reason text (when scored)
- Contact links (phone, email, website)

The attorneys page (`web/app/attorneys/page.tsx`) provides state and legal area filters with results updating in real time.

---

## Related

- [DATABASE.md](DATABASE.md) — Full schema including attorneys table
- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — Legal area classification used for matching
- [API.md](API.md) — Complete API reference
- ADR 014 — Attorney referral system design decision
