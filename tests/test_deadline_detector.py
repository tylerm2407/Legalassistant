"""Tests for the deadline detector — auto-detects deadlines from conversations.

Verifies that detect_and_save_deadlines correctly parses Claude responses,
creates deadlines on success, and handles failures gracefully.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.deadlines.detector import detect_and_save_deadlines

USER_ID = "user_test_detector"


@pytest.fixture
def mock_detector_deps():
    """Patch both the Anthropic client and create_deadline for detector tests."""
    mock_client = MagicMock()
    mock_create = AsyncMock()

    with (
        patch("backend.deadlines.detector.get_anthropic_client", return_value=mock_client),
        patch("backend.deadlines.detector.create_deadline", new=mock_create),
    ):
        yield mock_client, mock_create


class TestDetectAndSaveDeadlines:
    """Verify detect_and_save_deadlines end-to-end behavior."""

    async def test_detects_and_saves_deadlines(self, mock_detector_deps: tuple) -> None:
        mock_client, mock_create = mock_detector_deps

        response_data = {
            "deadlines": [
                {
                    "title": "Statute of limitations expires",
                    "date": "2026-06-01",
                    "legal_area": "landlord_tenant",
                    "notes": "30-day window for deposit claim",
                }
            ]
        }
        content_block = MagicMock()
        content_block.text = json.dumps(response_data)
        # Make isinstance check work for TextBlock
        from anthropic.types import TextBlock

        content_block.__class__ = TextBlock

        mock_response = MagicMock()
        mock_response.content = [content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        conversation = [{"role": "user", "content": "My landlord won't return my deposit"}]
        await detect_and_save_deadlines(USER_ID, conversation, conversation_id="conv_1")

        mock_create.assert_called_once_with(
            user_id=USER_ID,
            title="Statute of limitations expires",
            date="2026-06-01",
            legal_area="landlord_tenant",
            source_conversation_id="conv_1",
            notes="30-day window for deposit claim",
        )

    async def test_handles_detection_failure_gracefully(self, mock_detector_deps: tuple) -> None:
        mock_client, mock_create = mock_detector_deps

        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))

        conversation = [{"role": "user", "content": "Help with my lease"}]
        # Should not raise — errors are caught and logged
        await detect_and_save_deadlines(USER_ID, conversation)
        mock_create.assert_not_called()

    async def test_no_deadlines_detected(self, mock_detector_deps: tuple) -> None:
        mock_client, mock_create = mock_detector_deps

        response_data = {"deadlines": []}
        content_block = MagicMock()
        content_block.text = json.dumps(response_data)
        from anthropic.types import TextBlock

        content_block.__class__ = TextBlock

        mock_response = MagicMock()
        mock_response.content = [content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        conversation = [{"role": "user", "content": "Hello"}]
        await detect_and_save_deadlines(USER_ID, conversation)
        mock_create.assert_not_called()
