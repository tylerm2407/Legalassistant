# Actions — Generator System

> How CaseMate generates demand letters, rights summaries, and checklists using profile context + Claude.

---

## Overview

Action generators are CaseMate's "do something about it" feature. Instead of just answering questions, CaseMate produces ready-to-use legal documents personalized to the user's situation. Each generator follows the same pattern:

```
User's LegalProfile + Request Context + State Laws
        ↓
  Claude Prompt Assembly
        ↓
  claude-sonnet-4-20250514 (max_tokens=4096)
        ↓
  JSON Parse → Pydantic Model
        ↓
  Structured Output (letter / rights / checklist)
```

All three generators are decorated with `@retry_anthropic` (3 retries, exponential backoff) and are rate-limited to **5 requests/minute** per user.

---

## Demand Letter Generator

**Source:** `backend/actions/letter_generator.py` → `generate_demand_letter()`

```python
async def generate_demand_letter(profile: LegalProfile, context: str) -> DemandLetter:
```

### How it works

1. Classifies the legal area from the context string
2. Looks up state-specific statutes from `STATE_LAWS[profile.state][legal_area]`
3. Adds federal default statutes from `STATE_LAWS["federal_defaults"][legal_area]`
4. Builds a prompt that includes the user's full profile, active issues, legal facts, and the specific demand context
5. Instructs Claude to return JSON with `text`, `citations`, `recipient`, and `subject`
6. Parses the JSON response into a `DemandLetter` model

### Output Model

```python
class DemandLetter(BaseModel):
    text: str           # Full letter body, ready to print/send
    citations: list[str] # Statute citations used (e.g., "M.G.L. c.186 §15B")
    recipient: str       # Who the letter is addressed to
    subject: str         # Letter subject line
```

### Example Output (Sarah Chen Demo)

```
Subject: Demand for Return of Security Deposit — 123 Main St, Apt 4B

Dear [Landlord Name],

I am writing regarding the security deposit of $1,600 paid on January 15, 2025
for the property at 123 Main St, Apt 4B, Boston, MA 02101.

Under Massachusetts General Laws Chapter 186, Section 15B, a landlord must:
1. Hold the deposit in a separate, interest-bearing account
2. Provide a receipt within 30 days
3. Conduct a written statement of condition at move-in

You did not conduct a move-in inspection as required by M.G.L. c.186 §15B(1).
Under this statute, your failure to document pre-existing conditions means you
cannot make deductions for any damage...

Citations: M.G.L. c.186 §15B, M.G.L. c.93A §9
```

---

## Rights Summary Generator

**Source:** `backend/actions/rights_generator.py` → `generate_rights_summary()`

```python
async def generate_rights_summary(profile: LegalProfile, context: str) -> RightsSummary:
```

### How it works

Same injection pattern as the demand letter. Builds a prompt asking Claude to explain the user's specific rights given their state, situation, and legal facts. Returns a structured summary rather than a letter.

### Output Model

```python
class RightsSummary(BaseModel):
    text: str                # 3-5 paragraph explanation of rights
    key_rights: list[str]    # 5-8 bullet points of specific rights
    applicable_laws: list[str] # Statute citations that apply
```

---

## Checklist Generator

**Source:** `backend/actions/checklist_generator.py` → `generate_checklist()`

```python
async def generate_checklist(profile: LegalProfile, context: str) -> Checklist:
```

### How it works

Generates an ordered action plan with deadlines. Claude returns items, parallel deadline array, and priority ordering.

### Output Model

```python
class Checklist(BaseModel):
    items: list[str]          # Action items in logical order
    deadlines: list[str | None]  # Parallel array — deadline per item (or None)
    priority_order: list[int]    # Indices sorted by urgency (most urgent first)
```

### Validation

- `deadlines` array is padded with `None` if shorter than `items` to ensure parallel alignment
- `priority_order` indices are validated to be within bounds of `items`
- Raises `RuntimeError` if Claude returns unparseable JSON

---

## API Endpoints

| Method | Path | Auth | Rate Limit | Request Body | Response |
|--------|------|------|------------|--------------|----------|
| `POST` | `/api/actions/letter` | JWT | 5/min | `{"context": "..."}` | `DemandLetter` |
| `POST` | `/api/actions/rights` | JWT | 5/min | `{"context": "..."}` | `RightsSummary` |
| `POST` | `/api/actions/checklist` | JWT | 5/min | `{"context": "..."}` | `Checklist` |

All endpoints read the user's `LegalProfile` from Supabase using the authenticated `user_id`, then pass it to the generator along with the `context` string from the request body.

---

## How State Laws Are Injected

Each generator follows this lookup pattern:

```python
legal_area = classify_legal_area(context)
state_context = STATE_LAWS.get(profile.state, {}).get(legal_area, "")
federal_context = STATE_LAWS.get("federal_defaults", {}).get(legal_area, "")
```

Both state-specific and federal statutes are included in the generation prompt, ensuring the output cites real, applicable law.

---

## How to Add a New Action Type

1. Create `backend/actions/new_generator.py` with an async generator function
2. Define the output Pydantic model in `backend/models/action_output.py`
3. Add the API endpoint in `backend/main.py` with JWT auth and rate limiting
4. Add the UI trigger in `web/components/ActionGenerator.tsx`
5. Write tests in `tests/test_action_generators.py`

---

## Related

- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — How the profile is injected into prompts
- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — State law lookup system
- [EXPORT.md](EXPORT.md) — PDF generation and email delivery of action outputs
- [API.md](API.md) — Full API reference
- [MODELS.md](MODELS.md) — All Pydantic models
