# Testing

CaseMate uses pytest with pytest-asyncio for async tests and pytest-cov for coverage reporting.

See `CONTRIBUTING.md` for setup instructions and commit workflow.

## Running Tests

```bash
make test       # python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing
make verify     # lint + test — run before every commit
```

Configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

`asyncio_mode = "auto"` means all `async def test_*` functions are automatically treated as async tests without needing the `@pytest.mark.asyncio` decorator.

### Running Specific Tests

```bash
# Run a single test file
python -m pytest tests/test_memory_injector.py -v

# Run a single test class
python -m pytest tests/test_memory_injector.py::TestBuildSystemPromptIncludesProfileData -v

# Run a single test method
python -m pytest tests/test_memory_injector.py::TestBuildSystemPromptIncludesProfileData::test_includes_state -v

# Run with full output (no truncation)
python -m pytest tests/test_memory_injector.py -v --tb=long

# Run with coverage for a specific module
python -m pytest tests/test_memory_injector.py --cov=backend.memory.injector --cov-report=term-missing
```

## Test Files

There are 24 test files in `tests/`:

| File | What it tests |
|------|--------------|
| `test_memory_injector.py` | **Priority 1.** System prompt assembly in `backend/memory/injector.py`. Verifies profile data, state laws, active issues, legal facts, response rules, legal area classification, and federal fallback all appear correctly in the prompt. |
| `test_profile_updater.py` | Background fact extraction in `backend/memory/updater.py`. |
| `test_legal_classifier.py` | Legal area classification in `backend/legal/classifier.py`. |
| `test_action_generators.py` | Demand letter, rights summary, and checklist generation in `backend/actions/`. |
| `test_api_endpoints.py` | FastAPI route integration tests against `backend/main.py`. |
| `test_auth.py` | JWT verification in `backend/utils/auth.py`. |
| `test_rate_limiter.py` | Redis-backed rate limiting in `backend/utils/rate_limiter.py`. |
| `test_client_singleton.py` | Anthropic client singleton in `backend/utils/client.py`. |
| `test_document_analyzer.py` | Document analysis pipeline in `backend/documents/analyzer.py`. |
| `test_conversation_store.py` | Conversation CRUD in `backend/memory/conversation_store.py`. |
| `test_deadline_detector.py` | Deadline detection from conversations in `backend/deadlines/detector.py`. |
| `test_deadline_tracker.py` | Deadline CRUD operations in `backend/deadlines/tracker.py`. |
| `test_email_sender.py` | Email export in `backend/export/email_sender.py`. |
| `test_pdf_generator.py` | PDF document generation in `backend/export/pdf_generator.py`. |
| `test_referral_matcher.py` | Attorney matching in `backend/referrals/matcher.py`. |
| `test_rights_library.py` | Rights guide lookups in `backend/knowledge/rights_library.py`. |
| `test_workflow_engine.py` | Workflow instance management in `backend/workflows/engine.py`. |
| `test_workflow_templates.py` | Workflow template definitions in `backend/workflows/templates/`. |
| `test_models.py` | Pydantic model validation and serialization. |
| `test_retry.py` | Exponential backoff retry logic in `backend/utils/retry.py`. |
| `test_concurrency.py` | Concurrency utilities and thread safety. |
| `test_idempotency.py` | Idempotency key handling for API operations. |
| `test_lifecycle.py` | Application lifecycle (startup/shutdown) hooks. |
| `test_content_store.py` | Content storage and retrieval. |
| `test_audit_log.py` | Audit logging for sensitive operations. |

## Shared Fixtures

All shared fixtures are in `tests/conftest.py`. These ensure no test hits a real API.

### `mock_profile` — Sarah Chen demo profile

Returns a fully populated `LegalProfile` instance for Sarah Chen, a Massachusetts renter with an active landlord/tenant security deposit dispute. Includes 8 known legal facts, 1 active issue with 3 notes, and 2 document references. This is the same profile used in the demo.

