"""FastAPI application for the Lex AI Legal Assistant backend.

Provides REST API endpoints for chat, profile management, document analysis,
and action generation (demand letters, rights summaries, checklists).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

import anthropic
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

from backend.actions.checklist_generator import generate_checklist
from backend.actions.letter_generator import generate_demand_letter
from backend.actions.rights_generator import generate_rights_summary
from backend.documents.analyzer import analyze_document
from backend.documents.extractor import extract_text
from backend.legal.classifier import classify_legal_area
from backend.memory.injector import build_system_prompt
from backend.memory.profile import get_profile, update_profile
from backend.memory.updater import update_profile_from_conversation
from backend.models.action_output import Checklist, DemandLetter, RightsSummary
from backend.models.conversation import Conversation, Message
from backend.models.legal_profile import LegalProfile
from backend.utils.logger import configure_logging, get_logger
from backend.utils.retry import retry_anthropic

configure_logging()
_logger = get_logger(__name__)

app = FastAPI(
    title="Lex — AI Legal Assistant",
    description="Personalized AI legal assistant that remembers your legal situation.",
    version="0.1.0",
)


# ---------- Request / Response schemas ----------


class ChatRequest(BaseModel):
    """Request body for the chat endpoint.

    Attributes:
        user_id: Supabase auth user ID.
        message: The user's message text.
        conversation_id: Optional existing conversation ID to continue.
    """

    user_id: str
    message: str
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
        user_id: Supabase auth user ID.
        display_name: User's first name.
        state: Two-letter state code.
        housing_situation: Description of housing situation.
        employment_type: Employment classification.
        family_status: Family and dependent information.
    """

    user_id: str
    display_name: str
    state: str
    housing_situation: str
    employment_type: str
    family_status: str


class ActionRequest(BaseModel):
    """Request body for action generation endpoints.

    Attributes:
        user_id: Supabase auth user ID.
        context: Description of the situation for the action.
    """

    user_id: str
    context: str


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
) -> ChatResponse:
    """Process a user message and return Lex's response.

    Fetches the user's profile, builds a personalized system prompt,
    calls Claude, and schedules a background task to extract new
    legal facts from the conversation.

    Args:
        request: The chat request containing user_id and message.
        background_tasks: FastAPI background task manager.

    Returns:
        ChatResponse with the conversation ID, Lex's response, and
        the classified legal area.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if the Claude API call fails.
    """
    _logger.info("chat_request", user_id=request.user_id)

    profile = await get_profile(request.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding first.")

    legal_area = classify_legal_area(request.message)
    system_prompt = build_system_prompt(profile, request.message)

    conversation_id = request.conversation_id or str(uuid.uuid4())

    try:
        client = anthropic.AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        )

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
            return response.content[0].text if response.content else ""

        assistant_response = await _call_claude()

    except anthropic.APIError as exc:
        _logger.error(
            "claude_api_error",
            user_id=request.user_id,
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
        request.user_id,
        conversation_messages,
    )

    _logger.info(
        "chat_response",
        user_id=request.user_id,
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
async def upsert_profile(request: ProfileRequest) -> dict[str, object]:
    """Create or update a user's legal profile.

    Args:
        request: The profile data to upsert.

    Returns:
        Dict with the profile data as confirmed by Supabase.

    Raises:
        HTTPException: 500 if the upsert operation fails.
    """
    _logger.info("profile_upsert_request", user_id=request.user_id)

    profile = LegalProfile(
        user_id=request.user_id,
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
            user_id=request.user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/profile/{user_id}")
async def get_user_profile(user_id: str) -> dict[str, object]:
    """Fetch a user's legal profile.

    Args:
        user_id: The Supabase auth user ID.

    Returns:
        Dict with the profile data.

    Raises:
        HTTPException: 404 if the profile is not found.
    """
    profile = await get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"profile": profile.model_dump(mode="json")}


@app.post("/api/actions/letter")
async def create_demand_letter(request: ActionRequest) -> dict[str, object]:
    """Generate a demand letter for the user.

    Args:
        request: The action request with user_id and context.

    Returns:
        Dict with the generated DemandLetter data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(request.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        letter = await generate_demand_letter(profile, request.context)
        return {"letter": letter.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "demand_letter_error",
            user_id=request.user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate demand letter.") from exc


@app.post("/api/actions/rights")
async def create_rights_summary(request: ActionRequest) -> dict[str, object]:
    """Generate a rights summary for the user.

    Args:
        request: The action request with user_id and context.

    Returns:
        Dict with the generated RightsSummary data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(request.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        summary = await generate_rights_summary(profile, request.context)
        return {"rights": summary.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "rights_summary_error",
            user_id=request.user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate rights summary.") from exc


@app.post("/api/actions/checklist")
async def create_checklist(request: ActionRequest) -> dict[str, object]:
    """Generate a next-steps checklist for the user.

    Args:
        request: The action request with user_id and context.

    Returns:
        Dict with the generated Checklist data.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 500 if generation fails.
    """
    profile = await get_profile(request.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        checklist = await generate_checklist(profile, request.context)
        return {"checklist": checklist.model_dump()}
    except (anthropic.APIError, RuntimeError) as exc:
        _logger.error(
            "checklist_error",
            user_id=request.user_id,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to generate checklist.") from exc


@app.post("/api/documents")
async def upload_document(
    user_id: str,
    file: UploadFile,
    background_tasks: BackgroundTasks,
) -> dict[str, object]:
    """Upload and analyze a legal document.

    Extracts text from the uploaded file, fetches the user's profile,
    and sends both to Claude for structured legal analysis.

    Args:
        user_id: The Supabase auth user ID.
        file: The uploaded file (PDF, text, or image).
        background_tasks: FastAPI background task manager.

    Returns:
        Dict with the document analysis results including document_type,
        key_facts, red_flags, and summary.

    Raises:
        HTTPException: 404 if the user profile is not found.
        HTTPException: 400 if the file type is not supported.
        HTTPException: 500 if analysis fails.
    """
    _logger.info(
        "document_upload",
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
    )

    contents = await file.read()

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
