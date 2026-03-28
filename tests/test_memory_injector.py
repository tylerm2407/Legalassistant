"""Tests for the memory injector — the most critical module in Lex.

The injector builds the system prompt that makes every Claude response
personalized. If this breaks, Lex gives generic answers and the product
is worthless.
"""

from __future__ import annotations

from backend.memory.injector import build_system_prompt
from backend.models.legal_profile import LegalProfile


class TestBuildSystemPromptIncludesProfileData:
    """Verify that the user's personal context appears in the prompt."""

    def test_includes_display_name(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "Sarah Chen" in prompt

    def test_includes_state(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "State: MA" in prompt

    def test_includes_housing_situation(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "renter" in prompt
        assert "Boston" in prompt

    def test_includes_employment_type(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "full-time W-2 employee" in prompt

    def test_includes_family_status(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "single, no dependents" in prompt


class TestBuildSystemPromptIncludesStateLaws:
    """Verify that MA statutes appear when asking a landlord_tenant question."""

    def test_includes_ma_landlord_tenant_law(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "M.G.L." in prompt

    def test_includes_security_deposit_statute(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        # M.G.L. c. 186, section 15B is the key MA security deposit statute
        assert "186" in prompt
        assert "15B" in prompt

    def test_includes_federal_landlord_law(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "Fair Housing Act" in prompt

    def test_applicable_law_section_header(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "APPLICABLE LAW" in prompt
        assert "LANDLORD TENANT" in prompt


class TestBuildSystemPromptIncludesActiveIssues:
    """Verify that the user's active issues are injected into the prompt."""

    def test_includes_issue_summary(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what are my options")
        assert "security deposit" in prompt.lower()

    def test_includes_issue_status(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what are my options")
        assert "open" in prompt.lower()

    def test_includes_issue_notes(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what are my options")
        assert "January 15, 2026" in prompt

    def test_active_issues_header(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what are my options")
        assert "ACTIVE LEGAL ISSUES" in prompt


class TestBuildSystemPromptIncludesLegalFacts:
    """Verify all 8 known legal facts appear in the prompt."""

    def test_all_facts_present(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what should I do next")
        for fact in mock_profile.legal_facts:
            assert fact in prompt, f"Missing fact: {fact}"

    def test_known_facts_header(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what should I do next")
        assert "KNOWN LEGAL FACTS" in prompt

    def test_facts_formatted_as_bullet_points(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "what should I do next")
        for fact in mock_profile.legal_facts:
            assert f"- {fact}" in prompt


class TestBuildSystemPromptIncludesResponseRules:
    """Verify the 8 response rules from LEX_BASE_INSTRUCTIONS are present."""

    def test_rule_1_cite_statutes(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "cite specific statutes" in prompt.lower()

    def test_rule_2_tailor_to_state(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "state and personal situation" in prompt.lower()

    def test_rule_3_plain_english(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "plain English" in prompt

    def test_rule_4_no_fabrication(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "Never fabricate citations" in prompt

    def test_rule_5_recommend_attorney(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "licensed attorney" in prompt

    def test_rule_6_not_a_lawyer(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "NOT a lawyer" in prompt

    def test_rule_7_connect_to_issues(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "active legal issues" in prompt.lower()

    def test_rule_8_empathetic(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "empathetic" in prompt.lower()

    def test_disclaimer_present(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello")
        assert "legal information, not legal advice" in prompt.lower()


class TestBuildSystemPromptClassifiesArea:
    """Verify the injector detects landlord_tenant for a deposit question."""

    def test_deposit_question_detected(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my security deposit")
        assert "DETECTED LEGAL AREA: landlord_tenant" in prompt

    def test_employment_question_detected(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "my employer won't pay my wages")
        assert "DETECTED LEGAL AREA: employment_rights" in prompt

    def test_general_question_detected(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "hello how are you")
        assert "DETECTED LEGAL AREA: general" in prompt


class TestBuildSystemPromptFederalFallback:
    """Verify federal defaults are used for unsupported states."""

    def test_unsupported_state_gets_federal_law(self) -> None:
        profile = LegalProfile(
            user_id="user_test",
            display_name="Test User",
            state="WY",  # Wyoming — not in STATE_LAWS
            housing_situation="renter",
            employment_type="employed",
            family_status="single",
        )
        prompt = build_system_prompt(profile, "can my landlord keep my deposit")
        # Should still include federal landlord_tenant law
        assert "Federal law" in prompt
        assert "Fair Housing Act" in prompt

    def test_unsupported_state_no_state_specific_law(self) -> None:
        profile = LegalProfile(
            user_id="user_test",
            display_name="Test User",
            state="WY",
            housing_situation="renter",
            employment_type="employed",
            family_status="single",
        )
        prompt = build_system_prompt(profile, "can my landlord keep my deposit")
        # Should NOT contain MA-specific or other state-specific references
        assert "M.G.L." not in prompt
        assert "State law (WY)" not in prompt

    def test_supported_state_gets_both_state_and_federal(self, mock_profile: LegalProfile) -> None:
        prompt = build_system_prompt(mock_profile, "can my landlord keep my deposit")
        assert "State law (MA)" in prompt
        assert "Federal law" in prompt
