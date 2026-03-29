# CI/CD Pipeline

GitHub Actions workflow defined in `.github/workflows/ci.yml`. Two parallel jobs run on every push to `main`/`dev` and every PR targeting `main`.

## Triggers

```yaml
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]
```

## Jobs

### 1. Backend: `lint-and-test`

**Runner:** `ubuntu-latest` with Python 3.12.

| Step | Command | What It Checks |
|------|---------|----------------|
| Install deps | `pip install -e ".[dev]" pytest-cov` | All Python packages from `pyproject.toml` |
| Lint | `ruff check backend/ tests/` | Import order, unused imports, style rules |
| Typecheck | `mypy backend/` | Static type analysis (no `Any` allowed per project rules) |
| Test | `pytest tests/ -v --tb=short --cov=backend --cov-report=term-missing` | Full test suite with coverage report |

Environment variables are set to dummy values so tests can run without real credentials:

```
ANTHROPIC_API_KEY=test-key
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test-key
SUPABASE_ANON_KEY=test-key
SUPABASE_SERVICE_ROLE_KEY=test-key
SUPABASE_JWT_SECRET=test-jwt-secret
REDIS_URL=""                          # Empty = rate limiter fails open
```

### 2. Frontend: `web-build`

**Runner:** `ubuntu-latest` with Node 20.

| Step | Command | What It Checks |
|------|---------|----------------|
| Install + build | `cd web && npm ci && npm run build` | TypeScript compilation, Next.js static analysis, build output |

Environment variables for the build:

```
NEXT_PUBLIC_SUPABASE_URL=https://test.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=<dummy JWT>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Equivalents (Makefile)

The CI pipeline mirrors commands available locally via `make`. See `CLAUDE.md` for the full Makefile reference.

| CI Step | Local Command |
|---------|---------------|
| `ruff check backend/ tests/` | `make lint` |
| `ruff format --check backend/ tests/` | `make lint` (included) |
| `mypy backend/` | `make typecheck` |
| `pytest tests/ -v --cov=backend` | `make test` |
| `cd web && npm ci && npm run build` | `cd web && npm run build` |
| All backend gates | `make verify` (runs lint + test) |

**Rule:** Run `make verify` before every commit. CI will catch the same issues but the feedback loop is slower.

## What Is Not in CI (Yet)

- **Mobile build** -- The Expo React Native app (`mobile/`) has no CI job. Builds are done locally via `npx expo start`.
- **E2E tests** -- No Playwright or Cypress pipeline. Only unit/integration tests via pytest.
- **Deployment** -- No CD step. The pipeline is lint/test/build only.
- **Caching** -- No pip or npm cache configured. Each run installs from scratch.
- **Coverage threshold** -- Coverage is reported but not enforced with a minimum percentage.

## Adding New CI Steps

To add a step, edit `.github/workflows/ci.yml`. Keep backend and frontend jobs independent (they run in parallel). If adding a mobile job, use `actions/setup-node@v4` with Node 20 and run `cd mobile && npm ci && npx expo export --platform web` as a smoke test.
