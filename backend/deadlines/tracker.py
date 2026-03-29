"""Deadline and statute of limitations tracking backed by Supabase.

Provides CRUD operations for legal deadlines. Deadlines can be
auto-detected from conversations or manually created by users.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from backend.memory.profile import _get_supabase
from backend.utils.logger import get_logger

_logger = get_logger(__name__)


class DeadlineStatus(StrEnum):
    """Status values for a tracked deadline."""

    ACTIVE = "active"
    COMPLETED = "completed"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class Deadline(BaseModel):
    """A tracked legal deadline or statute of limitations.

    Attributes:
        id: Unique deadline identifier.
        user_id: Supabase auth user ID who owns this deadline.
        title: Short description of what's due.
        date: The deadline date.
        legal_area: Associated legal domain.
        source_conversation_id: Conversation where this was detected, if any.
        status: Current status of the deadline.
        notes: Additional context about this deadline.
        created_at: When the deadline was created.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    date: str  # ISO date string
    legal_area: str | None = None
    source_conversation_id: str | None = None
    status: DeadlineStatus = DeadlineStatus.ACTIVE
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DeadlineCreateRequest(BaseModel):
    """Request body for creating a deadline.

    Attributes:
        title: Short description (max 500 chars).
        date: ISO date string.
        legal_area: Optional legal domain.
        notes: Optional additional context.
    """

    title: str = Field(..., max_length=500)
    date: str
    legal_area: str | None = None
    notes: str = Field(default="", max_length=2000)


class DeadlineUpdateRequest(BaseModel):
    """Request body for updating a deadline.

    Attributes:
        title: Updated title.
        date: Updated date.
        status: Updated status.
        notes: Updated notes.
    """

    title: str | None = None
    date: str | None = None
    status: DeadlineStatus | None = None
    notes: str | None = None


async def create_deadline(
    user_id: str,
    title: str,
    date: str,
    legal_area: str | None = None,
    source_conversation_id: str | None = None,
    notes: str = "",
) -> Deadline:
    """Create a new deadline in Supabase.

    Args:
        user_id: The Supabase auth user ID.
        title: Short description of the deadline.
        date: ISO date string for the deadline.
        legal_area: Optional legal domain classification.
        source_conversation_id: Optional conversation ID where detected.
        notes: Optional additional context.

    Returns:
        The newly created Deadline.

    Raises:
        RuntimeError: If the insert fails.
    """
    deadline = Deadline(
        user_id=user_id,
        title=title,
        date=date,
        legal_area=legal_area,
        source_conversation_id=source_conversation_id,
        notes=notes,
    )
    try:
        client = _get_supabase()
        data = deadline.model_dump(mode="json")
        result = client.table("deadlines").insert(data).execute()
        if not result.data:
            raise RuntimeError(f"Failed to create deadline for user_id={user_id}")
        _logger.info("deadline_created", user_id=user_id, deadline_id=deadline.id, title=title)
        return deadline
    except Exception as exc:
        _logger.error(
            "deadline_create_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to create deadline: {exc}") from exc


async def list_deadlines(user_id: str, status: DeadlineStatus | None = None) -> list[Deadline]:
    """List a user's deadlines, optionally filtered by status.

    Args:
        user_id: The Supabase auth user ID.
        status: Optional status filter.

    Returns:
        List of Deadline objects, ordered by date ascending.
    """
    try:
        client = _get_supabase()
        query = client.table("deadlines").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status.value)
        result = query.order("date", desc=False).execute()
        return [Deadline(**dict(row)) for row in (result.data or [])]  # type: ignore[arg-type]
    except Exception as exc:
        _logger.error(
            "deadline_list_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return []


async def update_deadline(
    deadline_id: str,
    user_id: str,
    updates: DeadlineUpdateRequest,
) -> Deadline | None:
    """Update a deadline by ID, verifying ownership.

    Args:
        deadline_id: The deadline UUID.
        user_id: The authenticated user ID.
        updates: Fields to update.

    Returns:
        The updated Deadline, or None if not found.

    Raises:
        RuntimeError: If the update fails.
    """
    try:
        client = _get_supabase()
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        if not update_data:
            return None
        result = (
            client.table("deadlines")
            .update(update_data)
            .eq("id", deadline_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not result.data:
            return None
        _logger.info("deadline_updated", deadline_id=deadline_id, user_id=user_id)
        return Deadline(**dict(result.data[0]))  # type: ignore[arg-type]
    except Exception as exc:
        _logger.error(
            "deadline_update_error",
            deadline_id=deadline_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to update deadline: {exc}") from exc


async def delete_deadline(deadline_id: str, user_id: str) -> bool:
    """Delete a deadline by ID, verifying ownership.

    Args:
        deadline_id: The deadline UUID.
        user_id: The authenticated user ID.

    Returns:
        True if deleted, False if not found.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("deadlines")
            .delete()
            .eq("id", deadline_id)
            .eq("user_id", user_id)
            .execute()
        )
        deleted = bool(result.data)
        if deleted:
            _logger.info("deadline_deleted", deadline_id=deadline_id, user_id=user_id)
        return deleted
    except Exception as exc:
        _logger.error(
            "deadline_delete_error",
            deadline_id=deadline_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return False
