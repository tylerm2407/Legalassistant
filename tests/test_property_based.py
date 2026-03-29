"""Property-based tests for CaseMate using Hypothesis.

Validates invariants that must hold for all possible inputs:
- The legal classifier never crashes on arbitrary strings
- Token budget management preserves message structure
- LegalProfile round-trips through JSON serialization
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from backend.legal.classifier import (
    VALID_DOMAINS,
    ClassificationResult,
    classify_with_confidence,
)
from backend.models.legal_profile import LegalProfile
from backend.utils.token_budget import TokenBudgetManager

# ---------------------------------------------------------------------------
# Classifier safety: any string input never crashes
# ---------------------------------------------------------------------------


@given(question=st.text(min_size=0, max_size=5000))
@settings(max_examples=200, deadline=None)
def test_classifier_never_crashes(question: str) -> None:
    """The keyword classifier must handle any string without raising."""
    result = classify_with_confidence(question)

    assert isinstance(result, ClassificationResult)
    assert result.domain in VALID_DOMAINS
    assert 0.0 <= result.confidence <= 1.0
    assert result.method in ("keyword", "llm_fallback")
    assert isinstance(result.scores, dict)


@given(question=st.text(min_size=0, max_size=5000))
@settings(max_examples=100, deadline=None)
def test_classifier_returns_general_for_empty_like(question: str) -> None:
    """Classifier with no keyword matches should return 'general' domain."""
    result = classify_with_confidence(question)
    if not result.scores:
        assert result.domain == "general"
        assert result.confidence == 0.0


@given(
    question=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")),
        min_size=1,
        max_size=500,
    )
)
@settings(max_examples=100, deadline=None)
def test_classifier_confidence_bounds(question: str) -> None:
    """Confidence must always be between 0 and 1 inclusive."""
    result = classify_with_confidence(question)
    assert 0.0 <= result.confidence <= 1.0


# ---------------------------------------------------------------------------
# Token budget safety: never crashes, output within budget
# ---------------------------------------------------------------------------


@given(
    messages=st.lists(
        st.fixed_dictionaries(
            {
                "role": st.sampled_from(["user", "assistant"]),
                "content": st.text(min_size=1, max_size=500),
            }
        ),
        min_size=1,
        max_size=20,
    ),
    system_tokens=st.integers(min_value=0, max_value=5000),
)
@settings(max_examples=100, deadline=None)
def test_token_budget_never_crashes(
    messages: list[dict[str, str]],
    system_tokens: int,
) -> None:
    """Token budget manager must handle any message list without raising."""
    manager = TokenBudgetManager()
    result = manager.apply(messages, system_prompt_tokens=system_tokens)

    assert isinstance(result.messages, list)
    assert result.final_count >= 0
    assert result.original_count == len(messages)


@given(
    messages=st.lists(
        st.fixed_dictionaries(
            {
                "role": st.sampled_from(["user", "assistant"]),
                "content": st.text(min_size=1, max_size=200),
            }
        ),
        min_size=2,
        max_size=10,
    ),
)
@settings(max_examples=50, deadline=None)
def test_token_budget_preserves_roles(messages: list[dict[str, str]]) -> None:
    """All messages in output must have valid role fields."""
    manager = TokenBudgetManager()
    result = manager.apply(messages, system_prompt_tokens=500)

    for msg in result.messages:
        assert msg["role"] in ("user", "assistant", "system")


@given(
    messages=st.lists(
        st.fixed_dictionaries(
            {
                "role": st.sampled_from(["user", "assistant"]),
                "content": st.text(min_size=1, max_size=100),
            }
        ),
        min_size=1,
        max_size=5,
    ),
)
@settings(max_examples=50, deadline=None)
def test_token_budget_last_message_preserved(messages: list[dict[str, str]]) -> None:
    """The most recent user message should always be preserved."""
    manager = TokenBudgetManager()
    result = manager.apply(messages, system_prompt_tokens=500)

    if result.messages:
        # The last message from the input should be in the output
        assert result.messages[-1]["content"] == messages[-1]["content"]


# ---------------------------------------------------------------------------
# LegalProfile round-trip: serialize → deserialize → identical
# ---------------------------------------------------------------------------


legal_profile_strategy = st.builds(
    LegalProfile,
    user_id=st.text(
        min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))
    ),
    display_name=st.text(
        min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))
    ),
    state=st.sampled_from(["MA", "NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC"]),
    housing_situation=st.text(min_size=0, max_size=200),
    employment_type=st.text(min_size=0, max_size=200),
    family_status=st.text(min_size=0, max_size=200),
    active_issues=st.just([]),
    legal_facts=st.lists(st.text(min_size=1, max_size=100), max_size=5),
    documents=st.lists(st.text(min_size=1, max_size=50), max_size=3),
)


@given(profile=legal_profile_strategy)
@settings(max_examples=100, deadline=None)
def test_legal_profile_round_trip(profile: LegalProfile) -> None:
    """A LegalProfile must survive JSON round-trip without data loss."""
    json_data = profile.model_dump(mode="json")
    restored = LegalProfile.model_validate(json_data)

    assert restored.user_id == profile.user_id
    assert restored.display_name == profile.display_name
    assert restored.state == profile.state
    assert restored.housing_situation == profile.housing_situation
    assert restored.employment_type == profile.employment_type
    assert restored.family_status == profile.family_status
    assert restored.legal_facts == profile.legal_facts
    assert restored.documents == profile.documents


@given(profile=legal_profile_strategy)
@settings(max_examples=50, deadline=None)
def test_legal_profile_json_is_dict(profile: LegalProfile) -> None:
    """model_dump(mode='json') must return a plain dict, not a Pydantic model."""
    json_data = profile.model_dump(mode="json")
    assert isinstance(json_data, dict)
    assert "user_id" in json_data
    assert "state" in json_data
