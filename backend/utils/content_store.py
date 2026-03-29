"""Content-addressable document storage backed by Supabase.

Implements SHA-256 based content-addressable storage for uploaded documents.
Instead of storing duplicate copies of the same document, it computes a
content hash and deduplicates at the storage layer. This is critical for a
legal app where users may upload the same lease or contract multiple times.

Storage paths use a sharded directory structure: ``{hash[:2]}/{hash[2:4]}/{hash}``
to avoid large flat directories in Supabase Storage.

Reference counting ensures that shared content is only deleted from storage
when no users reference it anymore.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import BinaryIO, NewType

from pydantic import BaseModel, Field

from backend.memory.profile import _get_supabase
from backend.utils.logger import get_logger

_logger = get_logger(__name__)

ContentHash = NewType("ContentHash", str)


class StoredContent(BaseModel):
    """Metadata for a content-addressed blob stored in Supabase Storage.

    Attributes:
        content_hash: SHA-256 hex digest of the raw bytes.
        size_bytes: Size of the stored content in bytes.
        mime_type: MIME type of the stored content (e.g. ``application/pdf``).
        created_at: Timestamp when the content was first stored.
        reference_count: Number of user-document records pointing to this blob.
        storage_path: Sharded path inside the Supabase Storage bucket.
    """

    content_hash: str
    size_bytes: int
    mime_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reference_count: int = 1
    storage_path: str


class ContentMetadata(BaseModel):
    """Metadata returned to the caller after a store or lookup operation.

    Attributes:
        original_filename: The filename the user uploaded.
        uploaded_by: The user ID that uploaded this document.
        content_hash: SHA-256 hex digest used to address the content.
        is_duplicate: True when the same content was already in storage.
        size_bytes: Size of the content in bytes.
    """

    original_filename: str
    uploaded_by: str
    content_hash: str
    is_duplicate: bool
    size_bytes: int


def _compute_content_hash(data: bytes) -> str:
    """Compute the SHA-256 hex digest of raw bytes.

    Args:
        data: The raw bytes to hash.

    Returns:
        A lowercase hex string of the SHA-256 digest.
    """
    return hashlib.sha256(data).hexdigest()


def _compute_content_hash_streaming(file_obj: BinaryIO, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hex digest by streaming chunks from a file object.

    Avoids loading large files entirely into memory. The file object's read
    position is **not** reset after hashing — the caller should seek(0) if
    the file needs to be read again.

    Args:
        file_obj: A readable binary file-like object.
        chunk_size: Number of bytes to read per iteration. Defaults to 8192.

    Returns:
        A lowercase hex string of the SHA-256 digest.
    """
    hasher = hashlib.sha256()
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()


def _build_storage_path(content_hash: str) -> str:
    """Build a sharded storage path from a content hash.

    Uses the first two and next two characters as directory prefixes to
    distribute files across subdirectories and avoid performance issues
    with large flat directory listings.

    Args:
        content_hash: The SHA-256 hex digest of the content.

    Returns:
        A path string in the form ``ab/cd/abcd...full_hash``.
    """
    return f"{content_hash[:2]}/{content_hash[2:4]}/{content_hash}"


