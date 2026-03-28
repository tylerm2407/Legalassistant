"""Text extraction from uploaded legal documents.

Supports PDF, plain text, and image files. PDF extraction uses pdfplumber
for accurate text recovery from scanned and digital PDFs. Image OCR
support is noted as a future enhancement.
"""

from __future__ import annotations

import io

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """Extract text content from uploaded file bytes.

    Supports PDF files via pdfplumber, plain text files via UTF-8 decoding,
    and returns a placeholder message for image files indicating OCR is
    not yet implemented.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        content_type: MIME type of the file (e.g. 'application/pdf',
                      'text/plain', 'image/png').

    Returns:
        Extracted text content as a string.

    Raises:
        ValueError: If the content type is not supported.
        RuntimeError: If PDF text extraction fails.
    """
    if content_type == "application/pdf":
        return _extract_pdf(file_bytes)
    elif content_type.startswith("text/"):
        return _extract_text(file_bytes)
    elif content_type.startswith("image/"):
        return _extract_image_placeholder(content_type)
    else:
        raise ValueError(
            f"Unsupported content type: {content_type}. "
            "Supported types: application/pdf, text/*, image/*"
        )


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Concatenated text from all PDF pages.

    Raises:
        RuntimeError: If pdfplumber fails to extract text.
    """
    try:
        import pdfplumber

        pages_text: list[str] = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

        result = "\n\n".join(pages_text)
        _logger.info("pdf_extracted", page_count=len(pages_text), char_count=len(result))
        return result

    except ImportError as exc:
        raise RuntimeError(
            "pdfplumber is required for PDF extraction. "
            "Install it with: pip install pdfplumber"
        ) from exc
    except Exception as exc:
        _logger.error(
            "pdf_extraction_error",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to extract text from PDF: {exc}") from exc


def _extract_text(file_bytes: bytes) -> str:
    """Decode plain text file bytes as UTF-8.

    Args:
        file_bytes: Raw bytes of the text file.

    Returns:
        Decoded text content.

    Raises:
        ValueError: If the bytes cannot be decoded as UTF-8.
    """
    try:
        result = file_bytes.decode("utf-8")
        _logger.info("text_extracted", char_count=len(result))
        return result
    except UnicodeDecodeError as exc:
        raise ValueError(f"Failed to decode text file as UTF-8: {exc}") from exc


def _extract_image_placeholder(content_type: str) -> str:
    """Return a placeholder message for image files.

    Image OCR support is planned but not yet implemented. This returns
    a descriptive message so the caller can handle it gracefully.

    Args:
        content_type: The MIME type of the image file.

    Returns:
        A placeholder string indicating OCR is not yet available.
    """
    _logger.info("image_ocr_placeholder", content_type=content_type)
    return (
        f"[Image file received ({content_type}). "
        "OCR text extraction is not yet implemented. "
        "Please upload the document as a PDF or text file for full analysis, "
        "or describe the contents of the image in your message.]"
    )
