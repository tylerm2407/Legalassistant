# ADR 002 — State-specific legal context injection

**Date:** 2026-03-27
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

CaseMate injects state-specific legal statutes into every system prompt based on the user's stored state. Generic national-level legal answers are explicitly prohibited in our response rules. A user in Massachusetts gets Massachusetts law. A user in Texas gets Texas law.

---

## Context

Legal rights vary dramatically by state. The difference is not minor — it is often the difference between a user having a strong legal case and having no case at all.

Three concrete examples that informed this decision:

**Security deposits:** Massachusetts requires landlords to return deposits within 30 days and pay interest annually. Violation entitles the tenant to 3x the deposit amount plus attorney fees (M.G.L. c.186 §15B). Texas requires return within 30 days but has no interest requirement and no 3x multiplier. A generic answer ("landlords must return deposits within 30 days") is correct but useless — it omits the remedies that actually matter.

**Non-compete agreements:** California treats nearly all non-compete clauses as void and unenforceable. Many other states enforce them fully. Telling a California user they are bound by their non-compete is factually wrong and potentially damages them.

**Wage theft remedies:** Some states allow workers to recover double damages for wage theft. Others allow only the unpaid amount. The difference is whether a worker pursues a claim at all.

Giving a generic national answer in any of these situations actively harms users. It either understates their rights (missing 3x damages) or overstates their exposure (scaring them about an unenforceable non-compete).

---

## The implementation

### Legal area classification

Before building the system prompt, CaseMate classifies the user's question into one of ten legal domains:

```
landlord_tenant | employment_rights | consumer_protection |
debt_collections | small_claims | contract_disputes |
traffic_violations | family_law | criminal_records | immigration_basics
```

This classification is done by `legal/classifier.py` using a lightweight Claude call with the question text.

### State law library

`legal/state_laws.py` maintains a structured library of the most important statutes, rights, and remedies for each state × legal area combination. The library is not exhaustive — it covers the highest-frequency situations in each domain.

```python
STATE_LAWS = {
    "Massachusetts": {
        "landlord_tenant": """
            Security deposits: M.G.L. c.186 §15B. Landlord must return within 30 days
            of lease end. Must pay 5% interest annually or bank rate (whichever higher).
            Violation: tenant entitled to 3x deposit + attorney fees.
            Move-in inspection: required within 10 days or landlord waives right to
            claim damages. No inspection = no deposit claim.
            ...
        """,
        "employment_rights": """
            Wage Act: M.G.L. c.149 §148. Wages must be paid on regular schedule.
            Violation: 3x unpaid wages + attorney fees mandatory (not discretionary).
            Non-competes: enforceable but must meet 2018 Act requirements —
            garden leave payment required, reasonable in scope and duration.
            ...
        """,
    },
    "California": {
        ...
    }
}
```

### Prompt injection

The classified domain and the user's state are used to select and inject the appropriate legal context:

```python
state_context = STATE_LAWS[profile.state][legal_area]
# Injected as a named section in the system prompt
```

---

## Alternatives considered

**Single national-level legal knowledge base**
Rejected. Faster to build but produces answers that are often wrong for the user's specific jurisdiction. The harm from incorrect legal guidance outweighs the development cost.

**Fine-tuned legal model with full statutes**
Rejected for MVP. Building a proper legal RAG system over full state statute databases requires data licensing, indexing infrastructure, and retrieval evaluation that cannot be done in 36 hours. The curated library approach covers 80% of common situations with 10% of the complexity.

**Ask users to specify their state per question**
Rejected. The state is stored in the user's profile from onboarding. Making users re-specify it every time defeats the purpose of persistent memory and creates friction.

**Use web search to retrieve current statutes**
Considered. Rejected for MVP due to latency (adds 2–4 seconds per response) and reliability concerns. The curated library is faster and more consistent. Web search can be added as a fallback for unusual questions in a future version.

---

## Consequences

**Positive:**
- Answers are accurate for the user's jurisdiction — not generically correct and locally wrong
- Users in states with strong tenant/worker protections get answers that reflect those protections
- Classification step allows deeper domain-specific guidance per response
- State law library is a proprietary data asset that improves over time

**Negative:**
- State law library requires ongoing maintenance as laws change
- Classification adds a small amount of latency before the main response
- Coverage gaps exist for unusual legal areas or less common states
- Immigration answers are federal but still vary by state enforcement context

---

## Priority states for launch

Focus the state law library on these states first — they cover 40% of the US population and the highest-frequency legal issues:

1. California — strongest tenant and worker protections, non-compete law is unique
2. New York — robust tenant rights, strong wage theft remedies
3. Texas — large population, significant differences from blue states
4. Florida — major renter population, specific landlord-tenant rules
5. Massachusetts — strong protections, 3x multiplier on deposits and wages
6. Illinois — Chicago tenant ordinance is stronger than state law
7. Pennsylvania, Ohio, Georgia, North Carolina — complete the major population centers

All other states fall back to federal minimum standards with a disclaimer.

---

## Status

Accepted. State routing is implemented in `legal/state_laws.py` and `legal/classifier.py`.
