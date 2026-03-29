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


# ---------- Deadline create / update ----------


def test_create_deadline_success(client):
    """POST /api/deadlines creates a deadline and returns it."""
    mock_deadline = MagicMock()
    mock_deadline.model_dump.return_value = {
        "id": "dl_001",
        "title": "File answer",
        "date": "2026-04-15",
        "legal_area": "landlord_tenant",
        "notes": "Must file by this date",
    }

    with patch("backend.main.create_deadline", new_callable=AsyncMock, return_value=mock_deadline):
        response = client.post(
            "/api/deadlines",
            json={
                "title": "File answer",
                "date": "2026-04-15",
                "legal_area": "landlord_tenant",
                "notes": "Must file by this date",
            },
        )
        assert response.status_code == 200
        assert "deadline" in response.json()


def test_update_deadline_success(client):
    """PATCH /api/deadlines/{id} updates and returns the deadline."""
    mock_deadline = MagicMock()
    mock_deadline.model_dump.return_value = {
        "id": "dl_001",
        "title": "File answer (updated)",
    }

    with patch("backend.main.update_deadline", new_callable=AsyncMock, return_value=mock_deadline):
        response = client.patch(
            "/api/deadlines/dl_001",
            json={"title": "File answer (updated)"},
        )
        assert response.status_code == 200
        assert "deadline" in response.json()


def test_update_deadline_not_found(client):
    """PATCH /api/deadlines/{id} returns 404 when deadline missing."""
    with patch("backend.main.update_deadline", new_callable=AsyncMock, return_value=None):
        response = client.patch(
            "/api/deadlines/fake_id",
            json={"title": "nope"},
        )
        assert response.status_code == 404


# ---------- Actions success (rights + checklist) ----------


def test_action_rights_success(client, sample_profile):
    """POST /api/actions/rights returns generated rights summary."""
    mock_summary = MagicMock()
    mock_summary.model_dump.return_value = {"summary_text": "You have the right to..."}

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_rights_summary",
            new_callable=AsyncMock,
            return_value=mock_summary,
        ),
    ):
        response = client.post(
            "/api/actions/rights",
            json={"context": "Employment discrimination situation."},
        )
        assert response.status_code == 200
        assert "rights" in response.json()


def test_action_checklist_success(client, sample_profile):
    """POST /api/actions/checklist returns generated checklist."""
    mock_checklist = MagicMock()
    mock_checklist.model_dump.return_value = {"items": ["Step 1", "Step 2"]}

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_checklist",
            new_callable=AsyncMock,
            return_value=mock_checklist,
        ),
    ):
        response = client.post(
            "/api/actions/checklist",
            json={"context": "Small claims court filing."},
        )
        assert response.status_code == 200
        assert "checklist" in response.json()


# ---------- Documents success ----------


