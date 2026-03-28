"""Employment rights domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for employment law issues. Used by the memory injector
to specialize Claude's responses when the classifier detects an employment
rights question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with an employment rights issue. Focus on whether the user is "
    "an at-will employee or has a contract, as this fundamentally changes their rights. "
    "Always check if the employer size meets the threshold for applicable laws (e.g., "
    "Title VII requires 15+ employees, FMLA requires 50+). Distinguish between state "
    "and federal protections, as state laws often provide broader coverage. For wage "
    "disputes, identify whether the claim involves minimum wage, overtime, tips, or "
    "final paycheck timing. For discrimination claims, explain the EEOC filing process "
    "and state equivalents. Emphasize documentation: keep copies of pay stubs, written "
    "communications, performance reviews, and any evidence of the complained-about "
    "conduct. Note applicable statutes of limitations for filing claims."
)

KEY_STATUTES: dict[str, str] = {
    "Title VII (42 U.S.C. § 2000e)": (
        "Federal law prohibiting employment discrimination based on race, color, religion, "
        "sex, and national origin. Applies to employers with 15 or more employees."
    ),
    "FLSA (29 U.S.C. § 201)": (
        "Fair Labor Standards Act establishing minimum wage, overtime pay, recordkeeping, "
        "and youth employment standards."
    ),
    "ADA (42 U.S.C. § 12101)": (
        "Americans with Disabilities Act requiring reasonable accommodation for qualified "
        "individuals with disabilities."
    ),
    "FMLA (29 U.S.C. § 2601)": (
        "Family and Medical Leave Act providing 12 weeks of unpaid, job-protected leave "
        "for qualifying family and medical reasons."
    ),
    "M.G.L. c. 149, § 148": (
        "Massachusetts Wage Act requiring timely payment of all wages earned with treble "
        "damages and attorney fees for violations."
    ),
    "Cal. Labor Code § 1102.5": (
        "California whistleblower protection statute prohibiting retaliation against "
        "employees who report suspected violations of law."
    ),
    "OSHA (29 U.S.C. § 654)": (
        "Occupational Safety and Health Act requiring employers to provide a workplace "
        "free from recognized hazards."
    ),
    "ADEA (29 U.S.C. § 621)": (
        "Age Discrimination in Employment Act protecting workers 40 and older from "
        "age-based employment discrimination."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "I was fired without warning. Do I have any legal recourse?",
    "My employer isn't paying me overtime. What should I do?",
    "I'm being harassed at work and HR isn't helping. What are my options?",
    "Can my employer change my schedule or pay without notice?",
    "I was denied FMLA leave. How do I file a complaint?",
]
