"""FastAPI application for the Lex AI Legal Assistant backend.

Provides REST API endpoints for chat, profile management, document analysis,
and action generation (demand letters, rights summaries, checklists).
"""

from __future__ import annotations

import os
import uuid

import anthropic
from anthropic.types import TextBlock
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.actions.checklist_generator import generate_checklist
from backend.actions.letter_generator import generate_demand_letter
from backend.actions.rights_generator import generate_rights_summary
from backend.documents.analyzer import analyze_document
from backend.documents.extractor import extract_text
from backend.legal.classifier import classify_legal_area
from backend.memory.injector import build_system_prompt
from backend.memory.profile import get_profile, update_profile
from backend.memory.updater import update_profile_from_conversation
from backend.models.legal_profile import LegalProfile
from backend.utils.auth import verify_supabase_jwt
from backend.utils.client import get_anthropic_client
from backend.utils.logger import configure_logging, get_logger
from backend.utils.rate_limiter import rate_limit
from backend.utils.retry import retry_anthropic

configure_logging()
_logger = get_logger(__name__)

app = FastAPI(
    title="Lex — AI Legal Assistant",
    description="Personalized AI legal assistant that remembers your legal situation.",
    version="0.1.0",
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
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------- Middleware to stash user_id on request.state ----------


@app.middleware("http")
async def attach_user_id_to_state(request: Request, call_next):
    """Extract user_id from JWT and attach to request.state for rate limiter."""
    response = await call_next(request)
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
        response: Lex's response text.
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


# ---------- Rate limit dependencies ----------

_chat_rate_limit = rate_limit(max_requests=10, window_seconds=60)
_actions_rate_limit = rate_limit(max_requests=5, window_seconds=60)
_documents_rate_limit = rate_limit(max_requests=3, window_seconds=60)

# ---------- Max upload size ----------

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


# ---------- Endpoints ----------


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for uptime monitoring.

    Returns:
        Dict with status 'ok' and the current service version.
    """
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_supabase_jwt),
    _rate: None = Depends(_chat_rate_limit),
) -> ChatResponse:
    """Process a user message and return Lex's response.

    Fetches the user's profile, builds a personalized system prompt,
    calls Claude, and schedules a background task to extract new
    legal facts from the conversation.

    Args:
        request: The chat request containing the message.
        background_tasks: FastAPI background task manager.
        user_id: Authenticated user ID from JWT.
        _rate: Rate limit check (side-effect only).

    Returns:
        ChatResponse with the conversation ID, Lex's response, and
        the classified legal area.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if the Claude API call fails.
    """
    _logger.info("chat_request", user_id=user_id)

    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding first.")

    legal_area = classify_legal_area(request.message)
    system_prompt = build_system_prompt(profile, request.message)

    conversation_id = request.conversation_id or str(uuid.uuid4())

    try:
        client = get_anthropic_client()

        @retry_anthropic
        async def _call_claude() -> str:
            """Call the Claude API with the personalized system prompt.

            Returns:
                The assistant's response text.
            """
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": request.message}],
            )
            first_block = response.content[0] if response.content else None
            return first_block.text if isinstance(first_block, TextBlock) else ""

        assistant_response = await _call_claude()

    except anthropic.APIError as exc:
        _logger.error(
            "claude_api_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable.") from exc

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

    _logger.info(
        "chat_response",
        user_id=user_id,
        legal_area=legal_area,
        conversation_id=conversation_id,
        response_length=len(assistant_response),
    )

    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_response,
        legal_area=legal_area,
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
