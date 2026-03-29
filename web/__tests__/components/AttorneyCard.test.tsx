import React from "react";
import { render, screen } from "@testing-library/react";
import AttorneyCard from "@/components/AttorneyCard";

const mockAttorney = {
  id: "att-1",
  name: "Jane Smith, Esq.",
  state: "Massachusetts",
  specializations: ["landlord_tenant", "consumer"],
  rating: 4.8,
  cost_range: "$200-$350/hr",
  phone: "617-555-1234",
  email: "jane@lawfirm.com",
  website: "https://janesmithlaw.com",
  accepts_free_consultations: true,
  bio: "20 years experience in tenant rights.",
};

describe("AttorneyCard", () => {
  it("displays the attorney name", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Specializes in landlord-tenant law in MA"
        relevanceScore={0.95}
      />
    );
    expect(screen.getByText("Jane Smith, Esq.")).toBeInTheDocument();
  });

  it("shows free consultation badge when applicable", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match reason"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("Free consult")).toBeInTheDocument();
  });

  it("hides free consultation badge when not applicable", () => {
    const noFreeConsult = { ...mockAttorney, accepts_free_consultations: false };
    render(
      <AttorneyCard
        attorney={noFreeConsult}
        matchReason="Match reason"
        relevanceScore={0.9}
      />
    );
    expect(screen.queryByText("Free consult")).not.toBeInTheDocument();
  });

  it("displays match reason", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Specializes in landlord-tenant law in MA"
        relevanceScore={0.95}
      />
    );
    expect(screen.getByText("Specializes in landlord-tenant law in MA")).toBeInTheDocument();
  });

  it("displays specializations as badges", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("landlord tenant")).toBeInTheDocument();
    expect(screen.getByText("consumer")).toBeInTheDocument();
  });

  it("displays cost range", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("$200-$350/hr")).toBeInTheDocument();
  });

  it("displays rating", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("4.8")).toBeInTheDocument();
  });

  it("renders contact links", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("Call")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Website")).toBeInTheDocument();
  });

  it("displays bio text", () => {
    render(
      <AttorneyCard
        attorney={mockAttorney}
        matchReason="Match"
        relevanceScore={0.9}
      />
    );
    expect(screen.getByText("20 years experience in tenant rights.")).toBeInTheDocument();
  });
});
