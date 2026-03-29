# Legal Domains

CaseMate covers 10 legal domains with keyword-based classification, 50-state law coverage, per-domain area modules, and 19 pre-built rights guides.

## Domain Classification

`classify_legal_area()` in `backend/legal/classifier.py` uses deterministic keyword matching -- no LLM call. This is intentional: classification runs on every user message before the Claude API call and must be fast.

Each domain has 15-20 keywords. The classifier lowercases the user's message, counts keyword hits per domain, and returns the domain with the highest score. If no keywords match, it returns `"general"`.

### Classifier Algorithm Detail

The classifier uses a weighted scoring system:

1. **Phrase boost (3x):** Multi-word keywords (e.g., "security deposit") receive a `PHRASE_BOOST = 3` multiplier. This is because multi-word matches are far more specific — "security deposit" almost certainly means landlord/tenant law.

2. **Single word (1x):** Single keywords (e.g., "landlord") get a 1x weight. They provide signal but are less specific.

3. **Longest match tiebreaker:** When two domains score equally, the one with the longest matching keyword wins (more specific = more likely correct).

4. **Confidence scoring:** `classify_with_confidence()` returns a `ClassificationResult` with:
   - `confidence` (0.0-1.0) based on top score ratio and separation from runner-up
   - `method` ("keyword" or "llm")
   - `scores` dict for all domains (useful for debugging)

5. **LLM fallback:** `classify_with_llm_fallback()` uses keywords first, then falls back to Claude if confidence < `CONFIDENCE_THRESHOLD` (0.4). The LLM fallback adds ~2s latency and is used only for truly ambiguous queries.

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

### Per-Domain Detail

#### Landlord & Tenant
**Key statutes:** Security deposit laws (varies by state — MA: M.G.L. c.186 §15B, CA: Civil Code §1950.5), habitability requirements, eviction procedures, rent increase notice requirements.
**Common questions:** "Can my landlord keep my security deposit?", "Is my landlord required to fix this?", "How much notice does my landlord need to give me?"
**Response patterns:** Always cite specific state deposit return deadline, calculate potential penalty damages, reference move-in inspection requirements.

#### Employment Rights
**Key statutes:** FLSA (federal minimum wage/overtime), Title VII (discrimination), FMLA (family leave), state-specific wage laws, at-will employment exceptions.
**Common questions:** "Can my employer fire me for this?", "Am I owed overtime?", "Is this discrimination?"
**Response patterns:** Distinguish federal vs. state protections, identify whether the user is an employee vs. contractor, calculate unpaid wages.

#### Consumer Protection
**Key statutes:** FTC Act §5, state consumer protection acts (e.g., MA Chapter 93A), lemon laws (vary by state), Fair Credit Billing Act.
**Common questions:** "Can I get a refund?", "Is this a scam?", "My product is defective — what can I do?"
**Response patterns:** Identify the applicable state consumer protection act, explain the complaint process, calculate potential recovery.

#### Debt & Collections
**Key statutes:** Fair Debt Collection Practices Act (FDCPA), state collection laws, statute of limitations on debt (varies 3-10 years by state and debt type).
**Common questions:** "Can a debt collector do this?", "Is this debt too old to collect?", "How do I stop collection calls?"
**Response patterns:** Verify the debt is within the statute of limitations, explain validation rights, identify FDCPA violations.

#### Small Claims
**Key statutes:** State small claims court rules, dollar limits (vary $2,500-$25,000 by state), service of process requirements.
**Common questions:** "How do I sue someone in small claims?", "What's the filing fee?", "Do I need a lawyer?"
**Response patterns:** State the dollar limit for the user's state, explain filing process step-by-step, advise on evidence gathering.

#### Contract Disputes
**Key statutes:** UCC Article 2 (sales), Statute of Frauds, state contract law, non-compete enforceability (varies widely by state).
**Common questions:** "Is this contract enforceable?", "Can I break this contract?", "What are my damages for breach?"
**Response patterns:** Identify material vs. minor breach, explain available remedies (damages, specific performance), check if the contract needs to be in writing.

#### Traffic Violations
**Key statutes:** State traffic codes, DUI/DWI laws (BAC limits, implied consent), point systems, license suspension rules.
**Common questions:** "Should I fight this ticket?", "Will I lose my license?", "What happens after a DUI?"
**Response patterns:** Explain the specific violation and penalties, advise on traffic school options, identify procedural defenses.

#### Family Law
**Key statutes:** State divorce statutes, child custody standards (best interest of the child), child support guidelines, domestic violence protection orders.
**Common questions:** "How do I file for divorce?", "What are my custody rights?", "How is child support calculated?"
**Response patterns:** Explain the user's state-specific process, distinguish legal vs. physical custody, advise on mediation vs. litigation.

#### Criminal Records
**Key statutes:** State expungement laws (eligibility, waiting periods, process), FCRA (background check rights), Ban the Box laws.
**Common questions:** "Can I get my record expunged?", "How do I pass a background check?", "Is my conviction eligible for sealing?"
**Response patterns:** Check expungement eligibility for the user's state, explain the petition process, advise on timing.

#### Immigration
**Key statutes:** INA (Immigration and Nationality Act), DACA, state-specific immigration protections, 4th/5th Amendment rights.
**Common questions:** "What are my rights if ICE contacts me?", "How do I apply for a green card?", "Can I work while my visa is pending?"
**Response patterns:** Emphasize constitutional rights (regardless of status), explain the specific process, strongly recommend consulting an immigration attorney.

## How Domain Classification Feeds Into State Law Lookup

```
User message: "My landlord won't return my deposit"
        ↓
classify_legal_area() → "landlord_tenant"
        ↓
STATE_LAWS["MA"]["landlord_tenant"]
  → Massachusetts-specific security deposit law with M.G.L. citations
        ↓
STATE_LAWS["federal_defaults"]["landlord_tenant"]
  → Federal fair housing protections
        ↓
Both injected into system prompt → Claude gives MA-specific answer
```

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

### Coverage Matrix

Not all states have equal depth across all domains. Coverage levels:

| Level | Description | Example |
|-------|-------------|---------|
| **Deep** | Full statute citations, multiple sections, nuanced guidance | MA landlord_tenant, CA employment, TX family_law |
| **Standard** | Key statute cited, basic protections outlined | Most state/domain combinations |
| **Basic** | Federal defaults + generic state reference | Smaller states in less common domains |

States with the deepest coverage (most users, most complex laws):
- **Tier 1:** MA, NY, CA, TX, FL, IL — Deep coverage across all 10 domains
- **Tier 2:** PA, OH, GA, NJ, VA, WA — Deep in 6-8 domains
- **Tier 3:** All other states — Standard coverage, federal fallback for gaps

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

### How Guides Map to Domains

Every guide's `domain` field matches one of the 10 domain keys. The API supports filtering by domain:

```
GET /api/rights/guides?domain=landlord_tenant → 3 guides
GET /api/rights/guides?domain=immigration → 1 guide
GET /api/rights/guides → all 19 guides
```

Lookup functions: `get_all_guides()`, `get_guide_by_id(guide_id)`, `get_guides_by_domain(domain)`.

## Workflow Templates

Five guided workflow templates cover the most common multi-step legal actions. See `docs/WORKFLOWS.md` for details on the template system and engine.

---

## Related

- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — Detailed knowledge base guide
- [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md) — Full rights guide reference
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — How legal context is injected into prompts
- [EXTENDING.md](EXTENDING.md) — How to add new domains and states