```python
# Usage in any test:
def test_something(self, mock_profile: LegalProfile) -> None:
    assert mock_profile.state == "MA"
    assert len(mock_profile.legal_facts) == 8
```

### `mock_anthropic_response` — Factory for Claude responses

A callable fixture that builds a properly shaped `MagicMock` mimicking an Anthropic `messages.create` response. Pass the text you want Claude to "return":

```python
def test_something(self, mock_anthropic_response):
    response = mock_anthropic_response('{"new_facts": ["fact 1"]}')
    assert response.content[0].text == '{"new_facts": ["fact 1"]}'
```

### `mock_anthropic` — Patched Anthropic client

Patches `anthropic.AsyncAnthropic` globally so no real API calls are made. The default return value is `{"new_facts": []}`. Override per test:

```python
def test_something(self, mock_anthropic, mock_anthropic_response):
    mock_anthropic.messages.create.return_value = mock_anthropic_response("custom text")
```

### `mock_supabase` — Patched Supabase client

Patches `backend.memory.profile._get_supabase` to intercept all `table().select()...` and `table().upsert()...` call chains. Default behavior: select returns `None` (no profile), upsert returns empty list.

## Mocking Patterns

- **Anthropic API:** Always patched via `mock_anthropic`. The client is a `MagicMock` with `messages.create` as an `AsyncMock`.
- **Supabase:** Always patched via `mock_supabase`. The client intercepts chained method calls on `.table()`.
- **No real network calls:** Tests never hit Anthropic, Supabase, or Redis. If a test needs Redis behavior, mock the `_get_redis()` function in `backend/utils/rate_limiter.py`.

### How to Mock Specific Behaviors

#### Mock a Claude response with custom JSON

```python
async def test_fact_extraction(self, mock_anthropic, mock_anthropic_response):
    mock_anthropic.messages.create.return_value = mock_anthropic_response(
        '{"new_facts": ["Landlord did not return deposit within 30 days"]}'
    )
    # Now call the function under test — it will get this response from Claude
```

#### Mock a Supabase query result

```python
async def test_profile_lookup(self, mock_supabase):
    # Configure the mock to return a profile dict
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = {
        "user_id": "test-user",
        "state": "MA",
        # ... other fields
    }
```

#### Mock Redis for rate limiting

```python
from unittest.mock import patch, AsyncMock

async def test_rate_limit_exceeded(self):
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 21  # Over the 20/min limit
    mock_redis.expire = AsyncMock()
    with patch("backend.utils.rate_limiter._get_redis", return_value=mock_redis):
        # Test that the endpoint returns 429
```

## Test Organization

Tests use class-based grouping (e.g. `TestBuildSystemPromptIncludesProfileData`) to logically group related assertions. Each test method verifies one specific behavior. See `test_memory_injector.py` for the canonical example — it has 6 test classes covering profile data, state laws, active issues, legal facts, response rules, and legal area classification.

### Writing a New Test — Step by Step

1. **Identify the module** you're testing and find or create the corresponding test file (`tests/test_{module}.py`)

2. **Create a test class** that describes what you're testing:
   ```python
   class TestNewFeatureBehavior:
       """Tests for the new feature's specific behavior."""
   ```

3. **Use fixtures** from `conftest.py` as function parameters:
   ```python
   async def test_does_something(self, mock_profile, mock_anthropic):
   ```

4. **Arrange → Act → Assert** pattern:
   ```python
   async def test_extracts_deadline_from_conversation(
       self, mock_anthropic, mock_anthropic_response, mock_supabase
   ):
       # Arrange: set up mock responses
       mock_anthropic.messages.create.return_value = mock_anthropic_response(
           '[{"title": "File complaint", "date": "2026-04-15"}]'
       )

       # Act: call the function under test
       result = await detect_deadlines(user_id="test", conversation=[...])

       # Assert: verify the expected behavior
       assert len(result) == 1
       assert result[0].title == "File complaint"
   ```

