"""End-to-end integration tests for CaseMate API pipelines.

Verifies complete request/response cycles through the full stack:
user message -> profile fetch -> classification -> prompt build -> Claude API -> response.

All external services (Anthropic, Supabase) are mocked. These tests prove that
the internal wiring between modules works correctly as a whole.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.legal.classifier import classify_legal_area
from backend.main import app
from backend.models.legal_profile import LegalProfile
from backend.utils.auth import verify_supabase_jwt

TEST_USER_ID = "integration_user_001"


@pytest.fixture()
def _sample_profile() -> LegalProfile:
    """Minimal MA renter profile for integration tests."""
    return LegalProfile(
        user_id=TEST_USER_ID,
        display_name="Integration Test User",
        state="MA",
        housing_situation="renter, apartment in Cambridge",
        employment_type="full-time W-2",
        family_status="single",
        legal_facts=[
            "Landlord did not perform move-in inspection",
            "Security deposit was $1,800",
        ],
    )


async def _mock_auth() -> str:
    return TEST_USER_ID


async def _mock_rate_limit() -> None:
    return None


@pytest.fixture()
def integration_client() -> TestClient:
    """TestClient with auth and rate limits overridden."""
    app.dependency_overrides[verify_supabase_jwt] = _mock_auth
    from backend.main import (
        _actions_rate_limit,
        _chat_rate_limit,
        _documents_rate_limit,
        require_subscription_or_free_tier,
    )

    app.dependency_overrides[_chat_rate_limit] = _mock_rate_limit
    app.dependency_overrides[_actions_rate_limit] = _mock_rate_limit
    app.dependency_overrides[_documents_rate_limit] = _mock_rate_limit
    app.dependency_overrides[require_subscription_or_free_tier] = _mock_auth

    yield TestClient(app)

    app.dependency_overrides.clear()


# ---------- Health + Infrastructure ----------


def test_health_returns_lifecycle_info(integration_client: TestClient) -> None:
    """GET /health returns status, version, and lifecycle metadata."""
    resp = integration_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "lifecycle" in data
    assert "state" in data["lifecycle"]
    assert "active_requests" in data["lifecycle"]
    assert "uptime_seconds" in data["lifecycle"]


def test_metrics_returns_json(integration_client: TestClient) -> None:
    """GET /metrics returns a JSON metrics payload."""
    resp = integration_client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "counters" in data or "histograms" in data or isinstance(data, dict)


def test_openapi_docs_available(integration_client: TestClient) -> None:
    """GET /docs serves the Swagger UI."""
    resp = integration_client.get("/docs")
    assert resp.status_code == 200


# ---------- Full Chat Pipeline ----------


def test_full_chat_pipeline(integration_client: TestClient, _sample_profile: LegalProfile) -> None:
    """Complete chat flow: profile lookup -> classify -> prompt build -> response."""
    mock_oai_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = (
        "Under Massachusetts law, specifically M.G.L. c.186 §15B, "
        "your landlord must return your security deposit within 30 days."
    )
    mock_oai_response.choices = [mock_choice]

    mock_conversation = MagicMock()
    mock_conversation.id = "conv_integration_001"
    mock_conversation.legal_area = None
    mock_conversation.to_anthropic_messages.return_value = []
    mock_conversation.add_message = MagicMock()

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=_sample_profile),
        patch(
            "backend.main.classify_with_llm_fallback",
            new_callable=AsyncMock,
            return_value=MagicMock(domain="landlord_tenant", confidence=0.9, method="keyword"),
        ),
        patch(
            "backend.main.create_conversation",
            new_callable=AsyncMock,
            return_value=mock_conversation,
        ),
        patch("backend.main.save_conversation", new_callable=AsyncMock),
        patch("backend.main.update_profile_from_conversation", new_callable=AsyncMock),
        patch("backend.main.detect_and_save_deadlines", new_callable=AsyncMock),
        patch("backend.main.record_audit_event", new_callable=AsyncMock),
        patch("backend.main.increment_free_message_count", new_callable=AsyncMock),
        patch("backend.main.get_openai_client") as mock_get_client,
    ):
        mock_client = MagicMock()
        mock_client.chat = MagicMock()
        mock_client.chat.completions = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_oai_response)
        mock_get_client.return_value = mock_client

        resp = integration_client.post(
            "/api/chat",
            json={"message": "Can my landlord keep my security deposit?"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["conversation_id"] == "conv_integration_001"
        response_text = data["response"].lower()
        assert "massachusetts" in response_text, "Response should mention the user's state"
        assert any(
            term in response_text for term in ["law", "statute", "deposit", "landlord", "m.g.l."]
        ), "Response should contain legal content"
        assert data["legal_area"] == "landlord_tenant"


# ---------- Profile CRUD Pipeline ----------


def test_profile_create_and_retrieve(integration_client: TestClient) -> None:
    """Create a profile via POST, then retrieve it via GET."""
    created_profile_data = {
        "user_id": TEST_USER_ID,
        "display_name": "New User",
        "state": "CA",
        "housing_situation": "renter",
        "employment_type": "freelance",
        "family_status": "married",
        "active_issues": [],
        "legal_facts": [],
        "documents": [],
        "member_since": "2026-03-01T00:00:00",
        "conversation_count": 0,
    }
    mock_updated = LegalProfile.model_validate(created_profile_data)

    with patch("backend.main.update_profile", new_callable=AsyncMock, return_value=mock_updated):
        resp = integration_client.post(
            "/api/profile",
            json={
                "display_name": "New User",
                "state": "CA",
                "housing_situation": "renter",
                "employment_type": "freelance",
                "family_status": "married",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["profile"]["state"] == "CA"

    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=mock_updated):
        resp = integration_client.get(f"/api/profile/{TEST_USER_ID}")
        assert resp.status_code == 200
        assert resp.json()["profile"]["display_name"] == "New User"


def test_profile_access_denied_for_other_user(integration_client: TestClient) -> None:
    """GET /api/profile/{other_id} returns 403."""
    resp = integration_client.get("/api/profile/different_user_id")
    assert resp.status_code == 403


# ---------- Action Generation Pipeline ----------


def test_demand_letter_pipeline(
    integration_client: TestClient, _sample_profile: LegalProfile
) -> None:
    """Full demand letter: profile lookup -> Claude generation -> structured output."""
    mock_letter = MagicMock()
    mock_letter.model_dump.return_value = {
        "text": "Dear Mr. Peterson, pursuant to M.G.L. c.186 s.15B...",
        "citations": ["M.G.L. c.186 s.15B"],
        "recipient": "James Peterson",
    }

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=_sample_profile),
        patch(
            "backend.main.generate_demand_letter", new_callable=AsyncMock, return_value=mock_letter
        ),
    ):
        resp = integration_client.post(
            "/api/actions/letter",
            json={"context": "Landlord has not returned my $1,800 security deposit after 60 days"},
        )
        assert resp.status_code == 200
        letter = resp.json()["letter"]
        assert "M.G.L." in letter["text"]
        assert len(letter["citations"]) > 0


def test_rights_summary_pipeline(
    integration_client: TestClient, _sample_profile: LegalProfile
) -> None:
    """Full rights summary generation pipeline."""
    mock_rights = MagicMock()
    mock_rights.model_dump.return_value = {
        "text": "Under FLSA, you are entitled to overtime pay...",
        "citations": ["29 USC s.207"],
    }

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=_sample_profile),
        patch(
            "backend.main.generate_rights_summary", new_callable=AsyncMock, return_value=mock_rights
        ),
    ):
        resp = integration_client.post(
            "/api/actions/rights",
            json={"context": "My employer hasn't paid overtime for 3 months"},
        )
        assert resp.status_code == 200
        assert "FLSA" in resp.json()["rights"]["text"]


def test_checklist_pipeline(integration_client: TestClient, _sample_profile: LegalProfile) -> None:
    """Full checklist generation pipeline."""
    mock_checklist = MagicMock()
    mock_checklist.model_dump.return_value = {
        "steps": [
            {"step": 1, "action": "Gather move-out photos"},
            {"step": 2, "action": "Send demand letter via certified mail"},
            {"step": 3, "action": "File in small claims court if no response in 30 days"},
        ],
    }

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=_sample_profile),
        patch(
            "backend.main.generate_checklist", new_callable=AsyncMock, return_value=mock_checklist
        ),
    ):
        resp = integration_client.post(
            "/api/actions/checklist",
            json={"context": "I want to file for my deposit in small claims"},
        )
        assert resp.status_code == 200
        steps = resp.json()["checklist"]["steps"]
        assert len(steps) == 3


# ---------- Chat Without Profile → 404 ----------


def test_chat_without_profile_returns_404(integration_client: TestClient) -> None:
    """POST /api/chat with no profile returns 404 with onboarding hint."""
    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None):
        resp = integration_client.post(
            "/api/chat",
            json={"message": "Hello"},
        )
        assert resp.status_code == 404
        assert "onboarding" in resp.json()["detail"].lower()


# ---------- Legal Classifier Coverage ----------


def test_all_10_legal_domains_classify_correctly() -> None:
    """Verify the keyword classifier handles all 10 domains + general fallback."""
    cases: dict[str, str] = {
        "my landlord won't return my deposit": "landlord_tenant",
        "my boss fired me without notice": "employment_rights",
        "the product I bought is defective": "consumer_protection",
        "a debt collector keeps calling me": "debt_collections",
        "I want to sue for $3000": "small_claims",
        "they breached our contract": "contract_disputes",
        "I got a speeding ticket": "traffic_violations",
        "I'm going through a divorce": "family_law",
        "how do I expunge my record": "criminal_records",
        "my visa is expiring": "immigration",
        "hello how are you": "general",
    }
    for message, expected in cases.items():
        result = classify_legal_area(message)
        assert result == expected, f"'{message}' → {result}, expected {expected}"


# ---------- Conversation Pipeline ----------


def test_conversation_list_and_delete(integration_client: TestClient) -> None:
    """List conversations and delete one."""
    mock_convos = [
        {
            "id": "conv_001",
            "preview": "About my deposit...",
            "message_count": 4,
            "legal_area": "landlord_tenant",
        }
    ]
    with patch("backend.main.list_conversations", new_callable=AsyncMock, return_value=mock_convos):
        resp = integration_client.get("/api/conversations")
        assert resp.status_code == 200
        assert len(resp.json()["conversations"]) == 1

    with patch("backend.main.delete_conversation", new_callable=AsyncMock, return_value=True):
        resp = integration_client.delete("/api/conversations/conv_001")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"


# ---------- Audit Verification ----------


def test_audit_verification_endpoint(integration_client: TestClient) -> None:
    """GET /api/audit/verify returns chain verification result."""
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {
        "valid": True,
        "events_checked": 5,
        "break_at": None,
        "checked_at": "2026-03-29T12:00:00Z",
    }

    with patch("backend.utils.audit_log.AuditLog") as mock_audit_cls:
        mock_instance = MagicMock()
        mock_instance.verify_chain = AsyncMock(return_value=mock_result)
        mock_audit_cls.get_instance.return_value = mock_instance

        resp = integration_client.get("/api/audit/verify")
        assert resp.status_code == 200
        data = resp.json()["verification"]
        assert data["valid"] is True
        assert data["events_checked"] == 5
