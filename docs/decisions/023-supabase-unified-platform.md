# ADR 023 — Supabase as Unified Platform (Auth + DB + Storage + Realtime)

**Status:** Accepted
**Date:** 2026-03-29
**Decision Makers:** Tyler Moore, Owen Ash

---

## Context

CaseMate requires four infrastructure capabilities:

1. **Authentication** — JWT-based user auth with email/password and social login. Every API endpoint must verify the user's identity.
2. **Structured storage** — Legal profiles, conversations, legal facts, active issues. This is highly relational data: a user has many conversations, each conversation has many messages, each user has one profile with many legal facts. This is not a vector similarity problem — it is a structured data problem.
3. **File storage** — Users upload legal documents (leases, contracts, court filings) as PDFs and images. Files must be tied to the user's auth identity so one user cannot access another's documents.
4. **Realtime updates** — The legal profile sidebar in the chat UI must update live when the background profile updater extracts new facts from a conversation. The user should see their profile grow without refreshing the page.

We are a 2-person team. Every additional service we integrate is another SDK to learn, another set of credentials to manage, another billing account to monitor, another failure mode to handle, and another security surface to audit. Integration cost is not linear — it is multiplicative. Four separate services means six pairwise integration points, not four.

The decision needed to optimize for: minimal integration surface, strong authorization guarantees (legal data is sensitive), and speed of development.

---

## Decision

Use Supabase as the single platform for authentication, database (Postgres), file storage, and realtime subscriptions.

Specifically:

- **Auth:** Supabase Auth with JWT tokens. The backend verifies JWTs using the Supabase JWT secret. Social login (Google, Apple) available when needed without additional integration.
- **Database:** Postgres with Row Level Security (RLS) policies on every user-facing table. RLS ensures that even if application code has an authorization bug, a user can only read/write their own rows. The database enforces authorization, not just the application.
- **Storage:** Supabase Storage buckets with RLS policies. A user's uploaded documents are in a path scoped to their `user_id`. The storage policy ensures a user can only access files in their own path. No application-level file access control needed.
- **Realtime:** Supabase Realtime subscriptions on the `user_profiles` table. When the backend profile updater writes new legal facts, the Realtime subscription pushes the change to the client. The profile sidebar updates without polling or manual refresh.

All four capabilities use a single SDK (`supabase-py` on the backend, `@supabase/supabase-js` on the frontend), a single set of credentials (URL + anon key + service role key), and a single billing account.

---

## Alternatives Considered

### Firebase (Firestore + Auth + Storage + Realtime)

Firebase is the most direct competitor to Supabase for this use case. It provides all four capabilities in a single platform. However:

- **NoSQL does not fit legal profiles.** A user's legal profile has a fixed schema: state, housing_situation, employment_type, family_status, plus arrays of legal_facts and active_issues. This is textbook relational data. Firestore's document model would require denormalization that makes queries like "find all users in Massachusetts with active landlord disputes" inefficient or impossible without composite indexes.
- **No Row Level Security at the database level.** Firestore Security Rules operate at the API layer, not the storage engine. A misconfigured rule can expose data. Supabase RLS policies are Postgres policies — they are enforced by the database engine regardless of how the data is accessed (API, direct SQL, migration scripts).
- **Vendor lock-in.** Firestore's query language and data model are proprietary. Migrating off Firebase requires rewriting every query. Supabase is Postgres — we can migrate to any Postgres host (RDS, Cloud SQL, self-hosted) by changing a connection string.
- **Cost model.** Firebase charges per document read/write. CaseMate reads the user's profile on every chat request (to build the system prompt) and writes to it after every response (profile updater). At scale, this per-operation pricing becomes expensive for our access pattern. Supabase charges for compute and storage, not operations.

Rejected. NoSQL is the wrong data model for structured legal profiles, and the lack of database-level RLS is a security concern for sensitive legal data.

### Separate best-in-class services (Auth0 + Postgres + S3 + Pusher)

Each service is best-in-class for its specific capability. Auth0 has the most mature auth flows. RDS Postgres is the most battle-tested managed Postgres. S3 is the most reliable object storage. Pusher has the most mature realtime infrastructure.

The problem is integration tax:

