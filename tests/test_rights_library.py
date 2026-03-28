"""Tests for the rights library.

Covers domain listing, guide content, domain filtering,
invalid domains, guide structure, and guide loading.
"""

from __future__ import annotations

from backend.knowledge.rights_library import (
    RIGHTS_GUIDES,
    get_all_guides,
    get_domains,
    get_guide_by_id,
    get_guides_by_domain,
)


def test_all_domains_have_guides():
    """Every domain returned by get_domains has at least one guide."""
    domains = get_domains()
    assert len(domains) > 0
    for domain_info in domains:
        assert domain_info["guide_count"] > 0


def test_guide_content_is_non_empty():
    """Every guide has non-empty explanation and rights."""
    guides = get_all_guides()
    for guide in guides:
        assert len(guide.explanation) > 0, f"Guide {guide.id} has empty explanation"
        assert len(guide.your_rights) > 0, f"Guide {guide.id} has empty rights"
        assert len(guide.action_steps) > 0, f"Guide {guide.id} has empty action_steps"


def test_domain_filter_returns_correct_domain():
    """get_guides_by_domain returns only guides from that domain."""
    guides = get_guides_by_domain("landlord_tenant")
    assert len(guides) > 0
    for guide in guides:
        assert guide.domain == "landlord_tenant"


def test_invalid_domain_returns_empty():
    """get_guides_by_domain with unknown domain returns empty list."""
    guides = get_guides_by_domain("nonexistent_domain")
    assert guides == []


def test_guide_structure_has_required_fields():
    """Every guide has all required fields populated."""
    required_attrs = [
        "id", "domain", "title", "description", "explanation",
        "your_rights", "action_steps", "deadlines", "common_mistakes",
        "when_to_get_a_lawyer",
    ]
    guides = get_all_guides()
    for guide in guides:
        for attr in required_attrs:
            value = getattr(guide, attr)
            assert value is not None, f"Guide {guide.id} missing {attr}"
            if isinstance(value, str) or isinstance(value, list):
                assert len(value) > 0, f"Guide {guide.id} has empty {attr}"


def test_all_guides_loadable():
    """All guides defined in RIGHTS_GUIDES are retrievable by ID."""
    for guide in RIGHTS_GUIDES:
        retrieved = get_guide_by_id(guide.id)
        assert retrieved is not None, f"Guide {guide.id} not found by ID"
        assert retrieved.id == guide.id


def test_get_guide_by_id_returns_none_for_unknown():
    """get_guide_by_id returns None for an unknown ID."""
    result = get_guide_by_id("totally_fake_guide_id")
    assert result is None


def test_get_all_guides_returns_all():
    """get_all_guides returns the same count as RIGHTS_GUIDES."""
    assert len(get_all_guides()) == len(RIGHTS_GUIDES)


def test_domains_have_labels():
    """Every domain has a human-readable label."""
    domains = get_domains()
    for domain_info in domains:
        assert "label" in domain_info
        assert len(domain_info["label"]) > 0
