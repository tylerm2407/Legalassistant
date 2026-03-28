"""Traffic violations domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for traffic violation issues. Used by the memory injector
to specialize Claude's responses when the classifier detects a traffic
violation question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with a traffic violation matter. Start by identifying the "
    "specific violation type (moving violation, parking, DUI/DWI) as each has very "
    "different consequences and procedures. For standard tickets, explain the options: "
    "pay the fine (which is an admission of guilt), contest in traffic court, or "
    "request traffic school to avoid points. For DUI/DWI, emphasize the seriousness — "
    "there are often two separate proceedings (criminal court and DMV administrative "
    "hearing) with different deadlines. Explain the points system in the user's state "
    "and the consequences of accumulating points. Advise on whether hiring a traffic "
    "attorney is worthwhile given the specific violation and potential consequences. "
    "Always check deadlines for responding to tickets or requesting hearings."
)

KEY_STATUTES: dict[str, str] = {
    "M.G.L. c. 90, § 24 (MA OUI)": (
        "Massachusetts Operating Under the Influence statute with escalating penalties "
        "based on number of offenses. First offense can include license loss and fines."
    ),
    "Cal. Vehicle Code § 23152 (CA DUI)": (
        "California DUI statute covering both alcohol (BAC 0.08+) and drug impairment. "
        "Separate DMV hearing required within 10 days of arrest."
    ),
    "N.Y. VTL § 1192 (NY DWI/DWAI)": (
        "New York driving while intoxicated and driving while ability impaired statutes "
        "with tiered penalties based on BAC level."
    ),
    "Tex. Penal Code § 49.04 (TX DWI)": (
        "Texas Driving While Intoxicated statute. First offense is a Class B misdemeanor "
        "with up to 180 days jail and $2,000 fine."
    ),
    "Fla. Stat. § 316.193 (FL DUI)": (
        "Florida DUI statute with mandatory minimum penalties including fines, license "
        "revocation, and possible ignition interlock device."
    ),
    "Cal. Vehicle Code § 22350 (Basic Speed Law)": (
        "California basic speed law prohibiting driving faster than is reasonable "
        "given conditions, regardless of posted limits."
    ),
    "N.Y. VTL § 510 (Points System)": (
        "New York point accumulation system where 11 points in 18 months triggers "
        "mandatory license suspension."
    ),
    "49 U.S.C. § 30101 (NHTSA)": (
        "Federal motor vehicle safety standards administered by the National Highway "
        "Traffic Safety Administration."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "Should I fight my speeding ticket or just pay it?",
    "I got a DUI. What happens next and do I need a lawyer?",
    "How many points will this ticket add to my license?",
    "Can I go to traffic school to dismiss my ticket?",
    "My license was suspended. How do I get it reinstated?",
]
