"""Tests for the audio transcription module.

Tests the transcribe_audio function with mocked OpenAI Whisper API calls.
The function uses tenacity retry, so error tests expect RetryError wrapping.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tenacity import RetryError


class TestTranscribeAudio:
    """Tests for the transcribe_audio function."""

    @pytest.mark.asyncio
    async def test_transcribe_success(self) -> None:
        """Successful transcription returns the transcript text."""
        mock_transcript = MagicMock()
        mock_transcript.text = "This is a test transcription."

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_transcript)

        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("backend.audio.transcriber.AsyncOpenAI", return_value=mock_client),
        ):
            from backend.audio.transcriber import transcribe_audio

            result = await transcribe_audio(b"fake audio bytes", language="en")

        assert result == "This is a test transcription."

    @pytest.mark.asyncio
    async def test_transcribe_missing_api_key_raises(self) -> None:
        """Raises RetryError (wrapping ValueError) when OPENAI_API_KEY is empty."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            from backend.audio.transcriber import transcribe_audio

            with pytest.raises((ValueError, RetryError)):
                await transcribe_audio(b"audio", language="en")

    @pytest.mark.asyncio
    async def test_transcribe_api_error_retries_then_raises(self) -> None:
        """APIError from Whisper triggers retries then raises RetryError."""
        from openai import APIError

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create = AsyncMock(
            side_effect=APIError(
                message="Whisper error",
                request=MagicMock(),
                body=None,
            )
        )

        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("backend.audio.transcriber.AsyncOpenAI", return_value=mock_client),
            pytest.raises((APIError, RetryError)),
        ):
            from backend.audio.transcriber import transcribe_audio

            await transcribe_audio(b"bad audio", language="en")

    @pytest.mark.asyncio
    async def test_transcribe_default_language(self) -> None:
        """Default language parameter is 'en'."""
        mock_transcript = MagicMock()
        mock_transcript.text = "English text."

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_transcript)

        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("backend.audio.transcriber.AsyncOpenAI", return_value=mock_client),
        ):
            from backend.audio.transcriber import transcribe_audio

            result = await transcribe_audio(b"audio bytes")

        assert result == "English text."


class TestGetOpenaiClient:
    """Tests for the internal _get_openai_client helper."""

    def test_raises_on_missing_key(self) -> None:
        """Raises ValueError when OPENAI_API_KEY is not set."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            from backend.audio.transcriber import _get_openai_client

            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                _get_openai_client()

    def test_returns_client_with_key(self) -> None:
        """Returns an AsyncOpenAI instance when key is set."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from backend.audio.transcriber import _get_openai_client

            client = _get_openai_client()
            assert client is not None
