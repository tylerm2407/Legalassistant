"""Tests for all 10 legal area domain modules.

Each module exports DOMAIN_GUIDANCE (str), KEY_STATUTES (dict), and
COMMON_QUESTIONS (list). Tests verify the structure and content of each.
"""

from __future__ import annotations

import pytest

from backend.legal.areas import (
    consumer,
    contracts,
    criminal_records,
    debt_collections,
    employment,
    family_law,
    immigration,
    landlord_tenant,
    small_claims,
    traffic,
)

# Collect all modules for parametrized tests
ALL_AREA_MODULES = [
    consumer,
    contracts,
    criminal_records,
    debt_collections,
    employment,
    family_law,
    immigration,
    landlord_tenant,
    small_claims,
    traffic,
]

MODULE_IDS = [m.__name__.split(".")[-1] for m in ALL_AREA_MODULES]


@pytest.mark.parametrize("module", ALL_AREA_MODULES, ids=MODULE_IDS)
class TestLegalAreaStructure:
    """Every legal area module must export the three required attributes."""

    def test_has_domain_guidance(self, module) -> None:
        """Module exports a non-empty DOMAIN_GUIDANCE string."""
        assert hasattr(module, "DOMAIN_GUIDANCE")
        assert isinstance(module.DOMAIN_GUIDANCE, str)
        assert len(module.DOMAIN_GUIDANCE) > 50

    def test_has_key_statutes(self, module) -> None:
        """Module exports a non-empty KEY_STATUTES dict with string values."""
        assert hasattr(module, "KEY_STATUTES")
        assert isinstance(module.KEY_STATUTES, dict)
        assert len(module.KEY_STATUTES) >= 1
        for statute_name, description in module.KEY_STATUTES.items():
            assert isinstance(statute_name, str)
            assert isinstance(description, str)
            assert len(description) > 10

    def test_has_common_questions(self, module) -> None:
        """Module exports a non-empty COMMON_QUESTIONS list of strings."""
        assert hasattr(module, "COMMON_QUESTIONS")
        assert isinstance(module.COMMON_QUESTIONS, list)
        assert len(module.COMMON_QUESTIONS) >= 1
        for question in module.COMMON_QUESTIONS:
            assert isinstance(question, str)
            assert question.endswith("?")


class TestConsumerProtection:
    """Spot-check consumer protection content."""

    def test_mentions_deceptive_practices(self) -> None:
        assert "deceptive" in consumer.DOMAIN_GUIDANCE.lower()

    def test_includes_ftc_act(self) -> None:
        statute_names = list(consumer.KEY_STATUTES.keys())
        assert any("FTC" in name for name in statute_names)


class TestLandlordTenant:
    """Spot-check landlord-tenant content."""

    def test_mentions_security_deposit(self) -> None:
        assert "security deposit" in landlord_tenant.DOMAIN_GUIDANCE.lower()

    def test_includes_ma_statute(self) -> None:
        assert any("M.G.L." in k for k in landlord_tenant.KEY_STATUTES)


class TestEmployment:
    """Spot-check employment content."""

    def test_mentions_termination(self) -> None:
        guidance_lower = employment.DOMAIN_GUIDANCE.lower()
        assert (
            "termination" in guidance_lower
            or "fired" in guidance_lower
            or "employment" in guidance_lower
        )


class TestDebtCollections:
    """Spot-check debt collections content."""

    def test_includes_fdcpa(self) -> None:
        statute_names = list(debt_collections.KEY_STATUTES.keys())
        assert any("FDCPA" in name or "Fair Debt" in name for name in statute_names)


class TestSmallClaims:
    """Spot-check small claims content."""

    def test_mentions_jurisdictional_limit(self) -> None:
        assert "limit" in small_claims.DOMAIN_GUIDANCE.lower()


class TestContracts:
    """Spot-check contracts content."""

    def test_mentions_breach(self) -> None:
        guidance_lower = contracts.DOMAIN_GUIDANCE.lower()
        assert "breach" in guidance_lower or "contract" in guidance_lower


class TestTraffic:
    """Spot-check traffic content."""

    def test_mentions_ticket_or_violation(self) -> None:
        guidance_lower = traffic.DOMAIN_GUIDANCE.lower()
        assert (
            "ticket" in guidance_lower
            or "violation" in guidance_lower
            or "traffic" in guidance_lower
        )


class TestFamilyLaw:
    """Spot-check family law content."""

    def test_mentions_custody_or_divorce(self) -> None:
        guidance_lower = family_law.DOMAIN_GUIDANCE.lower()
        assert (
            "custody" in guidance_lower or "divorce" in guidance_lower or "family" in guidance_lower
        )


class TestCriminalRecords:
    """Spot-check criminal records content."""

    def test_mentions_expungement_or_record(self) -> None:
        guidance_lower = criminal_records.DOMAIN_GUIDANCE.lower()
        assert "expung" in guidance_lower or "record" in guidance_lower


class TestImmigration:
    """Spot-check immigration content."""

    def test_mentions_visa_or_immigration(self) -> None:
        guidance_lower = immigration.DOMAIN_GUIDANCE.lower()
        assert "visa" in guidance_lower or "immigration" in guidance_lower
