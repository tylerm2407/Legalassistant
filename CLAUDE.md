# CLAUDE.md — CaseMate

> Read this entire file before writing a single line of code.
> This is not a trading project, a data pipeline, or a generic chatbot.
> This is a personalized legal assistant where **memory is the product**.

---

## What CaseMate is

CaseMate is a web app that gives regular people access to legal guidance they can't afford. The average US lawyer charges $349/hour. The average American earns $52,000/year. That gap is the product.

The differentiator is persistent memory. CaseMate knows the user's state, housing situation, employment type, active legal disputes, and specific legal facts extracted from past conversations. Every answer is personalized to their actual situation — not a generic person's. A user in Massachusetts with a landlord dispute gets an answer that cites M.G.L. c.186 §15B and references the move-in inspection they mentioned two months ago. That is what makes people pay $20/month.

**The memory injection pattern is the core of this codebase. Protect it above everything else.**

---

## Project structure

```
casemate/
├── CLAUDE.md                     ← you are here
├── README.md                     ← product overview
├── ARCHITECTURE.md               ← full technical design
├── CHANGELOG.md                  ← updated after every meaningful commit
├── PROGRESS.md                   ← updated every 30 minutes during build
├── Makefile                      ← make dev | make test | make lint | make verify
├── .env.example                  ← all required env vars with comments
├── pyproject.toml                ← Python deps + ruff + mypy config
│
├── backend/
│   ├── main.py                   ← FastAPI app, all route definitions
│   ├── memory/
│   │   ├── injector.py           ← THE most important file. Builds system prompts.
│   │   ├── updater.py            ← Extracts facts from conversations post-response
│   │   ├── profile.py            ← LegalProfile Pydantic model
│   │   └── conversation_store.py ← Conversation CRUD (create, list, save, delete)
│   ├── legal/
│   │   ├── classifier.py         ← Classifies question into one of 10 legal areas
│   │   ├── state_laws.py         ← State-specific legal context (all 50 states)
│   │   ├── states/               ← Regional state law files (all 50 states)
│   │   │   ├── northeast.py      ← 9 states (MA, NY, CT, etc.)
│   │   │   ├── southeast.py      ← 14 states (FL, GA, VA, etc.)
│   │   │   ├── midwest.py        ← 12 states (IL, OH, MI, etc.)
│   │   │   ├── south_central.py  ← 2 states (TX, OK)
│   │   │   ├── west.py           ← 13 states (CA, WA, CO, etc.)
│   │   │   └── federal.py        ← Federal-level legal context
│   │   └── areas/                ← One module per legal domain
│   │       ├── landlord_tenant.py
│   │       ├── employment.py
│   │       ├── consumer.py
│   │       ├── debt_collections.py
│   │       ├── small_claims.py
│   │       ├── contracts.py
│   │       ├── traffic.py
│   │       ├── family_law.py
│   │       ├── criminal_records.py
│   │       └── immigration.py
│   ├── actions/
│   │   ├── letter_generator.py   ← Demand letter generation
│   │   ├── rights_generator.py   ← Rights summary generation
│   │   └── checklist_generator.py← Next-steps checklist generation
│   ├── documents/
│   │   ├── extractor.py          ← PDF/image text extraction
│   │   └── analyzer.py           ← Claude analysis → fact extraction
│   ├── knowledge/                ← Rights library (19 guides)
│   ├── workflows/                ← Guided legal workflows
│   ├── deadlines/                ← Deadline detection + tracking
│   ├── referrals/                ← Attorney matching
│   ├── export/                   ← PDF/email export
│   ├── models/
│   │   ├── legal_profile.py      ← LegalProfile, LegalIssue, LegalFact
│   │   ├── conversation.py       ← Conversation, Message models
│   │   └── action_output.py      ← DemandLetter, RightsSummary, Checklist
│   └── utils/
│       ├── auth.py               ← JWT authentication
│       ├── client.py             ← Singleton Anthropic client
│       ├── logger.py             ← Structured logging with user_id context
│       ├── rate_limiter.py       ← Redis-backed rate limiting
│       └── retry.py              ← Exponential backoff for Anthropic API calls
│
├── web/
│   ├── app/
│   │   ├── page.tsx              ← Marketing landing page
│   │   ├── api/waitlist/route.ts ← Waitlist signup API (Mailchimp + Supabase)
│   │   ├── onboarding/page.tsx   ← 5-question intake wizard
│   │   ├── chat/page.tsx         ← Main chat interface
│   │   ├── profile/page.tsx      ← Legal profile viewer/editor
│   │   ├── attorneys/page.tsx    ← Attorney search/referral page
│   │   ├── deadlines/page.tsx    ← Deadline tracking dashboard
│   │   ├── rights/page.tsx       ← Know Your Rights library browser
│   │   └── workflows/page.tsx    ← Guided legal workflow page
│   └── components/
│       ├── ChatInterface.tsx     ← Conversation UI + memory indicator
│       ├── LegalProfileSidebar.tsx← Live profile display (visible during chat)
│       ├── CaseHistory.tsx       ← Active issues timeline
│       ├── DocumentUpload.tsx    ← File upload + fact extraction preview
│       ├── ActionGenerator.tsx   ← Letter/rights/checklist generator
│       ├── OnboardingFlow.tsx    ← 5-step intake wizard component
│       ├── WaitlistForm.tsx      ← Email waitlist signup form
│       ├── DeadlineDashboard.tsx ← Deadline list + status management
│       ├── AttorneyCard.tsx      ← Attorney referral display card
│       ├── WorkflowWizard.tsx    ← Step-by-step workflow UI
│       ├── RightsGuide.tsx       ← Rights guide detail display
│       └── ConversationHistory.tsx← Conversation list + navigation
│
├── mobile/                       ← Expo React Native app
│
├── docs/
│   └── decisions/
│       ├── 001-memory-as-differentiator.md
│       ├── 002-state-specific-legal-context.md
│       ├── 003-profile-auto-update-strategy.md
│       ├── 004-document-pipeline-design.md
│       └── 005-action-generator-scope.md
│
└── tests/
    ├── conftest.py
    ├── test_memory_injector.py    ← Priority 1. Test memory above everything.
    ├── test_profile_updater.py
    ├── test_legal_classifier.py
    ├── test_action_generators.py
    ├── test_api_endpoints.py
    ├── test_auth.py
    ├── test_rate_limiter.py
    ├── test_anthropic_client.py
    ├── test_document_analyzer.py
    └── test_rights_library.py
```

