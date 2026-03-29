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

    async def test_smtp_connection_timeout(self) -> None:
        """Connection timeout should return False, not crash."""
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
            mock_smtp_cls.side_effect = smtplib.SMTPException("Connection timed out")

            result = await send_document_email(
                to_email="user@example.com",
                subject="Timeout Test",
                body="Body",
                attachment_bytes=ATTACHMENT,
                attachment_filename="doc.pdf",
            )

        assert result is False

    async def test_missing_smtp_from_uses_default(self) -> None:
        """When SMTP_FROM is not set, should use the default support@casemate.ai."""
        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "casemate@example.com",
            "SMTP_PASS": "secret",
        }
        mock_server = MagicMock()
        with (
            patch.dict("os.environ", env, clear=False),
            patch("backend.export.email_sender.smtplib.SMTP") as mock_smtp_cls,
        ):
            import os

            os.environ.pop("SMTP_FROM", None)

            mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = await send_document_email(
                to_email="user@example.com",
                subject="Default From",
                body="Body",
                attachment_bytes=ATTACHMENT,
                attachment_filename="doc.pdf",
            )

        assert result is True
        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg["From"] == "support@casemate.ai"

    async def test_large_attachment(self) -> None:
        """Large attachment (5MB) should still be sent successfully."""
        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "casemate@example.com",
            "SMTP_PASS": "secret",
            "SMTP_FROM": "support@casemate.ai",
        }
        large_attachment = b"x" * (5 * 1024 * 1024)  # 5MB
        mock_server = MagicMock()
        with (
            patch.dict("os.environ", env, clear=False),
            patch("backend.export.email_sender.smtplib.SMTP") as mock_smtp_cls,
        ):
            mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = await send_document_email(
                to_email="user@example.com",
                subject="Large File",
                body="Here is your large document.",
                attachment_bytes=large_attachment,
                attachment_filename="big_doc.pdf",
            )

        assert result is True
        mock_server.send_message.assert_called_once()

    async def test_special_characters_in_subject_and_body(self) -> None:
        """Subject and body with special characters should be handled correctly."""
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
                subject="Re: Demand Letter \u2014 M.G.L. c.186 \u00a715B (3x damages)",
                body="Dear Sir/Madam,\n\nPer \u00a715B, you owe $7,200.\n\nRegards,\nSarah\u2019s CaseMate",
                attachment_bytes=ATTACHMENT,
                attachment_filename="demand_letter.pdf",
            )

        assert result is True
        sent_msg = mock_server.send_message.call_args[0][0]
        assert "\u00a715B" in sent_msg["Subject"]
