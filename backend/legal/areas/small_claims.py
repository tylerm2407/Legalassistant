"""Small claims court domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for small claims court issues. Used by the memory
injector to specialize Claude's responses when the classifier detects a
small claims question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a small claims court matter. Start by confirming the claim "
    "amount falls within the state's jurisdictional limit (ranges from $5,000 to $25,000 "
    "depending on the state). Explain the filing process step by step: determine the "
    "correct court, file the claim form, pay the filing fee, and properly serve the "
    "defendant. Emphasize that small claims is designed for self-represented parties — "
    "some states like California prohibit attorneys entirely. Help the user organize "
    "their evidence: contracts, receipts, photos, text messages, and witness statements. "
    "Explain what to expect at the hearing and how to present a clear, chronological "
    "narrative. Discuss collection of judgments, as winning the case and collecting the "
    "money are two separate challenges."
)

KEY_STATUTES: dict[str, str] = {
    "M.G.L. c. 218, § 21": (
        "Massachusetts small claims jurisdiction up to $7,000. Cases heard in "
        "district court with simplified procedure."
    ),
    "Cal. Code Civ. Proc. § 116.220": (
        "California small claims limit of $10,000 for individuals, $5,000 for "
        "corporations. No attorneys allowed."
    ),
    "N.Y. Uniform City Court Act § 1801": (
        "New York small claims jurisdiction up to $10,000 in NYC, $5,000 in other city courts."
    ),
    "Tex. Gov. Code § 27.031": (
        "Texas justice court jurisdiction up to $20,000. Both parties may have attorneys."
    ),
    "Fla. Stat. § 34.01": (
        "Florida small claims jurisdiction up to $8,000 with mandatory pre-trial mediation."
    ),
    "28 U.S.C. § 1332": (
        "Federal diversity jurisdiction requiring amount in controversy over $75,000, "
        "making most small claims exclusively state matters."
    ),
    "Cal. Code Civ. Proc. § 116.520": (
        "California service of process requirements for small claims, including "
        "personal service and certified mail options."
    ),
    "Fla. Small Claims Rule 7.090": (
        "Florida pre-trial conference and mediation requirements in small claims actions."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "How do I file a small claims case and what does it cost?",
    "What evidence do I need to win in small claims court?",
    "Can I sue someone in small claims court if they live in another state?",
    "I won my small claims case but the other party won't pay. Now what?",
    "The amount I'm owed exceeds the small claims limit. What are my options?",
]