5. **One assertion per test** (when practical) — each test method should verify one specific behavior

6. **Run your test** to verify it passes:
   ```bash
   python -m pytest tests/test_new_module.py -v
   ```

## Frontend Testing

The web frontend uses **Jest** + **React Testing Library** for component and integration tests.

### Setup

```bash
cd web
npm test              # Run all tests
npm test -- --watch   # Watch mode for development
npm test -- --coverage # With coverage report
```

### Test Files

Frontend tests are co-located with components or in `web/__tests__/`:

| File Pattern | What it tests |
|-------------|---------------|
| `__tests__/components/*.test.tsx` | React component rendering and interaction |
| `__tests__/api/*.test.ts` | API client functions |
| `__tests__/auth/*.test.tsx` | Authentication flow |
| `__tests__/supabase/*.test.ts` | Supabase client integration |

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

## Property-Based Testing (Hypothesis)

CaseMate uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing, which generates randomized inputs to discover edge cases that manual test cases miss.

```python
from hypothesis import given, strategies as st

@given(state=st.sampled_from(["MA", "CA", "NY", "TX", "FL"]),
       question=st.text(min_size=1, max_size=500))
def test_classifier_always_returns_valid_area(state, question):
    area = classify_legal_area(question)
    assert area in VALID_LEGAL_AREAS
```

Property-based tests are in `tests/test_models.py` and integrated into the standard `make test` run. Hypothesis settings are configured in `.hypothesis/` (gitignored).

## Accessibility Testing (jest-axe)

Frontend components are tested for WCAG accessibility compliance using [jest-axe](https://github.com/nickcolley/jest-axe):

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<ChatInterface />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## End-to-End Testing (Playwright)

Critical user journeys are covered by Playwright E2E tests:

```bash
cd web && npx playwright test              # Run all E2E tests
cd web && npx playwright test --ui         # Interactive UI mode
cd web && npx playwright show-report       # View HTML report
```

E2E tests cover:
- Onboarding flow (5-question intake wizard)
- Chat interface (send message, receive response, memory indicator)
- Profile updates (sidebar reflects conversation-extracted facts)

Test artifacts (screenshots, traces) are captured on failure and uploaded as CI artifacts.

## Coverage

Coverage is reported for the `backend/` package via `--cov=backend --cov-report=term-missing`. The `term-missing` report shows which lines are not covered.

### Coverage Targets

| Module | Target | Notes |
|--------|--------|-------|
| Overall backend | 87% | Current threshold |
| `backend/memory/injector.py` | 100% | Core differentiator — no untested paths |
| `backend/memory/updater.py` | 90%+ | Background task with error handling branches |
| `backend/legal/classifier.py` | 90%+ | All 10 domains + edge cases |
| `backend/actions/` | 90%+ | All three generators |
| `backend/utils/` | 85%+ | Auth, rate limiting, retry |

### Reading Coverage Output

```
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
backend/memory/injector.py           45      0   100%
backend/memory/updater.py            38      3    92%   67-69
backend/legal/classifier.py          52      4    92%   88-91
```

- `Stmts`: Total executable statements
- `Miss`: Statements not covered by any test
- `Cover`: Percentage covered
- `Missing`: Line numbers not covered — these are what you need to test

### CI Integration

`make verify` runs `make lint` then `make test`. This is the pre-commit gate:

```bash
make verify
# Equivalent to:
#   ruff check backend/ tests/
#   ruff format --check backend/ tests/
#   python -m pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing
```

If any lint error or test failure occurs, `make verify` exits non-zero. **Never commit with a failing `make verify`.**

---

## Related

- [UTILS.md](UTILS.md) — Backend utilities that are heavily tested
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — The system most critical to test
- [MODELS.md](MODELS.md) — Pydantic models used in test fixtures
