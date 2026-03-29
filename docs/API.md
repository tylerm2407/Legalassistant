# CaseMate API Reference

> Version 0.4.0 | Base URL: `http://localhost:8000` (development) or your deployed backend URL.

This document is the definitive reference for every CaseMate API endpoint. A developer should be able to call any endpoint correctly using only this document.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Subscription Tiers](#subscription-tiers)
4. [Error Response Format](#error-response-format)
5. [Endpoints](#endpoints)
   - [Health & Metrics](#health--metrics)
   - [Chat](#chat)
   - [Profile](#profile)
   - [Conversations](#conversations)
   - [Actions](#actions)
   - [Documents](#documents)
   - [Deadlines](#deadlines)
   - [Rights Library](#rights-library)
   - [Workflows](#workflows)
   - [Export](#export)
   - [Attorney Referrals](#attorney-referrals)
   - [Payments](#payments)
   - [Waitlist](#waitlist)

---

## Authentication

CaseMate uses Supabase JWTs for authentication. Every endpoint except `/health`, `/metrics`, `/api/payments/webhook`, and `/api/waitlist` requires a valid JWT.

**How it works:**

1. The user authenticates via Supabase Auth (email/password, OAuth, or magic link).
2. Supabase returns a JWT access token.
3. Include the token in every API request as a Bearer token in the `Authorization` header.

```
Authorization: Bearer <supabase_jwt>
```

**Token details:**

- Algorithm: HS256
- Verification key: `SUPABASE_JWT_SECRET` environment variable
- The `sub` claim in the JWT payload is extracted as the `user_id` for all downstream operations.
- Expired or malformed tokens return `401 Unauthorized`.

**Getting a token (development):**

```bash
# Sign up or sign in via Supabase client
# The access_token in the response is your JWT
curl -X POST 'https://<project>.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

The response includes `access_token` — use that as your Bearer token.

---

## Rate Limiting

Rate limits are enforced per-user using Redis-backed sliding window counters (`backend/utils/rate_limiter.py`).

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| `/api/chat`, `/api/chat/*/stream` | 10 requests | 60 seconds |
| `/api/actions/*` | 5 requests | 60 seconds |
| `/api/documents` | 3 requests | 60 seconds |

**Behavior when exceeded:**

- HTTP status: `429 Too Many Requests`
- Response includes a `Retry-After` header with the number of seconds to wait.
- Response body: `{"detail": "Rate limit exceeded. Try again in X seconds."}`

**Fail-open policy:** If Redis is unavailable, rate limiting is disabled and all requests are allowed. This prevents Redis outages from blocking users.

---

## Subscription Tiers

CaseMate gates certain features behind a paid subscription managed via Stripe.

| Feature | Free Tier | Paid Tier ($20/month) |
|---------|-----------|----------------------|
| Chat messages | 5 per month | Unlimited |
| Action generation (letter, rights, checklist) | Blocked | Unlimited |
| Document upload & analysis | Blocked | Unlimited |
| PDF/email export | Blocked | Unlimited |
| Profile, conversations, deadlines, rights, workflows | Full access | Full access |

When a free-tier user exhausts their 5 monthly messages, the `/api/chat` endpoint returns `402 Payment Required`.

Subscription-gated endpoints are marked with "(subscription gate)" in this document. These return `402` for users without an active paid subscription.

---

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "detail": "Human-readable error message"
}
```

**Common HTTP status codes:**

| Code | Meaning |
|------|---------|
| 400 | Bad request — invalid input, unsupported file type, or missing required fields |
| 401 | Unauthorized — missing, expired, or invalid JWT |
| 402 | Payment required — free tier exhausted or subscription-gated feature |
| 403 | Forbidden — attempting to access another user's resource |
| 404 | Not found — resource does not exist |
| 413 | Payload too large — file exceeds 25 MB limit |
| 429 | Rate limit exceeded — retry after the duration in the `Retry-After` header |
| 500 | Internal server error — AI call failure or unexpected backend error |
| 503 | Service unavailable — circuit breaker open (AI provider experiencing issues) |

---

## Endpoints

---

## Health & Metrics

### GET /health

Returns the application's health status and version. Used by load balancers, uptime monitors, and deployment checks.

**Authentication:** None required.

**Rate Limit:** None.

**Request:** No parameters.

**Example Request:**

```bash
curl http://localhost:8000/health
```

**Example Response:**

```json
{
  "status": "ok",
  "version": "0.4.0",
  "lifecycle": {
    "uptime_seconds": 3621,
    "started_at": "2026-03-29T12:00:00Z"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always `"ok"` when the service is running |
| version | string | Current application version |
| lifecycle | object | Uptime and start time metadata |

**Errors:** This endpoint does not return errors. If it is unreachable, the service is down.

---

### GET /metrics

Returns Prometheus-compatible application metrics. Used by monitoring infrastructure.

**Authentication:** None required.

**Rate Limit:** None.

**Request:** No parameters.

**Example Request:**

```bash
curl http://localhost:8000/metrics
```

**Example Response:**

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/chat",status="200"} 142
http_requests_total{method="GET",endpoint="/health",status="200"} 891
# HELP response_latency_seconds Response latency in seconds
# TYPE response_latency_seconds histogram
response_latency_seconds_bucket{le="0.5"} 98
```

**Response Content-Type:** `text/plain`

**Errors:** This endpoint does not return errors under normal operation.

---

## Chat

### POST /api/chat

Send a message and receive a personalized legal response. This is the core endpoint of CaseMate. It loads the user's legal profile, classifies the legal area, builds a memory-injected system prompt, calls Claude, and returns the response. After responding, it schedules background tasks for profile auto-update, deadline detection, and audit logging.

**Authentication:** JWT Bearer token (subscription gate — free tier: 5 messages/month).

**Rate Limit:** 10 requests / 60 seconds.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | The user's legal question. Maximum 10,000 characters. |
| conversation_id | string or null | No | Existing conversation ID to continue. Omit or pass `null` to start a new conversation. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | string | The conversation ID (new or existing). Format: `conv_<alphanumeric>`. |
| response | string | CaseMate's personalized legal response with statute citations. |
| legal_area | string | Classified legal domain (e.g., `landlord_tenant`, `employment`, `consumer`). |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My landlord is keeping my security deposit and won'\''t give me an itemized list of deductions",
    "conversation_id": null
  }'
```

**Example Response:**

```json
{
  "conversation_id": "conv_abc123def456",
  "response": "Based on your situation in Massachusetts as a renter without a signed lease, your landlord is in a very weak position here. Under M.G.L. c.186 §15B, a landlord MUST provide an itemized list of deductions within 30 days of your tenancy ending. Since they didn't conduct a move-in inspection — which we discussed in your previous session — they cannot prove any of the damage was caused by you.\n\nYou are likely entitled to: your full deposit back PLUS up to 3x the deposit amount in damages, plus 5% annual interest, plus reasonable attorney's fees.\n\nNext step: I can generate a demand letter citing §15B that you can send to your landlord today. Want me to draft it?",
  "legal_area": "landlord_tenant"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | Free tier message limit exhausted (5/month) |
| 404 | User profile not found — user must complete onboarding first |
| 429 | Rate limit exceeded |
| 500 | AI provider error (Claude API failure after retries) |
| 503 | Circuit breaker open — AI provider experiencing sustained failures |

---

### GET /api/chat/{conversation_id}/stream

Stream a legal response in real time via Server-Sent Events (SSE). Same logic as `POST /api/chat` but delivers tokens as they are generated.

**Authentication:** JWT Bearer token.

**Rate Limit:** 10 requests / 60 seconds.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | The conversation ID to stream into. |

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | The user's legal question. |

**SSE Event Types:**

| Event Type | Fields | Description |
|------------|--------|-------------|
| token | `type`, `content` | A chunk of response text as it is generated. |
| done | `type`, `conversation_id`, `legal_area`, `response_length`, `latency_ms` | Signals the stream is complete with metadata. |
| error | `type`, `message`, `retry_after` | An error occurred. `retry_after` is seconds (present on 429). |

**Example Request:**

```bash
curl -N "http://localhost:8000/api/chat/conv_abc123/stream?message=What%20are%20my%20rights%20as%20a%20tenant" \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example SSE Stream:**

```
data: {"type": "token", "content": "Based on your "}

data: {"type": "token", "content": "situation in Massachusetts"}

data: {"type": "token", "content": ", under M.G.L. c.186 §15B..."}

data: {"type": "done", "conversation_id": "conv_abc123", "legal_area": "landlord_tenant", "response_length": 847, "latency_ms": 3200}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 429 | Rate limit exceeded |
| 500 | AI provider error |

---

## Profile

### POST /api/profile

Create or update the authenticated user's legal profile. Called after the onboarding wizard to store the user's baseline legal context.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| display_name | string | Yes | User's display name. Maximum 100 characters. |
| state | string | Yes | Two-letter US state code (e.g., `MA`, `CA`, `TX`). Maximum 2 characters. |
| housing_situation | string | Yes | Description of housing (e.g., "Renter, month-to-month, no signed lease"). Maximum 500 characters. |
| employment_type | string | Yes | Employment classification (e.g., "Full-time W2 employee"). Maximum 200 characters. |
| family_status | string | Yes | Family situation (e.g., "Single, no dependents"). Maximum 500 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| profile | LegalProfile | The complete persisted legal profile object. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/profile \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Sarah Chen",
    "state": "MA",
    "housing_situation": "Renter, month-to-month lease, no signed lease agreement",
    "employment_type": "Full-time W2, marketing coordinator",
    "family_status": "Single, no dependents"
  }'
```

**Example Response:**

```json
{
  "profile": {
    "user_id": "usr_a1b2c3d4",
    "display_name": "Sarah Chen",
    "state": "MA",
    "housing_situation": "Renter, month-to-month lease, no signed lease agreement",
    "employment_type": "Full-time W2, marketing coordinator",
    "family_status": "Single, no dependents",
    "active_issues": [],
    "legal_facts": [],
    "documents": [],
    "member_since": "2026-01-15T00:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 422 | Validation error (field too long, missing required field) |

---

### GET /api/profile/{user_id}

Fetch a user's legal profile. Users can only access their own profile.

**Authentication:** JWT Bearer token (the `user_id` in the path must match the authenticated user).

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | The user's ID. Must match the authenticated user's JWT `sub` claim. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| profile | LegalProfile | The complete legal profile with all accumulated facts and issues. |

**Example Request:**

```bash
curl http://localhost:8000/api/profile/usr_a1b2c3d4 \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "profile": {
    "user_id": "usr_a1b2c3d4",
    "display_name": "Sarah Chen",
    "state": "MA",
    "housing_situation": "Renter, month-to-month lease, no signed lease agreement",
    "employment_type": "Full-time W2, marketing coordinator",
    "family_status": "Single, no dependents",
    "active_issues": [
      {
        "id": "issue_001",
        "title": "Security deposit dispute with landlord",
        "legal_area": "landlord_tenant",
        "status": "active",
        "created_at": "2026-02-10T14:30:00Z",
        "facts": ["Landlord claims $800 for bathroom tile damage"]
      }
    ],
    "legal_facts": [
      "Landlord did not perform move-in inspection",
      "Pre-existing water damage documented in move-in photos",
      "Gave written 30-day notice on February 28, 2026"
    ],
    "documents": [],
    "member_since": "2026-01-15T00:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 403 | Attempting to access another user's profile |
| 404 | Profile not found — user has not completed onboarding |

---

## Conversations

### GET /api/conversations

List all conversations for the authenticated user, ordered by most recently updated.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No parameters.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| conversations | array | List of conversation summary objects. |
| conversations[].id | string | Conversation ID. |
| conversations[].legal_area | string | Classified legal domain of the conversation. |
| conversations[].updated_at | string | ISO 8601 timestamp of the last message. |
| conversations[].preview | string | Truncated preview of the last message. |
| conversations[].message_count | integer | Total number of messages in the conversation. |

**Example Request:**

```bash
curl http://localhost:8000/api/conversations \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "conversations": [
    {
      "id": "conv_abc123",
      "legal_area": "landlord_tenant",
      "updated_at": "2026-03-28T16:45:00Z",
      "preview": "My landlord is keeping my security deposit...",
      "message_count": 8
    },
    {
      "id": "conv_def456",
      "legal_area": "employment",
      "updated_at": "2026-03-20T09:12:00Z",
      "preview": "Can my employer change my schedule without notice?",
      "message_count": 4
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### GET /api/conversations/{conversation_id}

Load a specific conversation with its full message history.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | The conversation ID to retrieve. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| conversation | object | Full conversation object including all messages. |
| conversation.id | string | Conversation ID. |
| conversation.legal_area | string | Classified legal area. |
| conversation.messages | array | Ordered list of message objects with `role`, `content`, and `timestamp`. |
| conversation.created_at | string | ISO 8601 timestamp of conversation creation. |
| conversation.updated_at | string | ISO 8601 timestamp of last activity. |

**Example Request:**

```bash
curl http://localhost:8000/api/conversations/conv_abc123 \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "conversation": {
    "id": "conv_abc123",
    "legal_area": "landlord_tenant",
    "messages": [
      {
        "role": "user",
        "content": "My landlord is keeping my security deposit",
        "timestamp": "2026-03-28T16:40:00Z"
      },
      {
        "role": "assistant",
        "content": "Based on your situation in Massachusetts...",
        "timestamp": "2026-03-28T16:40:05Z"
      }
    ],
    "created_at": "2026-03-28T16:40:00Z",
    "updated_at": "2026-03-28T16:45:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Conversation not found or does not belong to the authenticated user |

---

### DELETE /api/conversations/{conversation_id}

Permanently delete a conversation and all its messages.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | The conversation ID to delete. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always `"deleted"` on success. |

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/api/conversations/conv_abc123 \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "status": "deleted"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Conversation not found or does not belong to the authenticated user |

---

## Actions

All action endpoints require a paid subscription and generate AI-powered legal documents personalized to the user's profile.

### POST /api/actions/letter

Generate a demand letter based on the user's legal profile and the provided context. The letter is pre-filled with the user's facts, cites relevant statutes for their state, and is formatted ready to send.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** 5 requests / 60 seconds.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| context | string | Yes | Description of the situation the letter addresses. Maximum 5,000 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| letter | object | The generated demand letter. |
| letter.text | string | Full text of the demand letter. |
| letter.citations | array of strings | Statutes cited in the letter (e.g., `"M.G.L. c.186 §15B"`). |
| letter.recipient | string | Identified recipient of the letter. |
| letter.subject | string | Subject line for the letter. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/actions/letter \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Landlord withheld $800 security deposit claiming bathroom tile damage. No move-in inspection was conducted. I have photos showing pre-existing water damage."
  }'
```

**Example Response:**

```json
{
  "letter": {
    "text": "Dear [Landlord Name],\n\nI am writing regarding the security deposit of $800 that you have withheld from my tenancy at [Address]...\n\nPursuant to Massachusetts General Laws Chapter 186, Section 15B, a landlord is required to...\n\nI hereby demand the return of my full security deposit of $800 plus statutory damages...",
    "citations": [
      "M.G.L. c.186 §15B",
      "M.G.L. c.93A §9"
    ],
    "recipient": "Landlord",
    "subject": "Demand for Return of Security Deposit"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 404 | User profile not found |
| 429 | Rate limit exceeded |
| 500 | AI provider error |

---

### POST /api/actions/rights

Generate a rights summary specific to the user's state and legal situation. Explains what the user is entitled to in plain language.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** 5 requests / 60 seconds.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| context | string | Yes | Description of the situation to assess rights for. Maximum 5,000 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| rights | object | The generated rights summary. |
| rights.text | string | Full narrative of the user's rights in this situation. |
| rights.key_rights | array of strings | Bullet-point list of specific rights that apply. |
| rights.applicable_laws | array of strings | Statutes and regulations that govern this situation. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/actions/rights \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "My employer is requiring me to work overtime without extra pay. I am classified as a non-exempt W2 employee."
  }'
```

**Example Response:**

```json
{
  "rights": {
    "text": "As a non-exempt W2 employee in Massachusetts, you have strong protections under both federal and state overtime laws...",
    "key_rights": [
      "You must be paid 1.5x your regular rate for all hours over 40 per week",
      "Your employer cannot waive your right to overtime through any agreement",
      "You can file a complaint with the MA Attorney General's Fair Labor Division",
      "You may recover up to 3x unpaid wages (treble damages) under M.G.L. c.149 §150"
    ],
    "applicable_laws": [
      "Fair Labor Standards Act (FLSA) 29 U.S.C. §207",
      "M.G.L. c.151 §1A",
      "M.G.L. c.149 §150"
    ]
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 404 | User profile not found |
| 429 | Rate limit exceeded |
| 500 | AI provider error |

---

### POST /api/actions/checklist

Generate a prioritized next-steps checklist with deadlines. Tells the user exactly what to do and in what order.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** 5 requests / 60 seconds.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| context | string | Yes | Description of the situation to generate steps for. Maximum 5,000 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| checklist | object | The generated checklist. |
| checklist.items | array of strings | Ordered list of action items. |
| checklist.deadlines | array of strings or nulls | Corresponding deadline for each item (`null` if no deadline applies). ISO 8601 date format. |
| checklist.priority_order | array of integers | Indices of `items` sorted by priority (most urgent first). |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/actions/checklist \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "I need to dispute my security deposit deduction. Lease ended March 1."
  }'
```

**Example Response:**

```json
{
  "checklist": {
    "items": [
      "Send written demand letter to landlord via certified mail",
      "File complaint with MA Attorney General if no response in 14 days",
      "File small claims court case if deposit not returned within 30 days",
      "Gather all evidence: move-in photos, lease, communication records"
    ],
    "deadlines": [
      "2026-04-01",
      "2026-04-15",
      "2026-04-30",
      null
    ],
    "priority_order": [3, 0, 1, 2]
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 404 | User profile not found |
| 429 | Rate limit exceeded |
| 500 | AI provider error |

---

## Documents

### POST /api/documents

Upload a legal document (PDF, text file, or image) for analysis. CaseMate extracts text, identifies the document type, pulls out key legal facts, flags potential red flags, and injects discovered facts into the user's profile.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** 3 requests / 60 seconds.

**Request Body:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | The document to upload. Maximum 25 MB. Supported types: PDF, plain text, PNG, JPG, JPEG. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| document_type | string | Identified document type (e.g., `"lease agreement"`, `"eviction notice"`, `"pay stub"`). |
| key_facts | array of strings | Legal facts extracted from the document. |
| red_flags | array of strings | Potential issues or concerning clauses found. |
| summary | string | Plain-language summary of the document. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/documents \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -F "file=@lease_agreement.pdf"
```

**Example Response:**

```json
{
  "document_type": "lease agreement",
  "key_facts": [
    "Lease is month-to-month with no fixed end date",
    "Security deposit of $1,600 collected",
    "Landlord responsible for all structural repairs",
    "30-day written notice required for termination"
  ],
  "red_flags": [
    "Clause 14 waives tenant's right to jury trial — may be unenforceable in MA",
    "No mention of move-in condition inspection — required under M.G.L. c.186 §15B",
    "Late fee of $150 exceeds typical MA court-approved amounts"
  ],
  "summary": "Month-to-month residential lease for a one-bedroom apartment. Standard terms with some clauses that may not hold up under Massachusetts tenant protection laws."
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 400 | Unsupported file type (only PDF, text, PNG, JPG, JPEG accepted) |
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 404 | User profile not found |
| 413 | File exceeds 25 MB limit |
| 429 | Rate limit exceeded |
| 500 | AI provider or text extraction error |

---

## Deadlines

### POST /api/deadlines

Create a legal deadline manually. Deadlines can also be auto-detected from chat conversations.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Description of the deadline. Maximum 500 characters. |
| date | string | Yes | Deadline date in ISO 8601 format (`YYYY-MM-DD`). |
| legal_area | string or null | No | Associated legal area (e.g., `"landlord_tenant"`). |
| notes | string | No | Additional context or instructions. Maximum 2,000 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| deadline | object | The created deadline object. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/deadlines \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "File small claims court case for security deposit",
    "date": "2026-04-30",
    "legal_area": "landlord_tenant",
    "notes": "Must file within 30 days of demand letter. Courthouse: Boston Municipal Court."
  }'
```

**Example Response:**

```json
{
  "deadline": {
    "id": "dl_x1y2z3",
    "title": "File small claims court case for security deposit",
    "date": "2026-04-30",
    "legal_area": "landlord_tenant",
    "status": "active",
    "notes": "Must file within 30 days of demand letter. Courthouse: Boston Municipal Court.",
    "created_at": "2026-03-29T14:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 422 | Validation error (missing title or date, invalid date format) |

---

### GET /api/deadlines

List all deadlines for the authenticated user.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No parameters.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| deadlines | array | List of deadline objects. |
| deadlines[].id | string | Deadline ID. |
| deadlines[].title | string | Deadline description. |
| deadlines[].date | string | Deadline date (`YYYY-MM-DD`). |
| deadlines[].legal_area | string or null | Associated legal area. |
| deadlines[].status | string | One of: `active`, `completed`, `dismissed`, `expired`. |
| deadlines[].notes | string | Additional context. |
| deadlines[].created_at | string | ISO 8601 creation timestamp. |

**Example Request:**

```bash
curl http://localhost:8000/api/deadlines \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "deadlines": [
    {
      "id": "dl_x1y2z3",
      "title": "File small claims court case for security deposit",
      "date": "2026-04-30",
      "legal_area": "landlord_tenant",
      "status": "active",
      "notes": "Must file within 30 days of demand letter.",
      "created_at": "2026-03-29T14:00:00Z"
    },
    {
      "id": "dl_a4b5c6",
      "title": "Respond to landlord's counterclaim",
      "date": "2026-04-15",
      "legal_area": "landlord_tenant",
      "status": "active",
      "notes": null,
      "created_at": "2026-03-25T10:30:00Z"
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### PATCH /api/deadlines/{deadline_id}

Update a deadline's title, date, status, or notes.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| deadline_id | string | Yes | The deadline ID to update. |

**Request Body (all fields optional):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | No | Updated title. Maximum 500 characters. |
| date | string | No | Updated date (`YYYY-MM-DD`). |
| status | string | No | New status. One of: `active`, `completed`, `dismissed`, `expired`. |
| notes | string | No | Updated notes. Maximum 2,000 characters. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| deadline | object | The updated deadline object. |

**Example Request:**

```bash
curl -X PATCH http://localhost:8000/api/deadlines/dl_x1y2z3 \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "notes": "Filed on April 28. Case number: 2026-SC-1234."
  }'
```

**Example Response:**

```json
{
  "deadline": {
    "id": "dl_x1y2z3",
    "title": "File small claims court case for security deposit",
    "date": "2026-04-30",
    "legal_area": "landlord_tenant",
    "status": "completed",
    "notes": "Filed on April 28. Case number: 2026-SC-1234.",
    "created_at": "2026-03-29T14:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Deadline not found or does not belong to the authenticated user |
| 422 | Validation error (invalid status value) |

---

### DELETE /api/deadlines/{deadline_id}

Permanently delete a deadline.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| deadline_id | string | Yes | The deadline ID to delete. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always `"deleted"` on success. |

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/api/deadlines/dl_x1y2z3 \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "status": "deleted"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Deadline not found or does not belong to the authenticated user |

---

## Rights Library

### GET /api/rights/domains

List all legal domains that have rights guides available.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No parameters.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| domains | array | List of legal domain objects. |
| domains[].id | string | Domain identifier (e.g., `"landlord_tenant"`). |
| domains[].name | string | Human-readable domain name (e.g., `"Landlord & Tenant"`). |
| domains[].description | string | Brief description of the domain. |
| domains[].guide_count | integer | Number of guides available in this domain. |

**Example Request:**

```bash
curl http://localhost:8000/api/rights/domains \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "domains": [
    {
      "id": "landlord_tenant",
      "name": "Landlord & Tenant",
      "description": "Security deposits, evictions, repairs, lease rights",
      "guide_count": 4
    },
    {
      "id": "employment",
      "name": "Employment",
      "description": "Wages, overtime, discrimination, wrongful termination",
      "guide_count": 3
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### GET /api/rights/guides

List all available rights guides. Optionally filter by legal domain.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | No | Filter guides by legal domain ID (e.g., `"landlord_tenant"`). |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| guides | array | List of guide summary objects. |
| guides[].id | string | Guide ID. |
| guides[].title | string | Guide title. |
| guides[].domain | string | Legal domain this guide belongs to. |
| guides[].description | string | Brief description of the guide's content. |

**Example Request:**

```bash
curl "http://localhost:8000/api/rights/guides?domain=landlord_tenant" \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "guides": [
    {
      "id": "security-deposit-rights",
      "title": "Your Security Deposit Rights",
      "domain": "landlord_tenant",
      "description": "What your landlord must do with your deposit and your remedies when they don't."
    },
    {
      "id": "eviction-defense",
      "title": "Defending Against Eviction",
      "domain": "landlord_tenant",
      "description": "Your rights when facing eviction, required notice periods, and legal defenses."
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### GET /api/rights/guides/{guide_id}

Get the full content of a specific rights guide, including rights, action steps, deadlines, and common mistakes.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| guide_id | string | Yes | The guide ID to retrieve. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| guide | object | Full rights guide object. |
| guide.id | string | Guide ID. |
| guide.title | string | Guide title. |
| guide.domain | string | Legal domain. |
| guide.description | string | Guide description. |
| guide.rights | array of strings | List of specific rights explained in plain language. |
| guide.action_steps | array of strings | Recommended steps the user should take. |
| guide.deadlines | array of strings | Key deadlines or time limits to be aware of. |
| guide.common_mistakes | array of strings | Mistakes people frequently make in this situation. |

**Example Request:**

```bash
curl http://localhost:8000/api/rights/guides/security-deposit-rights \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "guide": {
    "id": "security-deposit-rights",
    "title": "Your Security Deposit Rights",
    "domain": "landlord_tenant",
    "description": "What your landlord must do with your deposit and your remedies when they don't.",
    "rights": [
      "Your landlord must hold your deposit in a separate, interest-bearing account",
      "You must receive a receipt with the bank name and account number within 30 days",
      "Your landlord must return your deposit within 30 days of lease termination",
      "Any deductions must be itemized in writing with actual repair costs"
    ],
    "action_steps": [
      "Request your deposit receipt if you never received one",
      "Document the condition of your unit with photos before moving out",
      "Send a written demand letter if your deposit is not returned within 30 days",
      "File in small claims court if demand letter goes unanswered"
    ],
    "deadlines": [
      "30 days after move-out: landlord must return deposit or provide itemized deductions",
      "3 years: statute of limitations for security deposit claims in most states"
    ],
    "common_mistakes": [
      "Accepting a verbal promise that the deposit will be returned later",
      "Not documenting the unit's condition at move-in and move-out",
      "Waiting too long to send a demand letter"
    ]
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Guide not found |

---

## Workflows

### GET /api/workflows/templates

List available workflow templates. Each template is a step-by-step guided process for a common legal task.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | No | Filter templates by legal domain (e.g., `"landlord_tenant"`). |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| templates | array | List of workflow template objects. |
| templates[].id | string | Template ID (e.g., `"eviction-defense"`). |
| templates[].title | string | Template title. |
| templates[].description | string | What this workflow helps the user accomplish. |
| templates[].domain | string | Legal domain. |
| templates[].estimated_time | string | Estimated completion time (e.g., `"2-3 hours"`). |
| templates[].steps | array | List of step objects with `title` and `description`. |

**Example Request:**

```bash
curl "http://localhost:8000/api/workflows/templates?domain=landlord_tenant" \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "templates": [
    {
      "id": "security-deposit-recovery",
      "title": "Recover Your Security Deposit",
      "description": "Step-by-step guide to getting your security deposit back when your landlord won't return it.",
      "domain": "landlord_tenant",
      "estimated_time": "1-2 weeks",
      "steps": [
        {"title": "Document everything", "description": "Gather photos, lease, and communication records."},
        {"title": "Send demand letter", "description": "Generate and mail a formal demand letter."},
        {"title": "File small claims", "description": "If no response, file in small claims court."},
        {"title": "Prepare for hearing", "description": "Organize evidence and prepare your statement."}
      ]
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### POST /api/workflows

Start a new workflow from a template.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | string | Yes | The template ID to instantiate (e.g., `"eviction-defense"`). |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| workflow | object | The created workflow instance. |
| workflow.id | string | Workflow instance ID. |
| workflow.title | string | Workflow title (from template). |
| workflow.domain | string | Legal domain. |
| workflow.steps | array | Steps with `title`, `description`, and `status` (`pending`, `in_progress`, `completed`). |
| workflow.current_step | integer | Index of the current active step. |
| workflow.status | string | Overall status: `in_progress` or `completed`. |
| workflow.started_at | string | ISO 8601 timestamp. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{"template_id": "security-deposit-recovery"}'
```

**Example Response:**

```json
{
  "workflow": {
    "id": "wf_m1n2o3",
    "title": "Recover Your Security Deposit",
    "domain": "landlord_tenant",
    "steps": [
      {"title": "Document everything", "description": "Gather photos, lease, and communication records.", "status": "pending"},
      {"title": "Send demand letter", "description": "Generate and mail a formal demand letter.", "status": "pending"},
      {"title": "File small claims", "description": "If no response, file in small claims court.", "status": "pending"},
      {"title": "Prepare for hearing", "description": "Organize evidence and prepare your statement.", "status": "pending"}
    ],
    "current_step": 0,
    "status": "in_progress",
    "started_at": "2026-03-29T15:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Template not found |

---

### GET /api/workflows

List the authenticated user's active and completed workflows.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No parameters.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| workflows | array | List of workflow summary objects. |
| workflows[].id | string | Workflow instance ID. |
| workflows[].title | string | Workflow title. |
| workflows[].domain | string | Legal domain. |
| workflows[].current_step | integer | Index of the current step. |
| workflows[].status | string | `in_progress` or `completed`. |
| workflows[].started_at | string | ISO 8601 timestamp. |

**Example Request:**

```bash
curl http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "workflows": [
    {
      "id": "wf_m1n2o3",
      "title": "Recover Your Security Deposit",
      "domain": "landlord_tenant",
      "current_step": 1,
      "status": "in_progress",
      "started_at": "2026-03-29T15:00:00Z"
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### GET /api/workflows/{workflow_id}

Get the full details of a specific workflow instance, including all step statuses.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| workflow_id | string | Yes | The workflow instance ID. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| workflow | object | Full workflow instance with all steps and statuses. |

**Example Request:**

```bash
curl http://localhost:8000/api/workflows/wf_m1n2o3 \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "workflow": {
    "id": "wf_m1n2o3",
    "title": "Recover Your Security Deposit",
    "domain": "landlord_tenant",
    "steps": [
      {"title": "Document everything", "description": "Gather photos, lease, and communication records.", "status": "completed"},
      {"title": "Send demand letter", "description": "Generate and mail a formal demand letter.", "status": "in_progress"},
      {"title": "File small claims", "description": "If no response, file in small claims court.", "status": "pending"},
      {"title": "Prepare for hearing", "description": "Organize evidence and prepare your statement.", "status": "pending"}
    ],
    "current_step": 1,
    "status": "in_progress",
    "started_at": "2026-03-29T15:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Workflow not found or does not belong to the authenticated user |

---

### PATCH /api/workflows/{workflow_id}/steps

Update the status of a specific step in a workflow.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Path Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| workflow_id | string | Yes | The workflow instance ID. |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| step_index | integer | Yes | Zero-based index of the step to update. |
| status | string | Yes | New status: `completed`. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| workflow | object | The updated workflow instance. `current_step` advances automatically when a step is completed. |

**Example Request:**

```bash
curl -X PATCH http://localhost:8000/api/workflows/wf_m1n2o3/steps \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{"step_index": 0, "status": "completed"}'
```

**Example Response:**

```json
{
  "workflow": {
    "id": "wf_m1n2o3",
    "title": "Recover Your Security Deposit",
    "domain": "landlord_tenant",
    "steps": [
      {"title": "Document everything", "description": "Gather photos, lease, and communication records.", "status": "completed"},
      {"title": "Send demand letter", "description": "Generate and mail a formal demand letter.", "status": "pending"},
      {"title": "File small claims", "description": "If no response, file in small claims court.", "status": "pending"},
      {"title": "Prepare for hearing", "description": "Organize evidence and prepare your statement.", "status": "pending"}
    ],
    "current_step": 1,
    "status": "in_progress",
    "started_at": "2026-03-29T15:00:00Z"
  }
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 404 | Workflow not found or does not belong to the authenticated user |
| 422 | Invalid step index or status value |

---

## Export

### POST /api/export/document

Generate a PDF from a previously generated action (letter, rights summary, checklist, or custom content). Returns the PDF as a binary download.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Document type: `"letter"`, `"rights"`, `"checklist"`, or `"custom"`. |
| content | object | Yes | Type-specific content fields (the output from an action endpoint). |

**Response:** Binary PDF file with `Content-Disposition: attachment; filename="casemate-<type>.pdf"` header.

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/export/document \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "letter",
    "content": {
      "text": "Dear Landlord,\n\nPursuant to M.G.L. c.186 §15B...",
      "citations": ["M.G.L. c.186 §15B"],
      "recipient": "John Smith, Property Manager",
      "subject": "Demand for Return of Security Deposit"
    }
  }' \
  --output demand_letter.pdf
```

**Example Response:** Binary PDF data (save to file with `--output` or `-o`).

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 422 | Invalid type or missing required content fields |

---

### POST /api/export/email

Generate a PDF and email it to the specified address.

**Authentication:** JWT Bearer token (subscription gate).

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Document type: `"letter"`, `"rights"`, `"checklist"`, or `"custom"`. |
| content | object | Yes | Type-specific content fields (same as `/api/export/document`). |
| email | string | Yes | Email address to send the PDF to. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | `"sent"` on success. |
| email | string | The email address the document was sent to. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/export/email \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "letter",
    "content": {
      "text": "Dear Landlord,\n\nPursuant to M.G.L. c.186 §15B...",
      "citations": ["M.G.L. c.186 §15B"],
      "recipient": "John Smith, Property Manager",
      "subject": "Demand for Return of Security Deposit"
    },
    "email": "sarah.chen@example.com"
  }'
```

**Example Response:**

```json
{
  "status": "sent",
  "email": "sarah.chen@example.com"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 402 | No active subscription |
| 422 | Invalid email address or missing required content fields |
| 500 | Email delivery failure (SMTP error) |

---

## Attorney Referrals

### GET /api/attorneys/search

Search for attorney referrals by state and optionally by legal area. Returns matched attorneys with relevance scoring and match reasoning.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| state | string | Yes | Two-letter US state code (e.g., `"MA"`). |
| legal_area | string | No | Legal domain to filter by (e.g., `"landlord_tenant"`, `"employment"`). |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| suggestions | array | List of attorney suggestion objects. |
| suggestions[].attorney | object | Attorney details. |
| suggestions[].attorney.name | string | Attorney's full name. |
| suggestions[].attorney.specializations | array of strings | Legal areas the attorney practices. |
| suggestions[].attorney.rating | number | Rating score (0.0 - 5.0). |
| suggestions[].attorney.cost_range | string | Typical fee range (e.g., `"$150-250/hr"`). |
| suggestions[].attorney.phone | string | Contact phone number. |
| suggestions[].attorney.email | string | Contact email. |
| suggestions[].attorney.website | string | Attorney's website URL. |
| suggestions[].attorney.bio | string | Brief professional biography. |
| suggestions[].match_reason | string | Why this attorney was suggested for the user's situation. |
| suggestions[].relevance_score | number | Relevance score (0.0 - 1.0). |

**Example Request:**

```bash
curl "http://localhost:8000/api/attorneys/search?state=MA&legal_area=landlord_tenant" \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "suggestions": [
    {
      "attorney": {
        "name": "Maria Rodriguez, Esq.",
        "specializations": ["landlord_tenant", "consumer"],
        "rating": 4.8,
        "cost_range": "$200-300/hr",
        "phone": "(617) 555-0142",
        "email": "mrodriguez@example-law.com",
        "website": "https://example-law.com",
        "bio": "15 years practicing tenant rights law in Massachusetts. Former staff attorney at Greater Boston Legal Services."
      },
      "match_reason": "Specializes in security deposit disputes in Massachusetts with a strong track record in small claims court.",
      "relevance_score": 0.94
    }
  ]
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 422 | Missing required `state` parameter or invalid state code |

---

## Payments

### POST /api/payments/create-checkout-session

Create a Stripe checkout session to start a subscription. Returns a URL that the frontend redirects the user to for payment.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| price_id | string | Yes | Stripe price ID for the subscription plan (e.g., `"price_xxx"`). |
| success_url | string | Yes | URL to redirect to after successful payment. |
| cancel_url | string | Yes | URL to redirect to if the user cancels checkout. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Stripe checkout session ID (e.g., `"cs_xxx"`). |
| url | string | Stripe-hosted checkout page URL. Redirect the user here. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/payments/create-checkout-session \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "price_id": "price_1Abc2DefGhIjKl",
    "success_url": "https://casemate.app/dashboard?session_id={CHECKOUT_SESSION_ID}",
    "cancel_url": "https://casemate.app/pricing"
  }'
```

**Example Response:**

```json
{
  "session_id": "cs_test_a1b2c3d4e5f6",
  "url": "https://checkout.stripe.com/c/pay/cs_test_a1b2c3d4e5f6"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |
| 400 | Invalid price ID or malformed URLs |

---

### POST /api/payments/webhook

Handle incoming Stripe webhook events. This endpoint is called by Stripe, not by frontend code. It verifies the `Stripe-Signature` header against your webhook signing secret and processes subscription lifecycle events.

**Authentication:** Stripe signature verification (not JWT). The `stripe-signature` header is validated against the `STRIPE_WEBHOOK_SECRET` environment variable.

**Rate Limit:** None.

**Handled Events:**

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Activates the user's subscription in the database. |
| `customer.subscription.updated` | Updates subscription status (e.g., plan change). |
| `customer.subscription.deleted` | Deactivates the subscription. |
| `invoice.paid` | Records successful payment. |
| `invoice.payment_failed` | Flags payment failure for follow-up. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always `"ok"` on successful processing. |

**Example Request (sent by Stripe, not called manually):**

```bash
curl -X POST http://localhost:8000/api/payments/webhook \
  -H "stripe-signature: t=1234567890,v1=abc123..." \
  -H "Content-Type: application/json" \
  -d '{"type": "checkout.session.completed", "data": {...}}'
```

**Example Response:**

```json
{
  "status": "ok"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 400 | Invalid or missing Stripe signature |

---

### GET /api/payments/subscription

Get the authenticated user's current subscription status.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No parameters.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | The authenticated user's ID. |
| is_active | boolean | Whether the subscription is currently active. |
| stripe_subscription_id | string | Stripe subscription ID (e.g., `"sub_xxx"`). |
| status | string | Stripe status: `active`, `past_due`, `canceled`, `trialing`, etc. |
| current_period_end | string | ISO 8601 timestamp of when the current billing period ends. |

**Example Request:**

```bash
curl http://localhost:8000/api/payments/subscription \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "user_id": "usr_a1b2c3d4",
  "is_active": true,
  "stripe_subscription_id": "sub_1Abc2DefGhIjKl",
  "status": "active",
  "current_period_end": "2026-04-29T00:00:00Z"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 401 | Missing or invalid JWT |

---

### POST /api/payments/cancel

Cancel the user's subscription. The subscription remains active until the end of the current billing period (cancel at period end). The user retains full access until then.

**Authentication:** JWT Bearer token.

**Rate Limit:** None.

**Request:** No body required.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | The authenticated user's ID. |
| is_active | boolean | `true` (still active until period end). |
| status | string | Stripe status after cancellation (usually `"active"` with cancel_at_period_end set). |
| current_period_end | string | ISO 8601 timestamp. Access continues until this date. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/payments/cancel \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

**Example Response:**

```json
{
  "user_id": "usr_a1b2c3d4",
  "is_active": true,
  "status": "active",
  "current_period_end": "2026-04-29T00:00:00Z"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 400 | No active subscription to cancel |
| 401 | Missing or invalid JWT |

---

## Waitlist

### POST /api/waitlist

Sign up for the CaseMate waitlist. No authentication required. Used on the marketing landing page before launch.

**Authentication:** None required.

**Rate Limit:** None.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email address to add to the waitlist. |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | `true` if the email was added to the waitlist. |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email": "interested_user@example.com"}'
```

**Example Response:**

```json
{
  "success": true
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 422 | Invalid email format |

---

## Appendix: Legal Area Identifiers

The `legal_area` field appears in chat responses, conversations, deadlines, and workflows. These are the valid values:

| Identifier | Description |
|------------|-------------|
| `landlord_tenant` | Security deposits, evictions, repairs, habitability, lease disputes |
| `employment` | Wages, overtime, discrimination, wrongful termination, workplace rights |
| `consumer` | Consumer protection, fraud, unfair business practices |
| `debt_collections` | Debt collection harassment, validation, statute of limitations |
| `small_claims` | Small claims court procedures, filing, limits |
| `contracts` | Contract disputes, breach, enforcement |
| `traffic` | Traffic violations, license issues, DUI/DWI |
| `family_law` | Divorce, custody, child support, domestic violence |
| `criminal_records` | Expungement, sealing records, background checks |
| `immigration` | Visa issues, work permits, naturalization |
