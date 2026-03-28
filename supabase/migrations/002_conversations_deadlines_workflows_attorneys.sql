-- Migration 002: conversations, deadlines, workflow_instances, attorneys
-- All user-owned tables use per-user RLS (user_id = (SELECT auth.uid())).
-- attorneys uses public read / admin-only write (no user_id column).
-- update_updated_at_column() trigger function already exists from migration 001.

-- ============================================================
-- conversations
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id          UUID        PRIMARY KEY,
    user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    messages    JSONB       NOT NULL DEFAULT '[]'::jsonb,
    legal_area  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);

-- Supports list_conversations ORDER BY updated_at DESC filtered by user_id
CREATE INDEX IF NOT EXISTS idx_conversations_user_id_updated_at
    ON conversations(user_id, updated_at DESC);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own conversations"
    ON conversations
    FOR SELECT
    USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can insert own conversations"
    ON conversations
    FOR INSERT
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own conversations"
    ON conversations
    FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own conversations"
    ON conversations
    FOR DELETE
    USING ((SELECT auth.uid()) = user_id);

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- deadlines
-- ============================================================

CREATE TABLE IF NOT EXISTS deadlines (
    id                      UUID        PRIMARY KEY,
    user_id                 UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title                   TEXT        NOT NULL,
    date                    TEXT        NOT NULL,   -- ISO date string, e.g. '2026-04-15'
    legal_area              TEXT,
    source_conversation_id  UUID        REFERENCES conversations(id) ON DELETE SET NULL,
    status                  TEXT        NOT NULL DEFAULT 'active'
                                CHECK (status IN ('active', 'completed', 'dismissed', 'expired')),
    notes                   TEXT        NOT NULL DEFAULT '',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fast per-user lookups and status-filtered list queries
CREATE INDEX IF NOT EXISTS idx_deadlines_user_id
    ON deadlines(user_id);

CREATE INDEX IF NOT EXISTS idx_deadlines_user_id_status
    ON deadlines(user_id, status);

-- Supports ORDER BY date ASC used in list_deadlines
CREATE INDEX IF NOT EXISTS idx_deadlines_user_id_date
    ON deadlines(user_id, date ASC);

-- RLS policy column index
CREATE INDEX IF NOT EXISTS idx_deadlines_source_conversation_id
    ON deadlines(source_conversation_id);

ALTER TABLE deadlines ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own deadlines"
    ON deadlines
    FOR SELECT
    USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can insert own deadlines"
    ON deadlines
    FOR INSERT
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own deadlines"
    ON deadlines
    FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own deadlines"
    ON deadlines
    FOR DELETE
    USING ((SELECT auth.uid()) = user_id);

-- ============================================================
-- workflow_instances
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_instances (
    id           UUID        PRIMARY KEY,
    user_id      UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id  TEXT        NOT NULL,
    title        TEXT        NOT NULL,
    domain       TEXT        NOT NULL,
    steps        JSONB       NOT NULL DEFAULT '[]'::jsonb,
    current_step INTEGER     NOT NULL DEFAULT 0,
    status       TEXT        NOT NULL DEFAULT 'in_progress'
                     CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped')),
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Per-user lookups and list ordering
CREATE INDEX IF NOT EXISTS idx_workflow_instances_user_id
    ON workflow_instances(user_id);

CREATE INDEX IF NOT EXISTS idx_workflow_instances_user_id_updated_at
    ON workflow_instances(user_id, updated_at DESC);

-- Allows filtering instances by template
CREATE INDEX IF NOT EXISTS idx_workflow_instances_template_id
    ON workflow_instances(template_id);

ALTER TABLE workflow_instances ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own workflow instances"
    ON workflow_instances
    FOR SELECT
    USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can insert own workflow instances"
    ON workflow_instances
    FOR INSERT
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own workflow instances"
    ON workflow_instances
    FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own workflow instances"
    ON workflow_instances
    FOR DELETE
    USING ((SELECT auth.uid()) = user_id);

CREATE TRIGGER update_workflow_instances_updated_at
    BEFORE UPDATE ON workflow_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- attorneys
-- ============================================================
-- No user_id — this is a shared directory populated by admins.
-- RLS: public read, no direct write access for application users.

CREATE TABLE IF NOT EXISTS attorneys (
    id                          TEXT        PRIMARY KEY,
    name                        TEXT        NOT NULL,
    state                       TEXT        NOT NULL,    -- two-letter state code, stored uppercase
    specializations             JSONB       NOT NULL DEFAULT '[]'::jsonb,
    rating                      NUMERIC(3,2) NOT NULL DEFAULT 0.00
                                    CHECK (rating >= 0 AND rating <= 5),
    cost_range                  TEXT        NOT NULL DEFAULT '',
    phone                       TEXT        NOT NULL DEFAULT '',
    email                       TEXT        NOT NULL DEFAULT '',
    website                     TEXT        NOT NULL DEFAULT '',
    accepts_free_consultations  BOOLEAN     NOT NULL DEFAULT FALSE,
    bio                         TEXT        NOT NULL DEFAULT ''
);

-- Primary search pattern: filter by state, order by rating DESC
CREATE INDEX IF NOT EXISTS idx_attorneys_state
    ON attorneys(state);

CREATE INDEX IF NOT EXISTS idx_attorneys_state_rating
    ON attorneys(state, rating DESC);

-- GIN index for specializations JSONB containment queries (.contains())
CREATE INDEX IF NOT EXISTS idx_attorneys_specializations
    ON attorneys USING GIN (specializations);

ALTER TABLE attorneys ENABLE ROW LEVEL SECURITY;

-- Public read: anyone (authenticated or not) can search attorneys
CREATE POLICY "Anyone can read attorneys"
    ON attorneys
    FOR SELECT
    USING (true);

-- No INSERT / UPDATE / DELETE policies for application users.
-- Attorney records are managed directly in Supabase by administrators.