class ContentAddressableStore:
    """Content-addressable document storage backed by Supabase.

    Provides store, retrieve, and delete operations with automatic
    deduplication via SHA-256 content hashing and reference-counted
    garbage collection.

    Args:
        bucket_name: The Supabase Storage bucket to use for blob storage.
    """

    def __init__(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name

    async def store(
        self,
        data: bytes,
        filename: str,
        mime_type: str,
        user_id: str,
    ) -> ContentMetadata:
        """Store document bytes, deduplicating by content hash.

        If the exact same bytes have already been stored, the existing
        record's reference_count is incremented and ``is_duplicate`` is
        set to True in the returned metadata.

        Args:
            data: Raw document bytes.
            filename: Original filename from the upload.
            mime_type: MIME type of the document.
            user_id: ID of the uploading user.

        Returns:
            ContentMetadata describing the stored (or deduplicated) content.
        """
        content_hash = _compute_content_hash(data)
        size_bytes = len(data)
        log = _logger.bind(user_id=user_id, content_hash=content_hash)

        try:
            client = _get_supabase()

            # Check if content already exists
            existing = (
                client.table("document_hashes")
                .select("*")
                .eq("content_hash", content_hash)
                .maybe_single()
                .execute()
            )

            existing_data = getattr(existing, "data", None)
            if existing_data is not None and isinstance(existing_data, dict):
                # Duplicate — increment reference count
                new_count = int(existing_data["reference_count"]) + 1
                client.table("document_hashes").update({"reference_count": new_count}).eq(
                    "content_hash", content_hash
                ).execute()

                log.info("duplicate_content_stored", reference_count=new_count)
                return ContentMetadata(
                    original_filename=filename,
                    uploaded_by=user_id,
                    content_hash=content_hash,
                    is_duplicate=True,
                    size_bytes=size_bytes,
                )

            # New content — upload to storage with sharded path
            storage_path = _build_storage_path(content_hash)
            client.storage.from_(self._bucket_name).upload(
                path=storage_path,
                file=data,
                file_options={"content-type": mime_type},
            )

            # Create database record
            record = StoredContent(
                content_hash=content_hash,
                size_bytes=size_bytes,
                mime_type=mime_type,
                reference_count=1,
                storage_path=storage_path,
            )
            client.table("document_hashes").insert(record.model_dump(mode="json")).execute()

            log.info("new_content_stored", size_bytes=size_bytes, path=storage_path)
            return ContentMetadata(
                original_filename=filename,
                uploaded_by=user_id,
                content_hash=content_hash,
                is_duplicate=False,
                size_bytes=size_bytes,
            )

        except Exception as exc:
            log.error(
                "content_store_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return ContentMetadata(
                original_filename=filename,
                uploaded_by=user_id,
                content_hash=content_hash,
                is_duplicate=False,
                size_bytes=size_bytes,
            )

    async def retrieve(self, content_hash: str) -> bytes | None:
        """Fetch stored content by its SHA-256 hash.

        Args:
            content_hash: The hex digest identifying the content.

        Returns:
            The raw bytes if found, or None if the hash is unknown.
        """
        log = _logger.bind(content_hash=content_hash)
        try:
            client = _get_supabase()
            storage_path = _build_storage_path(content_hash)
            data = client.storage.from_(self._bucket_name).download(storage_path)
            log.info("content_retrieved", size_bytes=len(data))
            return bytes(data)
        except Exception as exc:
            log.error(
                "content_retrieve_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return None

    async def delete(self, content_hash: str, user_id: str) -> bool:
        """Remove a user's reference to content, deleting the blob when unreferenced.

        Decrements the reference count. When the count reaches zero the
        underlying blob is removed from Supabase Storage and the database
        record is deleted.

        Args:
            content_hash: The hex digest of the content to dereference.
            user_id: The user requesting deletion (for audit logging).

        Returns:
            True if the operation succeeded, False on error.
        """
        log = _logger.bind(user_id=user_id, content_hash=content_hash)
        try:
            client = _get_supabase()
            result = (
                client.table("document_hashes")
                .select("*")
                .eq("content_hash", content_hash)
                .maybe_single()
                .execute()
            )

            row_data = getattr(result, "data", None)
            if row_data is None or not isinstance(row_data, dict):
                log.warning("delete_nonexistent_content")
                return False

            current_count = int(row_data["reference_count"])

            if current_count <= 1:
                # Last reference — remove blob and DB record
                storage_path = _build_storage_path(content_hash)
                client.storage.from_(self._bucket_name).remove([storage_path])
                client.table("document_hashes").delete().eq("content_hash", content_hash).execute()
                log.info("content_deleted_permanently")
            else:
                client.table("document_hashes").update({"reference_count": current_count - 1}).eq(
                    "content_hash", content_hash
                ).execute()
                log.info("content_reference_decremented", new_count=current_count - 1)

            return True

        except Exception as exc:
            log.error(
                "content_delete_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return False

    async def get_metadata(self, content_hash: str) -> StoredContent | None:
        """Look up metadata for a stored content blob.

        Args:
            content_hash: The hex digest identifying the content.

        Returns:
            A StoredContent model if found, or None.
        """
        log = _logger.bind(content_hash=content_hash)
        try:
            client = _get_supabase()
            result = (
                client.table("document_hashes")
                .select("*")
                .eq("content_hash", content_hash)
                .maybe_single()
                .execute()
            )
            data = getattr(result, "data", None)
            if data is None:
                return None
            return StoredContent.model_validate(data)
        except Exception as exc:
            log.error(
                "metadata_lookup_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return None

    async def get_user_documents(self, user_id: str) -> list[ContentMetadata]:
        """List all documents uploaded by a specific user.

        Args:
            user_id: The user whose documents to list.

        Returns:
            A list of ContentMetadata records for the user's uploads.
        """
        log = _logger.bind(user_id=user_id)
        try:
            client = _get_supabase()
            result = client.table("user_documents").select("*").eq("uploaded_by", user_id).execute()
            rows = getattr(result, "data", None) or []
            documents = [ContentMetadata.model_validate(row) for row in rows]
            log.info("user_documents_listed", count=len(documents))
            return documents
        except Exception as exc:
            log.error(
                "user_documents_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return []

    async def get_storage_stats(self) -> dict[str, int]:
        """Compute aggregate storage statistics.

        Returns:
            A dict with keys: total_documents, total_bytes,
            unique_documents, dedup_savings_bytes.
        """
        try:
            client = _get_supabase()
            result = client.table("document_hashes").select("size_bytes,reference_count").execute()
            rows = getattr(result, "data", None) or []

            unique_documents = len(rows)
            total_documents = sum(row["reference_count"] for row in rows)
            total_bytes = sum(row["size_bytes"] for row in rows)
            total_logical_bytes = sum(row["size_bytes"] * row["reference_count"] for row in rows)
            dedup_savings_bytes = total_logical_bytes - total_bytes

            _logger.info(
                "storage_stats_computed",
                unique=unique_documents,
                total=total_documents,
                savings_bytes=dedup_savings_bytes,
            )
            return {
                "total_documents": total_documents,
                "total_bytes": total_bytes,
                "unique_documents": unique_documents,
                "dedup_savings_bytes": dedup_savings_bytes,
            }
        except Exception as exc:
            _logger.error(
                "storage_stats_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            return {
                "total_documents": 0,
                "total_bytes": 0,
                "unique_documents": 0,
                "dedup_savings_bytes": 0,
            }
