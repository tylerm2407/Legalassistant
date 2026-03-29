import React from "react";
import { render, screen } from "@testing-library/react";
import CaseHistory from "@/components/CaseHistory";
import type { LegalIssue } from "@/lib/types";

const mockIssues: LegalIssue[] = [
  {
    issue_type: "landlord_tenant",
    summary: "Security deposit dispute",
    status: "open",
    started_at: "2026-01-20T00:00:00Z",
    updated_at: "2026-03-01T00:00:00Z",
    notes: ["Sent demand letter"],
  },
  {
    issue_type: "employment",
    summary: "Overtime pay dispute",
    status: "resolved",
    started_at: "2025-11-01T00:00:00Z",
    updated_at: "2026-02-15T00:00:00Z",
    notes: [],
  },
];

describe("CaseHistory", () => {
  it("shows empty state when no issues", () => {
    render(<CaseHistory issues={[]} />);
    expect(screen.getByText("No active cases")).toBeInTheDocument();
  });

  it("renders issue types", () => {
    render(<CaseHistory issues={mockIssues} />);
    expect(screen.getByText("landlord tenant")).toBeInTheDocument();
    expect(screen.getByText("employment")).toBeInTheDocument();
  });

  it("renders issue summaries", () => {
    render(<CaseHistory issues={mockIssues} />);
    expect(screen.getByText("Security deposit dispute")).toBeInTheDocument();
    expect(screen.getByText("Overtime pay dispute")).toBeInTheDocument();
  });

  it("renders status badges", () => {
    render(<CaseHistory issues={mockIssues} />);
    expect(screen.getByText("open")).toBeInTheDocument();
    expect(screen.getByText("resolved")).toBeInTheDocument();
  });

  it("renders notes when present", () => {
    render(<CaseHistory issues={mockIssues} />);
    expect(screen.getByText("Sent demand letter")).toBeInTheDocument();
  });

  it("shows started and updated dates", () => {
    render(<CaseHistory issues={[mockIssues[0]]} />);
    // Check that date strings appear (format depends on locale)
    const startedText = screen.getByText(/Started:/);
    expect(startedText).toBeInTheDocument();
    const updatedText = screen.getByText(/Updated:/);
    expect(updatedText).toBeInTheDocument();
  });
});
