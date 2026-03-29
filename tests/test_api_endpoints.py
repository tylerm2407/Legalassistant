"""Tests for all FastAPI API endpoints.

Covers health, chat, profile CRUD, actions, documents, conversations,
deadlines, rights library, workflows, exports, and attorney referral endpoints.
"""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.legal_profile import LegalProfile
from backend.utils.auth import verify_supabase_jwt

# ---------- Helpers ----------

TEST_USER_ID = "user_test_001"


@pytest.fixture
def sample_profile() -> LegalProfile:
    """Return a minimal test profile."""
    return LegalProfile(
        user_id=TEST_USER_ID,
        display_name="Test User",
        state="MA",
        housing_situation="renter",
        employment_type="W-2",
        family_status="single",
    )


async def _mock_auth():
    """Override JWT auth to return test user_id."""
    return TEST_USER_ID


async def _mock_rate_limit():
    """Override rate limiting to always pass."""
    return None


@pytest.fixture
def client():
    """Create a TestClient with auth and rate limits overridden."""
    app.dependency_overrides[verify_supabase_jwt] = _mock_auth
    # Override rate limit dependencies
    from backend.main import _actions_rate_limit, _chat_rate_limit, _documents_rate_limit

    app.dependency_overrides[_chat_rate_limit] = _mock_rate_limit
    app.dependency_overrides[_actions_rate_limit] = _mock_rate_limit
    app.dependency_overrides[_documents_rate_limit] = _mock_rate_limit

    yield TestClient(app)

    app.dependency_overrides.clear()


# ---------- Health ----------


