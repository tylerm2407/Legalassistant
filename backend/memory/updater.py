"""Background task that extracts legal facts from conversations.

After each conversation turn, this module sends the conversation to Claude
with an extraction prompt, parses the response for new legal facts, and
merges them into the user's profile. This runs as a background task and
must never crash the main request flow.
"""

from __future__ import annotations

import json
from typing import cast

from anthropic.types import MessageParam, TextBlock

from backend.memory.profile import get_profile, update_profile
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

EXTRACTION_PROMPT: str = """Analyze the following conversation and extract
any NEW legal facts about the user.

Return ONLY a JSON object with this exact structure:
{
    "new_facts": ["fact 1", "fact 2"]
}

Rules:
- Only include facts that are specific and legally relevant
  (dates, amounts, events, relationships, document mentions).
- Do NOT include general legal information or advice that was given.
- Do NOT include facts that are vague or speculative.
- If there are no new facts, return {"new_facts": []}.
- Each fact should be a single, clear sentence.
"""


@retry_anthropic
async def _extract_facts(conversation: list[dict[str, str]]) -> list[str]:
    """Send conversation to Claude to extract new legal facts.

    Args:
        conversation: List of message dicts with 'role' and 'content' keys,
                      representing the conversation to analyze.

    Returns:
        List of newly extracted fact strings. Empty list if no new facts
        are found or if parsing fails.

    Raises:
        anthropic.APIError: If the API call fails after all retries.
    """
    client = get_anthropic_client()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=EXTRACTION_PROMPT,
        messages=cast(list[MessageParam], conversation),
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""

    try:
        parsed = json.loads(response_text)
        facts: list[str] = parsed.get("new_facts", [])
        if not isinstance(facts, list):
            _logger.warning("extraction_invalid_format", raw_response=response_text)
            return []
        return [f for f in facts if isinstance(f, str) and f.strip()]
    except json.JSONDecodeError:
        _logger.warning("extraction_json_parse_error", raw_response=response_text)
        return []


async def update_profile_from_conversation(
    user_id: str,
    conversation: list[dict[str, str]],
) -> None:
    """Extract legal facts from a conversation and merge into the user's profile.

    This is designed to run as a background task after each conversation turn.
    All errors are caught and logged — this function must never crash.

    Args:
        user_id: The Supabase auth user ID whose profile to update.
        conversation: List of message dicts with 'role' and 'content' keys.
    """
    try:
        _logger.info("profile_update_started", user_id=user_id)

        new_facts = await _extract_facts(conversation)

        if not new_facts:
            _logger.info("no_new_facts_extracted", user_id=user_id)
            return

        profile = await get_profile(user_id)
        if profile is None:
            _logger.warning("profile_not_found_for_update", user_id=user_id)
            return

        existing_facts_lower = {f.lower().strip() for f in profile.legal_facts}
        unique_new_facts = [f for f in new_facts if f.lower().strip() not in existing_facts_lower]

        if not unique_new_facts:
            _logger.info("all_facts_already_known", user_id=user_id)
            return

        profile.legal_facts.extend(unique_new_facts)
        await update_profile(profile)

        _logger.info(
            "profile_facts_updated",
            user_id=user_id,
            new_facts_count=len(unique_new_facts),
        )

    except Exception as exc:
        _logger.error(
            "profile_update_failed",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
