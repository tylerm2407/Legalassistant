# Legal Knowledge Base — State Laws & Legal Content Guide

> How CaseMate organizes and injects 50-state legal knowledge across 10 domains.

---

## Overview

CaseMate's legal knowledge base is the structured content that makes personalized legal guidance possible. It consists of:

1. **50-state statute database** — Real legal citations organized by state and domain
2. **10 legal domain modules** — Domain-specific guidance, key statutes, and common questions
3. **Legal area classifier** — Deterministic keyword matching to route questions to the right domain
4. **Federal defaults** — Federal-level statutes that apply nationwide

All of this content is injected into Claude's system prompt via the [memory injector](MEMORY_SYSTEM.md).

---

## Regional Organization

**Source:** `backend/legal/states/`

State laws are organized geographically into 6 regional files:

| File | States | Count |
|------|--------|-------|
| `northeast.py` | MA, NY, CT, NJ, PA, ME, NH, VT, RI | 9 |
| `southeast.py` | FL, GA, VA, NC, SC, AL, MS, TN, KY, WV, MD, DE, LA, AR | 14 |
| `midwest.py` | IL, OH, MI, IN, WI, MN, IA, MO, KS, NE, ND, SD | 12 |
| `south_central.py` | TX, OK | 2 |
| `west.py` | CA, WA, OR, CO, AZ, NV, UT, NM, ID, MT, WY, HI, AK | 13 |
| `federal.py` | Federal-level defaults | — |

**Total:** 50 states + federal defaults

### Data Structure

All regional files export into a single `STATE_LAWS` dictionary:

```python
STATE_LAWS: dict[str, dict[str, str]]

# Usage:
STATE_LAWS["MA"]["landlord_tenant"]
# → "Massachusetts General Laws Chapter 186, Section 15B governs security deposits..."

STATE_LAWS["federal_defaults"]["employment_rights"]
# → "The Fair Labor Standards Act (FLSA) establishes minimum wage..."
```

Each state entry maps legal domains to statute text with **real citations** — not vague summaries.

### Aggregation

**Source:** `backend/legal/state_laws.py`

Simple re-export that merges all regional dictionaries:

```python
from backend.legal.states import STATE_LAWS
```

---

## The 10 Legal Domains

**Source:** `backend/legal/areas/`

Each domain has a dedicated module exporting three items:

| Export | Type | Description |
|--------|------|-------------|
| `DOMAIN_GUIDANCE` | `str` | Prompt fragment injected when this domain is detected |
| `KEY_STATUTES` | `dict[str, str]` | Statute citation → plain-English explanation |
| `COMMON_QUESTIONS` | `list[str]` | Representative questions users ask in this domain |

### Domain Inventory

| # | Domain Key | Module | Description |
|---|-----------|--------|-------------|
| 1 | `landlord_tenant` | `areas/landlord_tenant.py` | Security deposits, evictions, habitability, lease disputes |
| 2 | `employment_rights` | `areas/employment.py` | Wrongful termination, wage theft, discrimination, FMLA |
| 3 | `consumer_protection` | `areas/consumer.py` | Scams, refunds, warranties, lemon law, hidden fees |
| 4 | `debt_collections` | `areas/debt_collections.py` | Debt collectors, FDCPA, garnishment, credit reports |
| 5 | `small_claims` | `areas/small_claims.py` | Filing, damages, court procedures, service of process |
| 6 | `contract_disputes` | `areas/contracts.py` | Breach, non-competes, NDAs, termination clauses |
| 7 | `traffic_violations` | `areas/traffic.py` | Tickets, DUI/DWI, license suspension, traffic school |
| 8 | `family_law` | `areas/family_law.py` | Divorce, custody, child support, domestic violence |
| 9 | `criminal_records` | `areas/criminal_records.py` | Expungement, background checks, probation, bail |
| 10 | `immigration` | `areas/immigration.py` | Visas, green cards, asylum, DACA, work permits |

---

## Legal Area Classifier

**Source:** `backend/legal/classifier.py`

### Algorithm: Weighted Keyword Matching

The classifier uses deterministic keyword scoring — no LLM call for most questions.

