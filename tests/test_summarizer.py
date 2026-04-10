"""Tests for the LLM-powered conversation summarizer.

Tests cover the ConversationSummary model, serialization, prompt block
formatting, the fallback summarizer, and the summarize_if_needed gate.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import TextBlock

from backend.memory.summarizer import (
    SUMMARY_THRESHOLD,
    ConversationSummary,
    _fallback_summary,
    _format_conversation_for_summary,
    _safe_str_list,
    generate_summary,
    needs_summarization,
    summarize_if_needed,
)

# ---------------------------------------------------------------------------
# ConversationSummary model tests
# ---------------------------------------------------------------------------


class TestConversationSummary:
    """Tests for the ConversationSummary data class."""

    def test_default_construction(self) -> None:
        """Empty summary has sensible defaults."""
        summary = ConversationSummary()
        assert summary.topics == []
        assert summary.user_facts == []
        assert summary.statutes_cited == []
        assert summary.advice_given == []
        assert summary.action_items == []
        assert summary.unresolved_questions == []
        assert summary.narrative == ""
        assert summary.message_count == 0

    def test_construction_with_data(self) -> None:
        """Summary populated with data preserves all fields."""
        summary = ConversationSummary(
            topics=["security deposit"],
            user_facts=["Landlord did not do move-in inspection"],
            statutes_cited=["M.G.L. c.186 §15B"],
            advice_given=["You may be entitled to 3x damages"],
            action_items=["Send demand letter"],
            unresolved_questions=["Did you take move-in photos?"],
            narrative="User discussed security deposit dispute in MA.",
            message_count=12,
        )
        assert summary.topics == ["security deposit"]
        assert summary.message_count == 12
        assert "M.G.L. c.186 §15B" in summary.statutes_cited

    def test_to_prompt_block_includes_all_sections(self) -> None:
        """Prompt block contains all non-empty sections."""
        summary = ConversationSummary(
            topics=["eviction"],
            user_facts=["Tenant in MA"],
            statutes_cited=["M.G.L. c.239 §1"],
            advice_given=["File answer within 20 days"],
            action_items=["Contact legal aid"],
            unresolved_questions=["What type of notice?"],
            narrative="Eviction defense discussion.",
            message_count=8,
        )
        block = summary.to_prompt_block()
        assert "8 earlier messages compressed" in block
        assert "Eviction defense discussion" in block
        assert "Tenant in MA" in block
        assert "M.G.L. c.239 §1" in block
        assert "File answer within 20 days" in block
        assert "Contact legal aid" in block
        assert "What type of notice?" in block

    def test_to_prompt_block_empty_summary(self) -> None:
        """Prompt block from empty summary still has header."""
        summary = ConversationSummary()
        block = summary.to_prompt_block()
        assert "CONVERSATION SUMMARY" in block

    def test_serialization_roundtrip(self) -> None:
        """Summary survives to_dict → from_dict roundtrip."""
        original = ConversationSummary(
            topics=["wage theft"],
            user_facts=["Employer withheld $2,000"],
            statutes_cited=["29 U.S.C. §206"],
            advice_given=["File with DOL"],
            action_items=["Gather pay stubs"],
            unresolved_questions=[],
            narrative="Wage dispute case.",
            message_count=15,
        )
        data = original.to_dict()
        restored = ConversationSummary.from_dict(data)
        assert restored.topics == original.topics
        assert restored.user_facts == original.user_facts
        assert restored.statutes_cited == original.statutes_cited
        assert restored.narrative == original.narrative
        assert restored.message_count == original.message_count

    def test_from_dict_handles_missing_fields(self) -> None:
        """from_dict works with partial or empty data."""
        summary = ConversationSummary.from_dict({})
        assert summary.topics == []
        assert summary.narrative == ""
        assert summary.message_count == 0

    def test_from_dict_handles_invalid_types(self) -> None:
        """from_dict handles non-list values gracefully."""
        summary = ConversationSummary.from_dict(
            {
                "topics": "not a list",
                "user_facts": 42,
                "message_count": "10",
            }
        )
        assert summary.topics == []
        assert summary.user_facts == []
        assert summary.message_count == 10


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for helper functions."""

    def test_safe_str_list_with_valid_list(self) -> None:
        """Converts list elements to strings."""
        assert _safe_str_list(["a", "b", "c"]) == ["a", "b", "c"]

    def test_safe_str_list_with_none(self) -> None:
        """Returns empty list for None."""
        assert _safe_str_list(None) == []

    def test_safe_str_list_with_non_list(self) -> None:
        """Returns empty list for non-list values."""
        assert _safe_str_list("string") == []
        assert _safe_str_list(42) == []

    def test_safe_str_list_filters_empty(self) -> None:
        """Filters out empty/falsy values."""
        assert _safe_str_list(["a", "", None, "b"]) == ["a", "b"]

    def test_needs_summarization_below_threshold(self) -> None:
        """Returns False for short conversations."""
        messages = [{"role": "user", "content": "hi"}] * (SUMMARY_THRESHOLD - 1)
        assert needs_summarization(messages) is False

    def test_needs_summarization_at_threshold(self) -> None:
        """Returns True at exactly the threshold."""
        messages = [{"role": "user", "content": "hi"}] * SUMMARY_THRESHOLD
        assert needs_summarization(messages) is True

    def test_needs_summarization_above_threshold(self) -> None:
        """Returns True above threshold."""
        messages = [{"role": "user", "content": "hi"}] * (SUMMARY_THRESHOLD + 5)
        assert needs_summarization(messages) is True

    def test_format_conversation_for_summary(self) -> None:
        """Formats messages into a readable transcript."""
        messages = [
            {"role": "user", "content": "My landlord won't return my deposit."},
            {"role": "assistant", "content": "Under M.G.L. c.186 §15B, your landlord must..."},
        ]
        result = _format_conversation_for_summary(messages)
        assert "User: My landlord" in result
        assert "CaseMate: Under M.G.L." in result

    def test_format_conversation_truncates_long_messages(self) -> None:
        """Very long messages are truncated in the transcript."""
        messages = [{"role": "user", "content": "x" * 2000}]
        result = _format_conversation_for_summary(messages)
        assert "[truncated]" in result
        assert len(result) < 2000


