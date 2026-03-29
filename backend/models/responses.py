"""Typed Pydantic response models for CaseMate API endpoints.

Replaces bare dict returns with structured, typed response models
to ensure consistent API contracts and full type safety. Includes
standardized error response models for OpenAPI documentation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


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


# ---------- Standardized Error Response Models ----------


class ErrorResponse(BaseModel):
    """Standard error response returned by all CaseMate API endpoints.

    Attributes:
        detail: Human-readable error description.
    """

    detail: str = Field(
        ...,
        examples=["Profile not found. Complete onboarding first."],
    )


class NotFoundResponse(ErrorResponse):
    """404 Not Found — the requested resource does not exist.

    Attributes:
        detail: Description of the missing resource.
    """

    detail: str = Field(
        ...,
        examples=["Profile not found. Complete onboarding first."],
    )


class ForbiddenResponse(ErrorResponse):
    """403 Forbidden — the user is not authorized to access this resource.

    Attributes:
        detail: Description of the access denial.
    """

    detail: str = Field(
        ...,
        examples=["Access denied."],
    )


class PaymentRequiredResponse(ErrorResponse):
    """402 Payment Required — free tier limit exhausted.

    Attributes:
        detail: Description of the payment requirement.
    """

    detail: str = Field(
        ...,
        examples=[
            "Free tier limit reached (5 messages/month). "
            "Subscribe for unlimited access."
        ],
    )


class RateLimitResponse(ErrorResponse):
    """429 Too Many Requests — rate limit exceeded.

    Attributes:
        detail: Rate limit description with retry guidance.
    """

    detail: str = Field(
        ...,
        examples=["Rate limit exceeded. Try again in 60 seconds."],
    )


class ServiceUnavailableResponse(ErrorResponse):
    """503 Service Unavailable — backend dependency is down.

    Attributes:
        detail: Description of the service disruption.
    """

    detail: str = Field(
        ...,
        examples=["AI service temporarily unavailable. Please try again shortly."],
    )


class BadRequestResponse(ErrorResponse):
    """400 Bad Request — the request is malformed or invalid.

    Attributes:
        detail: Description of the validation error.
    """

    detail: str = Field(
        ...,
        examples=["Unsupported file type: image/gif"],
    )


class PayloadTooLargeResponse(ErrorResponse):
    """413 Payload Too Large — the uploaded file exceeds the size limit.

    Attributes:
        detail: Description of the size constraint.
    """

    detail: str = Field(
        ...,
        examples=["File too large. Maximum size is 25MB."],
    )


class InternalErrorResponse(ErrorResponse):
    """500 Internal Server Error — an unexpected error occurred.

    Attributes:
        detail: Description of the server-side failure.
    """

    detail: str = Field(
        ...,
        examples=["AI service temporarily unavailable."],
    )
