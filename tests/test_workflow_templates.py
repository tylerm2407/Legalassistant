"""Tests for workflow template definitions — static data, no mocks needed.

Verifies that templates are well-formed, retrievable by ID and domain,
and contain the expected structure.
"""

from __future__ import annotations

from backend.workflows.templates.definitions import (
    WORKFLOW_TEMPLATES,
    get_all_templates,
    get_template_by_id,
    get_templates_by_domain,
)


class TestGetAllTemplates:
    """Verify get_all_templates returns the full list."""

    def test_returns_all_templates(self) -> None:
        templates = get_all_templates()
        assert len(templates) >= 5
        assert templates is WORKFLOW_TEMPLATES

    def test_all_templates_have_required_fields(self) -> None:
        for t in get_all_templates():
            assert t.id
            assert t.title
            assert t.description
            assert t.domain
            assert t.estimated_time
            assert len(t.steps) > 0


class TestGetTemplatesByDomain:
    """Verify filtering templates by legal domain."""

    def test_landlord_tenant_domain(self) -> None:
        templates = get_templates_by_domain("landlord_tenant")
        assert len(templates) >= 1
        assert all(t.domain == "landlord_tenant" for t in templates)

    def test_nonexistent_domain_returns_empty(self) -> None:
        templates = get_templates_by_domain("alien_law")
        assert templates == []


class TestGetTemplateById:
    """Verify fetching a single template by ID."""

    def test_existing_template(self) -> None:
        template = get_template_by_id("fight_eviction")
        assert template is not None
        assert template.title == "Fight an Eviction"
        assert template.domain == "landlord_tenant"
        assert len(template.steps) == 7

    def test_nonexistent_id_returns_none(self) -> None:
        template = get_template_by_id("does_not_exist")
        assert template is None
