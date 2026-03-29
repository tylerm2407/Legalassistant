"""Weighted keyword-based legal domain classifier.

Classifies user questions into one of 10 legal domains using weighted
keyword matching with multi-word phrase priority. This is deliberately
NOT LLM-based — it needs to be fast and deterministic since it runs on
every user message before the Claude API call.

Scoring strategy:
  - Multi-word phrases (e.g. "security deposit") receive a 3x weight
    boost because they are more specific and less likely to be ambiguous.
  - Single-word keywords receive a base weight of 1.
  - When two domains tie on score, the domain with the longest matching
    keyword wins (longer match = more specific intent).
  - If no keywords match, returns "general".
"""

from __future__ import annotations

# Weight multiplier for multi-word keyword phrases (2+ words).
# Multi-word phrases are more specific signals of intent, so they
# receive higher weight than single-word matches.
PHRASE_BOOST: int = 3

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


def _keyword_weight(keyword: str) -> int:
    """Return the scoring weight for a keyword based on word count.

    Multi-word phrases (e.g. "security deposit", "breach of contract")
    receive a boosted weight because they are more specific signals of
    user intent than single-word keywords.

    Args:
        keyword: A keyword string from DOMAIN_KEYWORDS.

    Returns:
        PHRASE_BOOST (3) for multi-word phrases, 1 for single words.
    """
    return PHRASE_BOOST if " " in keyword else 1


def _longest_match_length(question_lower: str, keywords: list[str]) -> int:
    """Return the character length of the longest matching keyword.

    Used as a tiebreaker when two domains have equal scores. A longer
    matching keyword indicates more specific intent.

    Args:
        question_lower: The user's question in lowercase.
        keywords: The keyword list for a domain.

    Returns:
        Length of the longest matching keyword, or 0 if none match.
    """
    return max(
        (len(kw) for kw in keywords if kw in question_lower),
        default=0,
    )


def classify_legal_area(question: str) -> str:
    """Classify a user question into a legal domain using weighted keyword matching.

    Performs case-insensitive keyword matching against 10 legal domains
    with weighted scoring. Multi-word phrases receive a 3x weight boost
    over single-word keywords because they are more specific indicators
    of legal intent (e.g. "security deposit" is a stronger signal for
    landlord-tenant than "repair" alone).

    Tie-breaking: when two domains score equally, the domain with the
    longest individual keyword match wins — longer matches indicate
    more specific user intent.

    Args:
        question: The user's question or message text.

    Returns:
        The legal domain string (e.g. 'landlord_tenant', 'employment_rights')
        or 'general' if no domain has any keyword matches.

    Examples:
        >>> classify_legal_area("my landlord kept my security deposit")
        'landlord_tenant'
        >>> classify_legal_area("hello how are you")
        'general'
    """
    question_lower = question.lower()

    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(_keyword_weight(kw) for kw in keywords if kw in question_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return "general"

    max_score = max(scores.values())
    top_domains = [d for d, s in scores.items() if s == max_score]

    if len(top_domains) == 1:
        return top_domains[0]

    # Tiebreaker: prefer the domain with the longest matching keyword
    return max(
        top_domains,
        key=lambda d: _longest_match_length(question_lower, DOMAIN_KEYWORDS[d]),
    )
