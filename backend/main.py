"""FastAPI application for the CaseMate AI Legal Assistant backend.

Provides REST API endpoints for chat, profile management, document analysis,
and action generation (demand letters, rights summaries, checklists).
"""

# ruff: noqa: E402

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

load_dotenv()  # Load .env before any os.environ.get() calls
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, Literal, TypedDict, cast

import anthropic
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from backend.actions.checklist_generator import generate_checklist
from backend.actions.letter_generator import generate_demand_letter
from backend.actions.rights_generator import generate_rights_summary
from backend.audio.transcriber import transcribe_audio
from backend.deadlines.detector import detect_and_save_deadlines
from backend.deadlines.tracker import (
    DeadlineCreateRequest,
    DeadlineUpdateRequest,
    create_deadline,
    delete_deadline,
    list_deadlines,
    update_deadline,
)
from backend.documents.analyzer import analyze_document
from backend.documents.extractor import extract_text
from backend.export.email_sender import send_document_email
from backend.export.pdf_generator import (
    generate_checklist_document,
    generate_demand_letter_document,
    generate_rights_document,
    generate_text_document,
)
from backend.knowledge.rights_library import (
    get_all_guides,
    get_domains,
    get_guide_by_id,
    get_guides_by_domain,
)
from backend.legal.classifier import classify_with_llm_fallback
from backend.memory.conversation_store import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    save_conversation,
)
from backend.memory.injector import build_system_prompt, build_system_prompt_parts
from backend.memory.profile import (
    get_free_message_count,
    get_profile,
    increment_free_message_count,
    update_profile,
)
from backend.memory.updater import update_profile_from_conversation
from backend.models.legal_profile import LegalProfile
from backend.models.responses import (
    BadRequestResponse,
    ForbiddenResponse,
    InternalErrorResponse,
    NotFoundResponse,
    PayloadTooLargeResponse,
    PaymentRequiredResponse,
    RateLimitResponse,
    ServiceUnavailableResponse,
)
from backend.payments.stripe_webhooks import handle_webhook
from backend.payments.subscription import (
    CheckoutSessionResponse,
    SubscriptionStatus,
    cancel_subscription,
    create_checkout_session,
    get_subscription_status,
)
from backend.referrals.matcher import find_attorneys, get_referral_suggestions
from backend.utils.audit_log import AuditEventType, record_audit_event
from backend.utils.auth import verify_supabase_jwt
from backend.utils.client import get_anthropic_client
from backend.utils.lifecycle import get_lifecycle_manager, lifecycle_middleware
from backend.utils.llm_router import get_llm_router
from backend.utils.logger import configure_logging, get_logger
from backend.utils.rate_limiter import rate_limit
from backend.utils.telemetry import MetricsCollector, get_metrics_response, telemetry_middleware
from backend.utils.token_budget import TokenBudgetManager, estimate_tokens
from backend.workflows.engine import (
    WorkflowStepUpdateRequest,
    get_workflow,
    list_workflows,
    start_workflow,
    update_workflow_step,
)
from backend.workflows.templates.definitions import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_domain,
)

configure_logging()
_logger = get_logger(__name__)

_OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Health & Monitoring",
        "description": "Service health checks, metrics, and audit verification.",
    },
    {
        "name": "Chat",
        "description": (
            "Core conversation endpoints. Each response is personalized using "
            "the user's legal profile, state-specific statutes, and conversation "
            "history with token budget management."
        ),
    },
    {
        "name": "Profile",
        "description": (
            "Legal profile CRUD. The profile is the persistent memory layer — "
            "state, housing, employment, legal facts, and active issues."
        ),
    },
    {
        "name": "Actions",
        "description": (
            "AI-generated legal documents: demand letters, rights summaries, "
            "and next-steps checklists — all pre-filled with profile context "
            "and statute citations."
        ),
    },
    {
        "name": "Documents",
        "description": (
            "Upload legal documents (PDF, images) for text extraction and "
            "AI-powered analysis. Extracted facts are injected into the profile."
        ),
    },
    {
        "name": "Audio",
        "description": "Audio recording transcription via speech-to-text API.",
    },
    {
        "name": "Conversations",
        "description": "List, retrieve, and delete conversation history.",
    },
    {
        "name": "Deadlines",
        "description": (
            "Auto-detected and manually created legal deadline tracking with status management."
        ),
    },
    {
        "name": "Rights Library",
        "description": (
            "19 pre-built Know Your Rights guides across 10 legal domains "
            "with rights, action steps, deadlines, and citations."
        ),
    },
    {
        "name": "Workflows",
        "description": (
            "Guided step-by-step legal process templates (eviction defense, "
            "wage claims, small claims, etc.)."
        ),
    },
    {
        "name": "Export",
        "description": "Generate branded PDFs and send documents via email.",
    },
    {
        "name": "Attorneys",
        "description": (
            "Attorney referral search with state and specialty-based weighted relevance scoring."
        ),
    },
    {
        "name": "Payments",
        "description": (
            "Stripe subscription lifecycle: checkout sessions, webhook "
            "processing, subscription status, and cancellation."
        ),
    },
]

