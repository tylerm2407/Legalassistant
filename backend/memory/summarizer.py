"""LLM-powered conversation summarizer for intelligent context compression.

When conversations grow long, naive truncation loses critical legal facts,
statute citations, and action items. This module uses Claude to generate
structured summaries that preserve the legally relevant information while
dramatically reducing token usage.

The summarizer is designed to run as a background task after each conversation
turn, storing the summary in the conversation record. The TokenBudgetManager
then uses the stored summary instead of doing naive first-sentence extraction.

This is part of CaseMate's core memory system — the compounding effect only
works if context is preserved intelligently, not just dropped.
"""

from __future__ import annotations

import json
from typing import cast

from anthropic.types import MessageParam, TextBlock

from backend.utils.client import get_anthropic_client
from backend.utils.logger import get_logger
from backend.utils.retry import retry_anthropic

_logger = get_logger(__name__)

# Conversations shorter than this don't need summarization
SUMMARY_THRESHOLD: int = 10

SUMMARIZATION_PROMPT: str = """You are a legal conversation summarizer for CaseMate,
an AI legal assistant. Your job is to compress a conversation history into a
structured summary that preserves all legally relevant information.

Analyze the conversation and return ONLY a JSON object with this structure:
{
    "topics": ["topic 1", "topic 2"],
    "user_facts": ["fact the user revealed about their situation"],
    "statutes_cited": ["M.G.L. c.186 §15B", "42 U.S.C. §1983"],
    "advice_given": ["key piece of advice 1", "key piece of advice 2"],
    "action_items": ["next step 1", "next step 2"],
    "unresolved_questions": ["question the user hasn't answered yet"],
    "narrative": "A 2-3 sentence narrative summary of what was discussed and decided."
}

Rules:
- Preserve ALL specific facts the user mentioned (names, dates, amounts, events).
- Include ALL statute citations exactly as they appeared.
- Capture the most important advice given, not every sentence.
- Action items are things the user was told to do and hasn't confirmed doing.
- Unresolved questions are things CaseMate asked but the user didn't answer.
- The narrative should read like a case brief — dense and factual.
- If a field has no entries, use an empty list [].
"""


class ConversationSummary:
    """Structured summary of a conversation's legally relevant content.

    Attributes:
        topics: Legal topics discussed (e.g., "security deposit", "wrongful termination").
        user_facts: Specific facts the user revealed about their situation.
        statutes_cited: Statute citations mentioned in the conversation.
        advice_given: Key legal advice provided by CaseMate.
        action_items: Next steps the user was advised to take.
        unresolved_questions: Questions CaseMate asked that remain unanswered.
        narrative: A 2-3 sentence narrative summary of the conversation.
        message_count: Number of messages that were summarized.
    """

    def __init__(
        self,
        topics: list[str] | None = None,
        user_facts: list[str] | None = None,
        statutes_cited: list[str] | None = None,
        advice_given: list[str] | None = None,
        action_items: list[str] | None = None,
        unresolved_questions: list[str] | None = None,
        narrative: str = "",
        message_count: int = 0,
    ) -> None:
        self.topics = topics or []
        self.user_facts = user_facts or []
        self.statutes_cited = statutes_cited or []
        self.advice_given = advice_given or []
        self.action_items = action_items or []
        self.unresolved_questions = unresolved_questions or []
        self.narrative = narrative
        self.message_count = message_count

    def to_prompt_block(self) -> str:
        """Format this summary as a context block for the system prompt.

        Produces a structured text block that Claude can use to maintain
        continuity with earlier parts of the conversation that were
        compressed out of the message history.

        Returns:
            A formatted string suitable for injection into the conversation
            as a context summary message.
        """
        parts: list[str] = [
            f"[CONVERSATION SUMMARY — {self.message_count} earlier messages compressed]",
        ]

        if self.narrative:
            parts.append(f"Context: {self.narrative}")

        if self.user_facts:
            parts.append("User's situation: " + "; ".join(self.user_facts))

        if self.statutes_cited:
            parts.append("Statutes referenced: " + ", ".join(self.statutes_cited))

        if self.advice_given:
            parts.append("Key advice given: " + "; ".join(self.advice_given[-3:]))

        if self.action_items:
            parts.append("Pending action items: " + "; ".join(self.action_items))

        if self.unresolved_questions:
            parts.append("Open questions: " + "; ".join(self.unresolved_questions))

        return "\n".join(parts)

    def to_dict(self) -> dict[str, object]:
        """Serialize to a dict for storage in Supabase JSONB.

        Returns:
            Dictionary representation of the summary.
        """
        return {
            "topics": self.topics,
            "user_facts": self.user_facts,
            "statutes_cited": self.statutes_cited,
            "advice_given": self.advice_given,
            "action_items": self.action_items,
            "unresolved_questions": self.unresolved_questions,
            "narrative": self.narrative,
            "message_count": self.message_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ConversationSummary:
        """Deserialize from a Supabase JSONB dict.

        Args:
            data: Dictionary with summary fields.

        Returns:
            A ConversationSummary instance.
        """
        return cls(
            topics=_safe_str_list(data.get("topics")),
            user_facts=_safe_str_list(data.get("user_facts")),
            statutes_cited=_safe_str_list(data.get("statutes_cited")),
            advice_given=_safe_str_list(data.get("advice_given")),
            action_items=_safe_str_list(data.get("action_items")),
            unresolved_questions=_safe_str_list(data.get("unresolved_questions")),
            narrative=str(data.get("narrative", "")),
            message_count=int(str(data.get("message_count", 0))),
        )


def _safe_str_list(val: object) -> list[str]:
    """Safely coerce a value into a list of strings.

    Args:
        val: The value to coerce (expected to be a list or None).

    Returns:
        A list of strings, or empty list if input is invalid.
    """
    if not isinstance(val, list):
        return []
    return [str(item) for item in val if item]


def needs_summarization(messages: list[dict[str, str]]) -> bool:
    """Check whether a conversation is long enough to benefit from summarization.

    Args:
        messages: The conversation message history.

    Returns:
        True if the conversation exceeds SUMMARY_THRESHOLD messages.
    """
    return len(messages) >= SUMMARY_THRESHOLD


@retry_anthropic
async def generate_summary(
    messages: list[dict[str, str]],
) -> ConversationSummary:
    """Generate an LLM-powered structured summary of conversation history.

    Sends the conversation to Claude with a specialized extraction prompt
    that preserves legal facts, statute citations, advice given, and
    action items. Falls back to a naive summary if parsing fails.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        A ConversationSummary with structured fields extracted from the
        conversation.

    Raises:
        anthropic.APIError: If the API call fails after all retries.
    """
    if not messages:
        return ConversationSummary()

    client = get_anthropic_client()

    # Format the conversation for Claude
    formatted_messages: list[dict[str, str]] = [
        {
            "role": "user",
            "content": _format_conversation_for_summary(messages),
        }
    ]

    _logger.info(
        "generating_conversation_summary",
        message_count=len(messages),
    )

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SUMMARIZATION_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=cast(list[MessageParam], formatted_messages),
    )

    first_block = response.content[0] if response.content else None
    response_text = first_block.text if isinstance(first_block, TextBlock) else ""

    try:
        parsed = json.loads(response_text)
        summary = ConversationSummary(
            topics=_safe_str_list(parsed.get("topics")),
            user_facts=_safe_str_list(parsed.get("user_facts")),
            statutes_cited=_safe_str_list(parsed.get("statutes_cited")),
            advice_given=_safe_str_list(parsed.get("advice_given")),
            action_items=_safe_str_list(parsed.get("action_items")),
            unresolved_questions=_safe_str_list(parsed.get("unresolved_questions")),
            narrative=str(parsed.get("narrative", "")),
            message_count=len(messages),
        )

        _logger.info(
            "conversation_summary_generated",
            topics=len(summary.topics),
            facts=len(summary.user_facts),
            statutes=len(summary.statutes_cited),
        )

        return summary

    except json.JSONDecodeError:
        _logger.warning(
            "summary_json_parse_error",
            raw_response=response_text[:200],
        )
        return _fallback_summary(messages)


