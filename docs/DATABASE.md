# Database Schema

CaseMate uses Supabase (PostgreSQL) with Row Level Security (RLS) on all tables. Migrations live in `supabase/migrations/`.

See `ARCHITECTURE.md` for how these tables fit into the overall system.

## Migrations

| File | Tables |
|------|--------|
| `001_user_profiles_rls.sql` | `user_profiles` |
| `002_conversations_deadlines_workflows_attorneys.sql` | `conversations`, `deadlines`, `workflow_instances`, `attorneys` |

### Migration Versioning Strategy

Migrations are numbered sequentially (`001`, `002`, ...) and are applied in order via `supabase db push` or the Supabase dashboard. Each migration is idempotent — it uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` where possible.

**Adding a new migration:**

1. Create a new file: `supabase/migrations/003_description.sql`
2. Write the SQL (CREATE TABLE, ALTER TABLE, CREATE INDEX, etc.)
3. Test locally: `supabase db reset` applies all migrations from scratch
4. Deploy: `supabase db push` applies pending migrations to the remote project

**Modifying an existing table:**

Never edit a deployed migration file. Instead, create a new migration with `ALTER TABLE` statements:

```sql
-- 003_add_subscription_fields.sql
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS subscription_tier TEXT DEFAULT 'free';
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
```

## Tables

### user_profiles

The most important table. Stores each user's persistent legal context, injected into every Claude API call via `backend/memory/injector.py`.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `user_id` | `UUID` (PK) | — | FK to `auth.users(id)`, CASCADE delete |
| `display_name` | `TEXT` | `''` | User's first name |
| `state` | `TEXT` | `''` | Two-letter state code (e.g. "MA") |
| `housing_situation` | `TEXT` | `''` | Free-text housing description |
| `employment_type` | `TEXT` | `''` | Employment classification |
| `family_status` | `TEXT` | `''` | Family and dependent info |
| `active_issues` | `JSONB` | `'[]'` | Array of `LegalIssue` objects (see below) |
| `legal_facts` | `JSONB` | `'[]'` | Array of strings extracted from conversations |
| `documents` | `JSONB` | `'[]'` | Array of uploaded document references |
| `member_since` | `TIMESTAMPTZ` | `now()` | When the user joined |
| `conversation_count` | `INTEGER` | `0` | Total conversations held |
| `created_at` | `TIMESTAMPTZ` | `now()` | Row creation time |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**JSONB structures:**

`active_issues` stores an array of objects matching the `LegalIssue` Pydantic model in `backend/models/legal_profile.py`:

```json
[
  {
    "issue_type": "landlord_tenant",
    "summary": "Landlord has not returned $2,400 security deposit",
    "status": "open",
    "started_at": "2026-02-01T00:00:00",
    "updated_at": "2026-03-15T00:00:00",
    "notes": ["Move-out date was January 15, 2026"]
  }
]
```

`legal_facts` stores an array of plain strings:

```json
["Landlord did not perform move-in inspection", "Pre-existing water damage documented"]
```

`documents` stores an array of document reference objects:

```json
[
  {
    "filename": "lease_agreement.pdf",
    "storage_path": "documents/user-id/lease_agreement.pdf",
    "uploaded_at": "2026-01-20T10:30:00",
    "extracted_facts": ["Lease term: 12 months", "Monthly rent: $1,600"]
  }
]
```

### conversations

Stores multi-turn chat histories. Messages are stored as a JSONB array rather than individual rows.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | Conversation ID |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `messages` | `JSONB` | `'[]'` | Array of message objects (`role`, `content`, `legal_area`, `timestamp`) |
| `legal_area` | `TEXT` | `NULL` | Primary legal domain for this conversation |
| `created_at` | `TIMESTAMPTZ` | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**Indexes:** `(user_id)`, `(user_id, updated_at DESC)` for list queries.

**Message JSONB structure:**

```json
[
  {
    "role": "user",
    "content": "My landlord is saying I owe $800 for the bathroom tiles",
    "timestamp": "2026-03-15T14:30:00Z"
  },
  {
    "role": "assistant",
    "content": "Based on your situation in Massachusetts...",
    "legal_area": "landlord_tenant",
    "timestamp": "2026-03-15T14:30:05Z"
  }
]
```

### deadlines

Legal deadlines detected from conversations or created manually.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | — |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `title` | `TEXT` | — | Deadline description |
| `date` | `TEXT` | — | ISO date string (e.g. `2026-04-15`) |
| `legal_area` | `TEXT` | `NULL` | — |
| `source_conversation_id` | `UUID` | `NULL` | FK to `conversations(id)`, SET NULL on delete |
| `status` | `TEXT` | `'active'` | CHECK: `active`, `completed`, `dismissed`, `expired` |
| `notes` | `TEXT` | `''` | — |
| `created_at` | `TIMESTAMPTZ` | `now()` | — |

**Indexes:** `(user_id)`, `(user_id, status)`, `(user_id, date ASC)`, `(source_conversation_id)`.

### workflow_instances

Tracks user progress through guided legal workflows.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `UUID` (PK) | — | — |
| `user_id` | `UUID` | — | FK to `auth.users(id)`, CASCADE delete |
| `template_id` | `TEXT` | — | Reference to workflow template definition |
| `title` | `TEXT` | — | Workflow display name |
| `domain` | `TEXT` | — | Legal domain |
| `steps` | `JSONB` | `'[]'` | Array of step objects with status |
| `current_step` | `INTEGER` | `0` | Index of the current step |
| `status` | `TEXT` | `'in_progress'` | CHECK: `not_started`, `in_progress`, `completed`, `skipped` |
| `started_at` | `TIMESTAMPTZ` | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | `now()` | Auto-updated via trigger |

**Indexes:** `(user_id)`, `(user_id, updated_at DESC)`, `(template_id)`.

**Steps JSONB structure:**

```json
[
  {
    "title": "Gather evidence",
    "description": "Collect all relevant documents and photos",
    "guidance": "Take photos of the damage, save all text messages...",
    "status": "completed",
    "completed_at": "2026-03-10T09:00:00Z"
  },
  {
    "title": "Send demand letter",
    "description": "Write and send a formal demand to your landlord",
    "guidance": "Use CaseMate's letter generator to create a demand letter...",
    "status": "in_progress",
    "completed_at": null
  }
]
```

### attorneys

Shared directory of attorney referrals. No `user_id` — this is admin-managed, not user-owned.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | `TEXT` (PK) | — | Unique attorney identifier |
| `name` | `TEXT` | — | Attorney name |
| `state` | `TEXT` | — | Two-letter state code (uppercase) |
| `specializations` | `JSONB` | `'[]'` | Array of legal area strings |
| `rating` | `NUMERIC(3,2)` | `0.00` | CHECK: 0-5 |
| `cost_range` | `TEXT` | `''` | e.g. "$200-400/hr" |
| `phone` | `TEXT` | `''` | — |
| `email` | `TEXT` | `''` | — |
| `website` | `TEXT` | `''` | — |
| `accepts_free_consultations` | `BOOLEAN` | `FALSE` | — |
| `bio` | `TEXT` | `''` | — |

**Indexes:** `(state)`, `(state, rating DESC)`, GIN on `specializations` for containment queries.

## Row Level Security

All user-owned tables (`user_profiles`, `conversations`, `deadlines`, `workflow_instances`) have full CRUD RLS policies scoped to `auth.uid() = user_id`. Users can only read, insert, update, and delete their own rows.

The `attorneys` table uses public read access (`USING (true)`) with no INSERT/UPDATE/DELETE policies for application users. Attorney records are managed by administrators directly in Supabase.

### RLS Policy SQL Examples

```sql
-- user_profiles: Users can only access their own profile
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own profile"
    ON user_profiles FOR DELETE
    USING (auth.uid() = user_id);
