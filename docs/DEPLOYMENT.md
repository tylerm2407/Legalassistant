# Deployment

CaseMate is deployed as three services: a FastAPI backend, a Next.js frontend, and a Supabase-hosted PostgreSQL database.

See `ARCHITECTURE.md` for the full system design.

## Docker — Backend

The backend is containerized via `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY backend/ backend/
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run locally:

```bash
docker build -t casemate-backend .
docker run -p 8000:8000 --env-file .env casemate-backend
```

The image includes only the `backend/` directory and `pyproject.toml` — no frontend code, tests, or dev dependencies.

## Deployment Targets

| Service | Platform | Notes |
|---------|----------|-------|
| Backend (FastAPI) | Railway | Deploy the Docker image. Set all env vars in Railway dashboard. |
| Frontend (Next.js) | Vercel | Connect the repo, set root directory to `web/`. Set `NEXT_PUBLIC_*` env vars. |
| Database | Supabase | Managed PostgreSQL. Apply migrations from `supabase/migrations/`. |
| Redis (optional) | Railway or Upstash | For rate limiting. Set `REDIS_URL` on the backend. Fails open if unavailable. |

## Environment Variables

All required variables are documented in `.env.example`. Copy it to `.env` for local dev, or set them in your deployment platform's dashboard.

### Required

| Variable | Used by | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Backend | Claude API key. All AI calls go through this. |
| `SUPABASE_URL` | Backend | Supabase project URL. |
| `SUPABASE_KEY` | Backend | Supabase anon/public key. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | Service role key for profile writes. **Never expose to frontend.** |
| `SUPABASE_JWT_SECRET` | Backend | For JWT verification. See `docs/SECURITY.md`. |

### Frontend

| Variable | Used by | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Frontend | Backend URL (e.g. `https://api.casematelaw.com`). |
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend | Supabase project URL (public). |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend | Supabase anon key (public). |

### Optional

| Variable | Used by | Description |
|----------|---------|-------------|
| `REDIS_URL` | Backend | Redis connection string for rate limiting. Fails open without it. |
| `CORS_ALLOWED_ORIGINS` | Backend | Comma-separated allowed origins. Defaults to `http://localhost:3000,http://localhost:8081`. |
| `MAILCHIMP_API_KEY` | Backend | For waitlist signups. |
| `MAILCHIMP_SERVER_PREFIX` | Backend | Datacenter prefix (e.g. `us21`). |
| `MAILCHIMP_LIST_ID` | Backend | Audience/list ID. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` | Backend | For email export feature. |

## CORS Configuration

For production, set `CORS_ALLOWED_ORIGINS` to your frontend domain(s):

```
CORS_ALLOWED_ORIGINS=https://casematelaw.com,https://www.casematelaw.com
```

The backend reads this variable in `backend/main.py` and passes it to FastAPI's `CORSMiddleware`. See `docs/SECURITY.md` for the full CORS policy.

## Health Check

The backend exposes `GET /health` (no auth required) returning:

```json
{"status": "ok", "version": "0.1.0"}
```

Configure your deployment platform to poll this endpoint for uptime monitoring. Railway and similar platforms support health check URLs natively.

## Database Migrations

Migrations are in `supabase/migrations/` and should be applied in order:

1. `001_user_profiles_rls.sql` — Creates `user_profiles` table with RLS policies.
2. `002_conversations_deadlines_workflows_attorneys.sql` — Creates `conversations`, `deadlines`, `workflow_instances`, and `attorneys` tables with RLS.

Apply via the Supabase dashboard SQL editor or CLI:

```bash
supabase db push
```

See `docs/DATABASE.md` for the full schema reference.

## Pre-Deploy Checklist

1. Run `make verify` locally — zero failures.
2. Confirm all required env vars are set in the deployment platform.
3. Confirm `CORS_ALLOWED_ORIGINS` includes only production domains.
4. Confirm `SUPABASE_SERVICE_ROLE_KEY` is set only on the backend, not the frontend.
5. Apply any new migrations to the Supabase project.
6. After deploy, verify `GET /health` returns 200.
7. Seed the demo profile if needed: `make seed` (or run `scripts/seed_demo.py` manually).
