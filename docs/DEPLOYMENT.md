# CaseMate — Deployment Guide

> Everything a developer needs to deploy CaseMate from scratch.
> If you follow this document top to bottom, you will have a working production deployment.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Environments](#environments)
3. [Environment Variables — Complete Reference](#environment-variables--complete-reference)
4. [Local Development Setup](#local-development-setup)
5. [Supabase Setup](#supabase-setup)
6. [Docker Development](#docker-development)
7. [Docker Production](#docker-production)
8. [Nginx Configuration](#nginx-configuration)
9. [Backend Deployment (Railway)](#backend-deployment-railway)
10. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
11. [Mobile Deployment (EAS)](#mobile-deployment-eas)
12. [CI/CD Pipeline](#cicd-pipeline)
13. [Database Migrations](#database-migrations)
14. [Health Checks and Verification](#health-checks-and-verification)
15. [Monitoring and Logging](#monitoring-and-logging)
16. [Rollback Procedures](#rollback-procedures)
17. [Security Checklist](#security-checklist)
18. [Pre-Deploy Checklist](#pre-deploy-checklist)
19. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                         ┌──────────────────┐
                         │     Vercel       │
                         │    (Next.js)     │
                         │  casematelaw.com │
                         └────────┬─────────┘
                                  │ HTTPS
                                  ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Supabase      │◄────│    Railway       │────►│     Redis        │
│   (PostgreSQL    │     │    (FastAPI)     │     │  (Rate Limiting) │
│    + Auth        │     │ api.casemate-    │     │  Railway Plugin  │
│    + Storage)    │     │   law.com        │     └──────────────────┘
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Anthropic     │
                         │   Claude API    │
                         │ (claude-sonnet) │
                         └──────────────────┘
```

**Component responsibilities:**

| Component | Platform | Role |
|-----------|----------|------|
| Frontend | Vercel | Next.js 14 App Router, SSR, marketing pages, chat UI |
| Backend | Railway | FastAPI, memory injection, Claude API calls, profile updates |
| Database | Supabase | PostgreSQL (profiles, conversations), Auth (JWT), Storage (documents) |
| Cache | Redis (Railway plugin) | Rate limiting per user/IP, fail-open if unavailable |
| AI | Anthropic | Claude claude-sonnet-4-6 for legal responses and fact extraction |
| Mobile | EAS Build | Expo React Native, submitted to App Store Connect + Google Play |

---

## Environments

| Environment | Backend URL | Frontend URL | Database | When to use |
|-------------|-------------|--------------|----------|-------------|
| **Development** | `http://localhost:8000` | `http://localhost:3000` | Supabase dev project | Local feature work |
| **Staging** | Railway staging service | Vercel preview deployment | Supabase staging project | QA, PR reviews |
| **Production** | `https://api.casematelaw.com` | `https://casematelaw.com` | Supabase production project | Live users |

Configuration templates:
- `.env.example` — Local development defaults
- `.env.production.example` — Production deployment reference

---

## Environment Variables — Complete Reference

### Required (Backend)

These must be set or the backend will not start.

```bash
# Anthropic — all Claude API calls route through this key
ANTHROPIC_API_KEY=sk-ant-...

# Supabase — database, auth, and file storage
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...                       # Anon key (used by frontend, safe to expose)
SUPABASE_SERVICE_ROLE_KEY=eyJ...          # Service role key (backend ONLY — never expose to frontend or client code)
SUPABASE_JWT_SECRET=...                   # HS256 secret for JWT verification
```

> **CRITICAL:** `SUPABASE_SERVICE_ROLE_KEY` bypasses Row Level Security. It must only
> exist on the backend server. Never put it in frontend code, mobile builds, or
> client-accessible environments. Leaking this key gives full database access.

### Required (Frontend)

Set these in the Vercel dashboard or in `.env.local` during development. All `NEXT_PUBLIC_` prefixed variables are embedded in the client bundle at build time.

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000           # Dev: localhost, Prod: https://api.casematelaw.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co    # Same as SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...                # Same as SUPABASE_KEY (anon key is safe for frontend)
```

### Optional — Payments

```bash
STRIPE_SECRET_KEY=sk_...                  # Stripe API key for subscription management
STRIPE_WEBHOOK_SECRET=whsec_...           # Signature verification on Stripe webhook events
```

Stripe is used for subscription billing ($20/month plan). The webhook secret is required
to verify that incoming webhook requests actually originate from Stripe. Without it,
an attacker could forge subscription events.

### Optional — Email and Waitlist

```bash
MAILCHIMP_API_KEY=...                     # Waitlist email collection and sync
MAILCHIMP_SERVER_PREFIX=us1               # Data center prefix (check your Mailchimp API key suffix)
MAILCHIMP_LIST_ID=...                     # Audience/list ID for the waitlist

SMTP_HOST=smtp.gmail.com                  # Email export (sending case summaries to users)
SMTP_PORT=587                             # TLS port
SMTP_USER=hello@casematelaw.com           # Sender address
SMTP_PASSWORD=...                         # App password (not your Gmail password)
```

### Optional — Monitoring and Infrastructure

```bash
REDIS_URL=redis://localhost:6379          # Rate limiting backend. If empty, rate limiting is disabled (fail-open).
SENTRY_DSN=https://...@sentry.io/...     # Error tracking. Highly recommended for production.
APP_VERSION=0.4.0                         # Reported in /health response
CORS_ALLOWED_ORIGINS=http://localhost:3000 # Comma-separated. Prod: https://casematelaw.com
```

### Mobile (EAS Build)

Set per build profile in `mobile/eas.json` under `env`:

```bash
EXPO_PUBLIC_API_URL=https://api.casematelaw.com
EXPO_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### CI/CD Secrets (GitHub)

These must be set in **GitHub repository Settings > Secrets and variables > Actions**:

| Secret | Used By | Purpose |
|--------|---------|---------|
| `RAILWAY_TOKEN` | CI deploy job | Authenticate Railway CLI for backend deploys |
| `VERCEL_TOKEN` | CI deploy job | Authenticate Vercel CLI for frontend deploys |
| `VERCEL_ORG_ID` | CI deploy job | Vercel organization identifier |
| `VERCEL_PROJECT_ID` | CI deploy job | Vercel project identifier |
| `EXPO_TOKEN` | Mobile CI job | Authenticate EAS CLI for mobile builds |
| `ANTHROPIC_API_KEY` | CI test job | Run integration tests that call Claude |
| `SUPABASE_URL` | CI test job | Run tests against Supabase |
| `SUPABASE_KEY` | CI test job | Supabase anon key for test environment |

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- A Supabase project (free tier works)
- An Anthropic API key

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/your-org/casemate.git
cd casemate

# 2. Create your .env file from the template
cp .env.example .env
# Open .env and fill in:
#   ANTHROPIC_API_KEY — get from console.anthropic.com
#   SUPABASE_URL — get from Supabase project settings
#   SUPABASE_KEY — anon key from Supabase project settings > API
#   SUPABASE_SERVICE_ROLE_KEY — service role key (same location)
#   SUPABASE_JWT_SECRET — JWT secret from Supabase project settings > API

# 3. Install Python dependencies (creates editable install with dev tools)
pip install -e ".[dev]"

# 4. Install frontend dependencies
cd web && npm install && cd ..

# 5. Start the backend (port 8000)
make dev

# 6. In a second terminal, start the frontend (port 3000)
cd web && npm run dev

# 7. Verify the backend is running
curl http://localhost:8000/health
# Expected: {"status": "ok", "version": "0.4.0"}

# 8. (Optional) Seed the demo profile for testing
make seed
# Creates Sarah Chen's profile with 12 conversations
```

### Makefile Reference

```bash
make dev              # Start backend on port 8000 (uvicorn with reload)
make test             # Run full test suite with coverage (pytest + pytest-cov)
make lint             # Run ruff check + ruff format --check
make format           # Auto-fix lint issues + format code
make verify           # Run lint + test (run before every commit)
make seed             # Seed demo profile (Sarah Chen)
make install          # Install all deps (pip install -e ".[dev]")
make deploy-backend   # railway up --service casemate-backend --detach
make deploy-frontend  # cd web && vercel --prod
make deploy-mobile    # cd mobile && eas build --platform all --profile production
make deploy           # deploy-backend + deploy-frontend
make docker-up        # docker compose up --build
make docker-down      # docker compose down
```

---

## Supabase Setup

### Create the Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project URL, anon key, service role key, and JWT secret from **Settings > API**
3. These go into your `.env` file

### Database Tables

CaseMate uses the following tables. All have Row Level Security (RLS) enabled.

| Table | Purpose | RLS Policy |
|-------|---------|------------|
| `user_profiles` | Legal profiles (state, housing, employment, facts) | Users can only read/write their own profile |
| `conversations` | Chat message history | Users can only access their own conversations |
| `deadlines` | Legal deadline tracking | User-scoped CRUD |
| `workflow_instances` | Guided workflow progress | User-scoped CRUD |
| `attorneys` | Attorney referral directory | Read-only for authenticated users |
| `subscriptions` | Stripe subscription status | Users can only read their own subscription |

### Apply Migrations

Migrations live in `supabase/migrations/` and must be applied in order:

```bash
# Option A: Supabase CLI (recommended)
npx supabase db push

# Option B: Copy-paste into Supabase SQL Editor
# Run each file in supabase/migrations/ in alphabetical order
```

Migration files:
1. `001_user_profiles_rls.sql` — User profiles table with RLS policies
2. `002_conversations_deadlines_workflows_attorneys.sql` — All supporting tables with RLS

### Auth Configuration

CaseMate uses Supabase Auth with email/password sign-up:

1. In Supabase dashboard, go to **Authentication > Providers**
2. Ensure **Email** provider is enabled
3. JWT algorithm: HS256 (default)
4. The `SUPABASE_JWT_SECRET` is used by the backend to verify JWTs on every API request

### Storage Configuration

1. In Supabase dashboard, go to **Storage**
2. Create a bucket named `documents`
3. Set the bucket policy to allow authenticated users to upload/read their own files
4. This bucket stores uploaded legal documents (PDFs, images) for fact extraction

---

## Docker Development

### docker-compose.yml

The development compose file runs three services:

```bash
# Start all services (backend + redis + web)
docker compose up --build
# or
make docker-up

# Stop all services
docker compose down
# or
make docker-down
```

Services:
- **backend** — FastAPI on port 8000, hot-reload enabled, mounts local code
- **redis** — Redis on port 6379 for rate limiting
- **web** — Next.js on port 3000, hot-reload enabled

### Backend Dockerfile

Multi-stage build for minimal image size:

```
Stage 1 (deps):    Install Python dependencies into a virtual environment
Stage 2 (builder): Copy application code
Stage 3 (runtime): Copy venv + app code, run as non-root user
```

Key details:
- Base image: Python 3.12-slim
- Runs as non-root user (`appuser`)
- Health check: `curl -f http://localhost:8000/health`
- Workers: 2 uvicorn workers for concurrency
- Exposed port: 8000

### Frontend Dockerfile (web/Dockerfile)

Multi-stage build for Next.js standalone output:

```
Stage 1 (deps):    Install node_modules
Stage 2 (builder): Build Next.js production bundle (standalone output)
Stage 3 (runner):  Copy standalone server, run as non-root user
```

Key details:
- Base image: Node 18-alpine
- Runs as non-root user (`nextjs`)
- Uses Next.js standalone output mode for minimal image
- Exposed port: 3000

---

## Docker Production

### docker-compose.prod.yml

The production compose file adds security hardening and an nginx reverse proxy:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Additional features over development compose:
- **Resource limits** — CPU and memory caps on all services
- **Redis** — AOF persistence enabled, 128MB memory limit
- **Nginx** — Reverse proxy with SSL termination, rate limiting, security headers
- **Health checks** — All services have health check probes
- **Log rotation** — JSON format, 10MB max per file, 3 files retained

---

## Nginx Configuration

The production nginx config (`nginx/nginx.conf`) handles:

### SSL/TLS Termination
- Protocols: TLSv1.2 and TLSv1.3 only (older protocols disabled)
- Certificate paths configured for your domain

### Rate Limiting
- 10 requests per second per IP address
- Burst allowance for legitimate traffic spikes
- Returns 429 Too Many Requests when exceeded

### Security Headers
Every response includes:
- `Strict-Transport-Security` (HSTS) — force HTTPS for 1 year
- `X-Frame-Options: DENY` — prevent clickjacking
- `X-Content-Type-Options: nosniff` — prevent MIME sniffing
- `Content-Security-Policy` — restrict resource loading origins
- `X-XSS-Protection` — legacy XSS filter

### Routing
- `/api/*` requests proxy to `backend:8000`
- All other requests proxy to `web:3000`

---

## Backend Deployment (Railway)

### Prerequisites

1. Create a Railway account at [railway.app](https://railway.app)
2. Create a new project and service named `casemate-backend`
3. Install the Railway CLI: `npm install -g @railway/cli`
4. Generate a `RAILWAY_TOKEN` from Railway dashboard for CI/CD
5. Add the token to GitHub Secrets as `RAILWAY_TOKEN`

### Configure Environment Variables

In the Railway dashboard for `casemate-backend`, set all required backend environment variables:

```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=...
REDIS_URL=<from Railway Redis plugin>
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
CORS_ALLOWED_ORIGINS=https://casematelaw.com
SENTRY_DSN=https://...@sentry.io/...
APP_VERSION=0.4.0
```

### Add Redis Plugin

1. In your Railway project, click **+ New** > **Database** > **Redis**
2. Copy the `REDIS_URL` from the Redis service variables
3. Paste it into the `casemate-backend` service variables

### Railway Configuration

The `railway.toml` tells Railway how to build and deploy:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Deploy

```bash
# Manual deploy
railway login
railway up --service casemate-backend --detach

# Or via Makefile
make deploy-backend

# Verify
curl https://api.casematelaw.com/health
# Expected: {"status": "ok", "version": "0.4.0"}
```

---

## Frontend Deployment (Vercel)

### Prerequisites

1. Create a Vercel account at [vercel.com](https://vercel.com)
2. Import the GitHub repository
3. Set the root directory to `web`
4. Install the Vercel CLI: `npm install -g vercel`
5. Get `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` from Vercel dashboard
6. Add all three to GitHub Secrets

### Configure Environment Variables

In the Vercel dashboard under **Settings > Environment Variables**, set:

```
NEXT_PUBLIC_API_URL=https://api.casematelaw.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

These are embedded at build time. Changing them requires a redeploy.

### Vercel Configuration

The `web/vercel.json` controls build and routing:

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "rewrites": [
    { "source": "/api/proxy/:path*", "destination": "${BACKEND_URL}/api/:path*" }
  ]
}
```

### Deploy

```bash
# Manual deploy
cd web && vercel --prod

# Or via Makefile
make deploy-frontend
```

Vercel automatically creates preview deployments for every PR. Production deploys
happen on merge to `main` or via manual `vercel --prod`.

---

## Mobile Deployment (EAS)

### Prerequisites

1. Expo account with EAS configured
2. Apple Developer account ($99/year) for iOS
3. Google Play Console account ($25 one-time) for Android
4. `EXPO_TOKEN` set in GitHub Secrets

### Build Profiles

Defined in `mobile/eas.json`:

| Profile | Use Case | Distribution | When |
|---------|----------|-------------|------|
| `development` | Local testing with Expo dev client | Internal (simulator/APK) | During development |
| `preview` | QA and stakeholder review | Internal (TestFlight/APK) | PR builds |
| `production` | App Store / Google Play release | Store submission | Merge to main |

### Build Commands

```bash
cd mobile

# Development build (simulator + dev client)
npx eas build --platform all --profile development --non-interactive

# Preview build (TestFlight + internal APK)
npx eas build --platform all --profile preview --non-interactive

# Production build (store submission)
npx eas build --platform all --profile production --non-interactive
```

### Submit to Stores

```bash
# iOS — submits to App Store Connect for TestFlight / App Store review
npx eas submit --platform ios --profile production

# Android — submits to Google Play Console
npx eas submit --platform android --profile production

# Or via Makefile (builds + submits)
make deploy-mobile
```

### Mobile Environment Variables

Set per profile in `mobile/eas.json` under the `env` key:

```json
{
  "build": {
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.casematelaw.com",
        "EXPO_PUBLIC_SUPABASE_URL": "https://xxx.supabase.co",
        "EXPO_PUBLIC_SUPABASE_ANON_KEY": "eyJ..."
      }
    }
  }
}
```

---

## CI/CD Pipeline

### Main Pipeline (`.github/workflows/ci.yml`)

Triggered on every push to `main`:

```
Push to main
    │
    ├─── Backend Job (parallel)
    │    ├── ruff check (linting)
    │    ├── mypy (type checking)
    │    └── pytest (462 tests, 91% coverage target)
    │
    ├─── Frontend Job (parallel)
    │    ├── eslint (linting)
    │    ├── jest (143 tests)
    │    └── next build (production build)
    │
    ├─── E2E Job (parallel)
    │    └── Playwright smoke tests against staging
    │
    └─── All pass?
         │
         ▼
    Docker Build
    ├── Build backend image
    └── Build frontend image
         │
         ▼
    Deploy to Staging
    ├── Railway (backend)
    └── Vercel (frontend preview)
         │
         ▼
    Deploy to Production (requires environment approval)
    ├── Railway (backend)
    └── Vercel (frontend --prod)
```

### Mobile Pipeline (`.github/workflows/mobile.yml`)

Triggered on changes to `mobile/` or `shared/` directories:

```
Change in mobile/ or shared/
    │
    ├── TypeScript typecheck
    ├── EAS Build
    │   ├── PR → preview profile (TestFlight / internal APK)
    │   └── main → production profile (store submission)
    └── EAS Submit (production only)
        ├── iOS → App Store Connect
        └── Android → Google Play Console
```

### Required GitHub Secrets for CI/CD

| Secret | Pipeline | Purpose |
|--------|----------|---------|
| `RAILWAY_TOKEN` | Main | Deploy backend to Railway |
| `VERCEL_TOKEN` | Main | Deploy frontend to Vercel |
| `VERCEL_ORG_ID` | Main | Identify Vercel organization |
| `VERCEL_PROJECT_ID` | Main | Identify Vercel project |
| `EXPO_TOKEN` | Mobile | Authenticate EAS builds and submissions |

---

## Database Migrations

### Migration Files

Located in `supabase/migrations/`, applied in alphabetical order:

| File | Contents |
|------|----------|
| `001_user_profiles_rls.sql` | `user_profiles` table, RLS policies for user-scoped access |
| `002_conversations_deadlines_workflows_attorneys.sql` | `conversations`, `deadlines`, `workflow_instances`, `attorneys`, `subscriptions` tables with RLS |

### Applying Migrations

```bash
# Using Supabase CLI (recommended for automation)
npx supabase db push

# Using Supabase Dashboard (manual)
# Go to SQL Editor, paste each migration file, run in order

# Verify tables exist
npx supabase db dump --schema public
```

### Writing New Migrations

1. Create a new file in `supabase/migrations/` with the next sequence number
2. Write forward migration SQL
3. Include a comment block at the top explaining what the migration does
4. Test locally before pushing to production
5. Migrations are append-only — never edit a migration that has been applied

### Rollback Strategy

- All migrations should be reversible where possible
- Supabase Pro plan: point-in-time recovery (restore to any second)
- Supabase Free plan: daily automatic backups
- For manual rollback: write a new migration that reverses the previous one

---

## Health Checks and Verification

### Backend Health

```bash
# Basic health check
curl https://api.casematelaw.com/health
# Response: {"status": "ok", "version": "0.4.0"}

# Prometheus-compatible metrics
curl https://api.casematelaw.com/metrics
# Response: counters and histograms for request volume, latency, errors
```

The `/health` endpoint verifies:
- The FastAPI server is running
- The app version is reported correctly

### Frontend Health

Vercel provides built-in uptime monitoring. Additionally:
- Every Vercel deployment gets a unique URL for testing before promotion
- Preview deployments are created automatically for every PR

### Redis Health

```bash
# Via Docker
docker exec casemate-redis redis-cli ping
# Response: PONG

# Via Railway
# Check Redis service health in Railway dashboard
```

### Full Stack Verification

After any deployment, run this checklist:

```bash
# 1. Backend is alive
curl -s https://api.casematelaw.com/health | jq .

# 2. Frontend loads
curl -s -o /dev/null -w "%{http_code}" https://casematelaw.com
# Expected: 200

# 3. Auth works (attempt login)
curl -s -X POST https://api.casematelaw.com/api/profile \
  -H "Authorization: Bearer <valid-jwt>" \
  | jq .

# 4. Chat endpoint responds
curl -s -X POST https://api.casematelaw.com/api/chat \
  -H "Authorization: Bearer <valid-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my rights as a tenant?"}' \
  | jq .
```

---

## Monitoring and Logging

### Structured Logging

All backend logs use `structlog` with JSON output. Every log line includes:
- `user_id` — which user triggered the action
- `event` — what happened
- `timestamp` — when it happened
- Additional context fields relevant to the event

Example log output:
```json
{
  "event": "profile_updated",
  "user_id": "usr_abc123",
  "facts_added": 3,
  "timestamp": "2026-03-29T14:30:00Z"
}
```

### Request Tracing

Every API response includes an `X-Trace-ID` header. Use this to correlate frontend
errors with backend logs. Include the trace ID when reporting issues.

### Error Tracking (Sentry)

When `SENTRY_DSN` is set:
- Backend errors are automatically reported with user context
- Frontend errors are captured via the Sentry Next.js SDK
- Errors include stack traces, request data, and user ID

To set up Sentry:
1. Create a project at [sentry.io](https://sentry.io)
2. Copy the DSN
3. Set `SENTRY_DSN` in Railway (backend) and Vercel (frontend)

### Metrics

The `GET /metrics` endpoint returns Prometheus-compatible data:

- **Request counters** — total requests by endpoint and status code
- **Latency histograms** — p50, p95, p99 response times
- **Error rates** — 4xx and 5xx by endpoint

Platform-level metrics:
- **Railway dashboard** — CPU, memory, network for backend service
- **Supabase dashboard** — query performance, connection pool, storage usage
- **Vercel dashboard** — function invocations, edge network performance

### Log Locations

| Component | Where to find logs |
|-----------|-------------------|
| Backend | Railway service logs (dashboard or `railway logs`) |
| Frontend | Vercel function logs (dashboard) |
| Nginx (Docker prod) | `nginx/logs/` with rotation (10MB, 3 files) |
| Redis | Railway Redis plugin logs |
| Database | Supabase dashboard > Logs |

---

## Rollback Procedures

### Backend Rollback (Railway)

```bash
# List recent deployments
railway deployment list

# Rollback to the previous deployment
railway deployment rollback

# Verify the rollback
curl https://api.casematelaw.com/health
```

Railway keeps a history of deployments. You can roll back to any previous one
from the dashboard or CLI.

### Frontend Rollback (Vercel)

**Option A: CLI**
```bash
vercel rollback
```

**Option B: Dashboard**
1. Go to Vercel dashboard > Deployments
2. Find the last known-good deployment
3. Click the three-dot menu > **Promote to Production**

Vercel rollbacks are instant — they re-point the production URL to a previous build
with no rebuild required.

### Database Rollback (Supabase)

- **Pro plan:** Point-in-time recovery. Restore to any second within the retention window.
- **Free plan:** Daily automatic backups. Restore from the most recent backup.
- **Manual:** Write a new migration that reverses the schema change and apply it.

### Mobile Rollback

Mobile rollbacks are not instant because they go through app store review:
1. Revert the code change on `main`
2. Trigger a new EAS production build
3. Submit to App Store Connect / Google Play Console
4. Wait for review approval (usually 24-48 hours)

For critical issues, use feature flags or a server-side kill switch to disable
broken functionality without a new app release.

---

## Security Checklist

Run through this before every production deployment:

- [ ] All secrets stored in platform dashboards (Railway, Vercel, GitHub Secrets) — never in code
- [ ] `SUPABASE_SERVICE_ROLE_KEY` set only on the backend service, not frontend or mobile
- [ ] `CORS_ALLOWED_ORIGINS` restricted to production domains only (no `localhost`, no `*`)
- [ ] Rate limiting active with Redis connected
- [ ] `STRIPE_WEBHOOK_SECRET` set and verified on every incoming webhook
- [ ] HTTPS enforced on all public endpoints (Vercel and Railway handle this by default)
- [ ] Row Level Security (RLS) enabled on all Supabase tables
- [ ] All Docker containers run as non-root users
- [ ] Security headers configured (HSTS, X-Frame-Options, CSP, X-Content-Type-Options)
- [ ] No `.env` files committed to git (check `.gitignore`)
- [ ] `ANTHROPIC_API_KEY` not exposed to frontend or client code
- [ ] JWT tokens verified on every authenticated API endpoint
- [ ] File uploads validated for type and size before processing
- [ ] SQL queries use parameterized queries (Supabase client handles this)

---

## Pre-Deploy Checklist

Before every production deployment:

```bash
# 1. Run the full verification suite — zero failures required
make verify
# This runs: ruff check + ruff format --check + pytest (462 tests) + coverage

# 2. Verify all environment variables are set in the target platform
#    Backend (Railway): ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY,
#      SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET, REDIS_URL,
#      STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, CORS_ALLOWED_ORIGINS

#    Frontend (Vercel): NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL,
#      NEXT_PUBLIC_SUPABASE_ANON_KEY

# 3. Confirm CORS_ALLOWED_ORIGINS includes only production domains
# 4. Confirm SUPABASE_SERVICE_ROLE_KEY is only on the backend service
# 5. Apply any pending database migrations to production Supabase
npx supabase db push

# 6. Deploy
make deploy

# 7. Post-deploy verification
curl https://api.casematelaw.com/health
# Expected: {"status": "ok", "version": "0.4.0"}

# 8. (If needed) Seed the demo profile
make seed
```

---

## Troubleshooting

### Backend won't start

**Symptom:** Railway deployment fails or `/health` returns 500.

```bash
# Check Railway logs
railway logs --service casemate-backend

# Common causes:
# - Missing ANTHROPIC_API_KEY → "Anthropic client not initialized"
# - Missing SUPABASE_URL → "Supabase client not initialized"
# - Invalid SUPABASE_JWT_SECRET → JWT verification fails on all requests
# - Port conflict → Ensure Railway is not overriding the port
```

### Frontend build fails on Vercel

**Symptom:** Vercel deployment fails during `npm run build`.

```bash
# Common causes:
# - Missing NEXT_PUBLIC_* variables → Build completes but API calls fail at runtime
# - TypeScript errors → Fix locally with `cd web && npm run build`
# - Dependency issues → Delete node_modules and package-lock.json, reinstall
```

### Rate limiting not working

**Symptom:** No 429 responses even under heavy load.

```bash
# Rate limiting fails open — if Redis is unreachable, all requests pass through.
# Check:
# 1. Is REDIS_URL set in Railway?
# 2. Is the Redis plugin running? (Railway dashboard)
# 3. Can the backend reach Redis? (check logs for connection errors)
```

### Profile not updating after chat

**Symptom:** User mentions new facts in chat but profile stays unchanged.

```bash
# The profile updater runs as a FastAPI background task after each response.
# Check:
# 1. Backend logs for "profile_updated" events
# 2. ANTHROPIC_API_KEY is valid (updater makes a separate Claude call)
# 3. SUPABASE_SERVICE_ROLE_KEY has write permissions
# 4. The updater never removes facts — only adds. Check if the fact extraction
#    prompt is actually finding extractable facts in the conversation.
```

### Docker compose fails locally

**Symptom:** `make docker-up` errors out.

```bash
# Common causes:
# - Port 8000 or 3000 already in use → stop other services or change ports
# - Docker not running → start Docker Desktop
# - .env file missing → cp .env.example .env and fill in values
# - Old images cached → docker compose down && docker compose up --build --force-recreate
```

### Mobile build fails on EAS

**Symptom:** EAS build errors in CI or locally.

```bash
# Common causes:
# - EXPO_TOKEN expired or invalid → regenerate in Expo dashboard
# - Missing Apple credentials → run `eas credentials` to configure
# - SDK version mismatch → check mobile/app.json matches installed expo version
# - OTA update issues → clear EAS cache with `eas build --clear-cache`
```

### Supabase RLS blocking requests

**Symptom:** API returns 403 or empty results for authenticated users.

```bash
# Check:
# 1. The JWT is being sent in the Authorization header
# 2. The JWT contains the correct user ID (decode at jwt.io)
# 3. RLS policies match the expected auth.uid() format
# 4. Test the query directly in Supabase SQL Editor with the service role key
#    to confirm the data exists (bypasses RLS)
```

---

## Quick Reference — Deploy Commands

```bash
# Full deployment (backend + frontend)
make deploy

# Backend only
make deploy-backend

# Frontend only
make deploy-frontend

# Mobile (all platforms)
make deploy-mobile

# Docker development
make docker-up
make docker-down

# Docker production
docker compose -f docker-compose.prod.yml up -d

# Verify
make verify

# Rollback
railway deployment rollback          # Backend
vercel rollback                      # Frontend
```
