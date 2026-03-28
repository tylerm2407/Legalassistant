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
