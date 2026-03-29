"""FastAPI application for the CaseMate AI Legal Assistant backend.

Provides REST API endpoints for chat, profile management, document analysis,
and action generation (demand letters, rights summaries, checklists).
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import TypedDict, cast

import anthropic
from anthropic.types import TextBlock
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from backend.actions.checklist_generator import generate_checklist
from backend.actions.letter_generator import generate_demand_letter
from backend.actions.rights_generator import generate_rights_summary
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
from backend.legal.classifier import classify_with_confidence
from backend.memory.conversation_store import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    save_conversation,
)
from backend.memory.injector import build_system_prompt
from backend.memory.profile import get_profile, update_profile
from backend.memory.updater import update_profile_from_conversation
from backend.models.legal_profile import LegalProfile
from backend.models.responses import HealthResponse
from backend.payments.stripe_webhooks import handle_webhook
from backend.payments.subscription import (
    CheckoutSessionResponse,
    SubscriptionStatus,
    cancel_subscription,
    create_checkout_session,
    get_subscription_status,
)
from backend.referrals.matcher import find_attorneys, get_referral_suggestions
from backend.utils.auth import verify_supabase_jwt
from backend.utils.circuit_breaker import CircuitBreakerOpenError, anthropic_breaker
from backend.utils.client import get_anthropic_client
from backend.utils.logger import configure_logging, get_logger
from backend.utils.rate_limiter import rate_limit
from backend.utils.retry import retry_anthropic
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

app = FastAPI(
    title="CaseMate — AI Legal Assistant",
    description="Personalized AI legal assistant that remembers your legal situation.",
    version="0.3.0",
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
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------- Telemetry middleware — traces every request ----------

app.middleware("http")(telemetry_middleware)

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

# ---------- Max upload size ----------

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


# ---------- Endpoints ----------


@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint for uptime monitoring.

    Returns:
        HealthResponse with status 'ok' and the current service version.
    """
    return HealthResponse(status="ok", version="0.3.0")


@app.get("/metrics")
async def metrics_endpoint() -> Response:
    """Expose in-process metrics for Prometheus scraping or monitoring.

    Returns counters (total requests, errors), histograms (latency p50/p95/p99),
    and labeled counters (status code distribution, legal area classification).
    """
    return get_metrics_response()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_supabase_jwt),
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
    classification = classify_with_confidence(request.message)
    legal_area = classification.domain
    metrics.increment_label("legal_area_classified", legal_area)
    metrics.increment_label("classifier_confidence_bucket", f"{classification.confidence:.1f}")

    system_prompt = build_system_prompt(profile, request.message)

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
        client = get_anthropic_client()

        @anthropic_breaker
        @retry_anthropic
        async def _call_claude() -> str:
            """Call the Claude API with circuit breaker + retry protection."""
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=api_messages,  # type: ignore[arg-type]
            )
            first_block = response.content[0] if response.content else None
            return first_block.text if isinstance(first_block, TextBlock) else ""

        assistant_response = await _call_claude()

    except CircuitBreakerOpenError as exc:
        _logger.warning(
            "circuit_breaker_open",
            user_id=user_id,
            service=exc.service_name,
            retry_after=exc.retry_after,
        )
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again shortly.",
            headers={"Retry-After": str(int(exc.retry_after))},
        ) from exc
    except anthropic.APIError as exc:
        _logger.error(
            "claude_api_error",
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

    _logger.info(
        "chat_response",
        user_id=user_id,
        legal_area=legal_area,
        conversation_id=conversation.id,
        response_length=len(assistant_response),
        classifier_confidence=classification.confidence,
        token_budget_truncated=budget_result.was_truncated,
        chat_latency_ms=round(chat_latency * 1000, 2),
    )

    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        legal_area=legal_area,
    )


