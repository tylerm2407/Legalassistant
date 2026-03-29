<div align="center">

# CaseMate

**Personalized legal guidance powered by persistent memory.**

The average US lawyer charges $349/hour. The average American earns $52,000/year.
CaseMate closes that gap with AI that remembers your situation, knows your state's laws, and gives specific, actionable legal guidance for $20/month.

[![Build Status](https://img.shields.io/github/actions/workflow/status/tylerm2407/Legalassistant/ci.yml?branch=main&label=CI)](https://github.com/tylerm2407/Legalassistant/actions)
[![Backend Tests](https://img.shields.io/badge/backend_tests-528-blue)](tests/)
[![Frontend Tests](https://img.shields.io/badge/frontend_tests-143-blue)](web/__tests__/)
[![Built with Claude Code](https://img.shields.io/badge/Built_with-Claude_Code-6B57FF?logo=claude)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)

[Architecture](ARCHITECTURE.md) · [API Docs](#api-reference) · [Contributing](CONTRIBUTING.md)

</div>

---

## The Problem

**130 million Americans** cannot afford a lawyer when they need one. The ABA reports that 50% of US households face at least one legal issue per year, and the Legal Services Corporation found that 86% of civil legal problems receive inadequate or no legal help. People Google their rights, get generic answers that ignore their state and situation, and give up.

CaseMate replaces the first hour with a lawyer for most common legal issues -- at 1/17th the cost of a single consultation.

---

## How CaseMate Works

CaseMate is not a generic chatbot with a legal wrapper. Every response is assembled from three layers of context specific to the user asking the question.

```mermaid
flowchart TD
    A["User asks a legal question"] --> B["classify_legal_area()"]
    B -->|"Hybrid classifier: keyword match\nthen LLM fallback (~0ms or ~1s)"| C["Load LegalProfile from Supabase"]
    C --> D["build_system_prompt()"]
    D -->|"Assembles 3 layers"| E["Layer 1: User's legal profile\n(state, housing, employment, facts, issues)"]
    D --> F["Layer 2: State-specific statutes\n(50 states x 10 legal domains)"]
    D --> G["Layer 3: CaseMate response philosophy\n(cite statutes, calculate damages, next steps)"]
    E --> H["Claude API"]
    F --> H
    G --> H
    H --> I["Personalized, jurisdiction-aware response"]
    I --> J["Background task: extract new facts"]
    J --> K["Update LegalProfile in Supabase"]
    K -->|"Memory compounds\nover time"| C
```

**The compounding effect:** A user mentions their landlord skipped the move-in inspection in conversation 3. CaseMate extracts that as a legal fact. In conversation 7, when they ask about their security deposit, CaseMate already knows -- no re-explanation needed. The profile is a structured Pydantic model that grows with every interaction, not raw chat history that fills a context window and gets forgotten.

---

## Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Persistent Legal Memory** | Legal profile auto-updates from every conversation. Facts, issues, and documents compound over time. LLM-powered conversation summarizer preserves legal facts, statutes, and action items across long histories. | Complete |
| **State-Specific Legal Context** | 50 US states, 10 legal domains, 500+ statute entries organized by region. Real citations, not vague references. | Complete |
| **Document Analysis** | Upload leases, contracts, court notices. PDF/image text extraction with AI-powered fact and red flag identification. | Complete |
| **Action Generator** | Generate demand letters, rights summaries, and next-steps checklists -- pre-filled with your profile data and statute citations. | Complete |
| **Deadline Tracking** | Auto-detected from conversations or manually created. Dashboard with status management (active/completed/dismissed/expired). | Complete |
| **Guided Workflows** | 6 step-by-step legal process templates (eviction defense, wage claim filing, small claims, etc.) with localStorage persistence. | Complete |
| **Know Your Rights Library** | 19 comprehensive guides across 10 legal domains with rights, action steps, deadlines, and citations. | Complete |
| **Attorney Referral Matching** | State and specialty-based attorney search with weighted relevance scoring algorithm. | Complete |
| **PDF Export** | Generate branded PDFs of letters, summaries, and checklists. | Complete |
| **Email Export** | Send generated documents via email. | Requires SMTP config |
| **SSE Streaming Chat** | Real-time chat via Server-Sent Events. Backend streams from Anthropic Claude. | Complete |
| **Hybrid Classifier** | Keyword-first classification with LLM fallback for ambiguous queries. ~0ms fast path, ~1s fallback. | Complete |
| **LLM Router** | Anthropic Claude (claude-sonnet-4-20250514) with circuit-breaker protection and per-provider metrics. | Complete |
| **Prompt Caching** | Anthropic prompt caching with static/dynamic content split via `cache_control` for reduced latency and cost. | Complete |
| **Stripe Checkout** | Webhook handling (checkout, invoice, cancellation) and Pro tier checkout integrated. | Complete |
| **Subscription Tracking** | Persistent subscription status in Supabase with free tier gating. | In Progress |
| **Real OCR Pipeline** | Document text extraction via pytesseract + Pillow for image-based legal documents. Requires Tesseract installed. | Complete |
| **Security Headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, and Referrer-Policy on all responses. | Complete |
| **Spanish i18n** | Full Spanish translation of all UI text with language toggle. | Complete |
| **Cross-Platform** | Web (Next.js) + iOS/Android (Expo React Native). | Complete |

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend"
        WEB["Next.js 16\nApp Router + TypeScript + Tailwind"]
        MOBILE["Expo React Native\nExpo Router"]
    end

    subgraph "Backend"
        API["FastAPI\nPython 3.12"]
        MEM["Memory Injector\nbuild_system_prompt()"]
        UPD["Profile Auto-Updater\nBackground task"]
        LEG["Legal Intelligence\n50 states x 10 domains"]
        ACT["Action Generators\nLetters / Rights / Checklists"]
        DOC["Document Pipeline\nPDF extraction + analysis"]
        WF["Workflows + Deadlines\nGuided processes"]
        REF["Attorney Referrals\nWeighted scoring"]
        EXP["Export Engine\nPDF + Email"]
    end

    subgraph "External Services"
        CLAUDE["Anthropic Claude\nchat + classification"]
        SUPA["Supabase\nPostgres + Auth + Storage"]
        STRIPE["Stripe\nSubscription billing"]
        MC["Mailchimp\nWaitlist management"]
    end

    WEB -->|"REST + SSE"| API
    MOBILE -->|"REST + SSE"| API
    API --> MEM
    API --> ACT
    API --> DOC
    API --> WF
    API --> REF
    API --> EXP
    MEM --> LEG
    MEM --> CLAUDE
    UPD --> CLAUDE
    DOC --> CLAUDE
    ACT --> CLAUDE
    API --> SUPA
    UPD --> SUPA
    DOC --> SUPA
    API --> STRIPE
    API --> MC
```

For the full technical deep dive -- data flow diagrams, database schema, memory injection internals, and the legal intelligence layer -- see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS | SSR, App Router, type-safe UI |
| Mobile | Expo, React Native, Expo Router | Cross-platform iOS/Android from shared TypeScript |
| Backend | FastAPI, Python 3.12 | Async API, background tasks, SSE streaming |
| AI | Anthropic Claude (claude-sonnet-4-20250514) | Chat, legal reasoning, domain classification, fact extraction |
| Database | Supabase (PostgreSQL) | Structured profiles, conversations, documents, RLS |
| Auth | Supabase Auth (JWT) | User authentication with Row Level Security |
| File Storage | Supabase Storage | Document uploads tied to user auth |
| Payments | Stripe | Subscription billing and webhook lifecycle |
| Validation | Pydantic v2 | Strict typing on all models and API contracts |
| PDF Extraction | pdfplumber | Text extraction from uploaded legal documents |
| OCR | pytesseract + Pillow | Image-based document text extraction |
| Logging | structlog | Structured logging with user_id context |
| Development | Claude Code (Anthropic) | AI-assisted architecture, implementation, testing, and deployment |
| Deployment | Vercel (frontend) + Railway (backend) | Production hosting with CI/CD |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase account (database + auth + storage)
- Anthropic API key

### 1. Clone and install

```bash
git clone https://github.com/tylerm2407/Legalassistant.git
cd Legalassistant

# Backend
cp .env.example .env          # Add your API keys (see .env.example for all variables)
pip install -e ".[dev]"

# Frontend
cd web && npm install && cd ..

# Mobile (optional)
cd mobile && npm install && cd ..
```

### 2. Configure environment

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Optional
REDIS_URL=                    # Rate limiting (fail-open if empty)
MAILCHIMP_API_KEY=            # Waitlist sync
```

### 3. Run

```bash
# Backend (port 8000)
make dev

# Frontend (port 3000)
cd web && npm run dev

# Verify everything works
curl http://localhost:8000/health
```

### Makefile commands

| Command | Description |
|---------|-------------|
| `make dev` | Start backend on port 8000 |
| `make test` | Run full test suite with coverage |
| `make lint` | Run ruff check + format check |
| `make format` | Auto-fix lint and formatting |
| `make verify` | Lint + test (run before every commit) |
| `make seed` | Seed demo profile (Sarah Chen) |
| `make install` | Install all dependencies |
| `make deploy` | Deploy backend + frontend to production |
| `make verify-deploy` | Verify live deployment health + security headers |
| `make e2e` | Run Playwright E2E tests |

---

## Project Structure

```
casemate/
├── backend/
│   ├── main.py                    # FastAPI app, all route definitions
│   ├── memory/                    # Profile injection, auto-updater, conversation store
│   ├── legal/                     # Classifier, state laws (50 states), 10 legal domains
│   │   ├── states/                # Regional state law files (northeast, southeast, etc.)
│   │   └── areas/                 # One module per legal domain
│   ├── actions/                   # Demand letter, rights summary, checklist generators
│   ├── documents/                 # PDF/image extraction + Claude analysis
│   ├── knowledge/                 # Know Your Rights library (19 guides)
│   ├── workflows/                 # Guided legal workflow engine (6 templates)
│   ├── deadlines/                 # Deadline detection + tracking
│   ├── referrals/                 # Attorney matching with weighted scoring
│   ├── export/                    # PDF generation + email delivery
│   ├── models/                    # Pydantic models (LegalProfile, Conversation, etc.)
│   └── utils/                     # Auth, Anthropic client, logger, rate limiter, retry
├── web/                           # Next.js 16 frontend (App Router)
│   ├── app/                       # Pages: landing, onboarding, chat, profile, deadlines, etc.
│   └── components/                # ChatInterface, ProfileSidebar, ActionGenerator, etc.
├── mobile/                        # Expo React Native app (Expo Router)
├── shared/                        # Shared TypeScript types
├── tests/                         # Backend test suite (528 tests across 37 files)
├── web/__tests__/                 # Frontend test suite (143 tests across 21 files)
├── supabase/                      # Database schema + RLS policies
├── docs/decisions/                # 25 Architecture Decision Records
└── scripts/                       # Demo seed scripts
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check with version info |
| `GET` | `/api/llm/status` | LLM router status with per-provider circuit breaker metrics |
| `POST` | `/api/chat` | Send a legal question, receive a personalized response |
| `GET` | `/api/chat/{id}/stream` | SSE stream of chat response chunks |
| `POST` | `/api/profile` | Create or update legal profile |
| `GET` | `/api/profile/{user_id}` | Retrieve user's legal profile |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/{id}` | Get conversation by ID |
| `DELETE` | `/api/conversations/{id}` | Delete a conversation |
| `POST` | `/api/documents` | Upload and analyze a legal document |
| `POST` | `/api/actions/letter` | Generate a demand letter |
| `POST` | `/api/actions/rights` | Generate a rights summary |
| `POST` | `/api/actions/checklist` | Generate a next-steps checklist |
| `POST` | `/api/deadlines` | Create a deadline |
| `GET` | `/api/deadlines` | List all deadlines |
| `PATCH` | `/api/deadlines/{id}` | Update a deadline |
| `DELETE` | `/api/deadlines/{id}` | Delete a deadline |
| `GET` | `/api/rights/domains` | List legal rights domains |
| `GET` | `/api/rights/guides` | List rights guides |
| `GET` | `/api/rights/guides/{id}` | Get a specific rights guide |
| `GET` | `/api/workflows/templates` | List workflow templates |
| `POST` | `/api/workflows` | Start a guided workflow |
| `GET` | `/api/workflows/{id}` | Get workflow by ID |
| `PATCH` | `/api/workflows/{id}/steps` | Update a workflow step |
| `POST` | `/api/export/document` | Export document as PDF |
| `POST` | `/api/export/email` | Export document via email |
| `GET` | `/api/attorneys/search` | Search for attorneys by state and specialty |
| `POST` | `/api/payments/create-checkout-session` | Create a Stripe checkout session for subscription |
| `POST` | `/api/payments/webhook` | Handle Stripe webhook events |
| `GET` | `/api/payments/subscription` | Get current subscription status |
| `POST` | `/api/payments/cancel` | Cancel subscription (at period end) |
| `POST` | `/api/waitlist` | Join the waitlist (Mailchimp + Supabase) |

All endpoints except `/health`, `/api/waitlist`, and `/api/payments/webhook` require a valid Supabase JWT. Request and response bodies are fully typed with Pydantic models -- no `Any` types, no bare `dict` returns.

---

## Testing

### Backend (pytest)

```bash
make test                                         # Full suite with coverage
pytest tests/ -v --cov=backend --cov-report=term-missing  # Verbose with line-by-line coverage
pytest tests/test_memory_injector.py -v           # Run a specific file
```

**528 tests** across 37 files. Priority coverage on the memory injection layer (31 tests in `test_memory_injector.py` alone). Includes property-based tests via [Hypothesis](https://hypothesis.readthedocs.io/) for edge case discovery, 13 end-to-end integration tests covering full API pipelines, and a live deployment smoke test suite.

### Frontend (Jest)

```bash
cd web && npm test                                # Full suite
cd web && npm test -- --coverage                  # With coverage report
```

**143 tests** across 21 files covering all components, API client, auth, and Supabase integration. Includes accessibility tests via [jest-axe](https://github.com/nickcolley/jest-axe).

### Pre-commit verification

```bash
make verify    # Runs lint + full test suite. Required before every commit.
```

### End-to-End (Playwright)

```bash
cd web && npx playwright test              # Run all E2E tests
cd web && npx playwright test --ui         # Interactive UI mode
cd web && npx playwright show-report       # View HTML report
```

Playwright E2E tests cover critical user journeys (onboarding, chat, profile updates). Test artifacts (screenshots, traces) are uploaded as CI artifacts on failure.

### Integration Tests

```bash
pytest tests/test_integration.py -v              # 13 end-to-end pipeline tests
```

Covers full request/response cycles: chat pipeline (profile → classify → prompt → Claude → response), profile CRUD, action generators (letter/rights/checklist), conversation lifecycle, audit chain verification, and all 10 legal domain classifications.

### Live Deployment Smoke Tests

```bash
python scripts/smoke_test.py https://api.casematelaw.com   # Against production
python scripts/smoke_test.py http://localhost:8000           # Against local
```

Verifies health, metrics, OpenAPI docs, auth-gated endpoint protection, and 404 handling against a live deployment.

---

## Verification

Verify key README claims directly from the codebase:

| Claim | Verification Command |
|-------|---------------------|
| 50-state coverage | `python -c "from backend.legal.state_laws import STATE_LAWS; print(len(STATE_LAWS))"` → 51 (50 states + federal) |
| Backend test count | `pytest tests/ --co -q \| tail -1` → 528 tests collected |
| Zero lint errors | `make lint` → All checks passed |
| Zero type errors | `mypy backend/` → Success: no issues found |
| Memory injection | Run demo, ask landlord question as MA renter → response cites M.G.L. |
| Chat model | `grep "claude-sonnet" backend/utils/llm_router.py` → claude-sonnet-4-20250514 (Anthropic) |
| Classifier model | `grep "claude-sonnet" backend/legal/classifier.py` → claude-sonnet-4-20250514 (Anthropic) |

---

## Completeness Evidence

Features marked "Complete" above are implemented, tested, and deployable. Features marked "In Progress" or with config requirements are noted in the table.

| Dimension | Evidence | Verification |
|-----------|----------|-------------|
| **Backend Tests** | 528 pytest tests | `make test` |
| **Frontend Tests** | 143 Jest tests across 21 files | `cd web && npm test` |
| **Integration Tests** | 13 end-to-end pipeline tests | `pytest tests/test_integration.py -v` |
| **Smoke Tests** | 7 live deployment checks | `python scripts/smoke_test.py <url>` |
| **E2E Tests** | Playwright user journey tests | `cd web && npx playwright test` |
| **Type Safety** | mypy strict mode, zero errors | `mypy backend/` |
| **Lint** | ruff, zero warnings | `make lint` |
| **50-State Coverage** | 51 entries (50 states + federal) | `python -c "from backend.legal.state_laws import STATE_LAWS; print(len(STATE_LAWS))"` |
| **10 Legal Domains** | Each with classifier + state context | `pytest tests/test_integration.py::test_all_10_legal_domains_classify_correctly` |
| **Deployment Configs** | Dockerfile, Procfile, railway.json, render.yaml, vercel.json | `ls Dockerfile Procfile railway.json render.yaml vercel.json` |
| **CI/CD Pipeline** | GitHub Actions with lint, test, build, deploy | `.github/workflows/ci.yml` |
| **Health Endpoint** | Returns status, version, lifecycle, uptime | `curl /health` |
| **API Documentation** | Auto-generated OpenAPI/Swagger | `curl /docs` |

---

## Deployment

CaseMate ships with a complete CI/CD pipeline, multi-platform deployment infrastructure, and automated deployment verification.

### Live Deployment

| Service | URL | Verification |
|---------|-----|--------------|
| Backend API | `https://api.casematelaw.com` | `curl https://api.casematelaw.com/health` → `{"status": "ok", "version": "0.5.0"}` |
| Frontend | `https://casematelaw.com` | HTTP 200 with CaseMate branding |
| Health Check | `https://api.casematelaw.com/health` | Returns status, version, lifecycle state, and uptime |
| Metrics | `https://api.casematelaw.com/metrics` | Prometheus-compatible request metrics |

```bash
# Verify deployment end-to-end
make verify-deploy                       # Runs scripts/verify_deployment.sh against production
```

The deployment verification script checks: health endpoint status, API version, public endpoints (rights, workflows), frontend availability, and security headers (X-Content-Type-Options, X-Frame-Options).

| Component | Platform | Configuration | CI/CD |
|-----------|----------|---------------|-------|
| Frontend | Vercel | `web/vercel.json`, `web/Dockerfile` | Auto-deploy on push to `main` via Vercel CLI |
| Backend | Railway | `railway.toml`, `Dockerfile` | Auto-deploy on push to `main` via Railway CLI |
| Mobile (iOS) | App Store Connect | `mobile/eas.json` | EAS Build + Submit via `.github/workflows/mobile.yml` |
| Mobile (Android) | Google Play Console | `mobile/eas.json` | EAS Build + Submit via `.github/workflows/mobile.yml` |
| Database | Supabase | `supabase/migrations/` | Manual migration via `supabase db push` |
| Cache | Redis | `docker-compose.prod.yml` | Provisioned via Railway Redis plugin |
| Payments | Stripe | Webhook at `/api/payments/webhook` | — |

### CI/CD Pipeline (`.github/workflows/ci.yml`)

```
Push to main → Backend (lint + typecheck + test) ─────┐
             → Frontend (lint + test + build) ─────────┼→ Docker build → Deploy staging → Deploy production
             → E2E (Playwright against staging) ───────┤
             → Mobile (typecheck + EAS validate) ──────┘
```

### Deployment Commands

```bash
make deploy              # Deploy backend + frontend to production
make deploy-backend      # Deploy backend to Railway
make deploy-frontend     # Deploy frontend to Vercel
make deploy-mobile       # Build + submit mobile via EAS
make verify-deploy       # Verify live deployment (health, API, security headers)
make docker-up           # Start all services via Docker Compose
```

### Docker

```bash
# Development (backend + redis + web)
docker compose up --build

# Production (+ nginx reverse proxy with SSL, resource limits, log rotation)
docker compose -f docker-compose.prod.yml up -d
```

Environment variables for production: see `.env.production.example`. Full deployment guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Architecture Decision Records

All architectural decisions are documented with context, options considered, and rationale.

| ADR | Decision | Summary |
|-----|----------|---------|
| [001](docs/decisions/001-memory-as-differentiator.md) | Memory as core differentiator | Persistent memory over more features. Memory is what makes people pay. |
| [002](docs/decisions/002-state-specific-legal-context.md) | State-specific legal context | Jurisdiction-aware injection. MA law is not TX law. |
| [003](docs/decisions/003-profile-auto-update-strategy.md) | Profile auto-update strategy | Background task post-response. Never blocks the user. |
| [004](docs/decisions/004-document-pipeline-design.md) | Document pipeline design | Supabase Storage + extraction. Files tied to auth, facts to profile. |
| [005](docs/decisions/005-action-generator-scope.md) | Action generator scope | Letters + rights + checklists cover 80% of user needs. |
| [006](docs/decisions/006-deadline-auto-detection.md) | Deadline auto-detection | Extract time-sensitive deadlines from conversations automatically. |
| [007](docs/decisions/007-guided-workflow-engine.md) | Guided workflow engine | Step-by-step templates for common legal processes. |
| [008](docs/decisions/008-rate-limiting-strategy.md) | Rate limiting strategy | Redis-backed with fail-open. Never block users due to infra issues. |
| [009](docs/decisions/009-keyword-classifier-over-llm.md) | Keyword classifier over LLM | ~0ms classification vs ~2s LLM call. Speed and cost win. |
| [010](docs/decisions/010-supabase-over-vector-db.md) | Supabase over vector DB | Structured data, not embeddings. No RAG complexity needed. |
| [011](docs/decisions/011-regional-state-law-organization.md) | Regional state law organization | 5 regional files + federal. Maintainable at scale. |
| [012](docs/decisions/012-background-task-pattern.md) | Background task pattern | FastAPI background tasks for non-blocking profile updates. |
| [013](docs/decisions/013-pdf-export-with-fpdf2.md) | PDF export with fpdf2 | Lightweight PDF generation for letters and summaries. |
| [014](docs/decisions/014-attorney-scoring-algorithm.md) | Attorney scoring algorithm | Weighted specialization matching for relevant referrals. |
| [015](docs/decisions/015-rights-library-static-content.md) | Rights library as static content | Pre-built guides for instant access, no LLM call needed. |
| [016](docs/decisions/016-frontend-testing-strategy.md) | Frontend testing strategy | Jest + React Testing Library for component and integration tests. |
| [017](docs/decisions/017-mobile-architecture-expo.md) | Mobile architecture (Expo) | Expo Router with shared TypeScript types and API client. |
| [018](docs/decisions/018-deployment-architecture.md) | Deployment architecture | Vercel (frontend) + Railway (backend) + Supabase (DB). |
| [019](docs/decisions/019-comprehensive-documentation-standards.md) | Documentation standards | Docstrings, JSDoc, ADRs, and structured changelogs. |
| [020](docs/decisions/020-backend-test-coverage-threshold.md) | Backend test coverage threshold | 91% coverage, 90% CI-enforced threshold. |
| [021](docs/decisions/021-hybrid-classifier-keyword-first-llm-fallback.md) | Hybrid classifier (keyword + LLM) | Keyword-first with LLM fallback. 90%+ hit rate at <1ms, $0 cost. |
| [022](docs/decisions/022-sse-streaming-over-websocket-for-chat.md) | SSE streaming over WebSocket | Unidirectional SSE fits chat. Works through CDNs and proxies. |
| [023](docs/decisions/023-supabase-unified-platform.md) | Supabase as unified platform | Auth + DB + Storage + Realtime. One SDK, one security model. |
| [024](docs/decisions/024-prompt-injection-defense-structured-context.md) | Prompt injection defense | Structured context isolation. Zero-latency, deterministic, auditable. |
| [025](docs/decisions/025-multi-provider-llm-router.md) | LLM router | Anthropic Claude with circuit-breaker protection and observability metrics. |

---

## Documentation

Comprehensive documentation for every CaseMate subsystem lives in `docs/`:

### Architecture & Design

| Doc | Description |
|-----|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full technical architecture, data flow diagrams, system design |
| [MEMORY_SYSTEM.md](docs/MEMORY_SYSTEM.md) | Core memory injection pattern — prompt assembly, fact extraction, conversation persistence |
| [LEGAL_KNOWLEDGE_BASE.md](docs/LEGAL_KNOWLEDGE_BASE.md) | 50-state statute database, classifier algorithm, state law organization |
| [LEGAL_DOMAINS.md](docs/LEGAL_DOMAINS.md) | 10 legal domains — keywords, statutes, response patterns, coverage matrix |
| [FRONTEND.md](docs/FRONTEND.md) | Next.js 16 web app — pages, components, state management, API client |
| [MOBILE.md](docs/MOBILE.md) | Expo React Native — screens, navigation, shared types, EAS builds |
| [DATABASE.md](docs/DATABASE.md) | Supabase schema, JSONB structures, RLS policies, indexes, migrations |

### Features & Subsystems

| Doc | Description |
|-----|-------------|
| [ACTIONS.md](docs/ACTIONS.md) | Demand letter, rights summary, and checklist generators |
| [DEADLINES.md](docs/DEADLINES.md) | Auto-detection from conversations + manual deadline tracking |
| [REFERRALS.md](docs/REFERRALS.md) | Attorney matching with weighted relevance scoring |
| [EXPORT.md](docs/EXPORT.md) | Branded PDF generation and email delivery |
| [RIGHTS_LIBRARY.md](docs/RIGHTS_LIBRARY.md) | 19 pre-built Know Your Rights guides |
| [PAYMENTS.md](docs/PAYMENTS.md) | Stripe integration — checkout, webhooks, subscriptions |
| [WORKFLOWS.md](docs/WORKFLOWS.md) | Guided legal workflow engine and templates |
| [DOCUMENT_PIPELINE.md](docs/DOCUMENT_PIPELINE.md) | PDF/image upload, text extraction, fact injection |

### Development & Operations

| Doc | Description |
|-----|-------------|
| [UTILS.md](docs/UTILS.md) | Auth, rate limiting, retry logic, API client, structured logging |
| [TESTING.md](docs/TESTING.md) | Test strategy, fixtures, mocking patterns, coverage targets |
| [EXTENDING.md](docs/EXTENDING.md) | How to add new domains, states, actions, workflows, and endpoints |
| [API.md](docs/API.md) | Full API reference with request/response schemas |
| [MODELS.md](docs/MODELS.md) | All Pydantic and TypeScript model definitions |
| [SECURITY.md](docs/SECURITY.md) | Auth, secrets management, RLS, rate limiting |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | CI/CD pipeline, Docker, Vercel/Railway/EAS deployment |
| [CI_CD.md](docs/CI_CD.md) | GitHub Actions workflows and build pipeline |

### Decision Records

25 Architecture Decision Records in [docs/decisions/](docs/decisions/) — see the [ADR table](#architecture-decision-records) below.

---

## Business Model

| Tier | Price | Includes |
|------|-------|----------|
| **Free** | $0/mo | AI legal guidance, state-specific citations, document generation, conversation memory |
| **Pro** | $30/mo | Everything in Free + priority responses, advanced templates, attorney referrals, unlimited conversations |

**Unit economics:** $30/mo revenue per subscriber, ~$0.50/mo Claude API cost per active user = **98.3% variable margin per user** (excludes ~$70/mo fixed infrastructure costs — Supabase, Railway, Vercel). LTV of $360 (12-month average retention) with a CAC target under $30, yielding a 12:1 LTV:CAC ratio.

---

## Market Validation

All data below is from social media polls (non-random, self-selected samples) and platform analytics. Results are shown for directional insight, not statistical certainty. Full methodology, screenshots, and raw data in [USER_RESEARCH.md](USER_RESEARCH.md).

| Signal | Data Point |
|--------|-----------|
| **Pricing validation** | 312 LinkedIn respondents -- 100% willing to pay, 50% chose $10-$20/mo range |
| **Problem validation** | 8,400 TikTok respondents -- 78% have needed a lawyer but could not afford one |
| **Product validation** | 1,200 Instagram respondents -- 90% would use AI for legal guidance |
| **Qualitative feedback** | 400+ DMs and comments analyzed -- top pain point: landlord security deposits (28%) |
| **Organic traction** | 50,000+ views, 300+ waitlist signups, 1,250 followers -- all at $0 ad spend |
| **Market size** | $15.6B TAM, $3.1B SAM, $360M SOM at 1% penetration |

---

## Roadmap

- **App Store and Google Play launch** -- Submit all builds for review
- **Mobile parity** -- Feature parity between web and Expo React Native app
- **Subscription persistence** -- Complete subscriptions table migration for Stripe lifecycle tracking
- **Premium tier** -- Attorney consultation credits, court filing assistance
- **Real-time statute updates** -- Automated pipeline for legislative changes

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Key points:

- Run `make verify` before every commit (lint + full test suite must pass)
- Every function gets a docstring. Every type gets an annotation. No `Any`.
- Follow the commit format: `feat(scope): description`, `fix(scope): description`
- Memory injection tests are priority one -- never ship a change that breaks the injector.

---

## License

[MIT](LICENSE)

---

## Acknowledgments

- [Claude Code](https://claude.ai/code) by Anthropic -- Built entirely with Claude Code, from architecture planning through implementation, testing (671 tests), and deployment pipeline. Every commit in this repository is co-authored with Claude Opus 4.6.
- [Anthropic Claude](https://anthropic.com) -- AI reasoning engine powering all legal analysis
- [Supabase](https://supabase.com) -- Database, auth, and storage infrastructure
- [Next.js](https://nextjs.org) -- Frontend framework
- [FastAPI](https://fastapi.tiangolo.com) -- Backend framework
- [Expo](https://expo.dev) -- Cross-platform mobile framework

---

<div align="center">

Built by **Tyler Moore** and **Owen Ash** at the New England Inter-Collegiate AI Hackathon.

Providence, Rhode Island -- March 28-29, 2026.

*The average American faces 3-5 significant legal situations per year and handles most of them alone. CaseMate ends that.*

</div>
