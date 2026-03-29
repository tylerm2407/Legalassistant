# ADR 028: Test Suite Alignment with Anthropic-Only Router

## Status
Accepted (updated to reflect Anthropic-only architecture)

## Context
After simplifying the LLM router to Anthropic-only (ADR 025), test mocks were updated to match. The auth endpoint also changed from returning 500 to 401 for empty JWT secrets (correct HTTP semantics — missing auth is unauthorized, not a server error). The onboarding flow added a 6th step (language preference), breaking step-count assertions.

## Decision
- Update `test_auth.py`: `test_empty_jwt_secret_returns_500` → `test_empty_jwt_secret_returns_401` to match corrected behavior.
- Update `test_integration.py`: Mock `get_llm_router` to return an Anthropic-only mock router.
- Update `OnboardingFlow.test.tsx`: Adjust step counts from 5 → 6 to reflect the new language preference step.

## Consequences
- **Positive:** Tests accurately reflect the current Anthropic-only architecture and provider configuration.
- **Positive:** Auth test uses correct HTTP semantics (401 vs 500).
- **Positive:** No coupling to unused providers — mocks are simpler and more maintainable.
