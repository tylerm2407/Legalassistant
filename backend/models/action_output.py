"""Pydantic models for structured action outputs.

These models represent the deliverables that Lex can generate for a user:
demand letters, rights summaries, and next-steps checklists. Each model
captures both the generated text and the supporting legal citations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemandLetter(BaseModel):
    """A generated demand letter with legal citations.

    Attributes:
        text: The full text of the demand letter, ready to send.
        citations: List of statute citations referenced in the letter.
        recipient: Optional name or description of the letter recipient.
        subject: The subject line or topic of the demand.
    """

    text: str
    citations: list[str] = Field(default_factory=list)
    recipient: str | None = None
    subject: str


class RightsSummary(BaseModel):
    """A plain-English summary of the user's legal rights.

    Attributes:
        text: Full narrative explanation of the user's rights.
        key_rights: Bulleted list of the most important rights.
        applicable_laws: Statute citations that establish these rights.
    """

    text: str
    key_rights: list[str] = Field(default_factory=list)
    applicable_laws: list[str] = Field(default_factory=list)


class Checklist(BaseModel):
    """A prioritized next-steps checklist for the user's legal situation.

    Attributes:
        items: List of action items the user should take.
        deadlines: Parallel list of deadline strings (or None) for each item.
                   Index-aligned with items.
        priority_order: List of indices into items, sorted by priority
                        (most urgent first).
    """

    items: list[str] = Field(default_factory=list)
    deadlines: list[str | None] = Field(default_factory=list)
    priority_order: list[int] = Field(default_factory=list)