@app.get("/api/chat/{conversation_id}/stream")
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

    classification = classify_with_confidence(message)
    legal_area = classification.domain
    system_prompt = build_system_prompt(profile, message)

    conversation.add_message("user", message, legal_area=legal_area)

    all_messages = conversation.to_anthropic_messages()
    system_tokens = estimate_tokens(system_prompt)
    budget_result = _token_budget.apply(all_messages, system_prompt_tokens=system_tokens)
    api_messages = budget_result.messages

    async def _generate_sse() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events from the Claude streaming API.

        Yields SSE-formatted strings with token chunks and metadata.
        """
        metrics = MetricsCollector.get_instance()
        stream_start = time.monotonic()
        full_response_parts: list[str] = []

        try:
            client = get_anthropic_client()
            async with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=api_messages,  # type: ignore[arg-type]
            ) as stream:
                async for text in stream.text_stream:
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

            done_data = json.dumps({
                "type": "done",
                "conversation_id": conversation_id,
                "legal_area": legal_area,
                "response_length": len(assistant_response),
                "latency_ms": round(stream_latency * 1000, 2),
            })
            yield f"data: {done_data}\n\n"

        except CircuitBreakerOpenError as exc:
            error_data = json.dumps({
                "type": "error",
                "message": "AI service temporarily unavailable.",
                "retry_after": int(exc.retry_after),
            })
            yield f"data: {error_data}\n\n"

        except anthropic.APIError as exc:
            _logger.error("stream_api_error", user_id=user_id, error=str(exc))
            error_data = json.dumps({
                "type": "error",
                "message": "AI service error. Please try again.",
            })
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


@app.post("/api/profile")
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
    )

    try:
        updated = await update_profile(profile)
        return {"profile": updated.model_dump(mode="json")}
    except (ValueError, RuntimeError) as exc:
        _logger.error(
            "profile_upsert_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/profile/{user_id}")
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


@app.get("/api/conversations")
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


@app.get("/api/conversations/{conversation_id}")
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


@app.delete("/api/conversations/{conversation_id}")
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


@app.post("/api/actions/letter")
async def create_demand_letter(
    request: ActionRequest,
    user_id: str = Depends(verify_supabase_jwt),
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


@app.post("/api/actions/rights")
async def create_rights_summary(
    request: ActionRequest,
    user_id: str = Depends(verify_supabase_jwt),
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


@app.post("/api/actions/checklist")
async def create_checklist(
    request: ActionRequest,
    user_id: str = Depends(verify_supabase_jwt),
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


@app.post("/api/documents")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_supabase_jwt),
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
        return analysis
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "document_analysis_error",
            user_id=user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to analyze document.") from exc


# ---------- Deadline Endpoints ----------


@app.post("/api/deadlines")
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


@app.get("/api/deadlines")
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


@app.patch("/api/deadlines/{deadline_id}")
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


@app.delete("/api/deadlines/{deadline_id}")
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


@app.get("/api/rights/domains")
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


@app.get("/api/rights/guides")
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


@app.get("/api/rights/guides/{guide_id}")
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


@app.get("/api/workflows/templates")
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


@app.post("/api/workflows")
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


@app.get("/api/workflows")
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


@app.get("/api/workflows/{workflow_id}")
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


@app.patch("/api/workflows/{workflow_id}/steps")
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


@app.post("/api/export/document")
async def export_document(
    request: ExportDocumentRequest,
    user_id: str = Depends(verify_supabase_jwt),
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


@app.post("/api/export/email")
async def export_email(
    request: ExportEmailRequest,
    user_id: str = Depends(verify_supabase_jwt),
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


@app.get("/api/attorneys/search")
async def search_attorneys(
    state: str,
    legal_area: str | None = None,
    user_id: str = Depends(verify_supabase_jwt),
) -> dict[str, object]:
    """Search for attorneys by state and legal area.

    Args:
        state: Two-letter state code.
        legal_area: Optional legal domain filter.
        user_id: Authenticated user ID from JWT.

    Returns:
        Dict with attorney referral suggestions.
    """
    if legal_area:
        suggestions = await get_referral_suggestions(state, legal_area)
        return {"suggestions": [s.model_dump() for s in suggestions]}

    attorneys = await find_attorneys(state)
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


@app.post("/api/payments/create-checkout-session")
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


@app.post("/api/payments/webhook")
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


@app.get("/api/payments/subscription")
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


@app.post("/api/payments/cancel")
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
