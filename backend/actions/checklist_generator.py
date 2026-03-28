"""Checklist generation using Claude with legal profile context.

Generates prioritized next-steps checklists with deadlines, tailored
to the user's state and legal situation.
"""

from __future__ import annotations

import json

import anthropic
from anthropic.types import TextBlock

from backend.legal.state_laws import STATE_LAWS
from backend.models.action_output import Checklist
from backend.models.legal_profile import LegalProfile
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

CHECKLIST_PROMPT: str = """You are Lex, an AI legal assistant generating a next-steps checklist.

Generate a prioritized checklist of actions the user should take based on their legal situation.
Return ONLY a JSON object with this exact structure:
{
    "items": ["Action item 1", "Action item 2", ...],
    "deadlines": ["Deadline for item 1 or null if no deadline", null, ...],
    "priority_order": [0, 2, 1, ...]
}

Rules:
- Each item should be a specific, actionable step (not vague advice).
- Include deadlines where applicable (statutory deadlines, filing windows, etc.).
- The deadlines list must be the same length as items, using null for items without deadlines.
- priority_order is a list of indices into items, sorted from most urgent to least.
- Include 5-10 items covering: immediate actions, evidence gathering,
  filing/communication steps, and follow-up.
- Note which items require a lawyer vs. which the user can do themselves.
- Reference specific statutes where deadlines come from statutory requirements.
"""


@retry_anthropic
async def generate_checklist(
    profile: LegalProfile,
    context: str,
) -> Checklist:
    """Generate a prioritized action checklist for the user's legal situation.

    Builds a prompt combining the user's profile and applicable state laws,
    then asks Claude to generate a concrete, prioritized list of next steps
    with deadlines where applicable.

    Args:
        profile: The user's legal profile for personalization.
        context: Description of the specific situation the user needs
                 a checklist for.

    Returns:
        A Checklist containing action items, deadlines, and priority ordering.

    Raises:
        anthropic.APIError: If the Claude API call fails after all retries.
        RuntimeError: If the response cannot be parsed as valid JSON.
    """
    client = get_anthropic_client()

    state_code = profile.state[:2].upper() if len(profile.state) >= 2 else profile.state.upper()
    state_laws = STATE_LAWS.get(state_code, {})
    federal_laws = STATE_LAWS.get("federal_defaults", {})

    laws_context_parts: list[str] = []
    for domain, law_text in state_laws.items():
        laws_context_parts.append(f"{domain}: {law_text}")
    for domain, law_text in federal_laws.items():
        laws_context_parts.append(f"Federal {domain}: {law_text}")

    profile_context = profile.to_context_string()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=CHECKLIST_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"USER PROFILE:\n{profile_context}\n\n"
                    f"APPLICABLE LAWS:\n" + "\n".join(laws_context_parts) + "\n\n"
                    f"SITUATION:\n{context}"
                ),
            }
        ],
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""
    _logger.info(
        "checklist_generated",
        user_id=profile.user_id,
        response_length=len(response_text),
    )

    try:
        parsed = json.loads(response_text)
        items = parsed.get("items", [])
        deadlines = parsed.get("deadlines", [None] * len(items))
        priority_order = parsed.get("priority_order", list(range(len(items))))

        # Ensure deadlines list matches items length
        while len(deadlines) < len(items):
            deadlines.append(None)
        deadlines = deadlines[: len(items)]

        # Ensure priority_order has valid indices
        valid_indices = set(range(len(items)))
        priority_order = [i for i in priority_order if i in valid_indices]
        # Add any missing indices at the end
        for i in range(len(items)):
            if i not in priority_order:
                priority_order.append(i)

        return Checklist(
            items=items,
            deadlines=deadlines,
            priority_order=priority_order,
        )
    except json.JSONDecodeError as exc:
        _logger.error(
            "checklist_parse_error",
            user_id=profile.user_id,
            raw_response=response_text[:500],
        )
        raise RuntimeError(
            f"Failed to parse checklist response as JSON: {exc}"
        ) from exc