---

## Commands

```bash
make dev          # Start backend (port 8000)
make test         # Run full test suite with coverage (pytest + pytest-cov)
make lint         # Run ruff check + ruff format --check
make format       # Auto-fix lint issues + format code
make verify       # Run lint + test (run before every commit)
make seed         # Seed demo profile (Sarah Chen)
make install      # Install all deps (pip install -e ".[dev]")
```

**Run `make verify` before every single commit. Never commit failing tests.**

---

## Environment variables

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...           # Required. All Claude calls go through this.

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...               # Frontend public key
SUPABASE_SERVICE_ROLE_KEY=eyJ...       # Backend only. Never expose to frontend.
SUPABASE_JWT_SECRET=...                # For JWT verification

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Optional
REDIS_URL=                             # For rate limiting (fail-open if empty)
```

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14 App Router + TypeScript + Tailwind | SSR, fast routing, type safety |
| Mobile | Expo + React Native | Cross-platform mobile |
| Backend | FastAPI + Python 3.12 | Background tasks for profile updates, SSE streaming |
| AI | Anthropic claude-sonnet-4-6 | Best instruction following for legal context injection |
| Database | Supabase (Postgres) | Structured profiles — not embeddings. Auth included. |
| File storage | Supabase Storage | Document uploads tied to user auth |
| Model validation | Pydantic v2 | All profile and response data is strictly typed |
| PDF | pdfplumber | Text extraction from legal documents |

---

## The memory injection pattern — build this first, build it right

This is the entire product. Get this working before touching UI.

```python
# backend/memory/injector.py

