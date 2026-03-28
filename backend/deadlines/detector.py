"""Auto-detect legal deadlines from conversation text.

After each conversation turn, this module sends the exchange to Claude
to identify any dates, deadlines, or statutes of limitations mentioned.
Detected deadlines are automatically created in the user's deadline tracker.
"""

from __future__ import annotations

import json

from anthropic.types import TextBlock

from backend.deadlines.tracker import create_deadline
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

DEADLINE_DETECTION_PROMPT: str = """Analyze the following conversation and extract
any deadlines, due dates, statutes of limitations, or time-sensitive legal
requirements mentioned.

Return ONLY a JSON object with this exact structure:
{
    "deadlines": [
        {
            "title": "Short description of the deadline",
            "date": "YYYY-MM-DD",
            "legal_area": "the legal domain (e.g., landlord_tenant, employment_rights)",
            "notes": "Brief context about why this date matters"
        }
    ]
}

Rules:
- Only include specific, actionable deadlines with real dates.
- Convert relative dates (e.g., "within 30 days") to absolute dates based on context.
- Include statutes of limitations when specific to the user's situation.
- If no deadlines are found, return {"deadlines": []}.
- Do NOT include vague time references without specific dates.
"""


@retry_anthropic
async def _detect_deadlines(conversation: list[dict[str, str]]) -> list[dict[str, str]]:
    """Send conversation to Claude to detect deadlines.

    Args:
        conversation: List of message dicts with 'role' and 'content' keys.

    Returns:
        List of deadline dicts with title, date, legal_area, and notes.
    """
    client = get_anthropic_client()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=DEADLINE_DETECTION_PROMPT,
        messages=conversation,  # type: ignore[arg-type]
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""

    try:
        parsed = json.loads(response_text)
        deadlines: list[dict[str, str]] = parsed.get("deadlines", [])
        if not isinstance(deadlines, list):
            _logger.warning("deadline_detection_invalid_format", raw_response=response_text)
            return []
        return deadlines
    except json.JSONDecodeError:
        _logger.warning("deadline_detection_parse_error", raw_response=response_text)
        return []


async def detect_and_save_deadlines(
    user_id: str,
    conversation: list[dict[str, str]],
    conversation_id: str | None = None,
) -> None:
    """Detect deadlines from a conversation and save them.

    This is designed to run as a background task after each conversation turn.
    All errors are caught and logged -- this function must never crash.

    Args:
        user_id: The Supabase auth user ID.
        conversation: List of message dicts with 'role' and 'content' keys.
        conversation_id: Optional source conversation ID.
    """
    try:
        _logger.info("deadline_detection_started", user_id=user_id)

        detected = await _detect_deadlines(conversation)

        if not detected:
            _logger.info("no_deadlines_detected", user_id=user_id)
            return

        for deadline_data in detected:
            title = deadline_data.get("title", "")
            date = deadline_data.get("date", "")
            if not title or not date:
                continue

            await create_deadline(
                user_id=user_id,
                title=title,
                date=date,
                legal_area=deadline_data.get("legal_area"),
                source_conversation_id=conversation_id,
                notes=deadline_data.get("notes", ""),
            )

        _logger.info(
            "deadlines_saved",
            user_id=user_id,
            count=len(detected),
        )

    except Exception as exc:
        _logger.error(
            "deadline_detection_failed",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