app = FastAPI(
    title="CaseMate — AI Legal Assistant",
    description=(
        "## Personalized legal guidance powered by persistent memory\n\n"
        "CaseMate is an AI legal assistant that **remembers your situation** — "
        "your state, housing, employment, active legal disputes, and facts "
        "extracted from past conversations. Every response cites jurisdiction-"
        "specific statutes and calculates concrete remedies.\n\n"
        "### Core capabilities\n\n"
        "- **Persistent legal memory** — profile auto-updates from every "
        "conversation\n"
        "- **50-state coverage** — 10 legal domains × 50 states + federal\n"
        "- **Action generation** — demand letters, rights summaries, "
        "checklists\n"
        "- **Document analysis** — PDF/image upload with fact extraction\n"
        "- **Deadline tracking** — auto-detected from conversations\n"
        "- **SSE streaming** — real-time token-by-token chat responses\n\n"
        "### Authentication\n\n"
        "All endpoints except `/health`, `/api/waitlist`, and "
        "`/api/payments/webhook` require a valid Supabase JWT in the "
        "`Authorization: Bearer <token>` header."
    ),
    version="0.5.0",
    openapi_tags=_OPENAPI_TAGS,
    contact={
        "name": "CaseMate Support",
        "url": "https://casematelaw.com",
        "email": "support@casematelaw.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------- CORS ----------

_allowed_origins = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8081",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------- Lifecycle middleware — graceful shutdown with request draining ----------

app.middleware("http")(lifecycle_middleware)

# ---------- Telemetry middleware — traces every request ----------

app.middleware("http")(telemetry_middleware)


# ---------- Security headers middleware ----------


@app.middleware("http")
async def security_headers_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Add security headers to every HTTP response.

    Applies defense-in-depth headers that protect against common web
    vulnerabilities (clickjacking, MIME sniffing, XSS, data leakage).
    HSTS is only set for non-localhost origins to avoid breaking local
    development.

    Args:
        request: The incoming FastAPI request.
        call_next: The next middleware or route handler.

    Returns:
        The response with security headers attached.
    """
    response: Response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.supabase.co https://api.anthropic.com https://api.stripe.com"
    )

    # Only add HSTS for non-localhost deployments
    host = request.headers.get("host", "")
    if "localhost" not in host and "127.0.0.1" not in host:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ---------- Lifecycle events — startup and shutdown ----------


@app.on_event("startup")
async def _on_startup() -> None:
    """Initialize lifecycle manager and register shutdown hooks."""
    manager = get_lifecycle_manager(drain_timeout=30)
    await manager.startup()


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    """Gracefully drain in-flight requests and run cleanup hooks."""
    manager = get_lifecycle_manager()
    await manager.shutdown()


# ---------- Token budget manager for context window optimization ----------

_token_budget = TokenBudgetManager()

# ---------- Middleware to stash user_id on request.state ----------


@app.middleware("http")
async def attach_user_id_to_state(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Extract user_id from JWT and attach to request.state for rate limiter.

    Parses the Authorization header to extract the user_id from the JWT
    without full verification (auth is handled by endpoint dependencies).
    Falls back to 'anonymous' if the header is missing or unparseable.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            import jwt as pyjwt

            payload = pyjwt.decode(token, options={"verify_signature": False})
            request.state.user_id = payload.get("sub", "anonymous")
        except Exception as exc:
            _logger.warning(
                "jwt_decode_fallback_to_anonymous",
                error_type=type(exc).__name__,
                error=str(exc),
            )
            request.state.user_id = "anonymous"
    else:
        request.state.user_id = "anonymous"
    response: Response = await call_next(request)
    return response


# ---------- Request / Response schemas ----------


class ChatRequest(BaseModel):
    """Request body for the chat endpoint.

    Attributes:
        message: The user's message text (max 10,000 characters).
        conversation_id: Optional existing conversation ID to continue.
    """

    message: str = Field(..., max_length=10_000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Response body for the chat endpoint.

    Attributes:
        conversation_id: The conversation ID (new or existing).
        response: CaseMate's response text.
        legal_area: The classified legal domain for this message.
    """

    conversation_id: str
    response: str
    legal_area: str


class ProfileRequest(BaseModel):
    """Request body for creating or updating a user profile.

    Attributes:
        display_name: User's first name (max 100 characters).
        state: Two-letter state code (max 2 characters).
        housing_situation: Description of housing situation (max 500 characters).
        employment_type: Employment classification (max 200 characters).
        family_status: Family and dependent information (max 500 characters).
    """

    display_name: str = Field(..., max_length=100)
    state: str = Field(..., max_length=2)
    housing_situation: str = Field(..., max_length=500)
    employment_type: str = Field(..., max_length=200)
    family_status: str = Field(..., max_length=500)
    language_preference: Literal["en", "es"] = Field(default="en")


class ActionRequest(BaseModel):
    """Request body for action generation endpoints.

    Attributes:
        context: Description of the situation for the action (max 5,000 characters).
    """

    context: str = Field(..., max_length=5_000)


class CreateCheckoutRequest(BaseModel):
    """Request body for creating a Stripe checkout session.

    Attributes:
        price_id: The Stripe price ID for the subscription plan.
        success_url: URL to redirect to after successful payment.
        cancel_url: URL to redirect to if the user cancels checkout.
    """

    price_id: str = Field(..., max_length=200)
    success_url: str = Field(..., max_length=2000)
    cancel_url: str = Field(..., max_length=2000)


# ---------- Rate limit dependencies ----------

_chat_rate_limit = rate_limit(max_requests=10, window_seconds=60)
_actions_rate_limit = rate_limit(max_requests=5, window_seconds=60)
_documents_rate_limit = rate_limit(max_requests=3, window_seconds=60)

# ---------- Subscription gate ----------

FREE_TIER_MESSAGE_LIMIT = 5


async def require_subscription_or_free_tier(
    user_id: str = Depends(verify_supabase_jwt),
) -> str:
    """Verify the user has an active subscription or free messages remaining.

    Free tier users get 5 messages per month. Paid subscribers have unlimited access.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        The verified user_id.

    Raises:
        HTTPException: 402 if the user has exhausted free messages and has no subscription.
    """
    sub_status = await get_subscription_status(user_id)
    if sub_status.is_active:
        return user_id

    free_count = await get_free_message_count(user_id)
    if free_count >= FREE_TIER_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=402,
            detail=(
                f"Free tier limit reached ({FREE_TIER_MESSAGE_LIMIT} messages/month). "
                "Subscribe for unlimited access."
            ),
        )
    return user_id


# ---------- Max upload size ----------

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


# ---------- Endpoints ----------


@app.get("/health", tags=["Health & Monitoring"])
async def health_check() -> dict[str, object]:
    """Health check endpoint with lifecycle state and uptime.

    Returns lifecycle state, active request count, and uptime alongside
    the standard status/version fields for richer monitoring.
    """
    lifecycle = get_lifecycle_manager().get_health()
    return {
        "status": "ok",
        "version": "0.5.0",
        "lifecycle": lifecycle,
    }


@app.get("/api/llm/status", tags=["Health & Monitoring"])
async def llm_router_status(
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Return the current LLM router status with per-provider metrics.

    Shows which providers are healthy, their circuit breaker states,
    call counts, failure rates, and average latencies. Useful for
    debugging degraded responses and monitoring failover events.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with per-provider metrics including circuit breaker state,
        call counts, failure counts, and average latency.
    """
    router = get_llm_router()
    return {"llm_router": router.metrics}


@app.get("/metrics", tags=["Health & Monitoring"])
async def metrics_endpoint() -> Response:
    """Expose in-process metrics for Prometheus scraping or monitoring.

    Returns counters (total requests, errors), histograms (latency p50/p95/p99),
    and labeled counters (status code distribution, legal area classification).
    """
    return get_metrics_response()


@app.get("/api/audit/verify", tags=["Health & Monitoring"])
async def verify_audit_chain(
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Verify the integrity of the user's audit event hash chain.

    Reads the user's audit events from Supabase and checks that each
    event's cryptographic hash correctly links to its predecessor,
    detecting any tampering or deletion.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        VerificationResult with validity status and events checked.
    """
    from backend.utils.audit_log import AuditLog

    audit_log = AuditLog.get_instance()
    result = await audit_log.verify_chain(user_id)
    return {"verification": result.model_dump(mode="json")}


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    responses={
        402: {"model": PaymentRequiredResponse},
        404: {"model": NotFoundResponse},
        429: {"model": RateLimitResponse},
        500: {"model": InternalErrorResponse},
        503: {"model": ServiceUnavailableResponse},
    },
)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(require_subscription_or_free_tier),
    _rate: None = Depends(_chat_rate_limit),
) -> ChatResponse:
    """Process a user message and return CaseMate's response.

    Supports multi-turn conversations by loading conversation history
    and applying token budget management to keep the context within
    the model's window. Uses circuit breaker for Anthropic API resilience.

    Args:
        request: The chat request containing the message.
        background_tasks: FastAPI background task manager.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        ChatResponse with the conversation ID, CaseMate's response, and
        the classified legal area.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if the Claude API call fails.
        HTTPException: 503 if the circuit breaker is open.
    """
    metrics = MetricsCollector.get_instance()
    chat_start = time.monotonic()
    _logger.info("chat_request", user_id=user_id)

    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding first.")

    # Classify with confidence scoring for observability
    client = get_anthropic_client()
    classification = await classify_with_llm_fallback(request.message, client=client)
    legal_area = classification.domain
    metrics.increment_label("legal_area_classified", legal_area)
    metrics.increment_label("classifier_confidence_bucket", f"{classification.confidence:.1f}")

    system_prompt = build_system_prompt(profile, request.message)
    static_prefix, dynamic_suffix = build_system_prompt_parts(profile, request.message)

    # Load or create conversation
    conversation = None
    if request.conversation_id:
        conversation = await get_conversation(request.conversation_id, user_id)

    if conversation is None:
        conversation = await create_conversation(user_id, legal_area=legal_area)

    # Add user message to conversation
    conversation.add_message("user", request.message, legal_area=legal_area)

    # Apply token budget management to conversation history
    all_messages = conversation.to_anthropic_messages()
    system_tokens = estimate_tokens(system_prompt)
    budget_result = _token_budget.apply(all_messages, system_prompt_tokens=system_tokens)
    api_messages = budget_result.messages

    if budget_result.was_truncated:
        _logger.info(
            "token_budget_truncated",
            user_id=user_id,
            original_messages=budget_result.original_count,
            final_messages=budget_result.final_count,
            summary_prepended=budget_result.summary_prepended,
        )

    try:
        router = get_llm_router()
        llm_response = await router.chat(system_prompt, api_messages)
        assistant_response = llm_response.content

        if llm_response.was_fallback:
            _logger.info(
                "chat_used_fallback_provider",
                user_id=user_id,
                provider=llm_response.provider,
                model=llm_response.model,
            )

    except Exception as exc:
        _logger.error(
            "llm_router_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable.") from exc

    # Record chat latency metric
    chat_latency = time.monotonic() - chat_start
    metrics.observe_latency("chat_latency_seconds", chat_latency)
    metrics.increment("chat_requests_total")

    # Add assistant response to conversation and save
    conversation.add_message("assistant", assistant_response, legal_area=legal_area)
    if not conversation.legal_area:
        conversation.legal_area = legal_area

    background_tasks.add_task(save_conversation, conversation)

    # Schedule background profile update
    conversation_messages = [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": assistant_response},
    ]
    background_tasks.add_task(
        update_profile_from_conversation,
        user_id,
        conversation_messages,
    )

    # Schedule background deadline detection
    background_tasks.add_task(
        detect_and_save_deadlines,
        user_id,
        conversation_messages,
        conversation.id,
    )

    # Record audit event for the chat interaction
    background_tasks.add_task(
        record_audit_event,
        AuditEventType.CONVERSATION_CREATED,
        user_id,
        {
            "conversation_id": conversation.id,
            "legal_area": legal_area,
            "classifier_confidence": str(round(classification.confidence, 2)),
        },
    )

    _logger.info(
        "chat_response",
        user_id=user_id,
        legal_area=legal_area,
        conversation_id=conversation.id,
        response_length=len(assistant_response),
        classifier_confidence=classification.confidence,
        classifier_method=classification.method,
        token_budget_truncated=budget_result.was_truncated,
        chat_latency_ms=round(chat_latency * 1000, 2),
    )

    # Track free tier usage for non-subscribers
    background_tasks.add_task(increment_free_message_count, user_id)

    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        legal_area=legal_area,
    )


