"""Tests for optimistic concurrency control.

Validates version-based conflict detection, retry logic, and error
propagation for Supabase operations.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from backend.utils.concurrency import (
    ConflictError,
    OptimisticLock,
    VersionedUpdate,
    optimistic_update,
)


def _make_supabase_mock(
    select_data: dict | None = None,
    version: int = 1,
) -> MagicMock:
    """Create a mock Supabase client with configurable select/update behavior.

    Args:
        select_data: The row data returned by select queries.
        version: The version number included in select results.

    Returns:
        A MagicMock configured to chain Supabase query methods.
    """
    mock = MagicMock()

    row = {**(select_data or {"user_id": "user_123", "name": "Test"}), "version": version}

    # Chain: table().select("*").eq(...).maybe_single().execute()
    select_result = MagicMock()
    select_result.data = row
    (
        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value
    ) = select_result

    # Chain: table().update(...).eq(...).execute()
    update_result = MagicMock()
    update_result.data = [{**row, "version": version + 1}]
    (
        mock.table.return_value.update.return_value.eq.return_value.execute.return_value
    ) = update_result

    return mock


class TestReadWithVersion:
    """Tests for reading rows with version tracking."""

    @pytest.mark.asyncio
    async def test_read_with_version_returns_data_and_version(self) -> None:
        """read_with_version returns the row data and its version number."""
        supabase = _make_supabase_mock(
            select_data={"user_id": "u1", "state": "MA"},
            version=3,
        )
        lock = OptimisticLock(supabase)

        data, version = await lock.read_with_version("user_profiles", "user_id", "u1")

        assert data["state"] == "MA"
        assert version == 3

    @pytest.mark.asyncio
    async def test_read_with_version_not_found_raises(self) -> None:
        """read_with_version raises ValueError when the row does not exist."""
        supabase = MagicMock()
        result = MagicMock()
        result.data = None
        (
            supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = result

        lock = OptimisticLock(supabase)

        with pytest.raises(ValueError, match="Row not found"):
            await lock.read_with_version("user_profiles", "user_id", "missing")


class TestWriteWithVersion:
    """Tests for versioned writes."""

    @pytest.mark.asyncio
    async def test_write_with_version_success(self) -> None:
        """A write succeeds when the expected version matches the current version."""
        supabase = _make_supabase_mock(version=5)
        lock = OptimisticLock(supabase)

        result = await lock.write_with_version(
            "user_profiles", "user_id", "u1", {"state": "NY"}, expected_version=5
        )

        assert result["version"] == 6

    @pytest.mark.asyncio
    async def test_write_with_version_conflict_raises(self) -> None:
        """A write raises ConflictError when versions do not match."""
        supabase = _make_supabase_mock(version=7)
        lock = OptimisticLock(supabase)

        with pytest.raises(ConflictError) as exc_info:
            await lock.write_with_version(
                "user_profiles", "user_id", "u1", {"state": "NY"}, expected_version=5
            )

        assert exc_info.value.expected_version == 5
        assert exc_info.value.actual_version == 7

    @pytest.mark.asyncio
    async def test_write_increments_version(self) -> None:
        """A successful write passes version + 1 in the update payload."""
        supabase = _make_supabase_mock(version=2)
        lock = OptimisticLock(supabase)

        await lock.write_with_version(
            "user_profiles", "user_id", "u1", {"name": "Updated"}, expected_version=2
        )

        # Verify update was called with version=3
        update_call = supabase.table.return_value.update
        update_call.assert_called_once()
        update_payload = update_call.call_args[0][0]
        assert update_payload["version"] == 3


class TestConflictError:
    """Tests for the ConflictError exception."""

    def test_conflict_error_contains_details(self) -> None:
        """ConflictError exposes resource_type, resource_id, and version info."""
        error = ConflictError(
            resource_type="user_profiles",
            resource_id="u1",
            expected_version=3,
            actual_version=5,
        )

        assert error.resource_type == "user_profiles"
        assert error.resource_id == "u1"
        assert error.expected_version == 3
        assert error.actual_version == 5
        assert "user_profiles" in str(error)
        assert "u1" in str(error)

    def test_conflict_error_message_format(self) -> None:
        """The error message includes table, id, and both version numbers."""
        error = ConflictError("profiles", "abc", 1, 2)
        assert str(error) == "Conflict on profiles[abc]: expected version 1, found 2"


class TestRetryWithMerge:
    """Tests for the automatic retry-on-conflict loop."""

    @pytest.mark.asyncio
    async def test_retry_with_merge_succeeds_after_conflict(self) -> None:
        """retry_with_merge retries and succeeds after an initial conflict."""
        supabase = MagicMock()
        lock = OptimisticLock(supabase)

        call_count = 0

        async def mock_read(table: str, id_col: str, id_val: str) -> tuple[dict, int]:
            nonlocal call_count
            call_count += 1
            return {"name": "Test", "version": call_count}, call_count

        async def mock_write(
            table: str, id_col: str, id_val: str, data: dict, expected: int
        ) -> dict:
            if expected == 1:
                raise ConflictError(table, id_val, 1, 2)
            return {**data, "version": expected + 1}

        lock.read_with_version = mock_read  # type: ignore[assignment]
        lock.write_with_version = mock_write  # type: ignore[assignment]

        result = await lock.retry_with_merge(
            "profiles", "user_id", "u1", lambda d: {**d, "updated": True}
        )

        assert result["updated"] is True
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_merge_exhausts_retries(self) -> None:
        """retry_with_merge raises ConflictError after max_retries failures."""
        supabase = MagicMock()
        lock = OptimisticLock(supabase)

        attempt = 0

        async def mock_read(table: str, id_col: str, id_val: str) -> tuple[dict, int]:
            nonlocal attempt
            attempt += 1
            return {"name": "Test"}, attempt

        async def mock_write(
            table: str, id_col: str, id_val: str, data: dict, expected: int
        ) -> dict:
            raise ConflictError(table, id_val, expected, expected + 1)

        lock.read_with_version = mock_read  # type: ignore[assignment]
        lock.write_with_version = mock_write  # type: ignore[assignment]

        with pytest.raises(ConflictError):
            await lock.retry_with_merge("profiles", "user_id", "u1", lambda d: d, max_retries=3)

        assert attempt == 3


class TestVersionedUpdateModel:
    """Tests for the VersionedUpdate Pydantic model."""

    def test_versioned_update_model(self) -> None:
        """VersionedUpdate stores resource info, version, data, and timestamp."""
        update = VersionedUpdate(
            resource_type="user_profiles",
            resource_id="u1",
            version=5,
            data={"state": "MA", "name": "Sarah"},
        )

        assert update.resource_type == "user_profiles"
        assert update.resource_id == "u1"
        assert update.version == 5
        assert update.data == {"state": "MA", "name": "Sarah"}
        assert isinstance(update.updated_at, datetime)

    def test_versioned_update_custom_timestamp(self) -> None:
        """VersionedUpdate accepts a custom updated_at value."""
        ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        update = VersionedUpdate(
            resource_type="conversations",
            resource_id="c1",
            version=1,
            data={},
            updated_at=ts,
        )
        assert update.updated_at == ts


class TestSupabaseErrorPropagation:
    """Tests for error handling when Supabase calls fail."""

    @pytest.mark.asyncio
    async def test_supabase_error_propagates(self) -> None:
        """Supabase client exceptions propagate through OptimisticLock."""
        supabase = MagicMock()
        (
            supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect
        ) = RuntimeError("Supabase connection failed")

        lock = OptimisticLock(supabase)

        with pytest.raises(RuntimeError, match="Supabase connection failed"):
            await lock.read_with_version("user_profiles", "user_id", "u1")


class TestOptimisticUpdateConvenience:
    """Tests for the optimistic_update() convenience function."""

    @pytest.mark.asyncio
    async def test_optimistic_update_delegates_to_lock(self) -> None:
        """optimistic_update() creates an OptimisticLock and performs retry_with_merge."""
        supabase = _make_supabase_mock(
            select_data={"user_id": "u1", "facts": []},
            version=1,
        )

        result = await optimistic_update(
            supabase,
            "user_profiles",
            "user_id",
            "u1",
            lambda d: {**d, "facts": ["new fact"]},
        )

        assert result is not None
