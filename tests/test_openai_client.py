"""Tests for the OpenAI client singleton.

Covers instance creation, missing API key error, and singleton behavior.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from openai import AsyncOpenAI

from backend.utils.openai_client import get_openai_client


def test_returns_async_openai_instance():
    """get_openai_client() returns an AsyncOpenAI instance when key is set."""
    with (
        patch("backend.utils.openai_client._client", None),
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"}),
    ):
        client = get_openai_client()
        assert isinstance(client, AsyncOpenAI)


def test_raises_valueerror_when_api_key_missing():
    """get_openai_client() raises ValueError when OPENAI_API_KEY is not set."""
    env_copy = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with (
        patch("backend.utils.openai_client._client", None),
        patch.dict(os.environ, env_copy, clear=True),
    ):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            get_openai_client()


def test_singleton_returns_same_instance():
    """Repeated calls return the same client instance."""
    with (
        patch("backend.utils.openai_client._client", None),
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"}),
    ):
        client1 = get_openai_client()
        client2 = get_openai_client()
        assert client1 is client2


def test_singleton_resets_when_cleared():
    """After clearing the module-level _client, a new instance is created."""
    with (
        patch("backend.utils.openai_client._client", None),
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"}),
    ):
        client1 = get_openai_client()

    with (
        patch("backend.utils.openai_client._client", None),
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"}),
    ):
        client2 = get_openai_client()

    assert client1 is not client2
