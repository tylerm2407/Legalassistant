# CaseMate Glossary

Domain terminology used throughout the CaseMate codebase and documentation.

## Legal Domain

| Term | Definition | Used In |
|------|-----------|---------|
| **Legal area** | One of 10 classified domains (landlord_tenant, employment, consumer, debt_collections, small_claims, contracts, traffic, family_law, criminal_records, immigration) | `classifier.py`, `state_laws.py` |
| **Legal fact** | A specific, verifiable piece of information about a user's legal situation, extracted from conversations | `LegalProfile.legal_facts`, `updater.py` |
| **Legal profile** | The persistent user context containing state, housing, employment, family status, active issues, and legal facts | `LegalProfile` model, `injector.py` |
| **Active issue** | An ongoing legal dispute being tracked for a user (e.g., "landlord withholding security deposit") | `LegalIssue` model |
| **Memory injection** | The process of assembling a personalized system prompt from the user's legal profile, state laws, and response rules | `build_system_prompt()` in `injector.py` |
| **State law context** | Jurisdiction-specific statutes and legal information injected into Claude prompts based on the user's state | `state_laws.py`, `states/` directory |
| **Demand letter** | A formal letter demanding specific action (e.g., return of security deposit), generated with the user's profile context and relevant law citations | `letter_generator.py` |
| **Rights summary** | A personalized summary of the user's legal rights in a specific domain, with applicable statutes | `rights_generator.py` |
| **Action checklist** | A prioritized list of next steps with deadlines for resolving a legal issue | `checklist_generator.py` |
| **Statute citation** | A reference to a specific law (e.g., M.G.L. c.186 §15B) — CaseMate always cites real statutes, not vague references | System prompt rules |
| **Rights guide** | A pre-written educational resource about rights in a specific legal domain (19 guides across 10 domains) | `backend/knowledge/` |
| **Guided workflow** | A step-by-step process for common legal tasks (e.g., "respond to eviction notice") | `backend/workflows/` |

## Technical Domain

| Term | Definition | Used In |
|------|-----------|---------|
| **Hybrid classifier** | Two-stage classification: keyword matching first (free, <1ms), LLM fallback for ambiguous queries ($0.003, ~800ms) | `classifier.py`, ADR-021 |
| **Prompt caching** | Anthropic's `cache_control: ephemeral` feature that caches static system prompt blocks across requests, reducing latency and cost | `injector.py`, ADR-024 |
| **SSE streaming** | Server-Sent Events for real-time token delivery from Claude to the client via `GET /api/chat/{id}/stream` | `main.py`, ADR-022 |
| **Circuit breaker** | Resilience pattern that stops calling a failing service after N failures, auto-recovers after a cooldown period | `circuit_breaker.py` |
| **Fail-open** | Design pattern where a failing subsystem (e.g., Redis for rate limiting) doesn't block the main service — requests are allowed rather than rejected | `rate_limiter.py`, ADR-008 |
| **Row Level Security (RLS)** | Supabase/Postgres feature that enforces data access rules at the database level — users can only read/write their own data | `SECURITY.md` |
| **Subscription gate** | Middleware that checks a user's Stripe subscription tier before allowing access to premium features | `stripe_webhooks.py` |
| **Profile auto-updater** | Background task that runs after every chat response, extracting new legal facts and updating the user's profile | `updater.py`, ADR-003 |
| **Background task** | A FastAPI `BackgroundTask` that runs after the response is sent — used for profile updates so they never block the user | `main.py` |
| **Singleton client** | Single `AsyncAnthropic` instance shared across all requests — avoids per-request connection overhead | `client.py` |

## Data Models

| Model | File | Purpose |
|-------|------|---------|
| `LegalProfile` | `backend/models/legal_profile.py` | User's persistent legal context (state, housing, employment, facts, issues) |
| `LegalIssue` | `backend/models/legal_profile.py` | Active legal dispute with description, status, and extracted facts |
| `LegalFact` | `backend/models/legal_profile.py` | Single verifiable fact from a conversation (text + source conversation ID) |
| `Conversation` | `backend/models/conversation.py` | Chat session with messages, timestamps, and legal area |
| `Message` | `backend/models/conversation.py` | Single chat message (role, content, timestamp) |
| `DemandLetter` | `backend/models/action_output.py` | Generated demand letter with text, citations, recipient, subject |
| `RightsSummary` | `backend/models/action_output.py` | Generated rights summary with text, key_rights, applicable_laws |
| `Checklist` | `backend/models/action_output.py` | Generated next-steps checklist with items, deadlines, priority_order |
