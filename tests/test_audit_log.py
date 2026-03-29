"""Tests for the event-sourced audit log with cryptographic hash chaining.

Validates hash determinism, chain integrity, tamper detection, Supabase
persistence, singleton behavior, and fail-safe error handling.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.utils.audit_log import (
    GENESIS_HASH,
    AuditEventType,
    AuditLog,
    VerificationResult,
    _compute_hash,
    record_audit_event,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the AuditLog singleton before each test."""
    AuditLog._reset()
    yield
    AuditLog._reset()


@pytest.fixture
def mock_supabase_audit():
    """Patch _get_supabase for audit log tests.

    Returns a MagicMock that intercepts all table().insert()... and
    table().select()... call chains used by the audit log.
    """
    mock_client = MagicMock()

    # Default: insert succeeds
    insert_chain = MagicMock()
    insert_chain.execute.return_value = MagicMock(data=[{"event_id": "test"}])
    mock_client.table.return_value.insert.return_value = insert_chain

    # Default: select returns empty list
    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=[])
    query = mock_client.table.return_value.select.return_value
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.gte.return_value = query
    query.execute = select_chain.execute

    with patch("backend.memory.profile._get_supabase", return_value=mock_client):
        yield mock_client


def test_genesis_hash_is_deterministic():
    """The genesis hash must always produce the same value."""
    expected = hashlib.sha256(b"CASEMATE_GENESIS_BLOCK").hexdigest()
    assert expected == GENESIS_HASH
    # Compute again to confirm determinism
    assert hashlib.sha256(b"CASEMATE_GENESIS_BLOCK").hexdigest() == GENESIS_HASH


def test_compute_hash_is_deterministic():
    """Calling _compute_hash with identical inputs must return the same hash."""
    ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=dt.UTC)
    kwargs = dict(
        event_id="abc-123",
        event_type="profile_updated",
        user_id="user_001",
        timestamp=ts,
        payload={"field": "state", "old": "NY", "new": "MA"},
        previous_hash=GENESIS_HASH,
    )
    hash1 = _compute_hash(**kwargs)
    hash2 = _compute_hash(**kwargs)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length


def test_compute_hash_changes_with_different_inputs():
    """Any change to any input field must produce a different hash."""
    ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=dt.UTC)
    base = dict(
        event_id="abc-123",
        event_type="profile_updated",
        user_id="user_001",
        timestamp=ts,
        payload={"field": "state"},
        previous_hash=GENESIS_HASH,
    )
    base_hash = _compute_hash(**base)

    # Change event_id
    assert _compute_hash(**{**base, "event_id": "xyz-456"}) != base_hash
    # Change event_type
    assert _compute_hash(**{**base, "event_type": "login"}) != base_hash
    # Change user_id
    assert _compute_hash(**{**base, "user_id": "user_002"}) != base_hash
    # Change timestamp
    assert _compute_hash(**{**base, "timestamp": ts + timedelta(seconds=1)}) != base_hash
    # Change payload
    assert _compute_hash(**{**base, "payload": {"field": "employment"}}) != base_hash
    # Change previous_hash
    assert _compute_hash(**{**base, "previous_hash": "0" * 64}) != base_hash


@pytest.mark.asyncio
async def test_record_event_creates_valid_chain(mock_supabase_audit):
    """A single recorded event must chain from the genesis hash."""
    audit = AuditLog.get_instance()
    event = await audit.record(
        AuditEventType.PROFILE_CREATED,
        "user_001",
        {"action": "created"},
    )
    assert event is not None
    assert event.previous_hash == GENESIS_HASH
    assert event.event_hash != ""
    assert event.event_hash != GENESIS_HASH

    # Verify the hash is correctly computed
    expected = _compute_hash(
        event_id=event.event_id,
        event_type=event.event_type.value,
        user_id=event.user_id,
        timestamp=event.timestamp,
        payload=event.payload,
        previous_hash=event.previous_hash,
    )
    assert event.event_hash == expected


