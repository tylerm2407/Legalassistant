"""Tests for the conversation store CRUD operations.

Verifies create, get, list, save, and delete of conversations
with all Supabase calls mocked.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.memory.conversation_store import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    save_conversation,
)
from backend.models.conversation import Conversation

USER_ID = "user_test_conversations"


@pytest.fixture
def mock_supabase_conversations():
    """Patch _get_supabase for the conversation store module."""
    mock_client = MagicMock()
    with patch("backend.memory.conversation_store._get_supabase", return_value=mock_client):
        yield mock_client


class TestCreateConversation:
    """Verify create_conversation inserts and returns a Conversation."""

    async def test_creates_conversation(self, mock_supabase_conversations: MagicMock) -> None:
        mock_supabase_conversations.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=[{"id": "c1"}])
        )

        conv = await create_conversation(USER_ID, legal_area="landlord_tenant")
        assert conv.user_id == USER_ID
        assert conv.legal_area == "landlord_tenant"
        assert conv.messages == []
        mock_supabase_conversations.table.assert_called_with("conversations")

    async def test_raises_on_failure(self, mock_supabase_conversations: MagicMock) -> None:
        mock_supabase_conversations.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=None)
        )

        with pytest.raises(RuntimeError, match="Failed to create conversation"):
            await create_conversation(USER_ID)


class TestGetConversation:
    """Verify get_conversation fetches and parses a conversation."""

    async def test_returns_conversation(self, mock_supabase_conversations: MagicMock) -> None:
        now = datetime.now(UTC).isoformat()
        mock_result = MagicMock()
        mock_result.data = {
            "id": "c1",
            "user_id": USER_ID,
            "messages": [
                {"role": "user", "content": "Help with my lease", "timestamp": now},
                {"role": "assistant", "content": "I can help with that.", "timestamp": now},
            ],
            "legal_area": "landlord_tenant",
            "created_at": now,
            "updated_at": now,
        }
        (
            mock_supabase_conversations.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = mock_result

        conv = await get_conversation("c1", USER_ID)
        assert conv is not None
        assert conv.id == "c1"
        assert len(conv.messages) == 2
        assert conv.messages[0].role == "user"

    async def test_returns_none_when_not_found(
        self, mock_supabase_conversations: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.data = None
        (
            mock_supabase_conversations.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = mock_result

        conv = await get_conversation("nonexistent", USER_ID)
        assert conv is None


class TestListConversations:
    """Verify list_conversations returns summary dicts."""

    async def test_returns_summaries(self, mock_supabase_conversations: MagicMock) -> None:
        now = datetime.now(UTC).isoformat()
        mock_supabase_conversations.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "c1",
                    "legal_area": "landlord_tenant",
                    "updated_at": now,
                    "messages": [
                        {"role": "user", "content": "My landlord won't return my deposit"}
                    ],
                },
            ]
        )

        summaries = await list_conversations(USER_ID)
        assert len(summaries) == 1
        assert summaries[0]["id"] == "c1"
        assert summaries[0]["message_count"] == 1
        assert "deposit" in summaries[0]["preview"]


class TestSaveConversation:
    """Verify save_conversation persists messages to Supabase."""

    async def test_saves_conversation(self, mock_supabase_conversations: MagicMock) -> None:
        conv = Conversation(id="c1", user_id=USER_ID, legal_area="landlord_tenant")
        conv.add_message("user", "My landlord is withholding my deposit")

        mock_supabase_conversations.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{}]
        )

        # Should not raise
        await save_conversation(conv)
        mock_supabase_conversations.table.assert_called_with("conversations")

    async def test_raises_on_save_failure(self, mock_supabase_conversations: MagicMock) -> None:
        conv = Conversation(id="c1", user_id=USER_ID)
        mock_supabase_conversations.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "DB error"
        )

        with pytest.raises(RuntimeError, match="Failed to save conversation"):
            await save_conversation(conv)


class TestDeleteConversation:
    """Verify delete_conversation removes and returns success flag."""

    async def test_deletes_existing(self, mock_supabase_conversations: MagicMock) -> None:
        mock_supabase_conversations.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "c1"}]
        )

        result = await delete_conversation("c1", USER_ID)
        assert result is True

    async def test_returns_false_when_not_found(
        self, mock_supabase_conversations: MagicMock
    ) -> None:
        mock_supabase_conversations.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )

        result = await delete_conversation("nonexistent", USER_ID)
        assert result is False
