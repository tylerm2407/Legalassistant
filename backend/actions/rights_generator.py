"""Rights summary generation using Claude with legal profile context.

Generates plain-English summaries of the user's legal rights with
applicable statute citations, tailored to their state and situation.
"""

from __future__ import annotations

import json

from anthropic.types import TextBlock

from backend.legal.state_laws import STATE_LAWS
from backend.models.action_output import RightsSummary
from backend.models.legal_profile import LegalProfile
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

RIGHTS_PROMPT: str = """You are CaseMate, an AI legal assistant generating a rights summary.

Generate a clear, plain-English summary of the user's legal rights
based on their situation and state.
Return ONLY a JSON object with this exact structure:
{
    "text": "Full narrative explanation of the user's rights in plain English, 3-5 paragraphs",
    "key_rights": ["Bulleted list of the 5-8 most important specific rights"],
    "applicable_laws": ["List of statute citations that establish these rights"]
}

Rules:
- Use plain English. Define legal terms the first time you use them.
- Be specific to the user's state — cite actual statutes.
- Organize rights from most to least relevant to the user's situation.
- Include both state and federal protections where applicable.
- Note any rights that have time limits or require specific actions to preserve.
- End with a clear statement of what the user should do next.
"""


@retry_anthropic
async def generate_rights_summary(
    profile: LegalProfile,
    context: str,
) -> RightsSummary:
    """Generate a rights summary tailored to the user's legal situation.

    Builds a prompt combining the user's profile and applicable state laws,
    then asks Claude to generate a comprehensive but accessible rights
    summary with real statute citations.

    Args:
        profile: The user's legal profile for personalization.
        context: Description of the specific situation the user wants
                 to understand their rights for.

    Returns:
        A RightsSummary containing the narrative explanation, key rights
        list, and applicable law citations.

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

    dynamic_context = (
        f"USER PROFILE:\n{profile_context}\n\n"
        f"APPLICABLE LAWS:\n" + "\n".join(laws_context_parts) + "\n\n"
        f"SITUATION:\n{context}"
    )

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[
            {"type": "text", "text": RIGHTS_PROMPT, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dynamic_context},
        ],
        messages=[
            {
                "role": "user",
                "content": "Generate the rights summary based on the above context.",
            }
        ],
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""
    _logger.info(
        "rights_summary_generated",
        user_id=profile.user_id,
        response_length=len(response_text),
    )

    try:
        parsed = json.loads(response_text)
        return RightsSummary(
            text=parsed.get("text", ""),
            key_rights=parsed.get("key_rights", []),
            applicable_laws=parsed.get("applicable_laws", []),
        )
    except json.JSONDecodeError as exc:
        _logger.error(
            "rights_summary_parse_error",
            user_id=profile.user_id,
            raw_response=response_text[:500],
        )
        raise RuntimeError(f"Failed to parse rights summary response as JSON: {exc}") from exc
