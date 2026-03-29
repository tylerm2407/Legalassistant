"""Profile CRUD operations backed by Supabase.

Provides functions to fetch and upsert user legal profiles in the
Supabase user_profiles table. All errors are caught and logged with
structured context rather than allowed to propagate silently.
"""

from __future__ import annotations

import os

from backend.models.legal_profile import LegalProfile
from backend.utils.logger import get_logger
from supabase import Client, create_client

_logger = get_logger(__name__)

_supabase_client: Client | None = None


def _get_supabase() -> Client:
    """Get or create the Supabase client singleton.

    Returns:
        An initialized Supabase client.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables
                    are not set.
    """
    global _supabase_client  # noqa: PLW0603
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        _supabase_client = create_client(url, key)
    return _supabase_client


async def get_profile(user_id: str) -> LegalProfile | None:
    """Fetch a user's legal profile from Supabase.

    Args:
        user_id: The Supabase auth user ID to look up.

    Returns:
        The user's LegalProfile if found, or None if no profile exists
        for the given user_id.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("user_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        data = getattr(result, "data", None)
        if data is None:
            _logger.info("profile_not_found", user_id=user_id)
            return None

        _logger.info("profile_fetched", user_id=user_id)
        return LegalProfile.model_validate(data)

    except ValueError:
        _logger.error("supabase_config_error", user_id=user_id)
        raise
    except Exception as exc:
        _logger.error(
            "profile_fetch_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return None


async def update_profile(profile: LegalProfile) -> LegalProfile:
    """Upsert a user's legal profile to Supabase.

    Creates the profile if it does not exist, or updates it if it does.
    Uses the user_id as the conflict resolution key.

    Args:
        profile: The LegalProfile to upsert.

    Returns:
        The updated LegalProfile as confirmed by Supabase.

    Raises:
        ValueError: If Supabase environment variables are not configured.
        RuntimeError: If the upsert operation fails.
    """
    try:
        client = _get_supabase()
        data = profile.model_dump(mode="json")
        result = client.table("user_profiles").upsert(data, on_conflict="user_id").execute()

        if not result.data:
            raise RuntimeError(f"Upsert returned no data for user_id={profile.user_id}")

        _logger.info("profile_updated", user_id=profile.user_id)
        return LegalProfile.model_validate(result.data[0])

    except ValueError:
        _logger.error("supabase_config_error", user_id=profile.user_id)
        raise
    except RuntimeError:
        _logger.error("profile_upsert_empty", user_id=profile.user_id)
        raise
    except Exception as exc:
        _logger.error(
            "profile_update_error",
            user_id=profile.user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(
            f"Failed to update profile for user_id={profile.user_id}: {exc}"
        ) from exc


async def get_free_message_count(user_id: str) -> int:
    """Get the number of free messages used by a user this month.

    Args:
        user_id: The Supabase auth user ID.

    Returns:
        The count of free messages used, or 0 if no profile exists.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("user_profiles")
            .select("free_messages_used")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        data = getattr(result, "data", None)
        if data is None:
            return 0
        return int(data.get("free_messages_used", 0))
    except Exception as exc:
        _logger.error(
            "free_message_count_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return 0


async def increment_free_message_count(user_id: str) -> None:
    """Increment the free message counter for a user.

    Args:
        user_id: The Supabase auth user ID.
    """
    try:
        client = _get_supabase()
        current = await get_free_message_count(user_id)
        client.table("user_profiles").update({"free_messages_used": current + 1}).eq(
            "user_id", user_id
        ).execute()

        _logger.info(
            "free_message_incremented",
            user_id=user_id,
            new_count=current + 1,
        )
    except Exception as exc:
        _logger.error(
            "free_message_increment_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