- **Four SDKs** to install, configure, and keep updated. Four sets of breaking changes to track across major versions.
- **Four sets of credentials** to manage. Four secrets in `.env`. Four rotation policies. Four audit trails.
- **Four billing accounts** to monitor. Four usage dashboards. Four cost alerts.
- **Four security surfaces** to audit. Auth0's token must be trusted by Postgres (custom JWT verification), S3 policies must reference Auth0 user IDs (cross-service authorization), Pusher channels must be authorized against Auth0 tokens (another cross-service integration).
- **Cross-service authorization is the hardest part.** Ensuring that User A cannot access User B's S3 files requires implementing authorization logic in the application layer — there is no equivalent to Supabase's RLS that spans Auth0 + S3. Every authorization check is application code that can have bugs.

For a 2-person team building a product that needs to ship in weeks, the integration tax of four separate services is prohibitive. Each service is better in isolation, but the system is worse in aggregate.

Rejected. Integration cost exceeds the sum of individual service advantages.

### PlanetScale + Clerk + S3 + Ably

A more modern variant of the separate-services approach. PlanetScale (MySQL-compatible serverless database), Clerk (developer-friendly auth), S3 (file storage), Ably (realtime messaging).

Same integration tax problems as above, plus: PlanetScale is MySQL, not Postgres. Postgres has richer JSON support (critical for storing legal_facts as JSONB), richer full-text search (useful for searching conversation history), and Row Level Security (MySQL has no equivalent). Switching to MySQL would sacrifice database-level authorization enforcement.

Rejected for the same reasons as the separate-services approach, with the additional downside of MySQL's limitations.

---

## Consequences

### Positive

- **Single SDK, single credential set.** One `supabase-py` import on the backend, one `@supabase/supabase-js` import on the frontend. One URL, one anon key, one service role key. One place to rotate credentials.
- **RLS on 100% of user-facing tables.** Authorization is enforced by Postgres, not application code. A bug in a FastAPI route handler cannot leak another user's legal profile because the database itself rejects the query.
- **Realtime subscriptions with zero additional infrastructure.** The profile sidebar updates live when the background updater writes new facts. No Pusher, no Socket.io, no additional WebSocket server.
- **Self-hostable escape hatch.** If Supabase's managed service becomes too expensive or unreliable, we can self-host the entire stack (Postgres + GoTrue + Storage API + Realtime) on our own infrastructure. The migration path is documented and tested by the Supabase community.
- **Local development with Supabase CLI.** `supabase start` runs the entire stack locally in Docker containers. No cloud dependency for development.

### Negative

- **Single vendor dependency.** If Supabase has an outage, all four capabilities are affected simultaneously. Separate services would degrade gracefully (auth could be down while storage still works).
- **Supabase Realtime is less mature than Pusher/Ably.** Edge cases like reconnection after network changes, message ordering guarantees, and connection limits are less battle-tested.
- **Storage is less feature-rich than S3.** No lifecycle policies, no cross-region replication, no object versioning. These are not needed now but could be needed if document storage grows.
- **Supabase is a startup.** If Supabase the company fails, we need to self-host or migrate. Mitigated by the Postgres foundation — our data is portable.

### Risks

- **Supabase outage takes down everything.** Mitigation: the backend can cache the user's profile in memory for the duration of a session, so a brief Supabase outage does not immediately break active conversations. File uploads and new user signups would fail during an outage.
- **RLS policy misconfiguration.** A permissive RLS policy is worse than no RLS because it creates a false sense of security. Mitigation: every RLS policy is tested with a dedicated test that attempts cross-user data access and verifies it is denied.
- **Realtime subscription limits.** Supabase's free tier limits concurrent realtime connections. Mitigation: only the chat page subscribes to realtime updates, and only for the current user's profile row. Connection count scales with concurrent active users, not total users.

---

## Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Credential count | 3 (URL, anon key, service role key) | Count of Supabase-related entries in `.env` |
| RLS coverage | 100% of user-facing tables | Audit: every table with user data has an RLS policy |
| Realtime subscription latency | <100ms from write to client notification | Timestamp delta: profile updater write to sidebar React re-render |
| Cross-user data access | 0 successful attempts | Integration test: User A attempts to read User B's profile, expects 403/empty |
| Local dev parity | Full stack runs locally | `supabase start` + `make dev` provides complete development environment |