def _format_conversation_for_summary(messages: list[dict[str, str]]) -> str:
    """Format conversation messages into a readable transcript for summarization.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        A formatted conversation transcript string.
    """
    lines: list[str] = []
    for msg in messages:
        role = "User" if msg.get("role") == "user" else "CaseMate"
        content = msg.get("content", "")
        # Truncate very long messages to keep summarization focused
        if len(content) > 1500:
            content = content[:1500] + "... [truncated]"
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def _fallback_summary(messages: list[dict[str, str]]) -> ConversationSummary:
    """Generate a naive summary when LLM-powered summarization fails.

    Extracts the first sentence from each message as a rough approximation.
    This is the same approach as the original ConversationSummarizer but
    packaged in the structured ConversationSummary format.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        A ConversationSummary with basic extracted information.
    """
    user_points: list[str] = []
    assistant_points: list[str] = []

    for msg in messages:
        content = msg.get("content", "")
        first_sentence = content.split(".")[0].strip()
        if len(first_sentence) > 150:
            first_sentence = first_sentence[:147] + "..."

        if msg.get("role") == "user" and first_sentence:
            user_points.append(first_sentence)
        elif msg.get("role") == "assistant" and first_sentence:
            assistant_points.append(first_sentence)

    return ConversationSummary(
        topics=[],
        user_facts=user_points[-5:],
        advice_given=assistant_points[-3:],
        narrative="Conversation summary generated via fallback extraction.",
        message_count=len(messages),
    )


async def summarize_if_needed(
    messages: list[dict[str, str]],
    existing_summary: dict[str, object] | None = None,
) -> ConversationSummary | None:
    """Conditionally generate a summary for a conversation.

    Only generates a new summary if:
    1. The conversation exceeds SUMMARY_THRESHOLD messages.
    2. There is no existing summary, or the existing summary covers
       fewer messages than the current history.

    This is designed to be called as a background task after each
    conversation turn.

    Args:
        messages: The full conversation message history.
        existing_summary: Previously stored summary dict, if any.

    Returns:
        A new ConversationSummary if one was generated, or None if
        summarization was skipped.
    """
    if not needs_summarization(messages):
        return None

    # Skip if existing summary already covers this conversation length
    if existing_summary:
        existing = ConversationSummary.from_dict(existing_summary)
        if existing.message_count >= len(messages):
            _logger.info(
                "summary_already_current",
                existing_count=existing.message_count,
                current_count=len(messages),
            )
            return None

    try:
        return await generate_summary(messages)
    except Exception as exc:
        _logger.error(
            "summarization_failed",
            error_type=type(exc).__name__,
            error_message=str(exc),
            message_count=len(messages),
        )
        return _fallback_summary(messages)
