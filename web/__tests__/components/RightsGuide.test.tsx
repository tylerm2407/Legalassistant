import React from "react";
import { render, screen } from "@testing-library/react";
import RightsGuide from "@/components/RightsGuide";

const mockGuide = {
  id: "guide-1",
  domain: "landlord_tenant",
  title: "Security Deposit Rights",
  description: "Know your rights when your landlord withholds your deposit.",
  explanation: "Under Massachusetts law, landlords must follow strict rules.",
  your_rights: [
    "Right to itemized list of deductions",
    "Right to return of deposit within 30 days",
  ],
  action_steps: [
    "Document the condition of your unit",
    "Send a written demand letter",
  ],
  deadlines: ["30 days to return deposit after move-out"],
  common_mistakes: [
    "Not documenting condition at move-in",
    "Accepting verbal promises",
  ],
  when_to_get_a_lawyer: "If your landlord refuses to return the deposit after a demand letter.",
};

describe("RightsGuide", () => {
  it("displays the guide title", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Security Deposit Rights")).toBeInTheDocument();
  });

  it("displays the domain label", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("landlord tenant")).toBeInTheDocument();
  });

  it("displays the description", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Know your rights when your landlord withholds your deposit.")).toBeInTheDocument();
  });

  it("displays the explanation", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Under Massachusetts law, landlords must follow strict rules.")).toBeInTheDocument();
  });

  it("displays your rights list", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Right to itemized list of deductions")).toBeInTheDocument();
    expect(screen.getByText("Right to return of deposit within 30 days")).toBeInTheDocument();
  });

  it("displays action steps with numbers", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Document the condition of your unit")).toBeInTheDocument();
    expect(screen.getByText("Send a written demand letter")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("displays deadlines", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("30 days to return deposit after move-out")).toBeInTheDocument();
  });

  it("displays common mistakes", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("Not documenting condition at move-in")).toBeInTheDocument();
    expect(screen.getByText("Accepting verbal promises")).toBeInTheDocument();
  });

  it("displays when to get a lawyer", () => {
    render(<RightsGuide guide={mockGuide} />);
    expect(screen.getByText("If your landlord refuses to return the deposit after a demand letter.")).toBeInTheDocument();
  });

  it("hides deadlines section when empty", () => {
    const guideNoDeadlines = { ...mockGuide, deadlines: [] };
    render(<RightsGuide guide={guideNoDeadlines} />);
    expect(screen.queryByText("Important Deadlines")).not.toBeInTheDocument();
  });

  it("hides common mistakes section when empty", () => {
    const guideNoMistakes = { ...mockGuide, common_mistakes: [] };
    render(<RightsGuide guide={guideNoMistakes} />);
    expect(screen.queryByText("Common Mistakes to Avoid")).not.toBeInTheDocument();
  });
});
