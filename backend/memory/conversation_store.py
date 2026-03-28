"""Conversation persistence backed by Supabase.

Provides CRUD operations for conversation threads in the Supabase
conversations table. Each conversation belongs to a user and contains
an ordered list of messages.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from backend.memory.profile import _get_supabase
from backend.models.conversation import Conversation, Message
from backend.utils.logger import get_logger

_logger = get_logger(__name__)


async def create_conversation(
    user_id: str,
    legal_area: str | None = None,
) -> Conversation:
    """Create a new conversation in Supabase.

    Args:
        user_id: The Supabase auth user ID.
        legal_area: Optional primary legal area classification.

    Returns:
        The newly created Conversation.

    Raises:
        RuntimeError: If the insert fails.
    """
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        legal_area=legal_area,
    )
    try:
        client = _get_supabase()
        data = {
            "id": conversation.id,
            "user_id": user_id,
            "messages": [],
            "legal_area": legal_area,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        result = client.table("conversations").insert(data).execute()
        if not result.data:
            raise RuntimeError(f"Failed to create conversation for user_id={user_id}")
        _logger.info("conversation_created", user_id=user_id, conversation_id=conversation.id)
        return conversation
    except Exception as exc:
        _logger.error(
            "conversation_create_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to create conversation: {exc}") from exc


async def get_conversation(conversation_id: str, user_id: str) -> Conversation | None:
    """Fetch a conversation by ID, verifying ownership.

    Args:
        conversation_id: The conversation UUID.
        user_id: The authenticated user ID (for ownership check).

    Returns:
        The Conversation if found and owned by the user, else None.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        data = getattr(result, "data", None)
        if data is None:
            return None
        messages = [Message(**m) for m in (data.get("messages") or [])]
        return Conversation(
            id=data["id"],
            user_id=data["user_id"],
            messages=messages,
            legal_area=data.get("legal_area"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )
    except Exception as exc:
        _logger.error(
            "conversation_fetch_error",
            conversation_id=conversation_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return None


async def list_conversations(user_id: str, limit: int = 50) -> list[dict[str, object]]:
    """List a user's conversations, most recent first.

    Args:
        user_id: The Supabase auth user ID.
        limit: Maximum number of conversations to return.

    Returns:
        List of conversation summary dicts with id, legal_area,
        updated_at, and preview (first message snippet).
    """
    try:
        client = _get_supabase()
        result = (
            client.table("conversations")
            .select("id, legal_area, updated_at, messages")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        summaries: list[dict[str, object]] = []
        for row in result.data or []:
            messages = row.get("messages") or []
            first_user_msg = next(
                (m["content"] for m in messages if m.get("role") == "user"),
                "New conversation",
            )
            preview = first_user_msg[:100] + ("..." if len(first_user_msg) > 100 else "")
            summaries.append({
                "id": row["id"],
                "legal_area": row.get("legal_area"),
                "updated_at": row.get("updated_at"),
                "preview": preview,
                "message_count": len(messages),
            })
        return summaries
    except Exception as exc:
        _logger.error(
            "conversation_list_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return []


async def save_conversation(conversation: Conversation) -> None:
    """Persist updated conversation messages to Supabase.

    Args:
        conversation: The conversation with updated messages.

    Raises:
        RuntimeError: If the update fails.
    """
    try:
        client = _get_supabase()
        messages_data = [m.model_dump(mode="json") for m in conversation.messages]
        client.table("conversations").update({
            "messages": messages_data,
            "legal_area": conversation.legal_area,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", conversation.id).execute()
        _logger.info(
            "conversation_saved",
            conversation_id=conversation.id,
            message_count=len(conversation.messages),
        )
    except Exception as exc:
        _logger.error(
            "conversation_save_error",
            conversation_id=conversation.id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to save conversation: {exc}") from exc


async def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """Delete a conversation by ID, verifying ownership.

    Args:
        conversation_id: The conversation UUID.
        user_id: The authenticated user ID.

    Returns:
        True if deleted, False if not found.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("conversations")
            .delete()
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        deleted = bool(result.data)
        if deleted:
            _logger.info("conversation_deleted", conversation_id=conversation_id, user_id=user_id)
        return deleted
    except Exception as exc:
        _logger.error(
            "conversation_delete_error",
            conversation_id=conversation_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return False