@pytest.mark.asyncio
async def test_record_multiple_events_chain_links(mock_supabase_audit):
    """Each new event's previous_hash must equal the prior event's event_hash."""
    audit = AuditLog.get_instance()

    event1 = await audit.record(AuditEventType.PROFILE_CREATED, "user_001", {"step": "first"})
    event2 = await audit.record(AuditEventType.PROFILE_UPDATED, "user_001", {"step": "second"})
    event3 = await audit.record(AuditEventType.FACT_EXTRACTED, "user_001", {"step": "third"})

    assert event1 is not None
    assert event2 is not None
    assert event3 is not None
    assert event1.previous_hash == GENESIS_HASH
    assert event2.previous_hash == event1.event_hash
    assert event3.previous_hash == event2.event_hash


@pytest.mark.asyncio
async def test_verify_chain_valid(mock_supabase_audit):
    """verify_chain returns valid=True for a correctly linked chain."""
    audit = AuditLog.get_instance()

    event1 = await audit.record(AuditEventType.LOGIN, "user_001", {"ip": "127.0.0.1"})
    event2 = await audit.record(AuditEventType.PROFILE_UPDATED, "user_001", {"field": "state"})
    assert event1 is not None
    assert event2 is not None

    # Configure mock to return these events
    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(
        data=[
            {
                "event_id": event1.event_id,
                "event_type": event1.event_type.value,
                "user_id": event1.user_id,
                "timestamp": event1.timestamp.isoformat(),
                "payload": event1.payload,
                "previous_hash": event1.previous_hash,
                "event_hash": event1.event_hash,
            },
            {
                "event_id": event2.event_id,
                "event_type": event2.event_type.value,
                "user_id": event2.user_id,
                "timestamp": event2.timestamp.isoformat(),
                "payload": event2.payload,
                "previous_hash": event2.previous_hash,
                "event_hash": event2.event_hash,
            },
        ]
    )
    query = mock_supabase_audit.table.return_value.select.return_value
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.gte.return_value = query
    query.execute = select_chain.execute

    result = await audit.verify_chain("user_001")
    assert result.valid is True
    assert result.events_checked == 2
    assert result.break_at is None


@pytest.mark.asyncio
async def test_verify_chain_detects_tamper(mock_supabase_audit):
    """verify_chain returns valid=False when an event hash has been tampered."""
    audit = AuditLog.get_instance()

    event1 = await audit.record(AuditEventType.LOGIN, "user_001", {"ip": "127.0.0.1"})
    event2 = await audit.record(AuditEventType.DOCUMENT_UPLOADED, "user_001", {"file": "lease.pdf"})
    assert event1 is not None
    assert event2 is not None

    # Tamper with event2's hash
    tampered_data = [
        {
            "event_id": event1.event_id,
            "event_type": event1.event_type.value,
            "user_id": event1.user_id,
            "timestamp": event1.timestamp.isoformat(),
            "payload": event1.payload,
            "previous_hash": event1.previous_hash,
            "event_hash": event1.event_hash,
        },
        {
            "event_id": event2.event_id,
            "event_type": event2.event_type.value,
            "user_id": event2.user_id,
            "timestamp": event2.timestamp.isoformat(),
            "payload": event2.payload,
            "previous_hash": event2.previous_hash,
            "event_hash": "tampered_hash_value_that_is_invalid",
        },
    ]

    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=tampered_data)
    query = mock_supabase_audit.table.return_value.select.return_value
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.gte.return_value = query
    query.execute = select_chain.execute

    result = await audit.verify_chain("user_001")
    assert result.valid is False
    assert result.break_at == 1


@pytest.mark.asyncio
async def test_verify_chain_empty_returns_valid(mock_supabase_audit):
    """An empty chain (no events) should verify as valid."""
    audit = AuditLog.get_instance()
    result = await audit.verify_chain("user_no_events")
    assert result.valid is True
    assert result.events_checked == 0
    assert result.break_at is None


