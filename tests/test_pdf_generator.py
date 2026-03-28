"""Tests for the PDF generator module.

Verifies that all four public generation functions return valid PDF
bytes (starting with the %PDF magic bytes from fpdf2).
"""

from __future__ import annotations

from backend.export.pdf_generator import (
    generate_checklist_document,
    generate_demand_letter_document,
    generate_rights_document,
    generate_text_document,
)


class TestGenerateTextDocument:
    """Verify generate_text_document produces valid PDF output."""

    def test_returns_pdf_bytes(self) -> None:
        result = generate_text_document(
            title="Test Document",
            content="This is a test legal document with some content.",
            user_name="Sarah Chen",
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_with_sections(self) -> None:
        result = generate_text_document(
            title="Multi-Section Doc",
            content="Main body text.",
            sections=[
                {"heading": "Section One", "body": "First section body."},
                {"heading": "Section Two", "body": "Second section body."},
            ],
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"
        assert len(result) > 100  # Non-trivial PDF


class TestGenerateDemandLetterDocument:
    """Verify generate_demand_letter_document produces valid PDF output."""

    def test_returns_pdf_with_citations(self) -> None:
        result = generate_demand_letter_document(
            letter_text="Dear Sir, I demand the return of my security deposit.",
            legal_citations=[
                "M.G.L. c. 186, s. 15B",
                "42 U.S.C. ss 3601-3619 (Fair Housing Act)",
            ],
            user_name="Sarah Chen",
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_returns_pdf_without_citations(self) -> None:
        result = generate_demand_letter_document(
            letter_text="Simple demand letter text.",
            legal_citations=[],
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"


class TestGenerateRightsDocument:
    """Verify generate_rights_document produces valid PDF output."""

    def test_returns_pdf_with_rights(self) -> None:
        result = generate_rights_document(
            summary_text="As a tenant in Massachusetts, you have the following rights.",
            key_rights=[
                "Right to habitable premises",
                "Right to security deposit return within 30 days",
                "Right to sue for treble damages",
            ],
            user_name="Sarah Chen",
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"


class TestGenerateChecklistDocument:
    """Verify generate_checklist_document produces valid PDF output."""

    def test_returns_pdf_with_deadlines(self) -> None:
        result = generate_checklist_document(
            items=["Send demand letter", "File small claims", "Attend hearing"],
            deadlines=["2026-04-01", "2026-04-15", None],
            user_name="Sarah Chen",
        )
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_returns_pdf_with_empty_items(self) -> None:
        result = generate_checklist_document(items=[], deadlines=[])
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"
