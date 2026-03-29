"""Audio transcription via the OpenAI Whisper API.

Provides a single async function that sends audio bytes to the OpenAI
Whisper API and returns the transcript text. Supports mp3, mp4, mpeg,
mpga, m4a, wav, and webm formats.
"""

from __future__ import annotations

import io
import os

from openai import AsyncOpenAI, APIError
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.utils.logger import get_logger

_logger = get_logger(__name__)

_SUPPORTED_FORMATS: frozenset[str] = frozenset(
    {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
)


def _get_openai_client() -> AsyncOpenAI:
    """Return a module-level singleton AsyncOpenAI client.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        _logger.error("openai_api_key_not_set")
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return AsyncOpenAI(api_key=api_key)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
async def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """Send audio to OpenAI Whisper API and return the transcript text.

    Retries up to 3 times with exponential backoff (2s, 4s, 8s) on
    transient API failures.

    Args:
        audio_bytes: Raw audio file content. Accepted formats are mp3,
            mp4, mpeg, mpga, m4a, wav, and webm.
        language: ISO-639-1 language code for the audio. Defaults to ``"en"``.

    Returns:
        The transcribed text string.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
        openai.APIError: If the Whisper API request fails after all retries.
    """
    client = _get_openai_client()

    _logger.info(
        "transcription_started",
        audio_size_bytes=len(audio_bytes),
        language=language,
    )

    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"

        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
        )

        _logger.info(
            "transcription_completed",
            transcript_length=len(transcript.text),
            language=language,
        )

        return transcript.text

    except APIError as exc:
        _logger.error(
            "transcription_failed",
            error=str(exc),
            status_code=getattr(exc, "status_code", None),
        )
        raise
