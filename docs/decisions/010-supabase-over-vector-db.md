# ADR 010 — Supabase Postgres over vector database for profiles

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

User legal profiles are stored as structured Pydantic models in Supabase Postgres — not as embeddings in a vector database. The `LegalProfile` model in `backend/models/legal_profile.py` defines typed fields (state, housing_situation, employment_type, family_status, active_issues, legal_facts) that are serialized to JSON columns in the `user_profiles` table. Profile CRUD in `backend/memory/profile.py` uses the Supabase Python client with direct table queries.

---

## Context

The core product decision (ADR 001) requires injecting the user's full legal context into every Claude API call. The question was how to store and retrieve that context.

The AI ecosystem defaults to vector databases and RAG for anything involving LLMs. But the user's legal profile is not unstructured text that needs semantic search. It is a known, finite set of fields: which state they live in, their housing situation, their employment type, their active legal disputes, and specific facts extracted from conversations. These are structured data with well-defined types.

We evaluated three storage strategies:

1. **Supabase Postgres** — Structured table with typed columns, JSON arrays for issues and facts
2. **Vector DB (Pinecone, Weaviate, pgvector)** — Embed profile text and retrieve via similarity search
3. **Hybrid** — Structured profile in Postgres + vector store for conversation history retrieval

---

## The implementation

`backend/models/legal_profile.py` defines `LegalProfile` as a Pydantic BaseModel with 11 typed fields. Key fields include `state` (str, two-letter code), `active_issues` (list[LegalIssue]), and `legal_facts` (list[str]). The `to_context_string()` method serializes the profile to a concise JSON string for injection into the system prompt.

`backend/memory/profile.py` provides `get_profile()` and `update_profile()` functions using the Supabase client. Profiles are fetched by `user_id` with `.eq("user_id", user_id).maybe_single()` and upserted with `.upsert(data, on_conflict="user_id")`. The Supabase client is a singleton created from `SUPABASE_URL` and `SUPABASE_KEY` environment variables.

The `LegalProfile.model_validate()` call on the Supabase response ensures that data coming out of the database is always validated against the Pydantic schema before being used in prompt assembly.

---

## Alternatives considered

**Vector database with semantic retrieval**
Rejected. The profile is 11 fields, not a corpus of documents. Embedding a user's state code or employment type adds no value — these are exact-match lookups, not semantic similarity problems. A vector DB would add infrastructure complexity (separate service, embedding model, index management) without improving retrieval quality for structured profile data.

**pgvector extension in Supabase**
Considered as a middle ground. Supabase supports pgvector natively. However, the same argument applies — profile fields are structured, not semantic. pgvector could be useful later for searching across conversation history, but that is a separate retrieval problem from profile injection.

**Hybrid: Postgres for profile + vector for conversations**
Deferred. The current profile auto-updater (`backend/memory/updater.py`) extracts key facts from conversations and writes them as structured strings into `legal_facts[]`. This avoids needing to search raw conversation history at query time. If conversation-level retrieval becomes necessary (e.g., "what did I say about my lease last month?"), a vector store for conversation history could be added without changing the profile storage layer.

---

## Consequences

**Positive:**
- No additional infrastructure — Supabase is already the auth and storage layer
- Profile reads are single-row lookups by primary key — sub-10ms latency
- Pydantic validation on every read guarantees type safety before prompt injection
- Profile is directly displayable in the UI sidebar without transformation
- RLS policies in Supabase protect profile data at the database level

**Negative:**
- Cannot do semantic search over profiles (e.g., "find users with similar situations")
- Legal facts are stored as flat strings — no structured metadata per fact
- If the number of legal_facts grows very large (100+), the full list is injected into every prompt, consuming tokens
- No built-in relevance ranking for which facts to include in the prompt

---

## Status

Accepted. Structured Postgres storage is the correct choice for the profile injection pattern. Vector search may be added later for conversation history retrieval, but the profile itself remains in typed Postgres columns.