def build_system_prompt(profile: LegalProfile, question: str) -> str:
    """
    Assembles the full system prompt for a CaseMate response.

    This function is the core differentiator of CaseMate. It combines:
      1. CaseMate's base response philosophy
      2. The user's complete legal profile (state, situation, known facts)
      3. State-specific statutes for the identified legal domain
      4. Domain-specific response guidance

    The output makes Claude respond as a knowledgeable friend who has been
    advising this specific user for months — not a generic legal chatbot.

    Args:
        profile: The user's complete LegalProfile from Supabase.
        question: The user's current question (used to classify legal area).

    Returns:
        A complete system prompt string ready to pass to the Anthropic API.
    """
    legal_area = classify_legal_area(question)
    state_context = STATE_LAWS[profile.state][legal_area]

    return f"""
You are CaseMate — a personalized legal assistant. You are the knowledgeable friend
that everyone deserves but few can afford. You give real, specific, actionable
legal guidance. You are NOT a licensed attorney and you make that clear when
relevant, but you do NOT hide behind that disclaimer to avoid giving real help.

USER'S LEGAL PROFILE:
- State: {profile.state}
- Housing: {profile.housing_situation}
- Employment: {profile.employment_type}
- Family status: {profile.family_status}

ACTIVE ISSUES:
{profile.format_active_issues()}

KNOWN LEGAL FACTS ABOUT THIS USER:
{profile.format_legal_facts()}

STATE-SPECIFIC LEGAL CONTEXT ({profile.state} — {legal_area}):
{state_context}

RESPONSE RULES — follow these exactly:
1. Open by acknowledging what you already know about their situation.
   Never make them repeat context you already have.
2. Answer their specific question with their specific facts.
   Not a generic person's situation — theirs.
3. Cite the relevant statute for their state when it exists.
   Real citation (e.g. M.G.L. c.186 §15B), not vague references.
4. Tell them what they are ENTITLED TO, not just what the law says.
   Calculate damages if relevant. Name the specific remedy.
5. End with ONE concrete next step they can take TODAY.
   Not "you should consider..." — tell them what to do.
6. If a letter, rights summary, or checklist would help, offer to generate it.
7. Keep responses under 400 words unless the situation demands more.
   Dense, clear, actionable beats long and thorough.
"""
```

---

## Profile auto-updater — runs after every response

```python
# backend/memory/updater.py

async def update_profile_from_conversation(
    user_id: str,
    conversation: list[dict],
    supabase: Client,
) -> None:
    """
    Extracts new legal facts from the conversation and writes them to
    the user's profile in Supabase.

    This is what makes the memory compound. A user mentions their landlord
    didn't do a move-in inspection in conversation 3. This function extracts
    that as a legal fact. In conversation 7, CaseMate already knows it.

    Runs as a FastAPI background task — never blocks the response stream.

    Args:
        user_id: The authenticated user's ID.
        conversation: The full message history including the latest exchange.
        supabase: Supabase client with service role key for profile writes.
    """
    # Ask Claude to extract new facts from the conversation
    # Write them back to user_profiles.legal_facts[]
    # Create or update active_issues[] if a new dispute was described
    # Never remove existing facts — only add
```

---

## API route contracts

Every route must be fully typed. No `Any`. No bare `dict` returns.

```
POST   /api/chat              → ChatResponse
GET    /api/chat/{id}/stream  → SSE stream of ChatChunk events
GET    /api/profile           → LegalProfile
POST   /api/profile           → LegalProfile
PATCH  /api/profile           → LegalProfile
POST   /api/documents         → DocumentAnalysis
POST   /api/actions/letter    → DemandLetter
POST   /api/actions/rights    → RightsSummary
POST   /api/actions/checklist → ActionChecklist
GET    /api/cases             → list[LegalIssue]
PATCH  /api/cases/{id}        → LegalIssue
GET    /api/conversations     → list[Conversation]
DELETE /api/conversations/{id}→ {"status": "deleted"}
POST   /api/waitlist           → { success: true }
GET    /health                → {"status": "ok", "version": "..."}
```

---

## Code standards — non-negotiable

### Every class and every public method gets a docstring

```python
class LegalProfile(BaseModel):
    """
    The user's persistent legal context. Injected into every Claude API call.

    This is the single most important data model in CaseMate. Every field either
    comes from the onboarding intake or is automatically extracted from
    conversations by the ProfileAutoUpdater.

    Attributes:
        state: Two-letter state code. Determines which laws apply.
        housing_situation: Free-text description of housing (renter/owner/etc).
        employment_type: Employment classification affecting which rights apply.
        family_status: Relevant for family law questions and dependents.
        active_issues: Ongoing legal disputes being tracked.
        legal_facts: Specific facts extracted from conversations over time.
        documents: References to uploaded legal documents in Supabase Storage.
        member_since: Used to show users how long CaseMate has been helping them.
    """
