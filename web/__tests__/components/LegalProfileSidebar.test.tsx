import React from "react";
import { render, screen } from "@testing-library/react";
import LegalProfileSidebar from "@/components/LegalProfileSidebar";
import type { LegalProfile } from "@/lib/types";

const mockProfile: LegalProfile = {
  user_id: "user-123",
  display_name: "Sarah Chen",
  state: "Massachusetts",
  housing_situation: "Renter — month-to-month",
  employment_type: "W-2 Employee — marketing coordinator",
  family_status: "Single",
  active_issues: [
    {
      issue_type: "landlord_tenant",
      summary: "Landlord claiming $800 for bathroom tile damage",
      status: "open",
      started_at: "2026-01-20T00:00:00Z",
      updated_at: "2026-03-01T00:00:00Z",
      notes: ["Pre-existing water damage documented"],
    },
  ],
  legal_facts: [
    "Landlord did not perform move-in inspection",
    "Pre-existing water damage in photos",
  ],
  documents: ["lease_agreement.pdf", "move_in_photos.zip"],
  member_since: "2026-01-15T00:00:00Z",
  conversation_count: 12,
};

describe("LegalProfileSidebar", () => {
  it("displays the user display name", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Sarah Chen")).toBeInTheDocument();
  });

  it("displays the user state", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Massachusetts")).toBeInTheDocument();
  });

  it("shows Memory Active indicator", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Memory Active")).toBeInTheDocument();
  });

  it("displays housing situation", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Renter — month-to-month")).toBeInTheDocument();
  });

  it("displays employment type", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("W-2 Employee — marketing coordinator")).toBeInTheDocument();
  });

  it("displays family status", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Single")).toBeInTheDocument();
  });

  it("displays active issues with status badge", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("landlord tenant")).toBeInTheDocument();
    expect(screen.getByText("open")).toBeInTheDocument();
    expect(screen.getByText("Landlord claiming $800 for bathroom tile damage")).toBeInTheDocument();
  });

  it("displays legal facts", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("Landlord did not perform move-in inspection")).toBeInTheDocument();
    expect(screen.getByText("Pre-existing water damage in photos")).toBeInTheDocument();
  });

  it("displays documents list", () => {
    render(<LegalProfileSidebar profile={mockProfile} />);
    expect(screen.getByText("lease_agreement.pdf")).toBeInTheDocument();
    expect(screen.getByText("move_in_photos.zip")).toBeInTheDocument();
  });

  it("shows empty state messages when no issues, facts, or documents", () => {
    const emptyProfile: LegalProfile = {
      ...mockProfile,
      active_issues: [],
      legal_facts: [],
      documents: [],
    };
    render(<LegalProfileSidebar profile={emptyProfile} />);
    expect(screen.getByText("No active issues")).toBeInTheDocument();
    expect(screen.getByText("Facts will appear as you chat")).toBeInTheDocument();
    expect(screen.getByText("No documents uploaded")).toBeInTheDocument();
  });
});
