# Cross-Verification Matrix

Every feature in CaseMate maps to implementation code, tests, and documentation. This matrix ensures nothing ships without all three.

> Last verified: 2026-03-29 | 459 backend tests | 132 frontend tests | 24 E2E tests

## How to Read This Matrix

- **Feature**: What the user sees or the system does
- **Implementation**: Exact file(s) and key function(s)
- **Tests**: Test file(s) and test count
- **Docs**: Where this feature is documented
- **Status**: Complete | Partial | Missing

## Core Features

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| Memory injection | `backend/memory/injector.py` -> `build_system_prompt()` | `tests/test_memory_injector.py` (31 tests) | ARCHITECTURE.md, ADR-001, MEMORY_SYSTEM.md | Complete |
| Profile auto-updater | `backend/memory/updater.py` -> `update_profile_from_conversation()` | `tests/test_profile_updater.py` (6 tests) | ARCHITECTURE.md, ADR-003, MEMORY_SYSTEM.md | Complete |
| Legal classifier (hybrid) | `backend/legal/classifier.py` -> `classify_legal_area()` | `tests/test_legal_classifier.py` (40 tests) | ADR-009, ADR-021, LEGAL_DOMAINS.md | Complete |
| Legal area modules | `backend/legal/areas/` (10 modules) | `tests/test_legal_areas.py` (15 tests) | LEGAL_DOMAINS.md, LEGAL_KNOWLEDGE_BASE.md | Complete |
| Chat API | `backend/main.py` -> `POST /api/chat` | `tests/test_api_endpoints.py` (63 tests) | API.md | Complete |
| SSE streaming | `backend/main.py` -> `GET /api/chat/{id}/stream` | `tests/test_api_endpoints.py` | ADR-022, ARCHITECTURE.md | Complete |
| Profile CRUD | `backend/main.py` -> `GET/POST/PATCH /api/profile` | `tests/test_profile_crud.py` (8 tests), `tests/test_api_endpoints.py` | API.md | Complete |
| Conversation CRUD | `backend/memory/conversation_store.py` | `tests/test_conversation_store.py` (9 tests), `tests/test_api_endpoints.py` | API.md | Complete |
| Document upload + extraction | `backend/documents/extractor.py` | `tests/test_document_extractor.py` (10 tests) | ADR-004, DOCUMENT_PIPELINE.md | Complete |
| Document analysis | `backend/documents/analyzer.py` | `tests/test_document_analyzer.py` (6 tests) | ADR-004, DOCUMENT_PIPELINE.md | Complete |
| Demand letter generator | `backend/actions/letter_generator.py` | `tests/test_action_generators.py` (7 tests total) | ADR-005, ACTIONS.md | Complete |
| Rights summary generator | `backend/actions/rights_generator.py` | `tests/test_action_generators.py` | ADR-005, ACTIONS.md | Complete |
| Checklist generator | `backend/actions/checklist_generator.py` | `tests/test_action_generators.py` | ADR-005, ACTIONS.md | Complete |
| Deadline detection | `backend/deadlines/detector.py` | `tests/test_deadline_detector.py` (9 tests) | ADR-006, DEADLINES.md | Complete |
| Deadline tracking | `backend/deadlines/tracker.py` | `tests/test_deadline_tracker.py` (9 tests) | ADR-006, DEADLINES.md | Complete |
| Attorney referral | `backend/referrals/matcher.py` | `tests/test_referral_matcher.py` (5 tests) | ADR-014, REFERRALS.md | Complete |
| Workflow engine | `backend/workflows/engine.py` | `tests/test_workflow_engine.py` (7 tests) | ADR-007, WORKFLOWS.md | Complete |
| Workflow templates | `backend/workflows/templates/definitions.py` | `tests/test_workflow_templates.py` (6 tests) | WORKFLOWS.md | Complete |
| Rights library | `backend/knowledge/rights_library.py` | `tests/test_rights_library.py` (9 tests) | ADR-015, RIGHTS_LIBRARY.md | Complete |
| State-specific laws | `backend/legal/state_laws.py`, `backend/legal/states/` (6 files) | `tests/test_legal_areas.py` | ADR-002, ADR-011, LEGAL_KNOWLEDGE_BASE.md | Complete |
| PDF export | `backend/export/pdf_generator.py` | `tests/test_pdf_generator.py` (7 tests) | ADR-013, EXPORT.md | Complete |
| Email sending | `backend/export/email_sender.py` | `tests/test_email_sender.py` (7 tests) | EXPORT.md | Complete |
| Prompt caching | `backend/memory/injector.py` (cache_control blocks) | `tests/test_memory_injector.py` | ARCHITECTURE.md, MEMORY_SYSTEM.md | Complete |
| Token budget management | `backend/utils/token_budget.py` | `tests/test_token_budget.py` (13 tests) | UTILS.md | Complete |