```

### Type annotations on everything — no `Any`

```python
# CORRECT
async def get_profile(user_id: str, supabase: Client) -> LegalProfile:

# WRONG — never do this
async def get_profile(user_id, supabase) -> dict:
```

### Structured logging with user context

```python
import structlog
log = structlog.get_logger(__name__)

# CORRECT — always include user_id for debugging
log.info("profile_updated", user_id=user_id, facts_added=len(new_facts))

# WRONG — useless for debugging
print("profile updated")
```

### All Anthropic API calls use retry with backoff

```python
# backend/utils/retry.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
async def call_claude(prompt: str, system: str) -> str:
    """
    Calls the Anthropic API with automatic retry on failure.

    Retries up to 3 times with exponential backoff (2s, 4s, 8s).
    This handles transient API errors without crashing the user's session.

    Args:
        prompt: The user-turn message.
        system: The assembled system prompt from memory/injector.py.

    Returns:
        The text content of Claude's response.

    Raises:
        anthropic.APIError: After all retries are exhausted.
    """
```

### No bare except

```python
# CORRECT
try:
    profile = await get_profile(user_id, supabase)
except ProfileNotFoundError as e:
    log.error("profile_not_found", user_id=user_id, error=str(e))
    raise HTTPException(status_code=404, detail="Profile not found")

# WRONG — never do this
try:
    profile = await get_profile(user_id, supabase)
except:
    pass
```

---

## Build order — follow this exactly

### Hour 0–1: Foundation (before any feature work)
- [x] `make install` — verify deps install clean
- [x] Supabase schema created (user_profiles, conversations, documents tables)
- [x] `.env` populated with all keys
- [x] `GET /health` returns 200
- [x] First commit: `chore: initial scaffold with Supabase schema`

### Hour 1–3: Memory layer (the product)
- [x] `backend/memory/profile.py` — LegalProfile model, all fields, full docstrings
- [x] `backend/memory/injector.py` — build_system_prompt(), classify_legal_area()
- [x] `POST /api/chat` — reads profile, builds prompt, calls Claude, returns response
- [x] Verify: ask a question as a Massachusetts renter, confirm state law in response
- [x] Commit: `feat(memory): profile injection working end-to-end`

### Hour 3–5: Onboarding + profile storage
- [x] `POST /api/profile` — creates profile from intake answers
- [x] `web/app/onboarding/page.tsx` — 5-question wizard, stores to Supabase
- [x] Profile visible in sidebar after onboarding
- [x] Commit: `feat(onboarding): intake flow stores legal profile`

### Hour 5–8: Profile auto-updater + document upload
- [x] `backend/memory/updater.py` — runs as background task after every response
- [x] `POST /api/documents` — PDF/image upload, text extraction, fact injection
- [x] Verify: mention a new fact in chat, confirm it appears in profile after response
- [x] Commit: `feat(memory): profile auto-updater and document pipeline`

### Hour 8–12: Action generator
- [x] `backend/actions/letter_generator.py` — demand letter from profile context
- [x] `POST /api/actions/letter` — full letter, pre-filled, ready to send
- [x] `web/components/ActionGenerator.tsx` — UI for generating actions
- [x] **This is the demo feature. Make it look good.**
- [x] Commit: `feat(actions): demand letter generation with profile context`

### Hour 12–18: UI polish
- [x] `LegalProfileSidebar.tsx` — visible during chat, updates live
- [x] `CaseHistory.tsx` — active issues timeline
- [x] Chat bubbles look clean, CaseMate responses formatted with citations
- [x] Mobile responsive (judges will test on phones)
- [x] Commit: `feat(ui): profile sidebar, case history, chat polish`

### Hour 18–24: Hardening + demo prep
- [x] Run full test suite — fix anything red
- [x] Run `make verify` — zero failures
- [x] Build Sarah Chen demo profile with 12 prior conversations
- [x] Pre-generate the landlord deposit demo response
- [x] Commit: `chore: demo profile, final QA pass`

---

## The demo — build Sarah Chen Friday night

The demo profile judges will see:

```
Name: Sarah Chen
State: Massachusetts
Housing: Renter | month-to-month | no signed lease
Employment: Full-time W2 | marketing coordinator
Active issues: Landlord claiming $800 for bathroom tile damage
Legal facts:
  - Landlord did not perform move-in inspection
  - Pre-existing water damage documented in move-in photos
  - Gave written 30-day notice on February 28, 2026
