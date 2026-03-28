"""Contract disputes domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for contract dispute issues. Used by the memory injector
to specialize Claude's responses when the classifier detects a contract
dispute question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a contract dispute. Begin by determining the type of "
    "contract (written, oral, implied) and whether it involves goods (UCC applies) or "
    "services (common law applies). Check whether the statute of frauds requires the "
    "contract to be in writing. Identify the specific breach: failure to perform, "
    "defective performance, or anticipatory repudiation. Explain available remedies: "
    "compensatory damages, specific performance, rescission, or restitution. Advise on "
    "any dispute resolution clauses (arbitration, mediation) that may control how the "
    "dispute must be handled. Check for limitation of liability clauses, force majeure "
    "provisions, and notice requirements. Always note the applicable statute of "
    "limitations for contract claims in the user's state."
)

KEY_STATUTES: dict[str, str] = {
    "UCC § 2-201 (Statute of Frauds for Goods)": (
        "Requires written evidence for sale of goods over $500. Exceptions exist for "
        "specially manufactured goods, admissions, and partial performance."
    ),
    "UCC § 2-314 (Implied Warranty of Merchantability)": (
        "Implied warranty that goods sold by merchants are fit for ordinary use, "
        "of average quality, and properly packaged."
    ),
    "UCC § 2-719 (Limitation of Remedies)": (
        "Allows contractual limitation of remedies but not if unconscionable. Failure "
        "of essential purpose restores full UCC remedies."
    ),
    "Restatement (Second) of Contracts § 90": (
        "Promissory estoppel: a promise inducing reliance may be enforceable even "
        "without consideration if injustice can only be avoided by enforcement."
    ),
    "Federal Arbitration Act (9 U.S.C. § 1-16)": (
        "Federal policy favoring enforcement of arbitration agreements in contracts "
        "involving interstate commerce."
    ),
    "E-SIGN Act (15 U.S.C. § 7001)": (
        "Electronic Signatures in Global and National Commerce Act validating "
        "electronic signatures and contracts."
    ),
    "Cal. Civ. Code § 1670.5": (
        "California unconscionability doctrine allowing courts to refuse enforcement "
        "of unconscionable contract terms."
    ),
    "N.Y. Gen. Oblig. Law § 5-701": (
        "New York statute of frauds requiring written agreements for contracts not "
        "performable within one year, among other categories."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "The other party breached our contract. What remedies do I have?",
    "Is my verbal agreement legally binding?",
    "Can I get out of a contract I signed under pressure?",
    "My contract has an arbitration clause. Can I still go to court?",
    "The other party says force majeure excuses their performance. Is that valid?",
]
