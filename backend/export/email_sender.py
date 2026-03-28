"""Email delivery for exported documents.

Sends generated documents via email using SMTP. Currently supports
sending text document attachments to specified email addresses.
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


async def send_document_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_bytes: bytes,
    attachment_filename: str,
) -> bool:
    """Send a document as an email attachment.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Email body text.
        attachment_bytes: The document content as bytes.
        attachment_filename: Filename for the attachment.

    Returns:
        True if sent successfully, False otherwise.
    """
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_email = os.environ.get("SMTP_FROM", "support@casemate.ai")

    if not smtp_host or not smtp_user:
        _logger.warning(
            "email_not_configured",
            message="SMTP settings not configured. Email sending disabled.",
        )
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body)

        msg.add_attachment(
            attachment_bytes,
            maintype="application",
            subtype="pdf",
            filename=attachment_filename,
        )

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        _logger.info(
            "email_sent",
            to=to_email,
            subject=subject,
            attachment=attachment_filename,
        )
        return True

    except smtplib.SMTPException as exc:
        _logger.error(
            "email_send_error",
            to=to_email,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return False
