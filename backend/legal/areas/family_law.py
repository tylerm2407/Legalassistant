"""Family law domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for family law issues. Used by the memory injector
to specialize Claude's responses when the classifier detects a family
law question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a family law matter. These cases are deeply personal — be "
    "empathetic while staying legally precise. For divorce, determine whether the state "
    "is community property (CA, TX) or equitable distribution (MA, NY, FL) as this "
    "fundamentally affects asset division. For child custody, the court's primary "
    "concern is always the best interests of the child. Explain the difference between "
    "legal custody (decision-making) and physical custody (where the child lives). For "
    "child support, most states use guidelines formulas — explain the inputs and how "
    "modifications work. For domestic violence situations, prioritize safety: explain "
    "how to obtain a restraining/protective order immediately. Always note that family "
    "law varies dramatically by state and that court filings have strict deadlines."
)

KEY_STATUTES: dict[str, str] = {
    "M.G.L. c. 208 (MA Divorce)": (
        "Massachusetts divorce statute providing both fault and no-fault grounds. "
        "Includes alimony reform with durational limits based on marriage length."
    ),
    "Cal. Fam. Code § 760 (Community Property)": (
        "California community property presumption that all property acquired during "
        "marriage is owned equally by both spouses."
    ),
    "N.Y. Dom. Rel. Law § 236B (Equitable Distribution)": (
        "New York equitable distribution law dividing marital property based on "
        "enumerated factors rather than equal split."
    ),
    "Tex. Fam. Code § 153.002 (Best Interests)": (
        "Texas best interests of the child standard as the primary consideration "
        "in all custody and visitation decisions."
    ),
    "Fla. Stat. § 61.08 (Alimony)": (
        "Florida alimony statute reformed in 2023 to eliminate permanent alimony "
        "and establish durational, rehabilitative, and bridge-the-gap types."
    ),
    "UCCJEA": (
        "Uniform Child Custody Jurisdiction and Enforcement Act determining which "
        "state has jurisdiction over custody disputes."
    ),
    "42 U.S.C. § 651 (Federal Child Support)": (
        "Federal Child Support Enforcement program providing interstate enforcement, "
        "income withholding, and federal tax intercept."
    ),
    "Violence Against Women Act (34 U.S.C. § 12291)": (
        "Federal law providing grants for victim services and establishing that "
        "protective orders from one state are enforceable in all states."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "How does the divorce process work in my state?",
    "What factors does the court consider for child custody?",
    "How is child support calculated and can it be modified?",
    "My spouse is hiding assets. What can I do?",
    "How do I get a restraining order for domestic violence?",
]
