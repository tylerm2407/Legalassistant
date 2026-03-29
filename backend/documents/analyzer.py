"""Document analysis using Claude to extract structured legal information.

Sends extracted document text along with the user's legal profile to Claude
for analysis, returning structured findings including document type,
key facts, red flags, and a plain-English summary.
"""

from __future__ import annotations

import json

from anthropic.types import TextBlock

from backend.models.legal_profile import LegalProfile
from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

ANALYSIS_PROMPT: str = """You are CaseMate, an AI legal assistant analyzing a document for a user.

Given the document text and the user's legal profile, extract the following and return as JSON:
{
    "document_type": "type of legal document (e.g., lease agreement, demand letter, court notice)",
    "key_facts": ["list of important facts extracted from the document"],
    "red_flags": ["list of concerning clauses, missing protections, or potential issues"],
    "summary": "Plain-English 2-3 paragraph summary of what this document means for the user"
}

Rules:
- Identify clauses that may be unenforceable under the user's state law.
- Flag any deadlines or time-sensitive requirements.
- Note anything that contradicts the user's known legal facts.
- Be specific — cite section numbers or paragraph references from the document.
- Tailor the analysis to the user's specific situation.
"""


@retry_anthropic
async def analyze_document(text: str, profile: LegalProfile) -> dict[str, object]:
    """Analyze a legal document using Claude with the user's profile context.

    Sends the document text and user profile to Claude, which returns a
    structured analysis including document type, key facts, red flags,
    and a plain-English summary.

    Args:
        text: The extracted text content of the document.
        profile: The user's legal profile for context-aware analysis.

    Returns:
        A dict containing:
            - document_type (str): The type of legal document.
            - key_facts (list[str]): Important facts from the document.
            - red_flags (list[str]): Concerning clauses or issues.
            - summary (str): Plain-English summary for the user.

    Raises:
        anthropic.APIError: If the Claude API call fails after all retries.
        RuntimeError: If the response cannot be parsed as valid JSON.
    """
    client = get_anthropic_client()

    profile_context = profile.to_context_string()

    dynamic_context = f"USER PROFILE:\n{profile_context}\n\nDOCUMENT TEXT:\n{text}"

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[
            {"type": "text", "text": ANALYSIS_PROMPT, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dynamic_context},
        ],
        messages=[
            {
                "role": "user",
                "content": "Analyze the document based on the above context.",
            }
        ],
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""
    _logger.info(
        "document_analyzed",
        user_id=profile.user_id,
        response_length=len(response_text),
    )

    try:
        result = json.loads(response_text)
        # Validate expected keys are present
        expected_keys = {"document_type", "key_facts", "red_flags", "summary"}
        missing_keys = expected_keys - set(result.keys())
        if missing_keys:
            _logger.warning(
                "document_analysis_missing_keys",
                missing=list(missing_keys),
                user_id=profile.user_id,
            )
            for key in missing_keys:
                if key == "document_type":
                    result[key] = "unknown"
                elif key == "summary":
                    result[key] = response_text
                else:
                    result[key] = []

        return dict(result)

    except json.JSONDecodeError as exc:
        _logger.error(
            "document_analysis_parse_error",
            user_id=profile.user_id,
            raw_response=response_text[:500],
        )
        raise RuntimeError(f"Failed to parse document analysis response as JSON: {exc}") from exc
