"""Tests for the CaseMate Stripe payment integration module.

Covers webhook signature verification, checkout session creation,
subscription status retrieval, and subscription cancellation.
All Stripe API calls are mocked to avoid external dependencies.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import stripe

from backend.payments.stripe_webhooks import handle_webhook
from backend.payments.subscription import (
    CheckoutSessionResponse,
    SubscriptionStatus,
    cancel_subscription,
    create_checkout_session,
    get_subscription_status,
)


class TestStripeWebhooks:
    """Tests for Stripe webhook handling and signature verification."""

    @pytest.mark.asyncio
    async def test_webhook_valid_checkout_completed(self) -> None:
        """Webhook processes checkout.session.completed with valid signature."""
        mock_event = {
            "id": "evt_test_123",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test_456",
                    "subscription": "sub_test_789",
                }
            },
        }

        with patch("backend.payments.stripe_webhooks.stripe.Webhook.construct_event", return_value=mock_event):
            # The handler will raise NotImplementedError because Supabase is not connected
            with pytest.raises(NotImplementedError, match="Supabase subscription activation"):
                await handle_webhook(b"payload", "sig_header")

    @pytest.mark.asyncio
    async def test_webhook_valid_subscription_updated(self) -> None:
        """Webhook processes customer.subscription.updated with valid signature."""
        mock_event = {
            "id": "evt_test_456",
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test_789",
                    "status": "active",
                    "customer": "cus_test_456",
                }
            },
        }

        with patch("backend.payments.stripe_webhooks.stripe.Webhook.construct_event", return_value=mock_event):
            with pytest.raises(NotImplementedError, match="Supabase subscription sync"):
                await handle_webhook(b"payload", "sig_header")

    @pytest.mark.asyncio
    async def test_webhook_valid_subscription_deleted(self) -> None:
        """Webhook processes customer.subscription.deleted with valid signature."""
        mock_event = {
            "id": "evt_test_789",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test_789",
                    "customer": "cus_test_456",
                }
            },
        }

        with patch("backend.payments.stripe_webhooks.stripe.Webhook.construct_event", return_value=mock_event):
            with pytest.raises(NotImplementedError, match="Supabase subscription cancellation"):
                await handle_webhook(b"payload", "sig_header")

    @pytest.mark.asyncio
    async def test_webhook_unhandled_event_returns_ok(self) -> None:
        """Webhook returns ok for unhandled event types without raising."""
        mock_event = {
            "id": "evt_test_unhandled",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "inv_test_123",
                }
            },
        }

        with patch("backend.payments.stripe_webhooks.stripe.Webhook.construct_event", return_value=mock_event):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_webhook_invalid_signature_raises_error(self) -> None:
        """Webhook raises ValueError when signature verification fails."""
        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            side_effect=stripe.error.SignatureVerificationError("bad sig", "sig_header"),
        ):
            with pytest.raises(ValueError, match="Invalid webhook signature"):
                await handle_webhook(b"payload", "bad_signature")


class TestCheckoutSession:
    """Tests for Stripe checkout session creation."""

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(self) -> None:
        """Creates a checkout session and returns session ID and URL."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_session_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_session_123"

        with patch("backend.payments.subscription.stripe.checkout.Session.create", return_value=mock_session):
            result = await create_checkout_session(
                user_id="user_123",
                price_id="price_abc",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert isinstance(result, CheckoutSessionResponse)
            assert result.session_id == "cs_test_session_123"
            assert result.url == "https://checkout.stripe.com/pay/cs_test_session_123"

    @pytest.mark.asyncio
    async def test_create_checkout_session_passes_metadata(self) -> None:
        """Checkout session includes user_id in metadata for webhook linking."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_meta"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_meta"

        with patch("backend.payments.subscription.stripe.checkout.Session.create", return_value=mock_session) as mock_create:
            await create_checkout_session(
                user_id="user_meta_test",
                price_id="price_xyz",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["metadata"] == {"user_id": "user_meta_test"}
            assert call_kwargs["client_reference_id"] == "user_meta_test"


class TestSubscriptionStatus:
    """Tests for subscription status retrieval."""

    @pytest.mark.asyncio
    async def test_get_subscription_status_returns_inactive_default(self) -> None:
        """Returns inactive status when Supabase is not yet connected."""
        result = await get_subscription_status("user_123")

        assert isinstance(result, SubscriptionStatus)
        assert result.user_id == "user_123"
        assert result.is_active is False
        assert result.status == "none"
        assert result.stripe_subscription_id is None


class TestSubscriptionCancellation:
    """Tests for subscription cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_subscription_raises_not_implemented(self) -> None:
        """Cancellation raises NotImplementedError until Supabase is connected."""
        with pytest.raises(NotImplementedError, match="Subscription cancellation not yet connected"):
            await cancel_subscription("user_123")
