"""Hybrid legal domain classifier with confidence scoring.

Primary classification uses weighted keyword matching at O(1) latency
for deterministic, low-cost classification on every user message.

When keyword confidence falls below the CONFIDENCE_THRESHOLD, the
classifier can optionally invoke Claude as a fallback for ambiguous
queries. This hybrid approach balances speed (99% of queries resolve
via keywords) with accuracy (edge cases get LLM classification).

Scoring strategy:
  - Multi-word phrases (e.g. "security deposit") receive a 3x weight
    boost because they are more specific and less likely to be ambiguous.
  - Single-word keywords receive a base weight of 1.
  - When two domains tie on score, the domain with the longest matching
    keyword wins (longer match = more specific intent).
  - Confidence score: normalized ratio of top score to total keyword
    matches. Low confidence triggers LLM fallback when enabled.
  - If no keywords match, returns "general".
"""

from __future__ import annotations

from dataclasses import dataclass

# Weight multiplier for multi-word keyword phrases (2+ words).
# Multi-word phrases are more specific signals of intent, so they
# receive higher weight than single-word matches.
PHRASE_BOOST: int = 3

# Minimum confidence (0.0–1.0) required to trust keyword classification.
# Below this threshold, the LLM fallback is invoked if available.
CONFIDENCE_THRESHOLD: float = 0.4

# All valid legal domain labels for validation
VALID_DOMAINS: frozenset[str] = frozenset({
    "landlord_tenant",
    "employment_rights",
    "consumer_protection",
    "debt_collections",
    "small_claims",
    "contract_disputes",
    "traffic_violations",
    "family_law",
    "criminal_records",
    "immigration",
    "general",
})

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


@dataclass(frozen=True)
class ClassificationResult:
    """Result of legal domain classification with confidence metadata.

    Attributes:
        domain: The classified legal domain (e.g. 'landlord_tenant').
        confidence: Confidence score from 0.0 to 1.0 indicating how
            strongly the keyword signals point to this domain.
        method: Classification method used ('keyword' or 'llm_fallback').
        scores: Raw keyword scores for all matched domains (for debugging).
    """

    domain: str
    confidence: float
    method: str
    scores: dict[str, int]


def _compute_confidence(scores: dict[str, int]) -> float:
    """Compute a confidence score from domain keyword scores.

    Confidence is based on how dominant the top-scoring domain is
    relative to competing domains. A single strong match with no
    competition yields high confidence; multiple close scores yield low.

    The formula: top_score / (total_scores + 1) * domain_separation_factor

    Args:
        scores: Dict mapping domain names to their keyword scores.

    Returns:
        Confidence value between 0.0 and 1.0.
    """
    if not scores:
        return 0.0

    sorted_scores = sorted(scores.values(), reverse=True)
    top_score = sorted_scores[0]
    total_score = sum(sorted_scores)

    # Base ratio: how much of the total score belongs to the top domain
    base_ratio = top_score / total_score if total_score > 0 else 0.0

    # Separation factor: how far ahead is the top domain from runner-up
    if len(sorted_scores) >= 2:
        runner_up = sorted_scores[1]
        separation = (top_score - runner_up) / top_score if top_score > 0 else 0.0
    else:
        separation = 1.0  # Only one domain matched — high confidence

    # Combined confidence: average of dominance ratio and separation
    confidence = (base_ratio + separation) / 2.0

    # Boost confidence when top score is high in absolute terms
    if top_score >= 6:
        confidence = min(1.0, confidence + 0.15)

    return round(min(1.0, confidence), 3)


def classify_with_confidence(question: str) -> ClassificationResult:
    """Classify a user question and return confidence metadata.

    Performs weighted keyword matching and computes a confidence score
    indicating how strongly the classification signal is. This enables
    downstream consumers to decide whether to trust the classification
    or request LLM-based reclassification.

    Args:
        question: The user's question or message text.

    Returns:
        ClassificationResult with domain, confidence, method, and raw scores.

    Examples:
        >>> result = classify_with_confidence("my landlord kept my security deposit")
        >>> result.domain
        'landlord_tenant'
        >>> result.confidence > 0.5
        True
    """
    question_lower = question.lower()

    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(_keyword_weight(kw) for kw in keywords if kw in question_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return ClassificationResult(
            domain="general",
            confidence=0.0,
            method="keyword",
            scores={},
        )

    max_score = max(scores.values())
    top_domains = [d for d, s in scores.items() if s == max_score]

    if len(top_domains) == 1:
        domain = top_domains[0]
    else:
        # Tiebreaker: prefer the domain with the longest matching keyword
        domain = max(
            top_domains,
            key=lambda d: _longest_match_length(question_lower, DOMAIN_KEYWORDS[d]),
        )

    confidence = _compute_confidence(scores)

    return ClassificationResult(
        domain=domain,
        confidence=confidence,
        method="keyword",
        scores=scores,
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

    This is the simplified API that returns only the domain string.
    For confidence metadata, use classify_with_confidence() instead.

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
    return classify_with_confidence(question).domain


async def classify_with_llm_fallback(
    question: str,
    client: object | None = None,
) -> ClassificationResult:
    """Hybrid classifier: keyword-first with LLM fallback for low confidence.

    Attempts keyword classification first. If the confidence score falls
    below CONFIDENCE_THRESHOLD and an Anthropic client is available,
    delegates to Claude for more accurate classification of ambiguous queries.

    This hybrid approach handles 99%+ of queries via fast keywords while
    catching edge cases that keyword matching would misclassify.

    Args:
        question: The user's question or message text.
        client: Optional AsyncAnthropic client for LLM fallback.
            If None, falls back to keyword result regardless of confidence.

    Returns:
        ClassificationResult with the chosen domain and classification method.
    """
    keyword_result = classify_with_confidence(question)

    # If keyword confidence is high enough, use it directly
    if keyword_result.confidence >= CONFIDENCE_THRESHOLD:
        return keyword_result

    # If no client available, return keyword result even at low confidence
    if client is None:
        return keyword_result

    # LLM fallback for ambiguous queries
    try:
        import anthropic
        from anthropic.types import TextBlock

        if not isinstance(client, anthropic.AsyncAnthropic):
            return keyword_result

        domain_list = ", ".join(sorted(VALID_DOMAINS - {"general"}))
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            system=(
                "You are a legal domain classifier. Respond with ONLY the domain name, "
                "nothing else. Valid domains: " + domain_list + ". "
                "If the question doesn't fit any domain, respond with 'general'."
            ),
            messages=[{"role": "user", "content": question}],
        )

        first_block = response.content[0] if response.content else None
        llm_domain = first_block.text.strip().lower() if isinstance(first_block, TextBlock) else ""

        if llm_domain in VALID_DOMAINS:
            return ClassificationResult(
                domain=llm_domain,
                confidence=0.85,  # LLM classification assumed high confidence
                method="llm_fallback",
                scores=keyword_result.scores,
            )

    except Exception:
        pass  # LLM fallback failed — use keyword result

    return keyword_result
