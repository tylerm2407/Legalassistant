# Rights Library — Know Your Rights Guides

> 19 pre-built, structured legal guides covering the most common situations users face.

---

## Overview

The Rights Library is a collection of **static, pre-built guides** that give users immediate answers to common legal questions without requiring a Claude API call. Unlike chat responses (which are dynamic and personalized), rights guides are reference material — structured, comprehensive, and always available.

**Source:** `backend/knowledge/rights_library.py`

---

## RightsGuide Model

```python
class RightsGuide(BaseModel):
    id: str                       # Unique identifier (e.g., "tenant_security_deposit")
    domain: str                   # Legal domain key (e.g., "landlord_tenant")
    title: str                    # Display title
    description: str              # One-line summary
    explanation: str              # Plain-English overview (2-3 paragraphs)
    your_rights: list[str]        # Specific rights as bullet points
    action_steps: list[str]       # Ordered steps to take
    deadlines: list[str]          # Time limits and filing windows
    common_mistakes: list[str]    # Pitfalls to avoid
    when_to_get_a_lawyer: str     # When professional help is recommended
```

---

## Full Guide Inventory

### Landlord & Tenant (3 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `tenant_eviction_defense` | Eviction Defense | Notice requirements, right to cure, court procedures, illegal lockout protections |
| `tenant_security_deposit` | Security Deposit Rights | Return deadlines, allowable deductions, itemized statement requirements, penalty damages |
| `tenant_habitability` | Habitability Standards | Required repairs, rent withholding rights, code violation reporting, constructive eviction |

### Employment (3 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `employment_wage_theft` | Wage Theft Recovery | Unpaid wages, overtime calculation, filing complaints with DOL, statute of limitations |
| `employment_wrongful_termination` | Wrongful Termination | At-will exceptions, retaliation protections, documentation, filing deadlines |
| `employment_discrimination` | Workplace Discrimination | Protected classes, EEOC filing, state agency complaints, burden of proof |

### Consumer Protection (2 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `consumer_refund_rights` | Refund & Return Rights | FTC cooling-off rule, state consumer protection acts, chargeback rights, complaint process |
| `consumer_lemon_law` | Lemon Law Basics | Qualification criteria, manufacturer notification, arbitration vs. lawsuit, state variations |

### Debt & Collections (3 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `consumer_debt_collection` | Debt Collection Defense | FDCPA protections, debt validation rights, cease-and-desist, statute of limitations on debt |
| `debt_bankruptcy_basics` | Bankruptcy Basics | Chapter 7 vs. 13, means test, exempt property, automatic stay, credit impact |
| `debt_garnishment` | Wage Garnishment Rights | Federal limits (25% disposable earnings), head-of-household exemption, objection process |

### Traffic (2 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `traffic_ticket_fight` | Fighting a Traffic Ticket | Court appearance, evidence gathering, negotiation, traffic school options, points impact |
| `traffic_dui_process` | DUI/DWI Process | Implied consent, field sobriety tests, license suspension, court process, penalties |

### Family Law (2 guides)

| ID | Title | Key Content |
|----|-------|-------------|
| `family_divorce_basics` | Divorce Basics | Filing requirements, residency rules, property division, mediation, uncontested vs. contested |
| `family_custody_basics` | Child Custody Rights | Legal vs. physical custody, best interest standard, modification, parenting plans |

### Criminal Records (1 guide)

| ID | Title | Key Content |
|----|-------|-------------|
| `criminal_expungement` | Record Expungement | Eligibility criteria, waiting periods, petition process, effect on background checks |

### Small Claims (1 guide)

| ID | Title | Key Content |
|----|-------|-------------|
| `small_claims_filing` | Filing in Small Claims Court | Dollar limits by state, filing fees, service of process, evidence preparation, judgment collection |

### Contracts (1 guide)

| ID | Title | Key Content |
|----|-------|-------------|
| `contract_breach` | Breach of Contract | Material vs. minor breach, remedies, statute of frauds, mitigation duty |

### Immigration (1 guide)

| ID | Title | Key Content |
|----|-------|-------------|
| `immigration_rights_overview` | Immigration Rights Overview | Constitutional protections, ICE encounter rights, detention rights, deportation defense |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/rights/domains` | JWT | List all domains that have guides |
| `GET` | `/api/rights/guides` | JWT | List all 19 guides (summary view) |
| `GET` | `/api/rights/guides?domain=landlord_tenant` | JWT | Filter guides by domain |
| `GET` | `/api/rights/guides/{id}` | JWT | Get a single guide by ID (full content) |

### Response format

List endpoint returns summary objects (id, domain, title, description).
Detail endpoint returns the full `RightsGuide` with all fields.

---

## Lookup Functions

```python
def get_all_guides() -> list[RightsGuide]:
    """Returns all 19 guides."""

def get_guide_by_id(guide_id: str) -> RightsGuide | None:
    """Returns a single guide by ID, or None if not found."""

def get_guides_by_domain(domain: str) -> list[RightsGuide]:
    """Returns all guides for a legal domain (e.g., 'landlord_tenant' → 3 guides)."""
```

---

## Guides vs. Chat Responses

| Aspect | Rights Guides | Chat Responses |
|--------|--------------|----------------|
| Content | Static, pre-built | Dynamic, generated per question |
| Personalization | None (generic) | Full (profile, state, facts) |
| API call | No Claude call | Claude API call required |
| Speed | Instant | 2-5 seconds |
| Use case | General reference | Specific situation advice |
| State-specific | No (general principles) | Yes (cites user's state law) |

Guides complement chat — they provide baseline knowledge that chat then personalizes.

---

## How to Add a New Guide

1. Define a new `RightsGuide` object in `backend/knowledge/rights_library.py`:
   ```python
   RightsGuide(
       id="unique_guide_id",
       domain="legal_domain_key",
       title="Guide Title",
       description="One-line summary",
       explanation="2-3 paragraphs of plain-English overview...",
       your_rights=["Right 1", "Right 2", ...],
       action_steps=["Step 1", "Step 2", ...],
       deadlines=["File within 30 days of...", ...],
       common_mistakes=["Don't do X because...", ...],
       when_to_get_a_lawyer="Get a lawyer if..."
   )
   ```
2. Add it to the `RIGHTS_GUIDES` list
3. Add a test in `tests/test_rights_library.py` verifying lookup by ID and domain
4. The guide is automatically available via the API — no route changes needed

---

## Domain Coverage Map

| Domain | Guide Count | Coverage |
|--------|-------------|----------|
| Landlord & Tenant | 3 | Eviction, deposits, habitability |
| Employment | 3 | Wage theft, termination, discrimination |
| Consumer Protection | 2 | Refunds, lemon law |
| Debt & Collections | 3 | FDCPA, bankruptcy, garnishment |
| Traffic | 2 | Tickets, DUI |
| Family Law | 2 | Divorce, custody |
| Criminal Records | 1 | Expungement |
| Small Claims | 1 | Filing process |
| Contracts | 1 | Breach |
| Immigration | 1 | Rights overview |

---

## Related

- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — State laws and classifier
- [LEGAL_DOMAINS.md](LEGAL_DOMAINS.md) — Domain detail and keywords
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — How personalized chat differs from static guides
- [EXTENDING.md](EXTENDING.md) — Full extension guide
