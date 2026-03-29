# CaseMate Data Model Reference

> Complete reference for every data model in CaseMate. Python models (Pydantic v2) define the
> backend contract. Supabase tables define persistent storage. TypeScript interfaces define the
> frontend contract. This document is the single source of truth for all data structures.

---

## Table of Contents

1. [Overview](#overview)
2. [Python Models — Core Profile](#python-models--core-profile)
3. [Python Models — Conversations](#python-models--conversations)
4. [Python Models — API Requests](#python-models--api-requests)
5. [Python Models — Action Outputs](#python-models--action-outputs)
6. [Python Models — Deadlines](#python-models--deadlines)
7. [Python Models — Workflows](#python-models--workflows)
8. [Python Models — Referrals](#python-models--referrals)
9. [Python Models — Payments](#python-models--payments)
10. [Python Models — Export](#python-models--export)
11. [Supabase Database Schema](#supabase-database-schema)
12. [Relationships Diagram](#relationships-diagram)
13. [Row-Level Security Policies](#row-level-security-policies)
14. [Indexes](#indexes)
15. [TypeScript Interfaces](#typescript-interfaces)
16. [Python/TypeScript Field Name Mapping](#pythontypescript-field-name-mapping)
17. [Example Data — Sarah Chen](#example-data--sarah-chen)

---

## Overview

CaseMate's data layer has three tiers:

| Tier | Technology | Purpose |
|------|-----------|---------|
| **Python models** | Pydantic v2 `BaseModel` | Request validation, response serialization, prompt injection |
| **Database tables** | Supabase (PostgreSQL 15) | Persistent storage with RLS enforcement |
| **TypeScript interfaces** | `shared/types/` | Frontend type safety across web and mobile |

**The most important model is `LegalProfile`.** It is injected into every Claude API call via
`backend/memory/injector.py`. Every other model exists to feed data into or out of that profile.

All Python models live in `backend/models/`. All use strict type annotations — no `Any` types
anywhere. All enums are `StrEnum` for JSON serialization compatibility.

---

## Python Models — Core Profile

Source: `backend/models/legal_profile.py`

### IssueStatus

A `StrEnum` representing the lifecycle state of a legal issue.

| Value | Meaning |
|-------|---------|
| `"open"` | Active dispute, CaseMate is tracking and advising |
| `"resolved"` | Issue concluded, kept for historical context |
| `"watching"` | Not yet a dispute, but user wants to monitor it |
| `"escalated"` | Referred to an attorney or requires professional help |

```python
class IssueStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    WATCHING = "watching"
    ESCALATED = "escalated"
```

### LegalIssue

An ongoing legal dispute tracked within a user's profile. Issues are created automatically
when the profile auto-updater detects a new dispute in conversation, or manually by the user.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `issue_type` | `str` | — | Yes | Legal domain identifier (e.g., `"landlord_tenant"`, `"employment_rights"`, `"consumer"`) |
| `summary` | `str` | — | Yes | Free-text description of the dispute |
| `status` | `IssueStatus` | `OPEN` | No | Current lifecycle state |
| `started_at` | `datetime` | `utcnow()` | No | When the issue was first mentioned |
| `updated_at` | `datetime` | `utcnow()` | No | Last modification timestamp |
| `notes` | `list[str]` | `[]` | No | Specific facts extracted from conversations about this issue |

**Example JSON:**

```json
{
  "issue_type": "landlord_tenant",
  "summary": "Landlord claiming $800 for bathroom tile damage from security deposit",
  "status": "open",
  "started_at": "2026-02-15T14:30:00Z",
  "updated_at": "2026-03-20T09:15:00Z",
  "notes": [
    "Landlord did not perform move-in inspection",
    "Pre-existing water damage documented in move-in photos",
    "Landlord sent informal email demand, no itemized statement",
    "Tenant gave written 30-day notice on February 28, 2026"
  ]
}
```

### LegalProfile

**THE most important model in the entire codebase.** This is what makes CaseMate different
from every other legal chatbot. Every field is injected into Claude's system prompt via
`backend/memory/injector.py`. The profile compounds over time as the auto-updater
(`backend/memory/updater.py`) extracts new facts from each conversation.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `user_id` | `str` | — | Yes | Supabase auth user ID, primary key across the system |
| `display_name` | `str` | — | Yes | User's name from onboarding, used in personalized responses |
| `state` | `str` | — | Yes | Two-letter state code (e.g., `"MA"`). Determines which state laws apply to every answer |
| `housing_situation` | `str` | — | Yes | Free text describing housing (e.g., `"Renter, month-to-month, no signed lease"`) |
| `employment_type` | `str` | — | Yes | Free text describing employment (e.g., `"Full-time W2, marketing coordinator"`) |
| `family_status` | `str` | — | Yes | Free text describing family context (e.g., `"Single, no dependents"`) |
| `active_issues` | `list[LegalIssue]` | `[]` | No | Ongoing legal disputes being tracked |
| `legal_facts` | `list[str]` | `[]` | No | Specific facts extracted from conversations over time. This list only grows — facts are never removed |
| `documents` | `list[str]` | `[]` | No | Supabase Storage references to uploaded legal documents |
| `member_since` | `datetime` | `utcnow()` | No | Account creation timestamp |
| `conversation_count` | `int` | `0` | No | Total conversations held, shows depth of relationship |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `to_context_string()` | `str` | Serializes the full profile to JSON for injection into Claude's system prompt. Includes active issues and legal facts only when present. |
| `format_active_issues()` | `str` | Formats active issues as a readable list for prompt injection |
| `format_legal_facts()` | `str` | Formats legal facts as a bulleted list for prompt injection |

**Example JSON:**

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "display_name": "Sarah Chen",
  "state": "MA",
  "housing_situation": "Renter, month-to-month, no signed lease",
  "employment_type": "Full-time W2, marketing coordinator",
  "family_status": "Single, no dependents",
  "active_issues": [
    {
      "issue_type": "landlord_tenant",
      "summary": "Landlord claiming $800 for bathroom tile damage",
      "status": "open",
      "started_at": "2026-02-15T14:30:00Z",
      "updated_at": "2026-03-20T09:15:00Z",
      "notes": [
        "Landlord did not perform move-in inspection",
        "Pre-existing water damage documented in move-in photos"
      ]
    }
  ],
  "legal_facts": [
    "Landlord did not perform move-in inspection",
    "Pre-existing water damage documented in move-in photos taken at move-in",
    "Gave written 30-day notice on February 28, 2026",
    "Monthly rent is $1,850",
    "Security deposit was $1,850 (one month's rent)",
    "Landlord has not provided itemized list of damages within 30 days"
  ],
  "documents": [
    "documents/a1b2c3d4/move-in-photos.pdf",
    "documents/a1b2c3d4/notice-to-vacate.pdf"
  ],
  "member_since": "2026-01-15T10:00:00Z",
  "conversation_count": 12
}
```

**Why this model matters:**

The `build_system_prompt()` function in `backend/memory/injector.py` reads this model and
constructs a system prompt that makes Claude respond as if it has been advising this specific
person for months. Without this model, CaseMate is just another generic chatbot. With it,
CaseMate knows that Sarah is a Massachusetts renter whose landlord skipped the move-in
inspection — and can immediately cite M.G.L. c.186 §15B without Sarah repeating herself.

---

## Python Models — Conversations

Source: `backend/models/conversation.py`

### Message

A single message within a conversation thread.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `role` | `Literal["user", "assistant", "error"]` | — | Yes | Who sent the message. `"error"` is for system error messages displayed in chat |
| `content` | `str` | — | Yes | Full text content of the message |
| `timestamp` | `datetime` | `utcnow()` | No | When the message was created |
| `legal_area` | `str \| None` | `None` | No | Classified legal domain (e.g., `"landlord_tenant"`, `"employment"`) |

**Example JSON:**

```json
{
  "role": "user",
  "content": "My landlord is saying I owe $800 for the bathroom tiles. Can he do that?",
  "timestamp": "2026-03-20T09:15:00Z",
  "legal_area": "landlord_tenant"
}
```

```json
{
  "role": "assistant",
  "content": "Based on your situation in Massachusetts, your landlord has a significant problem here. Under M.G.L. c.186 §15B, a landlord who fails to conduct a move-in inspection cannot deduct for pre-existing damage...",
  "timestamp": "2026-03-20T09:15:12Z",
  "legal_area": "landlord_tenant"
}
```

### Conversation

A full conversation thread between a user and CaseMate.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | UUID string, primary key |
| `user_id` | `str` | — | Yes | FK to user_profiles, the owning user's Supabase auth ID |
| `messages` | `list[Message]` | `[]` | No | Ordered list of messages in the thread |
| `legal_area` | `str \| None` | `None` | No | Dominant legal domain for the conversation |
| `created_at` | `datetime` | `utcnow()` | No | When the conversation started |
| `updated_at` | `datetime` | `utcnow()` | No | When the last message was added |

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_message()` | `(role: str, content: str, legal_area: str \| None)` | Appends a new Message and updates `updated_at` |
| `to_anthropic_messages()` | `() -> list[dict]` | Converts messages to Anthropic API format, filtering out `"error"` role messages |

**Example JSON:**

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "messages": [
    {
      "role": "user",
      "content": "My landlord is saying I owe $800 for the bathroom tiles.",
      "timestamp": "2026-03-20T09:15:00Z",
      "legal_area": "landlord_tenant"
    },
    {
      "role": "assistant",
      "content": "Based on your situation in Massachusetts...",
      "timestamp": "2026-03-20T09:15:12Z",
      "legal_area": "landlord_tenant"
    }
  ],
  "legal_area": "landlord_tenant",
  "created_at": "2026-03-20T09:15:00Z",
  "updated_at": "2026-03-20T09:15:12Z"
}
```

---

## Python Models — API Requests

Source: `backend/models/conversation.py` and `backend/models/legal_profile.py`

### ChatRequest

Inbound request to the `/api/chat` endpoint.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `message` | `str` | — | Yes | Max 10,000 chars | The user's question or message |
| `conversation_id` | `str \| None` | `None` | No | — | UUID of existing conversation to continue, or `None` to start new |

**Example JSON:**

```json
{
  "message": "My landlord is saying I owe $800 for the bathroom tiles. Can he do that?",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### ProfileRequest

Inbound request to create or update a user's legal profile (from onboarding or profile editor).

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `display_name` | `str` | — | Yes | Max 100 chars | User's display name |
| `state` | `str` | — | Yes | Max 2 chars | Two-letter state code |
| `housing_situation` | `str` | — | Yes | Max 500 chars | Housing description |
| `employment_type` | `str` | — | Yes | Max 200 chars | Employment description |
| `family_status` | `str` | — | Yes | Max 500 chars | Family context description |

**Example JSON:**

```json
{
  "display_name": "Sarah Chen",
  "state": "MA",
  "housing_situation": "Renter, month-to-month, no signed lease",
  "employment_type": "Full-time W2, marketing coordinator",
  "family_status": "Single, no dependents"
}
```

### ActionRequest

Inbound request to generate a demand letter, rights summary, or checklist.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `context` | `str` | — | Yes | Max 5,000 chars | Situation description for the action generator |

**Example JSON:**

```json
{
  "context": "My landlord is withholding my $1,850 security deposit claiming $800 in bathroom tile damage. He never did a move-in inspection and the damage was pre-existing."
}
```

---

## Python Models — Action Outputs

Source: `backend/models/action_output.py`

These models represent the structured output of CaseMate's action generators. Each is returned
by the corresponding `/api/actions/*` endpoint and rendered in the `ActionGenerator.tsx` component.

### DemandLetter

A ready-to-send demand letter generated from the user's profile and situation context.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `text` | `str` | — | Yes | Full letter body, formatted and ready to print/send |
| `citations` | `list[str]` | `[]` | No | Statute citations referenced in the letter |
| `recipient` | `str \| None` | `None` | No | Addressee name (e.g., landlord's name) |
| `subject` | `str` | — | Yes | Letter subject line |

**Example JSON:**

```json
{
  "text": "Dear Mr. Johnson,\n\nI am writing regarding the security deposit of $1,850 paid on January 15, 2026 for the rental unit at 42 Maple Street, Apt 3B, Boston, MA 02115.\n\nPursuant to Massachusetts General Laws Chapter 186, Section 15B, you are required to return my security deposit within 30 days of lease termination...\n\nSincerely,\nSarah Chen",
  "citations": [
    "M.G.L. c.186 §15B",
    "M.G.L. c.93A §9"
  ],
  "recipient": "Robert Johnson",
  "subject": "Demand for Return of Security Deposit — 42 Maple Street, Apt 3B"
}
```

### RightsSummary

A narrative explanation of the user's rights in their specific situation.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `text` | `str` | — | Yes | Full narrative explanation of rights |
| `key_rights` | `list[str]` | `[]` | No | Bullet-point list of the most important rights |
| `applicable_laws` | `list[str]` | `[]` | No | Statute citations that apply |

**Example JSON:**

```json
{
  "text": "As a Massachusetts renter, you have strong protections under the state's security deposit law...",
  "key_rights": [
    "Landlord must return deposit within 30 days of lease termination",
    "Landlord must provide itemized list of damages with receipts",
    "Landlord who fails to conduct move-in inspection cannot deduct for pre-existing damage",
    "You may be entitled to 3x the deposit amount if landlord violated the statute"
  ],
  "applicable_laws": [
    "M.G.L. c.186 §15B",
    "M.G.L. c.93A §9",
    "940 CMR 3.17"
  ]
}
```

### Checklist

A prioritized list of action items with optional deadlines.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `items` | `list[str]` | `[]` | No | Action items the user should take |
| `deadlines` | `list[str \| None]` | `[]` | No | Index-aligned with `items`. Each entry is an ISO date string or `None` if no deadline applies |
| `priority_order` | `list[int]` | `[]` | No | Indices into `items` sorted by urgency (most urgent first) |

**Example JSON:**

```json
{
  "items": [
    "Send demand letter to landlord via certified mail",
    "File complaint with Massachusetts Attorney General if no response in 30 days",
    "Gather all move-in photos and correspondence as evidence",
    "File small claims court action if deposit not returned"
  ],
  "deadlines": [
    "2026-04-05",
    "2026-05-05",
    null,
    "2026-06-15"
  ],
  "priority_order": [2, 0, 1, 3]
}
```

**Note:** `priority_order: [2, 0, 1, 3]` means: do item 2 first (gather evidence), then
item 0 (send letter), then item 1 (file complaint), then item 3 (small claims).

---

## Python Models — Deadlines

Source: `backend/models/` (deadline models)

### DeadlineStatus

A `StrEnum` representing the lifecycle state of a tracked deadline.

| Value | Meaning |
|-------|---------|
| `"active"` | Deadline is upcoming and being tracked |
| `"completed"` | User marked the deadline as done |
| `"dismissed"` | User chose to ignore this deadline |
| `"expired"` | Deadline date has passed without action |

```python
class DeadlineStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
```

### Deadline

A legal deadline detected from conversation or manually created by the user. Displayed
in the `DeadlineDashboard.tsx` component.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | UUID string |
| `user_id` | `str` | — | Yes | FK to user_profiles |
| `title` | `str` | — | Yes | Description of what is due |
| `date` | `str` | — | Yes | ISO date string (e.g., `"2026-04-15"`) |
| `legal_area` | `str \| None` | `None` | No | Legal domain this deadline relates to |
| `source_conversation_id` | `str \| None` | `None` | No | Conversation where deadline was detected |
| `status` | `DeadlineStatus` | `ACTIVE` | No | Current lifecycle state |
| `notes` | `str` | `""` | No | Additional context about this deadline |
| `created_at` | `datetime` | `utcnow()` | No | When the deadline was created |

**Example JSON:**

```json
{
  "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Landlord must return security deposit or provide itemized deduction list",
  "date": "2026-04-28",
  "legal_area": "landlord_tenant",
  "source_conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "active",
  "notes": "30 days from lease termination date (March 29, 2026). M.G.L. c.186 §15B.",
  "created_at": "2026-03-20T09:16:00Z"
}
```

### DeadlineCreateRequest

Inbound request to create a new deadline via the API.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `title` | `str` | — | Yes | Max 500 chars | Description of the deadline |
| `date` | `str` | — | Yes | ISO date format | Due date |
| `legal_area` | `str \| None` | `None` | No | — | Legal domain |
| `notes` | `str` | `""` | No | Max 2,000 chars | Additional context |

### DeadlineUpdateRequest

Inbound PATCH request to update an existing deadline.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `title` | `str \| None` | `None` | No | Max 500 chars | New title |
| `date` | `str \| None` | `None` | No | ISO date format | New due date |
| `status` | `DeadlineStatus \| None` | `None` | No | — | New status |
| `notes` | `str \| None` | `None` | No | Max 2,000 chars | New notes |

All fields are optional. Only provided fields are updated.

---

## Python Models — Workflows

Source: `backend/models/` (workflow models)

### StepStatus

A `StrEnum` representing the progress state of an individual workflow step.

| Value | Meaning |
|-------|---------|
| `"not_started"` | Step has not been begun |
| `"in_progress"` | User is currently working on this step |
| `"completed"` | Step is done |
| `"skipped"` | User chose to skip this step |

```python
class StepStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
```

### WorkflowStep

A single step within a guided legal workflow.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | Unique identifier for the step within the workflow |
| `title` | `str` | — | Yes | Short title (e.g., `"Send Demand Letter"`) |
| `explanation` | `str` | — | Yes | Detailed explanation of what to do and why |
| `required_documents` | `list[str]` | — | Yes | Documents needed for this step |
| `tips` | `list[str]` | — | Yes | Practical tips for completing the step |
| `deadlines` | `list[str]` | — | Yes | Any time-sensitive deadlines for this step |
| `status` | `StepStatus` | `NOT_STARTED` | No | Current progress |

**Example JSON:**

```json
{
  "id": "step-1-demand-letter",
  "title": "Send Demand Letter to Landlord",
  "explanation": "Before filing in court, Massachusetts law strongly favors demand letters. A well-crafted demand letter citing M.G.L. c.186 §15B often resolves deposit disputes without litigation.",
  "required_documents": [
    "Move-in condition photos",
    "Copy of lease or rental agreement",
    "Written notice to vacate"
  ],
  "tips": [
    "Send via certified mail with return receipt requested",
    "Keep a copy for your records",
    "Set a 30-day deadline for response"
  ],
  "deadlines": [
    "Send within 30 days of move-out for maximum leverage"
  ],
  "status": "not_started"
}
```

### WorkflowTemplate

A reusable template defining a guided legal workflow. Templates are read-only reference data.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | Template identifier (e.g., `"eviction-defense"`, `"security-deposit-recovery"`) |
| `title` | `str` | — | Yes | Display title |
| `description` | `str` | — | Yes | What this workflow helps the user accomplish |
| `domain` | `str` | — | Yes | Legal area (e.g., `"landlord_tenant"`) |
| `estimated_time` | `str` | — | Yes | How long the workflow typically takes (e.g., `"2-4 weeks"`) |
| `steps` | `list[WorkflowStep]` | — | Yes | Ordered list of steps |

### WorkflowInstance

A user's active instance of a workflow template, tracking their progress.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | UUID string |
| `user_id` | `str` | — | Yes | FK to user_profiles |
| `template_id` | `str` | — | Yes | Which template this instance was created from |
| `title` | `str` | — | Yes | Display title (copied from template) |
| `domain` | `str` | — | Yes | Legal area |
| `steps` | `list[WorkflowStep]` | — | Yes | Steps with user's progress state |
| `current_step` | `int` | `0` | No | Index of the step the user is currently on |
| `status` | `StepStatus` | `IN_PROGRESS` | No | Overall workflow status |
| `started_at` | `datetime` | `utcnow()` | No | When the user started this workflow |
| `updated_at` | `datetime` | `utcnow()` | No | Last progress update |

**Example JSON:**

```json
{
  "id": "b5c7d8e9-f0a1-2345-6789-0abcdef12345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "template_id": "security-deposit-recovery",
  "title": "Security Deposit Recovery",
  "domain": "landlord_tenant",
  "steps": [
    {
      "id": "step-1-demand-letter",
      "title": "Send Demand Letter to Landlord",
      "explanation": "...",
      "required_documents": ["Move-in photos", "Lease copy"],
      "tips": ["Send via certified mail"],
      "deadlines": ["Within 30 days of move-out"],
      "status": "completed"
    },
    {
      "id": "step-2-file-complaint",
      "title": "File AG Complaint if No Response",
      "explanation": "...",
      "required_documents": ["Copy of demand letter", "Certified mail receipt"],
      "tips": ["File online at mass.gov/ago"],
      "deadlines": ["30 days after demand letter"],
      "status": "not_started"
    }
  ],
  "current_step": 1,
  "status": "in_progress",
  "started_at": "2026-03-21T10:00:00Z",
  "updated_at": "2026-03-25T14:30:00Z"
}
```

---

## Python Models — Referrals

Source: `backend/models/` (referral models)

### Attorney

An attorney in the referral database. This is read-only reference data populated by CaseMate.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `str` | — | Yes | UUID string |
| `name` | `str` | — | Yes | Full name |
| `state` | `str` | — | Yes | Two-letter state code where they practice |
| `specializations` | `list[str]` | — | Yes | Legal areas (e.g., `["landlord_tenant", "consumer"]`) |
| `rating` | `float` | — | Yes | 0.0 to 5.0 rating |
| `cost_range` | `str` | — | Yes | Typical fee range (e.g., `"$150-300/hr"`) |
| `phone` | `str` | — | Yes | Contact phone number |
| `email` | `str` | — | Yes | Contact email |
| `website` | `str` | — | Yes | Website URL |
| `accepts_free_consultations` | `bool` | — | Yes | Whether they offer free initial consultations |
| `bio` | `str` | — | Yes | Short biography |

**Example JSON:**

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "name": "Maria Rodriguez",
  "state": "MA",
  "specializations": ["landlord_tenant", "consumer", "small_claims"],
  "rating": 4.7,
  "cost_range": "$150-250/hr",
  "phone": "(617) 555-0142",
  "email": "mrodriguez@bostonlegal.com",
  "website": "https://bostonlegal.com/rodriguez",
  "accepts_free_consultations": true,
  "bio": "15 years of experience in tenant rights and consumer protection law in Massachusetts."
}
```

### ReferralSuggestion

A matched attorney recommendation based on the user's profile and active issues.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `attorney` | `Attorney` | — | Yes | The matched attorney record |
| `match_reason` | `str` | — | Yes | Why this attorney was recommended |
| `relevance_score` | `int` | — | Yes | 0-100 relevance score based on specialization, state, and issue type match |

**Example JSON:**

```json
{
  "attorney": {
    "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "name": "Maria Rodriguez",
    "state": "MA",
    "specializations": ["landlord_tenant", "consumer"],
    "rating": 4.7,
    "cost_range": "$150-250/hr",
    "phone": "(617) 555-0142",
    "email": "mrodriguez@bostonlegal.com",
    "website": "https://bostonlegal.com/rodriguez",
    "accepts_free_consultations": true,
    "bio": "15 years of experience in tenant rights..."
  },
  "match_reason": "Specializes in landlord-tenant disputes in Massachusetts with free initial consultation",
  "relevance_score": 92
}
```

---

## Python Models — Payments

Source: `backend/models/` (payment/subscription models)

### CreateCheckoutRequest

Inbound request to create a Stripe checkout session.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `price_id` | `str` | — | Yes | Max 200 chars | Stripe Price ID (e.g., `"price_1abc..."`) |
| `success_url` | `str` | — | Yes | Max 2,000 chars | Redirect URL after successful payment |
| `cancel_url` | `str` | — | Yes | Max 2,000 chars | Redirect URL if user cancels |

**Example JSON:**

```json
{
  "price_id": "price_1OxBzKABCD1234567890",
  "success_url": "https://casemate.app/subscription/success",
  "cancel_url": "https://casemate.app/subscription/cancel"
}
```

### CheckoutSessionResponse

Response after creating a Stripe checkout session.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `session_id` | `str` | — | Yes | Stripe checkout session ID |
| `url` | `str` | — | Yes | Stripe hosted checkout URL to redirect the user to |

**Example JSON:**

```json
{
  "session_id": "cs_live_a1b2c3d4e5f6g7h8i9j0",
  "url": "https://checkout.stripe.com/c/pay/cs_live_a1b2c3d4..."
}
```

### SubscriptionStatus

The user's current subscription state.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `user_id` | `str` | — | Yes | Supabase auth user ID |
| `is_active` | `bool` | — | Yes | Whether the user has an active paid subscription |
| `stripe_subscription_id` | `str \| None` | `None` | No | Stripe subscription ID if subscribed |
| `status` | `str` | `"none"` | No | Subscription state: `"none"`, `"active"`, `"past_due"`, `"canceled"` |
| `current_period_end` | `datetime \| None` | `None` | No | When the current billing period ends |

**Example JSON (active subscriber):**

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "is_active": true,
  "stripe_subscription_id": "sub_1OxBzKABCD1234567890",
  "status": "active",
  "current_period_end": "2026-04-15T00:00:00Z"
}
```

**Example JSON (free user):**

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "is_active": false,
  "stripe_subscription_id": null,
  "status": "none",
  "current_period_end": null
}
```

---

## Python Models — Export

Source: `backend/models/` (export models)

### ExportDocumentRequest

Request to export a generated document (letter, rights summary, checklist) as a PDF.

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `type` | `str` | — | Yes | Document type: `"letter"`, `"rights"`, `"checklist"`, or `"custom"` |
| `content` | `dict[str, object]` | — | Yes | The document content matching the corresponding action output model |

### ExportEmailRequest

Request to email an exported document to the user.

| Field | Type | Default | Required | Constraints | Description |
|-------|------|---------|----------|-------------|-------------|
| `type` | `str` | — | Yes | — | Document type: `"letter"`, `"rights"`, `"checklist"`, or `"custom"` |
| `content` | `dict[str, object]` | — | Yes | — | Document content |
| `email` | `str` | — | Yes | Max 320 chars | Recipient email address |

---

## Supabase Database Schema

All tables live in the `public` schema. Auth is handled by Supabase's built-in `auth.users` table.

### user_profiles

The persistent storage for `LegalProfile`. One row per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | `uuid` | **PK**, FK to `auth.users` ON DELETE CASCADE | Supabase auth user ID |
| `display_name` | `text` | NOT NULL | User's display name |
| `state` | `varchar(2)` | NOT NULL | Two-letter state code |
| `housing_situation` | `text` | NOT NULL | Housing description |
| `employment_type` | `text` | NOT NULL | Employment description |
| `family_status` | `text` | NOT NULL | Family status description |
| `active_issues` | `jsonb` | DEFAULT `'[]'` | Array of `LegalIssue` objects |
| `legal_facts` | `jsonb` | DEFAULT `'[]'` | Array of fact strings |
| `documents` | `jsonb` | DEFAULT `'[]'` | Array of Supabase Storage paths |
| `member_since` | `timestamptz` | DEFAULT `now()` | Account creation time |
| `conversation_count` | `integer` | DEFAULT `0` | Total conversation count |
| `free_messages_used` | `integer` | DEFAULT `0` | Free-tier message counter (not in Pydantic model, DB-only) |
| `created_at` | `timestamptz` | DEFAULT `now()` | Row creation time |
| `updated_at` | `timestamptz` | DEFAULT `now()` | Last update time |

**Note:** `free_messages_used` exists only in the database, not in the Pydantic `LegalProfile`
model. It is used server-side to enforce free-tier message limits without exposing the count
to the client.

### conversations

Stores full conversation threads as JSONB message arrays.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | **PK** | Conversation UUID |
| `user_id` | `uuid` | FK to `auth.users`, NOT NULL | Owning user |
| `messages` | `jsonb` | DEFAULT `'[]'` | Array of `Message` objects |
| `legal_area` | `text` | NULL | Dominant legal domain |
| `created_at` | `timestamptz` | DEFAULT `now()` | Conversation start time |
| `updated_at` | `timestamptz` | DEFAULT `now()` | Last message time |

### deadlines

User-tracked legal deadlines, either auto-detected from conversations or manually created.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | **PK** | Deadline UUID |
| `user_id` | `uuid` | FK to `auth.users`, NOT NULL | Owning user |
| `title` | `text` | NOT NULL | Deadline description |
| `date` | `text` | NOT NULL | ISO date string |
| `legal_area` | `text` | NULL | Related legal domain |
| `source_conversation_id` | `uuid` | FK to `conversations`, NULL | Conversation where detected |
| `status` | `text` | DEFAULT `'active'` | One of: `active`, `completed`, `dismissed`, `expired` |
| `notes` | `text` | DEFAULT `''` | Additional context |
| `created_at` | `timestamptz` | DEFAULT `now()` | Creation time |

### subscriptions

Stripe subscription state for each user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | `uuid` | **PK**, FK to `auth.users` | Supabase auth user ID |
| `stripe_customer_id` | `text` | NULL | Stripe Customer ID |
| `stripe_subscription_id` | `text` | NULL | Stripe Subscription ID |
| `status` | `text` | DEFAULT `'none'` | One of: `none`, `active`, `past_due`, `canceled` |
| `cancel_at_period_end` | `boolean` | DEFAULT `false` | Whether subscription cancels at period end |
| `current_period_end` | `timestamptz` | NULL | End of current billing period |
| `created_at` | `timestamptz` | DEFAULT `now()` | Row creation time |
| `updated_at` | `timestamptz` | DEFAULT `now()` | Last update time |

### workflow_instances

Active workflow instances tracking a user's progress through guided legal workflows.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | **PK** | Instance UUID |
| `user_id` | `uuid` | FK to `auth.users` | Owning user |
| `template_id` | `text` | NOT NULL | Which workflow template this was created from |
| `title` | `text` | NOT NULL | Display title |
| `domain` | `text` | NOT NULL | Legal area |
| `steps` | `jsonb` | DEFAULT `'[]'` | Array of `WorkflowStep` objects with progress |
| `current_step` | `integer` | DEFAULT `0` | Index of current step |
| `status` | `text` | DEFAULT `'in_progress'` | Overall workflow status |
| `started_at` | `timestamptz` | DEFAULT `now()` | When user started the workflow |
| `updated_at` | `timestamptz` | DEFAULT `now()` | Last progress update |

### attorneys

Read-only reference table of attorneys available for referral.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | **PK** | Attorney UUID |
| `name` | `text` | NOT NULL | Full name |
| `state` | `varchar(2)` | NOT NULL | State where they practice |
| `specializations` | `jsonb` | DEFAULT `'[]'` | Array of legal area strings |
| `rating` | `real` | DEFAULT `0.0` | 0.0-5.0 rating |
| `cost_range` | `text` | DEFAULT `''` | Fee range string |
| `phone` | `text` | DEFAULT `''` | Phone number |
| `email` | `text` | DEFAULT `''` | Email address |
| `website` | `text` | DEFAULT `''` | Website URL |
| `accepts_free_consultations` | `boolean` | DEFAULT `false` | Free consultation availability |
| `bio` | `text` | DEFAULT `''` | Short biography |

---

## Relationships Diagram

```
auth.users (Supabase built-in)
    |
    |-- 1:1 -- user_profiles
    |              |
    |              |-- embeds --> active_issues (jsonb array of LegalIssue)
    |              |-- embeds --> legal_facts (jsonb array of strings)
    |              |-- embeds --> documents (jsonb array of storage paths)
    |
    |-- 1:N -- conversations
    |              |
    |              |-- embeds --> messages (jsonb array of Message)
    |              |
    |              |-- 1:N (reverse FK) -- deadlines.source_conversation_id
    |
    |-- 1:N -- deadlines
    |
    |-- 1:1 -- subscriptions
    |
    |-- 1:N -- workflow_instances
                   |
                   |-- embeds --> steps (jsonb array of WorkflowStep)
                   |-- references --> workflow templates (by template_id, not FK)

attorneys (standalone, no user FK)
    |
    |-- queried by state + specializations --> ReferralSuggestion (computed, not stored)
```

**Key design decisions:**

1. **JSONB for nested data:** `active_issues`, `legal_facts`, `messages`, and `steps` are
   stored as JSONB arrays rather than normalized tables. This keeps reads fast (single query
   returns the complete object) at the cost of not being able to query individual facts or
   messages via SQL. This tradeoff is correct because the primary consumer is prompt injection,
   which always needs the full array.

2. **1:1 profile-to-user:** Every Supabase auth user has exactly one `user_profiles` row.
   Created during onboarding. Never deleted (even if subscription lapses).

3. **No FK from workflow_instances to templates:** Templates are code-defined, not database rows.
   The `template_id` is a string reference to a Python object, not a foreign key.

---

## Row-Level Security Policies

All tables have RLS enabled. Policies enforce that users can only access their own data.

### user_profiles

| Policy | Operation | Rule |
|--------|-----------|------|
| `Users can read own profile` | SELECT | `auth.uid() = user_id` |
| `Users can update own profile` | UPDATE | `auth.uid() = user_id` |
| `Users can insert own profile` | INSERT | `auth.uid() = user_id` |

Users cannot delete their own profile. Profile deletion is an admin operation.

### conversations

| Policy | Operation | Rule |
|--------|-----------|------|
| `Users can read own conversations` | SELECT | `auth.uid() = user_id` |
| `Users can create own conversations` | INSERT | `auth.uid() = user_id` |
| `Users can update own conversations` | UPDATE | `auth.uid() = user_id` |
| `Users can delete own conversations` | DELETE | `auth.uid() = user_id` |

Full CRUD access to own conversations only.

### deadlines

| Policy | Operation | Rule |
|--------|-----------|------|
| `Users can read own deadlines` | SELECT | `auth.uid() = user_id` |
| `Users can create own deadlines` | INSERT | `auth.uid() = user_id` |
| `Users can update own deadlines` | UPDATE | `auth.uid() = user_id` |
| `Users can delete own deadlines` | DELETE | `auth.uid() = user_id` |

Full CRUD access to own deadlines only.

### subscriptions

| Policy | Operation | Rule |
|--------|-----------|------|
| `Users can read own subscription` | SELECT | `auth.uid() = user_id` |

Read-only for users. Subscription writes are handled server-side via Stripe webhooks
using the service role key.

### attorneys

| Policy | Operation | Rule |
|--------|-----------|------|
| `Public read access` | SELECT | `true` |

No authentication required to search attorneys. This table is read-only reference data.
Writes are admin-only (service role key).

### workflow_instances

| Policy | Operation | Rule |
|--------|-----------|------|
| `Users can read own workflows` | SELECT | `auth.uid() = user_id` |
| `Users can create own workflows` | INSERT | `auth.uid() = user_id` |
| `Users can update own workflows` | UPDATE | `auth.uid() = user_id` |
| `Users can delete own workflows` | DELETE | `auth.uid() = user_id` |

---

## Indexes

### Primary Keys (implicit B-tree indexes)

| Table | Column(s) |
|-------|-----------|
| `user_profiles` | `user_id` |
| `conversations` | `id` |
| `deadlines` | `id` |
| `subscriptions` | `user_id` |
| `workflow_instances` | `id` |
| `attorneys` | `id` |

### Secondary Indexes

| Table | Column(s) | Type | Purpose |
|-------|-----------|------|---------|
| `conversations` | `user_id` | B-tree | Fast lookup of all conversations for a user |
| `conversations` | `updated_at DESC` | B-tree | Sort conversations by most recent activity |
| `deadlines` | `user_id` | B-tree | Fast lookup of all deadlines for a user |
| `deadlines` | `status` | B-tree | Filter deadlines by active/completed/etc. |
| `attorneys` | `state` | B-tree | Filter attorneys by state |
| `attorneys` | `specializations` | GIN | JSONB containment queries for legal area matching (e.g., `specializations @> '["landlord_tenant"]'`) |

**GIN index on attorneys.specializations** enables queries like:

```sql
SELECT * FROM attorneys
WHERE state = 'MA'
AND specializations @> '["landlord_tenant"]'::jsonb
ORDER BY rating DESC;
```

---

## TypeScript Interfaces

All TypeScript interfaces live in `shared/types/` and are consumed by both `web/` and `mobile/`.
The mobile app re-exports them via `mobile/lib/types.ts`.

### shared/types/legal-profile.ts

`LegalProfile` and `LegalIssue` mirror the Python models. `IssueStatus` is a union type:
`"open" | "resolved" | "watching" | "escalated"`. Dates are `string` (ISO format) instead
of `datetime`.

### shared/types/conversation.ts

- `Message` — mirrors Python `Message`
- `ChatResponse` — includes `suggested_actions: string[]` (not in Python model)
- `ConversationSummary` — lightweight list view with `id`, `title`, `legal_area`, `updated_at`
- `ConversationDetail` — full thread including inline message type

### shared/types/actions.ts

- `DemandLetter` — fields: `letter_text`, `legal_citations` (different names from Python)
- `RightsSummary` — fields: `summary_text`, `key_rights`
- `Checklist` — fields: `items`, `deadlines`

### shared/types/deadlines.ts

`Deadline`, `DeadlineCreateRequest`, `DeadlineUpdateRequest` — mirror Python models.

### shared/types/rights.ts

- `RightsGuide` — `domain`, `title`, `your_rights`, `action_steps`, `common_mistakes`, `when_to_get_a_lawyer`
- `RightsDomain` — `domain`, `label`, `guide_count`

### shared/types/workflows.ts

`WorkflowStep`, `WorkflowTemplate`, `WorkflowInstance`, `WorkflowSummary` — mirror Python models.

### shared/types/referrals.ts

`Attorney`, `ReferralSuggestion` — mirror Python models.

---

## Python/TypeScript Field Name Mapping

The frontend and backend use slightly different field names for some models. This table
documents every difference to prevent confusion when mapping API responses to UI components.

| Model | Python Field | TypeScript Field | Notes |
|-------|-------------|-----------------|-------|
| DemandLetter | `text` | `letter_text` | Full letter body |
| DemandLetter | `citations` | `legal_citations` | Statute references |
| RightsSummary | `text` | `summary_text` | Narrative explanation |
| Checklist | `priority_order` | *(not present)* | Frontend sorts by array order |
| ChatResponse | *(not present)* | `suggested_actions` | Frontend-only field for quick action buttons |

---

## Example Data — Sarah Chen

This is the complete demo profile used for the CaseMate demo. It represents a real-world
user who has been using CaseMate for ~2 months with 12 conversations.

### user_profiles row

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "display_name": "Sarah Chen",
  "state": "MA",
  "housing_situation": "Renter, month-to-month, no signed lease",
  "employment_type": "Full-time W2, marketing coordinator",
  "family_status": "Single, no dependents",
  "active_issues": [
    {
      "issue_type": "landlord_tenant",
      "summary": "Landlord claiming $800 for bathroom tile damage from security deposit",
      "status": "open",
      "started_at": "2026-02-15T14:30:00Z",
      "updated_at": "2026-03-20T09:15:00Z",
      "notes": [
        "Landlord did not perform move-in inspection",
        "Pre-existing water damage documented in move-in photos",
        "Landlord sent informal email demand, no itemized statement",
        "Tenant gave written 30-day notice on February 28, 2026"
      ]
    }
  ],
  "legal_facts": [
    "Landlord did not perform move-in inspection",
    "Pre-existing water damage documented in move-in photos taken at move-in",
    "Gave written 30-day notice on February 28, 2026",
    "Monthly rent is $1,850",
    "Security deposit was $1,850 (one month's rent)",
    "Landlord has not provided itemized list of damages within 30 days",
    "Apartment is at 42 Maple Street, Apt 3B, Boston, MA 02115",
    "Landlord's name is Robert Johnson",
    "Lease started January 15, 2026",
    "No signed formal lease — month-to-month verbal agreement",
    "Has photos of all rooms taken at move-in",
    "Bathroom tiles had visible cracks before move-in per photos"
  ],
  "documents": [
    "documents/a1b2c3d4/move-in-photos.pdf",
    "documents/a1b2c3d4/notice-to-vacate.pdf",
    "documents/a1b2c3d4/landlord-email-demand.pdf"
  ],
  "member_since": "2026-01-15T10:00:00Z",
  "conversation_count": 12,
  "free_messages_used": 5,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-03-20T09:15:00Z"
}
```

### Sample conversation (conversation 12 of 12)

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "messages": [
    {
      "role": "user",
      "content": "My landlord is saying I owe $800 for the bathroom tiles. Can he do that?",
      "timestamp": "2026-03-20T09:15:00Z",
      "legal_area": "landlord_tenant"
    },
    {
      "role": "assistant",
      "content": "Sarah, based on what I know about your situation, your landlord has a serious problem here.\n\nUnder Massachusetts law (M.G.L. c.186 §15B), a landlord MUST conduct a move-in inspection and provide you with a written statement of the apartment's condition. Your landlord never did this. That alone means he cannot deduct for any pre-existing damage — and you have move-in photos showing the tile cracks were already there.\n\nHere's what you're entitled to:\n- Full return of your $1,850 security deposit\n- If he wrongfully withholds it, you can recover up to 3x the deposit ($5,550) plus court costs and attorney fees under M.G.L. c.93A §9\n\nThe $800 claim has no legal basis because:\n1. No move-in inspection was conducted (required by §15B)\n2. Your photos prove the damage was pre-existing\n3. He has not provided an itemized deduction list within 30 days\n\n**Your next step today:** I can generate a demand letter citing these specific statutes and facts. Would you like me to do that?",
      "timestamp": "2026-03-20T09:15:12Z",
      "legal_area": "landlord_tenant"
    }
  ],
  "legal_area": "landlord_tenant",
  "created_at": "2026-03-20T09:15:00Z",
  "updated_at": "2026-03-20T09:15:12Z"
}
```

### Sample deadline

```json
{
  "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Landlord must return security deposit or provide itemized deductions",
  "date": "2026-04-28",
  "legal_area": "landlord_tenant",
  "source_conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "active",
  "notes": "30 days from lease termination (March 29, 2026). M.G.L. c.186 §15B requires return within 30 days.",
  "created_at": "2026-03-20T09:16:00Z"
}
```

### Sample subscription

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "stripe_customer_id": "cus_PxQrStUvWxYz",
  "stripe_subscription_id": "sub_1OxBzKABCD1234567890",
  "status": "active",
  "cancel_at_period_end": false,
  "current_period_end": "2026-04-15T00:00:00Z",
  "created_at": "2026-01-15T10:05:00Z",
  "updated_at": "2026-03-15T00:00:00Z"
}
```

### Sample demand letter output

```json
{
  "text": "Dear Mr. Robert Johnson,\n\nRe: Demand for Return of Security Deposit — 42 Maple Street, Apt 3B, Boston, MA 02115\n\nI am writing to demand the immediate return of my security deposit in the amount of $1,850.00, paid on or about January 15, 2026.\n\nAs you are aware, I provided written notice of my intent to vacate on February 28, 2026. Under Massachusetts General Laws Chapter 186, Section 15B, you are required to return my security deposit, together with interest, within thirty (30) days of the termination of my tenancy.\n\nYour claim of $800.00 for bathroom tile damage is without legal basis for the following reasons:\n\n1. You failed to conduct a move-in condition inspection as required by M.G.L. c.186 §15B(1). This failure alone bars you from making any deductions for property damage.\n\n2. I possess dated photographs taken at move-in that document pre-existing damage to the bathroom tiles, including visible cracks.\n\n3. You have failed to provide an itemized list of damages with supporting documentation within the statutory 30-day period.\n\nPlease be advised that under M.G.L. c.186 §15B and M.G.L. c.93A §9, wrongful retention of a security deposit may subject you to liability for treble damages (up to $5,550.00), plus court costs and reasonable attorney fees.\n\nI demand the full return of my $1,850.00 security deposit within fourteen (14) days of the date of this letter. Failure to comply will result in my pursuing all available legal remedies.\n\nSincerely,\nSarah Chen\n42 Maple Street, Apt 3B\nBoston, MA 02115",
  "citations": [
    "M.G.L. c.186 §15B",
    "M.G.L. c.186 §15B(1)",
    "M.G.L. c.93A §9",
    "940 CMR 3.17"
  ],
  "recipient": "Robert Johnson",
  "subject": "Demand for Return of Security Deposit — 42 Maple Street, Apt 3B"
}
```

---

*This document is the authoritative reference for all CaseMate data models. When in doubt
about a field type, constraint, or default — this file is correct. Update it whenever a
model changes.*
