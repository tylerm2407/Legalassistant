-- Subscriptions table for Stripe subscription lifecycle tracking.
-- Stores the mapping between Supabase users and their Stripe subscription status.
-- Used by backend/payments/subscription.py and backend/payments/stripe_webhooks.py.

CREATE TABLE IF NOT EXISTS subscriptions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID        NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id      TEXT        NOT NULL,
    stripe_subscription_id  TEXT        NOT NULL,
    status                  TEXT        NOT NULL DEFAULT 'none'
                                CHECK (status IN ('none', 'active', 'canceled', 'past_due', 'trialing', 'incomplete')),
    cancel_at_period_end    BOOLEAN     NOT NULL DEFAULT FALSE,
    current_period_end      TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id
    ON subscriptions (user_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id
    ON subscriptions (stripe_subscription_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id
    ON subscriptions (stripe_customer_id);

-- Auto-update updated_at on changes
CREATE OR REPLACE TRIGGER set_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can read their own subscription
CREATE POLICY subscriptions_select_own ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Service role (backend) can manage all subscriptions
-- Note: Inserts and updates happen via the backend service role key,
-- not directly from the frontend, so no INSERT/UPDATE policies for users.