## Authentication and Security

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| JWT authentication | `backend/utils/auth.py` | `tests/test_auth.py` (8 tests) | SECURITY.md | Complete |
| Rate limiting | `backend/utils/rate_limiter.py` | `tests/test_rate_limiter.py` (10 tests) | ADR-008, SECURITY.md | Complete |
| Security headers middleware | `backend/main.py` (SecurityHeadersMiddleware) | `tests/test_api_endpoints.py` | SECURITY.md | Complete |

## Reliability and Infrastructure

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| Circuit breaker | `backend/utils/circuit_breaker.py` | `tests/test_circuit_breaker.py` (10 tests) | ARCHITECTURE.md, UTILS.md | Complete |
| Retry with backoff | `backend/utils/retry.py` | `tests/test_retry.py` (10 tests) | ARCHITECTURE.md, UTILS.md | Complete |
| Anthropic client singleton | `backend/utils/client.py` | `tests/test_client_singleton.py` (6 tests) | UTILS.md | Complete |
| Structured logging | `backend/utils/logger.py` | Used across all test files | UTILS.md | Complete |
| Telemetry | `backend/utils/telemetry.py` | `tests/test_telemetry.py` (11 tests) | UTILS.md | Complete |
| Audit logging | `backend/utils/audit_log.py` | `tests/test_audit_log.py` (15 tests) | UTILS.md | Complete |
| Concurrency utilities | `backend/utils/concurrency.py` | `tests/test_concurrency.py` (13 tests) | UTILS.md | Complete |
| Content store | `backend/utils/content_store.py` | `tests/test_content_store.py` (15 tests) | UTILS.md | Complete |
| Idempotency | `backend/utils/idempotency.py` | `tests/test_idempotency.py` (12 tests) | UTILS.md | Complete |
| Lifecycle management | `backend/utils/lifecycle.py` | `tests/test_lifecycle.py` (20 tests) | UTILS.md | Complete |

## Payments

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| Stripe webhooks | `backend/payments/stripe_webhooks.py` | `tests/test_payments.py` (22 tests) | PAYMENTS.md | Complete |
| Subscription management | `backend/payments/subscription.py` | `tests/test_payments.py` | PAYMENTS.md | Complete |

## Data Models

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| LegalProfile model | `backend/models/legal_profile.py` | `tests/test_models.py` (19 tests) | MODELS.md | Complete |
| Conversation model | `backend/models/conversation.py` | `tests/test_models.py` | MODELS.md | Complete |
| Action output models | `backend/models/action_output.py` | `tests/test_models.py` | MODELS.md | Complete |
| Response models | `backend/models/responses.py` | `tests/test_models.py` | MODELS.md | Complete |
| Property-based model tests | All models | `tests/test_property_based.py` (8 tests) | TESTING.md | Complete |