```

```sql
-- conversations: Same pattern
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own conversations"
    ON conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
    ON conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
    ON conversations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
    ON conversations FOR DELETE
    USING (auth.uid() = user_id);
```

```sql
-- attorneys: Public read, admin-only write
ALTER TABLE attorneys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view attorneys"
    ON attorneys FOR SELECT
    USING (true);
-- No INSERT/UPDATE/DELETE policies = only service_role can write
```

### Defense in Depth

RLS provides database-level access control. The application code also checks ownership (e.g., `conversation_store.py` includes `user_id` in all queries). This means:

1. **Application bug** where user_id isn't checked → RLS still blocks cross-user access
2. **RLS misconfiguration** → Application code still filters by user_id
3. **Both must fail** for a data leak to occur

## Triggers

An `update_updated_at_column()` trigger function (created in migration 001) automatically sets `updated_at = now()` before any UPDATE on `user_profiles`, `conversations`, and `workflow_instances`.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Index Strategy

### Query Patterns and Their Indexes

| Query Pattern | Index Used | Example |
|---------------|-----------|---------|
| Get user's profile | PK (`user_id`) | `SELECT * FROM user_profiles WHERE user_id = $1` |
| List user's conversations | `(user_id, updated_at DESC)` | `SELECT * FROM conversations WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 50` |
| List user's active deadlines | `(user_id, status)` | `SELECT * FROM deadlines WHERE user_id = $1 AND status = 'active'` |
| List user's deadlines by date | `(user_id, date ASC)` | `SELECT * FROM deadlines WHERE user_id = $1 ORDER BY date ASC` |
| Find attorneys by state | `(state)` | `SELECT * FROM attorneys WHERE state = $1` |
| Find top attorneys by state | `(state, rating DESC)` | `SELECT * FROM attorneys WHERE state = $1 ORDER BY rating DESC LIMIT 5` |
| Find attorneys by specialization | GIN `(specializations)` | `SELECT * FROM attorneys WHERE specializations @> '["landlord_tenant"]'` |
| Link deadline to conversation | `(source_conversation_id)` | `SELECT * FROM deadlines WHERE source_conversation_id = $1` |

### GIN Index on `specializations`

The attorneys table uses a GIN (Generalized Inverted Index) on the `specializations` JSONB column. This enables efficient containment queries:

```sql
-- Find all attorneys who specialize in landlord_tenant law
SELECT * FROM attorneys WHERE specializations @> '["landlord_tenant"]';
```

Without the GIN index, this query would require a full table scan.

## How to Add a New Table

1. **Create a migration file:** `supabase/migrations/NNN_description.sql`

2. **Define the table:**
   ```sql
   CREATE TABLE IF NOT EXISTS new_table (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
       -- ... columns ...
       created_at TIMESTAMPTZ DEFAULT now(),
       updated_at TIMESTAMPTZ DEFAULT now()
   );
   ```

3. **Add indexes** for expected query patterns:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_new_table_user ON new_table(user_id);
   ```

