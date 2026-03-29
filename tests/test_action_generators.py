"""Tests for the action generators: demand letters, rights summaries, checklists.

All three generators follow the same pattern: build a prompt with the user's
profile and state laws, call Claude, parse the JSON response into a Pydantic
model. Tests verify the output models and that profile/legal-area context
is passed through to the API call.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models.action_output import Checklist, DemandLetter, RightsSummary
from backend.models.legal_profile import LegalProfile

DEMAND_LETTER_JSON = json.dumps(
    {
        "text": (
            "Dear Mr. Peterson,\n\nI am writing to demand"
            " the return of my $2,400 security deposit..."
        ),
        "citations": ["M.G.L. c. 186, § 15B", "42 U.S.C. § 3601"],
        "recipient": "James Peterson",
        "subject": "Demand for Return of Security Deposit",
    }
)

RIGHTS_SUMMARY_JSON = json.dumps(
    {
        "text": "As a tenant in Massachusetts, you have strong protections under state law...",
        "key_rights": [
            "Right to return of deposit within 30 days",
            "Right to triple damages if deposit is wrongfully withheld",
            "Right to an itemized list of deductions",
        ],
        "applicable_laws": ["M.G.L. c. 186, § 15B", "Fair Housing Act 42 U.S.C. § 3601"],
    }
)

CHECKLIST_JSON = json.dumps(
    {
        "items": [
            "Send a formal demand letter to your landlord",
            "Gather all move-out photos and documentation",
            "File a complaint with the MA Attorney General if no response in 30 days",
            "Consider filing in small claims court for triple damages",
            "Consult with a tenant rights attorney",
        ],
        "deadlines": [
            "Within 7 days",
            None,
            "30 days after demand letter",
            "Within 3 years (statute of limitations)",
            None,
        ],
        "priority_order": [0, 1, 2, 3, 4],
    }
)


def _make_mock_response(text: str) -> MagicMock:
    """Build a mock Anthropic response with the given text."""
    from anthropic.types import TextBlock

    content_block = MagicMock(spec=TextBlock)
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


class TestGenerateDemandLetter:
    """Tests for the demand letter generator."""

    @pytest.mark.asyncio
    async def test_returns_demand_letter_model(self, mock_profile: LegalProfile) -> None:
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_mock_response(DEMAND_LETTER_JSON)
        )

        with patch(
            "backend.actions.letter_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.letter_generator import generate_demand_letter

            result = await generate_demand_letter(
                mock_profile, "My landlord won't return my security deposit"
            )

        assert isinstance(result, DemandLetter)
        assert result.subject == "Demand for Return of Security Deposit"
        assert result.recipient == "James Peterson"
        assert len(result.citations) == 2
        assert "M.G.L." in result.citations[0]
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_letter_includes_profile_state(self, mock_profile: LegalProfile) -> None:
        """Verify the user's state appears in the prompt sent to Claude."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_mock_response(DEMAND_LETTER_JSON)
        )

        with patch(
            "backend.actions.letter_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.letter_generator import generate_demand_letter

            await generate_demand_letter(mock_profile, "Return my deposit")

        # Inspect the system argument passed to create() — profile context is in system, not messages
        call_args = mock_client.messages.create.call_args
        system = call_args.kwargs.get("system") or call_args[1].get("system", [])
        system_text = " ".join(
            block["text"] if isinstance(block, dict) else str(block) for block in system
        )
        assert "MA" in system_text


class TestGenerateRightsSummary:
    """Tests for the rights summary generator."""

    @pytest.mark.asyncio
    async def test_returns_rights_summary_model(self, mock_profile: LegalProfile) -> None:
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_mock_response(RIGHTS_SUMMARY_JSON)
        )

        with patch(
            "backend.actions.rights_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.rights_generator import generate_rights_summary

            result = await generate_rights_summary(
                mock_profile, "What are my rights regarding my security deposit?"
            )

        assert isinstance(result, RightsSummary)
        assert len(result.key_rights) == 3
        assert len(result.applicable_laws) == 2
        assert "triple damages" in result.key_rights[1].lower()
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_rights_includes_legal_area(self, mock_profile: LegalProfile) -> None:
        """Verify the legal domain context is passed in the prompt to Claude."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_mock_response(RIGHTS_SUMMARY_JSON)
        )

        with patch(
            "backend.actions.rights_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.rights_generator import generate_rights_summary

            await generate_rights_summary(mock_profile, "security deposit rights")

        call_args = mock_client.messages.create.call_args
        system = call_args.kwargs.get("system") or call_args[1].get("system", [])
        system_text = " ".join(
            block["text"] if isinstance(block, dict) else str(block) for block in system
        )
        # The system prompt should contain landlord_tenant law text from STATE_LAWS
        assert "landlord_tenant" in system_text or "186" in system_text


class TestGenerateChecklist:
    """Tests for the checklist generator."""

    @pytest.mark.asyncio
    async def test_returns_checklist_model(self, mock_profile: LegalProfile) -> None:
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=_make_mock_response(CHECKLIST_JSON))

        with patch(
            "backend.actions.checklist_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.checklist_generator import generate_checklist

            result = await generate_checklist(
                mock_profile, "What should I do about my security deposit?"
            )

        assert isinstance(result, Checklist)
        assert len(result.items) == 5
        assert len(result.deadlines) == 5
        assert len(result.priority_order) == 5
        assert result.deadlines[1] is None
        assert result.deadlines[0] == "Within 7 days"
        assert result.items[0] == "Send a formal demand letter to your landlord"

    @pytest.mark.asyncio
    async def test_checklist_priority_order_valid(self, mock_profile: LegalProfile) -> None:
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=_make_mock_response(CHECKLIST_JSON))

        with patch(
            "backend.actions.checklist_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.checklist_generator import generate_checklist

            result = await generate_checklist(mock_profile, "next steps")

        # All priority indices should be valid
        for idx in result.priority_order:
            assert 0 <= idx < len(result.items)

    @pytest.mark.asyncio
    async def test_checklist_handles_missing_deadlines(self, mock_profile: LegalProfile) -> None:
        """Verify deadlines list is padded if Claude returns fewer deadlines than items."""
        partial_json = json.dumps(
            {
                "items": ["Step 1", "Step 2", "Step 3"],
                "deadlines": ["Tomorrow"],
                "priority_order": [0, 1, 2],
            }
        )

        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=_make_mock_response(partial_json))

        with patch(
            "backend.actions.checklist_generator.get_anthropic_client", return_value=mock_client
        ):
            from backend.actions.checklist_generator import generate_checklist

            result = await generate_checklist(mock_profile, "next steps")

        assert len(result.deadlines) == 3
        assert result.deadlines[0] == "Tomorrow"
        assert result.deadlines[1] is None
        assert result.deadlines[2] is None
