"""Tests for CaseMate Pydantic models — LegalProfile, LegalIssue, and response models.

Verifies serialization round-trips, edge cases with empty/maximal data,
and validation behavior for the core data models.
"""

from __future__ import annotations

import json

from backend.models.legal_profile import IssueStatus, LegalIssue, LegalProfile
from backend.models.responses import DeleteResponse, HealthResponse, WaitlistResponse


class TestLegalProfileSerialization:
    """Verify LegalProfile serialization and deserialization."""

    def test_round_trip_serialization(self, mock_profile) -> None:
        """Profile serialized to dict and back should be equal."""
        data = mock_profile.model_dump()
        restored = LegalProfile(**data)

        assert restored.user_id == mock_profile.user_id
        assert restored.state == mock_profile.state
        assert restored.legal_facts == mock_profile.legal_facts
        assert len(restored.active_issues) == len(mock_profile.active_issues)
        assert restored.active_issues[0].summary == mock_profile.active_issues[0].summary

    def test_json_round_trip(self, mock_profile) -> None:
        """Profile serialized to JSON string and back should preserve data."""
        json_str = mock_profile.model_dump_json()
        restored = LegalProfile.model_validate_json(json_str)

        assert restored.user_id == mock_profile.user_id
        assert restored.conversation_count == mock_profile.conversation_count
        assert restored.documents == mock_profile.documents

    def test_empty_fields_profile(self) -> None:
        """Profile with no issues, facts, or documents should serialize cleanly."""
        profile = LegalProfile(
            user_id="user_empty",
            display_name="Empty User",
            state="TX",
            housing_situation="",
            employment_type="",
            family_status="",
            active_issues=[],
            legal_facts=[],
            documents=[],
        )
        data = profile.model_dump()

        assert data["active_issues"] == []
        assert data["legal_facts"] == []
        assert data["documents"] == []
        assert data["conversation_count"] == 0

    def test_maximum_data_profile(self) -> None:
        """Profile with 50+ facts and multiple issues should serialize correctly."""
        facts = [f"Legal fact number {i}" for i in range(55)]
        issues = [
            LegalIssue(
                issue_type=f"area_{i}",
                summary=f"Issue {i} description",
                status=IssueStatus.OPEN,
            )
            for i in range(10)
        ]

        profile = LegalProfile(
            user_id="user_max",
            display_name="Max Data User",
            state="CA",
            housing_situation="Owner of multi-unit property",
            employment_type="Self-employed, LLC",
            family_status="Married, 3 dependents",
            active_issues=issues,
            legal_facts=facts,
            documents=[f"doc_{i}.pdf" for i in range(20)],
            conversation_count=500,
        )

        assert len(profile.legal_facts) == 55
        assert len(profile.active_issues) == 10
        assert len(profile.documents) == 20

        # Round-trip
        restored = LegalProfile.model_validate_json(profile.model_dump_json())
        assert len(restored.legal_facts) == 55


class TestToContextString:
    """Verify to_context_string() output for prompt injection."""

    def test_context_string_includes_state(self, mock_profile) -> None:
        """Context string should include the user's state."""
        ctx = mock_profile.to_context_string()
        parsed = json.loads(ctx)

        assert parsed["state"] == "MA"

    def test_context_string_includes_active_issues(self, mock_profile) -> None:
        """Context string should include active issues when present."""
        ctx = mock_profile.to_context_string()
        parsed = json.loads(ctx)

        assert "active_issues" in parsed
        assert parsed["active_issues"][0]["type"] == "landlord_tenant"
        assert parsed["active_issues"][0]["status"] == "open"

    def test_context_string_includes_known_facts(self, mock_profile) -> None:
        """Context string should include legal facts when present."""
        ctx = mock_profile.to_context_string()
        parsed = json.loads(ctx)

        assert "known_facts" in parsed
        assert len(parsed["known_facts"]) == 8

    def test_context_string_omits_empty_issues_and_facts(self) -> None:
        """Context string should omit active_issues and known_facts when empty."""
        profile = LegalProfile(
            user_id="user_min",
            display_name="Minimal",
            state="NY",
            housing_situation="renter",
            employment_type="W-2",
            family_status="single",
        )
        ctx = profile.to_context_string()
        parsed = json.loads(ctx)

        assert "active_issues" not in parsed
        assert "known_facts" not in parsed
        assert parsed["state"] == "NY"

    def test_context_string_is_valid_json(self, mock_profile) -> None:
        """to_context_string must always return valid JSON."""
        ctx = mock_profile.to_context_string()
        parsed = json.loads(ctx)  # Should not raise
        assert isinstance(parsed, dict)


class TestLegalIssue:
    """Verify LegalIssue model validation and defaults."""

    def test_default_status_is_open(self) -> None:
        """New issues should default to OPEN status."""
        issue = LegalIssue(
            issue_type="employment",
            summary="Wrongful termination claim",
        )
        assert issue.status == IssueStatus.OPEN

    def test_default_notes_is_empty(self) -> None:
        """Notes should default to empty list."""
        issue = LegalIssue(
            issue_type="consumer",
            summary="Defective product claim",
        )
        assert issue.notes == []

    def test_timestamps_are_set(self) -> None:
        """started_at and updated_at should be auto-populated."""
        issue = LegalIssue(
            issue_type="traffic",
            summary="Speeding ticket dispute",
        )
        assert issue.started_at is not None
        assert issue.updated_at is not None

    def test_all_status_values(self) -> None:
        """All IssueStatus enum values should be valid."""
        for status in IssueStatus:
            issue = LegalIssue(
                issue_type="test",
                summary="Test issue",
                status=status,
            )
            assert issue.status == status

    def test_issue_serialization(self) -> None:
        """LegalIssue should serialize to dict with all fields."""
        issue = LegalIssue(
            issue_type="landlord_tenant",
            summary="Security deposit not returned",
            status=IssueStatus.ESCALATED,
            notes=["Filed complaint", "Awaiting response"],
        )
        data = issue.model_dump()

        assert data["issue_type"] == "landlord_tenant"
        assert data["status"] == "escalated"
        assert len(data["notes"]) == 2


class TestResponseModels:
    """Verify response model serialization."""

    def test_health_response(self) -> None:
        """HealthResponse serializes correctly."""
        resp = HealthResponse(status="ok", version="0.1.0")
        data = resp.model_dump()
        assert data == {"status": "ok", "version": "0.1.0"}

    def test_delete_response(self) -> None:
        """DeleteResponse serializes correctly."""
        resp = DeleteResponse(status="deleted")
        assert resp.model_dump() == {"status": "deleted"}

    def test_waitlist_response(self) -> None:
        """WaitlistResponse serializes correctly."""
        resp = WaitlistResponse(success=True)
        assert resp.model_dump() == {"success": True}

    def test_waitlist_response_false(self) -> None:
        """WaitlistResponse handles failure case."""
        resp = WaitlistResponse(success=False)
        assert resp.success is False

    def test_health_response_json_round_trip(self) -> None:
        """HealthResponse should survive JSON round-trip."""
        resp = HealthResponse(status="ok", version="1.2.3")
        restored = HealthResponse.model_validate_json(resp.model_dump_json())
        assert restored.status == "ok"
        assert restored.version == "1.2.3"
