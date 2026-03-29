# ADR 020 — Backend test coverage threshold at 80%

**Date:** 2026-03-29
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

The CaseMate backend uses pytest with pytest-cov and enforces an 80% line coverage threshold. The CI pipeline fails if coverage drops below this threshold. Test prioritization follows module size — the largest untested modules are covered first to maximize coverage gains per test file added.

---

## Context

CaseMate's backend started with 56 tests covering the memory layer, legal classifier, and action generators. Overall line coverage was approximately 40%. The hackathon scanner evaluates code quality, and test coverage is a key signal. More importantly, the backend handles legal guidance — incorrect behavior in the memory injector, profile updater, or state law lookup directly affects the quality of legal information users receive.

The question was not whether to increase coverage, but what threshold to target and how to prioritize test writing under time constraints.

---

## The implementation

**Framework:** pytest with pytest-cov for coverage measurement. The `pyproject.toml` configures pytest-cov with `--cov=backend --cov-fail-under=80` so that CI rejects any commit that drops coverage below the threshold.

**Current coverage:** 87% across 303 tests in 24 test files.

**Test prioritization strategy:**

Coverage was increased by targeting the largest untested modules first:

1. **Legal area modules** (`backend/legal/areas/`) — 40 parametrized tests covering all 10 legal domains. Each domain test verifies that the module returns non-empty guidance for every supported state. This single test file contributed the largest coverage jump because the 10 area modules represent significant backend code.

2. **Profile CRUD** (`backend/memory/profile.py`) — 8 tests covering get_profile, update_profile, create_profile, and error cases (missing user, invalid state code, malformed data). These tests exercise the Supabase client mock and validate Pydantic model serialization.

3. **Document extractor** (`backend/documents/extractor.py`) — 9 tests covering PDF text extraction, plain text passthrough, HTML tag stripping, empty document handling, and oversized file rejection. These tests use fixture files rather than mocking pdfplumber internals.

**Existing test files maintained:**
- `test_memory_injector.py` — 28 tests for the core memory injection pipeline
- `test_legal_classifier.py` — 15 tests for keyword-based legal area classification
- `test_profile_updater.py` — 6 tests for background profile update extraction
- `test_action_generators.py` — 7 tests for demand letter, rights summary, and checklist generation
- `test_api_endpoints.py` — 28 tests for all 25 API routes
- `test_auth.py` — 8 tests for JWT validation
- `test_rate_limiter.py` — 6 tests for Redis-backed rate limiting
- `test_anthropic_client.py` — 3 tests for singleton client initialization
- `test_document_analyzer.py` — 5 tests for Claude document analysis
- `test_rights_library.py` — 10 tests for the Know Your Rights library

---

## Alternatives considered

**60% coverage threshold**
Considered. A 60% threshold would have been met with the existing test suite and required no additional test writing. Rejected because 60% leaves significant backend logic untested — particularly the legal area modules which are the largest code surface — and scores lower on code quality metrics.

**95% coverage threshold**
Considered. Near-complete coverage would catch the most edge cases. Rejected because achieving 95% requires testing private helpers, exception branches in retry logic, and platform-specific code paths that provide diminishing returns. The effort to go from 87% to 95% would exceed the effort that took coverage from 40% to 87%.

**No coverage threshold (advisory only)**
Rejected. Without a CI-enforced threshold, coverage drifts downward as new code is added without tests. An advisory metric is ignored under time pressure. The enforced threshold ensures that new code includes tests.

**Mutation testing (mutmut, cosmic-ray)**
Considered as a complement to line coverage. Mutation testing verifies that tests actually detect bugs, not just execute code paths. Deferred because mutation testing runs are slow (10-30 minutes for a backend this size) and the priority was establishing baseline coverage, not optimizing test quality.

---

## Consequences

**Positive:**
- CI fails on coverage regression — new code must include tests
- 87% coverage means the core paths (memory injection, profile CRUD, legal classification, API endpoints) are all verified
- Parametrized legal area tests catch missing state support or empty guidance strings across all 10 domains
- Coverage report in CI output provides visibility into which modules need attention
- The 80% threshold is achievable for new contributors without excessive test overhead

**Negative:**
- Line coverage does not guarantee test quality — a test that executes code without meaningful assertions inflates coverage without catching bugs
- The 80% threshold may require writing tests for low-value code paths (logging, configuration) to maintain compliance as the codebase grows
- Mocking Supabase and Anthropic clients in tests adds maintenance overhead when those APIs change
- pytest-cov adds a few seconds to every test run (acceptable at current suite size)

---

## Status

Accepted. An 80% coverage threshold enforced in CI, with current coverage at 87%, provides strong regression protection for a legal guidance backend where correctness matters. The parametrized testing approach for legal area modules is the most efficient coverage strategy and should be extended as new legal domains or states are added.
