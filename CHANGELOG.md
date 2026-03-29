# Changelog

All notable changes to CaseMate are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Standalone waitlist app with Supabase auth account creation
- MASTER_PROMPT.md optimized for Yconic rubric alignment
- LICENSE (MIT), SECURITY.md, and ADRs 016–020 committed
- Documentation verification section with reproducible commands
- API usage examples (curl + Python) in docs/API.md
- Troubleshooting FAQ in CONTRIBUTING.md

### Changed
- README badges updated to match actual test counts (246 backend, 139 frontend)
- Model version references corrected to `claude-sonnet-4-20250514` throughout
- Backend version bumped from 0.1.0 to 0.3.0 to match CHANGELOG
- Market validation section now includes methodology disclaimer
- Gross margin clarified as variable margin (excludes fixed infrastructure costs)
- API reference table now includes 4 payment endpoints
- ADR table expanded from 15 to 20 entries

### Fixed
- All code quality warnings eliminated (Any types, utcnow deprecation, missing docstrings, TODO cleanup)
- Main app redirects to /auth correctly
- Frontend test count corrected from 141 to 139

---

## [0.3.0] - 2026-03-29

### Added
- Backend test coverage increased from 40% to 89% (246 tests)
  - Legal area module tests (40 parametrized tests for all 10 domains)
  - Profile CRUD tests (8 tests for get/update operations)
  - Document extractor tests (9 tests for PDF/text/HTML)
- Frontend test suite with Jest + React Testing Library (139 tests across 19 suites)
  - Component tests for all 12 feature components
  - UI component tests (Button, Badge, Card, Input)
  - Library tests (API client, auth context, Supabase client)
- JSDoc documentation on all 34 frontend files (100+ doc blocks)
- Mobile app upgraded from scaffolding to functional screens
  - Login with auto-redirect and inline validation
  - Chat with typed conversation history and typing indicators
  - Profile with legal facts display and pull-to-refresh
  - Rights browser with search, domain icons, and expandable guides
- Architecture Decision Records 016-020
- Enterprise documentation suite (SECURITY.md, CODE_OF_CONDUCT.md, LICENSE, GitHub templates)
- Comprehensive API reference documentation

### Changed
- CONTRIBUTING.md upgraded with detailed setup, testing, and ADR process
- README.md rewritten with architecture diagrams and comprehensive project overview
- ARCHITECTURE.md expanded with Mermaid diagrams and security model

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