## Frontend Features

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| Chat interface | `web/components/ChatInterface.tsx` | `web/__tests__/components/ChatInterface.test.tsx` (11 tests) | FRONTEND.md | Complete |
| Legal profile sidebar | `web/components/LegalProfileSidebar.tsx` | `web/__tests__/components/LegalProfileSidebar.test.tsx` (11 tests) | FRONTEND.md | Complete |
| Onboarding wizard | `web/components/OnboardingFlow.tsx` | `web/__tests__/components/OnboardingFlow.test.tsx` (9 tests) | FRONTEND.md | Complete |
| Document upload | `web/components/DocumentUpload.tsx` | `web/__tests__/components/DocumentUpload.test.tsx` (7 tests) | FRONTEND.md | Complete |
| Action generator | `web/components/ActionGenerator.tsx` | `web/__tests__/components/ActionGenerator.test.tsx` (8 tests) | FRONTEND.md | Complete |
| Deadline dashboard | `web/components/DeadlineDashboard.tsx` | `web/__tests__/components/DeadlineDashboard.test.tsx` (10 tests) | FRONTEND.md | Complete |
| Attorney cards | `web/components/AttorneyCard.tsx` | `web/__tests__/components/AttorneyCard.test.tsx` (9 tests) | FRONTEND.md | Complete |
| Workflow wizard | `web/components/WorkflowWizard.tsx` | `web/__tests__/components/WorkflowWizard.test.tsx` (11 tests) | FRONTEND.md | Complete |
| Rights guide | `web/components/RightsGuide.tsx` | `web/__tests__/components/RightsGuide.test.tsx` (11 tests) | FRONTEND.md | Complete |
| Waitlist form | `web/components/WaitlistForm.tsx` | `web/__tests__/components/WaitlistForm.test.tsx` (6 tests) | FRONTEND.md | Complete |
| Case history | `web/components/CaseHistory.tsx` | `web/__tests__/components/CaseHistory.test.tsx` (6 tests) | FRONTEND.md | Complete |
| Conversation history | `web/components/ConversationHistory.tsx` | `web/__tests__/components/ConversationHistory.test.tsx` (7 tests) | FRONTEND.md | Complete |
| Auth library | `web/lib/auth.ts` | `web/__tests__/lib/auth.test.tsx` (5 tests) | SECURITY.md | Complete |

### Frontend UI Components

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| Button | `web/components/ui/Button.tsx` | `web/__tests__/components/ui/Button.test.tsx` (6 tests) | FRONTEND.md | Complete |
| Card | `web/components/ui/Card.tsx` | `web/__tests__/components/ui/Card.test.tsx` (5 tests) | FRONTEND.md | Complete |
| Badge | `web/components/ui/Badge.tsx` | `web/__tests__/components/ui/Badge.test.tsx` (5 tests) | FRONTEND.md | Complete |
| Input | `web/components/ui/Input.tsx` | `web/__tests__/components/ui/Input.test.tsx` (5 tests) | FRONTEND.md | Complete |
| Error boundary | `web/components/ui/ErrorBoundary.tsx` | — | FRONTEND.md | Partial (no dedicated test) |
| Skeleton loader | `web/components/ui/Skeleton.tsx` | — | FRONTEND.md | Partial (no dedicated test) |
| 3D scene | `web/components/Scene3D.tsx` | — | — | Partial (no test, no docs) |
| Liquid ether effect | `web/components/LiquidEther.tsx` | — | — | Partial (no test, no docs) |

## Infrastructure

| Feature | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| CI/CD pipeline | `.github/workflows/ci.yml` | Pipeline self-tests | CI_CD.md | Complete |
| Mobile CI | `.github/workflows/mobile.yml` | Pipeline self-tests | MOBILE.md | Complete |
| Docker containerization | `Dockerfile`, `web/Dockerfile` | Docker build in CI | DEPLOYMENT.md | Complete |
| Docker Compose (prod) | `docker-compose.prod.yml` | — | DEPLOYMENT.md | Complete |
| Docker Compose (dev) | `docker-compose.yml` | — | DEPLOYMENT.md | Complete |
| Nginx reverse proxy | `nginx/nginx.conf` | — | DEPLOYMENT.md | Complete |
| E2E tests (Playwright) | `web/e2e/smoke.spec.ts` (24 tests) | Self-testing | TESTING.md, ADR-016 | Complete |
| Property-based tests | `tests/test_property_based.py` (8 tests) | Self-testing | TESTING.md | Complete |
| Deployment verification | `scripts/verify_deployment.sh` | — | DEPLOYMENT.md | Complete |
| Demo seed script | `scripts/seed_demo.py` | — | CLAUDE.md | Complete |

