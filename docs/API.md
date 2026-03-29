# API Reference

All endpoints are defined in `backend/main.py`. The backend runs on FastAPI at port 8000.

## Authentication

Every endpoint except `/health` requires a Supabase JWT in the `Authorization` header:

```
Authorization: Bearer <supabase_jwt>
```

JWT verification is handled by `backend/utils/auth.py` (`verify_supabase_jwt`). The token is decoded with HS256 using `SUPABASE_JWT_SECRET`, and the `sub` claim is extracted as `user_id`. See `docs/SECURITY.md` for details.

## Rate Limits

Rate limits are enforced per-user via Redis sliding window counters (`backend/utils/rate_limiter.py`). If Redis is unavailable, rate limiting fails open (requests are allowed).

| Endpoint group | Limit |
|---------------|-------|
| `/api/chat` | 10 requests / 60 seconds |
| `/api/actions/*` | 5 requests / 60 seconds |
| `/api/documents` | 3 requests / 60 seconds |

Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header.

## Request/Response Schemas

Defined as Pydantic models in `backend/main.py`:

- **ChatRequest** — `message: str` (max 10,000 chars), `conversation_id: str | None`
- **ChatResponse** — `conversation_id: str`, `response: str`, `legal_area: str`
- **ProfileRequest** — `display_name: str`, `state: str` (2 chars), `housing_situation: str`, `employment_type: str`, `family_status: str`
- **ActionRequest** — `context: str` (max 5,000 chars)
- **ExportDocumentRequest** — `type: str` (letter/rights/checklist/custom), `content: dict`
- **ExportEmailRequest** — `type: str`, `content: dict`, `email: str`
- **WorkflowStartRequest** — `template_id: str`

Core data models are in `backend/models/legal_profile.py` (`LegalProfile`, `LegalIssue`, `IssueStatus`).

## Endpoints

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Returns `{"status": "ok", "version": "0.3.0"}` |

### Chat

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|-----------|-------------|
| POST | `/api/chat` | Yes | 10/min | Send a message, get a personalized legal response. Loads user profile via `get_profile()`, classifies the legal area, builds a system prompt via `build_system_prompt()`, calls Claude, and schedules background tasks for profile update and deadline detection. Returns `ChatResponse`. |

### Profile

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/profile` | Yes | Create or update the authenticated user's legal profile. Accepts `ProfileRequest`, returns the confirmed profile. |
| GET | `/api/profile/{user_id}` | Yes | Fetch a profile. Users can only access their own (403 otherwise). |

### Conversations

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/conversations` | Yes | List all conversations for the authenticated user. |
| GET | `/api/conversations/{id}` | Yes | Load a specific conversation with full message history. |
| DELETE | `/api/conversations/{id}` | Yes | Delete a conversation. Returns `{"status": "deleted"}`. |

### Actions (AI-generated documents)

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|-----------|-------------|
| POST | `/api/actions/letter` | Yes | 5/min | Generate a demand letter. Requires user profile. Returns `DemandLetter`. |
| POST | `/api/actions/rights` | Yes | 5/min | Generate a rights summary. Returns `RightsSummary`. |
| POST | `/api/actions/checklist` | Yes | 5/min | Generate a next-steps checklist. Returns `Checklist`. |

### Documents

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|-----------|-------------|
| POST | `/api/documents` | Yes | 3/min | Upload a file (PDF, text, image). Max 25 MB. Text is extracted via `backend/documents/extractor.py`, then analyzed by Claude via `backend/documents/analyzer.py`. |

### Deadlines

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/deadlines` | Yes | Create a deadline manually. |
| GET | `/api/deadlines` | Yes | List all deadlines for the user. |
| PATCH | `/api/deadlines/{id}` | Yes | Update a deadline (status, notes, etc.). |
| DELETE | `/api/deadlines/{id}` | Yes | Delete a deadline. |

### Rights Library

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/rights/domains` | Yes | List legal domains with guide counts. |
| GET | `/api/rights/guides` | Yes | List all guides. Optional `?domain=` filter. |
| GET | `/api/rights/guides/{id}` | Yes | Get a specific rights guide by ID. |

### Workflows

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/workflows/templates` | Yes | List available workflow templates. Optional `?domain=` filter. |
| POST | `/api/workflows` | Yes | Start a workflow from a template. Accepts `WorkflowStartRequest`. |
| GET | `/api/workflows` | Yes | List the user's active workflows. |
| GET | `/api/workflows/{id}` | Yes | Load a specific workflow instance. |
| PATCH | `/api/workflows/{id}/steps` | Yes | Update a step's status in a workflow. |

### Export

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/export/document` | Yes | Generate a PDF (letter, rights, checklist, or custom). Returns binary PDF with `Content-Disposition` header. |
| POST | `/api/export/email` | Yes | Generate a PDF and email it. Requires SMTP configuration. |

### Attorney Referrals

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/attorneys/search` | Yes | Search attorneys by `state` (required) and optional `legal_area`. |

### Payments

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/payments/create-checkout-session` | Yes | Create a Stripe checkout session. Accepts `CreateCheckoutRequest` (price_id, success_url, cancel_url). Returns `CheckoutSessionResponse`. |
| POST | `/api/payments/webhook` | No (Stripe signature) | Handle Stripe webhook events. Verifies `Stripe-Signature` header. |
| GET | `/api/payments/subscription` | Yes | Get the user's current subscription status. Returns `SubscriptionStatus`. |
| POST | `/api/payments/cancel` | Yes | Cancel subscription at period end. Returns updated `SubscriptionStatus`. |

## Quick Examples

### Send a chat message (curl)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{"message": "My landlord is keeping my security deposit"}'
```

### Get user profile (curl)

```bash
curl http://localhost:8000/api/profile/$USER_ID \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

### Generate a demand letter (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/actions/letter",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={"context": "Landlord withheld $800 security deposit without itemized deductions"},
)
letter = response.json()["letter"]
print(letter["letter_text"])
```

### SSE streaming (curl)

```bash
curl -N http://localhost:8000/api/chat/$CONVERSATION_ID/stream \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

## Error Responses

All errors follow the standard FastAPI pattern: `{"detail": "Error message"}` with the appropriate HTTP status code (400, 401, 403, 404, 413, 429, 500).
