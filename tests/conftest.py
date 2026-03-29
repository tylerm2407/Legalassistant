"""Shared pytest fixtures for the CaseMate test suite.

Provides reusable fixtures for a mock legal profile, patched Anthropic
client, and patched Supabase client so tests never hit real APIs.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models.legal_profile import IssueStatus, LegalIssue, LegalProfile


@pytest.fixture
def mock_profile() -> LegalProfile:
    """Return a LegalProfile for Sarah Chen — a MA renter with a landlord_tenant issue."""
    return LegalProfile(
        user_id="user_sarah_001",
        display_name="Sarah Chen",
        state="MA",
        housing_situation="renter, apartment in Boston, lease expires June 2026",
        employment_type="full-time W-2 employee",
        family_status="single, no dependents",
        active_issues=[
            LegalIssue(
                issue_type="landlord_tenant",
                summary=(
                    "Landlord has not returned $2,400 security deposit after move-out 45 days ago"
                ),
                status=IssueStatus.OPEN,
                started_at=datetime(2026, 2, 1),
                updated_at=datetime(2026, 3, 15),
                notes=[
                    "Move-out date was January 15, 2026",
                    "Deposit was $2,400 for a one-bedroom apartment",
                    "Landlord has not provided an itemized deduction list",
                ],
            ),
        ],
        legal_facts=[
            "Sarah paid a $2,400 security deposit on January 1, 2024",
            "The lease was a standard 1-year lease renewed once",
            "Sarah has photos of the apartment in move-out condition",
            "The landlord's name is James Peterson",
            "The property address is 45 Beacon St, Boston, MA 02108",
            "Sarah sent a written request for the deposit on February 20, 2026",
            "No itemized deduction statement was received",
            "Sarah has all rent payment receipts from 2024-2026",
        ],
        documents=["move_out_photos.zip", "lease_agreement.pdf"],
        member_since=datetime(2026, 1, 10),
        conversation_count=12,
    )


@pytest.fixture
def mock_anthropic_response():
    """Factory fixture that builds a mock Anthropic messages.create response.

    Returns a callable: pass the text you want Claude to "return" and get
    back a properly shaped mock response object.
    """

    def _make_response(text: str) -> MagicMock:
        content_block = MagicMock()
        content_block.text = text
        response = MagicMock()
        response.content = [content_block]
        return response

    return _make_response


@pytest.fixture
def mock_anthropic(mock_anthropic_response):
    """Patch anthropic.AsyncAnthropic so no real API calls are made.

    The mock client's messages.create is an AsyncMock that returns a
    default JSON response. Tests can override the return value via:
        mock_anthropic.messages.create.return_value = mock_anthropic_response("...")
    """
    mock_client = MagicMock()
    mock_create = AsyncMock(return_value=mock_anthropic_response(json.dumps({"new_facts": []})))
    mock_client.messages = MagicMock()
    mock_client.messages.create = mock_create

    with patch("anthropic.AsyncAnthropic", return_value=mock_client) as patcher:
        patcher._mock_client = mock_client  # expose for tests
        yield mock_client


@pytest.fixture
def mock_supabase():
    """Patch the Supabase client used by backend.memory.profile.

    Returns a MagicMock that intercepts all table().select()... and
    table().upsert()... call chains.
    """
    mock_client = MagicMock()

    # Default: select returns None (no profile found)
    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=None)
    (
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value
    ) = select_chain

    # Default: upsert returns empty list
    upsert_chain = MagicMock()
    upsert_chain.execute.return_value = MagicMock(data=[])
    mock_client.table.return_value.upsert.return_value = upsert_chain

    with patch("backend.memory.profile._get_supabase", return_value=mock_client):
        yield mock_client
