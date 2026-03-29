"""Typed Pydantic response models for CaseMate API endpoints.

Replaces bare dict returns with structured, typed response models
to ensure consistent API contracts and full type safety.
"""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response for uptime monitoring.

    Attributes:
        status: Service status string (typically 'ok').
        version: The current API version string.
    """

    status: str
    version: str


class DeleteResponse(BaseModel):
    """Generic deletion confirmation response.

    Attributes:
        status: Deletion status string (typically 'deleted').
    """

    status: str


class WaitlistResponse(BaseModel):
    """Waitlist signup confirmation response.

    Attributes:
        success: Whether the signup was successfully recorded.
    """

    success: bool
