"""Keyword-based legal domain classifier.

Classifies user questions into one of 10 legal domains using keyword
matching. This is deliberately NOT LLM-based — it needs to be fast
and deterministic since it runs on every user message before the
Claude API call.
"""

from __future__ import annotations

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "landlord_tenant": [
        "landlord",
        "tenant",
        "rent",
        "lease",
        "eviction",
        "evict",
        "security deposit",
        "apartment",
        "rental",
        "move-in",
        "move-out",
        "habitability",
        "repair",
        "maintenance",
        "sublease",
        "subtenant",
        "notice to quit",
        "rent increase",
        "housing code",
        "lockout",
    ],
    "employment_rights": [
        "employer",
        "employee",
        "fired",
        "terminated",
        "wrongful termination",
        "discrimination",
        "harassment",
        "wage",
        "overtime",
        "paycheck",
        "minimum wage",
        "retaliation",
        "whistleblower",
        "fmla",
        "leave",
        "unemployment",
        "workers comp",
        "workplace",
        "job",
        "salary",
    ],
    "consumer_protection": [
        "scam",
        "fraud",
        "refund",
        "warranty",
        "defective",
        "consumer",
        "deceptive",
        "false advertising",
        "recall",
        "lemon law",
        "ftc",
        "bbb",
        "unfair business",
        "return policy",
        "overcharge",
        "billing error",
        "subscription cancel",
        "auto-renew",
        "hidden fee",
    ],
    "debt_collections": [
        "debt collector",
        "collection agency",
        "collections",
        "creditor",
        "debt",
        "owe",
        "past due",
        "default",
        "garnishment",
        "wage garnishment",
        "statute of limitations",
        "cease and desist",
        "fdcpa",
        "credit report",
        "charge off",
        "settlement",
        "payment plan",
        "repossession",
        "repo",
    ],
    "small_claims": [
        "small claims",
        "small claims court",
        "sue",
        "lawsuit",
        "damages",
        "filing fee",
        "court date",
        "hearing",
        "judgment",
        "claim",
        "dispute",
        "mediation",
        "arbitration",
        "settlement",
        "counterclaim",
        "serve",
        "service of process",
        "default judgment",
        "appeal",
    ],
    "contract_disputes": [
        "contract",
        "agreement",
        "breach",
        "breach of contract",
        "terms",
        "conditions",
        "signed",
        "binding",
        "void",
        "voidable",
        "consideration",
        "performance",
        "non-compete",
        "nda",
        "indemnification",
        "liability",
        "clause",
        "amendment",
        "termination clause",
    ],
    "traffic_violations": [
        "traffic ticket",
        "speeding",
        "traffic court",
        "moving violation",
        "parking ticket",
        "dui",
        "dwi",
        "license suspended",
        "points",
        "traffic school",
        "reckless driving",
        "red light",
        "stop sign",
        "accident",
        "hit and run",
        "insurance",
        "registration",
        "citation",
    ],
    "family_law": [
        "divorce",
        "custody",
        "child support",
        "alimony",
        "spousal support",
        "prenup",
        "prenuptial",
        "marriage",
        "separation",
        "visitation",
        "adoption",
        "guardian",
        "guardianship",
        "paternity",
        "domestic violence",
        "restraining order",
        "protective order",
        "parenting plan",
        "marital property",
    ],
    "criminal_records": [
        "criminal record",
        "expungement",
        "expunge",
        "seal record",
        "felony",
        "misdemeanor",
        "arrest record",
        "background check",
        "conviction",
        "probation",
        "parole",
        "plea",
        "plea bargain",
        "public defender",
        "arraignment",
        "bail",
        "bond",
        "sentence",
        "diversion program",
    ],
    "immigration": [
        "visa",
        "immigration",
        "green card",
        "citizenship",
        "naturalization",
        "deportation",
        "removal",
        "asylum",
        "refugee",
        "work permit",
        "ead",
        "h1b",
        "daca",
        "uscis",
        "ice",
        "undocumented",
        "sponsor",
        "petition",
        "i-130",
        "i-485",
    ],
}


def classify_legal_area(question: str) -> str:
    """Classify a user question into a legal domain using keyword matching.

    Performs case-insensitive keyword matching against 10 legal domains.
    Each domain has 15-20 representative keywords. The domain with the
    highest number of keyword matches wins.

    Args:
        question: The user's question or message text.

    Returns:
        The legal domain string (e.g. 'landlord_tenant', 'employment_rights')
        or 'general' if no domain has any keyword matches.
    """
    question_lower = question.lower()

    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return "general"

    return max(scores, key=lambda k: scores[k])
