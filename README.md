# CaseMate

> The legal friend everyone deserves.

![CI](https://github.com/tylerm2407/Legalassistant/actions/workflows/ci.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Expo](https://img.shields.io/badge/Expo-React_Native-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CaseMate is a personalized AI legal assistant that **remembers your full legal situation across every conversation** — your state, your housing, your employment, your ongoing disputes. It answers every legal question in the context of your actual life, not a generic stranger's.

Most legal AI tools answer one question and forget you exist. CaseMate builds a **legal profile** that compounds over time — so the fifth conversation is smarter than the first, and you never have to re-explain your situation.

---

## The problem

The average hourly rate for a lawyer in the United States is $349. A person with a median income of $52,000/year cannot afford to call a lawyer every time a landlord, employer, or debt collector does something illegal. They Google it, get generic answers, and give up.

The legal system is designed for people who can afford $349/hour. CaseMate changes that.

---

## Demo

1. Complete a 90-second legal intake (state, housing, employment, active issues)
2. Ask any legal question — CaseMate already knows your situation
3. Get a specific, jurisdiction-aware answer with your exact rights
4. Generate a ready-to-send letter, rights summary, or next-steps checklist

**Example:** A user in Massachusetts with a landlord dispute types *"my landlord is claiming I owe $800 for bathroom tiles."* CaseMate already knows: Massachusetts law, no move-in inspection was done, there's pre-existing water damage on file. It responds citing M.G.L. c.186 §15B, calculates the user is owed their deposit PLUS potential 3x damages, and offers to generate the demand letter — pre-filled, ready to send.

That response would cost $700 at a law firm. CaseMate costs $20/month.

---

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

---

## What CaseMate remembers

```json
{
  "state": "Massachusetts",
  "housing": "renter | month-to-month | no signed lease",
  "employment": "full-time W2 | tech industry",
  "active_issues": [
    {
      "type": "landlord-tenant",
      "summary": "Landlord claiming $800 deposit for pre-existing damage",
      "status": "open",
      "started": "2026-03-10"
    }
  ],
  "legal_facts": [
    "Landlord did not perform move-in inspection",
    "Unit had pre-existing water damage documented",
    "Gave 30 days written notice"
  ],
  "documents": ["lease_2024.pdf", "move_out_notice.png"],
  "conversations": 12
}
```

Every answer CaseMate gives is personalized to this profile. Not a generic person. You.

---

## Features

- **Persistent Memory** — Legal profile grows with every conversation
- **State-Specific Guidance** — Real statute citations for all 50 US states, organized by region
- **10 Legal Domains** — Landlord/tenant, employment, consumer, debt, small claims, contracts, traffic, family law, criminal records, immigration
- **Action Generators** — Demand letters, rights summaries, next-steps checklists — all pre-filled from your profile
- **Document Analysis** — Upload leases, notices, contracts — CaseMate extracts key facts and red flags
- **Know Your Rights Library** — 19 pre-built guides with rights, action steps, deadlines, and statute citations
- **Guided Workflows** — Step-by-step legal processes (eviction defense, wage claim filing, etc.)
- **Attorney Referrals** — State and domain-specific attorney matching
- **Deadline Tracking** — Auto-detected and manual legal deadlines
- **Document Export** — Generate downloadable letters, summaries, and checklists
- **Cross-Platform** — Web (Next.js) + iOS/Android (Expo React Native)

---

## Legal areas covered

| Area | Key capabilities |
|------|-----------------|
| Landlord-tenant | Deposits, illegal entry, habitability, eviction defense |
| Employment rights | Wage theft, wrongful termination, non-compete enforceability |
| Consumer protection | Debt collection violations, billing disputes, warranty claims |
| Debt & collections | FDCPA violations, statute of limitations, negotiation |
| Small claims | Filing guidance, evidence preparation, judgment enforcement |
| Contract disputes | Reading agreements, breach analysis, demand letters |
| Traffic violations | Defense options, DMV hearings, insurance impact |
| Family law basics | Custody basics, support calculations, separation agreements |
| Criminal records | Expungement eligibility, background check rights |
| Immigration basics | Status questions, document requirements, rights during enforcement |

State-specific law is applied to every answer. CaseMate knows you're in Massachusetts before you say a word.

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full technical design.

The core insight: every API call to Claude injects the user's legal profile as structured context. The memory layer is not a feature — it is the product.

```
User question
    +
Legal profile (from Supabase)
    +
State-specific legal system prompt
    =
A personalized answer no generic chatbot can give
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Mobile | Expo, React Native, Expo Router |
| Backend | FastAPI, Python 3.12 |
| AI | Anthropic Claude (claude-sonnet-4-6) |
| Database | Supabase (profiles + conversations + documents) |
| Auth | Supabase Auth (JWT) |
| File storage | Supabase Storage (document uploads) |
| Logging | structlog |
| PDF | pdfplumber |
| Deployment | Vercel (frontend) + Railway (backend) |

---

## Quick start

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
make test             # Run all tests with coverage
make verify           # Lint + test
```

---

## Early Access / Waitlist

CaseMate is currently in pre-launch. Join the waitlist on the landing page to get notified when we launch. Signups are synced to Mailchimp and backed up in Supabase.

---

## Environment variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # for backend profile writes
SUPABASE_JWT_SECRET=...            # for JWT verification

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Mailchimp (waitlist signup)
MAILCHIMP_API_KEY=                 # Mailchimp API key (Account → Extras → API keys)
MAILCHIMP_SERVER_PREFIX=           # Datacenter prefix, e.g. "us21" (from API key suffix)
MAILCHIMP_LIST_ID=                 # Audience/list ID (Audience → Settings → Audience ID)

# Email export (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_FROM=hello@casematelaw.com

# Optional
REDIS_URL=                         # for rate limiting (fail-open if empty)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
```

---

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
| `POST` | `/api/waitlist` | Join the waitlist (Mailchimp + Supabase) |

---

## Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app with all routes
│   ├── models/                  # Pydantic models (LegalProfile, etc.)
│   ├── memory/                  # Profile, injector, conversation store
│   ├── legal/                   # Classifier + state law library
│   ├── actions/                 # Demand letter, rights, checklist generators
│   ├── documents/               # PDF extraction + Claude analysis
│   ├── knowledge/               # Rights library (19 guides)
│   ├── workflows/               # Guided legal workflows
│   ├── deadlines/               # Deadline detection + tracking
│   ├── referrals/               # Attorney matching
│   ├── export/                  # PDF/email export
│   └── utils/                   # Auth, client, logger, rate limiter, retry
├── web/                         # Next.js 14 frontend
├── mobile/                      # Expo React Native app
├── shared/                      # Shared TypeScript types
├── tests/                       # Pytest test suite (168 tests)
├── supabase/                    # Database schema + RLS policies
├── docs/                        # Architecture decisions
└── scripts/                     # Demo seed scripts
```

---

## Security

- **JWT Authentication** — All API endpoints require valid Supabase JWT
- **CORS** — Configurable allowed origins
- **Rate Limiting** — Redis-backed per-user rate limits (fail-open if Redis unavailable)
- **Input Validation** — Pydantic models with field constraints (max lengths, required fields)
- **File Size Limits** — 25MB max upload
- **Row Level Security** — Supabase RLS policies ensure users only access their own data
- **Prompt Injection Mitigation** — Profile context is structured data, not raw user input in system prompt

---

## Testing

```bash
# Run all tests with verbose output and coverage
pytest tests/ -v --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Lint
ruff check backend/ tests/
```

---

## Business model

| Tier | Price | Limits |
|------|-------|--------|
| Free | $0/month | 3 questions/month, basic profile |
| Personal | $20/month | Unlimited questions, document upload, letter generation |
| Family | $35/month | Up to 5 profiles, shared document vault |

At 1% penetration of Americans who cannot afford a lawyer: **$360M ARR**.

## Early traction

- **15,000+ TikTok views** in the first week of content (@casematelaw)
- **1,000+ engagements** across platforms pre-launch
- Active Instagram with content live and posting 4x/week
- 25 ready-to-post pieces across Instagram, X, LinkedIn, and TikTok

---

## Built at

**New England Inter-Collegiate AI Hackathon**
225 Dyer Street · Providence, Rhode Island · March 28–29, 2026

## Team

Built by Tyler Moore and Owen Ash.

> *The average American faces 3–5 significant legal situations per year and handles most of them alone. CaseMate ends that.*
