# ADR 011 — Regional organization for 50-state law coverage

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

State-specific legal context for all 50 states is organized into 5 regional Python modules plus a federal defaults module inside `backend/legal/states/`. The regions are: northeast (9 states), southeast (14 states), midwest (12 states), south_central (2 states), and west (13 states). A single `__init__.py` merges all regional dictionaries into one `STATE_LAWS` dict keyed by two-letter state code.

---

## Context

CaseMate's memory injection pattern (ADR 001) requires state-specific statute citations for each of the 10 legal domains. When a Massachusetts renter asks about their security deposit, the system prompt must include M.G.L. c.186 section 15B — not a generic federal reference. This means we need 50 states times 10 legal domains = 500 state-domain entries, plus federal defaults for domains where a state has no specific statute.

The question was how to organize these 500+ entries in the codebase. A single file would be thousands of lines. One file per state would create 50+ files with repetitive structure. We needed a middle ground.

---

## The implementation

The `backend/legal/states/` directory contains six files:

- `northeast.py` — 9 states (CT, ME, MA, NH, NJ, NY, PA, RI, VT) → `NORTHEAST_LAWS` dict
- `southeast.py` — 14 states (AL, AR, DE, FL, GA, KY, LA, MD, MS, NC, SC, TN, VA, WV) → `SOUTHEAST_LAWS` dict
- `midwest.py` — 12 states (IA, IL, IN, KS, MI, MN, MO, NE, ND, OH, SD, WI) → `MIDWEST_LAWS` dict
- `south_central.py` — 2 states (OK, TX) → `SOUTH_CENTRAL_LAWS` dict
- `west.py` — 13 states (AK, AZ, CA, CO, HI, ID, MT, NM, NV, OR, UT, WA, WY) → `WEST_LAWS` dict
- `federal.py` — Federal baseline for all 10 legal domains → `FEDERAL_DEFAULTS` dict

Each regional file exports a `dict[str, dict[str, str]]` mapping state codes to legal domain entries. Each entry is a paragraph-length string containing real statute citations (e.g., "C.G.S. section 47a-21", "Iowa Code section 562A.12") with plain-English descriptions of what the law requires.

`backend/legal/states/__init__.py` merges all six dictionaries into the unified `STATE_LAWS` dict using dictionary unpacking: `{**FEDERAL_DEFAULTS, **NORTHEAST_LAWS, **SOUTHEAST_LAWS, ...}`. The `backend/legal/state_laws.py` module re-exports this for use by the injector and action generators.

Federal defaults are unpacked first so that state-specific entries override them when present.

---

## Alternatives considered

**Single monolithic file**
Rejected. A single `state_laws.py` with all 500+ entries would exceed 5,000 lines, making it impossible to review or maintain. Git diffs would be unreadable when updating a single state's laws.

**One file per state (50 files)**
Rejected. Creates excessive directory clutter and file-switching overhead. Most edits affect a handful of neighboring states at a time (e.g., updating northeast tenant laws). Regional grouping keeps related states together.

**Database-stored law context**
Considered but rejected for MVP. Storing statute citations in Supabase would allow updates without code deploys, but adds a database read to every prompt assembly. Since the legal context is relatively stable (statutes do not change daily) and is read on every request, a Python dictionary in memory is faster and simpler. Database storage can be added later if non-engineer legal reviewers need to update citations.

**JSON or YAML files**
Rejected. Loses Python type checking and IDE support. The dictionary structure with string keys and string values is simple enough that Python dicts are the right format. Import-time validation catches typos immediately.

---

## Consequences

**Positive:**
- Each regional file is 200–400 lines — small enough to review and maintain
- Related states are grouped together, reflecting regional legal patterns (e.g., northeast states often have stronger tenant protections)
- Federal defaults provide a safety net when a state-specific entry is missing
- The merged `STATE_LAWS` dict is a single import for the injector — no conditional logic needed
- Adding a new legal domain requires updating 6 files, not 50

**Negative:**
- Regional boundaries are somewhat arbitrary (e.g., south_central has only 2 states)
- All 500+ entries load into memory at startup — roughly 200KB, acceptable for a server process
- Statute citations can become outdated and require manual review
- No versioning or audit trail for when citations were last verified

---

## Status

Accepted. The regional organization scales well to 50 states and 10 legal domains. If the legal domain count grows significantly, the per-domain `backend/legal/areas/` modules handle domain-specific guidance separately from state-specific statute citations.
