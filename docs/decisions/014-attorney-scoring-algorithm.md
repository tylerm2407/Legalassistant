# ADR 014 — Weighted scoring for attorney referral matching

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Attorney referral matching uses a deterministic weighted scoring algorithm that ranks attorneys on a 0–100 scale based on specialization match, rating, and free consultation availability. The implementation lives in `backend/referrals/matcher.py` and is served via `GET /api/attorneys/search`.

---

## Context

CaseMate includes an attorney referral feature for cases that exceed what an AI assistant can handle — complex litigation, court appearances, or situations where the user explicitly needs a lawyer. The referral system needs to surface relevant attorneys from the `attorneys` Supabase table, ranked by how well they match the user's state and legal domain.

The scoring needs to be transparent and explainable. Users should understand why a particular attorney was recommended. An opaque ML-based ranking would undermine trust in a legal context where users are already anxious about their situation.

---

## The implementation

`backend/referrals/matcher.py` defines the `get_referral_suggestions()` function, which:

1. Queries the `attorneys` table filtered by `state` and optionally by `legal_area` (using Supabase `.contains("specializations", [legal_area])`)
2. Scores each attorney with a weighted formula
3. Returns results sorted by score descending

The scoring formula:

| Factor | Points | Logic |
|--------|--------|-------|
| Base score | 50 | Every attorney in the correct state starts here |
| Specialization match | +30 | Attorney's `specializations` list includes the user's legal area |
| Rating bonus | +0–10 | `attorney.rating * 2` (a 5.0-star attorney gets +10) |
| Free consultation | +10 | `accepts_free_consultations` is True |

The score is capped at 100 via `min(score, 100)`.

Each `ReferralSuggestion` includes a `match_reason` string built from the scoring factors (e.g., "Specializes in Landlord Tenant. Licensed in MA. Offers free consultations.") so the UI can show users why this attorney was suggested.

The `Attorney` model stores: name, state, specializations (list[str]), rating (float 1–5), cost_range, phone, email, website, accepts_free_consultations (bool), and bio.

---

## Alternatives considered

**LLM-based matching with issue summary**
Considered. The `get_referral_suggestions()` function accepts an optional `issue_summary` parameter that is currently unused. The intent is to allow a future version to use Claude to match the user's specific issue description against attorney bios for more nuanced matching. Deferred because the current weighted scoring handles the common case (state + domain match) well, and LLM matching would add latency and cost to every referral request.

**Collaborative filtering ("users like you chose...")**
Rejected. Requires significant user volume to generate meaningful recommendations. With a pre-launch product and zero historical referral data, collaborative filtering has no signal to work with. Could be revisited after reaching significant user scale.

**External API integration (Avvo, Martindale-Hubbell)**
Deferred. Third-party attorney directories would provide richer data (verified reviews, disciplinary records, case outcomes) but add API costs, rate limits, and a dependency on external services. The current approach uses a self-managed Supabase table that can be populated with curated attorney data. External API integration can be layered on top later.

**Simple alphabetical or rating-only sort**
Rejected. Sorting by rating alone ignores specialization relevance. A highly-rated real estate attorney is not useful for a user with an employment discrimination case. The weighted scoring ensures domain relevance is the primary ranking factor.

---

## Consequences

**Positive:**
- Fully transparent — each suggestion includes a human-readable match_reason
- Deterministic and fast — no API calls, scoring runs in Python with pre-fetched data
- Specialization match is the dominant factor (+30), ensuring domain relevance
- Free consultation bonus (+10) prioritizes cost-accessible options for CaseMate's target demographic
- Easy to tune — weights can be adjusted without changing the algorithm structure

**Negative:**
- Scoring is simplistic — does not consider attorney workload, response time, or outcome history
- The `issue_summary` parameter is accepted but not yet used in scoring
- Attorney data quality depends on manual curation of the Supabase `attorneys` table
- No geographic proximity scoring within a state (a Boston attorney may not be practical for a Springfield user)
- Rating data may be sparse or absent for newly added attorneys (defaults to 0.0)

---

## Status

Accepted. The weighted scoring algorithm handles the MVP referral use case. The `issue_summary` parameter is a hook for future LLM-enhanced matching. Geographic proximity and external directory integration are on the roadmap for post-launch iteration.
