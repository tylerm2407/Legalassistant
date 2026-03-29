"""Tests for the content-addressable document storage module.

Verifies SHA-256 hashing, deduplication, reference-counted deletion,
sharded storage paths, and graceful error handling when Supabase fails.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

from backend.utils.content_store import (
    ContentAddressableStore,
    ContentMetadata,
    _build_storage_path,
    _compute_content_hash,
    _compute_content_hash_streaming,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_supabase_mock(
    select_data: dict | None = None,
    select_rows: list[dict] | None = None,
) -> MagicMock:
    """Build a MagicMock that mimics the Supabase client call chains.

    Args:
        select_data: Data returned by a .maybe_single().execute() call.
        select_rows: Data returned by a bare .execute() call (list queries).
    """
    mock = MagicMock()

    # table().select().eq().maybe_single().execute()
    single_result = MagicMock()
    single_result.data = select_data
    (
        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value
    ) = single_result

    # table().select().execute()  (for stats / list queries)
    list_result = MagicMock()
    list_result.data = select_rows if select_rows is not None else []
    mock.table.return_value.select.return_value.execute.return_value = list_result

    # table().insert().execute()
    mock.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])

    # table().update().eq().execute()
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{}]
    )

    # table().delete().eq().execute()
    mock.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{}]
    )

    # storage.from_().upload / download / remove
    mock.storage.from_.return_value.upload.return_value = None
    mock.storage.from_.return_value.download.return_value = b"file-content"
    mock.storage.from_.return_value.remove.return_value = None

    return mock


# ---------------------------------------------------------------------------
# Pure function tests
# ---------------------------------------------------------------------------


class TestComputeContentHash:
    """Tests for _compute_content_hash and _compute_content_hash_streaming."""

    def test_compute_content_hash_deterministic(self) -> None:
        """Same input bytes always produce the same hash."""
        data = b"legal document content here"
        assert _compute_content_hash(data) == _compute_content_hash(data)

    def test_compute_content_hash_different_for_different_content(self) -> None:
        """Different content produces different hashes."""
        hash_a = _compute_content_hash(b"lease agreement version 1")
        hash_b = _compute_content_hash(b"lease agreement version 2")
        assert hash_a != hash_b

    def test_compute_content_hash_streaming_matches_direct(self) -> None:
        """Streaming hash of the same bytes matches the direct hash."""
        data = b"some legal document bytes" * 100
        direct = _compute_content_hash(data)
        streaming = _compute_content_hash_streaming(io.BytesIO(data), chunk_size=64)
        assert direct == streaming

    def test_compute_content_hash_returns_hex_string(self) -> None:
        """Hash is a 64-character lowercase hex string (SHA-256)."""
        h = _compute_content_hash(b"test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestShardedPath:
    """Tests for _build_storage_path."""

    def test_sharded_storage_path_format(self) -> None:
        """Storage path follows the ab/cd/full_hash pattern."""
        h = "abcdef1234567890" + "0" * 48  # 64-char hex
        path = _build_storage_path(h)
        assert path == f"ab/cd/{h}"

    def test_sharded_path_uses_hash_prefix(self) -> None:
        """First two segments come from the first four characters."""
        h = _compute_content_hash(b"anything")
        path = _build_storage_path(h)
        parts = path.split("/")
        assert len(parts) == 3
        assert parts[0] == h[:2]
        assert parts[1] == h[2:4]
        assert parts[2] == h


# ---------------------------------------------------------------------------
# Store / retrieve / delete tests (async, Supabase mocked)
# ---------------------------------------------------------------------------


class TestContentAddressableStore:
    """Integration-style tests for ContentAddressableStore with mocked Supabase."""

    @pytest.mark.asyncio
    async def test_store_new_content(self) -> None:
        """Storing new content uploads to storage and returns is_duplicate=False."""
        mock_client = _make_supabase_mock(select_data=None)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            meta = await store.store(b"new document", "lease.pdf", "application/pdf", "user_1")

        assert isinstance(meta, ContentMetadata)
        assert meta.is_duplicate is False
        assert meta.original_filename == "lease.pdf"
        assert meta.uploaded_by == "user_1"
        assert meta.size_bytes == len(b"new document")
        mock_client.storage.from_.return_value.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_duplicate_content_returns_is_duplicate(self) -> None:
        """Storing content that already exists returns is_duplicate=True."""
        existing = {
            "content_hash": _compute_content_hash(b"duplicate doc"),
            "size_bytes": 13,
            "mime_type": "application/pdf",
            "reference_count": 1,
            "storage_path": "xx/yy/hash",
        }
        mock_client = _make_supabase_mock(select_data=existing)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            meta = await store.store(b"duplicate doc", "lease.pdf", "application/pdf", "user_2")

        assert meta.is_duplicate is True
        # Should NOT upload again
        mock_client.storage.from_.return_value.upload.assert_not_called()

    @pytest.mark.asyncio
    async def test_store_duplicate_increments_reference_count(self) -> None:
        """Storing duplicate content increments the reference_count in the DB."""
        existing = {
            "content_hash": "abc123",
            "size_bytes": 10,
            "mime_type": "text/plain",
            "reference_count": 3,
            "storage_path": "ab/c1/abc123",
        }
        mock_client = _make_supabase_mock(select_data=existing)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            await store.store(b"content", "file.txt", "text/plain", "user_3")

        # Verify update was called with incremented count
        mock_client.table.return_value.update.assert_called_once_with({"reference_count": 4})

    @pytest.mark.asyncio
    async def test_retrieve_existing_content(self) -> None:
        """Retrieving by hash returns the raw bytes from storage."""
        mock_client = _make_supabase_mock()
        mock_client.storage.from_.return_value.download.return_value = b"the-content"
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            result = await store.retrieve("aabbcc")

        assert result == b"the-content"

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent_returns_none(self) -> None:
        """Retrieving a hash that doesn't exist returns None."""
        mock_client = _make_supabase_mock()
        mock_client.storage.from_.return_value.download.side_effect = Exception("Not found")
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            result = await store.retrieve("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_decrements_reference_count(self) -> None:
        """Deleting content with reference_count > 1 decrements but keeps the blob."""
        existing = {
            "content_hash": "aabb",
            "size_bytes": 5,
            "reference_count": 3,
            "storage_path": "aa/bb/aabb",
        }
        mock_client = _make_supabase_mock(select_data=existing)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            result = await store.delete("aabb", "user_1")

        assert result is True
        mock_client.table.return_value.update.assert_called_once_with({"reference_count": 2})
        # Storage blob should NOT be removed
        mock_client.storage.from_.return_value.remove.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_removes_when_count_zero(self) -> None:
        """Deleting the last reference removes both the blob and the DB record."""
        existing = {
            "content_hash": "aabb",
            "size_bytes": 5,
            "reference_count": 1,
            "storage_path": "aa/bb/aabb",
        }
        mock_client = _make_supabase_mock(select_data=existing)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            result = await store.delete("aabb", "user_1")

        assert result is True
        mock_client.storage.from_.return_value.remove.assert_called_once()
        mock_client.table.return_value.delete.return_value.eq.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_storage_stats(self) -> None:
        """get_storage_stats computes correct totals and dedup savings."""
        rows = [
            {"size_bytes": 1000, "reference_count": 3},
            {"size_bytes": 500, "reference_count": 1},
        ]
        mock_client = _make_supabase_mock(select_rows=rows)
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")
            stats = await store.get_storage_stats()

        assert stats["unique_documents"] == 2
        assert stats["total_documents"] == 4  # 3 + 1
        assert stats["total_bytes"] == 1500  # 1000 + 500
        # logical = 1000*3 + 500*1 = 3500; savings = 3500 - 1500 = 2000
        assert stats["dedup_savings_bytes"] == 2000

    @pytest.mark.asyncio
    async def test_supabase_error_does_not_raise(self) -> None:
        """Supabase errors are caught and logged, never propagated."""
        mock_client = MagicMock()
        error = Exception("Supabase is down")
        mock_client.table.side_effect = error
        mock_client.storage.from_.return_value.download.side_effect = error
        mock_client.storage.from_.return_value.upload.side_effect = error
        with patch("backend.utils.content_store._get_supabase", return_value=mock_client):
            store = ContentAddressableStore("documents")

            # store should return metadata (not raise)
            meta = await store.store(b"data", "f.txt", "text/plain", "user_x")
            assert isinstance(meta, ContentMetadata)

            # retrieve should return None (not raise)
            result = await store.retrieve("abc")
            assert result is None

            # delete should return False (not raise)
            ok = await store.delete("abc", "user_x")
            assert ok is False

            # stats should return zeroed dict (not raise)
            stats = await store.get_storage_stats()
            assert stats["total_documents"] == 0
