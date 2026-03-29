"""Subscription management for CaseMate via the Stripe API.

Provides functions to create checkout sessions, query subscription status,
and cancel subscriptions. All functions interact with the Stripe API using
the STRIPE_SECRET_KEY environment variable.
"""

from __future__ import annotations

import os
from datetime import datetime

import stripe
from pydantic import BaseModel

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")


class CheckoutSessionResponse(BaseModel):
    """Response returned after creating a Stripe checkout session.

    Attributes:
        session_id: The Stripe checkout session ID.
        url: The hosted checkout page URL to redirect the user to.
    """

    session_id: str
    url: str


class SubscriptionStatus(BaseModel):
    """Current subscription status for a CaseMate user.

    Attributes:
        user_id: The CaseMate user ID.
        is_active: Whether the subscription is currently active.
        stripe_subscription_id: The Stripe subscription ID, if one exists.
        status: The Stripe subscription status string (active, canceled, past_due, etc.).
        current_period_end: When the current billing period ends, if applicable.
    """

    user_id: str
    is_active: bool
    stripe_subscription_id: str | None = None
    status: str = "none"
    current_period_end: datetime | None = None


async def create_checkout_session(
    user_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> CheckoutSessionResponse:
    """Create a Stripe checkout session for a new subscription.

    Creates a hosted checkout page where the user can enter payment details
    and subscribe to CaseMate. The user_id is stored in the session metadata
    so the webhook handler can link the Stripe customer to the CaseMate user.

    Args:
        user_id: The authenticated CaseMate user ID.
        price_id: The Stripe price ID for the subscription plan.
        success_url: URL to redirect to after successful payment.
        cancel_url: URL to redirect to if the user cancels checkout.

    Returns:
        CheckoutSessionResponse with the session ID and checkout URL.

    Raises:
        stripe.error.StripeError: If the Stripe API call fails.
    """
    _logger.info(
        "creating_checkout_session",
        user_id=user_id,
        price_id=price_id,
    )

    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user_id},
        client_reference_id=user_id,
    )

    _logger.info(
        "checkout_session_created",
        user_id=user_id,
        session_id=session.id,
    )

    return CheckoutSessionResponse(
        session_id=session.id,
        url=session.url or "",
    )


async def get_subscription_status(user_id: str) -> SubscriptionStatus:
    """Get the current subscription status for a user.

    Queries Supabase for the user's Stripe customer/subscription mapping,
    then fetches the live status from Stripe.

    Args:
        user_id: The authenticated CaseMate user ID.

    Returns:
        SubscriptionStatus with the current subscription state.
    """
    _logger.info("get_subscription_status", user_id=user_id)

    # TODO: Query Supabase for user's stripe_subscription_id
    # For now, return inactive status until the subscriptions table is connected
    _logger.warning(
        "subscription_lookup_not_connected",
        user_id=user_id,
        detail="Supabase subscriptions table not yet connected",
    )

    return SubscriptionStatus(
        user_id=user_id,
        is_active=False,
        status="none",
    )


async def cancel_subscription(user_id: str) -> SubscriptionStatus:
    """Cancel the user's active subscription.

    Cancels the subscription at period end (the user retains access until
    the current billing period expires). Does not issue a refund.

    Args:
        user_id: The authenticated CaseMate user ID.

    Returns:
        SubscriptionStatus reflecting the updated (canceled) state.

    Raises:
        ValueError: If the user has no active subscription to cancel.
        stripe.error.StripeError: If the Stripe API call fails.
    """
    _logger.info("cancel_subscription", user_id=user_id)

    # TODO: Query Supabase for user's stripe_subscription_id
    # For now, raise an error until the subscriptions table is connected
    raise NotImplementedError(
        "Subscription cancellation not yet connected. "
        "Requires subscriptions table with user-to-stripe mapping."
    )
