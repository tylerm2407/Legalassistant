# Testing

CaseMate has a comprehensive test suite spanning backend unit tests, frontend component tests, and end-to-end browser tests. The test suite contains **34 backend test files (437+ tests)**, **19 frontend test files (143 tests)**, and **Playwright E2E smoke tests**.

All external dependencies (Anthropic API, Supabase, Redis) are fully mocked. No test makes a real network call.

---

## Table of Contents

- [Running Tests](#running-tests)
- [Backend Test Suite](#backend-test-suite)
- [Frontend Test Suite](#frontend-test-suite)
- [End-to-End Tests (Playwright)](#end-to-end-tests-playwright)
- [Test Fixtures and Mocking Strategy](#test-fixtures-and-mocking-strategy)
- [Coverage Thresholds](#coverage-thresholds)
- [Adding New Tests](#adding-new-tests)
- [CI/CD Integration](#cicd-integration)

---

## Running Tests

### Quick Reference

```bash
make test          # Backend: pytest with coverage
make verify        # Lint + test (required before every commit)
make test-all      # Backend + frontend tests
cd web && npm test # Frontend: Jest
cd web && npm run e2e # E2E: Playwright
```

### Backend Commands

```bash
# Full test suite with coverage
python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing

# Run a single test file
python -m pytest tests/test_memory_injector.py -v

# Run a single test class
python -m pytest tests/test_memory_injector.py::TestBuildSystemPromptIncludesProfileData -v

# Run a single test method
python -m pytest tests/test_memory_injector.py::TestBuildSystemPromptIncludesProfileData::test_includes_state -v

# Run with full traceback output
python -m pytest tests/test_memory_injector.py -v --tb=long

# Run with coverage for a specific module
python -m pytest tests/test_memory_injector.py --cov=backend.memory.injector --cov-report=term-missing
```

### Frontend Commands

```bash
cd web
npm test                    # Run all Jest tests
npm test -- --watch         # Watch mode for development
npm test -- --coverage      # With coverage report
npm test -- ChatInterface   # Run tests matching a pattern
```

### E2E Commands

```bash
cd web
npx playwright test              # Run all E2E tests
npx playwright test --ui         # Interactive UI mode
npx playwright show-report       # View HTML report after run
```

### Configuration

Backend (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

`asyncio_mode = "auto"` means all `async def test_*` functions are automatically treated as async tests without needing the `@pytest.mark.asyncio` decorator.

Frontend (`web/jest.config.ts`):

- Environment: `jsdom`
- Transform: SWC for TypeScript/JSX
- Module aliases: `@/` mapped to `web/`

E2E (`web/playwright.config.ts`):

- Browser: Chromium only
- Timeout: 30 seconds per test
- Retries: 2 in CI, 0 locally
- Artifacts: Screenshots and traces captured on failure

---

## Backend Test Suite

34 test files containing 437+ test functions organized by module.

### Memory System (Priority 1)

The memory injection pattern is the core product. These tests are the highest priority.

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_memory_injector.py` | 37 | `backend/memory/injector.py` | Profile data injection into system prompts, state-specific law inclusion, active issue formatting, legal fact formatting, response rule presence, legal area classification routing, federal fallback behavior. 6 test classes covering every code path. |
| `test_profile_updater.py` | 14 | `backend/memory/updater.py` | Fact extraction from conversations via Claude, deduplication of existing facts, background task execution without blocking response, error handling when extraction fails, partial update behavior. |
| `test_conversation_store.py` | 18 | `backend/memory/conversation_store.py` | Conversation create, list, save, and delete operations. Message append, conversation retrieval by user ID, deletion cascading. |
| `test_profile_crud.py` | 11 | `backend/memory/profile.py` | Profile create, read, update, and delete. Default values on creation, partial update merging, Supabase query construction. |

### Legal Domain

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_legal_classifier.py` | 54 | `backend/legal/classifier.py` | Classification into all 10 legal domains (landlord_tenant, employment, consumer, debt_collections, small_claims, contracts, traffic, family_law, criminal_records, immigration). Keyword scoring accuracy, confidence thresholds, LLM fallback for ambiguous questions, multi-domain overlap resolution. |
| `test_legal_areas.py` | 26 | `backend/legal/areas/*.py` | All 10 legal domain modules. State law retrieval for each area, statute formatting, domain-specific guidance text generation. |
| `test_rights_library.py` | 16 | `backend/knowledge/rights_library.py` | All 19 rights guides. Guide lookup by legal area and state, guide structure validation (title, sections, citations), fallback for states without specific guides. |

### Action Generators

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_action_generators.py` | 25 | `backend/actions/*.py` | Demand letter generation with profile context, rights summary generation with state-specific statutes, checklist generation with actionable next steps. Output formatting, citation inclusion, profile data injection into generated content. |

### API Layer

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_api_endpoints.py` | 88 | `backend/main.py` | All 28 API routes. Success paths, error responses (400, 401, 403, 404, 422, 429, 500), authentication enforcement, request validation, response schema compliance. Covers: `/api/chat`, `/api/profile`, `/api/documents`, `/api/actions/*`, `/api/cases`, `/api/conversations`, `/api/waitlist`, `/health`. |
| `test_auth.py` | 9 | `backend/utils/auth.py` | JWT token verification, expired token rejection, malformed token handling, missing token behavior, user ID extraction from valid tokens. |
| `test_rate_limiter.py` | 14 | `backend/utils/rate_limiter.py` | Redis-backed sliding window rate limiting. Under-limit pass-through, at-limit rejection (429), window expiration reset, fail-open behavior when Redis is unavailable. |

### Document Processing

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_document_analyzer.py` | 11 | `backend/documents/analyzer.py` | Claude-powered document analysis. Fact extraction from legal documents, structured output parsing, error handling for unparseable documents, integration with profile updater. |
| `test_document_extractor.py` | 11 | `backend/documents/extractor.py` | PDF text extraction via pdfplumber, image OCR text extraction, multi-page document handling, empty document handling, corrupted file error handling. |

### Workflows and Deadlines

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_workflow_engine.py` | 18 | `backend/workflows/engine.py` | Guided workflow instance creation, step progression, step validation, workflow completion, state persistence across steps. |
| `test_workflow_templates.py` | 16 | `backend/workflows/templates/` | Template structure validation for all workflow types, required field presence, step ordering, template-to-engine compatibility. |
| `test_deadline_tracker.py` | 17 | `backend/deadlines/tracker.py` | Deadline CRUD operations. Create with date parsing, list by user, update status (pending/completed/missed), delete, overdue detection. |
| `test_deadline_detector.py` | 9 | `backend/deadlines/detector.py` | Pattern-based deadline detection from conversation text. Date extraction, statute of limitations identification, filing deadline recognition. |

### Referrals and Export

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_referral_matcher.py` | 11 | `backend/referrals/matcher.py` | Attorney matching by legal area, state, and specialization. Result ranking, empty result handling, location-based filtering. |
| `test_email_sender.py` | 13 | `backend/export/email_sender.py` | Email delivery for exported documents. Template rendering, attachment handling, delivery error handling, recipient validation. |
| `test_pdf_generator.py` | 15 | `backend/export/pdf_generator.py` | PDF export of demand letters, rights summaries, and checklists. Document formatting, header/footer inclusion, multi-page layout, file output. |

### Infrastructure and Resilience

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_circuit_breaker.py` | 32 | Circuit breaker pattern | Three-state transitions (closed, open, half-open). Failure counting, threshold-based opening, cooldown timer, half-open probe success/failure, reset behavior. |
| `test_concurrency.py` | 32 | Async task handling | Concurrent request handling, task isolation, shared state protection, async context propagation, cancellation behavior. |
| `test_idempotency.py` | 26 | Request deduplication | Idempotency key handling. Duplicate request detection, response caching, key expiration, concurrent identical request handling. |
| `test_retry.py` | 19 | `backend/utils/retry.py` | Exponential backoff for Anthropic API calls. Retry on transient errors (429, 500, 503), no retry on client errors (400, 401), max attempt enforcement, backoff timing (2s, 4s, 8s). |
| `test_client_singleton.py` | 6 | `backend/utils/client.py` | Anthropic client singleton. Single instance creation, reuse across calls, configuration from environment variables. |
| `test_token_budget.py` | 19 | Context window management | Token counting, budget allocation across system prompt components, truncation when over budget, priority-based section trimming. |

### Security and Observability

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_audit_log.py` | 50 | Security event logging | Audit event recording for sensitive operations (profile access, document upload, letter generation). Hash chain integrity verification, tamper detection, event querying, log rotation. |
| `test_telemetry.py` | 26 | Metrics and observability | Request duration tracking, error rate metrics, API call counting, custom metric registration, metric export format. |
| `test_payments.py` | 26 | Stripe subscription lifecycle | Subscription creation, upgrade, downgrade, cancellation. Webhook event handling, payment failure recovery, trial period management. |

### Models and Data

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_models.py` | 40 | `backend/models/*.py` | Pydantic model validation for LegalProfile, LegalIssue, LegalFact, Conversation, Message, DemandLetter, RightsSummary, ActionChecklist. Field validation, serialization/deserialization, default values, constraint enforcement. |
| `test_content_store.py` | 35 | Knowledge base persistence | Content storage and retrieval. CRUD operations, content versioning, search by topic, bulk operations. |
| `test_lifecycle.py` | 40 | Full user conversation lifecycle | End-to-end user journey simulation. Onboarding through profile creation, first conversation, fact extraction, subsequent conversation with memory, action generation from accumulated context. |

### Property-Based Testing

| File | Tests | Module Under Test | What It Covers |
|------|------:|-------------------|----------------|
| `test_property_based.py` | 24 | Multiple modules | Hypothesis-driven property-based tests. Randomized inputs for classifier (always returns valid area), profile model (always serializable), prompt builder (never exceeds token limit). Discovers edge cases that manual test cases miss. |

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) and are included in the standard `make test` run:

```python
from hypothesis import given, strategies as st

@given(state=st.sampled_from(["MA", "CA", "NY", "TX", "FL"]),
       question=st.text(min_size=1, max_size=500))
def test_classifier_always_returns_valid_area(state, question):
    area = classify_legal_area(question)
    assert area in VALID_LEGAL_AREAS
```

Hypothesis settings are configured in `.hypothesis/` (gitignored).

---

## Frontend Test Suite

19 test files containing 143 tests, using Jest with React Testing Library.

### Component Tests

| File | Tests | What It Covers |
|------|------:|----------------|
| `ChatInterface.test.tsx` | 16 | Message display and formatting, user input handling, API call triggering on send, loading state during response, error display on API failure, memory indicator visibility, citation formatting in responses. |
| `LegalProfileSidebar.test.tsx` | 17 | Profile data display during chat, state and housing info rendering, active issues listing, legal facts display, live update when new facts are extracted, empty state when no profile exists, responsive collapse on mobile. |
| `OnboardingFlow.test.tsx` | 16 | 5-step wizard progression, input validation at each step (state selection, housing, employment, family status, active issues), back navigation, completion callback, data submission to API, error handling on submission failure. |
| `ActionGenerator.test.tsx` | 15 | Demand letter generation UI, rights summary generation, checklist generation, loading states during generation, generated content display, copy-to-clipboard, PDF download trigger, error handling. |
| `RightsGuide.test.tsx` | 16 | Rights library browser, guide list rendering, guide detail display, section navigation, citation display, state-specific filtering, search functionality. |
| `WorkflowWizard.test.tsx` | 14 | Guided workflow step display, step completion, progress tracking, workflow completion state, restart capability, step validation before progression. |
| `DocumentUpload.test.tsx` | 11 | File upload via drag-and-drop and file picker, upload progress indicator, extraction preview display, supported file type validation (PDF, images), file size limit enforcement, error handling on upload failure. |
| `DeadlineDashboard.test.tsx` | 11 | Deadline list rendering, status indicators (pending, completed, overdue), status toggle, deadline creation form, date validation, empty state display. |
| `CaseHistory.test.tsx` | 10 | Active issues timeline display, issue detail expansion, chronological ordering, status badges, note display, empty state when no issues exist. |
| `ConversationHistory.test.tsx` | 9 | Conversation list rendering, conversation selection and navigation, delete functionality with confirmation, timestamp display, empty state, active conversation highlighting. |
| `AttorneyCard.test.tsx` | 12 | Attorney referral card rendering, specialization display, contact information, location display, rating/review display, call-to-action buttons, multiple card layout. |
| `WaitlistForm.test.tsx` | 7 | Email input validation, form submission, success confirmation display, duplicate email handling, loading state during submission. |

### UI Component Tests

| File | What It Covers |
|------|----------------|
| `Button.test.tsx` | Rendering variants (primary, secondary, ghost), disabled state, click handler, loading state. |
| `Badge.test.tsx` | Color variants, text display, icon support. |
| `Card.test.tsx` | Content rendering, header/footer slots, hover state. |
| `Input.test.tsx` | Value binding, placeholder, error state, disabled state. |

### Integration Tests

| File | Tests | What It Covers |
|------|------:|----------------|
| `api.test.ts` | 9 | API client wrapper. Request formatting, response parsing, retry on 500 errors, authentication header injection, error response handling, base URL configuration. |
| `auth.test.tsx` | 8 | `useAuth` hook behavior. Session detection, login redirect, logout cleanup, token refresh, protected route enforcement, loading state during session check. |
| `supabase.test.ts` | 6 | Supabase client initialization. Environment variable usage, client singleton behavior, auth configuration. |

### Accessibility Testing

All component tests include WCAG accessibility checks via `jest-axe`:

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<ChatInterface />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

Every component is tested for keyboard navigation, ARIA labels, color contrast, and semantic HTML structure.

### Component Test Pattern

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '@/components/ChatInterface';

describe('ChatInterface', () => {
  it('renders message input', () => {
    render(<ChatInterface />);
    expect(screen.getByPlaceholderText('Type your legal question...')).toBeInTheDocument();
  });

  it('sends message on submit', async () => {
    const mockSend = jest.fn();
    render(<ChatInterface onSend={mockSend} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'test question' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    expect(mockSend).toHaveBeenCalledWith('test question');
  });
});
```

### Mocking the API Client

```typescript
jest.mock('@/lib/api', () => ({
  api: {
    chat: jest.fn().mockResolvedValue({ response: 'mocked response', legal_area: 'general' }),
    getProfile: jest.fn().mockResolvedValue({ state: 'MA', legal_facts: [] }),
  },
}));
```

---

## End-to-End Tests (Playwright)

E2E tests live in `web/e2e/` and cover critical user journeys through the full application stack.

### Smoke Tests (`smoke.spec.ts` -- 5 tests)

| Test | What It Verifies |
|------|-----------------|
| Landing page loads | Marketing page renders, CTA buttons visible, no console errors |
| Navigation works | All nav links route to correct pages, back/forward works |
| Onboarding flow completes | 5-step wizard can be filled and submitted end-to-end |
| Chat sends and receives | Message input, send action, response display with formatting |
| Profile displays after onboarding | Sidebar shows user data post-intake, facts visible |

### Configuration

```typescript
// playwright.config.ts
{
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  use: {
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
}
```

- **Browser:** Chromium only (keeps CI fast)
- **Timeout:** 30 seconds per test
- **Retries:** 2 retries in CI, 0 locally
- **Artifacts:** Screenshots on failure, traces on first retry, uploaded as CI artifacts

### Running E2E Tests

```bash
cd web
npx playwright test              # Run all E2E tests
npx playwright test --ui         # Interactive UI mode
npx playwright show-report       # View HTML report after run
npx playwright test --debug      # Step through tests in browser
```

---

## Test Fixtures and Mocking Strategy

All shared fixtures are defined in `tests/conftest.py`. They ensure no test makes real API calls.

### `mock_profile` -- Sarah Chen Demo Profile

Returns a fully populated `LegalProfile` for Sarah Chen, the demo user:

- **State:** Massachusetts (MA)
- **Housing:** Renter, month-to-month, no signed lease
- **Employment:** Full-time W2, marketing coordinator
- **Active issues:** 1 (landlord claiming $800 for bathroom tile damage, 3 notes)
- **Legal facts:** 8 (including no move-in inspection, pre-existing water damage, written 30-day notice)
- **Documents:** 2 references
- **Conversations:** 12
- **Member since:** January 15, 2026

```python
def test_something(self, mock_profile: LegalProfile) -> None:
    assert mock_profile.state == "MA"
    assert len(mock_profile.legal_facts) == 8
    assert len(mock_profile.active_issues) == 1
```

### `mock_anthropic_response` -- Claude Response Factory

A callable fixture that builds a `MagicMock` mimicking an Anthropic `messages.create` response. Pass the text you want Claude to "return":

```python
def test_something(self, mock_anthropic_response):
    response = mock_anthropic_response('{"new_facts": ["fact 1"]}')
    assert response.content[0].text == '{"new_facts": ["fact 1"]}'
```

### `mock_anthropic` -- Patched Anthropic Client

Patches `anthropic.AsyncAnthropic` globally. Default return value: `{"new_facts": []}`. Override per test:

```python
def test_something(self, mock_anthropic, mock_anthropic_response):
    mock_anthropic.messages.create.return_value = mock_anthropic_response("custom text")
```

### `mock_supabase` -- Patched Supabase Client

Patches `backend.memory.profile._get_supabase` to intercept all `.table().select()...` and `.table().upsert()...` chains. Default: select returns `None`, upsert returns empty list.

```python
async def test_profile_lookup(self, mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value \
        .maybe_single.return_value.execute.return_value.data = {
        "user_id": "test-user",
        "state": "MA",
    }
```

### Mocking Patterns

**Anthropic API:** Always patched via `mock_anthropic`. The client is a `MagicMock` with `messages.create` as an `AsyncMock`.

**Supabase:** Always patched via `mock_supabase`. Intercepts chained method calls on `.table()`.

**Redis:** Mock `_get_redis()` in `backend/utils/rate_limiter.py` when testing rate limiting:

```python
from unittest.mock import patch, AsyncMock

async def test_rate_limit_exceeded(self):
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 21  # Over the 20/min limit
    mock_redis.expire = AsyncMock()
    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        # Test that the endpoint returns 429
```

**No real network calls:** Tests never hit Anthropic, Supabase, or Redis. If a test accidentally makes a real call, it will fail due to missing credentials in the test environment.

### Frontend Mocking

API client mocking:

```typescript
jest.mock('@/lib/api', () => ({
  api: {
    chat: jest.fn().mockResolvedValue({ response: 'mocked response', legal_area: 'general' }),
    getProfile: jest.fn().mockResolvedValue({ state: 'MA', legal_facts: [] }),
  },
}));
```

Supabase client mocking:

```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    auth: { getSession: jest.fn().mockResolvedValue({ data: { session: mockSession } }) },
    from: jest.fn().mockReturnValue({ select: jest.fn().mockReturnThis(), eq: jest.fn() }),
  },
}));
```

---

## Coverage Thresholds

### Backend Coverage

Enforced via `pytest-cov`. Minimum threshold: **90%** overall.

| Module | Target | Rationale |
|--------|--------|-----------|
| `backend/memory/injector.py` | 100% | Core product differentiator. No untested code paths. |
| `backend/memory/updater.py` | 90%+ | Background task with multiple error handling branches. |
| `backend/legal/classifier.py` | 90%+ | All 10 legal domains must be classified correctly. |
| `backend/actions/` | 90%+ | All three generators (letter, rights, checklist). |
| `backend/utils/` | 85%+ | Auth, rate limiting, retry logic. |
| Overall backend | 90% | Enforced threshold in CI. |

### Frontend Coverage

Enforced via Jest. Thresholds in `jest.config.ts`:

| Metric | Threshold |
|--------|-----------|
| Branch coverage | 60% |
| Line coverage | 70% |

### Reading Coverage Output

```
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
backend/memory/injector.py           45      0   100%
backend/memory/updater.py            38      3    92%   67-69
backend/legal/classifier.py          52      4    92%   88-91
```

- **Stmts:** Total executable statements in the file
- **Miss:** Statements not executed by any test
- **Cover:** Percentage of statements covered
- **Missing:** Line numbers to target with new tests

---

## Adding New Tests

### Backend: Adding a Test File

1. Create `tests/test_<module>.py` matching the module you are testing.

2. Import shared fixtures from `conftest.py`:

   ```python
   from backend.models.legal_profile import LegalProfile
   ```

3. Create a test class describing the behavior under test:

   ```python
   class TestNewFeatureBehavior:
       """Tests for the new feature's specific behavior."""
   ```

4. Use fixtures as method parameters:

   ```python
   async def test_does_something(self, mock_profile, mock_anthropic):
   ```

5. Follow the **Arrange, Act, Assert** pattern:

   ```python
   async def test_extracts_deadline_from_conversation(
       self, mock_anthropic, mock_anthropic_response, mock_supabase
   ):
       # Arrange
       mock_anthropic.messages.create.return_value = mock_anthropic_response(
           '[{"title": "File complaint", "date": "2026-04-15"}]'
       )

       # Act
       result = await detect_deadlines(user_id="test", conversation=[...])

       # Assert
       assert len(result) == 1
       assert result[0].title == "File complaint"
   ```

6. One behavior per test method. Each test should verify one specific thing.

7. Run and verify:

   ```bash
   python -m pytest tests/test_new_module.py -v
   ```

### Frontend: Adding a Component Test

1. Create `web/__tests__/components/<Component>.test.tsx`.

2. Use React Testing Library:

   ```typescript
   import { render, screen, fireEvent } from '@testing-library/react';
   import { MyComponent } from '@/components/MyComponent';

   describe('MyComponent', () => {
     it('renders the expected content', () => {
       render(<MyComponent data={mockData} />);
       expect(screen.getByText('Expected Text')).toBeInTheDocument();
     });

     it('handles user interaction', async () => {
       const onAction = jest.fn();
       render(<MyComponent onAction={onAction} />);
       fireEvent.click(screen.getByRole('button', { name: /submit/i }));
       expect(onAction).toHaveBeenCalledTimes(1);
     });

     it('has no accessibility violations', async () => {
       const { container } = render(<MyComponent />);
       const results = await axe(container);
       expect(results).toHaveNoViolations();
     });
   });
   ```

3. Mock external dependencies at the top of the file:

   ```typescript
   jest.mock('@/lib/api', () => ({ api: { myEndpoint: jest.fn() } }));
   ```

4. Run:

   ```bash
   cd web && npm test -- MyComponent
   ```

### E2E: Adding a Playwright Test

1. Create or add to a spec file in `web/e2e/`.

2. Use the Playwright `page` fixture:

   ```typescript
   import { test, expect } from '@playwright/test';

   test('user can complete the new flow', async ({ page }) => {
     await page.goto('/new-feature');
     await page.fill('[data-testid="input"]', 'test value');
     await page.click('[data-testid="submit"]');
     await expect(page.locator('[data-testid="result"]')).toBeVisible();
   });
   ```

3. Run:

   ```bash
   cd web && npx playwright test e2e/new-flow.spec.ts
   ```

### Test Organization Conventions

- **Backend:** Tests use class-based grouping (e.g., `TestBuildSystemPromptIncludesProfileData`) to logically group related assertions. Each test method verifies one specific behavior. See `test_memory_injector.py` for the canonical example -- it has 6 test classes covering profile data, state laws, active issues, legal facts, response rules, and legal area classification.

- **Frontend:** Tests use `describe` blocks for grouping and `it` blocks for individual assertions. Each component gets its own test file.

- **E2E:** Tests are organized by user journey, not by page. Each spec file covers a complete flow.

---

## CI/CD Integration

### Pre-Commit Gate

`make verify` is the pre-commit gate. It runs linting and the full test suite:

```bash
make verify
# Equivalent to:
#   ruff check backend/ tests/
#   ruff format --check backend/ tests/
#   python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing
```

If any lint error or test failure occurs, `make verify` exits non-zero. **Never commit with a failing `make verify`.**

### CI Pipeline

The CI pipeline runs on every push and pull request:

1. **Lint:** `ruff check` and `ruff format --check` on all Python files
2. **Backend tests:** `pytest` with coverage enforcement (90% threshold)
3. **Frontend tests:** `jest` with coverage thresholds (60% branch, 70% line)
4. **E2E tests:** Playwright with Chromium, 2 retries on failure
5. **Artifacts:** Coverage reports, Playwright screenshots/traces uploaded on failure

### Test Execution Order

Tests are independent and can run in any order. There are no inter-test dependencies. The CI pipeline runs backend and frontend tests in parallel for speed.

### Failure Handling

- **Backend test failure:** CI fails, coverage report shows uncovered lines
- **Frontend test failure:** CI fails, Jest output shows failing assertions
- **E2E test failure:** CI retries twice, then fails with screenshot and trace artifacts
- **Coverage below threshold:** CI fails even if all tests pass

---

## Related Documentation

- [UTILS.md](UTILS.md) -- Backend utilities that are heavily tested
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) -- The memory system, most critical to test
- [MODELS.md](MODELS.md) -- Pydantic models used in test fixtures