def test_health_check(client):
    """GET /health returns 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


# ---------- Profile ----------


def test_create_profile(client):
    """POST /api/profile creates or updates a profile."""
    with patch("backend.main.update_profile", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = LegalProfile(
            user_id=TEST_USER_ID,
            display_name="Test",
            state="MA",
            housing_situation="renter",
            employment_type="W-2",
            family_status="single",
        )
        response = client.post(
            "/api/profile",
            json={
                "display_name": "Test",
                "state": "MA",
                "housing_situation": "renter",
                "employment_type": "W-2",
                "family_status": "single",
            },
        )
        assert response.status_code == 200
        assert "profile" in response.json()


def test_get_profile_own(client, sample_profile):
    """GET /api/profile/{user_id} returns own profile."""
    with patch("backend.main.get_profile", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = sample_profile
        response = client.get(f"/api/profile/{TEST_USER_ID}")
        assert response.status_code == 200
        assert response.json()["profile"]["display_name"] == "Test User"


def test_get_profile_access_denied(client):
    """GET /api/profile/{other_id} returns 403."""
    response = client.get("/api/profile/other_user_999")
    assert response.status_code == 403


def test_get_profile_not_found(client):
    """GET /api/profile/{user_id} returns 404 when profile missing."""
    with patch("backend.main.get_profile", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/api/profile/{TEST_USER_ID}")
        assert response.status_code == 404


def test_profile_state_max_length(client):
    """POST /api/profile with state > 2 chars returns 422."""
    response = client.post(
        "/api/profile",
        json={
            "display_name": "Test",
            "state": "MASS",
            "housing_situation": "renter",
            "employment_type": "W-2",
            "family_status": "single",
        },
    )
    assert response.status_code == 422


# ---------- Chat ----------


def test_chat_no_profile_returns_404(client):
    """POST /api/chat returns 404 when profile doesn't exist."""
    with patch("backend.main.get_profile", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.post(
            "/api/chat",
            json={"message": "What are my tenant rights?"},
        )
        assert response.status_code == 404


def test_chat_success(client, sample_profile):
    """POST /api/chat returns valid ChatResponse shape."""
    mock_conversation = MagicMock()
    mock_conversation.id = "conv_001"
    mock_conversation.legal_area = "landlord_tenant"
    mock_conversation.to_anthropic_messages.return_value = [{"role": "user", "content": "test"}]

    mock_client = MagicMock()
    mock_content_block = MagicMock()
    mock_content_block.text = "Here is your legal advice."
    mock_response = MagicMock()
    mock_response.content = [mock_content_block]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.create_conversation",
            new_callable=AsyncMock,
            return_value=mock_conversation,
        ),
        patch("backend.main.get_anthropic_client", return_value=mock_client),
        patch("backend.main.save_conversation", new_callable=AsyncMock),
        patch("backend.main.update_profile_from_conversation", new_callable=AsyncMock),
        patch("backend.main.detect_and_save_deadlines", new_callable=AsyncMock),
    ):
        response = client.post(
            "/api/chat",
            json={"message": "What are my tenant rights?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "legal_area" in data


def test_chat_oversized_message(client):
    """POST /api/chat with message > 10000 chars returns 422."""
    response = client.post(
        "/api/chat",
        json={"message": "x" * 10_001},
    )
    assert response.status_code == 422


# ---------- Conversations ----------


def test_list_conversations(client):
    """GET /api/conversations returns list."""
    with patch("backend.main.list_conversations", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        response = client.get("/api/conversations")
        assert response.status_code == 200
        assert "conversations" in response.json()


def test_get_conversation_not_found(client):
    """GET /api/conversations/{id} returns 404 when not found."""
    with patch("backend.main.get_conversation", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get("/api/conversations/fake_id")
        assert response.status_code == 404


def test_delete_conversation(client):
    """DELETE /api/conversations/{id} returns deleted status."""
    with patch("backend.main.delete_conversation", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = True
        response = client.delete("/api/conversations/conv_001")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


def test_delete_conversation_not_found(client):
    """DELETE /api/conversations/{id} returns 404 when not found."""
    with patch("backend.main.delete_conversation", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = False
        response = client.delete("/api/conversations/fake_id")
        assert response.status_code == 404


# ---------- Actions ----------


def test_action_letter_no_profile(client):
    """POST /api/actions/letter returns 404 without profile."""
    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None):
        response = client.post(
            "/api/actions/letter",
            json={"context": "My landlord won't return my deposit."},
        )
        assert response.status_code == 404


def test_action_rights_no_profile(client):
    """POST /api/actions/rights returns 404 without profile."""
    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None):
        response = client.post(
            "/api/actions/rights",
            json={"context": "Employment discrimination situation."},
        )
        assert response.status_code == 404


def test_action_checklist_no_profile(client):
    """POST /api/actions/checklist returns 404 without profile."""
    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None):
        response = client.post(
            "/api/actions/checklist",
            json={"context": "Small claims court filing."},
        )
        assert response.status_code == 404


def test_action_letter_success(client, sample_profile):
    """POST /api/actions/letter returns generated letter."""
    mock_letter = MagicMock()
    mock_letter.model_dump.return_value = {"letter_text": "Dear Sir..."}

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_demand_letter", new_callable=AsyncMock, return_value=mock_letter
        ),
    ):
        response = client.post(
            "/api/actions/letter",
            json={"context": "My landlord won't return my deposit."},
        )
        assert response.status_code == 200
        assert "letter" in response.json()


# ---------- Documents ----------


def test_document_upload_no_profile(client):
    """POST /api/documents returns 404 without profile."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None),
        patch("backend.main.extract_text", return_value="Some text"),
    ):
        file_content = b"fake pdf content"
        response = client.post(
            "/api/documents",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 404


def test_document_upload_too_large(client):
    """POST /api/documents with file > 25MB returns 413."""
    big_content = b"x" * (26 * 1024 * 1024)
    response = client.post(
        "/api/documents",
        files={"file": ("big.pdf", io.BytesIO(big_content), "application/pdf")},
    )
    assert response.status_code == 413


# ---------- Deadlines ----------


def test_list_deadlines(client):
    """GET /api/deadlines returns list."""
    with patch("backend.main.list_deadlines", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        response = client.get("/api/deadlines")
        assert response.status_code == 200
        assert "deadlines" in response.json()


def test_delete_deadline_not_found(client):
    """DELETE /api/deadlines/{id} returns 404 when not found."""
    with patch("backend.main.delete_deadline", new_callable=AsyncMock) as mock_del:
        mock_del.return_value = False
        response = client.delete("/api/deadlines/fake_id")
        assert response.status_code == 404


# ---------- Rights Library ----------


def test_get_rights_domains(client):
    """GET /api/rights/domains returns domain list."""
    response = client.get("/api/rights/domains")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert len(data["domains"]) > 0


def test_get_rights_guides_list(client):
    """GET /api/rights/guides returns guides list."""
    response = client.get("/api/rights/guides")
    assert response.status_code == 200
    data = response.json()
    assert "guides" in data
    assert len(data["guides"]) > 0


def test_get_rights_guide_not_found(client):
    """GET /api/rights/guides/{id} returns 404 for unknown guide."""
    response = client.get("/api/rights/guides/nonexistent_guide")
    assert response.status_code == 404


def test_get_rights_guide_by_id(client):
    """GET /api/rights/guides/{id} returns a specific guide."""
    response = client.get("/api/rights/guides/tenant_eviction_defense")
    assert response.status_code == 200
    data = response.json()
    assert data["guide"]["id"] == "tenant_eviction_defense"


# ---------- Workflows ----------


def test_list_workflow_templates(client):
    """GET /api/workflows/templates returns template list."""
    response = client.get("/api/workflows/templates")
    assert response.status_code == 200
    assert "templates" in response.json()


def test_start_workflow_bad_template(client):
    """POST /api/workflows with bad template_id returns 404."""
    response = client.post(
        "/api/workflows",
        json={"template_id": "nonexistent_template"},
    )
    assert response.status_code == 404


# ---------- Export ----------


def test_export_document_unknown_type(client):
    """POST /api/export/document with unknown type returns 400."""
    with patch("backend.main.get_profile", new_callable=AsyncMock, return_value=None):
        response = client.post(
            "/api/export/document",
            json={"type": "unknown_type", "content": {}},
        )
        assert response.status_code == 400


# ---------- Attorney Referral ----------


def test_search_attorneys(client):
    """GET /api/attorneys/search returns results."""
    with patch("backend.main.find_attorneys", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = []
        response = client.get("/api/attorneys/search?state=MA")
        assert response.status_code == 200
        assert "suggestions" in response.json()