## Architecture Decision Records

| ADR | Title | Docs |
|-----|-------|------|
| 001 | Memory as differentiator | `docs/decisions/001-memory-as-differentiator.md` |
| 002 | State-specific legal context | `docs/decisions/002-state-specific-legal-context.md` |
| 003 | Profile auto-update strategy | `docs/decisions/003-profile-auto-update-strategy.md` |
| 004 | Document pipeline design | `docs/decisions/004-document-pipeline-design.md` |
| 005 | Action generator scope | `docs/decisions/005-action-generator-scope.md` |
| 006 | Deadline auto-detection | `docs/decisions/006-deadline-auto-detection.md` |
| 007 | Guided workflow engine | `docs/decisions/007-guided-workflow-engine.md` |
| 008 | Rate limiting strategy | `docs/decisions/008-rate-limiting-strategy.md` |
| 009 | Keyword classifier over LLM | `docs/decisions/009-keyword-classifier-over-llm.md` |
| 010 | Supabase over vector DB | `docs/decisions/010-supabase-over-vector-db.md` |
| 011 | Regional state law organization | `docs/decisions/011-regional-state-law-organization.md` |
| 012 | Background task pattern | `docs/decisions/012-background-task-pattern.md` |
| 013 | PDF export with fpdf2 | `docs/decisions/013-pdf-export-with-fpdf2.md` |
| 014 | Attorney scoring algorithm | `docs/decisions/014-attorney-scoring-algorithm.md` |
| 015 | Rights library static content | `docs/decisions/015-rights-library-static-content.md` |
| 016 | Frontend testing strategy | `docs/decisions/016-frontend-testing-strategy.md` |
| 017 | Mobile architecture (Expo) | `docs/decisions/017-mobile-architecture-expo.md` |
| 018 | Deployment architecture | `docs/decisions/018-deployment-architecture.md` |
| 019 | Comprehensive documentation standards | `docs/decisions/019-comprehensive-documentation-standards.md` |
| 020 | Backend test coverage threshold | `docs/decisions/020-backend-test-coverage-threshold.md` |
| 021 | Hybrid classifier (keyword-first, LLM fallback) | `docs/decisions/021-hybrid-classifier-keyword-first-llm-fallback.md` |
| 022 | SSE streaming over WebSocket for chat | `docs/decisions/022-sse-streaming-over-websocket-for-chat.md` |
| 023 | Supabase unified platform | `docs/decisions/023-supabase-unified-platform.md` |

## Verification Commands

```bash
# Run all backend tests with coverage
make test

# Run frontend tests
cd web && npm test

# Run E2E tests
cd web && npx playwright test

# Run full verification (lint + test)
make verify

# Verify deployment health
scripts/verify_deployment.sh

# Seed demo profile (Sarah Chen)
make seed
```

## Test Pyramid

```
           /\
          /  \        E2E Tests (24 Playwright)
         /    \       Critical user journeys
        /------\
       /        \     Backend Tests (459 pytest)
      /          \    API endpoints, memory injection,
     /            \   classifier, actions, auth, payments
    /--------------\
   /                \  Frontend Tests (132 Jest)
  /                  \ Components, hooks, utilities
 /--------------------\
```

## Coverage Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| `ErrorBoundary.tsx` — no dedicated test | Low | Covered indirectly by component tests that trigger errors |
| `Skeleton.tsx` — no dedicated test | Low | Pure presentational component |
| `Scene3D.tsx` — no test or docs | Low | Visual effect, not business logic |
| `LiquidEther.tsx` — no test or docs | Low | Visual effect, not business logic |
| `nginx/nginx.conf` — no test | Low | Validated at deploy time via `verify_deployment.sh` |
