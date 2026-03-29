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

## Test Files

There are 18 test files in `tests/`:

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

## Test Organization

Tests use class-based grouping (e.g. `TestBuildSystemPromptIncludesProfileData`) to logically group related assertions. Each test method verifies one specific behavior. See `test_memory_injector.py` for the canonical example — it has 6 test classes covering profile data, state laws, active issues, legal facts, response rules, and legal area classification.

## Coverage

Coverage is reported for the `backend/` package via `--cov=backend --cov-report=term-missing`. The `term-missing` report shows which lines are not covered. The memory injector (`backend/memory/injector.py`) should always have 100% coverage.
