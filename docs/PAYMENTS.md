# Payments — Stripe Integration Guide

> How CaseMate handles subscriptions via Stripe Checkout, webhooks, and Supabase.

---

## Subscription Tiers

| Tier | Price | Stripe Price ID Env Var | Features |
|------|-------|------------------------|----------|
| **Free** | $0/mo | — | 5 questions/day, basic profile, no document upload |
| **Personal** | $20/mo | `STRIPE_PRICE_ID_PERSONAL` | Unlimited questions, full profile, document upload, action generators |
| **Family** | $45/mo | `STRIPE_PRICE_ID_FAMILY` | Everything in Personal for up to 4 family members |

---

## Checkout Session Flow

```
┌──────────┐     POST /api/payments/checkout     ┌──────────────┐
│ Frontend │ ──────────────────────────────────► │   Backend    │
│ (Next.js)│                                     │  (FastAPI)   │
└──────────┘                                     └──────┬───────┘
                                                        │
                                                        ▼
                                              stripe.checkout.sessions.create(
                                                mode="subscription",
                                                price=STRIPE_PRICE_ID_*,
                                                metadata={"user_id": user_id}
                                              )
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │   Stripe     │
                                                 │  Checkout    │◄── User pays here
                                                 └──────┬───────┘
                                                        │
                                              webhook POST /api/payments/webhook
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  Supabase    │
                                                 │ subscriptions│ ← status updated
                                                 └──────────────┘
```

### 1. Frontend initiates checkout

The subscription page calls `POST /api/payments/checkout` with the desired tier. The backend creates a Stripe Checkout Session and returns the session URL.

### 2. Backend creates session

**Source:** `backend/payments/subscription.py` → `create_checkout_session()`

```python
async def create_checkout_session(user_id: str, price_id: str) -> CheckoutSessionResponse:
```

- Sets `mode="subscription"` for recurring billing
- Attaches `metadata={"user_id": user_id}` so the webhook can link payment to the CaseMate user
- Configures `success_url` and `cancel_url` for post-checkout redirects
- Returns `CheckoutSessionResponse` with `checkout_url` and `session_id`

### 3. Stripe handles payment

User completes payment on Stripe's hosted checkout page. Stripe fires webhook events to our endpoint.

### 4. Webhook processes event

**Source:** `backend/payments/stripe_webhooks.py`

---

## Webhook Event Handling

The webhook endpoint at `POST /api/payments/webhook` verifies the Stripe signature and dispatches to handlers:

```python
event = stripe.Webhook.construct_event(
    payload=body,
    sig_header=stripe_signature,
    secret=STRIPE_WEBHOOK_SECRET,
)
```

### Handled Events

| Event | Handler | Action |
|-------|---------|--------|
| `checkout.session.completed` | `_handle_checkout_completed()` | Creates subscription record in Supabase, links `user_id` from metadata |
| `customer.subscription.updated` | `_handle_subscription_updated()` | Updates subscription status (e.g., past_due, active) |
| `customer.subscription.deleted` | `_handle_subscription_deleted()` | Marks subscription as canceled in Supabase |

All handlers use structured logging with `event_type` and `user_id` for debugging.

**Current status:** Webhook handlers are defined but raise `NotImplementedError` — the Supabase `subscriptions` table connection is pending.

---

## Data Models

### `CheckoutSessionResponse`

```python
class CheckoutSessionResponse(BaseModel):
    checkout_url: str    # Stripe hosted checkout URL
    session_id: str      # Stripe session ID for tracking
```

### `SubscriptionStatus`

```python
class SubscriptionStatus(BaseModel):
    is_active: bool           # Whether user has active subscription
    tier: str | None          # "personal" | "family" | None
    stripe_subscription_id: str | None
    current_period_end: str | None   # ISO timestamp
    cancel_at_period_end: bool       # True if user canceled but period not over
```

---

## Subscription Management

### Get status

```python
async def get_subscription_status(user_id: str) -> SubscriptionStatus:
```

Queries Supabase for the user's Stripe subscription mapping, then checks Stripe for current status.

### Cancel subscription

```python
async def cancel_subscription(user_id: str) -> SubscriptionStatus:
```

Sets `cancel_at_period_end=True` on the Stripe subscription. The user retains access until the current billing period ends. Does **not** immediately revoke access.

---

## API Endpoints

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|------------|-------------|
| `POST` | `/api/payments/checkout` | JWT | 5/min | Create checkout session |
| `POST` | `/api/payments/webhook` | Stripe signature | — | Receive Stripe events |
| `GET` | `/api/payments/status` | JWT | 10/min | Get subscription status |
| `POST` | `/api/payments/cancel` | JWT | 5/min | Cancel at period end |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe API secret key (starts with `sk_test_` or `sk_live_`) |
| `STRIPE_WEBHOOK_SECRET` | Yes | Webhook endpoint signing secret (starts with `whsec_`) |
| `STRIPE_PRICE_ID_PERSONAL` | Yes | Stripe Price ID for the $20/mo Personal tier |
| `STRIPE_PRICE_ID_FAMILY` | Yes | Stripe Price ID for the $45/mo Family tier |

---

## Test Mode Setup

1. Use Stripe test keys (`sk_test_...`) in `.env`
2. Install the Stripe CLI: `stripe login`
3. Forward webhook events locally:
   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook
   ```
4. Copy the webhook signing secret from the CLI output into `STRIPE_WEBHOOK_SECRET`
5. Test a checkout flow — use card `4242 4242 4242 4242` with any future expiry

---

## Related

- [API.md](API.md) — Full API reference including payment endpoints
- [SECURITY.md](SECURITY.md) — How secrets are managed
- [DATABASE.md](DATABASE.md) — Supabase schema (subscriptions table pending)
