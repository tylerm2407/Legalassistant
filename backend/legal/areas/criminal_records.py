"""Criminal records domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for criminal records issues. Used by the memory injector
to specialize Claude's responses when the classifier detects a criminal
records question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a criminal records issue. Distinguish between expungement "
    "(complete destruction of the record) and sealing (record exists but is hidden from "
    "public view) as the terminology and availability varies by state. Determine the "
    "specific conviction type (misdemeanor vs. felony) and when it occurred, as waiting "
    "periods depend on both. Check if the offense is eligible — violent crimes, sex "
    "offenses, and certain felonies are typically excluded. Explain the application "
    "process step by step, including any required forms, fees, and hearing procedures. "
    "Discuss the practical impact on employment, housing, and professional licensing. "
    "Explain ban-the-box laws that limit when employers can ask about criminal history. "
    "Always note that federal convictions follow different rules than state convictions."
)

KEY_STATUTES: dict[str, str] = {
    "M.G.L. c. 276, § 100E-100U (MA Expungement)": (
        "Massachusetts expungement law allowing sealing of misdemeanors after 3 years "
        "and felonies after 7 years from disposition."
    ),
    "Cal. Penal Code § 1203.4 (CA Expungement)": (
        "California dismissal after completion of probation. Reopens the case, "
        "withdraws guilty plea, and dismisses the case."
    ),
    "N.Y. CPL § 160.59 (NY Sealing)": (
        "New York sealing law allowing up to two convictions to be sealed from "
        "public access after waiting period."
    ),
    "Tex. Gov. Code § 411.071 (TX Nondisclosure)": (
        "Texas nondisclosure orders sealing criminal records from public view "
        "after deferred adjudication or qualifying convictions."
    ),
    "Fla. Stat. § 943.0585 (FL Expungement)": (
        "Florida expungement statute allowing one lifetime expungement or sealing "
        "with Certificate of Eligibility from FDLE."
    ),
    "18 U.S.C. § 3607 (Federal First Offender)": (
        "Federal provision allowing dismissal and expungement for first-time "
        "simple drug possession offenses."
    ),
    "Fair Chance to Compete Act": (
        "Federal ban-the-box law prohibiting federal agencies and contractors from "
        "requesting criminal history before conditional offer."
    ),
    "EEOC Guidance on Criminal Records": (
        "EEOC enforcement guidance stating that blanket exclusion of applicants with "
        "criminal records may violate Title VII disparate impact provisions."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "How do I get my criminal record expunged or sealed?",
    "Will my conviction show up on a background check?",
    "Can an employer refuse to hire me because of my criminal record?",
    "What is the difference between expungement and sealing?",
    "I completed a diversion program. Is my record clean now?",
]
