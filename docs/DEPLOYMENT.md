# Deployment Guide

CaseMate uses a multi-platform deployment strategy: **Vercel** for the web frontend, **Railway** for the backend API, **Supabase** for the database, and **EAS** for mobile app builds.

---

## Architecture

```
                    ┌─────────────┐
                    │   Vercel    │
                    │  (Next.js)  │
                    │  Frontend   │
                    └──────┬──────┘
                           │ HTTPS
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Supabase   │◄───│  Railway    │───►│   Redis     │
│  (Postgres  │    │  (FastAPI)  │    │  (Rate      │
│   + Auth    │    │  Backend    │    │   Limiting) │
│   + Storage)│    └─────────────┘    └─────────────┘
└─────────────┘           │
                          ▼
                   ┌─────────────┐
                   │  Anthropic  │
                   │  Claude API │
                   └─────────────┘
```

---

## Environments

| Environment | Backend | Frontend | Database |
|-------------|---------|----------|----------|
| **Development** | `localhost:8000` | `localhost:3000` | Supabase (dev project) |
| **Staging** | Railway (staging service) | Vercel (preview) | Supabase (staging project) |
| **Production** | Railway (production service) | Vercel (production) | Supabase (production project) |

Environment-specific configuration templates:
- `.env.example` — Local development
- `.env.production.example` — Production deployment

---

## CI/CD Pipeline

### Automated Workflow (`.github/workflows/ci.yml`)

```
Push to main
    │
    ├── Backend: lint → typecheck → test (303 tests, 87% coverage)
    ├── Frontend: lint → test (143 tests) → build
    ├── E2E: Playwright tests against staging
    └── Mobile: typecheck → EAS validate
           │
           ▼
    Docker: build backend + frontend images
           │
           ▼
    Deploy staging: Railway (backend) + Vercel (frontend)
           │
           ▼
    Deploy production: Railway + Vercel (requires environment approval)
```

### Mobile Pipeline (`.github/workflows/mobile.yml`)

Triggered on changes to `mobile/` or `shared/`:
1. TypeScript typecheck
2. EAS Build (preview on PR, production on main)
3. EAS Submit to App Store Connect + Google Play Console

---

## Backend Deployment (Railway)

### Prerequisites
- Railway account with project created
- `RAILWAY_TOKEN` set in GitHub Secrets
- Environment variables configured in Railway dashboard

### Manual Deploy
```bash
npm install -g @railway/cli
railway login
railway up --service casemate-backend --detach
```

### Makefile Deploy
```bash
make deploy-backend
```

### Railway Configuration (`railway.toml`)
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

### Docker Image
Multi-stage build (`Dockerfile`):
- Stage 1: Install Python deps in virtual env
- Stage 2: Copy venv + app code, run as non-root user
- Health check: `curl -f http://localhost:8000/health`
- Workers: 2 uvicorn workers for concurrency

### Health Check
```bash
curl https://api.casematelaw.com/health
# → {"status": "ok", "version": "0.3.0"}
```

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account with project linked to GitHub repo
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` in GitHub Secrets
- Build-time environment variables configured in Vercel dashboard

### Manual Deploy
```bash
npm install -g vercel
cd web && vercel --prod
```

### Makefile Deploy
```bash
make deploy-frontend
```

### Vercel Configuration (`web/vercel.json`)
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

### Docker Image (`web/Dockerfile`)
Multi-stage build for standalone deployment:
- Stage 1: Install node_modules
- Stage 2: Build Next.js production bundle
- Stage 3: Run standalone server as non-root user

---

## Mobile Deployment (EAS)

### Prerequisites
- Expo account with EAS configured
- `EXPO_TOKEN` in GitHub Secrets
- Apple Developer account (iOS) and Google Play Console (Android)

### Build Profiles (`mobile/eas.json`)

| Profile | Use Case | Distribution |
|---------|----------|-------------|
| `development` | Local testing with dev client | Internal (simulator/APK) |
| `preview` | QA and stakeholder review | Internal (TestFlight/APK) |
| `production` | App Store / Google Play release | Store submission |

### Manual Build
```bash
cd mobile
npx eas build --platform all --profile production --non-interactive
```

### Manual Submit
```bash
# iOS → App Store Connect
npx eas submit --platform ios --profile production

