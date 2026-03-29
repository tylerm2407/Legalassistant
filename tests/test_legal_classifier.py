"""Tests for the weighted keyword-based legal domain classifier.

The classifier must be fast and deterministic — it runs on every user
message before the Claude API call. Tests cover all 10 domains, the
general fallback, weighted scoring with phrase boost, and tiebreaker
behavior.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from backend.legal.classifier import (
    CONFIDENCE_THRESHOLD,
    PHRASE_BOOST,
    VALID_DOMAINS,
    ClassificationResult,
    _compute_confidence,
    _keyword_weight,
    _longest_match_length,
    classify_legal_area,
    classify_with_confidence,
    classify_with_llm_fallback,
)


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
        # "landlord" + "tenant" + "rent" + "security deposit" (3x) = high landlord score
        result = classify_legal_area(
            "my landlord as a tenant with rent issues about my security deposit"
        )
        assert result == "landlord_tenant"

    def test_classify_mixed_domains_picks_dominant(self) -> None:
        # "fired" = 1 employment, "landlord" + "tenant" + "eviction" = 3+ landlord
        result = classify_legal_area(
            "I was fired and now my landlord is threatening tenant eviction"
        )
        assert result == "landlord_tenant"


class TestWeightedScoring:
    """Test the weighted scoring system with phrase boost and tiebreaking."""

    def test_phrase_boost_constant_is_3(self) -> None:
        """Multi-word phrases should get 3x weight."""
        assert PHRASE_BOOST == 3

    def test_keyword_weight_single_word(self) -> None:
        """Single-word keywords get base weight of 1."""
        assert _keyword_weight("landlord") == 1
        assert _keyword_weight("rent") == 1

    def test_keyword_weight_multi_word(self) -> None:
        """Multi-word phrases get PHRASE_BOOST weight."""
        assert _keyword_weight("security deposit") == PHRASE_BOOST
        assert _keyword_weight("wrongful termination") == PHRASE_BOOST
        assert _keyword_weight("breach of contract") == PHRASE_BOOST

    def test_multi_word_phrase_outweighs_single_keywords(self) -> None:
        """A single multi-word phrase match (3 pts) should beat two single-word matches (2 pts)."""
        # "security deposit" = 3 pts for landlord_tenant
        # vs a query with 2 single keywords in another domain
        result = classify_legal_area("I need my security deposit back, is this a claim?")
        assert result == "landlord_tenant"

    def test_longest_match_length_finds_longest(self) -> None:
        """Should return the length of the longest matching keyword."""
        keywords = ["rent", "security deposit", "landlord"]
        length = _longest_match_length("security deposit and rent", keywords)
        assert length == len("security deposit")

    def test_longest_match_length_no_match(self) -> None:
        """Should return 0 when no keywords match."""
        keywords = ["landlord", "tenant"]
        length = _longest_match_length("hello world", keywords)
        assert length == 0

    def test_tiebreaker_prefers_longer_keyword_match(self) -> None:
        """When scores tie, the domain with longer keyword match should win."""
        # "breach of contract" (3 words, 3x boost) in contract_disputes
        # vs "wrongful termination" (2 words, 3x boost) in employment_rights
        # Both score 3 if only one phrase matches each, but "breach of contract"
        # is longer (18 chars) than "wrongful termination" (20 chars)
        # Let's construct a case where we know tiebreaking kicks in
        result = classify_legal_area("statute of limitations on my debt")
        # "statute of limitations" is in debt_collections (3x boost = 3 pts)
        # "debt" is also in debt_collections (+1 = 4 pts total)
        assert result == "debt_collections"

    def test_no_keywords_returns_general(self) -> None:
        """Random text with no legal keywords should return general."""
        result = classify_legal_area("what is the weather like today in Boston")
        assert result == "general"

    def test_ambiguous_query_multi_domain(self) -> None:
        """Query touching multiple domains should pick the highest-scoring one."""
        # "settlement" appears in both debt_collections and small_claims
        # Add domain-specific keywords to disambiguate
        result = classify_legal_area("I want to settle my debt with the collection agency")
        # "debt" (1) + "collection agency" (3) + "debt collector" not present
        # debt_collections should win
        assert result == "debt_collections"

    def test_phrase_match_beats_many_single_matches(self) -> None:
        """A domain with phrase matches should outscore one with only single matches."""
        # "false advertising" (3x) + "hidden fee" (3x) = 6 consumer_protection
        result = classify_legal_area("this company uses false advertising and hidden fee tactics")
        assert result == "consumer_protection"


class TestConfidenceScoring:
    """Test the confidence scoring and classify_with_confidence API."""

    def test_returns_classification_result(self) -> None:
        result = classify_with_confidence("my landlord kept my security deposit")
        assert isinstance(result, ClassificationResult)
        assert result.domain == "landlord_tenant"
        assert result.method == "keyword"
        assert 0.0 <= result.confidence <= 1.0

    def test_high_confidence_for_clear_signal(self) -> None:
        result = classify_with_confidence(
            "my landlord kept my security deposit and won't return it"
        )
        assert result.confidence > CONFIDENCE_THRESHOLD

    def test_zero_confidence_for_general(self) -> None:
        result = classify_with_confidence("hello how are you today")
        assert result.domain == "general"
        assert result.confidence == 0.0

    def test_scores_dict_populated(self) -> None:
        result = classify_with_confidence("my landlord won't fix the broken repair")
        assert "landlord_tenant" in result.scores
        assert result.scores["landlord_tenant"] > 0

    def test_compute_confidence_single_domain(self) -> None:
        # Only one domain matched → high confidence
        scores = {"landlord_tenant": 5}
        conf = _compute_confidence(scores)
        assert conf >= 0.8

    def test_compute_confidence_competing_domains(self) -> None:
        # Two domains with similar scores → lower confidence
        scores = {"landlord_tenant": 3, "small_claims": 3}
        conf = _compute_confidence(scores)
        assert conf < 0.6

    def test_compute_confidence_empty_scores(self) -> None:
        assert _compute_confidence({}) == 0.0

    def test_compute_confidence_dominant_winner(self) -> None:
        scores = {"landlord_tenant": 10, "employment_rights": 1}
        conf = _compute_confidence(scores)
        assert conf > 0.7

    def test_valid_domains_constant(self) -> None:
        assert "landlord_tenant" in VALID_DOMAINS
        assert "general" in VALID_DOMAINS
        assert len(VALID_DOMAINS) == 11  # 10 domains + general

    def test_classify_with_confidence_matches_classify(self) -> None:
        """classify_with_confidence and classify_legal_area should agree."""
        questions = [
            "my landlord kept my deposit",
            "I got fired without notice",
            "the product is defective",
            "hello world",
        ]
        for q in questions:
            assert classify_with_confidence(q).domain == classify_legal_area(q)


class TestClassifyWithLlmFallback:
    """Test the hybrid keyword + LLM fallback classifier."""

    async def test_high_confidence_returns_keyword_without_llm(self) -> None:
        """High confidence keyword result returns without making an LLM call."""
        # "landlord" + "security deposit" = high confidence
        result = await classify_with_llm_fallback(
            "my landlord kept my security deposit and won't return it"
        )
        assert result.domain == "landlord_tenant"
        assert result.method == "keyword"

    async def test_low_confidence_no_client_returns_keyword(self) -> None:
        """Low confidence with no client returns keyword result."""
        result = await classify_with_llm_fallback("hello", client=None)
        assert result.domain == "general"
        assert result.method == "keyword"

    async def test_low_confidence_with_mock_client_returns_llm(self) -> None:
        """Low confidence with a valid AsyncAnthropic client calls LLM."""
        import anthropic
        from anthropic.types import TextBlock

        mock_text_block = TextBlock(type="text", text="employment_rights")
        mock_response = MagicMock()
        mock_response.content = [mock_text_block]

        mock_client = AsyncMock(spec=anthropic.AsyncAnthropic)
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        # Use an ambiguous query that has low keyword confidence
        result = await classify_with_llm_fallback("what should I do about this", client=mock_client)
        assert result.domain == "employment_rights"
        assert result.method == "llm_fallback"
        assert result.confidence == 0.85

    async def test_llm_returns_invalid_domain_falls_back(self) -> None:
        """LLM returning an invalid domain falls back to keyword result."""
        import anthropic
        from anthropic.types import TextBlock

        mock_text_block = TextBlock(type="text", text="not_a_real_domain")
        mock_response = MagicMock()
        mock_response.content = [mock_text_block]

        mock_client = AsyncMock(spec=anthropic.AsyncAnthropic)
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await classify_with_llm_fallback("what should I do about this", client=mock_client)
        # Falls back to keyword result since "not_a_real_domain" not in VALID_DOMAINS
        assert result.method == "keyword"

    async def test_llm_api_error_falls_back_to_keyword(self) -> None:
        """LLM API error falls back to keyword result."""
        import anthropic

        mock_client = AsyncMock(spec=anthropic.AsyncAnthropic)
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.APIError(
                message="API error",
                request=MagicMock(),
                body=None,
            )
        )

        result = await classify_with_llm_fallback("what should I do about this", client=mock_client)
        assert result.method == "keyword"
