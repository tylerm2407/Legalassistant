"""Tests for backend.documents.extractor — text extraction from uploads.

Covers PDF extraction, plain text decoding, image placeholder,
unsupported types, and error handling.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.documents.extractor import extract_text


class TestExtractText:
    """Route-level tests for extract_text dispatcher."""

    def test_plain_text_extraction(self) -> None:
        """Decodes UTF-8 text bytes correctly."""
        content = "This is a lease agreement between the landlord and tenant."
        result = extract_text(content.encode("utf-8"), "text/plain")
        assert result == content

    def test_text_html_extraction(self) -> None:
        """Handles text/* subtypes (e.g. text/html)."""
        html = "<html><body>Legal notice</body></html>"
        result = extract_text(html.encode("utf-8"), "text/html")
        assert result == html

    def test_image_returns_placeholder(self) -> None:
        """Image files return an OCR placeholder message."""
        result = extract_text(b"\x89PNG", "image/png")
        assert "OCR text extraction is not yet implemented" in result
        assert "image/png" in result

    def test_image_jpeg_returns_placeholder(self) -> None:
        """JPEG images also return placeholder."""
        result = extract_text(b"\xff\xd8\xff", "image/jpeg")
        assert "image/jpeg" in result

    def test_unsupported_type_raises(self) -> None:
        """Unsupported content types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported content type"):
            extract_text(b"data", "application/zip")

    def test_invalid_utf8_raises(self) -> None:
        """Non-UTF-8 bytes with text/* type raise ValueError."""
        with pytest.raises(ValueError, match="Failed to decode"):
            extract_text(b"\xff\xfe\x00\x01", "text/plain")

    def test_pdf_extraction_with_mock(self) -> None:
        """PDF extraction delegates to pdfplumber and joins pages."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page one content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page two content"

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("backend.documents.extractor.pdfplumber", create=True) as mock_pdfplumber:
            mock_pdfplumber.open.return_value = mock_pdf
            # Patch the import inside the function
            with patch.dict("sys.modules", {"pdfplumber": mock_pdfplumber}):
                result = extract_text(b"%PDF-fake", "application/pdf")
                assert "Page one content" in result
                assert "Page two content" in result

    def test_pdf_empty_pages(self) -> None:
        """PDF with pages that return None text produces empty string."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("backend.documents.extractor.pdfplumber", create=True) as mock_pdfplumber:
            mock_pdfplumber.open.return_value = mock_pdf
            with patch.dict("sys.modules", {"pdfplumber": mock_pdfplumber}):
                result = extract_text(b"%PDF-fake", "application/pdf")
                assert result == ""

    def test_pdf_extraction_error_raises_runtime(self) -> None:
        """RuntimeError raised when pdfplumber fails."""
        with patch.dict("sys.modules", {"pdfplumber": MagicMock()}) as modules:
            modules["pdfplumber"].open.side_effect = Exception("corrupt PDF")
            with pytest.raises(RuntimeError, match="Failed to extract text from PDF"):
                extract_text(b"%PDF-corrupt", "application/pdf")
