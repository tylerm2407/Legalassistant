"""Tests for the CaseMate Stripe payment integration module.

Covers webhook signature verification, checkout session creation,
subscription status retrieval, and subscription cancellation.
All Stripe API calls and Supabase operations are mocked to avoid external dependencies.
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


def _mock_supabase_client() -> MagicMock:
    """Create a mock Supabase client with chained query methods."""
    client = MagicMock()
    client.table.return_value = client
    client.select.return_value = client
    client.eq.return_value = client
    client.maybe_single.return_value = client
    client.upsert.return_value = client
    client.update.return_value = client
    client.execute.return_value = MagicMock(data=None)
    return client


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
                    "metadata": {"user_id": "user_abc"},
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            mock_client.table.assert_called_with("subscriptions")

    @pytest.mark.asyncio
    async def test_webhook_checkout_missing_user_id(self) -> None:
        """Webhook handles checkout without user_id in metadata gracefully."""
        mock_event = {
            "id": "evt_test_no_user",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test_456",
                    "subscription": "sub_test_789",
                }
            },
        }

        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}

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
                    "current_period_end": "2026-04-29T00:00:00Z",
                    "cancel_at_period_end": False,
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            mock_client.table.assert_called_with("subscriptions")

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

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}

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

        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
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

        with patch(
            "backend.payments.subscription.stripe.checkout.Session.create",
            return_value=mock_session,
        ):
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

        with patch(
            "backend.payments.subscription.stripe.checkout.Session.create",
            return_value=mock_session,
        ) as mock_create:
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
    async def test_get_subscription_status_no_subscription(self) -> None:
        """Returns inactive status when no subscription exists in Supabase."""
        mock_client = _mock_supabase_client()
        mock_client.execute.return_value = MagicMock(data=None)

        with patch(
            "backend.payments.subscription._get_supabase",
            return_value=mock_client,
        ):
            result = await get_subscription_status("user_123")

            assert isinstance(result, SubscriptionStatus)
            assert result.user_id == "user_123"
            assert result.is_active is False
            assert result.status == "none"

    @pytest.mark.asyncio
    async def test_get_subscription_status_active(self) -> None:
        """Returns active status when an active subscription exists."""
        mock_client = _mock_supabase_client()
        mock_client.execute.return_value = MagicMock(
            data={
                "status": "active",
                "stripe_subscription_id": "sub_abc",
                "current_period_end": "2026-04-29T00:00:00",
            }
        )

        with patch(
            "backend.payments.subscription._get_supabase",
            return_value=mock_client,
        ):
            result = await get_subscription_status("user_123")

            assert result.is_active is True
            assert result.status == "active"
            assert result.stripe_subscription_id == "sub_abc"

    @pytest.mark.asyncio
    async def test_get_subscription_status_error_returns_error(self) -> None:
        """Returns error status when Supabase query fails."""
        with patch(
            "backend.payments.subscription._get_supabase",
            side_effect=Exception("connection failed"),
        ):
            result = await get_subscription_status("user_123")

            assert result.is_active is False
            assert result.status == "error"


class TestSubscriptionCancellation:
    """Tests for subscription cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_active_raises(self) -> None:
        """Cancellation raises ValueError when user has no active subscription."""
        mock_client = _mock_supabase_client()
        mock_client.execute.return_value = MagicMock(data=None)

        with patch(
            "backend.payments.subscription._get_supabase",
            return_value=mock_client,
        ):
            with pytest.raises(ValueError, match="No active subscription found"):
                await cancel_subscription("user_123")

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self) -> None:
        """Cancellation sets cancel_at_period_end on Stripe and updates DB."""
        mock_client = _mock_supabase_client()
        mock_client.execute.return_value = MagicMock(
            data={
                "status": "active",
                "stripe_subscription_id": "sub_cancel_test",
                "current_period_end": "2026-04-29T00:00:00",
                "cancel_at_period_end": False,
            }
        )

        with (
            patch(
                "backend.payments.subscription._get_supabase",
                return_value=mock_client,
            ),
            patch(
                "backend.payments.subscription.stripe.Subscription.modify",
            ) as mock_modify,
        ):
            result = await cancel_subscription("user_123")

            mock_modify.assert_called_once_with(
                "sub_cancel_test",
                cancel_at_period_end=True,
            )
            assert isinstance(result, SubscriptionStatus)


