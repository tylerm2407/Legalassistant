"""Supabase JWT verification for FastAPI endpoints.

Provides a dependency that extracts and verifies the JWT from the
Authorization header, returning the authenticated user_id. Uses the
Supabase admin client to validate tokens server-side.
"""

from __future__ import annotations

import os

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.utils.logger import get_logger
from supabase import Client, create_client

_logger = get_logger(__name__)

_bearer_scheme = HTTPBearer()

_supabase_admin: Client | None = None


def _get_admin_client() -> Client:
    """Return a module-level Supabase admin client singleton.

    Uses the service role key for server-side token verification.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY are not set.
    """
    global _supabase_admin  # noqa: PLW0603
    if _supabase_admin is None:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        _supabase_admin = create_client(url, key)
    return _supabase_admin


async def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """Verify a Supabase JWT and return the user_id.

    Uses a two-step approach:
    1. Try to verify the JWT locally using the JWT secret (fast path).
    2. If local verification fails, fall back to the Supabase admin API
       to validate the token server-side (handles algorithm mismatches).

    Args:
        credentials: The HTTP Bearer credentials extracted by FastAPI.

    Returns:
        The authenticated user_id from the JWT 'sub' claim.

    Raises:
        HTTPException: 401 if the token is missing, expired, or invalid.
        HTTPException: 500 if the authentication service is misconfigured.
    """
    token = credentials.credentials
    jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")

    # Fast path: local JWT verification
    if jwt_secret:
        try:
            payload = pyjwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256", "HS384", "HS512"],
                audience="authenticated",
            )
            user_id: str | None = payload.get("sub")
            if user_id:
                return user_id
        except pyjwt.ExpiredSignatureError as exc:
            _logger.warning("jwt_expired", token_prefix=token[:10])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
            ) from exc
        except pyjwt.InvalidTokenError as e:
            # Log the specific error before falling through
            _logger.warning(
                "jwt_local_verify_failed",
                error=str(e),
                error_type=type(e).__name__,
                token_prefix=token[:10],
            )
            pass

    # Slow path: verify via Supabase Auth API using the user's own token
    try:
        import httpx

        supabase_url = os.environ.get("SUPABASE_URL", "")
        service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if supabase_url and service_role_key:
            resp = httpx.get(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": service_role_key,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                user_data = resp.json()
                user_id_from_api = user_data.get("id")
                if user_id_from_api:
                    _logger.info("jwt_verified_via_admin", user_id=user_id_from_api)
                    return str(user_id_from_api)
            else:
                _logger.warning(
                    "jwt_admin_verify_failed",
                    status=resp.status_code,
                    body=resp.text[:200],
                    token_prefix=token[:10],
                )
    except Exception as exc:
        _logger.warning("jwt_admin_verify_failed", error=str(exc), token_prefix=token[:10])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token.",
    )
