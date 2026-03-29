"""Tests for the Anthropic client singleton.

Covers instance creation, singleton behavior, and timeout configuration.
"""

from __future__ import annotations

from unittest.mock import patch

import anthropic

from backend.utils.client import get_anthropic_client


def test_returns_async_anthropic_instance():
    """get_anthropic_client() returns an AsyncAnthropic instance."""
    with patch("backend.utils.client._client", None):
        client = get_anthropic_client()
        assert isinstance(client, anthropic.AsyncAnthropic)


def test_singleton_returns_same_instance():
    """Repeated calls return the same client instance."""
    with patch("backend.utils.client._client", None):
        client1 = get_anthropic_client()
        client2 = get_anthropic_client()
        assert client1 is client2


def test_timeout_configured():
    """Client is configured with 30s timeout."""
    with patch("backend.utils.client._client", None):
        client = get_anthropic_client()
        assert client.timeout == 30.0


def test_uses_api_key_from_environment():
    """Client should use ANTHROPIC_API_KEY from environment."""
    with (
        patch("backend.utils.client._client", None),
        patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test-key-123"}),
    ):
        client = get_anthropic_client()
        assert client.api_key == "sk-ant-test-key-123"


def test_empty_api_key_when_env_missing():
    """Client should get empty string when ANTHROPIC_API_KEY is not set."""
    import os

    env_copy = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    with (
        patch("backend.utils.client._client", None),
        patch.dict("os.environ", env_copy, clear=True),
    ):
        client = get_anthropic_client()
        assert client.api_key == ""


def test_singleton_resets_when_cleared():
    """After clearing the module-level _client, a new instance is created."""
    with patch("backend.utils.client._client", None):
        client1 = get_anthropic_client()

    # Simulate clearing the singleton
    with patch("backend.utils.client._client", None):
        client2 = get_anthropic_client()

    # These are different instances because _client was reset between calls
    assert client1 is not client2
