"""Tests for the keyword-based legal domain classifier.

The classifier must be fast and deterministic — it runs on every user
message before the Claude API call.
"""

from __future__ import annotations

import pytest

from backend.legal.classifier import classify_legal_area


class TestClassifyLegalArea:
    """Test all 10 legal domains plus general fallback and edge cases."""

    def test_classify_landlord_tenant(self) -> None:
        result = classify_legal_area("can my landlord keep my deposit")
        assert result == "landlord_tenant"

    def test_classify_employment(self) -> None:
        result = classify_legal_area("my boss fired me without notice")
        assert result == "employment_rights"

    def test_classify_consumer(self) -> None:
        result = classify_legal_area("the product I bought is defective")
        assert result == "consumer_protection"

    def test_classify_debt(self) -> None:
        result = classify_legal_area("a debt collector keeps calling me")
        assert result == "debt_collections"

    def test_classify_small_claims(self) -> None:
        result = classify_legal_area("I want to sue for $3000")
        assert result == "small_claims"

    def test_classify_contracts(self) -> None:
        result = classify_legal_area("they breached our contract")
        assert result == "contract_disputes"

    def test_classify_traffic(self) -> None:
        result = classify_legal_area("I got a speeding ticket")
        assert result == "traffic_violations"

    def test_classify_family(self) -> None:
        result = classify_legal_area("I'm going through a divorce")
        assert result == "family_law"

    def test_classify_criminal(self) -> None:
        result = classify_legal_area("how do I expunge my record")
        assert result == "criminal_records"

    def test_classify_immigration(self) -> None:
        result = classify_legal_area("my visa is expiring")
        assert result == "immigration"

    def test_classify_general_fallback(self) -> None:
        result = classify_legal_area("hello how are you")
        assert result == "general"

    def test_classify_case_insensitive(self) -> None:
        result = classify_legal_area("MY LANDLORD WON'T RETURN MY DEPOSIT")
        assert result == "landlord_tenant"

    def test_classify_empty_string(self) -> None:
        result = classify_legal_area("")
        assert result == "general"

    def test_classify_multiple_keywords_picks_highest_score(self) -> None:
        # "landlord" + "tenant" + "rent" + "deposit" = 4 hits for landlord_tenant
        result = classify_legal_area(
            "my landlord as a tenant with rent issues about my security deposit"
        )
        assert result == "landlord_tenant"

    def test_classify_mixed_domains_picks_dominant(self) -> None:
        # "fired" = 1 employment, "landlord" + "tenant" + "eviction" = 3 landlord
        result = classify_legal_area(
            "I was fired and now my landlord is threatening tenant eviction"
        )
        assert result == "landlord_tenant"
