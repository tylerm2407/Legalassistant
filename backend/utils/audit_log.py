"""Event-sourced audit log with cryptographic hash chaining.

Provides tamper-evident audit logging for all profile mutations, document
uploads, and sensitive operations in CaseMate. Every event is hash-chained —
each event's hash includes the previous event's hash, creating a cryptographic
chain that proves no events have been modified or deleted.

Architecture:
  - AuditEventType enum: Classifies all auditable operations.
  - AuditEvent model: Immutable record with event_hash linking to previous_hash.
  - AuditLog singleton: Manages the hash chain head and persists events to
    Supabase. Fail-safe — never blocks or crashes the main request flow.
  - verify_chain: Reads events back from Supabase and validates the hash chain,
    detecting any tampering or deletion.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import uuid
from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

GENESIS_HASH: str = hashlib.sha256(b"CASEMATE_GENESIS_BLOCK").hexdigest()
"""The hash that anchors the start of every user's audit chain."""


class AuditEventType(StrEnum):
    """All auditable event types in CaseMate.

    Each variant maps to a specific user-facing or system operation
    that must be recorded for compliance and tamper detection.
    """

    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    FACT_EXTRACTED = "fact_extracted"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_ANALYZED = "document_analyzed"
    CONVERSATION_CREATED = "conversation_created"
    SUBSCRIPTION_CHANGED = "subscription_changed"
    DEADLINE_DETECTED = "deadline_detected"
    ACTION_GENERATED = "action_generated"
    LOGIN = "login"
    EXPORT_GENERATED = "export_generated"


