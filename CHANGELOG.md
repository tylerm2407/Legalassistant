# Changelog

All notable changes to CaseMate are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- README.md — product overview, demo, architecture summary, quick start
- ARCHITECTURE.md — full system design, memory architecture, API contracts, folder structure
- CLAUDE.md — Claude Code configuration, build order, code standards
- docs/decisions/001 — Memory as the core differentiator
- docs/decisions/002 — State-specific legal context injection
- docs/decisions/003 — Profile auto-update strategy
- docs/decisions/004 — Document pipeline design
- docs/decisions/005 — Action generator scope
- Project scaffold — full folder structure, Makefile, pyproject.toml, .env.example, CI workflow

---

## [0.2.0] — 2026-03-28

### Added
- Comprehensive test suite: 168 tests across 18 test files
- API endpoint tests for all 25 routes
- JWT authentication tests (valid, expired, missing, malformed tokens)
- Rate limiter tests (fail-open, under/over limit, Retry-After header)
- Anthropic client singleton tests
- Document analyzer tests (valid, missing keys, parse errors)
- Rights library tests (domains, guides, structure validation)
- CI pipeline with pytest-cov coverage reporting
- Web build step in CI pipeline
- Know Your Rights library (19 guides across 10 legal domains)
- Guided workflow system with templates and step tracking
- Attorney referral matching by state and legal area
- Deadline detection and tracking (auto-detected + manual)
- Conversation CRUD (list, get, delete)
- Document export (PDF download + email)
- README with badges, architecture diagram, full API docs

### Security
- JWT authentication on all API endpoints via Supabase
- CORS middleware with configurable allowed origins
- Redis-backed per-user rate limiting (fail-open if unavailable)
- Input validation: message length (10K), state code (2 chars), file size (25MB)
- Row Level Security policies in Supabase
- Prompt injection mitigation via structured profile context
- Singleton Anthropic client with 30s timeout

### Infrastructure
- Singleton AsyncAnthropic client (avoids per-request overhead)
- Retry logic with exponential backoff for all Claude API calls
- Structured logging with user_id context via structlog
- Redis integration for rate limiting

## [0.1.0] — 2026-03-27

### Added

**Core features:**
- Legal profile onboarding (5-question intake)
- Persistent memory injection into every Claude API call
- State-specific legal context for 10 US states at launch
- Legal area classification (10 domains)
- Profile auto-updater (background task post-response)
- Document upload pipeline (PDF + image OCR)
- Action generator: demand letter, rights summary, next-steps checklist
- Case history timeline
- Legal profile sidebar (visible during chat)

**Infrastructure:**
- Initial project scaffold with full monorepo structure
- Backend models: LegalProfile, LegalIssue, Conversation, Message, ActionOutput
- Memory injection system: build_system_prompt() with profile + state laws
- Legal classifier: keyword-based classification across 10 legal domains
- State law library: MA, CA, NY, TX, FL with real statute citations
- FastAPI backend with chat, profile, actions, and document routes
- Web frontend: Next.js with chat interface, profile sidebar, onboarding
- Mobile frontend: Expo React Native with chat, profile, cases screens
- Action generators: demand letters, rights summaries, checklists
- Document pipeline: PDF extraction + Claude analysis
- Test suite for memory layer, classifier, and action generators
- CI/CD pipeline with lint + test on push
- 5 Architecture Decision Records

**Stack:** Next.js 14 · FastAPI · Anthropic claude-sonnet-4-6 · Supabase · Tailwind CSS
