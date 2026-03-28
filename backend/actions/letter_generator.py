"""Demand letter generation using Claude with legal profile context.

Generates complete, ready-to-send demand letters with real statute citations
tailored to the user's state and legal situation.
"""

from __future__ import annotations

import json
import os

import anthropic

from backend.legal.state_laws import STATE_LAWS
from backend.models.action_output import DemandLetter
from backend.models.legal_profile import LegalProfile
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

LETTER_PROMPT: str = """You are Lex, an AI legal assistant generating a demand letter.

Generate a professional demand letter based on the user's situation and applicable laws.
Return ONLY a JSON object with this exact structure:
{
    "text": "The full text of the demand letter, properly formatted with date, addresses, salutation, body paragraphs, and closing",
    "citations": ["List of statute citations referenced in the letter"],
    "recipient": "Name or description of the letter recipient if known, or null",
    "subject": "The subject line of the demand"
}

Rules:
- Use a professional, firm but respectful tone.
- Cite specific statutes from the user's state.
- Include specific deadlines for response (typically 30 days).
- Reference specific facts from the user's situation.
- Include the legal consequences of non-compliance.
- Format the letter ready to print and send.
"""


@retry_anthropic
async def generate_demand_letter(
    profile: LegalProfile,
    context: str,
) -> DemandLetter:
    """Generate a demand letter tailored to the user's legal situation.

    Builds a prompt combining the user's profile, applicable state laws,
    and the specific context for the demand, then asks Claude to generate
    a complete demand letter with real citations.

    Args:
        profile: The user's legal profile for personalization.
        context: Description of the specific situation requiring a demand letter,
                 including what the user is demanding and from whom.

    Returns:
        A DemandLetter containing the full letter text, citations,
        recipient information, and subject line.

    Raises:
        anthropic.APIError: If the Claude API call fails after all retries.
        RuntimeError: If the response cannot be parsed as valid JSON.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

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
        system=LETTER_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"USER PROFILE:\n{profile_context}\n\n"
                    f"APPLICABLE LAWS:\n" + "\n".join(laws_context_parts) + "\n\n"
                    f"SITUATION / DEMAND CONTEXT:\n{context}"
                ),
            }
        ],
    )

    response_text = response.content[0].text if response.content else ""
    _logger.info(
        "demand_letter_generated",
        user_id=profile.user_id,
        response_length=len(response_text),
    )

    try:
        parsed = json.loads(response_text)
        return DemandLetter(
            text=parsed.get("text", ""),
            citations=parsed.get("citations", []),
            recipient=parsed.get("recipient"),
            subject=parsed.get("subject", "Demand Letter"),
        )
    except json.JSONDecodeError as exc:
        _logger.error(
            "demand_letter_parse_error",
            user_id=profile.user_id,
            raw_response=response_text[:500],
        )
        raise RuntimeError(
            f"Failed to parse demand letter response as JSON: {exc}"
        ) from exc
