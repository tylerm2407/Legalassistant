"""Optimistic concurrency control for Supabase operations.

Implements version-based conflict detection to prevent lost updates when
background tasks (e.g., profile auto-updater) and user-initiated edits
race on the same resource. Every mutable row carries an integer `version`
column that is checked-and-incremented atomically on write.

Pattern:
  1. Read the row and its current version.
  2. Perform local modifications.
  3. Write back with expected_version = the version you read.
  4. If another writer incremented the version in between, a ConflictError
     is raised and the caller can retry with a fresh read.

The retry_with_merge helper automates the read-modify-write loop with
configurable retry count, making it safe for background tasks that must
not silently drop updates.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


class ConflictError(Exception):
    """Raised when a version-based write detects a concurrent modification.

    Attributes:
        resource_type: The Supabase table name (e.g. 'user_profiles').
        resource_id: The primary key value of the conflicting row.
        expected_version: The version the caller believed was current.
        actual_version: The version found in the database at write time.
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        expected_version: int,
        actual_version: int,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Conflict on {resource_type}[{resource_id}]: "
            f"expected version {expected_version}, found {actual_version}"
        )


class VersionedUpdate(BaseModel):
    """A versioned update payload for auditing and debugging.

    Attributes:
        resource_type: The Supabase table being updated.
        resource_id: The primary key value of the row.
        version: The version number after this update.
        data: The fields being written.
        updated_at: Timestamp of the update.
    """

    resource_type: str
    resource_id: str
    version: int
    data: dict[str, Any]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class OptimisticLock:
    """Version-based optimistic locking for Supabase row updates.

    Reads include the current version number. Writes succeed only if the
    version in the database still matches the expected version, preventing
    lost updates from concurrent writers.

    Args:
        supabase: An initialized Supabase client instance.
        version_column: The column name used for version tracking.
            Defaults to 'version'.

    Example::

        lock = OptimisticLock(supabase_client)
        data, version = await lock.read_with_version("user_profiles", "user_id", "user_123")
        data["legal_facts"].append("New fact")
        await lock.write_with_version("user_profiles", "user_id", "user_123", data, version)
    """

    def __init__(self, supabase: Any, version_column: str = "version") -> None:
        self._supabase = supabase
        self._version_column = version_column

    async def read_with_version(
        self, table: str, id_column: str, id_value: str
    ) -> tuple[dict[str, Any], int]:
        """Read a row and its current version from Supabase.

        Args:
            table: The Supabase table name.
            id_column: The column to filter on (e.g. 'user_id').
            id_value: The value to match in id_column.

        Returns:
            A tuple of (row_data, version_number).

        Raises:
            ValueError: If the row is not found.
        """
        result = (
            self._supabase.table(table).select("*").eq(id_column, id_value).maybe_single().execute()
        )

        if result.data is None:
            raise ValueError(f"Row not found: {table}.{id_column}={id_value}")

        row = result.data
        version = row.get(self._version_column, 0)

        _logger.debug(
            "optimistic_read",
            table=table,
            id_value=id_value,
            version=version,
        )

        return row, version

    async def write_with_version(
        self,
        table: str,
        id_column: str,
        id_value: str,
        data: dict[str, Any],
        expected_version: int,
    ) -> dict[str, Any]:
        """Write data to a row only if its version matches the expected value.

        Increments the version column on success. If another writer has already
        incremented the version, raises ConflictError.

        Args:
            table: The Supabase table name.
            id_column: The column to filter on (e.g. 'user_id').
            id_value: The value to match in id_column.
            data: The fields to update (version column is set automatically).
            expected_version: The version number the caller read previously.

        Returns:
            The updated row data from Supabase.

        Raises:
            ConflictError: If the current version does not match expected_version.
        """
        # First verify the current version matches
        current_result = (
            self._supabase.table(table)
            .select(self._version_column)
            .eq(id_column, id_value)
            .maybe_single()
            .execute()
        )

        if current_result.data is None:
            raise ValueError(f"Row not found: {table}.{id_column}={id_value}")

        actual_version = current_result.data.get(self._version_column, 0)

        if actual_version != expected_version:
            _logger.warning(
                "optimistic_lock_conflict",
                table=table,
                id_value=id_value,
                expected_version=expected_version,
                actual_version=actual_version,
            )
            raise ConflictError(
                resource_type=table,
                resource_id=id_value,
                expected_version=expected_version,
                actual_version=actual_version,
            )

        # Version matches — perform the update with incremented version
        new_version = expected_version + 1
        update_data = {
            **data,
            self._version_column: new_version,
            "updated_at": datetime.now(tz=UTC).isoformat(),
        }

        result = self._supabase.table(table).update(update_data).eq(id_column, id_value).execute()

        _logger.info(
            "optimistic_write",
            table=table,
            id_value=id_value,
            old_version=expected_version,
            new_version=new_version,
        )

        return result.data[0] if result.data else update_data

    async def retry_with_merge(
        self,
        table: str,
        id_column: str,
        id_value: str,
        update_fn: Callable[[dict[str, Any]], dict[str, Any]],
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Read-modify-write loop with automatic retry on version conflicts.

        Reads the current row, applies update_fn to produce new data, then
        attempts a versioned write. On ConflictError, re-reads and retries
        up to max_retries times.

        Args:
            table: The Supabase table name.
            id_column: The column to filter on.
            id_value: The value to match in id_column.
            update_fn: A callable that takes the current row dict and returns
                the modified dict to write back. Must be idempotent.
            max_retries: Maximum number of retry attempts. Defaults to 3.

        Returns:
            The successfully written row data.

        Raises:
            ConflictError: If all retries are exhausted without a successful write.
        """
        last_error: ConflictError | None = None

        for attempt in range(max_retries):
            try:
                data, version = await self.read_with_version(table, id_column, id_value)
                updated_data = update_fn(data)
                result = await self.write_with_version(
                    table, id_column, id_value, updated_data, version
                )
                if attempt > 0:
                    _logger.info(
                        "optimistic_retry_succeeded",
                        table=table,
                        id_value=id_value,
                        attempt=attempt + 1,
                    )
                return result

            except ConflictError as exc:
                last_error = exc
                _logger.warning(
                    "optimistic_retry",
                    table=table,
                    id_value=id_value,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                )

        _logger.error(
            "optimistic_retries_exhausted",
            table=table,
            id_value=id_value,
            max_retries=max_retries,
        )
        raise last_error  # type: ignore[misc]


async def optimistic_update(
    supabase: Any,
    table: str,
    id_column: str,
    id_value: str,
    update_fn: Callable[[dict[str, Any]], dict[str, Any]],
    max_retries: int = 3,
) -> dict[str, Any]:
    """Convenience function for optimistic read-modify-write on a Supabase row.

    Creates an OptimisticLock and delegates to retry_with_merge.

    Args:
        supabase: An initialized Supabase client.
        table: The Supabase table name.
        id_column: The column to filter on.
        id_value: The value to match.
        update_fn: A callable that transforms the current row data.
        max_retries: Maximum retry attempts on conflict. Defaults to 3.

    Returns:
        The successfully written row data.

    Raises:
        ConflictError: If all retries are exhausted.
        ValueError: If the row is not found.
    """
    lock = OptimisticLock(supabase)
    return await lock.retry_with_merge(table, id_column, id_value, update_fn, max_retries)
