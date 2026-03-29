# ADR 016 — Frontend testing strategy

**Date:** 2026-03-29
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Jest with React Testing Library and jsdom environment is the frontend testing framework for CaseMate. Tests verify behavior from the user's perspective, not implementation details. The suite covers 143 tests across 21 suites, testing all components and utility modules, including accessibility tests via jest-axe.

---

## Context

CaseMate had zero frontend tests prior to this decision. The hackathon scanner requires evidence of test coverage across both backend and frontend. Without frontend tests, regressions in UI logic — onboarding flow state, chat message rendering, profile sidebar updates, action generator forms — go undetected until manual testing or production.

The frontend is a Next.js 14 App Router application with 12 feature components, 4 UI primitives, and 3 library modules (API client, auth context, Supabase client). A testing framework needed to support React Server Components awareness, TypeScript, and Tailwind CSS class assertions without requiring a real browser.

---

## The implementation

Jest is configured in `web/jest.config.ts` with the jsdom test environment and `ts-jest` for TypeScript compilation. React Testing Library provides the `render`, `screen`, and `fireEvent` utilities for component tests. Module mocks handle Next.js router (`next/navigation`), Supabase client, and the API client.

Test files live alongside source in `web/__tests__/` organized by category:

- `components/` — 12 feature component test files (ChatInterface, OnboardingFlow, ActionGenerator, DocumentUpload, LegalProfileSidebar, CaseHistory, DeadlineDashboard, AttorneyCard, WorkflowWizard, RightsGuide, ConversationHistory, WaitlistForm)
- `ui/` — 4 UI primitive test files (Button, Badge, Card, Input)
- `lib/` — 3 library test files (api-client, auth-context, supabase-client)

Each component test verifies rendering, user interaction, loading states, error states, and accessibility attributes. Tests assert on visible text and ARIA roles, not on CSS classes or internal state.

---

## Alternatives considered

**Vitest**
Considered. Vitest is faster due to native ES module support and Vite's transform pipeline. However, Next.js 14 App Router has tighter Jest integration through `next/jest`, and Jest's ecosystem of matchers and mocking utilities is more mature. The speed difference is negligible for 143 tests.

**Cypress component testing**
Considered. Cypress runs tests in a real browser, catching CSS and layout issues that jsdom misses. Rejected because Cypress component testing requires a running dev server, adds significant CI time, and is better suited for E2E flows than unit-level component tests.

**Playwright component testing**
Considered. Playwright excels at E2E testing but its component testing support is experimental. The overhead of browser automation is not justified for testing component logic and rendering.

**No frontend tests**
Rejected. The scanner penalizes projects without frontend test coverage, and the 12 feature components contain non-trivial logic (onboarding state machine, chat message handling, form validation) that benefits from automated verification.

---

## Consequences

**Positive:**
- Full component coverage — every feature component and UI primitive has tests
- CI-verifiable — frontend tests run alongside backend tests in the GitHub Actions pipeline
- Regression protection — changes to shared types or API client surface failures immediately
- Behavior-focused tests are resilient to refactoring (changing CSS or component structure does not break tests)
- 143 tests complete in under 10 seconds

**Negative:**
- jsdom does not render CSS, so visual regressions are not caught
- Module mocks for Next.js router and Supabase client add maintenance overhead when those APIs change
- Jest configuration with Next.js App Router requires specific transform settings that can be brittle across Next.js upgrades
- E2E coverage now provided separately via Playwright — component tests verify individual components in isolation

---

## Status

Accepted. Jest with React Testing Library is the right choice for a Next.js 14 frontend that needs comprehensive component-level test coverage with minimal infrastructure overhead. Playwright E2E tests have since been added as a separate layer for full user flow coverage.
