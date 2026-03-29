"""Tests for the email sender module.

Verifies send_document_email handles success, SMTP errors, and
unconfigured SMTP gracefully. All SMTP operations are mocked.
"""

from __future__ import annotations

import smtplib
from unittest.mock import MagicMock, patch

from backend.export.email_sender import send_document_email

ATTACHMENT = b"%PDF-1.4 fake pdf content"


class TestSendDocumentEmail:
    """Verify send_document_email behavior across scenarios."""

    async def test_sends_email_successfully(self) -> None:
        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "casemate@example.com",
            "SMTP_PASS": "secret",
            "SMTP_FROM": "support@casemate.ai",
        }
        mock_server = MagicMock()
        with (
            patch.dict("os.environ", env, clear=False),
            patch("backend.export.email_sender.smtplib.SMTP") as mock_smtp_cls,
        ):
            mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = await send_document_email(
                to_email="user@example.com",
                subject="Your Legal Document",
                body="Please find attached your document.",
                attachment_bytes=ATTACHMENT,
                attachment_filename="document.pdf",
            )

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("casemate@example.com", "secret")
        mock_server.send_message.assert_called_once()

    async def test_returns_false_on_smtp_error(self) -> None:
        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "casemate@example.com",
            "SMTP_PASS": "secret",
        }
        with (
            patch.dict("os.environ", env, clear=False),
            patch("backend.export.email_sender.smtplib.SMTP") as mock_smtp_cls,
        ):
            mock_smtp_cls.return_value.__enter__ = MagicMock(
                side_effect=smtplib.SMTPException("Connection refused")
            )
            mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = await send_document_email(
                to_email="user@example.com",
                subject="Test",
                body="Body",
                attachment_bytes=ATTACHMENT,
                attachment_filename="doc.pdf",
            )

        assert result is False

    async def test_returns_false_when_not_configured(self) -> None:
        env = {"SMTP_HOST": "", "SMTP_USER": ""}
        with patch.dict("os.environ", env, clear=False):
            result = await send_document_email(
                to_email="user@example.com",
                subject="Test",
                body="Body",
                attachment_bytes=ATTACHMENT,
                attachment_filename="doc.pdf",
            )

        assert result is False
