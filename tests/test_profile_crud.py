"""Tests for backend.memory.profile — Supabase-backed profile CRUD.

Covers get_profile (found, not found, config error, generic error)
and update_profile (success, empty upsert, config error, generic error).
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.memory.profile import get_profile, update_profile
from backend.models.legal_profile import LegalProfile


@pytest.fixture
def sample_profile_data() -> dict:
    """Return a dict matching the shape Supabase would return for a profile row."""
    return {
        "user_id": "user_test_001",
        "display_name": "Test User",
        "state": "MA",
        "housing_situation": "renter",
        "employment_type": "full-time W-2",
        "family_status": "single",
        "active_issues": [],
        "legal_facts": ["Test fact one"],
        "documents": [],
        "member_since": "2026-01-01T00:00:00",
        "conversation_count": 0,
    }


@pytest.fixture
def sample_profile(sample_profile_data: dict) -> LegalProfile:
    """Return a LegalProfile instance for upsert tests."""
    return LegalProfile.model_validate(sample_profile_data)


# ---------- get_profile ----------


@pytest.mark.asyncio
async def test_get_profile_found(mock_supabase: MagicMock, sample_profile_data: dict) -> None:
    """Returns a LegalProfile when the user exists in Supabase."""
    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=sample_profile_data)
    (
        mock_supabase.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
    ) = select_chain

    result = await get_profile("user_test_001")
    assert result is not None
    assert result.user_id == "user_test_001"
    assert result.state == "MA"


@pytest.mark.asyncio
async def test_get_profile_not_found(mock_supabase: MagicMock) -> None:
    """Returns None when no profile exists for the user_id."""
    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=None)
    (
        mock_supabase.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
    ) = select_chain

    result = await get_profile("nonexistent_user")
    assert result is None


@pytest.mark.asyncio
async def test_get_profile_config_error() -> None:
    """Raises ValueError when Supabase env vars are missing."""
    with patch("backend.memory.profile._get_supabase", side_effect=ValueError("missing env")):
        with pytest.raises(ValueError, match="missing env"):
            await get_profile("user_test_001")


@pytest.mark.asyncio
async def test_get_profile_generic_error(mock_supabase: MagicMock) -> None:
    """Returns None on unexpected Supabase errors (logged, not raised)."""
    mock_supabase.table.side_effect = RuntimeError("connection lost")

    result = await get_profile("user_test_001")
    assert result is None


# ---------- update_profile ----------


@pytest.mark.asyncio
async def test_update_profile_success(
    mock_supabase: MagicMock,
    sample_profile: LegalProfile,
    sample_profile_data: dict,
) -> None:
    """Returns the updated LegalProfile on successful upsert."""
    upsert_chain = MagicMock()
    upsert_chain.execute.return_value = MagicMock(data=[sample_profile_data])
    mock_supabase.table.return_value.upsert.return_value = upsert_chain

    result = await update_profile(sample_profile)
    assert result.user_id == "user_test_001"
    assert result.state == "MA"


@pytest.mark.asyncio
async def test_update_profile_empty_response(
    mock_supabase: MagicMock,
    sample_profile: LegalProfile,
) -> None:
    """Raises RuntimeError when upsert returns no data."""
    upsert_chain = MagicMock()
    upsert_chain.execute.return_value = MagicMock(data=[])
    mock_supabase.table.return_value.upsert.return_value = upsert_chain

    with pytest.raises(RuntimeError, match="Upsert returned no data"):
        await update_profile(sample_profile)


@pytest.mark.asyncio
async def test_update_profile_config_error(sample_profile: LegalProfile) -> None:
    """Raises ValueError when Supabase env vars are missing."""
    with patch("backend.memory.profile._get_supabase", side_effect=ValueError("missing env")):
        with pytest.raises(ValueError, match="missing env"):
            await update_profile(sample_profile)


@pytest.mark.asyncio
async def test_update_profile_generic_error(
    mock_supabase: MagicMock,
    sample_profile: LegalProfile,
) -> None:
    """Raises RuntimeError wrapping the original exception on generic failure."""
    mock_supabase.table.side_effect = ConnectionError("db down")

    with pytest.raises(RuntimeError, match="Failed to update profile"):
        await update_profile(sample_profile)