# Android → Google Play Console
npx eas submit --platform android --profile production
```

### Makefile Deploy
```bash
make deploy-mobile
```

---

## Docker Deployment

### Development
```bash
docker compose up --build                    # Start all services
docker compose down                          # Stop all services
make docker-up                               # Shortcut
make docker-down                             # Shortcut
```

### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

Production compose (`docker-compose.prod.yml`) includes:
- Resource limits (CPU/memory) on all services
- Redis with AOF persistence and 128MB memory limit
- Nginx reverse proxy with SSL termination, rate limiting, security headers
- Health checks on all services
- JSON log rotation (10MB, 3 files)

---

## Environment Variables

### Backend (Railway)

All variables from `.env.production.example`:

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key (backend only) |
| `SUPABASE_JWT_SECRET` | Yes | JWT verification secret |
| `REDIS_URL` | Yes (prod) | Rate limiting (fail-open if empty) |
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Yes | Webhook signing secret |
| `CORS_ALLOWED_ORIGINS` | Yes | Production domain whitelist |
| `SENTRY_DSN` | Recommended | Error tracking |

### Frontend (Vercel)

Build-time variables (prefix `NEXT_PUBLIC_`):

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase public key |
| `NEXT_PUBLIC_APP_URL` | Frontend URL (for SSR) |

### Mobile (EAS)

Set per build profile in `eas.json`:

| Variable | Description |
|----------|-------------|
| `EXPO_PUBLIC_API_URL` | Backend API URL |
| `EXPO_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | Supabase public key |

---

## Database Migrations

Migrations in `supabase/migrations/` applied in order:

1. `001_user_profiles_rls.sql` — User profiles table with RLS policies
2. `002_conversations_deadlines_workflows_attorneys.sql` — All supporting tables with RLS

```bash
# Apply via Supabase CLI
supabase db push

# Or via SQL editor in Supabase dashboard
```

See `docs/DATABASE.md` for the full schema reference.

---

## Monitoring

### Health Checks
- **Backend:** `GET /health` → `{"status": "ok", "version": "0.3.0"}`
- **Frontend:** Vercel built-in uptime monitoring
- **Database:** Supabase dashboard health metrics
- **Redis:** `redis-cli ping` via Docker health check

### Logging
- **Backend:** structlog JSON output with `user_id` context on every log line
- **Frontend:** Vercel function logs
- **Nginx:** Access/error logs with rotation (10MB, 3 files)

### Error Tracking
- Sentry integration via `SENTRY_DSN` environment variable
- Backend errors auto-reported with user context
- Frontend errors captured via Sentry Next.js SDK

### Metrics
- Railway: CPU, memory, network metrics dashboard
- Supabase: Query performance, connection pool, storage metrics
- Custom: OpenTelemetry-compatible telemetry via `backend/utils/telemetry.py`

---

## Rollback

### Backend (Railway)
```bash
railway deployment list        # List recent deployments
railway deployment rollback    # Rollback to previous
```

### Frontend (Vercel)
Instant rollback via Vercel dashboard → Deployments → select previous → Promote to Production.

### Database (Supabase)
Point-in-time recovery on Pro plan. Daily backups on Free plan.

---

## Security Checklist

- [ ] All secrets in platform dashboards, never in code
- [ ] `SUPABASE_SERVICE_ROLE_KEY` only on backend
- [ ] CORS restricted to production domains
- [ ] Rate limiting active with Redis
- [ ] Stripe webhook secret verified on every webhook
- [ ] HTTPS enforced on all endpoints
- [ ] Row Level Security enabled on all Supabase tables
- [ ] Non-root user in Docker containers
- [ ] Security headers set (HSTS, X-Frame-Options, CSP)

---

## Pre-Deploy Checklist

1. `make verify` — zero failures (lint + 303 backend tests + 143 frontend tests)
2. All required env vars set in deployment platform
3. `CORS_ALLOWED_ORIGINS` includes only production domains
4. `SUPABASE_SERVICE_ROLE_KEY` set only on backend
5. Database migrations applied to production Supabase
6. After deploy: `GET /health` returns 200
7. Seed demo profile if needed: `make seed`