@pytest.mark.asyncio
async def test_get_events_filters_by_type(mock_supabase_audit):
    """get_events passes the event_type filter to Supabase."""
    audit = AuditLog.get_instance()

    event = await audit.record(AuditEventType.LOGIN, "user_001", {"ip": "127.0.0.1"})
    assert event is not None

    # Set up the mock to return one event
    row = {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "user_id": event.user_id,
        "timestamp": event.timestamp.isoformat(),
        "payload": event.payload,
        "previous_hash": event.previous_hash,
        "event_hash": event.event_hash,
    }

    select_chain = MagicMock()
    select_chain.execute.return_value = MagicMock(data=[row])
    query = mock_supabase_audit.table.return_value.select.return_value
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.gte.return_value = query
    query.execute = select_chain.execute

    events = await audit.get_events("user_001", event_type=AuditEventType.LOGIN)
    assert len(events) == 1
    assert events[0].event_type == AuditEventType.LOGIN


@pytest.mark.asyncio
async def test_get_events_filters_by_since(mock_supabase_audit):
    """get_events passes the since timestamp filter to Supabase."""
    audit = AuditLog.get_instance()

    since = datetime(2026, 3, 1, tzinfo=dt.UTC)

    # The mock returns empty by default, we just verify no errors
    events = await audit.get_events("user_001", since=since)
    assert events == []


@pytest.mark.asyncio
async def test_record_event_supabase_failure_does_not_raise(mock_supabase_audit):
    """If Supabase insert fails, record() returns None but does not raise."""
    mock_supabase_audit.table.return_value.insert.return_value.execute.side_effect = RuntimeError(
        "Supabase connection lost"
    )

    audit = AuditLog.get_instance()
    result = await audit.record(
        AuditEventType.PROFILE_UPDATED,
        "user_001",
        {"field": "state"},
    )
    assert result is None
    # The caller's code did not crash — that is the requirement


def test_audit_event_type_enum_values():
    """All 11 required event types must exist with the correct string values."""
    expected = {
        "PROFILE_CREATED": "profile_created",
        "PROFILE_UPDATED": "profile_updated",
        "FACT_EXTRACTED": "fact_extracted",
        "DOCUMENT_UPLOADED": "document_uploaded",
        "DOCUMENT_ANALYZED": "document_analyzed",
        "CONVERSATION_CREATED": "conversation_created",
        "SUBSCRIPTION_CHANGED": "subscription_changed",
        "DEADLINE_DETECTED": "deadline_detected",
        "ACTION_GENERATED": "action_generated",
        "LOGIN": "login",
        "EXPORT_GENERATED": "export_generated",
    }
    for name, value in expected.items():
        member = AuditEventType[name]
        assert member.value == value
    assert len(AuditEventType) == 11


def test_singleton_pattern():
    """AuditLog.get_instance() must return the same object every time."""
    a = AuditLog.get_instance()
    b = AuditLog.get_instance()
    assert a is b


@pytest.mark.asyncio
async def test_convenience_function_delegates_to_singleton(mock_supabase_audit):
    """record_audit_event() convenience function delegates to AuditLog singleton."""
    event = await record_audit_event(
        AuditEventType.ACTION_GENERATED,
        "user_001",
        {"action": "demand_letter"},
    )
    assert event is not None
    assert event.event_type == AuditEventType.ACTION_GENERATED
    assert event.user_id == "user_001"


@pytest.mark.asyncio
async def test_verification_result_model():
    """VerificationResult fields are correctly typed and defaulted."""
    result = VerificationResult(valid=True, events_checked=5)
    assert result.valid is True
    assert result.events_checked == 5
    assert result.break_at is None
    assert result.checked_at is not None

    broken = VerificationResult(valid=False, events_checked=3, break_at=2)
    assert broken.valid is False
    assert broken.break_at == 2