def test_document_upload_success(client, sample_profile):
    """POST /api/documents with valid file returns analysis."""
    analysis_result = {
        "document_type": "lease",
        "key_facts": ["Lease term is 12 months"],
        "red_flags": [],
        "summary": "Standard residential lease.",
    }

    with (
        patch("backend.main.extract_text", return_value="Lease agreement text here"),
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.analyze_document", new_callable=AsyncMock, return_value=analysis_result
        ),
    ):
        file_content = b"fake pdf content"
        response = client.post(
            "/api/documents",
            files={"file": ("lease.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "lease"
        assert "key_facts" in data


# ---------- Workflows success ----------


def test_start_workflow_success(client):
    """POST /api/workflows with valid template returns workflow instance."""
    mock_instance = MagicMock()
    mock_instance.model_dump.return_value = {
        "id": "wf_001",
        "template_id": "fight_eviction",
        "title": "Fight Eviction",
        "current_step": 0,
    }

    with patch("backend.main.start_workflow", new_callable=AsyncMock, return_value=mock_instance):
        response = client.post(
            "/api/workflows",
            json={"template_id": "fight_eviction"},
        )
        assert response.status_code == 200
        assert "workflow" in response.json()


def test_get_workflow_success(client):
    """GET /api/workflows/{id} returns workflow data."""
    mock_workflow = MagicMock()
    mock_workflow.model_dump.return_value = {
        "id": "wf_001",
        "template_id": "fight_eviction",
        "current_step": 0,
    }

    with patch("backend.main.get_workflow", new_callable=AsyncMock, return_value=mock_workflow):
        response = client.get("/api/workflows/wf_001")
        assert response.status_code == 200
        assert "workflow" in response.json()


def test_get_workflow_not_found(client):
    """GET /api/workflows/{id} returns 404 when not found."""
    with patch("backend.main.get_workflow", new_callable=AsyncMock, return_value=None):
        response = client.get("/api/workflows/fake_id")
        assert response.status_code == 404


def test_update_workflow_step_success(client):
    """PATCH /api/workflows/{id}/steps updates a step status."""
    mock_workflow = MagicMock()
    mock_workflow.model_dump.return_value = {
        "id": "wf_001",
        "current_step": 1,
    }

    with patch(
        "backend.main.update_workflow_step", new_callable=AsyncMock, return_value=mock_workflow
    ):
        response = client.patch(
            "/api/workflows/wf_001/steps",
            json={"step_index": 0, "status": "completed"},
        )
        assert response.status_code == 200
        assert "workflow" in response.json()


def test_update_workflow_step_not_found(client):
    """PATCH /api/workflows/{id}/steps returns 404 when workflow missing."""
    with patch("backend.main.update_workflow_step", new_callable=AsyncMock, return_value=None):
        response = client.patch(
            "/api/workflows/fake_id/steps",
            json={"step_index": 0, "status": "completed"},
        )
        assert response.status_code == 404


# ---------- Export success ----------


def test_export_document_letter(client, sample_profile):
    """POST /api/export/document with type=letter returns PDF bytes."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_demand_letter_document",
            return_value=b"%PDF-1.4 fake pdf bytes",
        ),
    ):
        response = client.post(
            "/api/export/document",
            json={
                "type": "letter",
                "content": {"letter_text": "Dear Sir...", "legal_citations": ["M.G.L. c.186"]},
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


def test_export_document_rights(client, sample_profile):
    """POST /api/export/document with type=rights returns PDF."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_rights_document",
            return_value=b"%PDF-1.4 fake pdf bytes",
        ),
    ):
        response = client.post(
            "/api/export/document",
            json={
                "type": "rights",
                "content": {"summary_text": "Your rights...", "key_rights": ["Right 1"]},
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


def test_export_document_checklist(client, sample_profile):
    """POST /api/export/document with type=checklist returns PDF."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_checklist_document",
            return_value=b"%PDF-1.4 fake pdf bytes",
        ),
    ):
        response = client.post(
            "/api/export/document",
            json={
                "type": "checklist",
                "content": {"items": ["Do this", "Do that"], "deadlines": ["2026-04-01"]},
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


def test_export_document_custom(client, sample_profile):
    """POST /api/export/document with type=custom returns PDF."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_text_document",
            return_value=b"%PDF-1.4 fake pdf bytes",
        ),
    ):
        response = client.post(
            "/api/export/document",
            json={
                "type": "custom",
                "content": {"title": "My Doc", "body": "Body text"},
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


# ---------- Payments ----------


def test_get_subscription_status(client):
    """GET /api/payments/subscription returns subscription status."""
    from backend.payments.subscription import SubscriptionStatus

    status = SubscriptionStatus(
        user_id=TEST_USER_ID,
        is_active=False,
        status="none",
    )

    with patch("backend.main.get_subscription_status", new_callable=AsyncMock, return_value=status):
        response = client.get("/api/payments/subscription")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert data["is_active"] is False


def test_cancel_subscription_success(client):
    """POST /api/payments/cancel returns updated subscription status."""
    from backend.payments.subscription import SubscriptionStatus

    status = SubscriptionStatus(
        user_id=TEST_USER_ID,
        is_active=False,
        status="canceled",
    )

    with patch("backend.main.cancel_subscription", new_callable=AsyncMock, return_value=status):
        response = client.post("/api/payments/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "canceled"


# ---------- Rights guides filtered by domain ----------


def test_get_rights_guides_filtered_by_domain(client):
    """GET /api/rights/guides?domain=landlord_tenant returns filtered guides."""
    response = client.get("/api/rights/guides?domain=landlord_tenant")
    assert response.status_code == 200
    data = response.json()
    assert "guides" in data


# ---------- List workflows ----------


def test_list_user_workflows(client):
    """GET /api/workflows returns the user's workflows."""
    with patch("backend.main.list_workflows", new_callable=AsyncMock, return_value=[]):
        response = client.get("/api/workflows")
        assert response.status_code == 200
        assert "workflows" in response.json()


# ---------- Delete deadline success ----------


def test_delete_deadline_success(client):
    """DELETE /api/deadlines/{id} returns deleted status."""
    with patch("backend.main.delete_deadline", new_callable=AsyncMock, return_value=True):
        response = client.delete("/api/deadlines/dl_001")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


# ---------- Get conversation success ----------


def test_get_conversation_success(client):
    """GET /api/conversations/{id} returns conversation data."""
    mock_conversation = MagicMock()
    mock_conversation.model_dump.return_value = {
        "id": "conv_001",
        "user_id": TEST_USER_ID,
        "messages": [],
    }

    with patch(
        "backend.main.get_conversation", new_callable=AsyncMock, return_value=mock_conversation
    ):
        response = client.get("/api/conversations/conv_001")
        assert response.status_code == 200
        assert "conversation" in response.json()


# ---------- Export email ----------


def test_export_email_success(client, sample_profile):
    """POST /api/export/email sends document via email."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch("backend.main.generate_text_document", return_value=b"%PDF-1.4 bytes"),
        patch("backend.main.send_document_email", new_callable=AsyncMock, return_value=True),
    ):
        response = client.post(
            "/api/export/email",
            json={
                "type": "custom",
                "content": {"title": "Doc", "body": "Body"},
                "email": "user@example.com",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
        assert data["email"] == "user@example.com"


def test_export_email_send_failure(client, sample_profile):
    """POST /api/export/email returns 500 when email sending fails."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch("backend.main.generate_text_document", return_value=b"%PDF-1.4 bytes"),
        patch("backend.main.send_document_email", new_callable=AsyncMock, return_value=False),
    ):
        response = client.post(
            "/api/export/email",
            json={
                "type": "custom",
                "content": {"title": "Doc", "body": "Body"},
                "email": "user@example.com",
            },
        )
        assert response.status_code == 500


# ---------- Action error branches ----------


def test_action_letter_api_error(client, sample_profile):
    """POST /api/actions/letter returns 500 on API error."""

    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_demand_letter",
            new_callable=AsyncMock,
            side_effect=RuntimeError("generation failed"),
        ),
    ):
        response = client.post(
            "/api/actions/letter",
            json={"context": "test context"},
        )
        assert response.status_code == 500


def test_action_rights_api_error(client, sample_profile):
    """POST /api/actions/rights returns 500 on API error."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_rights_summary",
            new_callable=AsyncMock,
            side_effect=RuntimeError("generation failed"),
        ),
    ):
        response = client.post(
            "/api/actions/rights",
            json={"context": "test context"},
        )
        assert response.status_code == 500


def test_action_checklist_api_error(client, sample_profile):
    """POST /api/actions/checklist returns 500 on API error."""
    with (
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.generate_checklist",
            new_callable=AsyncMock,
            side_effect=RuntimeError("generation failed"),
        ),
    ):
        response = client.post(
            "/api/actions/checklist",
            json={"context": "test context"},
        )
        assert response.status_code == 500


# ---------- Document upload error branches ----------


def test_document_upload_unsupported_type(client):
    """POST /api/documents with unsupported file type returns 400."""
    with patch(
        "backend.main.extract_text",
        side_effect=ValueError("Unsupported file type"),
    ):
        file_content = b"not a pdf"
        response = client.post(
            "/api/documents",
            files={"file": ("test.xyz", io.BytesIO(file_content), "application/octet-stream")},
        )
        assert response.status_code == 400


def test_document_analysis_error(client, sample_profile):
    """POST /api/documents returns 500 when analysis fails."""
    with (
        patch("backend.main.extract_text", return_value="Extracted text"),
        patch("backend.main.get_profile", new_callable=AsyncMock, return_value=sample_profile),
        patch(
            "backend.main.analyze_document",
            new_callable=AsyncMock,
            side_effect=RuntimeError("analysis failed"),
        ),
    ):
        file_content = b"fake pdf"
        response = client.post(
            "/api/documents",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 500


# ---------- Deadline create error ----------


def test_create_deadline_error(client):
    """POST /api/deadlines returns 500 when creation fails."""
    with patch(
        "backend.main.create_deadline",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DB error"),
    ):
        response = client.post(
            "/api/deadlines",
            json={
                "title": "File answer",
                "date": "2026-04-15",
                "legal_area": "landlord_tenant",
            },
        )
        assert response.status_code == 500


# ---------- Profile update error ----------


def test_update_profile_error(client):
    """POST /api/profile returns 500 on update failure."""
    with patch(
        "backend.main.update_profile",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DB connection lost"),
    ):
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
        assert response.status_code == 500


# ---------- Workflow start error ----------


def test_start_workflow_runtime_error(client):
    """POST /api/workflows returns 500 on runtime error."""
    with patch(
        "backend.main.start_workflow",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DB error"),
    ):
        response = client.post(
            "/api/workflows",
            json={"template_id": "fight_eviction"},
        )
        assert response.status_code == 500


# ---------- Workflow step update error ----------


def test_update_workflow_step_runtime_error(client):
    """PATCH /api/workflows/{id}/steps returns 500 on runtime error."""
    with patch(
        "backend.main.update_workflow_step",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DB error"),
    ):
        response = client.patch(
            "/api/workflows/wf_001/steps",
            json={"step_index": 0, "status": "completed"},
        )
        assert response.status_code == 500


# ---------- Deadline update error ----------


def test_update_deadline_runtime_error(client):
    """PATCH /api/deadlines/{id} returns 500 on runtime error."""
    with patch(
        "backend.main.update_deadline",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DB error"),
    ):
        response = client.patch(
            "/api/deadlines/dl_001",
            json={"title": "Updated"},
        )
        assert response.status_code == 500


# ---------- Attorney search with legal_area ----------


def test_search_attorneys_with_legal_area(client):
    """GET /api/attorneys/search with legal_area returns referral suggestions."""
    mock_suggestion = MagicMock()
    mock_suggestion.model_dump.return_value = {
        "attorney": {"name": "Jane Doe"},
        "match_reason": "Specializes in landlord_tenant",
        "relevance_score": 85,
    }

    with patch(
        "backend.main.get_referral_suggestions",
        new_callable=AsyncMock,
        return_value=[mock_suggestion],
    ):
        response = client.get("/api/attorneys/search?state=MA&legal_area=landlord_tenant")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) == 1