Conversations: 12  ← makes it look like a real product in use
Member since: January 15, 2026
```

Demo script (2 minutes 45 seconds):
1. Open CaseMate — Sarah's profile is visible in the sidebar
2. Type: "My landlord is saying I owe $800 for the bathroom tiles"
3. CaseMate responds citing M.G.L. c.186 §15B, referencing the missing inspection,
   calculating Sarah may be owed her deposit PLUS up to 3x damages
4. Click "Generate demand letter"
5. Letter appears — pre-filled, cited, ready to send
6. Say: "A lawyer would have charged $700 for that consultation.
   CaseMate costs $20 a month. That is the gap we are closing."

---

## What NOT to do

- **Do not use the trading-bot skill.** This is not a trading system. If the global
  CLAUDE.md references algorithmic trading patterns, ignore them for this project.

- **Do not build a generic chatbot first and add memory later.** Memory is the
  foundation. Build the injector before building the chat UI.

- **Do not use `Any` types.** Every model is typed. Strict type annotations
  are enforced by mypy and are essential for code quality.

- **Do not hardcode API keys.** All secrets go in `.env`. The `.env.example`
  must have every variable with a comment explaining what it is.

- **Do not skip docstrings under time pressure.** Docstring density is a core
  code quality metric. A function without a docstring is incomplete code.

- **Do not leave placeholder implementations.** Any function with `pass` or
  `# TODO` is an incomplete product. Mark unfinished work with a clear comment
  explaining what it does and raise `NotImplementedError` with a message.

- **Do not make the memory invisible in the UI.** The profile sidebar must be
  visible during the chat. If judges can't see the memory, they don't believe it.

---

## Architecture decisions (see docs/decisions/ for full writeups)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 001 | Core differentiator | Persistent memory | Generic chatbots are commodities. Memory is defensible. |
| 002 | Legal context strategy | State-specific injection | One-size-fits-all legal answers are useless. MA law ≠ TX law. |
| 003 | Profile update mechanism | Background task post-response | Never blocks the user. Memory compounds silently. |
| 004 | Document storage | Supabase Storage + extraction | Files tied to auth, facts extracted to structured profile. |
| 005 | Action generator scope | Letter + rights + checklist | Three outputs cover 80% of what users actually need to do next. |

---

## Progress tracking

Update `PROGRESS.md` every 30 minutes during the build. A stale PROGRESS.md
signals a stalled team. Frequent updates show consistent velocity.

Format:
```markdown
## [HH:MM] — What just got built
- Specific thing completed
- Specific thing completed
- Next: what is being built right now
```

---

## Commit message format

```
feat(memory): profile injection working end-to-end
feat(onboarding): 5-question intake stores to Supabase
feat(actions): demand letter generation with profile context
feat(documents): PDF upload and fact extraction pipeline
feat(ui): profile sidebar visible during chat
fix(memory): profile updater now handles missing state field
test(memory): add tests for inject with empty legal_facts
docs(decisions): add ADR 003 for profile update strategy
chore: update PROGRESS.md
```

Type prefixes: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`, `style`
Scope (in parens): `memory`, `onboarding`, `chat`, `actions`, `documents`, `ui`, `api`

**Commit every 45–60 minutes minimum. Commit velocity is a scored dimension.**

## Legal Domain — NOT Trading

This is a legal assistant. Ignore trading/fintech patterns. The only domain knowledge is legal.
