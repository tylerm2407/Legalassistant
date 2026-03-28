"""50-state law coverage organized by geographic region.

Merges all regional modules into a single STATE_LAWS dictionary
keyed by two-letter state code (plus ``federal_defaults``).
"""

from __future__ import annotations

from backend.legal.states.federal import FEDERAL_DEFAULTS
from backend.legal.states.midwest import MIDWEST_LAWS
from backend.legal.states.northeast import NORTHEAST_LAWS
from backend.legal.states.south_central import SOUTH_CENTRAL_LAWS
from backend.legal.states.southeast import SOUTHEAST_LAWS
from backend.legal.states.west import WEST_LAWS

STATE_LAWS: dict[str, dict[str, str]] = {
    **FEDERAL_DEFAULTS,
    **NORTHEAST_LAWS,
    **SOUTHEAST_LAWS,
    **MIDWEST_LAWS,
    **SOUTH_CENTRAL_LAWS,
    **WEST_LAWS,
}

__all__ = ["STATE_LAWS"]