class TestInvoicePaid:
    """Tests for _handle_invoice_paid via the webhook dispatcher."""

    @pytest.mark.asyncio
    async def test_invoice_paid_with_valid_subscription(self) -> None:
        """Invoice paid updates subscription to active and syncs period end."""
        mock_event = {
            "id": "evt_inv_paid_1",
            "type": "invoice.paid",
            "data": {
                "object": {
                    "subscription": "sub_inv_123",
                    "customer": "cus_inv_456",
                    "lines": {
                        "data": [
                            {
                                "period": {
                                    "end": 1717200000,
                                }
                            }
                        ]
                    },
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            mock_client.table.assert_called_with("subscriptions")
            mock_client.update.assert_called_once()
            update_args = mock_client.update.call_args[0][0]
            assert update_args["status"] == "active"
            assert update_args["current_period_end"] == 1717200000

    @pytest.mark.asyncio
    async def test_invoice_paid_no_subscription_does_not_crash(self) -> None:
        """Invoice paid with no subscription_id logs and returns ok."""
        mock_event = {
            "id": "evt_inv_paid_nosub",
            "type": "invoice.paid",
            "data": {
                "object": {
                    "subscription": "",
                    "customer": "cus_inv_789",
                }
            },
        }

        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_invoice_paid_without_line_items(self) -> None:
        """Invoice paid without line items still sets status to active."""
        mock_event = {
            "id": "evt_inv_paid_nolines",
            "type": "invoice.paid",
            "data": {
                "object": {
                    "subscription": "sub_inv_nolines",
                    "customer": "cus_inv_nolines",
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            update_args = mock_client.update.call_args[0][0]
            assert update_args["status"] == "active"
            assert "current_period_end" not in update_args


class TestInvoicePaymentFailed:
    """Tests for _handle_invoice_payment_failed via the webhook dispatcher."""

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_marks_past_due(self) -> None:
        """Failed invoice payment marks subscription as past_due."""
        mock_event = {
            "id": "evt_inv_fail_1",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "subscription": "sub_fail_123",
                    "customer": "cus_fail_456",
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            mock_client.table.assert_called_with("subscriptions")
            mock_client.update.assert_called_once_with({"status": "past_due"})

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_no_subscription(self) -> None:
        """Failed invoice with no subscription_id logs and returns ok."""
        mock_event = {
            "id": "evt_inv_fail_nosub",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "subscription": "",
                    "customer": "cus_fail_789",
                }
            },
        }

        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}


class TestWebhookEventRouting:
    """Tests for webhook event type routing and edge cases."""

    @pytest.mark.asyncio
    async def test_unknown_event_type_returns_ok(self) -> None:
        """Unknown event types are logged but do not raise exceptions."""
        mock_event = {
            "id": "evt_unknown",
            "type": "payment_intent.created",
            "data": {
                "object": {
                    "id": "pi_test_123",
                }
            },
        }

        with patch(
            "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_checkout_completed_routes_correctly(self) -> None:
        """checkout.session.completed routes to _handle_checkout_completed."""
        mock_event = {
            "id": "evt_route_checkout",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_route_1",
                    "subscription": "sub_route_1",
                    "metadata": {"user_id": "user_route_1"},
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            # Verify upsert was called (checkout uses upsert, not update)
            mock_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_updated_routes_correctly(self) -> None:
        """customer.subscription.updated routes to _handle_subscription_updated."""
        mock_event = {
            "id": "evt_route_sub_upd",
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_route_upd",
                    "status": "past_due",
                    "customer": "cus_route_upd",
                    "current_period_end": "2026-05-01T00:00:00Z",
                    "cancel_at_period_end": True,
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            update_args = mock_client.update.call_args[0][0]
            assert update_args["status"] == "past_due"
            assert update_args["cancel_at_period_end"] is True
            assert update_args["current_period_end"] == "2026-05-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_subscription_deleted_routes_correctly(self) -> None:
        """customer.subscription.deleted routes to _handle_subscription_deleted."""
        mock_event = {
            "id": "evt_route_sub_del",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_route_del",
                    "customer": "cus_route_del",
                }
            },
        }

        mock_client = _mock_supabase_client()

        with (
            patch(
                "backend.payments.stripe_webhooks.stripe.Webhook.construct_event",
                return_value=mock_event,
            ),
            patch(
                "backend.payments.stripe_webhooks._get_supabase",
                return_value=mock_client,
            ),
        ):
            result = await handle_webhook(b"payload", "sig_header")
            assert result == {"status": "ok"}
            mock_client.update.assert_called_once_with({"status": "canceled"})
