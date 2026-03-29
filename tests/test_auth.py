"""Tests for JWT authentication logic.

Covers valid tokens, expired tokens, missing headers, malformed tokens,
missing claims, wrong audience, and missing JWT secret configuration.
"""

from __future__ import annotations

import os
import time
from unittest.mock import patch

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.utils.auth import verify_supabase_jwt

# ---------- Test App ----------

_test_app = FastAPI()
JWT_SECRET = "test-jwt-secret-for-unit-tests-ok"
TEST_USER_ID = "user_auth_test_001"


@_test_app.get("/protected")
async def protected_endpoint(user_id: str = Depends(verify_supabase_jwt)):
    """A simple protected endpoint for testing auth."""
    return {"user_id": user_id}


@pytest.fixture
def auth_client():
    """Create a TestClient for the auth test app."""
    return TestClient(_test_app)


def _make_token(
    sub: str | None = TEST_USER_ID,
    exp: int | None = None,
    aud: str = "authenticated",
    algorithm: str = "HS256",
    secret: str = JWT_SECRET,
) -> str:
    """Generate a JWT token for testing."""
    payload: dict = {}
    if sub is not None:
        payload["sub"] = sub
    if exp is not None:
        payload["exp"] = exp
    else:
        payload["exp"] = int(time.time()) + 3600  # 1 hour from now
    payload["aud"] = aud
    return jwt.encode(payload, secret, algorithm=algorithm)


# ---------- Tests ----------


def test_valid_jwt_returns_user_id(auth_client):
    """A valid JWT with correct secret/aud/sub returns 200 with user_id."""
    token = _make_token()
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["user_id"] == TEST_USER_ID


def test_expired_jwt_returns_401(auth_client):
    """An expired JWT returns 401."""
    token = _make_token(exp=int(time.time()) - 3600)  # Expired 1 hour ago
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 401


def test_missing_auth_header_returns_error(auth_client):
    """A request without Authorization header returns an error (401 or 403)."""
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get("/protected")
    # FastAPI's HTTPBearer returns 401 or 403 depending on version
    assert response.status_code in (401, 403)


def test_malformed_jwt_returns_401(auth_client):
    """A malformed JWT string returns 401."""
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": "Bearer not.a.valid.jwt.token"},
        )
    assert response.status_code == 401


def test_empty_jwt_secret_returns_500(auth_client):
    """An empty JWT secret environment variable returns 500."""
    token = _make_token()
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": ""}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 500


def test_missing_sub_claim_returns_401(auth_client):
    """A JWT without the 'sub' claim returns 401."""
    token = _make_token(sub=None)
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 401


def test_wrong_audience_returns_401(auth_client):
    """A JWT with wrong audience returns 401."""
    token = _make_token(aud="wrong_audience")
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 401


def test_wrong_secret_returns_401(auth_client):
    """A JWT signed with a different secret returns 401."""
    token = _make_token(secret="wrong-secret-padding-for-length!!")
    with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET}):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 401
