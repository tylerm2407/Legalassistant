"""Real statute citations organized by state and legal domain.

This module provides the STATE_LAWS dictionary, which maps state codes
and legal domains to concise descriptions of applicable laws with real
statute citations. Used by the memory injector and action generators
to ground Claude's responses in actual law.

All 50 states plus federal_defaults.
"""

from __future__ import annotations

from backend.legal.states import STATE_LAWS

__all__ = ["STATE_LAWS"]
