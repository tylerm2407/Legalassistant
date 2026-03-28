"""Consumer protection domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for consumer protection issues. Used by the memory
injector to specialize Claude's responses when the classifier detects a
consumer protection question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a consumer protection issue. Focus on identifying whether "
    "the business engaged in deceptive, unfair, or unconscionable practices. Many state "
    "consumer protection statutes (like MA c. 93A or TX DTPA) require a demand letter "
    "before filing suit — always check this procedural requirement. Distinguish between "
    "warranty claims (express vs. implied) and fraud claims, as remedies differ. For "
    "product defects, determine if lemon law applies (typically new vehicles only). "
    "Advise the user to preserve all receipts, contracts, advertisements, and written "
    "communications. Explain the difference between individual claims and class actions. "
    "Note that many consumer statutes allow recovery of attorney fees, making smaller "
    "claims economically viable."
)

KEY_STATUTES: dict[str, str] = {
    "FTC Act (15 U.S.C. § 45)": (
        "Federal Trade Commission Act prohibiting unfair or deceptive acts or practices "
        "in commerce. Enforced by the FTC, no private right of action."
    ),
    "Magnuson-Moss Warranty Act (15 U.S.C. § 2301)": (
        "Federal law governing consumer product warranties, requiring clear disclosure "
        "and allowing suit for breach of warranty."
    ),
    "M.G.L. c. 93A": (
        "Massachusetts Consumer Protection Act prohibiting unfair or deceptive acts with "
        "treble damages. Requires 30-day demand letter before suit."
    ),
    "Cal. Civ. Code § 1750 (CLRA)": (
        "California Consumers Legal Remedies Act listing specific prohibited deceptive "
        "practices with class action availability."
    ),
    "Tex. Bus. & Com. Code § 17.41 (DTPA)": (
        "Texas Deceptive Trade Practices Act providing treble damages for knowing "
        "violations. Requires 60-day demand letter."
    ),
    "N.Y. Gen. Bus. Law § 349": (
        "New York deceptive practices statute allowing private right of action with "
        "treble damages up to $1,000."
    ),
    "Fla. Stat. § 501.201 (FDUTPA)": (
        "Florida Deceptive and Unfair Trade Practices Act providing injunctive relief "
        "and attorney fees for prevailing consumer plaintiffs."
    ),
    "UCC § 2-314 (Implied Warranty of Merchantability)": (
        "Uniform Commercial Code provision implying that goods sold by merchants are "
        "fit for their ordinary purpose."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "I bought a defective product and the company won't give me a refund. What can I do?",
    "A company charged me for a subscription I already cancelled. How do I get my money back?",
    "I think I was scammed by an online business. What are my legal options?",
    "My new car keeps breaking down. Does the lemon law apply?",
    "A contractor did terrible work and won't fix it. What are my rights?",
]
