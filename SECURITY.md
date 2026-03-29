# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |
| < 0.1   | No                 |

## Reporting a Vulnerability

We take the security of CaseMate seriously. If you discover a security vulnerability, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

### How to Report

Send an email to **security@novawealthhq.com** with the following information:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The affected component(s) (backend, frontend, API, authentication, etc.)
- The potential impact and severity (your assessment)
- Any proof-of-concept code or screenshots
- Your name and contact information (optional, for credit)

### What to Expect

| Step                    | Timeline              |
|-------------------------|-----------------------|
| Acknowledgment          | Within 48 hours       |
| Initial triage          | Within 5 business days|
| Status update           | Every 10 business days|
| Fix deployed (critical) | Within 7 days         |
| Fix deployed (moderate) | Within 30 days        |

### Disclosure Policy

We follow a coordinated disclosure process:

1. The reporter submits the vulnerability privately via email.
2. Our team acknowledges receipt and begins triage.
3. We work on a fix and coordinate a disclosure timeline with the reporter.
4. The fix is deployed and verified in production.
5. A public advisory is published after the fix is live.
6. The reporter receives credit (unless they prefer to remain anonymous).

The standard disclosure window is **90 days** from the initial report. If we need additional time for a complex fix, we will negotiate an extension with the reporter.

## Security Best Practices for Contributors

All contributors must follow these practices:

- **No secrets in code.** API keys, tokens, passwords, and credentials must never appear in source code, comments, or commit history. Use environment variables exclusively.
- **Use `.env` for local secrets.** The `.env` file is listed in `.gitignore`. Copy `.env.example` and populate it locally.
- **Validate all input.** Every API endpoint must validate and sanitize input using Pydantic models with field constraints.
- **Use parameterized queries.** Never construct SQL strings by concatenation. All database access goes through Supabase client methods.
- **Enforce authentication.** Every endpoint that accesses user data must include `Depends(verify_supabase_jwt)`.
- **Follow the principle of least privilege.** Frontend uses the Supabase anon key. Only the backend uses the service role key.
- **Review dependencies.** Before adding a new dependency, verify it is actively maintained and has no known critical vulnerabilities.

## Known Security Controls

CaseMate implements the following security measures:

| Control                    | Implementation                                              |
|----------------------------|-------------------------------------------------------------|
| Authentication             | JWT verification via Supabase Auth (`backend/utils/auth.py`)|
| Authorization              | Row Level Security (RLS) policies on all Supabase tables    |
| Rate limiting              | Redis-backed per-user rate limits (`backend/utils/rate_limiter.py`) |
| Input validation           | Pydantic v2 models with `Field` constraints on all endpoints|
| CORS                       | Allowlist-based origin restriction via FastAPI middleware    |
| Secret management          | All secrets loaded from environment variables               |
| File upload limits         | 25 MB maximum file size enforced server-side                |
| API retry with backoff     | Exponential backoff on external API calls (`backend/utils/retry.py`) |
| Structured logging         | `structlog` with user context for audit trails              |

## Out of Scope

The following are out of scope for our vulnerability disclosure program:

- Social engineering attacks against NovaWealth employees or users
- Denial of service (DoS/DDoS) testing against production infrastructure
- Physical attacks against offices, data centers, or equipment
- Attacks against third-party services (Supabase, Anthropic, Stripe) -- report those to the respective vendors
- Spam or abuse of the waitlist signup form
- Vulnerabilities in dependencies that have already been publicly disclosed and have a patch available (please verify we are on the latest version first)