# ---------------------------------------------------------------------------
# Fallback summarizer tests
# ---------------------------------------------------------------------------


class TestFallbackSummary:
    """Tests for the naive fallback summarizer."""

    def test_fallback_with_messages(self) -> None:
        """Fallback extracts first sentences from messages."""
        messages = [
            {"role": "user", "content": "I got evicted. The landlord gave me 3 days."},
            {
                "role": "assistant",
                "content": "In your state, the minimum notice period is 30 days.",
            },
            {"role": "user", "content": "Can I fight this? I paid rent on time."},
        ]
        summary = _fallback_summary(messages)
        assert summary.message_count == 3
        assert len(summary.user_facts) == 2
        assert len(summary.advice_given) == 1
        assert "fallback" in summary.narrative.lower()

    def test_fallback_with_empty_messages(self) -> None:
        """Fallback returns empty summary for no messages."""
        summary = _fallback_summary([])
        assert summary.message_count == 0
        assert summary.user_facts == []

    def test_fallback_truncates_long_sentences(self) -> None:
        """Fallback truncates sentences longer than 150 chars."""
        messages = [{"role": "user", "content": "A" * 200 + ". Second sentence."}]
        summary = _fallback_summary(messages)
        assert all(len(fact) <= 150 for fact in summary.user_facts)


# ---------------------------------------------------------------------------
# LLM-powered summarizer tests (mocked)
# ---------------------------------------------------------------------------