4. **Enable RLS:**
   ```sql
   ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
   CREATE POLICY "Users can view own records" ON new_table FOR SELECT USING (auth.uid() = user_id);
   -- ... INSERT, UPDATE, DELETE policies ...
   ```

5. **Add updated_at trigger** (if the table has an `updated_at` column):
   ```sql
   CREATE TRIGGER update_new_table_updated_at
       BEFORE UPDATE ON new_table
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column();
   ```

6. **Create the Pydantic model** in `backend/models/`

7. **Test locally:** `supabase db reset` to apply all migrations

8. **Deploy:** `supabase db push`

## Supabase Dashboard vs. Migration Files

| Task | Dashboard | Migration File |
|------|-----------|---------------|
| Explore data | Yes (Table Editor) | No |
| Quick schema prototyping | Yes | No |
| Production schema changes | No | Yes (always) |
| RLS policy changes | No | Yes (always) |
| Seed data (attorneys) | Yes (for one-off) | Yes (for reproducible) |
| Index changes | No | Yes (always) |

**Rule:** Any schema change that affects production must be in a migration file. The dashboard is for exploration and debugging only.

---

## Related

- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — How profile data is read and written
- [SECURITY.md](SECURITY.md) — RLS and auth strategy
- [MODELS.md](MODELS.md) — Pydantic models that map to these tables
- [DEPLOYMENT.md](DEPLOYMENT.md) — How migrations are applied in CI/CD
- [EXTENDING.md](EXTENDING.md) — How to add new tables
