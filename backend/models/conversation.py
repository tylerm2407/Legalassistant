"""Pydantic models for conversations and individual messages.

A Conversation is a full thread between a user and CaseMate, containing an
ordered list of Messages. Each message is tagged with a role and optional
legal area so the UI can render domain-specific badges and the backend
can filter conversations by topic.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message within a conversation.

    Attributes:
        role: Who produced this message — the user, the assistant (CaseMate),
              or an error sentinel used for failed API calls.
        content: The full text content of the message.
        timestamp: When the message was created.
        legal_area: Optional legal domain classification for this message,
                    e.g. 'landlord_tenant' or 'employment_rights'.
    """

    role: Literal["user", "assistant", "error"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    legal_area: str | None = None


class Conversation(BaseModel):
    """A complete conversation thread between a user and CaseMate.

    Attributes:
        id: Unique conversation identifier (UUID string).
        user_id: Supabase auth user ID who owns this conversation.
        messages: Ordered list of messages in the conversation.
        legal_area: Primary legal domain for the overall conversation,
                    determined by the classifier on the first user message.
        created_at: When the conversation was started.
        updated_at: When the last message was added.
    """

    id: str
    user_id: str
    messages: list[Message] = Field(default_factory=list)
    legal_area: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def add_message(
        self,
        role: Literal["user", "assistant", "error"],
        content: str,
        legal_area: str | None = None,
    ) -> Message:
        """Append a new message to the conversation and update the timestamp.

        Args:
            role: The message sender role.
            content: The text content of the message.
            legal_area: Optional legal domain tag for this message.

        Returns:
            The newly created Message instance.
        """
        message = Message(role=role, content=content, legal_area=legal_area)
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
        return message

    def to_anthropic_messages(self) -> list[dict[str, str]]:
        """Convert conversation messages to the Anthropic API message format.

        Filters out error messages since the Anthropic API only accepts
        'user' and 'assistant' roles.

        Returns:
            List of dicts with 'role' and 'content' keys suitable for
            the Anthropic messages API.
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
            if msg.role in ("user", "assistant")
        ]
