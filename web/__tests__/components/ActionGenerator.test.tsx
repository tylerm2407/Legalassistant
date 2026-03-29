import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ActionGenerator from "@/components/ActionGenerator";

// Mock the api module
const mockGenerateLetter = jest.fn();
const mockGenerateRights = jest.fn();
const mockGenerateChecklist = jest.fn();

jest.mock("@/lib/api", () => ({
  api: {
    generateLetter: (...args: unknown[]) => mockGenerateLetter(...args),
    generateRights: (...args: unknown[]) => mockGenerateRights(...args),
    generateChecklist: (...args: unknown[]) => mockGenerateChecklist(...args),
  },
}));

describe("ActionGenerator", () => {
  beforeEach(() => {
    mockGenerateLetter.mockReset();
    mockGenerateRights.mockReset();
    mockGenerateChecklist.mockReset();
  });

  it("renders three action buttons", () => {
    render(<ActionGenerator userId="user-123" />);
    expect(screen.getByText("Generate Letter")).toBeInTheDocument();
    expect(screen.getByText("Rights Summary")).toBeInTheDocument();
    expect(screen.getByText("Checklist")).toBeInTheDocument();
  });

  it("renders Actions label", () => {
    render(<ActionGenerator userId="user-123" />);
    expect(screen.getByText("Actions:")).toBeInTheDocument();
  });

  it("displays demand letter result after generating", async () => {
    mockGenerateLetter.mockResolvedValueOnce({
      letter_text: "Dear Landlord, I demand...",
      legal_citations: ["M.G.L. c.186 §15B"],
    });

    const user = userEvent.setup();
    render(<ActionGenerator userId="user-123" />);
    await user.click(screen.getByText("Generate Letter"));

    await waitFor(() => {
      expect(screen.getByText("Demand Letter")).toBeInTheDocument();
      expect(screen.getByText("Dear Landlord, I demand...")).toBeInTheDocument();
      expect(screen.getByText("M.G.L. c.186 §15B")).toBeInTheDocument();
    });
  });

  it("displays rights summary result after generating", async () => {
    mockGenerateRights.mockResolvedValueOnce({
      summary_text: "As a tenant in Massachusetts...",
      key_rights: ["Right to deposit return within 30 days"],
    });

    const user = userEvent.setup();
    render(<ActionGenerator userId="user-123" />);
    await user.click(screen.getByText("Rights Summary"));

    await waitFor(() => {
      expect(screen.getByText("As a tenant in Massachusetts...")).toBeInTheDocument();
      expect(screen.getByText("Right to deposit return within 30 days")).toBeInTheDocument();
    });
  });

  it("displays checklist result after generating", async () => {
    mockGenerateChecklist.mockResolvedValueOnce({
      items: ["Send demand letter", "File small claims"],
      deadlines: ["March 30, 2026", null],
    });

    const user = userEvent.setup();
    render(<ActionGenerator userId="user-123" />);
    await user.click(screen.getByText("Checklist"));

    await waitFor(() => {
      expect(screen.getByText("Send demand letter")).toBeInTheDocument();
      expect(screen.getByText("File small claims")).toBeInTheDocument();
      expect(screen.getByText("Deadline: March 30, 2026")).toBeInTheDocument();
    });
  });

  it("displays error message on API failure", async () => {
    mockGenerateLetter.mockRejectedValueOnce(new Error("Server error"));

    const user = userEvent.setup();
    render(<ActionGenerator userId="user-123" />);
    await user.click(screen.getByText("Generate Letter"));

    await waitFor(() => {
      expect(screen.getByText("Server error")).toBeInTheDocument();
    });
  });

  it("disables all buttons while generating", async () => {
    let resolvePromise: (value: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockGenerateLetter.mockReturnValueOnce(pendingPromise);

    const user = userEvent.setup();
    render(<ActionGenerator userId="user-123" />);
    await user.click(screen.getByText("Generate Letter"));

    expect(screen.getByText("Generating...")).toBeInTheDocument();

    // Clean up
    resolvePromise!({ letter_text: "test", legal_citations: [] });
  });
});
