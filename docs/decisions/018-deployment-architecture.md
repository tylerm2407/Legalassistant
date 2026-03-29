# ADR 018 — Deployment architecture with Vercel and Railway

**Date:** 2026-03-29
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

The CaseMate web frontend deploys to Vercel. The FastAPI backend deploys to Railway. Both platforms provide push-to-deploy workflows with automatic SSL, health checks, and preview environments.

---

## Context

CaseMate is a monorepo with a Next.js 14 frontend in `web/` and a FastAPI backend in `backend/`. The team is two people. Neither has dedicated DevOps experience, and the product is pre-launch with no paying customers yet. The deployment solution must minimize operational overhead while providing production-grade reliability.

The backend serves the Anthropic Claude API calls, Supabase profile reads/writes, and document processing. It needs persistent process support (background tasks for profile updates), WebSocket or SSE capability (chat streaming), and Docker support (for reproducible builds with Python dependencies).

The frontend is a standard Next.js app with server-side rendering, API routes (waitlist signup), and static marketing pages. It needs edge network distribution for fast global load times and automatic preview deployments for pull requests.

---

## The implementation

**Frontend (Vercel):**
Vercel auto-detects the Next.js framework in `web/` and configures build settings, environment variables, and edge caching automatically. The `vercel.json` or project settings point to the `web/` subdirectory as the root. Environment variables (`NEXT_PUBLIC_APP_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `BACKEND_URL`) are set in the Vercel dashboard. Every push to `main` triggers a production deploy. Every pull request gets a preview URL.

**Backend (Railway):**
Railway deploys the FastAPI backend from the `Dockerfile` in the repository root. The Dockerfile installs Python 3.12 dependencies from `pyproject.toml` and runs `uvicorn backend.main:app`. Railway provides managed environment variables for `ANTHROPIC_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, and `REDIS_URL`. Health checks hit `GET /health` every 30 seconds. Railway's persistent process model supports FastAPI's background tasks for profile auto-updating.

**Database (Supabase):**
Supabase runs as a managed service, separate from both deployment platforms. Both the Vercel frontend (via the anon key) and the Railway backend (via the service role key) connect to the same Supabase project. Row Level Security policies enforce that users can only access their own data regardless of which client makes the request.

---

## Alternatives considered

**AWS (EC2 + ECS or Lambda)**
Considered. AWS provides the most flexibility and scalability. Rejected because configuring VPCs, load balancers, security groups, IAM roles, and ECS task definitions is a multi-day effort for a two-person team. The operational overhead is not justified for a pre-launch product with single-digit concurrent users.

**Fly.io for backend**
Considered. Fly.io provides edge deployment for Docker containers with a simple CLI. Rejected because Fly.io's free tier is more limited than Railway's, and Railway's dashboard provides better visibility into logs, deployments, and environment variables for a team that is not experienced with infrastructure management.

**Self-hosted (VPS on DigitalOcean or Hetzner)**
Considered. A VPS provides full control at low cost. Rejected because self-hosting requires managing OS updates, SSL certificates, reverse proxy configuration, process supervision, and monitoring — all operational work that takes time away from product development.

**Vercel serverless functions for backend**
Considered. Vercel can run API routes as serverless functions, eliminating the need for a separate backend host. Rejected because FastAPI's background tasks, SSE streaming, and startup-time initialization (Anthropic client singleton, Redis connection) are not well suited to serverless execution. Cold starts would degrade the chat experience.

---

## Consequences

**Positive:**
- Push-to-deploy on both platforms — no manual deployment steps
- Automatic SSL and custom domain support on both Vercel and Railway
- Preview deployments on Vercel for every pull request
- Combined hosting cost under $20/month at current usage levels
- Health check monitoring on Railway catches backend crashes automatically
- Separation of frontend and backend allows independent scaling

**Negative:**
- Two deployment platforms to manage instead of one
- Backend URL must be configured as an environment variable in the frontend (no same-origin API calls)
- Railway's free tier has usage limits that may require a paid plan as traffic grows
- Vendor lock-in to Vercel's Next.js optimizations (mitigated by Next.js being deployable anywhere)
- Cross-origin requests between Vercel and Railway require CORS configuration

---

## Status

Accepted. Vercel for the frontend and Railway for the backend provides the right balance of simplicity, reliability, and cost for a two-person team shipping a pre-launch product. If traffic grows past Railway's capacity or cost becomes a concern, migrating the backend to Fly.io or a self-hosted Docker setup is a straightforward change — the Dockerfile and FastAPI app are platform-agnostic.
