# ADR 028: Test Suite Alignment with LLM Router

## Status
Accepted

## Context
After introducing the multi-provider LLM router (ADR 025), several tests were still mocking the old direct-Anthropic path. The auth endpoint also changed from returning 500 to 401 for empty JWT secrets (correct HTTP semantics — missing auth is unauthorized, not a server error). The onboarding flow added a 6th step (language preference), breaking step-count assertions.

## Decision
- Update `test_auth.py`: `test_empty_jwt_secret_returns_500` → `test_empty_jwt_secret_returns_401` to match corrected behavior.
- Update `test_integration.py`: Replace Anthropic mock patches with OpenAI mock patches to match the router's primary provider.
- Update `OnboardingFlow.test.tsx`: Adjust step counts from 5 → 6 to reflect the new language preference step.

## Consequences
- **Positive:** Tests accurately reflect the current system behavior and provider configuration.
- **Positive:** Auth test uses correct HTTP semantics (401 vs 500).
- **Negative:** Tests are now coupled to OpenAI as primary provider — if provider order changes, mocks need updating.
