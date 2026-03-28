"""Supabase JWT verification for FastAPI endpoints.

Provides a dependency that extracts and verifies the JWT from the
Authorization header, returning the authenticated user_id.
"""

from __future__ import annotations

import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

_bearer_scheme = HTTPBearer()


async def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """Verify a Supabase JWT and return the user_id.

    Extracts the Bearer token from the Authorization header, decodes it
    using the Supabase JWT secret, and returns the 'sub' claim as the
    authenticated user_id.

    Args:
        credentials: The HTTP Bearer credentials extracted by FastAPI.

    Returns:
        The authenticated user_id from the JWT 'sub' claim.

    Raises:
        HTTPException: 401 if the token is missing, expired, or invalid.
    """
    token = credentials.credentials
    jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")

    if not jwt_secret:
        _logger.error("supabase_jwt_secret_not_set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service misconfigured.",
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject.",
            )
        return user_id

    except jwt.ExpiredSignatureError as exc:
        _logger.warning("jwt_expired", token_prefix=token[:10])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        _logger.warning("jwt_invalid", error=str(exc), token_prefix=token[:10])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc
