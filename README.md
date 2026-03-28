# Lex — Your Personal AI Legal Assistant

![CI](https://github.com/tylerm2407/Legalassistant/actions/workflows/ci.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Expo](https://img.shields.io/badge/Expo-React_Native-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Lex remembers your legal situation.** Every answer is specific to your state, your housing, your employment, and every legal fact you've shared. Not a generic chatbot — a knowledgeable friend who has been advising you for months.

## The Problem

Legal advice is expensive ($200–500/hour). Free resources give generic answers that don't account for your specific situation, state laws, or history. Most people facing legal issues — landlord disputes, employment violations, debt collection — can't afford real help and don't know their rights.

## The Solution

Lex builds a persistent legal profile from every conversation. When you ask about your security deposit, Lex already knows you're in Massachusetts, you've been renting for 2 years, your landlord didn't do a move-in inspection, and your deposit hasn't earned interest. The answer cites M.G.L. c.186 §15B and calculates your specific damages.

## How It Works

```
User Question
    │
    ▼
classify_legal_area(question)  ─── keyword-based, 10 domains
    │
    ▼
get_profile(user_id)  ─── persistent LegalProfile from Supabase
    │
    ▼
build_system_prompt(profile, question)  ─── injects state laws + facts
    │
    ▼
Claude API  ─── personalized response with statute citations
    │
    ▼
Background: extract new facts → update profile  ─── memory grows
```

## Features

- **Persistent Memory** — Legal profile grows with every conversation
- **State-Specific Guidance** — Real statute citations for MA, CA, NY, TX, FL
- **10 Legal Domains** — Landlord/tenant, employment, consumer, debt, small claims, contracts, traffic, family law, criminal records, immigration
- **Action Generators** — Demand letters, rights summaries, next-steps checklists — all pre-filled from your profile
- **Document Analysis** — Upload leases, notices, contracts — Lex extracts key facts and red flags
- **Know Your Rights Library** — 18 pre-built guides with rights, action steps, deadlines, and statute citations
- **Guided Workflows** — Step-by-step legal processes (eviction defense, wage claim filing, etc.)
- **Attorney Referrals** — State and domain-specific attorney matching
- **Deadline Tracking** — Auto-detected and manual legal deadlines
- **Document Export** — Generate downloadable letters, summaries, and checklists
- **Cross-Platform** — Web (Next.js) + iOS/Android (Expo React Native)

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase account (for auth + database)
- Anthropic API key

### Backend

```bash
cp .env.example .env  # Add your API keys
pip install -e ".[dev]"
make dev              # Starts uvicorn on :8000
```

### Web Frontend

```bash
cd web
npm install
npm run dev           # Starts Next.js on :3000
```

### Mobile

```bash
cd mobile
npm install
npx expo start        # Starts Expo dev server
```

### Run Tests

```bash
make test             # Run all tests
make verify           # Lint + test
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Send legal question, get personalized answer |
| `POST` | `/api/profile` | Create/update legal profile |
| `GET` | `/api/profile/{user_id}` | Get user's legal profile |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/{id}` | Get conversation by ID |
| `DELETE` | `/api/conversations/{id}` | Delete conversation |
| `POST` | `/api/actions/letter` | Generate demand letter |
| `POST` | `/api/actions/rights` | Generate rights summary |
| `POST` | `/api/actions/checklist` | Generate next-steps checklist |
| `POST` | `/api/documents` | Upload and analyze legal document |
| `POST` | `/api/deadlines` | Create deadline |
| `GET` | `/api/deadlines` | List deadlines |
| `PATCH` | `/api/deadlines/{id}` | Update deadline |
| `DELETE` | `/api/deadlines/{id}` | Delete deadline |
| `GET` | `/api/rights/domains` | List legal rights domains |
| `GET` | `/api/rights/guides` | List rights guides |
| `GET` | `/api/rights/guides/{id}` | Get specific rights guide |
| `GET` | `/api/workflows/templates` | List workflow templates |
| `POST` | `/api/workflows` | Start a workflow |
| `GET` | `/api/workflows` | List active workflows |
| `GET` | `/api/workflows/{id}` | Get workflow by ID |
| `PATCH` | `/api/workflows/{id}/steps` | Update workflow step |
| `POST` | `/api/export/document` | Export document as file |
| `POST` | `/api/export/email` | Export document via email |
| `GET` | `/api/attorneys/search` | Search for attorneys |

## Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app with all routes
│   ├── models/                  # Pydantic models (LegalProfile, etc.)
│   ├── memory/                  # Profile, injector, conversation store
│   ├── legal/                   # Classifier + state law library
│   ├── actions/                 # Demand letter, rights, checklist generators
│   ├── documents/               # PDF extraction + Claude analysis
│   ├── knowledge/               # Rights library (18 guides)
│   ├── workflows/               # Guided legal workflows
│   ├── deadlines/               # Deadline detection + tracking
│   ├── referrals/               # Attorney matching
│   ├── export/                  # PDF/email export
│   └── utils/                   # Auth, client, logger, rate limiter, retry
├── web/                         # Next.js 14 frontend
├── mobile/                      # Expo React Native app
├── shared/                      # Shared TypeScript types
├── tests/                       # Pytest test suite (110+ tests)
├── supabase/                    # Database schema + RLS policies
├── docs/                        # Architecture decisions
└── scripts/                     # Demo seed scripts
```

## Security

- **JWT Authentication** — All API endpoints require valid Supabase JWT
- **CORS** — Configurable allowed origins
- **Rate Limiting** — Redis-backed per-user rate limits (fail-open if Redis unavailable)
- **Input Validation** — Pydantic models with field constraints (max lengths, required fields)
- **File Size Limits** — 25MB max upload
- **Row Level Security** — Supabase RLS policies ensure users only access their own data
- **Prompt Injection Mitigation** — Profile context is structured data, not raw user input in system prompt

## Testing

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Lint
ruff check backend/ tests/
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system design.

## Demo

Ask Sarah Chen's profile: *"Can my landlord keep my security deposit for bathroom tile damage?"*

Lex responds with MA-specific deposit law (M.G.L. c.186 §15B), references her move-in photos showing pre-existing water damage, calculates triple damages ($6,600), and offers to generate a demand letter.

## Team

Built by Tyler Moore and Owen Ash for the New England Inter-Collegiate AI Hackathon, March 2026.