class TestGenerateSummary:
    """Tests for the LLM-powered generate_summary function."""

    @pytest.mark.asyncio
    async def test_generate_summary_parses_valid_response(self) -> None:
        """Successfully parses a well-formed Claude response."""
        mock_response = MagicMock()
        mock_response.content = [
            TextBlock(
                type="text",
                text=json.dumps(
                    {
                        "topics": ["security deposit"],
                        "user_facts": ["Landlord did not inspect"],
                        "statutes_cited": ["M.G.L. c.186 §15B"],
                        "advice_given": ["Send demand letter"],
                        "action_items": ["Write letter by Friday"],
                        "unresolved_questions": [],
                        "narrative": "Deposit dispute in Massachusetts.",
                    }
                ),
            )
        ]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.memory.summarizer.get_anthropic_client", return_value=mock_client):
            messages = [
                {"role": "user", "content": "My landlord won't return my deposit."},
                {"role": "assistant", "content": "Under MA law..."},
            ]
            summary = await generate_summary(messages)

        assert summary.topics == ["security deposit"]
        assert summary.statutes_cited == ["M.G.L. c.186 §15B"]
        assert summary.message_count == 2
        assert "Massachusetts" in summary.narrative

    @pytest.mark.asyncio
    async def test_generate_summary_falls_back_on_invalid_json(self) -> None:
        """Falls back to naive extraction when Claude returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = [TextBlock(type="text", text="This is not valid JSON")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.memory.summarizer.get_anthropic_client", return_value=mock_client):
            messages = [
                {"role": "user", "content": "Question about rent."},
                {"role": "assistant", "content": "The law says..."},
            ]
            summary = await generate_summary(messages)

        assert summary.message_count == 2
        assert "fallback" in summary.narrative.lower()

    @pytest.mark.asyncio
    async def test_generate_summary_empty_messages(self) -> None:
        """Returns empty summary for no messages without calling API."""
        summary = await generate_summary([])
        assert summary.message_count == 0
        assert summary.topics == []


# ---------------------------------------------------------------------------
# summarize_if_needed gate tests
# ---------------------------------------------------------------------------


class TestSummarizeIfNeeded:
    """Tests for the conditional summarization gate."""

    @pytest.mark.asyncio
    async def test_skips_short_conversations(self) -> None:
        """Does not summarize conversations below threshold."""
        messages = [{"role": "user", "content": "hi"}] * 3
        result = await summarize_if_needed(messages)
        assert result is None

    @pytest.mark.asyncio
    async def test_skips_when_summary_is_current(self) -> None:
        """Does not re-summarize when existing summary covers all messages."""
        messages = [{"role": "user", "content": "hi"}] * 12
        existing = ConversationSummary(message_count=12).to_dict()
        result = await summarize_if_needed(messages, existing_summary=existing)
        assert result is None

    @pytest.mark.asyncio
    async def test_summarizes_when_new_messages_exist(self) -> None:
        """Generates new summary when conversation has grown past existing summary."""
        messages = [{"role": "user", "content": "Question about my case."}] * 15

        existing = ConversationSummary(message_count=10).to_dict()

        mock_response = MagicMock()
        mock_response.content = [
            TextBlock(
                type="text",
                text=json.dumps(
                    {
                        "topics": ["case discussion"],
                        "user_facts": [],
                        "statutes_cited": [],
                        "advice_given": [],
                        "action_items": [],
                        "unresolved_questions": [],
                        "narrative": "Extended case discussion.",
                    }
                ),
            )
        ]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.memory.summarizer.get_anthropic_client", return_value=mock_client):
            result = await summarize_if_needed(messages, existing_summary=existing)

        assert result is not None
        assert result.message_count == 15

    @pytest.mark.asyncio
    async def test_falls_back_on_api_error(self) -> None:
        """Uses fallback summary when the API call raises an exception."""
        messages = [{"role": "user", "content": "Legal question."}] * 12

        with patch(
            "backend.memory.summarizer.generate_summary",
            side_effect=Exception("API unavailable"),
        ):
            result = await summarize_if_needed(messages)

        assert result is not None
        assert result.message_count == 12
        assert "fallback" in result.narrative.lower()
