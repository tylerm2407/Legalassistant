"""Stripe webhook handler for processing subscription lifecycle events.

Verifies webhook signatures using the Stripe library and dispatches
events to the appropriate handler based on event type. Supported events
include checkout completion, subscription updates, and cancellations.
"""

from __future__ import annotations

import os

import stripe
from pydantic import BaseModel

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


class StripeWebhookEvent(BaseModel):
    """Parsed Stripe webhook event with typed fields.

    Attributes:
        event_id: The unique Stripe event identifier (e.g. evt_xxx).
        event_type: The Stripe event type string (e.g. checkout.session.completed).
        customer_id: The Stripe customer ID associated with the event.
        subscription_id: The Stripe subscription ID, if applicable.
    """

    event_id: str
    event_type: str
    customer_id: str
    subscription_id: str | None = None


async def handle_webhook(payload: bytes, sig_header: str) -> dict[str, str]:
    """Verify and process an incoming Stripe webhook event.

    Uses stripe.Webhook.construct_event() to verify the signature against
    STRIPE_WEBHOOK_SECRET. Dispatches to the appropriate handler based on
    the event type.

    Args:
        payload: The raw request body bytes from the webhook POST.
        sig_header: The Stripe-Signature header value for verification.

    Returns:
        A dict with status 'ok' on successful processing.

    Raises:
        ValueError: If the webhook signature verification fails.
        stripe.error.SignatureVerificationError: If the signature is invalid.
    """
    try:
        event = stripe.Webhook.construct_event(  # type: ignore[no-untyped-call]
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError as exc:
        _logger.error(
            "webhook_signature_invalid",
            error=str(exc),
        )
        raise ValueError("Invalid webhook signature") from exc

    event_type: str = event["type"]
    event_id: str = event["id"]
    data_object: dict[str, str] = event["data"]["object"]

    _logger.info(
        "webhook_received",
        event_id=event_id,
        event_type=event_type,
    )

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data_object)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(data_object)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(data_object)
    else:
        _logger.info(
            "webhook_unhandled_event",
            event_type=event_type,
            event_id=event_id,
        )

    return {"status": "ok"}


async def _handle_checkout_completed(session: dict[str, str]) -> None:
    """Process a completed checkout session.

    Activates the user's subscription in Supabase after successful payment.
    The customer and subscription IDs are extracted from the session object.

    Args:
        session: The Stripe checkout session object from the webhook payload.
    """
    customer_id = session.get("customer", "")
    subscription_id = session.get("subscription", "")

    _logger.info(
        "checkout_completed",
        customer_id=customer_id,
        subscription_id=subscription_id,
    )

    raise NotImplementedError(
        "Supabase subscription activation not yet connected. "
        "Requires subscriptions table and user-customer mapping."
    )


async def _handle_subscription_updated(subscription: dict[str, str]) -> None:
    """Process a subscription update event.

    Syncs the subscription status (active, past_due, etc.) to Supabase
    whenever Stripe reports a change.

    Args:
        subscription: The Stripe subscription object from the webhook payload.
    """
    subscription_id = subscription.get("id", "")
    status = subscription.get("status", "")
    customer_id = subscription.get("customer", "")

    _logger.info(
        "subscription_updated",
        subscription_id=subscription_id,
        status=status,
        customer_id=customer_id,
    )

    raise NotImplementedError(
        "Supabase subscription sync not yet connected. "
        "Requires subscriptions table and user-customer mapping."
    )


async def _handle_subscription_deleted(subscription: dict[str, str]) -> None:
    """Process a subscription cancellation/deletion event.

    Marks the user's subscription as cancelled in Supabase when Stripe
    confirms the subscription has ended.

    Args:
        subscription: The Stripe subscription object from the webhook payload.
    """
    subscription_id = subscription.get("id", "")
    customer_id = subscription.get("customer", "")

    _logger.info(
        "subscription_deleted",
        subscription_id=subscription_id,
        customer_id=customer_id,
    )

    raise NotImplementedError(
        "Supabase subscription cancellation not yet connected. "
        "Requires subscriptions table and user-customer mapping."
    )
