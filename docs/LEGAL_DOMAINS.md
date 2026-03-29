# Legal Domains

CaseMate covers 10 legal domains with keyword-based classification, 50-state law coverage, per-domain area modules, and 19 pre-built rights guides.

## Domain Classification

`classify_legal_area()` in `backend/legal/classifier.py` uses deterministic keyword matching -- no LLM call. This is intentional: classification runs on every user message before the Claude API call and must be fast.

Each domain has 15-20 keywords. The classifier lowercases the user's message, counts keyword hits per domain, and returns the domain with the highest score. If no keywords match, it returns `"general"`.

## The 10 Domains

| Domain key | Keywords (sample) | Area module |
|---|---|---|
| `landlord_tenant` | landlord, eviction, security deposit, habitability, lease | `areas/landlord_tenant.py` |
| `employment_rights` | fired, wage, overtime, discrimination, fmla, retaliation | `areas/employment.py` |
| `consumer_protection` | scam, fraud, refund, warranty, lemon law, hidden fee | `areas/consumer.py` |
| `debt_collections` | debt collector, garnishment, fdcpa, credit report, repo | `areas/debt_collections.py` |
| `small_claims` | small claims court, sue, damages, filing fee, judgment | `areas/small_claims.py` |
| `contract_disputes` | contract, breach, non-compete, nda, termination clause | `areas/contracts.py` |
| `traffic_violations` | traffic ticket, speeding, dui, license suspended, citation | `areas/traffic.py` |
| `family_law` | divorce, custody, child support, restraining order, adoption | `areas/family_law.py` |
| `criminal_records` | expungement, felony, background check, probation, bail | `areas/criminal_records.py` |
| `immigration` | visa, green card, deportation, asylum, h1b, daca, uscis | `areas/immigration.py` |

## Area Modules

Each file in `backend/legal/areas/` exports three items:

- `DOMAIN_GUIDANCE` (str) -- A prompt fragment injected into the system prompt when that domain is detected. Tells Claude how to approach the topic (e.g., cite deposit return timelines, distinguish lease violations from illegal conduct).
- `KEY_STATUTES` (dict[str, str]) -- Statute citation to plain-English explanation. Example: `"M.G.L. c. 186, SS 15B"` maps to Massachusetts security deposit law.
- `COMMON_QUESTIONS` (list[str]) -- Representative questions for the domain, useful for onboarding suggestions and testing.

## 50-State Coverage

State-specific laws live in `backend/legal/states/` organized by region:

| File | Region | States |
|------|--------|--------|
| `northeast.py` | Northeast | MA, NY, CT, NJ, PA, ME, NH, VT, RI |
| `southeast.py` | Southeast | FL, GA, VA, NC, SC, AL, MS, TN, KY, WV, MD, DE, LA, AR |
| `midwest.py` | Midwest | IL, OH, MI, IN, WI, MN, IA, MO, KS, NE, ND, SD |
| `south_central.py` | South Central | TX, OK |
| `west.py` | West | CA, WA, OR, CO, AZ, NV, UT, NM, ID, MT, WY, HI, AK |
| `federal.py` | Federal | Federal-level defaults |

All state data is aggregated into `STATE_LAWS` in `backend/legal/state_laws.py`, keyed by two-letter state code. Federal defaults live under the key `"federal_defaults"`. The memory injector looks up `STATE_LAWS[state_code][legal_area]` for state law and `STATE_LAWS["federal_defaults"][legal_area]` for federal law.

## Rights Guides Library

`backend/knowledge/rights_library.py` contains 19 `RightsGuide` objects. Each guide has a structured format:

- `id` / `domain` / `title` / `description` -- Identification and categorization
- `explanation` -- Plain-English overview of the legal situation
- `your_rights` -- Specific rights the user has
- `action_steps` -- Ordered steps to take
- `deadlines` -- Time limits and filing windows
- `common_mistakes` -- Pitfalls to avoid
- `when_to_get_a_lawyer` -- When professional help is recommended

### Guide Inventory by Domain

| Domain | Guides |
|--------|--------|
| Landlord/Tenant | `tenant_eviction_defense`, `tenant_security_deposit`, `tenant_habitability` |
| Employment | `employment_wage_theft`, `employment_wrongful_termination`, `employment_discrimination` |
| Consumer | `consumer_refund_rights`, `consumer_lemon_law` |
| Debt/Collections | `consumer_debt_collection`, `debt_bankruptcy_basics`, `debt_garnishment` |
| Traffic | `traffic_ticket_fight`, `traffic_dui_process` |
| Family Law | `family_divorce_basics`, `family_custody_basics` |
| Criminal Records | `criminal_expungement` |
| Small Claims | `small_claims_filing` |
| Contracts | `contract_breach` |
| Immigration | `immigration_rights_overview` |

Lookup functions: `get_all_guides()`, `get_guide_by_id(guide_id)`, `get_guides_by_domain(domain)`.

## Workflow Templates

Five guided workflow templates cover the most common multi-step legal actions. See `docs/WORKFLOWS.md` for details on the template system and engine.
