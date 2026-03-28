"""Tests for the document analyzer.

Covers valid analysis, missing keys, JSON parse errors,
empty documents, and profile context inclusion.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import TextBlock

from backend.documents.analyzer import analyze_document
from backend.models.legal_profile import LegalProfile


@pytest.fixture
def test_profile() -> LegalProfile:
    """Return a minimal profile for document analysis tests."""
    return LegalProfile(
        user_id="user_doc_test",
        display_name="Doc Tester",
        state="CA",
        housing_situation="renter",
        employment_type="W-2",
        family_status="single",
    )


def _mock_claude_response(text: str) -> MagicMock:
    """Build a mock Claude API response with given text."""
    content_block = MagicMock(spec=TextBlock)
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


@pytest.mark.asyncio
async def test_valid_document_returns_structured_analysis(test_profile):
    """A valid Claude response returns all expected fields."""
    analysis_result = {
        "document_type": "lease agreement",
        "key_facts": ["12-month term", "$2000/month"],
        "red_flags": ["No repair clause"],
        "summary": "This is a standard lease.",
    }
    mock_response = _mock_claude_response(json.dumps(analysis_result))
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("backend.documents.analyzer.get_anthropic_client", return_value=mock_client):
        result = await analyze_document(text="Lease text here.", profile=test_profile)
        assert result["document_type"] == "lease agreement"
        assert len(result["key_facts"]) == 2
        assert len(result["red_flags"]) == 1
        assert "summary" in result


@pytest.mark.asyncio
async def test_missing_keys_get_defaults(test_profile):
    """Missing keys in Claude response get populated with defaults."""
    partial_result = {
        "document_type": "notice",
        "summary": "A notice was served.",
    }
    mock_response = _mock_claude_response(json.dumps(partial_result))
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("backend.documents.analyzer.get_anthropic_client", return_value=mock_client):
        result = await analyze_document(text="Notice text.", profile=test_profile)
        assert result["document_type"] == "notice"
        assert result["key_facts"] == []
        assert result["red_flags"] == []


@pytest.mark.asyncio
async def test_json_parse_error_raises_runtime_error(test_profile):
    """Non-JSON Claude response raises RuntimeError."""
    mock_response = _mock_claude_response("This is not JSON at all.")
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("backend.documents.analyzer.get_anthropic_client", return_value=mock_client):
        with pytest.raises(RuntimeError, match="Failed to parse"):
            await analyze_document(text="Some document.", profile=test_profile)


@pytest.mark.asyncio
async def test_empty_document_still_processes(test_profile):
    """An empty document string still calls Claude and returns result."""
    analysis_result = {
        "document_type": "unknown",
        "key_facts": [],
        "red_flags": [],
        "summary": "Empty document.",
    }
    mock_response = _mock_claude_response(json.dumps(analysis_result))
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("backend.documents.analyzer.get_anthropic_client", return_value=mock_client):
        result = await analyze_document(text="", profile=test_profile)
        assert result["document_type"] == "unknown"


@pytest.mark.asyncio
async def test_profile_context_included_in_prompt(test_profile):
    """The user's profile context is sent to Claude in the message."""
    analysis_result = {
        "document_type": "lease",
        "key_facts": [],
        "red_flags": [],
        "summary": "Analysis.",
    }
    mock_response = _mock_claude_response(json.dumps(analysis_result))
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("backend.documents.analyzer.get_anthropic_client", return_value=mock_client):
        await analyze_document(text="Lease text.", profile=test_profile)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get("messages", [])
        user_message = messages[0]["content"]
        assert "CA" in user_message
        assert "USER PROFILE" in user_message
