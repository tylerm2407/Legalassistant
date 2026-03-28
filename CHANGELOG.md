# Changelog

All notable changes to Lex will be documented in this file.

## [0.2.0] — 2026-03-28

### Added
- Comprehensive test suite: 110+ tests across 10 test files
- API endpoint tests for all 25 routes
- JWT authentication tests (valid, expired, missing, malformed tokens)
- Rate limiter tests (fail-open, under/over limit, Retry-After header)
- Anthropic client singleton tests
- Document analyzer tests (valid, missing keys, parse errors)
- Rights library tests (domains, guides, structure validation)
- CI pipeline with pytest-cov coverage reporting
- Web build step in CI pipeline
- Know Your Rights library (18 guides across 10 legal domains)
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
