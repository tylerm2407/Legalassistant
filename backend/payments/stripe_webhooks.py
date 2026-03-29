"""Stripe webhook handler for processing subscription lifecycle events.

Verifies webhook signatures using the Stripe library and dispatches
events to the appropriate handler based on event type. Supported events
include checkout completion, subscription updates, cancellations,
invoice payments, and payment failures.
"""

from __future__ import annotations

import os

import stripe
from pydantic import BaseModel

from backend.memory.profile import _get_supabase
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
    data_object: dict[str, object] = event["data"]["object"]

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
    elif event_type == "invoice.paid":
        await _handle_invoice_paid(data_object)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_payment_failed(data_object)
    else:
        _logger.info(
            "webhook_unhandled_event",
            event_type=event_type,
            event_id=event_id,
        )

    return {"status": "ok"}


async def _handle_checkout_completed(session: dict[str, object]) -> None:
    """Process a completed checkout session.

    Activates the user's subscription in Supabase after successful payment.
    Extracts user_id from session metadata (set during checkout creation),
    then upserts the subscription record linking Stripe IDs to the CaseMate user.

    Args:
        session: The Stripe checkout session object from the webhook payload.
    """
    customer_id = session.get("customer", "")
    subscription_id = session.get("subscription", "")
    raw_metadata: object = session.get("metadata", {})
    metadata: dict[str, object] = raw_metadata if isinstance(raw_metadata, dict) else {}
    user_id = metadata.get("user_id", "") if isinstance(metadata, dict) else ""

    _logger.info(
        "checkout_completed",
        customer_id=customer_id,
        subscription_id=subscription_id,
        user_id=user_id,
    )

    if not user_id:
        _logger.error("checkout_missing_user_id", customer_id=customer_id)
        return

    try:
        client = _get_supabase()
        upsert_data: dict[str, str | bool] = {
            "user_id": str(user_id),
            "stripe_customer_id": str(customer_id),
            "stripe_subscription_id": str(subscription_id),
            "status": "active",
            "cancel_at_period_end": False,
        }
        client.table("subscriptions").upsert(
            upsert_data,
            on_conflict="user_id",
        ).execute()

        _logger.info(
            "subscription_activated",
            user_id=user_id,
            subscription_id=subscription_id,
        )
    except Exception as exc:
        _logger.error(
            "subscription_activation_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


async def _handle_subscription_updated(subscription: dict[str, object]) -> None:
    """Process a subscription update event.

    Syncs the subscription status, current_period_end, and cancel_at_period_end
    fields to Supabase whenever Stripe reports a change.

    Args:
        subscription: The Stripe subscription object from the webhook payload.
    """
    subscription_id = subscription.get("id", "")
    status = subscription.get("status", "")
    customer_id = subscription.get("customer", "")
    current_period_end = subscription.get("current_period_end", "")
    cancel_at_period_end = subscription.get("cancel_at_period_end", False)

    _logger.info(
        "subscription_updated",
        subscription_id=subscription_id,
        status=status,
        customer_id=customer_id,
    )

    try:
        client = _get_supabase()
        update_data: dict[str, object] = {
            "status": status,
            "cancel_at_period_end": bool(cancel_at_period_end),
        }
        if current_period_end:
            update_data["current_period_end"] = current_period_end

        client.table("subscriptions").update(
            update_data  # type: ignore[arg-type]
        ).eq("stripe_subscription_id", subscription_id).execute()

        _logger.info(
            "subscription_synced",
            subscription_id=subscription_id,
            status=status,
        )
    except Exception as exc:
        _logger.error(
            "subscription_sync_error",
            subscription_id=subscription_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


async def _handle_subscription_deleted(subscription: dict[str, object]) -> None:
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

    try:
        client = _get_supabase()
        client.table("subscriptions").update({"status": "canceled"}).eq(
            "stripe_subscription_id", subscription_id
        ).execute()

        _logger.info(
            "subscription_canceled",
            subscription_id=subscription_id,
        )
    except Exception as exc:
        _logger.error(
            "subscription_cancel_error",
            subscription_id=subscription_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


async def _handle_invoice_paid(invoice: dict[str, object]) -> None:
    """Process a successful invoice payment event.

    Updates the subscription status to 'active' in Supabase and syncs
    the current_period_end from the invoice line items when available.
    This handles reactivation after failed payments and regular renewals.

    Args:
        invoice: The Stripe invoice object from the webhook payload.
    """
    subscription_id = str(invoice.get("subscription", ""))
    customer_id = str(invoice.get("customer", ""))

    _logger.info(
        "invoice_paid",
        subscription_id=subscription_id,
        customer_id=customer_id,
    )

    if not subscription_id:
        _logger.info("invoice_paid_no_subscription", customer_id=customer_id)
        return

    try:
        client = _get_supabase()
        update_data: dict[str, object] = {
            "status": "active",
        }

        # Extract current_period_end from invoice line items if available
        lines: object = invoice.get("lines", {})
        if isinstance(lines, dict):
            line_data: object = lines.get("data", [])
            if isinstance(line_data, list) and len(line_data) > 0:
                first_line: object = line_data[0]
                if isinstance(first_line, dict):
                    period: object = first_line.get("period", {})
                    if isinstance(period, dict):
                        period_end: object = period.get("end")
                        if period_end:
                            update_data["current_period_end"] = period_end

        client.table("subscriptions").update(
            update_data  # type: ignore[arg-type]
        ).eq("stripe_subscription_id", subscription_id).execute()

        _logger.info(
            "invoice_paid_subscription_activated",
            subscription_id=subscription_id,
        )
    except Exception as exc:
        _logger.error(
            "invoice_paid_update_error",
            subscription_id=subscription_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


async def _handle_invoice_payment_failed(invoice: dict[str, object]) -> None:
    """Process a failed invoice payment event.

    Marks the subscription as 'past_due' in Supabase when a payment
    attempt fails. This triggers visual indicators in the UI prompting
    the user to update their payment method.

    Args:
        invoice: The Stripe invoice object from the webhook payload.
    """
    subscription_id = str(invoice.get("subscription", ""))
    customer_id = str(invoice.get("customer", ""))

    _logger.info(
        "invoice_payment_failed",
        subscription_id=subscription_id,
        customer_id=customer_id,
    )

    if not subscription_id:
        _logger.info("invoice_payment_failed_no_subscription", customer_id=customer_id)
        return

    try:
        client = _get_supabase()
        client.table("subscriptions").update({"status": "past_due"}).eq(
            "stripe_subscription_id", subscription_id
        ).execute()

        _logger.info(
            "invoice_payment_failed_marked_past_due",
            subscription_id=subscription_id,
            customer_id=customer_id,
        )
    except Exception as exc:
        _logger.error(
            "invoice_payment_failed_update_error",
            subscription_id=subscription_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
