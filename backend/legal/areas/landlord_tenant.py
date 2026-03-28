"""Landlord-tenant law domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for landlord-tenant legal issues. Used by the memory
injector to specialize Claude's responses when the classifier detects a
landlord-tenant question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a landlord-tenant issue. Focus on the user's specific "
    "state laws regarding security deposits, lease terms, eviction procedures, and "
    "habitability standards. Always cite the relevant state statute when discussing "
    "rights and obligations. Distinguish between lease violations and illegal landlord "
    "conduct. If the user is facing eviction, emphasize procedural requirements the "
    "landlord must follow and any defenses available. For security deposit disputes, "
    "explain the statutory timeline for return, required itemization, and penalties "
    "for landlord non-compliance. Advise on documentation: photos, written "
    "communications, and move-in/move-out condition reports. Always recommend "
    "sending written communications to create a paper trail."
)

KEY_STATUTES: dict[str, str] = {
    "M.G.L. c. 186, § 15B": (
        "Massachusetts security deposit law requiring separate interest-bearing account, "
        "itemized deductions within 30 days, and treble damages for violations."
    ),
    "Cal. Civ. Code § 1950.5": (
        "California security deposit statute limiting deposits to two months' rent for "
        "unfurnished units with 21-day return requirement."
    ),
    "N.Y. Gen. Oblig. Law § 7-108": (
        "New York security deposit law limiting deposits to one month's rent and requiring "
        "14-day return with itemized statement."
    ),
    "Tex. Prop. Code § 92.103": (
        "Texas security deposit return requirement of 30 days with written itemized "
        "accounting of any deductions."
    ),
    "Fla. Stat. § 83.49": (
        "Florida security deposit law requiring 15-30 day return depending on whether "
        "deductions are claimed, with specific notice requirements."
    ),
    "42 U.S.C. § 3601 (Fair Housing Act)": (
        "Federal law prohibiting discrimination in housing based on race, color, religion, "
        "sex, national origin, familial status, and disability."
    ),
    "Cal. Civ. Code § 1942.5": (
        "California anti-retaliation statute protecting tenants who exercise their rights, "
        "including a presumption of retaliation within 180 days."
    ),
    "Warranty of Habitability (common law)": (
        "Implied warranty in most states that rental property must be fit for human "
        "habitation, including working plumbing, heating, and structural integrity."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "My landlord won't return my security deposit. What are my rights?",
    "Can my landlord evict me without proper notice?",
    "My apartment has mold and my landlord won't fix it. What can I do?",
    "Can my landlord raise my rent in the middle of my lease?",
    "My landlord entered my apartment without permission. Is that legal?",
]
