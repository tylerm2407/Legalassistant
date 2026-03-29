"""Tests for the Anthropic API retry decorator.

Verifies retry behavior, exponential backoff, logging, and that
non-retryable errors propagate immediately.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import pytest
import tenacity

from backend.utils.retry import _log_retry, retry_anthropic


class TestRetryDecorator:
    """Verify retry_anthropic decorator behavior."""

    async def test_successful_call_no_retry(self) -> None:
        """A successful call should return immediately without retrying."""
        mock_fn = AsyncMock(return_value="success")
        decorated = retry_anthropic(mock_fn)

        result = await decorated()

        assert result == "success"
        assert mock_fn.call_count == 1

    async def test_retry_on_api_error_recovers_second_attempt(self) -> None:
        """Should retry on APIError and succeed on the second attempt."""
        mock_fn = AsyncMock(
            side_effect=[
                anthropic.APIError(
                    message="server error",
                    request=MagicMock(),
                    body=None,
                ),
                "recovered",
            ]
        )
        decorated = retry_anthropic(mock_fn)

        result = await decorated()

        assert result == "recovered"
        assert mock_fn.call_count == 2

    async def test_retry_on_rate_limit_error_recovers_third_attempt(self) -> None:
        """Should retry on RateLimitError and succeed on the third attempt."""
        rate_limit_err = anthropic.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        mock_fn = AsyncMock(side_effect=[rate_limit_err, rate_limit_err, "recovered"])
        decorated = retry_anthropic(mock_fn)

        result = await decorated()

        assert result == "recovered"
        assert mock_fn.call_count == 3

    async def test_max_retries_exhausted_raises(self) -> None:
        """After 3 failed attempts, the original exception should be re-raised."""
        api_err = anthropic.APIError(
            message="persistent failure",
            request=MagicMock(),
            body=None,
        )
        mock_fn = AsyncMock(side_effect=api_err)
        decorated = retry_anthropic(mock_fn)

        with pytest.raises(anthropic.APIError, match="persistent failure"):
            await decorated()

        assert mock_fn.call_count == 3

    async def test_non_retryable_error_not_retried(self) -> None:
        """A ValueError (non-API error) should NOT be retried — it propagates immediately."""
        mock_fn = AsyncMock(side_effect=ValueError("bad input"))
        decorated = retry_anthropic(mock_fn)

        with pytest.raises(ValueError, match="bad input"):
            await decorated()

        assert mock_fn.call_count == 1

    async def test_exponential_backoff_configuration(self) -> None:
        """Verify the wait strategy is exponential with correct min/max."""
        # Access the retry object's wait configuration
        mock_fn = AsyncMock(return_value="ok")
        decorated = retry_anthropic(mock_fn)

        # The decorated function has retry attributes from tenacity
        retry_obj = decorated.retry
        wait = retry_obj.wait

        assert isinstance(wait, tenacity.wait_exponential)
        assert wait.multiplier == 1
        assert wait.min == 1
        assert wait.max == 16

    async def test_stop_after_3_attempts(self) -> None:
        """Verify stop configuration is set to 3 attempts."""
        mock_fn = AsyncMock(return_value="ok")
        decorated = retry_anthropic(mock_fn)

        stop = decorated.retry.stop
        assert isinstance(stop, tenacity.stop_after_attempt)
        assert stop.max_attempt_number == 3

    async def test_decorator_preserves_return_value(self) -> None:
        """Decorated function should return the original function's return value."""
        expected = {"response": "legal advice", "citations": ["M.G.L. c.186"]}
        mock_fn = AsyncMock(return_value=expected)
        decorated = retry_anthropic(mock_fn)

        result = await decorated()

        assert result == expected


class TestLogRetry:
    """Verify the _log_retry callback logs structured info."""

    def test_log_retry_with_exception(self) -> None:
        """_log_retry should log attempt number and exception details."""
        retry_state = MagicMock()
        retry_state.attempt_number = 2
        exc = anthropic.APIError(
            message="server error",
            request=MagicMock(),
            body=None,
        )
        retry_state.outcome.exception.return_value = exc
        retry_state.next_action.sleep = 2.0

        with patch("backend.utils.retry._logger") as mock_logger:
            _log_retry(retry_state)

            mock_logger.warning.assert_called_once_with(
                "anthropic_api_retry",
                attempt=2,
                exception_type="APIError",
                exception_message=str(exc),
                wait_seconds=2.0,
            )

    def test_log_retry_with_no_outcome(self) -> None:
        """_log_retry handles None outcome gracefully."""
        retry_state = MagicMock()
        retry_state.attempt_number = 1
        retry_state.outcome = None
        retry_state.next_action.sleep = 1.0

        with patch("backend.utils.retry._logger") as mock_logger:
            _log_retry(retry_state)

            mock_logger.warning.assert_called_once_with(
                "anthropic_api_retry",
                attempt=1,
                exception_type=None,
                exception_message=None,
                wait_seconds=1.0,
            )
