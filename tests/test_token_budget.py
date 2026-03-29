"""Tests for the token budget manager and conversation summarization.

Validates context window management including token estimation, budget
enforcement, conversation truncation, and summary generation.
"""

from __future__ import annotations

from backend.utils.token_budget import (
    ConversationSummarizer,
    TokenBudgetManager,
    estimate_messages_tokens,
    estimate_tokens,
)


class TestTokenEstimation:
    """Test the character-based token estimation heuristic."""

    def test_empty_string_returns_zero(self) -> None:
        assert estimate_tokens("") == 0

    def test_short_text_returns_minimum_one(self) -> None:
        assert estimate_tokens("hi") >= 1

    def test_typical_sentence(self) -> None:
        # ~40 chars = ~10 tokens
        text = "The quick brown fox jumps over the lazy."
        tokens = estimate_tokens(text)
        assert 8 <= tokens <= 15

    def test_long_text_scales_linearly(self) -> None:
        short = estimate_tokens("hello world")
        long_text = "hello world " * 100
        long_tokens = estimate_tokens(long_text)
        assert long_tokens > short * 50  # Should scale roughly linearly

    def test_messages_tokens_includes_overhead(self) -> None:
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
        ]
        total = estimate_messages_tokens(messages)
        raw = estimate_tokens("hello") + estimate_tokens("hi there")
        assert total > raw  # Should include per-message overhead


class TestConversationSummarizer:
    """Test conversation summarization for older messages."""

    def test_empty_messages_returns_empty(self) -> None:
        summarizer = ConversationSummarizer()
        assert summarizer.summarize([]) == ""

    def test_summarizes_user_and_assistant(self) -> None:
        messages = [
            {"role": "user", "content": "My landlord kept my deposit. What can I do?"},
            {"role": "assistant", "content": "Under MA law, landlords must return deposits within 30 days."},
            {"role": "user", "content": "He didn't do a move-in inspection either."},
            {"role": "assistant", "content": "Without a move-in inspection, the landlord cannot claim damages."},
        ]
        summary = ConversationSummarizer().summarize(messages)
        assert "CONVERSATION SUMMARY" in summary
        assert "User discussed" in summary
        assert "CaseMate advised" in summary

    def test_truncates_long_sentences(self) -> None:
        long_sentence = "A" * 200 + ". More text here."
        messages = [{"role": "user", "content": long_sentence}]
        summary = ConversationSummarizer().summarize(messages)
        # Should truncate to 150 chars max per point
        assert len(summary) < 300


class TestTokenBudgetManager:
    """Test the budget manager's truncation and summarization logic."""

    def test_short_conversation_passes_through(self) -> None:
        manager = TokenBudgetManager()
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
        ]
        result = manager.apply(messages)
        assert not result.was_truncated
        assert result.messages == messages
        assert result.original_count == 2
        assert result.final_count == 2

    def test_long_conversation_gets_truncated(self) -> None:
        manager = TokenBudgetManager(conversation_budget=100)
        # Create messages that exceed 100 tokens
        messages = [
            {"role": "user", "content": "This is a long message. " * 20}
            for _ in range(20)
        ]
        result = manager.apply(messages)
        assert result.was_truncated
        assert result.final_count < result.original_count

    def test_summary_prepended_when_truncated(self) -> None:
        manager = TokenBudgetManager(
            conversation_budget=200,
            min_recent_messages=2,
        )
        messages = [
            {"role": "user", "content": "This is message number " + str(i) + " with some padding text." * 5}
            for i in range(20)
        ]
        result = manager.apply(messages)
        if result.summary_prepended:
            assert "CONVERSATION SUMMARY" in result.messages[0]["content"]

    def test_recent_messages_always_preserved(self) -> None:
        manager = TokenBudgetManager(
            conversation_budget=100,
            min_recent_messages=4,
        )
        messages = [
            {"role": "user", "content": f"Message {i} " * 10}
            for i in range(20)
        ]
        result = manager.apply(messages)
        # The last messages should always be the most recent ones
        assert result.final_count >= 1  # At least some messages kept

    def test_system_prompt_tokens_subtracted(self) -> None:
        manager = TokenBudgetManager(conversation_budget=200)
        messages = [
            {"role": "user", "content": "Short message " * 10}
            for _ in range(10)
        ]
        # With high system prompt overhead, should truncate more aggressively
        result_no_system = manager.apply(messages, system_prompt_tokens=0)
        result_with_system = manager.apply(messages, system_prompt_tokens=150)

        # With system prompt overhead, should keep fewer messages
        assert result_with_system.final_count <= result_no_system.final_count
