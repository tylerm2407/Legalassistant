# Contributing to CaseMate

## Setup

1. Clone the repo and install dependencies:

```bash
make install    # pip install -e ".[dev]" + cd web && npm install
```

2. Copy `.env.example` to `.env` and fill in all required keys (see comments in `.env.example`).

3. Start the backend:

```bash
make dev        # uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

4. Start the frontend (separate terminal):

```bash
make frontend   # cd web && npm run dev (port 3000)
```

5. Verify health: `GET http://localhost:8000/health` should return `{"status": "ok", "version": "0.4.0"}`.

## Dev Workflow

Run these commands from the project root via `Makefile`:

| Command | What it does |
|---------|-------------|
| `make dev` | Start backend on port 8000 with hot reload |
| `make frontend` | Start Next.js frontend on port 3000 |
| `make test` | Full pytest suite with coverage (`--cov=backend --cov-report=term-missing`) |
| `make lint` | `ruff check` + `ruff format --check` on `backend/` and `tests/` |
| `make format` | Auto-fix lint issues and reformat code |
| `make typecheck` | `mypy backend/` in strict mode |
| `make verify` | Runs `lint` then `test` — **must pass before every commit** |
| `make seed` | Seed the Sarah Chen demo profile via `scripts/seed_demo.py` |
| `make clean` | Remove `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` |

## Code Standards

These are non-negotiable. See `pyproject.toml` for full ruff/mypy configuration.

### Docstrings on every class and public method

Every class and every public function must have a docstring explaining what it does, its args, and return value. See `backend/memory/injector.py` (`build_system_prompt`) or `backend/models/legal_profile.py` (`LegalProfile`) for the expected style.

### Type annotations everywhere — no `Any`

All function signatures must have full type annotations. The ruff rule set (`ANN` selectors in `pyproject.toml`) enforces this. Use `from __future__ import annotations` at the top of every module.

### Structured logging with user context

Use `structlog` via `backend/utils/logger.py`. Always include `user_id` in log calls for traceability.

```python
from backend.utils.logger import get_logger
_logger = get_logger(__name__)
_logger.info("profile_updated", user_id=user_id, facts_added=3)
```

Never use `print()`. Never use bare `except:`.

### Retry on all Anthropic API calls

Wrap every Claude API call with `@retry_anthropic` from `backend/utils/retry.py`. This provides exponential backoff (3 attempts, 2s/4s/8s) via `tenacity`.

### Ruff configuration

- Target: Python 3.12 (`target-version = "py312"`)
- Line length: 100
- Enabled rule sets: `E`, `F`, `I`, `N`, `W`, `UP`, `B`, `SIM`, `ANN`
- Tests are exempted from annotation rules (see `per-file-ignores` in `pyproject.toml`)

## Commit Message Format

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `test`, `docs`, `chore`, `refactor`, `style`

**Scopes:** `memory`, `onboarding`, `chat`, `actions`, `documents`, `ui`, `api`

Examples:

```
feat(memory): profile injection working end-to-end
fix(memory): profile updater now handles missing state field
test(memory): add tests for inject with empty legal_facts
docs(decisions): add ADR 003 for profile update strategy
chore: update PROGRESS.md
```

## PR Process

1. Create a feature branch from `main`.
2. Run `make verify` — zero failures required.
3. Commit with the format above. Commit every 45-60 minutes minimum.
4. Open a PR with a clear description of what changed and why.
5. All tests must pass and lint must be clean before merge.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests pass but coverage seems low | Make sure you run `pytest tests/ --cov=backend --cov-report=term-missing`. The `--cov=backend` flag is required to measure backend coverage. |
| Supabase connection error | Check that `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` are set correctly in `.env`. Copy from `.env.example` if missing. |
| "Redis not configured" warning | This is expected if `REDIS_URL` is not set. Rate limiting fails open — requests are allowed without Redis. No action needed for local development. |
| How do I create the demo profile? | Run `make seed` — this runs `scripts/seed_demo.py` to create the Sarah Chen demo profile with 12 prior conversations. |
| mypy errors on fresh install | Run `make install` first, then `mypy backend/`. The dev dependencies include type stubs. |
| Frontend tests fail with module errors | Run `cd web && npm install` to ensure all frontend dependencies are installed. |

## Development Approach

CaseMate is developed with [Claude Code](https://claude.ai/code), Anthropic's AI development CLI. Every commit is co-authored with Claude Opus 4.6. The workflow:

1. Architecture decisions documented in ADRs (`docs/decisions/`)
2. Implementation with Claude Code (memory injection, legal modules, tests)
3. `make verify` before every commit (lint + 605 tests: 462 backend + 143 frontend)
4. `cd web && npx playwright test` for E2E tests
4. CI/CD validates on push, deploys on merge to main

## Architecture

See `ARCHITECTURE.md` for the full system design. The memory injection pattern in `backend/memory/injector.py` is the core differentiator — protect it above everything else.
