"""System prompt builder that injects the user's legal profile into every Claude call.

This is the most important file in the Lex backend. The build_system_prompt
function constructs a personalized system prompt that makes Claude aware of
the user's state, legal situation, active issues, and known facts — so every
response is tailored rather than generic.
"""

from __future__ import annotations

from backend.legal.classifier import classify_legal_area
from backend.legal.state_laws import STATE_LAWS
from backend.models.legal_profile import LegalProfile

LEX_BASE_INSTRUCTIONS: str = """You are Lex, a personalized AI legal assistant.
You help everyday people understand their legal rights, navigate disputes,
and take concrete next steps.

RULES:
1. Always cite specific statutes when discussing legal rights.
2. Tailor every answer to the user's state and personal situation (provided below).
3. Use plain English. Explain legal terms when you first use them.
4. If you are unsure about a specific law, say so clearly. Never fabricate citations.
5. Always recommend consulting a licensed attorney for complex or high-stakes matters.
6. You are NOT a lawyer. You provide legal information, not legal advice.
7. When the user has active legal issues, proactively connect your answer to those issues.
8. Be empathetic but precise. People come to you stressed — acknowledge that, then help.

DISCLAIMER (include at the end of substantive legal responses):
"This is legal information, not legal advice. For advice specific to your
situation, consult a licensed attorney in your state."
"""


def _format_active_issues(profile: LegalProfile) -> str:
    """Format active legal issues into a readable prompt section.

    Args:
        profile: The user's legal profile containing active issues.

    Returns:
        Formatted string listing each active issue with its type, summary,
        status, and any associated notes. Returns empty string if no
        active issues exist.
    """
    if not profile.active_issues:
        return ""

    lines: list[str] = ["\n--- ACTIVE LEGAL ISSUES ---"]
    for i, issue in enumerate(profile.active_issues, 1):
        lines.append(f"\nIssue {i}: {issue.issue_type.replace('_', ' ').title()}")
        lines.append(f"  Summary: {issue.summary}")
        lines.append(f"  Status: {issue.status.value}")
        if issue.notes:
            lines.append("  Key facts:")
            for note in issue.notes:
                lines.append(f"    - {note}")
    return "\n".join(lines)


def _format_legal_facts(profile: LegalProfile) -> str:
    """Format known legal facts into a readable prompt section.

    Args:
        profile: The user's legal profile containing extracted facts.

    Returns:
        Formatted string listing all known legal facts. Returns empty
        string if no facts exist.
    """
    if not profile.legal_facts:
        return ""

    lines: list[str] = ["\n--- KNOWN LEGAL FACTS ---"]
    for fact in profile.legal_facts:
        lines.append(f"- {fact}")
    return "\n".join(lines)


def build_system_prompt(profile: LegalProfile, user_message: str) -> str:
    """Build a complete system prompt personalized to the user's legal profile.

    This function is called before every Claude API request. It combines:
    1. Base Lex instructions and rules
    2. The user's personal legal context (state, situation, active issues)
    3. State-specific law citations relevant to the detected legal domain
    4. Domain-specific guidance based on the classified legal area

    Args:
        profile: The user's persistent legal profile.
        user_message: The current user message, used to classify the legal
                      domain and select relevant state laws.

    Returns:
        A complete system prompt string ready for the Claude API system parameter.
    """
    legal_area = classify_legal_area(user_message)

    # Start with base instructions
    prompt_parts: list[str] = [LEX_BASE_INSTRUCTIONS]

    # Add personal context
    prompt_parts.append("\n--- USER PROFILE ---")
    prompt_parts.append(f"Name: {profile.display_name}")
    prompt_parts.append(f"State: {profile.state}")
    prompt_parts.append(f"Housing: {profile.housing_situation}")
    prompt_parts.append(f"Employment: {profile.employment_type}")
    prompt_parts.append(f"Family: {profile.family_status}")

    # Add active issues and known facts
    active_issues_text = _format_active_issues(profile)
    if active_issues_text:
        prompt_parts.append(active_issues_text)

    legal_facts_text = _format_legal_facts(profile)
    if legal_facts_text:
        prompt_parts.append(legal_facts_text)

    # Add state-specific laws for the detected domain
    state_code = profile.state[:2].upper() if len(profile.state) >= 2 else profile.state.upper()
    state_laws = STATE_LAWS.get(state_code, {})
    federal_laws = STATE_LAWS.get("federal_defaults", {})

    if legal_area != "general":
        prompt_parts.append(f"\n--- APPLICABLE LAW ({legal_area.replace('_', ' ').upper()}) ---")
        if legal_area in state_laws:
            prompt_parts.append(f"State law ({state_code}): {state_laws[legal_area]}")
        if legal_area in federal_laws:
            prompt_parts.append(f"Federal law: {federal_laws[legal_area]}")

    prompt_parts.append(f"\n--- DETECTED LEGAL AREA: {legal_area} ---")

    return "\n".join(prompt_parts)