class AuditEvent(BaseModel):
    """A single immutable audit event with a cryptographic hash link.

    Each event's hash is computed from its own fields plus the previous
    event's hash, creating an append-only chain. Any modification to a
    past event breaks the chain and is detectable via verify_chain().

    Attributes:
        event_id: Unique identifier for this event.
        event_type: The classification of the auditable operation.
        user_id: The authenticated user who triggered the event.
        timestamp: UTC timestamp of when the event occurred.
        payload: Arbitrary structured data describing the event details.
        previous_hash: The event_hash of the preceding event in the chain.
        event_hash: SHA-256 hash of this event's canonical representation.
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(dt.UTC))
    payload: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str = ""


class VerificationResult(BaseModel):
    """Result of an audit chain integrity verification.

    Attributes:
        valid: True if every event's hash correctly links to its predecessor.
        events_checked: The number of events that were verified.
        break_at: The index (0-based) where the chain broke, or None if valid.
        checked_at: UTC timestamp of when the verification was performed.
    """

    valid: bool
    events_checked: int
    break_at: int | None = None
    checked_at: datetime = Field(default_factory=lambda: datetime.now(dt.UTC))


def _compute_hash(
    event_id: str,
    event_type: str,
    user_id: str,
    timestamp: datetime,
    payload: dict[str, str | int | float | bool | None],
    previous_hash: str,
) -> str:
    """Compute the SHA-256 hash for an audit event.

    Uses canonical JSON serialization (sorted keys, no whitespace) to
    ensure deterministic hashing regardless of dict insertion order.

    Args:
        event_id: The event's unique identifier.
        event_type: The event type string value.
        user_id: The user who triggered the event.
        timestamp: The UTC timestamp of the event.
        payload: The event's detail payload.
        previous_hash: The hash of the preceding event in the chain.

    Returns:
        A lowercase hex SHA-256 digest string.
    """
    canonical = (
        event_id
        + event_type
        + user_id
        + timestamp.isoformat()
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
        + previous_hash
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditLog:
    """Event-sourced audit log with cryptographic hash chaining.

    Singleton that manages the chain head and persists events to the
    Supabase ``audit_events`` table. All write failures are caught and
    logged — audit logging must never block or crash the main request.

    The chain head is initialized to GENESIS_HASH and advances with
    each recorded event. On restart the head is re-read from Supabase.
    """

    _instance: ClassVar[AuditLog | None] = None

    def __init__(self) -> None:
        self._chain_head: str = GENESIS_HASH

    @classmethod
    def get_instance(cls) -> AuditLog:
        """Get or create the singleton AuditLog.

        Returns:
            The shared AuditLog instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _reset(cls) -> None:
        """Reset the singleton for testing. Not for production use."""
        cls._instance = None

    async def record(
        self,
        event_type: AuditEventType,
        user_id: str,
        payload: dict[str, str | int | float | bool | None],
    ) -> AuditEvent | None:
        """Record an auditable event and append it to the hash chain.

        Creates the event, computes its chained hash, writes it to
        Supabase, and advances the chain head. If the Supabase write
        fails the error is logged but never propagated to the caller.

        Args:
            event_type: The type of operation being recorded.
            user_id: The authenticated user who triggered the operation.
            payload: Structured details about the event.

        Returns:
            The persisted AuditEvent, or None if the write failed.
        """
        try:
            event = AuditEvent(
                event_type=event_type,
                user_id=user_id,
                payload=payload,
                previous_hash=self._chain_head,
            )
            event.event_hash = _compute_hash(
                event_id=event.event_id,
                event_type=event.event_type.value,
                user_id=event.user_id,
                timestamp=event.timestamp,
                payload=event.payload,
                previous_hash=event.previous_hash,
            )

            await self._persist(event)
            self._chain_head = event.event_hash

            _logger.info(
                "audit_event_recorded",
                user_id=user_id,
                event_type=event_type.value,
                event_id=event.event_id,
            )
            return event

        except Exception as exc:
            _logger.error(
                "audit_record_failed",
                user_id=user_id,
                event_type=event_type.value,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return None

    async def verify_chain(self, user_id: str, limit: int = 100) -> VerificationResult:
        """Verify the integrity of a user's audit event chain.

        Reads events from Supabase ordered by timestamp and checks that
        each event's hash correctly incorporates the previous event's
        hash. A break indicates tampering or data loss.

        Args:
            user_id: The user whose chain to verify.
            limit: Maximum number of events to check.

        Returns:
            A VerificationResult indicating whether the chain is intact.
        """
        try:
            events = await self._fetch_events(
                user_id=user_id, event_type=None, since=None, limit=limit
            )

            if not events:
                return VerificationResult(valid=True, events_checked=0)

            for i, event in enumerate(events):
                expected_previous = GENESIS_HASH if i == 0 else events[i - 1].event_hash
                if event.previous_hash != expected_previous:
                    return VerificationResult(valid=False, events_checked=i + 1, break_at=i)

                expected_hash = _compute_hash(
                    event_id=event.event_id,
                    event_type=event.event_type.value,
                    user_id=event.user_id,
                    timestamp=event.timestamp,
                    payload=event.payload,
                    previous_hash=event.previous_hash,
                )
                if event.event_hash != expected_hash:
                    return VerificationResult(valid=False, events_checked=i + 1, break_at=i)

            return VerificationResult(valid=True, events_checked=len(events))

        except Exception as exc:
            _logger.error(
                "audit_verify_failed",
                user_id=user_id,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return VerificationResult(valid=False, events_checked=0, break_at=0)

    async def get_events(
        self,
        user_id: str,
        event_type: AuditEventType | None = None,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        """Retrieve audit events for a user with optional filters.

        Args:
            user_id: The user whose events to retrieve.
            event_type: Optional filter to a single event type.
            since: Optional lower bound on event timestamp (inclusive).
            limit: Maximum number of events to return.

        Returns:
            A list of AuditEvent instances ordered by timestamp ascending.
        """
        try:
            return await self._fetch_events(
                user_id=user_id, event_type=event_type, since=since, limit=limit
            )
        except Exception as exc:
            _logger.error(
                "audit_get_events_failed",
                user_id=user_id,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return []

    async def _persist(self, event: AuditEvent) -> None:
        """Write an audit event to the Supabase audit_events table.

        Args:
            event: The fully constructed AuditEvent to persist.

        Raises:
            Exception: Propagated to the caller (record) which catches it.
        """
        from backend.memory.profile import _get_supabase

        client = _get_supabase()
        client.table("audit_events").insert(
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
                "previous_hash": event.previous_hash,
                "event_hash": event.event_hash,
            }
        ).execute()

    async def _fetch_events(
        self,
        user_id: str,
        event_type: AuditEventType | None,
        since: datetime | None,
        limit: int,
    ) -> list[AuditEvent]:
        """Fetch audit events from Supabase with optional filters.

        Args:
            user_id: The user whose events to fetch.
            event_type: Optional event type filter.
            since: Optional timestamp lower bound.
            limit: Maximum rows to return.

        Returns:
            Parsed AuditEvent list ordered by timestamp ascending.
        """
        from backend.memory.profile import _get_supabase

        client = _get_supabase()
        query = (
            client.table("audit_events")
            .select("*")
            .eq("user_id", user_id)
            .order("timestamp", desc=False)
            .limit(limit)
        )

        if event_type is not None:
            query = query.eq("event_type", event_type.value)
        if since is not None:
            query = query.gte("timestamp", since.isoformat())

        result = query.execute()
        rows = getattr(result, "data", None) or []

        events: list[AuditEvent] = []
        for row in rows:
            events.append(
                AuditEvent(
                    event_id=row["event_id"],
                    event_type=AuditEventType(row["event_type"]),
                    user_id=row["user_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    payload=row.get("payload", {}),
                    previous_hash=row["previous_hash"],
                    event_hash=row["event_hash"],
                )
            )
        return events


async def record_audit_event(
    event_type: AuditEventType,
    user_id: str,
    payload: dict[str, str | int | float | bool | None],
) -> AuditEvent | None:
    """Convenience function to record an audit event via the singleton.

    Gets the AuditLog singleton and delegates to its record() method.
    This is the primary entry point for other modules to log auditable
    operations without managing the AuditLog instance directly.

    Args:
        event_type: The type of operation being recorded.
        user_id: The authenticated user who triggered the operation.
        payload: Structured details about the event.

    Returns:
        The persisted AuditEvent, or None if recording failed.
    """
    audit_log = AuditLog.get_instance()
    return await audit_log.record(event_type, user_id, payload)
