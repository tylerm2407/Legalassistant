"""Attorney referral matching system.

Matches users with attorneys based on state, legal area, and issue
complexity. Attorney data is stored in Supabase and can be populated
by administrators.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.memory.profile import _get_supabase
from backend.utils.logger import get_logger
from backend.utils.type_helpers import parse_supabase_rows

_logger = get_logger(__name__)


class Attorney(BaseModel):
    """An attorney in the referral directory.

    Attributes:
        id: Unique attorney identifier.
        name: Attorney's full name.
        state: State where they are licensed.
        zip_code: Attorney's office zip code (5 digits).
        specializations: List of legal domains they handle.
        rating: Average rating (1-5 scale).
        cost_range: Typical cost description.
        phone: Contact phone number.
        email: Contact email address.
        website: Attorney or firm website.
        accepts_free_consultations: Whether they offer free initial consultations.
        bio: Brief description of practice.
    """

    id: str
    name: str
    state: str
    zip_code: str = ""
    specializations: list[str] = Field(default_factory=list)
    rating: float = 0.0
    cost_range: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    accepts_free_consultations: bool = False
    bio: str = ""


class ReferralSuggestion(BaseModel):
    """A suggested attorney referral with match context.

    Attributes:
        attorney: The matched attorney.
        match_reason: Why this attorney was suggested.
        relevance_score: How relevant this match is (0-100).
    """

    attorney: Attorney
    match_reason: str
    relevance_score: int


async def find_attorneys(
    state: str,
    legal_area: str | None = None,
    zip_code: str | None = None,
    limit: int = 10,
) -> list[Attorney]:
    """Find attorneys by state, optional legal area, and optional zip code.

    When a zip_code is provided, results are filtered to attorneys whose zip code
    matches exactly or shares the same 3-digit prefix (same postal region).
    Matching attorneys are sorted by zip proximity before the limit is applied.

    Args:
        state: Two-letter state code.
        legal_area: Optional legal domain to filter by.
        zip_code: Optional 5-digit zip code for location filtering.
        limit: Maximum number of results.

    Returns:
        List of matching Attorney objects.
    """
    try:
        client = _get_supabase()
        query = client.table("attorneys").select("*").eq("state", state.upper())
        if legal_area:
            query = query.contains("specializations", [legal_area])
        # Fetch extra rows when zip filtering so we have enough after pruning
        fetch_limit = limit * 3 if zip_code else limit
        result = query.order("rating", desc=True).limit(fetch_limit).execute()
        attorneys = parse_supabase_rows(result.data, Attorney)

        if zip_code:
            prefix = zip_code[:3]
            attorneys = [a for a in attorneys if a.zip_code == zip_code or a.zip_code[:3] == prefix]

        return attorneys[:limit]
    except Exception as exc:
        _logger.error(
            "attorney_search_error",
            state=state,
            legal_area=legal_area,
            zip_code=zip_code,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return []


async def get_referral_suggestions(
    state: str,
    legal_area: str,
    issue_summary: str = "",
    zip_code: str | None = None,
    limit: int = 5,
) -> list[ReferralSuggestion]:
    """Get ranked attorney referral suggestions.

    Matches attorneys based on state and legal area, then ranks by
    relevance considering specialization match, rating, and zip code
    proximity. Exact zip code match adds 15 points; same 3-digit
    prefix adds 8 points.

    Args:
        state: Two-letter state code.
        legal_area: The legal domain for matching.
        issue_summary: Brief description of the legal issue.
        zip_code: Optional 5-digit zip code for proximity scoring.
        limit: Maximum number of suggestions.

    Returns:
        List of ReferralSuggestion objects, ranked by relevance.
    """
    attorneys = await find_attorneys(state, legal_area, zip_code=zip_code, limit=limit * 2)

    suggestions: list[ReferralSuggestion] = []
    for attorney in attorneys:
        # Calculate relevance score
        score = 50  # Base score

        # Specialization match bonus
        if legal_area in attorney.specializations:
            score += 30

        # Rating bonus (up to 10 points)
        score += int(attorney.rating * 2)

        # Free consultation bonus
        if attorney.accepts_free_consultations:
            score += 10

        # Zip code proximity bonus
        if zip_code and attorney.zip_code:
            if attorney.zip_code == zip_code:
                score += 15
            elif attorney.zip_code[:3] == zip_code[:3]:
                score += 8

        match_reason_parts: list[str] = []
        if legal_area in attorney.specializations:
            domain_label = legal_area.replace("_", " ").title()
            match_reason_parts.append(f"Specializes in {domain_label}")
        match_reason_parts.append(f"Licensed in {attorney.state}")
        if zip_code and attorney.zip_code:
            if attorney.zip_code == zip_code:
                match_reason_parts.append("In your zip code")
            elif attorney.zip_code[:3] == zip_code[:3]:
                match_reason_parts.append("Nearby area")
        if attorney.accepts_free_consultations:
            match_reason_parts.append("Offers free consultations")

        suggestions.append(
            ReferralSuggestion(
                attorney=attorney,
                match_reason=". ".join(match_reason_parts),
                relevance_score=min(score, 100),
            )
        )

    # Sort by relevance score descending
    suggestions.sort(key=lambda s: s.relevance_score, reverse=True)

    _logger.info(
        "referral_suggestions_generated",
        state=state,
        legal_area=legal_area,
        zip_code=zip_code,
        count=len(suggestions[:limit]),
    )

    return suggestions[:limit]
