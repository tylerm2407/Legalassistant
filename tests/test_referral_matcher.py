"""Tests for the attorney referral matcher.

Verifies find_attorneys, get_referral_suggestions, and empty result
handling. All Supabase calls are mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.referrals.matcher import (
    Attorney,
    find_attorneys,
    get_referral_suggestions,
)

USER_ID = "user_test_referrals"

ATTORNEY_ROW = {
    "id": "att_1",
    "name": "Jane Smith, Esq.",
    "state": "MA",
    "specializations": ["landlord_tenant", "small_claims"],
    "rating": 4.5,
    "cost_range": "$200-$400/hr",
    "phone": "617-555-1234",
    "email": "jane@lawfirm.com",
    "website": "https://lawfirm.com",
    "accepts_free_consultations": True,
    "bio": "20 years of landlord-tenant experience in Boston.",
}


@pytest.fixture
def mock_supabase_referrals():
    """Patch _get_supabase for the referral matcher module."""
    mock_client = MagicMock()
    with patch("backend.referrals.matcher._get_supabase", return_value=mock_client):
        yield mock_client


class TestFindAttorneys:
    """Verify find_attorneys queries Supabase correctly."""

    async def test_returns_attorneys(self, mock_supabase_referrals: MagicMock) -> None:
        mock_supabase_referrals.table.return_value.select.return_value.eq.return_value.contains.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[ATTORNEY_ROW]
        )

        attorneys = await find_attorneys("MA", legal_area="landlord_tenant")
        assert len(attorneys) == 1
        assert attorneys[0].name == "Jane Smith, Esq."
        assert attorneys[0].state == "MA"

    async def test_returns_empty_on_error(self, mock_supabase_referrals: MagicMock) -> None:
        mock_supabase_referrals.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = Exception("DB error")

        attorneys = await find_attorneys("MA")
        assert attorneys == []

    async def test_empty_results(self, mock_supabase_referrals: MagicMock) -> None:
        mock_supabase_referrals.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        attorneys = await find_attorneys("WY")
        assert attorneys == []


class TestGetReferralSuggestions:
    """Verify get_referral_suggestions ranks attorneys correctly."""

    async def test_returns_ranked_suggestions(self, mock_supabase_referrals: MagicMock) -> None:
        # Mock find_attorneys indirectly through Supabase
        mock_supabase_referrals.table.return_value.select.return_value.eq.return_value.contains.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[ATTORNEY_ROW]
        )

        suggestions = await get_referral_suggestions(
            state="MA",
            legal_area="landlord_tenant",
            issue_summary="Security deposit dispute",
        )

        assert len(suggestions) == 1
        s = suggestions[0]
        assert s.attorney.name == "Jane Smith, Esq."
        assert s.relevance_score > 50  # Base + specialization + rating + consultation bonuses
        assert "Landlord Tenant" in s.match_reason
        assert "free consultations" in s.match_reason.lower()

    async def test_empty_when_no_attorneys(self, mock_supabase_referrals: MagicMock) -> None:
        mock_supabase_referrals.table.return_value.select.return_value.eq.return_value.contains.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        suggestions = await get_referral_suggestions(
            state="WY",
            legal_area="alien_law",
        )
        assert suggestions == []
