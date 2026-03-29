"""Text extraction from uploaded legal documents.

Supports PDF, plain text, and image files. PDF extraction uses pdfplumber
for accurate text recovery from scanned and digital PDFs. Image OCR
uses pytesseract with Pillow for text extraction from uploaded images.
"""

from __future__ import annotations

import io

from backend.utils.logger import get_logger

_logger = get_logger(__name__)


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """Extract text content from uploaded file bytes.

    Supports PDF files via pdfplumber, plain text files via UTF-8 decoding,
    and image files via pytesseract OCR.

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
        return _extract_image(file_bytes, content_type)
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
            "pdfplumber is required for PDF extraction. Install it with: pip install pdfplumber"
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


def _extract_image(file_bytes: bytes, content_type: str) -> str:
    """Extract text from image bytes using Tesseract OCR.

    Uses pytesseract (a Python wrapper for Google's Tesseract OCR engine)
    and Pillow for image loading. Both are lazy-imported to match the
    existing pdfplumber pattern and avoid hard failures at import time.

    Falls back to a descriptive error message if the tesseract binary
    is not installed on the host system.

    Args:
        file_bytes: Raw bytes of the image file.
        content_type: The MIME type of the image (e.g. 'image/png').

    Returns:
        Extracted text from the image via OCR.

    Raises:
        RuntimeError: If pytesseract or Pillow are not installed, or if
            the tesseract binary is not available on the system PATH.
    """
    try:
        import pytesseract  # type: ignore[import-untyped]
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "pytesseract and Pillow are required for image OCR. "
            "Install them with: pip install pytesseract Pillow"
        ) from exc

    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        result = text.strip()

        _logger.info(
            "image_ocr_extracted",
            content_type=content_type,
            char_count=len(result),
            image_size=f"{image.width}x{image.height}",
        )

        if not result:
            _logger.warning(
                "image_ocr_empty",
                content_type=content_type,
                detail="OCR produced no text — image may be blank or non-textual",
            )
            return (
                "[OCR extracted no readable text from this image. "
                "The image may not contain text, or the text may be "
                "too small or unclear for OCR.]"
            )

        return str(result)

    except Exception as exc:
        if "tesseract" in str(exc).lower() or "not installed" in str(exc).lower():
            _logger.error(
                "tesseract_not_installed",
                error=str(exc),
            )
            raise RuntimeError(
                "Tesseract OCR engine is not installed. "
                "Install it with: sudo apt-get install tesseract-ocr (Linux) "
                "or brew install tesseract (macOS)"
            ) from exc

        _logger.error(
            "image_ocr_error",
            content_type=content_type,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to extract text from image: {exc}") from exc