@app.get(
    "/api/chat/{conversation_id}/stream",
    tags=["Chat"],
    responses={
        404: {"model": NotFoundResponse},
        429: {"model": RateLimitResponse},
        503: {"model": ServiceUnavailableResponse},
    },
)
async def chat_stream(
    conversation_id: str,
    message: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_supabase_jwt),
    _rate: None = Depends(_chat_rate_limit),
) -> StreamingResponse:
    """Stream CaseMate's response via Server-Sent Events (SSE).

    Provides real-time token-by-token streaming for a more responsive UX.
    Each SSE event contains a JSON payload with the event type and data:
      - type: "token" — a new text chunk from the response
      - type: "done" — streaming complete, includes full response metadata
      - type: "error" — an error occurred during streaming

    Args:
        conversation_id: The conversation UUID to continue.
        message: The user's message (passed as query parameter).
        background_tasks: FastAPI background task manager.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        StreamingResponse with text/event-stream content type.

    Raises:
        HTTPException: 404 if the user profile or conversation is not found.
        HTTPException: 503 if the circuit breaker is open.
    """
    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    conversation = await get_conversation(conversation_id, user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    anthropic_client = get_anthropic_client()
    classification = await classify_with_llm_fallback(message, client=anthropic_client)
    legal_area = classification.domain
    system_prompt = build_system_prompt(profile, message)
    static_prefix, dynamic_suffix = build_system_prompt_parts(profile, message)

    conversation.add_message("user", message, legal_area=legal_area)

    all_messages = conversation.to_anthropic_messages()
    system_tokens = estimate_tokens(system_prompt)
    budget_result = _token_budget.apply(all_messages, system_prompt_tokens=system_tokens)
    api_messages = budget_result.messages

    async def _generate_sse() -> AsyncGenerator[str, None]:
        """Generate SSE from the LLM router with automatic failover.

        Uses the LLM router to stream from Anthropic Claude.

        Yields SSE-formatted strings with token chunks and metadata.
        """
        metrics = MetricsCollector.get_instance()
        stream_start = time.monotonic()
        full_response_parts: list[str] = []

        try:
            router = get_llm_router()
            provider_name, stream_obj = await router.stream(system_prompt, api_messages)

            async with cast(Any, stream_obj) as anthropic_stream:
                async for text in anthropic_stream.text_stream:
                    full_response_parts.append(text)
                    event_data = json.dumps({"type": "token", "content": text})
                    yield f"data: {event_data}\n\n"

            assistant_response = "".join(full_response_parts)
            stream_latency = time.monotonic() - stream_start
            metrics.observe_latency("chat_stream_latency_seconds", stream_latency)
            metrics.increment("chat_stream_requests_total")

            # Add assistant response and schedule background tasks
            conversation.add_message("assistant", assistant_response, legal_area=legal_area)
            if not conversation.legal_area:
                conversation.legal_area = legal_area

            background_tasks.add_task(save_conversation, conversation)
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response},
            ]
            background_tasks.add_task(
                update_profile_from_conversation, user_id, conversation_messages
            )
            background_tasks.add_task(
                detect_and_save_deadlines, user_id, conversation_messages, conversation.id
            )

            done_data = json.dumps(
                {
                    "type": "done",
                    "conversation_id": conversation_id,
                    "legal_area": legal_area,
                    "response_length": len(assistant_response),
                    "provider": provider_name,
                    "latency_ms": round(stream_latency * 1000, 2),
                }
            )
            yield f"data: {done_data}\n\n"

        except Exception as exc:
            _logger.error("stream_api_error", user_id=user_id, error=str(exc))
            error_data = json.dumps(
                {
                    "type": "error",
                    "message": "AI service error. Please try again.",
                }
            )
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        _generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post(
    "/api/profile",
    tags=["Profile"],
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def upsert_profile(
    request: ProfileRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Create or update a user's legal profile.

    Args:
        request: The profile data to upsert.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the profile data as confirmed by Supabase.

    Raises:
        HTTPException: 500 if the upsert operation fails.
    """
    _logger.info("profile_upsert_request", user_id=user_id)

    profile = LegalProfile(
        user_id=user_id,
        display_name=request.display_name,
        state=request.state,
        housing_situation=request.housing_situation,
        employment_type=request.employment_type,
        family_status=request.family_status,
        language_preference=request.language_preference,
    )

    try:
        updated = await update_profile(profile)
        await record_audit_event(
            AuditEventType.PROFILE_UPDATED,
            user_id,
            {"state": request.state, "action": "upsert"},
        )
        return {"profile": updated.model_dump(mode="json")}
    except (ValueError, RuntimeError) as exc:
        _logger.error(
            "profile_upsert_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(
    "/api/profile/update",
    tags=["Profile"],
    responses={
        404: {"model": NotFoundResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def patch_profile(
    request: Request,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Partially update a user's legal profile.

    Accepts a JSON body with any subset of profile fields to update.
    Fetches the existing profile, merges the updates, and upserts.

    Args:
        request: The raw request containing partial profile fields.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the updated profile data.

    Raises:
        HTTPException: 404 if no existing profile is found.
        HTTPException: 500 if the update operation fails.
    """
    body = await request.json()
    _logger.info("profile_patch_request", user_id=user_id, fields=list(body.keys()))

    existing = await get_profile(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found.")

    # Merge updates into existing profile
    update_data = existing.model_dump()
    allowed_fields = {
        "display_name",
        "state",
        "housing_situation",
        "employment_type",
        "family_status",
        "language_preference",
    }
    for key, value in body.items():
        if key in allowed_fields:
            update_data[key] = value

    try:
        merged_profile = LegalProfile.model_validate(update_data)
        updated = await update_profile(merged_profile)
        await record_audit_event(
            AuditEventType.PROFILE_UPDATED,
            user_id,
            {"fields": ",".join(body.keys()), "action": "patch"},
        )
        return {"profile": updated.model_dump(mode="json")}
    except (ValueError, RuntimeError) as exc:
        _logger.error(
            "profile_patch_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/api/profile/{user_id}",
    tags=["Profile"],
    responses={
        403: {"model": ForbiddenResponse},
        404: {"model": NotFoundResponse},
    },
)
async def get_user_profile(
    user_id: str,
    authenticated_user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Fetch a user's legal profile.

    Users can only fetch their own profile.

    Args:
        user_id: The user ID from the URL path.
        authenticated_user_id: The authenticated user ID from JWT.

    Returns:
        Dict with the profile data.

    Raises:
        HTTPException: 403 if attempting to access another user's profile.
        HTTPException: 404 if the profile is not found.
    """
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"profile": profile.model_dump(mode="json")}


@app.get("/api/conversations", tags=["Conversations"])
async def list_user_conversations(
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List the authenticated user's conversations.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with a list of conversation summaries.
    """
    conversations = await list_conversations(user_id)
    return {"conversations": conversations}


@app.get(
    "/api/conversations/{conversation_id}",
    tags=["Conversations"],
    responses={404: {"model": NotFoundResponse}},
)
async def get_user_conversation(
    conversation_id: str,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Load a specific conversation by ID.

    Args:
        conversation_id: The conversation UUID.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the full conversation data.

    Raises:
        HTTPException: 404 if conversation not found or not owned by user.
    """
    conversation = await get_conversation(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"conversation": conversation.model_dump(mode="json")}


@app.delete(
    "/api/conversations/{conversation_id}",
    tags=["Conversations"],
    responses={404: {"model": NotFoundResponse}},
)
async def delete_user_conversation(
    conversation_id: str,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, str]:
    """Delete a conversation by ID.

    Args:
        conversation_id: The conversation UUID.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with status message.

    Raises:
        HTTPException: 404 if conversation not found or not owned by user.
    """
    deleted = await delete_conversation(conversation_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "deleted"}


@app.post(
    "/api/actions/letter",
    tags=["Actions"],
    responses={
        402: {"model": PaymentRequiredResponse},
        404: {"model": NotFoundResponse},
        429: {"model": RateLimitResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def create_demand_letter(
    request: ActionRequest,
    user_id: str = Depends(require_subscription_or_free_tier),
    _rate: None = Depends(_actions_rate_limit),
) -> dict[str, object]:
    """Generate a demand letter for the user.

    Args:
        request: The action request with context.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        Dict with the generated DemandLetter data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        letter = await generate_demand_letter(profile, request.context)
        return {"letter": letter.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "demand_letter_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate demand letter.") from exc


@app.post(
    "/api/actions/rights",
    tags=["Actions"],
    responses={
        402: {"model": PaymentRequiredResponse},
        404: {"model": NotFoundResponse},
        429: {"model": RateLimitResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def create_rights_summary(
    request: ActionRequest,
    user_id: str = Depends(require_subscription_or_free_tier),
    _rate: None = Depends(_actions_rate_limit),
) -> dict[str, object]:
    """Generate a rights summary for the user.

    Args:
        request: The action request with context.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        Dict with the generated RightsSummary data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        summary = await generate_rights_summary(profile, request.context)
        return {"rights": summary.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "rights_summary_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate rights summary.") from exc


@app.post(
    "/api/actions/checklist",
    tags=["Actions"],
    responses={
        402: {"model": PaymentRequiredResponse},
        404: {"model": NotFoundResponse},
        429: {"model": RateLimitResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def create_checklist(
    request: ActionRequest,
    user_id: str = Depends(require_subscription_or_free_tier),
    _rate: None = Depends(_actions_rate_limit),
) -> dict[str, object]:
    """Generate a next-steps checklist for the user.

    Args:
        request: The action request with context.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        Dict with the generated Checklist data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        checklist = await generate_checklist(profile, request.context)
        return {"checklist": checklist.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "checklist_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate checklist.") from exc


@app.post(
    "/api/documents",
    tags=["Documents"],
    responses={
        400: {"model": BadRequestResponse},
        402: {"model": PaymentRequiredResponse},
        404: {"model": NotFoundResponse},
        413: {"model": PayloadTooLargeResponse},
        429: {"model": RateLimitResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(require_subscription_or_free_tier),
    _rate: None = Depends(_documents_rate_limit),
) -> dict[str, object]:
    """Upload and analyze a legal document.

    Extracts text from the uploaded file, fetches the user's profile,
    and sends both to Claude for structured legal analysis.

    Args:
        file: The uploaded file (PDF, text, or image).
        background_tasks: FastAPI background task manager.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        Dict with the document analysis results including document_type,
        key_facts, red_flags, and summary.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 400 if the file type is not supported.
        HTTPException: 413 if the file exceeds the size limit.
        HTTPException: 500 if analysis fails.
    """
    _logger.info(
        "document_upload",
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
    )

    # Check file size
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)}MB.",
        )

    try:
        text = extract_text(contents, file.content_type or "application/pdf")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        analysis = await analyze_document(text, profile)
        await record_audit_event(
            AuditEventType.DOCUMENT_ANALYZED,
            user_id,
            {"filename": file.filename or "unknown", "size_bytes": len(contents)},
        )
        return analysis
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "document_analysis_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to analyze document.") from exc


# ---------- Audio Transcription Endpoints ----------

_AUDIO_MAX_BYTES = 25 * 1024 * 1024  # 25 MB — Whisper API limit

_ALLOWED_AUDIO_TYPES: set[str] = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "video/mp4",
    "video/webm",
}


@app.post(
    "/api/audio/transcribe",
    tags=["Audio"],
    responses={
        400: {"model": BadRequestResponse},
        413: {"model": PayloadTooLargeResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def transcribe_audio_endpoint(
    file: UploadFile,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, str]:
    """Transcribe an audio file using speech-to-text.

    Accepts an uploaded audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm),
    sends it to the transcription API for speech-to-text, and returns
    the transcript text.

    Args:
        file: The uploaded audio file (max 25MB).
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with ``transcript`` (the transcribed text) and ``language``.

    Raises:
        HTTPException: 400 if the file type is not a supported audio format.
        HTTPException: 413 if the file exceeds 25MB.
        HTTPException: 500 if transcription fails.
    """
    _logger.info(
        "audio_transcribe_request",
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
    )

    # Validate content type
    content_type = (file.content_type or "").lower()
    if not content_type or content_type not in _ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {content_type}. "
            "Accepted formats: mp3, mp4, mpeg, mpga, m4a, wav, webm.",
        )

    # Read and check size
    contents = await file.read()
    if len(contents) > _AUDIO_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large. Maximum size is {_AUDIO_MAX_BYTES // (1024 * 1024)}MB.",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    try:
        transcript = await transcribe_audio(contents, language="en")
        return {"transcript": transcript, "language": "en"}
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        _logger.error(
            "audio_transcription_error",
            user_id=user_id,
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.") from exc


# ---------- Deadline Endpoints ----------


@app.post(
    "/api/deadlines",
    tags=["Deadlines"],
    responses={500: {"model": InternalErrorResponse}},
)
async def create_user_deadline(
    request: DeadlineCreateRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Create a new deadline manually.

    Args:
        request: The deadline creation data.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the created deadline.

    Raises:
        HTTPException: 500 if creation fails.
    """
    try:
        deadline = await create_deadline(
            user_id=user_id,
            title=request.title,
            date=request.date,
            legal_area=request.legal_area,
            notes=request.notes,
        )
        return {"deadline": deadline.model_dump(mode="json")}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/deadlines", tags=["Deadlines"])
async def list_user_deadlines(
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List the authenticated user's deadlines.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with a list of deadlines.
    """
    deadlines = await list_deadlines(user_id)
    return {"deadlines": [d.model_dump(mode="json") for d in deadlines]}


@app.patch(
    "/api/deadlines/{deadline_id}",
    tags=["Deadlines"],
    responses={
        404: {"model": NotFoundResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def update_user_deadline(
    deadline_id: str,
    request: DeadlineUpdateRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Update a deadline.

    Args:
        deadline_id: The deadline UUID.
        request: The update data.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the updated deadline.

    Raises:
        HTTPException: 404 if deadline not found.
    """
    try:
        deadline = await update_deadline(deadline_id, user_id, request)
        if not deadline:
            raise HTTPException(status_code=404, detail="Deadline not found.")
        return {"deadline": deadline.model_dump(mode="json")}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete(
    "/api/deadlines/{deadline_id}",
    tags=["Deadlines"],
    responses={404: {"model": NotFoundResponse}},
)
async def delete_user_deadline(
    deadline_id: str,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, str]:
    """Delete a deadline.

    Args:
        deadline_id: The deadline UUID.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with status message.

    Raises:
        HTTPException: 404 if deadline not found.
    """
    deleted = await delete_deadline(deadline_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Deadline not found.")
    return {"status": "deleted"}


# ---------- Rights Library Endpoints ----------


@app.get("/api/rights/domains", tags=["Rights Library"])
async def get_rights_domains(
    _user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List available legal rights domains with guide counts.

    Args:
        _user_id: Authenticated user ID from JWT (side-effect only).

    Returns:
        Dict with a list of domain summaries.
    """
    return {"domains": get_domains()}


@app.get("/api/rights/guides", tags=["Rights Library"])
async def get_rights_guides_list(
    domain: str | None = None,
    _user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List rights guides, optionally filtered by domain.

    Args:
        domain: Optional legal domain to filter by.
        _user_id: Authenticated user ID from JWT (side-effect only).

    Returns:
        Dict with a list of rights guides.
    """
    guides = get_guides_by_domain(domain) if domain else get_all_guides()
    return {"guides": [g.model_dump() for g in guides]}


@app.get(
    "/api/rights/guides/{guide_id}",
    tags=["Rights Library"],
    responses={404: {"model": NotFoundResponse}},
)
async def get_rights_guide(
    guide_id: str,
    _user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Get a specific rights guide by ID.

    Args:
        guide_id: The unique guide identifier.
        _user_id: Authenticated user ID from JWT (side-effect only).

    Returns:
        Dict with the rights guide data.

    Raises:
        HTTPException: 404 if guide not found.
    """
    guide = get_guide_by_id(guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found.")
    return {"guide": guide.model_dump()}


# ---------- Workflow Endpoints ----------


class WorkflowStartRequest(BaseModel):
    """Request body for starting a workflow.

    Attributes:
        template_id: The workflow template to start.
    """

    template_id: str


@app.get("/api/workflows/templates", tags=["Workflows"])
async def list_workflow_templates(
    domain: str | None = None,
    _user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List available workflow templates.

    Args:
        domain: Optional legal domain filter.
        _user_id: Authenticated user ID from JWT (side-effect only).

    Returns:
        Dict with a list of workflow templates.
    """
    templates = get_templates_by_domain(domain) if domain else get_all_templates()
    return {"templates": [t.model_dump() for t in templates]}


@app.post(
    "/api/workflows",
    tags=["Workflows"],
    responses={
        404: {"model": NotFoundResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def start_user_workflow(
    request: WorkflowStartRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Start a new workflow from a template.

    Args:
        request: The workflow start request with template_id.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the created workflow instance.

    Raises:
        HTTPException: 404 if template not found.
        HTTPException: 500 if creation fails.
    """
    template = get_template_by_id(request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found.")

    try:
        instance = await start_workflow(user_id, template)
        return {"workflow": instance.model_dump(mode="json")}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/workflows", tags=["Workflows"])
async def list_user_workflows(
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """List the authenticated user's active workflows.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with a list of workflow summaries.
    """
    workflows = await list_workflows(user_id)
    return {"workflows": workflows}


@app.get(
    "/api/workflows/{workflow_id}",
    tags=["Workflows"],
    responses={404: {"model": NotFoundResponse}},
)
async def get_user_workflow(
    workflow_id: str,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Load a specific workflow by ID.

    Args:
        workflow_id: The workflow instance UUID.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the full workflow data.

    Raises:
        HTTPException: 404 if workflow not found.
    """
    workflow = await get_workflow(workflow_id, user_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return {"workflow": workflow.model_dump(mode="json")}


@app.patch(
    "/api/workflows/{workflow_id}/steps",
    tags=["Workflows"],
    responses={
        404: {"model": NotFoundResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def update_user_workflow_step(
    workflow_id: str,
    request: WorkflowStepUpdateRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Update a step's status in a workflow.

    Args:
        workflow_id: The workflow instance UUID.
        request: The step update data.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with the updated workflow.

    Raises:
        HTTPException: 404 if workflow not found.
        HTTPException: 500 if update fails.
    """
    try:
        workflow = await update_workflow_step(workflow_id, user_id, request)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found.")
        return {"workflow": workflow.model_dump(mode="json")}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class _LetterContent(TypedDict, total=False):
    """Typed view of letter export content dict."""

    letter_text: str
    legal_citations: list[str]


class _RightsContent(TypedDict, total=False):
    """Typed view of rights export content dict."""

    summary_text: str
    key_rights: list[str]


class _ChecklistContent(TypedDict, total=False):
    """Typed view of checklist export content dict."""

    items: list[str]
    deadlines: list[str]


class _CustomContent(TypedDict, total=False):
    """Typed view of custom/generic export content dict."""

    title: str
    body: str
    sections: list[dict[str, str]]


# ---------- Export Endpoints ----------


class ExportDocumentRequest(BaseModel):
    """Request body for document export.

    Attributes:
        type: Document type (letter, rights, checklist, custom).
        content: Document content fields.
    """

    type: str
    content: dict[str, object]


class ExportEmailRequest(BaseModel):
    """Request body for email export.

    Attributes:
        type: Document type.
        content: Document content fields.
        email: Recipient email address.
    """

    type: str
    content: dict[str, object]
    email: str = Field(..., max_length=320)


@app.post(
    "/api/export/document",
    tags=["Export"],
    responses={
        400: {"model": BadRequestResponse},
        402: {"model": PaymentRequiredResponse},
    },
)
async def export_document(
    request: ExportDocumentRequest,
    user_id: str = Depends(require_subscription_or_free_tier),
) -> Response:
    """Generate and download a document.

    Args:
        request: The export request with document type and content.
        user_id: Authenticated user ID from JWT.

    Returns:
        The generated document as a downloadable file.

    Raises:
        HTTPException: 400 if document type is unknown.
    """
    profile = await get_profile(user_id)
    user_name = profile.display_name if profile else ""
    content = request.content

    if request.type == "letter":
        doc_bytes = generate_demand_letter_document(
            letter_text=str(content.get("letter_text", "")),
            legal_citations=cast(_LetterContent, content).get("legal_citations", []),
            user_name=user_name,
        )
        filename = "casemate_demand_letter.pdf"
    elif request.type == "rights":
        doc_bytes = generate_rights_document(
            summary_text=str(content.get("summary_text", "")),
            key_rights=cast(_RightsContent, content).get("key_rights", []),
            user_name=user_name,
        )
        filename = "casemate_rights_summary.pdf"
    elif request.type == "checklist":
        doc_bytes = generate_checklist_document(
            items=cast(_ChecklistContent, content).get("items", []),
            deadlines=cast(list[str | None], cast(_ChecklistContent, content).get("deadlines", [])),
            user_name=user_name,
        )
        filename = "casemate_checklist.pdf"
    elif request.type == "custom":
        doc_bytes = generate_text_document(
            title=str(content.get("title", "Legal Document")),
            content=str(content.get("body", "")),
            user_name=user_name,
            sections=cast(_CustomContent, content).get("sections"),
        )
        filename = "casemate_document.pdf"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown document type: {request.type}")

    return Response(
        content=doc_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post(
    "/api/export/email",
    tags=["Export"],
    responses={
        402: {"model": PaymentRequiredResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def export_email(
    request: ExportEmailRequest,
    user_id: str = Depends(require_subscription_or_free_tier),
) -> dict[str, object]:
    """Generate a document and send it via email.

    Args:
        request: The export request with document type, content, and email.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with send status.

    Raises:
        HTTPException: 500 if email sending fails.
    """
    profile = await get_profile(user_id)
    user_name = profile.display_name if profile else ""

    doc_bytes = generate_text_document(
        title=str(request.content.get("title", "Legal Document")),
        content=str(request.content.get("body", "")),
        user_name=user_name,
    )

    sent = await send_document_email(
        to_email=request.email,
        subject=f"CaseMate Legal Document - {request.type}",
        body=(
            "Please find your legal document attached.\n\nGenerated by CaseMate AI Legal Assistant."
        ),
        attachment_bytes=doc_bytes,
        attachment_filename="casemate_document.pdf",
    )

    if not sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check email configuration.",
        )
    return {"status": "sent", "email": request.email}


# ---------- Attorney Referral Endpoints ----------


@app.get("/api/attorneys/search", tags=["Attorneys"])
async def search_attorneys(
    state: str,
    legal_area: str | None = None,
    zip_code: str | None = None,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Search for attorneys by state, legal area, and zip code.

    Args:
        state: Two-letter state code.
        legal_area: Optional legal domain filter.
        zip_code: Optional 5-digit zip code for proximity matching.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with attorney referral suggestions.
    """
    if legal_area:
        suggestions = await get_referral_suggestions(state, legal_area, zip_code=zip_code)
        return {"suggestions": [s.model_dump() for s in suggestions]}

    attorneys = await find_attorneys(state, zip_code=zip_code)
    return {
        "suggestions": [
            {
                "attorney": a.model_dump(),
                "match_reason": f"Licensed in {a.state}",
                "relevance_score": 50,
            }
            for a in attorneys
        ]
    }


# ---------- Payment Endpoints ----------


@app.post(
    "/api/payments/create-checkout-session",
    tags=["Payments"],
    responses={500: {"model": InternalErrorResponse}},
)
async def create_checkout(
    request: CreateCheckoutRequest,
    user_id: str = Depends(verify_supabase_jwt),
) -> CheckoutSessionResponse:
    """Create a Stripe checkout session for subscription signup.

    Args:
        request: The checkout request with price ID and redirect URLs.
        user_id: Authenticated user ID from JWT.

    Returns:
        CheckoutSessionResponse with the session ID and hosted checkout URL.

    Raises:
        HTTPException: 500 if Stripe API call fails.
    """
    return await create_checkout_session(
        user_id=user_id,
        price_id=request.price_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url,
    )


@app.post(
    "/api/payments/webhook",
    tags=["Payments"],
    responses={400: {"model": BadRequestResponse}},
)
async def stripe_webhook(request: Request) -> dict[str, str]:
    """Handle incoming Stripe webhook events.

    Reads the raw request body and Stripe-Signature header, then delegates
    to the webhook handler for signature verification and event processing.

    Args:
        request: The raw FastAPI request object.

    Returns:
        Dict with status 'ok' on successful processing.

    Raises:
        HTTPException: 400 if webhook signature verification fails.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    return await handle_webhook(payload, sig_header)


@app.get("/api/payments/subscription", tags=["Payments"])
async def get_user_subscription(
    user_id: str = Depends(verify_supabase_jwt),
) -> SubscriptionStatus:
    """Get the authenticated user's subscription status.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        SubscriptionStatus with the current subscription state.
    """
    return await get_subscription_status(user_id)


@app.post(
    "/api/payments/cancel",
    tags=["Payments"],
    responses={400: {"model": BadRequestResponse}},
)
async def cancel_user_subscription(
    user_id: str = Depends(verify_supabase_jwt),
) -> SubscriptionStatus:
    """Cancel the authenticated user's subscription.

    Cancels at period end so the user retains access until the current
    billing period expires.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        SubscriptionStatus reflecting the canceled state.

    Raises:
        HTTPException: 400 if the user has no active subscription.
    """
    return await cancel_subscription(user_id)
