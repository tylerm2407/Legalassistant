"""Tests for the deadline tracker CRUD operations.

Verifies create, list, update, delete, and filtered listing of
legal deadlines. All Supabase calls are mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.deadlines.tracker import (
    DeadlineStatus,
    DeadlineUpdateRequest,
    create_deadline,
    delete_deadline,
    list_deadlines,
    update_deadline,
)

USER_ID = "user_test_deadlines"


@pytest.fixture
def mock_supabase_deadlines():
    """Patch _get_supabase for the deadline tracker module."""
    mock_client = MagicMock()
    with patch("backend.deadlines.tracker._get_supabase", return_value=mock_client):
        yield mock_client


class TestCreateDeadline:
    """Verify create_deadline inserts into Supabase and returns a Deadline."""

    async def test_creates_deadline_successfully(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=[{"id": "d1"}])
        )

        deadline = await create_deadline(
            user_id=USER_ID,
            title="File court answer",
            date="2026-04-15",
            legal_area="landlord_tenant",
            notes="Must file before deadline",
        )

        assert deadline.user_id == USER_ID
        assert deadline.title == "File court answer"
        assert deadline.date == "2026-04-15"
        assert deadline.legal_area == "landlord_tenant"
        assert deadline.status == DeadlineStatus.ACTIVE
        mock_supabase_deadlines.table.assert_called_with("deadlines")

    async def test_raises_on_insert_failure(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=None)
        )

        with pytest.raises(RuntimeError, match="Failed to create deadline"):
            await create_deadline(user_id=USER_ID, title="Test", date="2026-05-01")


class TestListDeadlines:
    """Verify list_deadlines returns parsed Deadline objects."""

    async def test_returns_deadlines(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "d1", "user_id": USER_ID, "title": "Court date", "date": "2026-04-10", "status": "active"},
                {"id": "d2", "user_id": USER_ID, "title": "Filing deadline", "date": "2026-04-20", "status": "active"},
            ]
        )

        deadlines = await list_deadlines(USER_ID)
        assert len(deadlines) == 2
        assert deadlines[0].title == "Court date"

    async def test_returns_empty_on_error(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("DB down")

        deadlines = await list_deadlines(USER_ID)
        assert deadlines == []

    async def test_filters_by_status(self, mock_supabase_deadlines: MagicMock) -> None:
        eq_mock = MagicMock()
        eq_mock.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"id": "d1", "user_id": USER_ID, "title": "Done", "date": "2026-04-01", "status": "completed"}]
        )
        mock_supabase_deadlines.table.return_value.select.return_value.eq.return_value = eq_mock

        deadlines = await list_deadlines(USER_ID, status=DeadlineStatus.COMPLETED)
        assert len(deadlines) == 1
        assert deadlines[0].status == DeadlineStatus.COMPLETED


class TestUpdateDeadline:
    """Verify update_deadline modifies and returns the updated Deadline."""

    async def test_updates_deadline(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "d1", "user_id": USER_ID, "title": "Updated title", "date": "2026-05-01", "status": "active"}]
        )

        result = await update_deadline(
            "d1", USER_ID, DeadlineUpdateRequest(title="Updated title")
        )
        assert result is not None
        assert result.title == "Updated title"

    async def test_returns_none_for_empty_updates(self, mock_supabase_deadlines: MagicMock) -> None:
        result = await update_deadline("d1", USER_ID, DeadlineUpdateRequest())
        assert result is None


class TestDeleteDeadline:
    """Verify delete_deadline removes a deadline and returns success flag."""

    async def test_deletes_existing_deadline(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "d1"}]
        )

        result = await delete_deadline("d1", USER_ID)
        assert result is True

    async def test_returns_false_when_not_found(self, mock_supabase_deadlines: MagicMock) -> None:
        mock_supabase_deadlines.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )

        result = await delete_deadline("nonexistent", USER_ID)
        assert result is False
