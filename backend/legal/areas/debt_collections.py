"""Debt collections domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for debt collection issues. Used by the memory injector
to specialize Claude's responses when the classifier detects a debt
collections question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a debt collection issue. First determine whether the "
    "collector is the original creditor or a third-party collector, as the FDCPA only "
    "applies to third-party collectors (though some states extend protections to "
    "original creditors). Always check the statute of limitations for the specific "
    "debt type in the user's state — if expired, the debt is time-barred and the user "
    "should not make any payment that could restart the clock. Explain the user's right "
    "to request debt validation within 30 days of first contact. For harassment, "
    "document every call with date, time, and what was said. Explain wage garnishment "
    "limits and exemptions. Advise on the impact of debt on credit reports and the "
    "7-year reporting period under the FCRA."
)

KEY_STATUTES: dict[str, str] = {
    "FDCPA (15 U.S.C. § 1692)": (
        "Fair Debt Collection Practices Act regulating third-party debt collectors, "
        "prohibiting harassment, false statements, and unfair practices."
    ),
    "FCRA (15 U.S.C. § 1681)": (
        "Fair Credit Reporting Act governing accuracy of credit reports with 7-year "
        "reporting limit for most negative information."
    ),
    "TILA (15 U.S.C. § 1601)": (
        "Truth in Lending Act requiring clear disclosure of credit terms including "
        "APR, finance charges, and payment schedules."
    ),
    "Regulation F (12 CFR Part 1006)": (
        "CFPB rule implementing the FDCPA with modern communication rules including "
        "limits on call frequency (7 calls per week per debt)."
    ),
    "Cal. Civ. Code § 1788 (Rosenthal Act)": (
        "California law extending FDCPA-like protections to original creditors, "
        "not just third-party collectors."
    ),
    "M.G.L. c. 93, § 49": (
        "Massachusetts debt collection regulation with AG enforcement through "
        "940 CMR 7.00 consumer protection rules."
    ),
    "Tex. Fin. Code Chapter 392": (
        "Texas Debt Collection Act prohibiting fraudulent, deceptive, or "
        "misleading representations by debt collectors."
    ),
    "11 U.S.C. § 362 (Automatic Stay)": (
        "Bankruptcy automatic stay that immediately stops all collection actions, "
        "lawsuits, garnishments, and creditor contact upon filing."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "A debt collector keeps calling me at work. Can they do that?",
    "I got a letter about a debt I don't recognize. What should I do?",
    "The statute of limitations on my debt has passed. Can they still sue me?",
    "A collector is threatening to garnish my wages. What are my rights?",
    "How do I dispute an incorrect debt on my credit report?",
]
