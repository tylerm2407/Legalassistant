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

from backend.memory.profile import _get_supabase
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

    Queries the subscriptions table in Supabase for the user's record,
    then returns the current subscription state.

    Args:
        user_id: The authenticated CaseMate user ID.

    Returns:
        SubscriptionStatus with the current subscription state.
    """
    _logger.info("get_subscription_status", user_id=user_id)

    try:
        client = _get_supabase()
        result = (
            client.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        data = getattr(result, "data", None)
        if data is None:
            return SubscriptionStatus(
                user_id=user_id,
                is_active=False,
                status="none",
            )

        status = data.get("status", "none")
        period_end_raw = data.get("current_period_end")
        period_end = datetime.fromisoformat(period_end_raw) if period_end_raw else None

        return SubscriptionStatus(
            user_id=user_id,
            is_active=status == "active",
            stripe_subscription_id=data.get("stripe_subscription_id"),
            status=status,
            current_period_end=period_end,
        )

    except Exception as exc:
        _logger.error(
            "subscription_status_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return SubscriptionStatus(
            user_id=user_id,
            is_active=False,
            status="error",
        )


async def cancel_subscription(user_id: str) -> SubscriptionStatus:
    """Cancel the user's active subscription at period end.

    Sets cancel_at_period_end on the Stripe subscription so the user
    retains access until the current billing period expires. Updates
    the local Supabase record to reflect the pending cancellation.

    Args:
        user_id: The authenticated CaseMate user ID.

    Returns:
        SubscriptionStatus reflecting the updated state.

    Raises:
        ValueError: If the user has no active subscription to cancel.
        stripe.error.StripeError: If the Stripe API call fails.
    """
    _logger.info("cancel_subscription", user_id=user_id)

    current = await get_subscription_status(user_id)
    if not current.is_active or not current.stripe_subscription_id:
        raise ValueError(f"No active subscription found for user {user_id}")

    stripe.Subscription.modify(
        current.stripe_subscription_id,
        cancel_at_period_end=True,
    )

    try:
        client = _get_supabase()
        client.table("subscriptions").update({"cancel_at_period_end": True}).eq(
            "user_id", user_id
        ).execute()
    except Exception as exc:
        _logger.error(
            "subscription_cancel_db_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

    _logger.info(
        "subscription_cancel_scheduled",
        user_id=user_id,
        subscription_id=current.stripe_subscription_id,
    )

    return await get_subscription_status(user_id)
