"""Tests for the profile auto-updater that extracts facts from conversations.

The updater runs as a background task after each conversation turn. It must
never crash the main request flow, so graceful error handling is critical.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models.legal_profile import LegalProfile


@pytest.fixture
def sample_conversation() -> list[dict[str, str]]:
    """A short conversation with extractable legal facts."""
    return [
        {
            "role": "user",
            "content": (
                "My landlord James Peterson hasn't returned my"
                " $2,400 deposit. I moved out on January 15."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "Under Massachusetts law, your landlord was required"
                " to return your deposit within 30 days."
            ),
        },
    ]


@pytest.fixture
def sample_profile() -> LegalProfile:
    """A minimal profile for the updater tests."""
    return LegalProfile(
        user_id="user_sarah_001",
        display_name="Sarah Chen",
        state="MA",
        housing_situation="renter",
        employment_type="employed",
        family_status="single",
        legal_facts=["Sarah paid a $2,400 security deposit on January 1, 2024"],
    )


class TestUpdateProfileExtractsNewFacts:
    """Verify that new facts from Claude are merged into the profile."""

    @pytest.mark.asyncio
    async def test_new_facts_added_to_profile(
        self, sample_conversation: list[dict[str, str]], sample_profile: LegalProfile
    ) -> None:
        new_facts = ["Move-out date was January 15, 2026", "Landlord name is James Peterson"]
        api_response_text = json.dumps({"new_facts": new_facts})

        content_block = MagicMock()
        content_block.text = api_response_text
        mock_response = MagicMock()
        mock_response.content = [content_block]

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
                return_value=sample_profile,
            ),
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            mock_update.assert_called_once()
            updated_profile = mock_update.call_args[0][0]
            assert "Move-out date was January 15, 2026" in updated_profile.legal_facts
            assert "Landlord name is James Peterson" in updated_profile.legal_facts


class TestUpdateProfileDeduplicatesFacts:
    """Verify that existing facts are not duplicated."""

    @pytest.mark.asyncio
    async def test_existing_facts_not_duplicated(
        self, sample_conversation: list[dict[str, str]], sample_profile: LegalProfile
    ) -> None:
        # Return a fact that already exists (case-insensitive match)
        duplicate_fact = "sarah paid a $2,400 security deposit on january 1, 2024"
        new_fact = "The apartment is at 45 Beacon St"
        api_response_text = json.dumps({"new_facts": [duplicate_fact, new_fact]})

        content_block = MagicMock()
        content_block.text = api_response_text
        mock_response = MagicMock()
        mock_response.content = [content_block]

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
                return_value=sample_profile,
            ),
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            mock_update.assert_called_once()
            updated_profile = mock_update.call_args[0][0]
            # The original fact should still be there exactly once
            original_count = sum(
                1
                for f in updated_profile.legal_facts
                if f.lower().strip() == "sarah paid a $2,400 security deposit on january 1, 2024"
            )
            assert original_count == 1
            # The new unique fact should be added
            assert "The apartment is at 45 Beacon St" in updated_profile.legal_facts


class TestUpdateProfileHandlesApiError:
    """Verify graceful handling when the Anthropic API fails."""

    @pytest.mark.asyncio
    async def test_api_error_does_not_crash(
        self, sample_conversation: list[dict[str, str]]
    ) -> None:
        import anthropic

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.APIError(
                message="Service unavailable",
                request=MagicMock(),
                body=None,
            )
        )

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            # Should not raise — errors are caught and logged
            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            # Profile should never have been fetched or updated
            mock_get.assert_not_called()
            mock_update.assert_not_called()


class TestUpdateProfileHandlesEmptyResponse:
    """Verify no crash when Claude returns no new facts."""

    @pytest.mark.asyncio
    async def test_empty_facts_list(
        self, sample_conversation: list[dict[str, str]], sample_profile: LegalProfile
    ) -> None:
        api_response_text = json.dumps({"new_facts": []})

        content_block = MagicMock()
        content_block.text = api_response_text
        mock_response = MagicMock()
        mock_response.content = [content_block]

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            # No facts extracted means no profile fetch or update needed
            mock_get.assert_not_called()
            mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_malformed_json_response(
        self, sample_conversation: list[dict[str, str]]
    ) -> None:
        content_block = MagicMock()
        content_block.text = "This is not JSON at all"
        mock_response = MagicMock()
        mock_response.content = [content_block]

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            # Should not raise
            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            mock_get.assert_not_called()
            mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_content_response(
        self, sample_conversation: list[dict[str, str]]
    ) -> None:
        mock_response = MagicMock()
        mock_response.content = []  # No content blocks at all

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("anthropic.AsyncAnthropic", return_value=mock_client),
            patch(
                "backend.memory.updater.get_profile",
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                "backend.memory.updater.update_profile",
                new_callable=AsyncMock,
            ) as mock_update,
        ):
            from backend.memory.updater import update_profile_from_conversation

            # Should not raise
            await update_profile_from_conversation("user_sarah_001", sample_conversation)

            mock_get.assert_not_called()
            mock_update.assert_not_called()
