"""Pydantic models for the user's persistent legal profile.

The LegalProfile is the single most important data model in CaseMate. It is
injected into every Claude API call so that responses are personalized
to the user's specific legal situation, state, and history.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class IssueStatus(StrEnum):
    """Status values for a user's active legal issue."""

    OPEN = "open"
    RESOLVED = "resolved"
    WATCHING = "watching"
    ESCALATED = "escalated"


class LegalIssue(BaseModel):
    """A single ongoing legal dispute or situation being tracked for a user.

    Attributes:
        issue_type: The legal domain (landlord_tenant, employment, etc.).
        summary: A one-sentence description of the specific dispute.
        status: Current state of the issue.
        started_at: When the issue was first mentioned to CaseMate.
        updated_at: When the issue was last updated.
        notes: Additional context extracted from conversations over time.
    """

    issue_type: str
    summary: str
    status: IssueStatus = IssueStatus.OPEN
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: list[str] = Field(default_factory=list)


class LegalProfile(BaseModel):
    """The user's persistent legal context. Injected into every Claude API call.

    This is the single most important data model in CaseMate. Every field either
    comes from the onboarding intake or is automatically extracted from
    conversations by the ProfileAutoUpdater background task.

    Attributes:
        user_id: Supabase auth user ID. Primary key.
        display_name: First name for personalized responses.
        state: Two-letter state code. Determines which laws apply.
        housing_situation: Renter/owner/etc with relevant details.
        employment_type: Classification affecting applicable rights.
        family_status: Relevant for family law and dependent questions.
        language_preference: ISO language code for response language ("en" or "es").
        active_issues: Ongoing legal disputes tracked over time.
        legal_facts: Specific facts extracted from conversations.
        documents: References to uploaded documents in Supabase Storage.
        member_since: Used to show users how long CaseMate has helped them.
        conversation_count: Total conversations — shows product usage depth.
    """

    user_id: str
    display_name: str
    state: str
    housing_situation: str
    employment_type: str
    family_status: str
    language_preference: Literal["en", "es"] = "en"
    active_issues: list[LegalIssue] = Field(default_factory=list)
    legal_facts: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    member_since: datetime = Field(default_factory=lambda: datetime.now(UTC))
    conversation_count: int = 0

    def to_context_string(self) -> str:
        """Serialize the profile to a concise JSON string for prompt injection.

        Returns:
            JSON string containing all non-empty profile fields relevant
            to legal context. Active issues and known facts are included
            only when present.
        """
        data: dict[str, object] = {
            "state": self.state,
            "housing": self.housing_situation,
            "employment": self.employment_type,
            "family": self.family_status,
            "language": self.language_preference,
        }
        if self.active_issues:
            data["active_issues"] = [
                {
                    "type": issue.issue_type,
                    "summary": issue.summary,
                    "status": issue.status.value,
                }
                for issue in self.active_issues
            ]
        if self.legal_facts:
            data["known_facts"] = self.legal_facts
        return json.dumps(data, indent=2)