```
User question (lowercased)
        ↓
  Score each domain's keywords against the question
        ↓
  Multi-word phrases get 3x boost (PHRASE_BOOST = 3)
  Single keywords get 1x weight
        ↓
  Highest scoring domain wins
        ↓
  If no matches → "general"
```

### Functions

#### `classify_legal_area(question: str) -> str`

Fast O(1) classification. Returns domain key string (e.g., `"landlord_tenant"`) or `"general"`.

#### `classify_with_confidence(question: str) -> ClassificationResult`

Returns detailed result:

```python
class ClassificationResult:
    domain: str          # e.g., "landlord_tenant"
    confidence: float    # 0.0 - 1.0
    method: str          # "keyword" or "llm"
    scores: dict         # All domain scores for debugging
```

Confidence is computed from:
- **Top score ratio:** How much of the question matched the winning domain
- **Separation factor:** How far ahead the winner is from the runner-up

#### `classify_with_llm_fallback(question: str) -> str`

Uses keyword classification first. If confidence < `CONFIDENCE_THRESHOLD` (0.4), falls back to Claude for classification (~2s latency).

### Keyword Examples

Each domain has 15-20 keywords. Multi-word phrases are more specific and receive the 3x boost:

| Domain | Sample Keywords |
|--------|----------------|
| `landlord_tenant` | landlord, eviction, security deposit, habitability, lease, rental, move-in inspection, notice to quit, rent increase, housing code |
| `employment_rights` | employer, fired, wrongful termination, discrimination, harassment, wage, overtime, minimum wage, retaliation, whistleblower, fmla, workers comp |
| `consumer_protection` | scam, fraud, refund, warranty, defective, lemon law, ftc, return policy, overcharge, billing error, hidden fee |
| `debt_collections` | debt collector, collection agency, creditor, garnishment, fdcpa, credit report, charge off, settlement, payment plan, repossession |

---

## How Injection Works

When a user sends a message:

1. `classify_legal_area(question)` determines the domain
2. `STATE_LAWS[profile.state][legal_area]` loads state-specific statutes
3. `STATE_LAWS["federal_defaults"][legal_area]` loads federal statutes
4. Both are injected into the system prompt (see [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md))

If a state doesn't have coverage for a specific domain, the federal defaults provide baseline guidance.

---

## How to Add a New State

1. Determine the regional file (`northeast.py`, `southeast.py`, etc.)
2. Add the state's 2-letter code with entries for all 10 legal domains:
   ```python
   "XX": {
       "landlord_tenant": "State XX Revised Statutes §XX-XX governs...",
       "employment_rights": "...",
       # ... all 10 domains
   }
   ```
3. Include **real statute citations** — not vague summaries
4. Update tests in `tests/test_legal_classifier.py` to verify the new state

---

## How to Add a New Legal Domain

1. **Classifier keywords:** Add a new entry in `backend/legal/classifier.py` → `DOMAIN_KEYWORDS`
2. **Domain module:** Create `backend/legal/areas/new_domain.py` exporting `DOMAIN_GUIDANCE`, `KEY_STATUTES`, `COMMON_QUESTIONS`
3. **State law entries:** Add the new domain key to every state in all 6 regional files + `federal.py`
4. **Rights guides:** Create guides in `backend/knowledge/rights_library.py` (see [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md))
5. **Update tests:** Add classifier tests and verify prompt injection includes the new domain

---

## How to Update Statute Citations

Laws change. When updating citations:

1. Find the state in the appropriate regional file
2. Update the statute text for the affected domain
3. Update `KEY_STATUTES` in the corresponding area module if the statute is listed there
4. Run `make test` to ensure no tests break from the change
5. Note the update in the commit message: `fix(legal): update MA security deposit statute citation`

---

## Related

- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — How state laws are injected into prompts
- [LEGAL_DOMAINS.md](LEGAL_DOMAINS.md) — Domain-level detail and coverage matrix
- [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md) — Pre-built rights guides per domain
- [EXTENDING.md](EXTENDING.md) — Full guide to extending CaseMate
- ADR 002 — State-specific legal context design decision
